#!/bin/bash
# 手动编译 tvm-ffi + caffe-ffi（显式指定 conda python，绕过 /opt/venv 干扰）
# 用 python -m pip 确保使用 conda 环境的 pip
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export PATH="$CONDA_PREFIX/bin:$PATH"
export CMAKE_GENERATOR=Ninja
export CMAKE_MAKE_PROGRAM="$(which ninja)"
export CMAKE_PREFIX_PATH="$CONDA_PREFIX"
export Python_EXECUTABLE="$(which python)"
export Python_INCLUDE_DIR="$CONDA_PREFIX/include/python3.14"
export Python_LIBRARY="$CONDA_PREFIX/lib/libpython3.14.so"

echo "=== python: $(which python) $(python --version) ==="

echo "===== 步骤1: 编译安装 tvm-ffi (来自 vendor 源码) ====="
cd /workspace/projects/xuanspace/vendor/tvm-ffi
rm -rf build /tmp/tvm-ffi-dist
export SETUPTOOLS_SCM_PRETEND_VERSION="0.1.13.post2"
python -m pip install --no-build-isolation --no-cache-dir \
  -Ccmake.define.TVM_FFI_USE_LIBBACKTRACE=OFF \
  -Ccmake.define.TVM_FFI_BUILD_TESTS=OFF \
  -Ccmake.define.TVM_FFI_BUILD_PYTHON_MODULE=ON \
  -Ccmake.define.Python_EXECUTABLE="$(which python)" \
  -e . 2>&1 | tail -40
echo "TVM_FFI_PIP_EXIT=$?"

echo "===== 验证 tvm_ffi ====="
python -c "import tvm_ffi; print('tvm_ffi:', tvm_ffi.__version__); print('file:', tvm_ffi.__file__)" 2>&1 || echo "tvm_ffi import FAILED"

echo "===== 步骤2: 编译安装 caffe-ffi ====="
cd /workspace/projects/xuanspace/libs/caffe-ffi
rm -rf build
python -m pip install --no-build-isolation --no-cache-dir \
  -Ccmake.define.CAFFE_CPU_ONLY=ON \
  -Ccmake.define.CAFFE_USE_BLAS=ON \
  -Ccmake.define.CAFFE_FFI_BUILD_TESTS=OFF \
  -Ccmake.define.CAFFE_FFI_ENABLE_COW_PHASE3=ON \
  -Ccmake.define.Python_EXECUTABLE="$(which python)" \
  -e . 2>&1 | tail -40
echo "CAFFE_FFI_PIP_EXIT=$?"

echo "===== 最终验证 ====="
python - <<PY
import tvm_ffi
print("tvm_ffi:", tvm_ffi.__version__)
import caffe_ffi
print("caffe_ffi:", caffe_ffi.__version__)
print("native:", caffe_ffi._ffi_api.is_available())
print("file:", caffe_ffi.__file__)
PY