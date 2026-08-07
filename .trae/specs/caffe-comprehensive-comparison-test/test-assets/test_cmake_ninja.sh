#!/bin/bash
# 检查 ninja + 用 ninja generator 干净配置
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
echo "=== ninja ==="
which ninja; ninja --version 2>&1
echo "=== make ==="
which make 2>&1 || echo "make NOT FOUND"
echo "=== cmake ==="
cmake --version 2>&1 | head -1
echo "=== python ninja ==="
python -c "import ninja; print('py ninja', ninja.__version__)" 2>&1
echo "=== 干净 cmake 配置（ninja generator）==="
cd /workspace/projects/xuanspace/vendor/tvm-ffi
rm -rf /tmp/tvm-ffi-build
cmake . -B /tmp/tvm-ffi-build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DTVM_FFI_USE_LIBBACKTRACE=OFF \
  -DTVM_FFI_BUILD_TESTS=OFF \
  -DTVM_FFI_BUILD_PYTHON_MODULE=ON \
  -DCMAKE_CXX_COMPILER=/opt/conda/envs/caffe-ffi/bin/x86_64-conda-linux-gnu-c++ \
  -DCMAKE_C_COMPILER=/opt/conda/envs/caffe-ffi/bin/x86_64-conda-linux-gnu-cc \
  -DCMAKE_MAKE_PROGRAM=$(which ninja) \
  -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" 2>&1 | tail -40
echo "CMAKE_EXIT=$?"