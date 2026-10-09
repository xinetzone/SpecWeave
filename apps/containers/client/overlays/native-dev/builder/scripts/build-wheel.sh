#!/bin/bash
# ==============================================================================
# build-wheel.sh — native-dev 叠加层容器内 Nuitka 打包脚本（运行时调用）
#
# 调用方式：
#   invoke native.wheel                       # client 任务（经 compose exec）
#   podman-compose exec native bash /opt/native-builder/scripts/build-wheel.sh
#
# 流程：环境自检 → libtvm.so 前置检查 → Nuitka 串行编译 tvm → 并行 vta/xmnn
#       → python -m build 组装 wheel。
#
# 源码树全程只读：Python 3.12+ 移除的 ast 遗留节点由运行期兼容层兜底
# （_xmnn_bootstrap.py 的 .pth 启动钩子 + xmnn/vta_compat.apply_ast_compat()），
# 不再向任何包的 __init__.py 注入/还原代码，故无「注入态」残留风险。
#
# 产物：$DIST_DIR/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl
#       （默认 /workspace/dist，宿主可见的 bind 挂载目录）
#
# 双 ABI 事实（rootless 基底 2026-09-14 实证）：
#   /opt/conda            = Python 3.14 cp314 GIL enabled（Nuitka 4.2.2 打包）
#   /opt/conda/envs/main  = Python 3.14 cp314t free-threading（Nuitka 不兼容）
# 故本脚本固定以 /opt/conda/bin/python 为编译解释器；clang/LLVM/cmake 工具链
# 位于 main env（PATH 第二段，CC/CXX/LLVM_CONFIG 绝对指向）。
# ==============================================================================
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILDER_DIR="${BUILDER_DIR:-$(cd "$SCRIPT_DIR/.." && pwd)}"   # /opt/native-builder

source "${SCRIPT_DIR}/lib/logging.sh"
LOG_FILE=/dev/null
log_enable_trap

log_set_error_help '  Nuitka 打包失败排查：
  1. "fatal error: xxx.h: No such file" → 工具链缺失，检查叠加镜像构建层
  2. "LLVM error" → 确认 LLVM_CONFIG 指向 main env 的 llvm-config（22.1.x）
  3. "cloudpickle/dill serialization error" → 确认 --enable-plugin=dill-compat
  4. "Killed" / "out of memory" → 降低并发：NUITKA_JOBS=4 inv native.wheel --jobs 4
  5. libtvm.so 缺失 → 先执行：inv native.build-tvm（或 scripts/build-tvm.sh）
  6. 交互调试：podman-compose exec native bash，cd /opt/native-builder 重跑本脚本
  7. "Unmet dependencies (checked against /opt/conda/bin/python): cmake>=3.18"
     → PYTHONPATH 污染致 scikit-build-core 误判 PyPI cmake 已装（本脚本已用
       env -u PYTHONPATH 规避）；若复现，先 `env -u PYTHONPATH python -m build ...`'

# ── 路径变量化（compose 注入环境变量可覆盖全部默认值）─────────────────────
TVM_ROOT="${TVM_ROOT:-/workspace/npu_tvm}"
XMN_ROOT="${XMN_ROOT:-/workspace/npuusertools}"
XMN_PKG="$XMN_ROOT/xmnn"
NUITKA_OUT="${NUITKA_OUT:-$BUILDER_DIR/build/nuitka}"
VTA_NUITKA_OUT="$NUITKA_OUT/vta_out"
XMNN_NUITKA_OUT="$NUITKA_OUT/xmnn_out"
DIST_DIR="${DIST_DIR:-/workspace/dist}"
CCACHE_DIR="${CCACHE_DIR:-/root/.ccache}"

BASE_PREFIX=/opt/conda
MAIN_PREFIX=/opt/conda/envs/main
BASE_PYTHON="$BASE_PREFIX/bin/python"

# ── 双 env 跨环境导出（仅本脚本进程内生效，不污染容器全局/Python 服务）──────
export PATH="$BASE_PREFIX/bin:$MAIN_PREFIX/bin:${PATH:-}"
export LD_LIBRARY_PATH="$MAIN_PREFIX/lib:$BASE_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export PIP_USER=0
export PIP_NO_CACHE_DIR=1
export LLVM_CONFIG="${LLVM_CONFIG:-$MAIN_PREFIX/bin/llvm-config}"
export CC="${CC:-$MAIN_PREFIX/bin/clang}"
export CXX="${CXX:-$MAIN_PREFIX/bin/clang++}"
# LLVM_LIB_DIR 传给 CMake：动态实测，禁止硬编码（SONAME 漂移由 CMake glob 吸收）
LLVM_LIB_DIR="$("$LLVM_CONFIG" --libdir)"

# ── libtvm.so 前置检查（消费挂载源码树中的既有 TVM 构建产物）──────────────
if [ ! -f "$TVM_ROOT/build/libtvm.so" ]; then
    log_error "未找到 $TVM_ROOT/build/libtvm.so"
    echo "  → 请先在运行中的栈内编译 TVM：inv native.build-tvm"
    echo "    （或 podman-compose exec native bash /opt/native-builder/scripts/build-tvm.sh）"
    exit 2
fi

# ── 源码树只读：本脚本不再改写任何 __init__.py，故无需还原兜底 trap。─────
TVM_PYTHON="$TVM_ROOT/python"
TVM_PKG="$TVM_PYTHON/tvm"
VTA_PYTHON="$TVM_ROOT/vta/python"
VTA_CONFIG_DIR="$TVM_ROOT/vta/vta_hw/config"
VTA_PKG="$VTA_PYTHON/vta"

# ── ccache 配置（命名卷 /root/.ccache 由 compose 挂载持久化）──────────────
export CCACHE_MAXSIZE=5G
CLEAN_REBUILD="${CLEAN_REBUILD:-0}"
# 离线模式（invoke native.up --offline / root .env NATIVE_OFFLINE=1 经 exec -e 注入）：
# 禁用一切联网兜底，缺依赖即硬失败，不在无网机器上静默挂起或拉取。
NATIVE_OFFLINE="${NATIVE_OFFLINE:-0}"
mkdir -p "$CCACHE_DIR"
if command -v ccache >/dev/null 2>&1; then
    export NUITKA_CCACHE_BINARY="$(command -v ccache)"
    if [ "$CLEAN_REBUILD" = "1" ]; then
        export CCACHE_DISABLE=1
        ccache -z 2>/dev/null || true
        log_warn "CLEAN REBUILD MODE: ccache DISABLED（不查不写，已有缓存保留）"
    else
        log_kv "ccache" "$(ccache --version | head -1) (enabled, $CCACHE_DIR)"
    fi
else
    log_warn "ccache: NOT FOUND（重复构建将全量重编译）"
fi

# ── Nuitka 选项 ─────────────────────────────────────────────────────────
NUITKA_JOBS="${NUITKA_JOBS:-8}"
NUITKA_PLUGINS="${NUITKA_PLUGINS:-dill-compat}"
# 运行期更新检查统一关闭。Nuitka 版本由镜像构建期 install-build-deps.py 精确钉
# 版（nuitka==X.Y.Z），本打包链路要求可复现/离线一致：不得让构建日志随构建时
# 网络出现 pypi.org 的 "older than latest stable" WARNING。该检查是独立子系统，
# --quiet 不抑制，tvm/vta/xmnn 三次调用（含并行子 shell）各打印一次，且缓存
# /root/.cache/Nuitka 位于容器易失层、重建后必然复发。此处 export 一次即覆盖
# 全部调用点；容器内手工 `python -m nuitka` 的交互式调试不经过本脚本，更新
# 提醒在该场景刻意保留（维护者升级 pin 的知情渠道）。版本跟进走「pin → smoke
# 守卫 → LABEL/文档 → 镜像重建 → wheel 验证」原子变更，不在打包运行期决策。
export NUITKA_UPDATE_CHECK=never
# 模式旗标必须写 --mode=module，禁用遗留别名 --module：4.x 里 --module 只置
# module_mode，而「module-mode 专属选项」告警的判据是 compilation_mode（仅
# --mode= 才赋值），故 --module 配 --no-pyi-file 会误报 "has no effect"。
NOFOLLOW_IMPORTS="${NOFOLLOW_IMPORTS:-torch,torchvision,onnx2pytorch}"
TVM_COMPILE_FLAGS="${TVM_COMPILE_FLAGS:-}"
# Nuitka 辅助工具（ccache/depends 等）的下载确认旗标：离线时置空（不带引号展开 →
# 零词消失），使 Nuitka 在需要下载时直接失败而非交互式等待或静默联网。
if [ "$NATIVE_OFFLINE" = "1" ]; then
    NUITKA_DL_FLAG=""
else
    NUITKA_DL_FLAG="--assume-yes-for-downloads"
fi

nofollow_args() {
    local IFS=',' p
    for p in ${NOFOLLOW_IMPORTS}; do
        [ -n "$p" ] && printf -- '--nofollow-import-to=%s\n' "$p"
    done
}

log_section "Environment Check"
if [ "$NATIVE_OFFLINE" = "1" ] && ! command -v gcc >/dev/null 2>&1; then
    log_error "离线模式（NATIVE_OFFLINE=1）：系统 gcc 缺失（镜像层应已 apt 安装 gcc/g++），无法编译"
    log_error "请在联网机器重建镜像并重新导出归档：invoke native.build && invoke native.save"
    exit 2
fi
"$BASE_PYTHON" --version
log_kv "cmake" "$(cmake --version | head -1) at $(command -v cmake)"
log_kv "ninja" "$(ninja --version) at $(command -v ninja)"
log_kv "clang" "$($CC --version | head -1)"
log_kv "LLVM" "$($LLVM_CONFIG --version) @ $LLVM_LIB_DIR"
# 版本行禁止用 head/sed -q 截断管道：消费者提前退出会让 Python 侧 flush 抛
# BrokenPipeError（"Exception ignored while flushing sys.stdout"）污染终端，
# 且被截断的行失去 log_kv 排版。awk 读完整个输入再在 END 块格式化，两处问题
# 一次消解。只取首行版本与 "Commercial:" 行——4.2+ 的第 2 行是
# "Update status: ... (cached, N seconds old)."（联网/时间相关，非确定性），
# 塞进日志行即为噪声。
log_kv "nuitka" "$("$BASE_PYTHON" -m nuitka --version 2>/dev/null \
    | awk 'NR==1{v=$0} /^Commercial:/ && $0 !~ /None/{c=$0} END{printf "%s (pinned, update-check off)%s", v, (c ? " (" c ")" : "")}')"

if [ "$NATIVE_OFFLINE" = "1" ]; then
    log_info "offline mode: pip 镜像配置跳过 / Nuitka 下载旗标已禁用（NUITKA_DL_FLAG 置空）"
else
    case "${PIP_MIRROR:-official}" in
        tuna)
            "$BASE_PYTHON" -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
            "$BASE_PYTHON" -m pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
            ;;
        aliyun)
            "$BASE_PYTHON" -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
            "$BASE_PYTHON" -m pip config set global.trusted-host mirrors.aliyun.com
            ;;
        *)
            log_info "pip mirror: inherited (official/镜像构建期配置)"
            ;;
    esac
fi

log_section "Ensuring numpy/scipy present"
if "$BASE_PYTHON" -c "import numpy, scipy; print(f'  numpy {numpy.__version__}, scipy {scipy.__version__} OK')"; then
    :
elif [ "$NATIVE_OFFLINE" = "1" ]; then
    log_error "离线模式（NATIVE_OFFLINE=1）：base env 缺少 numpy/scipy，且禁止联网 pip 安装"
    log_error "镜像层本应已装；请在联网机器重跑 invoke native.build 后重新导出归档"
    exit 2
else
    "$BASE_PYTHON" -m pip install --no-cache-dir "numpy>=1.26" "scipy>=1.11"
fi

mkdir -p "$NUITKA_OUT" "$VTA_NUITKA_OUT" "$XMNN_NUITKA_OUT" "$DIST_DIR"

# ── tvm：串行先编（vta/xmnn 的编译环境依赖 tvm 先行语义）─────────────────
echo ""
log_step "Nuitka-compiling tvm package"

set +e
PYTHONPATH="$TVM_PYTHON:${PYTHONPATH:-}" \
"$BASE_PYTHON" -m nuitka \
    --mode=module \
    --include-package=tvm \
    --enable-plugin="${NUITKA_PLUGINS}" \
    --nofollow-import-to=vta \
    --nofollow-import-to=xmnn \
    $(nofollow_args) \
    $TVM_COMPILE_FLAGS \
    --output-dir="$NUITKA_OUT" \
    --remove-output \
    $NUITKA_DL_FLAG \
    --quiet \
    --no-pyi-file \
    --jobs="${NUITKA_JOBS}" \
    "$TVM_PKG" 2>&1
NUITKA_TVM_EXIT=$?
set -e

if [ "$NUITKA_TVM_EXIT" -ne 0 ]; then
    log_error "tvm Nuitka compilation failed (exit $NUITKA_TVM_EXIT)"
    exit "$NUITKA_TVM_EXIT"
fi
ls -la "$NUITKA_OUT/"
log_ok "tvm Nuitka compilation complete"

# ── vta + xmnn：后台并行（串行 ~180s → 并行 ~90s）──────────────────────
echo ""
log_step "Nuitka-compiling vta & xmnn packages (parallel)"

(
    set +e
    PYTHONPATH="$VTA_PYTHON:$TVM_ROOT/python:${PYTHONPATH:-}" \
    "$BASE_PYTHON" -m nuitka \
        --mode=module \
        --include-package=vta \
        --enable-plugin="${NUITKA_PLUGINS}" \
        --nofollow-import-to=tvm \
        --include-data-dir="$VTA_CONFIG_DIR=vta_hw/config" \
        $TVM_COMPILE_FLAGS \
        --output-dir="$VTA_NUITKA_OUT" \
        --remove-output \
        $NUITKA_DL_FLAG \
        --quiet \
        --no-pyi-file \
        --jobs="${NUITKA_JOBS}" \
        "$VTA_PKG" 2>&1
    echo $? > "$BUILDER_DIR/.vta_exit"
) &

(
    set +e
    PYTHONPATH="$XMN_ROOT:$TVM_ROOT/vta/python:$TVM_ROOT/python:${PYTHONPATH:-}" \
    "$BASE_PYTHON" -m nuitka \
        --mode=module \
        --include-package=xmnn \
        --enable-plugin="${NUITKA_PLUGINS}" \
        --nofollow-import-to=tvm \
        --nofollow-import-to=vta \
        $(nofollow_args) \
        $TVM_COMPILE_FLAGS \
        --output-dir="$XMNN_NUITKA_OUT" \
        --remove-output \
        $NUITKA_DL_FLAG \
        --quiet \
        --no-pyi-file \
        --jobs="${NUITKA_JOBS}" \
        "$XMN_PKG" 2>&1
    echo $? > "$BUILDER_DIR/.xmnn_exit"
) &

set +e
wait
set -e

ls -la "$VTA_NUITKA_OUT/"
ls -la "$XMNN_NUITKA_OUT/"

NUITKA_VTA_EXIT="$(sed 's/.*=//' "$BUILDER_DIR/.vta_exit" 2>/dev/null || echo 1)"
NUITKA_XMNN_EXIT="$(sed 's/.*=//' "$BUILDER_DIR/.xmnn_exit" 2>/dev/null || echo 1)"
rm -f "$BUILDER_DIR/.vta_exit" "$BUILDER_DIR/.xmnn_exit"

if [ "$NUITKA_VTA_EXIT" -ne 0 ]; then
    log_error "vta Nuitka compilation failed (exit $NUITKA_VTA_EXIT)"
    exit "$NUITKA_VTA_EXIT"
fi
if [ "$NUITKA_XMNN_EXIT" -ne 0 ]; then
    log_error "xmnn Nuitka compilation failed (exit $NUITKA_XMNN_EXIT)"
    exit "$NUITKA_XMNN_EXIT"
fi
log_ok "vta & xmnn parallel compilation complete"

# ── scikit-build/CMake 组装 wheel（产物直接落宿主可见 DIST_DIR）───────────
echo ""
log_step "Building Wheel"
cd "$BUILDER_DIR"
log_kv "LLVM libdir" "$LLVM_LIB_DIR"
log_kv "dist dir" "$DIST_DIR"

set +e
# PYTHONPATH 必须剥离（env -u，不可写 PYTHONPATH=""——空串会被 Python 解析为
# cwd 条目）：compose 注入的 /workspace/npuusertools 下存在非 Python 包的 cmake/
# 目录（仅 xmnn_version.py.in 模板），PEP 420 使其成为命名空间包，
# scikit-build-core 的 GetRequires.cmake() 遂误判「PyPI cmake 已装」并申报
# cmake>=3.18 构建依赖；--no-isolation 下 pypa/build 的依赖检查随即以
# 「ERROR Unmet dependencies (checked against /opt/conda/bin/python)」硬失败。
# 实测：保留 PYTHONPATH → 申报 cmake>=3.18；剥离 → 回落系统 cmake 4.4.3，零申报。
# 本步骤只用 site-packages 内的 build 后端 + 显式 --config-setting 绝对路径，
# 不需要从源码树导入（PYTHONPATH 仅服务 Nuitka 编译段与交互式调试）。
env -u PYTHONPATH "$BASE_PYTHON" -m build \
    --wheel \
    --no-isolation \
    --outdir "$DIST_DIR" \
    --config-setting=cmake.define.NUITKA_OUTPUT_DIR="$NUITKA_OUT" \
    --config-setting=cmake.define.TVM_BUILD_DIR="$TVM_ROOT/build" \
    --config-setting=cmake.define.TVM_ROOT_DIR="$TVM_ROOT" \
    --config-setting=cmake.define.XMN_PYTHON_DIR="$XMN_ROOT" \
    --config-setting=cmake.define.XMN_NUITKA_OUT="$XMNN_NUITKA_OUT" \
    --config-setting=cmake.define.LLVM_LIB_DIR="$LLVM_LIB_DIR" \
    . 2>&1
BUILD_EXIT=$?
set -e
if [ "$BUILD_EXIT" -ne 0 ]; then
    log_error "Wheel build failed with exit code $BUILD_EXIT"
    exit "$BUILD_EXIT"
fi

log_section "List dist contents"
ls -la "$DIST_DIR/"
WHL_FILE="$(ls "$DIST_DIR"/xmnn-*.whl 2>/dev/null | head -1 || true)"

if [ -n "$WHL_FILE" ]; then
    WHL_SIZE="$(du -h "$WHL_FILE" | cut -f1)"
    echo ""
    log_header
    log_banner "  🎉  WHEEL BUILD COMPLETE!"
    log_footer
    log_ok "Wheel: $WHL_FILE ($WHL_SIZE)"
    log_info "10 项隔离验证：bash $SCRIPT_DIR/verify-wheel.sh"
else
    log_error "No wheel file found in $DIST_DIR/"
    exit 1
fi
