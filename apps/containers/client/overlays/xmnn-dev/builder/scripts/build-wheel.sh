#!/bin/bash
# ==============================================================================
# build-wheel.sh — xmnn-dev 叠加层容器内 Nuitka 打包脚本（运行时调用）
#
# 调用方式：
#   invoke xmnn.wheel                         # client 任务（经 compose exec）
#   podman-compose exec xmnn bash /opt/xmnn-builder/scripts/build-wheel.sh
#
# 流程：环境自检 → libtvm.so 前置检查 → AST PREAMBLE 注入/还原（全程统一
#       EXIT trap + 自愈状态机）→ Nuitka 串行编译 tvm → 并行 vta/xmnn
#       → python -m build 组装 wheel。
#
# 产物：$DIST_DIR/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl
#       （默认 /workspace/dist，宿主可见的 bind 挂载目录）
#
# 双 ABI 事实（rootless 基底 2026-09-14 实证）：
#   /opt/conda            = Python 3.14 cp314 GIL enabled（Nuitka 4.1.3 兼容）
#   /opt/conda/envs/main  = Python 3.14 cp314t free-threading（Nuitka 不兼容）
# 故本脚本固定以 /opt/conda/bin/python 为编译解释器；clang/LLVM/cmake 工具链
# 位于 main env（PATH 第二段，CC/CXX/LLVM_CONFIG 绝对指向）。
# ==============================================================================
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILDER_DIR="${BUILDER_DIR:-$(cd "$SCRIPT_DIR/.." && pwd)}"   # /opt/xmnn-builder

source "${SCRIPT_DIR}/lib/logging.sh"
LOG_FILE=/dev/null
log_enable_trap

# AST 注入/还原库（自愈状态机 + 原子备份；R1 F-1 后提取为可测共享库）
export AST_PYTHON=/opt/conda/bin/python
source "${SCRIPT_DIR}/lib/ast_inject.sh"

log_set_error_help '  Nuitka 打包失败排查：
  1. "fatal error: xxx.h: No such file" → 工具链缺失，检查叠加镜像构建层
  2. "LLVM error" → 确认 LLVM_CONFIG 指向 main env 的 llvm-config（22.1.x）
  3. "cloudpickle/dill serialization error" → 确认 --enable-plugin=dill-compat
  4. "Killed" / "out of memory" → 降低并发：NUITKA_JOBS=4 inv xmnn.wheel --jobs 4
  5. libtvm.so 缺失 → 先执行：inv xmnn.build-tvm（或 scripts/build-tvm.sh）
  6. 提示「已含 AST PREAMBLE 但备份缺失」→ 按提示 git checkout 对应 __init__.py
  7. 交互调试：podman-compose exec xmnn bash，cd /opt/xmnn-builder 重跑本脚本'

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
    echo "  → 请先在运行中的栈内编译 TVM：inv xmnn.build-tvm"
    echo "    （或 podman-compose exec xmnn bash /opt/xmnn-builder/scripts/build-tvm.sh）"
    exit 2
fi

# ── 统一还原兜底：无论正常结束/set -e 错误退出/子 shell 被杀导致父退出，
#    父进程 EXIT 时都按确定性备份路径幂等还原三对 __init__.py。SIGKILL 打中
#    父进程本身（机器断电/容器被 kill -9）超出 trap 能力，由 ast_inject 的
#    重跑自愈状态机收敛（见 lib/ast_inject.sh）。────────────────────────────
TVM_PYTHON="$TVM_ROOT/python"
TVM_PKG="$TVM_PYTHON/tvm"
VTA_PYTHON="$TVM_ROOT/vta/python"
VTA_CONFIG_DIR="$TVM_ROOT/vta/vta_hw/config"
VTA_PKG="$VTA_PYTHON/vta"

_restore_all() {
    ast_restore "$TVM_PKG/__init__.py" "$TVM_PKG/__init__.py.bak_tvm" 2>/dev/null || true
    ast_restore "$VTA_PKG/__init__.py" "$VTA_PKG/__init__.py.bak_vta" 2>/dev/null || true
    ast_restore "$XMN_PKG/__init__.py" "$XMN_PKG/__init__.py.bak_xmnn" 2>/dev/null || true
}
trap _restore_all EXIT

# ── ccache 配置（命名卷 /root/.ccache 由 compose 挂载持久化）──────────────
export CCACHE_MAXSIZE=5G
CLEAN_REBUILD="${CLEAN_REBUILD:-0}"
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
NOFOLLOW_IMPORTS="${NOFOLLOW_IMPORTS:-torch,torchvision,onnx2pytorch}"
TVM_COMPILE_FLAGS="${TVM_COMPILE_FLAGS:-}"

nofollow_args() {
    local IFS=',' p
    for p in ${NOFOLLOW_IMPORTS}; do
        [ -n "$p" ] && printf -- '--nofollow-import-to=%s\n' "$p"
    done
}

log_section "Environment Check"
"$BASE_PYTHON" --version
log_kv "cmake" "$(cmake --version | head -1) at $(command -v cmake)"
log_kv "ninja" "$(ninja --version) at $(command -v ninja)"
log_kv "clang" "$($CC --version | head -1)"
log_kv "LLVM" "$($LLVM_CONFIG --version) @ $LLVM_LIB_DIR"
"$BASE_PYTHON" -m nuitka --version | head -2

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

log_section "Ensuring numpy/scipy present"
"$BASE_PYTHON" -c "import numpy, scipy; print(f'  numpy {numpy.__version__}, scipy {scipy.__version__} OK')" \
    || "$BASE_PYTHON" -m pip install --no-cache-dir "numpy>=1.26" "scipy>=1.11"

mkdir -p "$NUITKA_OUT" "$VTA_NUITKA_OUT" "$XMNN_NUITKA_OUT" "$DIST_DIR"

# ── tvm：串行先编（vta/xmnn 的编译环境依赖 tvm 先行语义）─────────────────
echo ""
log_step "Nuitka-compiling tvm package"

ast_inject "$TVM_PKG/__init__.py" tvm >/dev/null
set +e
PYTHONPATH="$TVM_PYTHON:${PYTHONPATH:-}" \
"$BASE_PYTHON" -m nuitka \
    --module \
    --include-package=tvm \
    --enable-plugin="${NUITKA_PLUGINS}" \
    --nofollow-import-to=vta \
    --nofollow-import-to=xmnn \
    $(nofollow_args) \
    $TVM_COMPILE_FLAGS \
    --output-dir="$NUITKA_OUT" \
    --remove-output \
    --assume-yes-for-downloads \
    --quiet \
    --no-pyi-file \
    --jobs="${NUITKA_JOBS}" \
    "$TVM_PKG" 2>&1
NUITKA_TVM_EXIT=$?
set -e
ast_restore "$TVM_PKG/__init__.py" "$TVM_PKG/__init__.py.bak_tvm" || true

if [ "$NUITKA_TVM_EXIT" -ne 0 ]; then
    log_error "tvm Nuitka compilation failed (exit $NUITKA_TVM_EXIT)"
    exit "$NUITKA_TVM_EXIT"
fi
ls -la "$NUITKA_OUT/"
log_ok "tvm Nuitka compilation complete"

# ── vta + xmnn：后台并行（串行 ~180s → 并行 ~90s）──────────────────────
# 子 shell 被 SIGKILL 时其局部清理无法执行，由父 shell 的 _restore_all EXIT
# trap 按确定性 .bak 路径兜底。
echo ""
log_step "Nuitka-compiling vta & xmnn packages (parallel)"

(
    set +e
    if ! ast_inject "$VTA_PKG/__init__.py" vta >/dev/null 2>&1; then
        echo "2" > "$BUILDER_DIR/.vta_exit"
        exit 2
    fi
    PYTHONPATH="$VTA_PYTHON:$TVM_ROOT/python:${PYTHONPATH:-}" \
    "$BASE_PYTHON" -m nuitka \
        --module \
        --include-package=vta \
        --enable-plugin="${NUITKA_PLUGINS}" \
        --nofollow-import-to=tvm \
        --include-data-dir="$VTA_CONFIG_DIR=vta_hw/config" \
        $TVM_COMPILE_FLAGS \
        --output-dir="$VTA_NUITKA_OUT" \
        --remove-output \
        --assume-yes-for-downloads \
        --quiet \
        --no-pyi-file \
        --jobs="${NUITKA_JOBS}" \
        "$VTA_PKG" 2>&1
    echo $? > "$BUILDER_DIR/.vta_exit"
    ast_restore "$VTA_PKG/__init__.py" "$VTA_PKG/__init__.py.bak_vta" >/dev/null 2>&1 || true
) &

(
    set +e
    if ! ast_inject "$XMN_PKG/__init__.py" xmnn >/dev/null 2>&1; then
        echo "2" > "$BUILDER_DIR/.xmnn_exit"
        exit 2
    fi
    PYTHONPATH="$XMN_ROOT:$TVM_ROOT/vta/python:$TVM_ROOT/python:${PYTHONPATH:-}" \
    "$BASE_PYTHON" -m nuitka \
        --module \
        --include-package=xmnn \
        --enable-plugin="${NUITKA_PLUGINS}" \
        --nofollow-import-to=tvm \
        --nofollow-import-to=vta \
        $(nofollow_args) \
        $TVM_COMPILE_FLAGS \
        --output-dir="$XMNN_NUITKA_OUT" \
        --remove-output \
        --assume-yes-for-downloads \
        --quiet \
        --no-pyi-file \
        --jobs="${NUITKA_JOBS}" \
        "$XMN_PKG" 2>&1
    echo $? > "$BUILDER_DIR/.xmnn_exit"
    ast_restore "$XMN_PKG/__init__.py" "$XMN_PKG/__init__.py.bak_xmnn" >/dev/null 2>&1 || true
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
"$BASE_PYTHON" -m build \
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
