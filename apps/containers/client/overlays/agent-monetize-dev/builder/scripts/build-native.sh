#!/bin/bash
# ==============================================================================
# build-native.sh — agent-monetize tvm-ffi 原生 C++ 模块编译（运行时调用）
#
# 调用：invoke monetize.build-native
#       podman-compose exec monetize bash /opt/monetize-builder/scripts/build-native.sh
#
# 产物：$SRC_ROOT/native/build/score_opportunity.so
#   - clang++ 单文件编译（-shared -fPIC），头/库来自 pip 包 apache-tvm-ffi
#     （tvm_ffi/include + tvm_ffi/lib/libtvm_ffi.so），无需系统/conda LLVM
#   - patchelf 写绝对 rpath 指向容器内 tvm_ffi/lib，使 Python 端
#     ctypes.CDLL(score_opportunity.so) 能自动解析其依赖 libtvm_ffi.so
# ==============================================================================
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILDER_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
source "${SCRIPT_DIR}/lib/logging.sh"
LOG_FILE=/dev/null
log_enable_trap

SRC_ROOT="${SRC_ROOT:-/workspace/agent-monetize}"
CC="${CC:-clang++}"
SRC_CC="$SRC_ROOT/native/score_opportunity.cc"
OUT_DIR="$SRC_ROOT/native/build"
OUT_SO="$OUT_DIR/score_opportunity.so"
BASE_PYTHON=/opt/conda/bin/python

if [ ! -f "$SRC_CC" ]; then
    log_error "未找到 C++ 源码：$SRC_CC（SRC_ROOT=$SRC_ROOT 挂载是否正确？）"
    exit 2
fi
if ! command -v "$CC" >/dev/null 2>&1; then
    log_error "未找到 clang++（镜像 apt 层应已安装）"
    exit 2
fi

# tvm_ffi 头/库路径由已安装的 apache-tvm-ffi pip 包动态定位（不写死版本）
SITE_PACKAGES="$("$BASE_PYTHON" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')"
TVM_FFI_INC="$SITE_PACKAGES/tvm_ffi/include"
TVM_FFI_LIB="$SITE_PACKAGES/tvm_ffi/lib"
if [ ! -f "$TVM_FFI_INC/tvm/ffi/tvm_ffi.h" ]; then
    log_error "缺少 tvm-ffi 头文件：$TVM_FFI_INC/tvm/ffi/tvm_ffi.h（镜像应已 pip 装 apache-tvm-ffi）"
    exit 2
fi
if [ ! -f "$TVM_FFI_LIB/libtvm_ffi.so" ]; then
    log_error "缺少 libtvm_ffi.so：$TVM_FFI_LIB（apache-tvm-ffi pip 包异常）"
    exit 2
fi

log_section "Environment Check"
"$BASE_PYTHON" --version
log_kv "clang++" "$($CC --version | head -1)"
log_kv "tvm_ffi include" "$TVM_FFI_INC"
log_kv "tvm_ffi lib" "$TVM_FFI_LIB ($(ls "$TVM_FFI_LIB"/libtvm_ffi.so))"
command -v patchelf >/dev/null && log_kv "patchelf" "$(patchelf --version)" || \
    log_warn "patchelf 缺失（rpath 将无法写入，运行时需依赖 LD_LIBRARY_PATH）"

mkdir -p "$OUT_DIR"

echo ""
log_step "Compiling score_opportunity.cc → score_opportunity.so"
# -shared -fPIC 生成 Python 可 dlopen 的共享库；-std=c++17 对齐 tvm-ffi 头；
# -O2 与 Windows build.ps1 的 /O2 等价；链接 tvm_ffi 运行时（-ltvm_ffi）。
"$CC" -std=c++17 -shared -fPIC -O2 \
    -I"$TVM_FFI_INC" \
    "$SRC_CC" \
    -L"$TVM_FFI_LIB" -ltvm_ffi \
    -Wl,-rpath,"$TVM_FFI_LIB" \
    -o "$OUT_SO"

if [ ! -f "$OUT_SO" ]; then
    log_error "编译结束但未生成 $OUT_SO"
    exit 1
fi

# 显式 patchelf 兜底（-Wl,-rpath 已写入，patchelf 再确保一次，幂等）
if command -v patchelf >/dev/null 2>&1; then
    patchelf --set-rpath "$TVM_FFI_LIB" "$OUT_SO" || true
fi

echo ""
log_kv "NATIVE_SO" "$OUT_SO ($(du -h "$OUT_SO" | cut -f1))"
echo "== readelf NEEDED/RPATH =="
(readelf -d "$OUT_SO" 2>/dev/null | grep -E "NEEDED|RPATH|RUNPATH" | head) || true
echo ""
log_ok "原生 tvm-ffi 模块编译完成；下一步: invoke monetize.smoke（验证 backend=native）"
