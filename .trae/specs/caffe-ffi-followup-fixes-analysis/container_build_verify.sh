#!/bin/bash
# =============================================================================
# container_build_verify.sh
#
# 在 `caffe-ffi-jupyter` 容器内一键执行「native 重编译 + A-001 修复验证」闭环。
#
# 功能：
#   1) 装载 conda env（caffe-ffi / Python 3.14）
#   2) 定位本地 tvm-ffi 源码并 editable 重编译（caffe-ffi 的 FFI 依赖，须与本地一致）
#   3) `pip install -e . --no-build-isolation` 重编译 caffe-ffi 的 _caffe_ffi.so
#   4) 运行 a001_verify_fix.py（conv1 权重真实 / 无 NaN / 与 caffex 对齐 三项断言）
#
# 特性：
#   - 幂等可重入：已编译且 import 成功时跳过重编译（用 --force 强制重编译）
#   - 失败即停：每个阶段失败均输出明确错误信息并以非零退出码结束
#
# 用法：
#   在容器内（已挂载 /SpecWeave）：
#     bash /SpecWeave/.trae/specs/caffe-ffi-followup-fixes-analysis/container_build_verify.sh
#   强制重编译：
#     FORCE=1 bash container_build_verify.sh
#
# 退出码：
#   0 = 全部通过；1 = 编译/验证失败；2 = 环境不满足（conda env / 源码缺失）
# =============================================================================
set -u   # 不 set -e，改为逐阶段显式检查，便于输出明确错误

# ---- 0. 参数与环境 ----
FORCE="${FORCE:-0}"
SPEC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SPEC_DIR/../../.." && pwd)"          # /SpecWeave
CAFFE_FFI_DIR="$REPO_ROOT/projects/xuanspace/libs/caffe-ffi"
TVM_FFI_DIR="$REPO_ROOT/projects/xuanspace/vendor/tvm-ffi"
VERIFY_PY="$SPEC_DIR/a001_verify_fix.py"
CONDA_ENV="caffe-ffi"
MODEL_DIR="$REPO_ROOT/.trae/specs/caffe-comprehensive-comparison-test/test-assets/models"

fail() {
  echo "[container_build_verify] ERROR: $*" >&2
  exit 1
}

# ---- 1. 装载 conda env ----
CONDA_BASE="/opt/conda"
if [ ! -f "$CONDA_BASE/etc/profile.d/conda.sh" ]; then
  # 兼容非 /opt/conda 的 conda 位置
  CONDA_BASE="$(conda info --base 2>/dev/null || true)"
  [ -n "$CONDA_BASE" ] || fail "未找到 conda。请确认容器内已安装 Miniconda（默认 /opt/conda）。"
fi
source "$CONDA_BASE/etc/profile.d/conda.sh"
if ! conda env list | awk '{print $1}' | grep -qx "$CONDA_ENV"; then
  fail "conda env '$CONDA_ENV' 不存在。请先构建 caffe-ffi-jupyter 镜像。"
fi
conda activate "$CONDA_ENV"
export PATH="$CONDA_BASE/envs/$CONDA_ENV/bin:$PATH"
# Windows 多 OpenMP 运行时副本共存时允许继续运行
export KMP_DUPLICATE_LIB_OK=TRUE
echo "[1/5] conda env activated: $(which python) $($CONDA_BASE/envs/$CONDA_ENV/bin/python --version 2>&1)"

# ---- 2. 前置校验：源码与模型存在 ----
echo "[2/5] 前置校验"
[ -d "$CAFFE_FFI_DIR" ]                    || fail "caffe-ffi 源码目录缺失: $CAFFE_FFI_DIR"
[ -f "$CAFFE_FFI_DIR/pyproject.toml" ]     || fail "caffe-ffi 缺少 pyproject.toml: $CAFFE_FFI_DIR"
[ -d "$TVM_FFI_DIR" ]                      || fail "tvm-ffi 源码缺失: $TVM_FFI_DIR"
[ -f "$VERIFY_PY" ]                        || fail "验证脚本缺失: $VERIFY_PY"
[ -f "$MODEL_DIR/inceptionv1.prototxt" ]   || fail "测试模型 prototxt 缺失: $MODEL_DIR/inceptionv1.prototxt"
[ -f "$MODEL_DIR/inceptionv1.caffemodel" ] || fail "测试模型 caffemodel 缺失: $MODEL_DIR/inceptionv1.caffemodel"
echo "  校验通过。"

# ---- 3. 重编译本地 tvm-ffi（caffe-ffi 的 FFI 依赖，保证版本一致）----
echo "[3/5] 编译本地 tvm-ffi: $TVM_FFI_DIR"
# 无 .git 场景下 setuptools-scm 无法探测版本，用显式版本号
export SETUPTOOLS_SCM_PRETEND_VERSION="${SETUPTOOLS_SCM_PRETEND_VERSION:-0.1.13.post2}"
if [ "$FORCE" = "1" ] || ! python -c "import tvm_ffi; print(tvm_ffi.__version__)"; then
  ( cd "$TVM_FFI_DIR"                                   \
    && TVM_FFI_BUILD_PYTHON_MODULE=ON python -m pip install -e . --no-build-isolation >/dev/null 2>&1 )
  ret=$?
  [ $ret -eq 0 ] || fail "tvm-ffi 编译失败（exit=$ret）。查看上述完整日志。"
  # 强制使用 vendor 内置 TypeTraits，避免与已安装版本冲突
  export TVM_FFI_USE_BUILTIN_TYPETRAITS=1
fi
echo "  tvm_ffi.$(python -c "import tvm_ffi; print(tvm_ffi.__version__)") 就绪。"

# ---- 4. editable 重编译 caffe-ffi native（_caffe_ffi.so）----
echo "[4/5] 编译 caffe-ffi native: $CAFFE_FFI_DIR"
if [ "$FORCE" = "1" ] || ! python -c "import caffe_ffi" >/dev/null 2>&1; then
  # 显式指定编译宏：启用 OpenMP 与 COW Phase3（Split 层 lazy reshape 依赖）
  export CAFFE_FFI_CMAKE_ARGS="${CAFFE_FFI_CMAKE_ARGS:--DCAFFE_FFI_ENABLE_COW_PHASE3=ON -DCAFFE_USE_OPENMP=ON}"
  ( cd "$CAFFE_FFI_DIR" \
    && python -m pip install -e . --no-build-isolation >/dev/null 2>&1 )
  ret=$?
  [ $ret -eq 0 ] || fail "caffe-ffi 编译失败（exit=$ret）。查看上述完整日志。"
  # editable 安装后新 .so 与重新生成的 caffe_pb2.py 可能未同步到包目录，手动复制确保加载到最新版本
  SO="$CAFFE_FFI_DIR/build/python/caffe_ffi/_caffe_ffi.so"
  if [ -f "$SO" ]; then
    cp -f "$SO" "$CAFFE_FFI_DIR/python/caffe_ffi/_caffe_ffi.so"
  fi
  PB2="$CAFFE_FFI_DIR/build/caffe_proto_gen/caffe/proto/caffe_pb2.py"
  if [ -f "$PB2" ]; then
    cp -f "$PB2" "$CAFFE_FFI_DIR/python/caffe_ffi/caffe_pb2.py"
  fi
fi
echo "  caffe_ffi.$(python -c "import caffe_ffi; print(caffe_ffi.__version__)") native=$(
  python -c "import caffe_ffi; print(caffe_ffi.is_available())") 就绪。"
[ "$(python -c 'import caffe_ffi; print(caffe_ffi.is_available())')" = "True" ] \
  || fail "caffe_ffi native 扩展不可用：import OK 但 is_available()=False。请强制重编译（FORCE=1）。"

# ---- 5. 运行 A-001 验证 ----
echo "[5/5] 运行 A-001 修复验证: $VERIFY_PY"
python "$VERIFY_PY"
ret=$?
if [ $ret -ne 0 ]; then
  fail "A-001 验证未通过（exit=$ret）。请检查上述 FAIL 项。"
fi

echo "================================================================"
echo "[OK] 编译 + A-001 验证全部通过。"
echo "================================================================"
exit 0