#!/bin/sh
# 部署启动脚本：解析一个可用的 Python 解释器并拉起 support-agent。
#
# 为什么需要它：
#   WorkBuddy 部署沙箱用 pyenv 管理 Python，但预置版本里没有 3.14；
#   而项目根的 .python-version 钉死了 3.14，于是直接执行 `python3` 会命中
#   pyenv 的 "version `3.14' is not installed" 而启动失败。
#   本应用零第三方依赖、纯标准库（已在 3.13 / 3.14 双版本跑通 78 项测试），
#   因此可以安全地"优先 3.14、降级到任意 >=3.10"。
#
# 解析顺序：
#   1) uv 托管的 3.14（部署期由 installCmd 执行 `uv python install 3.14` 预装）
#   2) 系统预置解释器 /usr/bin、/usr/local/bin
#   3) pyenv 与 uv 的版本目录里任意一个 >=3.10 的解释器
#   4) PYENV_VERSION=system —— 让 pyenv 忽略 .python-version，用系统解释器兜底
#
# 用法：sh scripts/deploy-start.sh（平台会注入 PORT；HOST 默认 0.0.0.0）

set -u

log() { printf '[deploy-start] %s\n' "$*" >&2; }

# 切到应用根目录（脚本位于 <app>/scripts/ 下），并把 PYTHONPATH 钉成绝对路径
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
# Git Bash / MSYS 下 pwd 返回 /d/... 形式，Windows Python 认不出；取原生路径
case "$(uname -s 2>/dev/null || echo unknown)" in
    MINGW*|MSYS*|CYGWIN*) APP_DIR="$(cd "$(dirname "$0")/.." && pwd -W)" ;;
esac
cd "$APP_DIR" || { log "FATAL: 无法进入应用目录 $APP_DIR"; exit 1; }
# 直接覆盖 PYTHONPATH（不与既有值合并）：应用零第三方依赖，无需外部路径；
# 且既有值的分隔符在 POSIX(:)/Windows(;) 之间不一致，合并会造成解析歧义。
export PYTHONPATH="$APP_DIR/src"

usable() {
    # 接受解释器路径，判定其版本 >= 3.10
    [ -x "$1" ] || return 1
    "$1" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null
}

PY=""
TRY=""

# 1) uv 托管的 3.14
if command -v uv >/dev/null 2>&1; then
    TRY="$(uv python find --python 3.14 --no-download 2>/dev/null || true)"
    if usable "$TRY"; then PY="$TRY"; fi
fi

# 2) 平台自带 venv（平台若已建好虚拟环境，优先用它）
if [ -z "$PY" ]; then
    for c in "${VIRTUAL_ENV:-/nonexistent}/bin/python3" /workspace/.venv/bin/python3 \
             "$APP_DIR/.venv/bin/python3" /opt/venv/bin/python3; do
        if usable "$c"; then PY="$c"; break; fi
    done
fi

# 3) 系统预置解释器（显式枚举，不走 pyenv shim，避开 .python-version 干扰）
if [ -z "$PY" ]; then
    for c in /usr/bin/python3.14 /usr/bin/python3.13 /usr/bin/python3.12 \
             /usr/bin/python3.11 /usr/bin/python3.10 \
             /usr/local/bin/python3.14 /usr/local/bin/python3.13 \
             /usr/local/bin/python3.12 /usr/local/bin/python3.11; do
        if usable "$c"; then PY="$c"; break; fi
    done
fi

# 4) pyenv / uv 的版本目录
if [ -z "$PY" ]; then
    for c in /root/.pyenv/versions/*/bin/python3 /root/.local/share/uv/python/*/bin/python3 \
             "$HOME"/.pyenv/versions/*/bin/python3 "$HOME"/.local/share/uv/python/*/bin/python3; do
        if usable "$c"; then PY="$c"; break; fi
    done
fi

# 5) 让 pyenv 忽略 .python-version（system = 绕过 pyenv 用系统解释器）
if [ -z "$PY" ]; then
    for c in system; do
        if PYENV_VERSION="$c" python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
            PY=system
            break
        fi
    done
fi

if [ -z "$PY" ]; then
    log "FATAL: 没有找到可用的 Python 解释器（>=3.10）"
    log "--- 诊断信息 ---"
    command -v python3 python3.13 python3.12 python3.11 2>/dev/null || true
    python3 -V 2>&1 || true
    pyenv versions 2>/dev/null || true
    ls -d /root/.pyenv/versions/* /root/.local/share/uv/python/* 2>/dev/null || true
    exit 1
fi

export HOST="${HOST:-0.0.0.0}"

if [ "$PY" = "system" ]; then
    log "interpreter: system python3 ($(PYENV_VERSION=system python3 -V 2>&1))"
    export PYENV_VERSION=system
    exec python3 -m support_agent.cli serve
fi

log "interpreter: $PY ($("$PY" -V 2>&1))"
exec "$PY" -m support_agent.cli serve
