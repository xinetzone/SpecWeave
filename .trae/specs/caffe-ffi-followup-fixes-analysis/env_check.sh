#!/bin/bash
# 在 caffe-ffi 容器内检查环境
set +e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi 2>/dev/null
echo "python: $(which python)"
echo "python version: $(python --version 2>&1)"
echo "--- caffe_ffi import ---"
python -c "import caffe_ffi; print('version:', getattr(caffe_ffi, '__version__', 'N/A'))" 2>&1 | head -10
echo "--- tvm_ffi import ---"
python -c "import tvm_ffi; print('version:', getattr(tvm_ffi, '__version__', 'N/A'))" 2>&1 | head -5
echo "--- find caffe_ffi install ---"
python -c "import caffe_ffi, os; p=os.path.dirname(caffe_ffi.__file__); print(p); print([f for f in os.listdir(p) if f.endswith('.so')])" 2>&1 | head -10