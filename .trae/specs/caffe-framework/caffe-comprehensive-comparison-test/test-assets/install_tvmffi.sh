#!/bin/bash
# 从本地最新源码安装 tvm_ffi（/SpecWeave/projects/xuanspace/vendor/tvm-ffi）
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export PATH="$CONDA_PREFIX/bin:$PATH"

echo "=== python: $(which python) $(python --version) ==="
echo "=== 当前 tvm_ffi 状态 ==="
python -c "import tvm_ffi, os; print('  version:', tvm_ffi.__version__); print('  file:', tvm_ffi.__file__)" 2>&1 || echo "  tvm_ffi 未安装"

SRC="/SpecWeave/projects/xuanspace/vendor/tvm-ffi"
echo ""
echo "=== 源码目录: $SRC ==="
ls -la "$SRC/pyproject.toml" 2>&1

echo ""
echo "=== 编译安装 tvm_ffi (来自本地源码) ==="
cd "$SRC"
export SETUPTOOLS_SCM_PRETEND_VERSION="0.1.13.post2"
python -m pip install --no-build-isolation --no-cache-dir \
  -Ccmake.define.TVM_FFI_USE_LIBBACKTRACE=OFF \
  -Ccmake.define.TVM_FFI_BUILD_TESTS=OFF \
  -Ccmake.define.TVM_FFI_BUILD_PYTHON_MODULE=ON \
  -Ccmake.define.TVM_FFI_ATTACH_DEBUG_SYMBOLS=OFF \
  -Ccmake.define.Python_EXECUTABLE="$(which python)" \
  -e . 2>&1 | tail -50
echo "TVM_FFI_PIP_EXIT=${PIPESTATUS[0]}"

echo ""
echo "=== 验证 tvm_ffi ==="
python -c "import tvm_ffi, os; print('  version:', tvm_ffi.__version__); print('  file:', tvm_ffi.__file__)" 2>&1 || echo "tvm_ffi import FAILED"

echo ""
echo "=== 验证 caffe_ffi native ==="
python -c "import caffe_ffi; print('  caffe_ffi:', caffe_ffi.__version__); print('  native:', caffe_ffi._ffi_api.is_available())" 2>&1 || echo "caffe_ffi import FAILED"