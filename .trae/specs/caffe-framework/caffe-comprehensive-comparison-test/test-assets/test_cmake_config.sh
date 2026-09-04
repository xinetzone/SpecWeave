#!/bin/bash
# 在容器本地路径（非挂载）做干净 cmake 配置，隔离 Windows mount 问题
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
cd /workspace/projects/xuanspace/vendor/tvm-ffi
rm -rf /tmp/tvm-ffi-build
echo "=== 干净 cmake 配置（本地路径）==="
cmake . -B /tmp/tvm-ffi-build -DCMAKE_BUILD_TYPE=Release \
  -DTVM_FFI_USE_LIBBACKTRACE=OFF \
  -DTVM_FFI_BUILD_TESTS=OFF \
  -DTVM_FFI_BUILD_PYTHON_MODULE=ON \
  -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" 2>&1 | tail -30
echo "CMAKE_EXIT=$?"