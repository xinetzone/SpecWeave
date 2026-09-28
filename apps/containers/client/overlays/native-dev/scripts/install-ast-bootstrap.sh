#!/usr/bin/env bash
# ==============================================================================
# install-ast-bootstrap.sh — 把解释器启动期 AST 兼容钩子烤入镜像内全部解释器
#
# 背景（2026-09-28，Terminal import tvm 修复）：
#   CPython 3.12+ 移除 ast.NameConstant/Num/Str/Bytes/Ellipsis，而 tvm 源码树
#   python/tvm/relay/testing/py_converter.py 在**模块导入期**执行
#   `from ast import ..., NameConstant, Num, Str`（经 relay/frontend/caffe
#   导入链触发），任何 xmnn 层运行期补丁都晚于该语句——唯一注入位点是解释器
#   site 初始化期（.pth 钩子）。
#   镜像内 /opt/native-builder/_xmnn_bootstrap.py（stdlib-only、幂等）原本只
#   服务于 wheel 交付物与 verify-wheel 临时 venv，镜像自身解释器（base cp314
#   GIL / main cp314t）从未安装——Terminal/SSH/notebook 内核 import tvm 开箱
#   即 ImportError。本脚本把钩子模块拷入两解释器 site-packages 并各写单行
#   xmnn_bootstrap.pth（`import _xmnn_bootstrap`；模块本体已就地，无需路径行，
#   不依赖运行时可剥离的 /workspace bind mount，符合离线自足契约）。
#
# 语义真源：npuusertools 仓库 _xmnn_bootstrap.py（元类精确复刻旧版 isinstance
#   语义）；builder 携带的简版满足 py_converter 仅 `from ast import` 的需求。
# 幂等：重复执行安全；旧版解释器（3.8–3.13）install() 内 hasattr 短路为 no-op。
# 守卫：smoke/_toolchain_guards.py §11 以「新解释器进程 hasattr」双端断言。
# ==============================================================================
set -euo pipefail

BOOTSTRAP_SRC=/opt/native-builder/_xmnn_bootstrap.py
PTH_NAME=xmnn_bootstrap.pth

[ -f "$BOOTSTRAP_SRC" ] || { echo "[FATAL] 钩子模块缺失: $BOOTSTRAP_SRC" >&2; exit 1; }

install_into() {
    local py="$1" label="$2"
    local sp
    sp="$("$py" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')"
    install -m 644 "$BOOTSTRAP_SRC" "$sp/_xmnn_bootstrap.py"
    printf 'import _xmnn_bootstrap\n' > "$sp/$PTH_NAME"
    "$py" -c 'import ast; assert all(hasattr(ast, n) for n in ("NameConstant", "Num", "Str", "Bytes", "Ellipsis")), "ast aliases missing"'
    echo "[OK] $label: $sp/$PTH_NAME"
}

install_into /opt/conda/bin/python "base (cp314 GIL)"
install_into /opt/conda/envs/main/bin/python "main (cp314t)"
