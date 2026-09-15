#!/bin/bash
# ==============================================================================
# build-tvm.sh — 在容器内编译 TVM C++ 原生库（libtvm.so），xmnn wheel 的前置
#
# 调用方式：
#   invoke xmnn.build-tvm
#   podman-compose exec xmnn bash /opt/xmnn-builder/scripts/build-tvm.sh
#
# 做什么：
#   1. 导出 main env 的 LLVM/Clang 工具链（22.1.x）与 base cp314 解释器；
#   2. cd $TVM_ROOT，invoke config -f（npu_tvm tasks.py 读 LLVM_CONFIG 生成
#      build/config.cmake，含 USE_LLVM 路径）；
#   3. 正则置 USE_EXAMPLE_TARGET_HOOKS=ON（xmnn 打包的必需目标钩子）；
#   4. invoke make（Ninja + ccache，产出 build/libtvm.so）。
#
# 幂等：已有 build/ 时增量编译；强制全量可在容器内 `rm -rf $TVM_ROOT/build`。
# 9p 提示：TVM 全量编译在 Windows 挂载的 9p 路径上很慢，可把 NPU_TVM_PATH
#          指向 WSL 原生克隆（见 overlay README §性能）。
# ==============================================================================
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/logging.sh"
LOG_FILE=/dev/null
log_enable_trap

TVM_ROOT="${TVM_ROOT:-/workspace/npu_tvm}"
BASE_PREFIX=/opt/conda
MAIN_PREFIX=/opt/conda/envs/main
BASE_PYTHON="$BASE_PREFIX/bin/python"

# ── 跨 env：base cp314 跑 invoke，main env 提供 LLVM/cmake/ninja ──────────
export PATH="$MAIN_PREFIX/bin:$BASE_PREFIX/bin:${PATH:-}"
export LD_LIBRARY_PATH="$MAIN_PREFIX/lib:$BASE_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export LLVM_CONFIG="${LLVM_CONFIG:-$MAIN_PREFIX/bin/llvm-config}"
# 编译前端默认 gcc/g++（2026-09-15：VTA FSIM 的 VLA+初始化器 Clang 22 报
# hard error、GCC 允许；LLVM 22 工具链仍用于 llvm-config/链接/守卫）。
# 可用环境变量覆盖回退 clang：CC=/opt/conda/envs/main/bin/clang CXX=.../clang++
export CC="${CC:-gcc}"
export CXX="${CXX:-g++}"

log_section "TVM build preflight"
[ -d "$TVM_ROOT" ] || {
    log_error "TVM_ROOT 不存在或未挂载：$TVM_ROOT（compose 应把 npu_tvm 挂到 /workspace/npu_tvm）"
    exit 2
}
[ -f "$TVM_ROOT/tasks.py" ] || {
    log_error "$TVM_ROOT/tasks.py 不存在：$TVM_ROOT 不是有效的 npu_tvm 源码树"
    exit 2
}
if [ ! -d "$TVM_ROOT/3rdparty/dmlc-core" ] || [ -z "$(ls -A "$TVM_ROOT/3rdparty/dmlc-core" 2>/dev/null)" ]; then
    log_error "npu_tvm git 子模块未检出（至少需要 dmlc-core）。请在宿主源码树执行："
    echo "    cd $TVM_ROOT && git submodule update --init --recursive"
    echo "  （仅 dmlc-core 亦可：git submodule update --init 3rdparty/dmlc-core）"
    exit 2
fi
log_kv "TVM_ROOT" "$TVM_ROOT"
log_kv "LLVM_CONFIG" "$LLVM_CONFIG ($("$LLVM_CONFIG" --version))"
"$BASE_PYTHON" --version

cd "$TVM_ROOT"

echo ""
log_step "1/3 inv config -f（生成 build/config.cmake，LLVM=$LLVM_CONFIG）"
"$BASE_PYTHON" -m invoke config -f

echo ""
log_step "2/3 补丁 USE_EXAMPLE_TARGET_HOOKS=ON"
CONFIG_CMAKE="$TVM_ROOT/build/config.cmake"
if [ -f "$CONFIG_CMAKE" ]; then
    "$BASE_PYTHON" - "$CONFIG_CMAKE" <<'PYEOF'
import re
import sys

path = sys.argv[1]
content = open(path, encoding="utf-8").read()
pattern = r"set\(USE_EXAMPLE_TARGET_HOOKS\s+\w+\)"
replacement = "set(USE_EXAMPLE_TARGET_HOOKS ON)"
if re.search(pattern, content):
    content = re.sub(pattern, replacement, content)
elif "USE_EXAMPLE_TARGET_HOOKS" in content:
    print("  [WARN] USE_EXAMPLE_TARGET_HOOKS 存在但形态不匹配，跳过正则补丁")
else:
    content = content.rstrip() + "\nset(USE_EXAMPLE_TARGET_HOOKS ON)\n"
open(path, "w", encoding="utf-8").write(content)
print("  [OK] USE_EXAMPLE_TARGET_HOOKS=ON")
PYEOF
else
    log_error "config.cmake 未生成于 $CONFIG_CMAKE（inv config 失败）"
    exit 1
fi

echo ""
log_step "3/3 构建 libtvm.so（inv make 配置 + ninja 主目标）"
# npu_tvm tasks.py 的 make 在 ninja 失败时吞掉非零 rc 并打印"成功"（假象），
# 只靠本脚本尾部 libtvm.so 存在性兜底；且 VTA FSIM 仿真驱动
# （vta/vta_hw/src/sim_*）是 GCC 允许、Clang 22 拒绝的「VLA + 初始化器」
# hard error（variable-sized object may not be initialized），无法 -W 降级。
# libtvm.so 是主库目标，不依赖 vta_fsim_* 独立 targets——这里保留 inv make
# 完成 cmake 配置，再用 ninja 直连主目标产出 libtvm.so（外部树零修改，
# wheel 打包亦只依赖 libtvm.so；VTA 硬件仿真库降级不在产物范围）。
"$BASE_PYTHON" -m invoke make || true
[ -f "$TVM_ROOT/build/build.ninja" ] || {
    log_error "build.ninja 未生成于 $TVM_ROOT/build（inv make 配置失败）"
    exit 1
}
ninja -C "$TVM_ROOT/build" libtvm.so

TVM_LIB="$TVM_ROOT/build/libtvm.so"
if [ -f "$TVM_LIB" ]; then
    echo ""
    log_ok "libtvm.so 就绪：$TVM_LIB ($(du -h "$TVM_LIB" | cut -f1))"
    log_info "下一步：inv xmnn.wheel（Nuitka 打包 xmnn whl）"
else
    log_error "编译结束但未找到 $TVM_LIB"
    exit 1
fi
