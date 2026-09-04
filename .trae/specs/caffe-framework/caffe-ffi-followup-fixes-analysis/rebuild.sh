#!/bin/bash
# 重建 caffe-ffi native 扩展（含 A-001 net.cpp 修复）
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export PATH=/opt/conda/envs/caffe-ffi/bin:$PATH
export KMP_DUPLICATE_LIB_OK=TRUE
cd /SpecWeave/projects/xuanspace/libs/caffe-ffi
echo "=== rebuilding caffe-ffi (editable, no-build-isolation) ==="
pip install -e . --no-build-isolation 2>&1 | tail -30
echo "=== rebuild done, check .so ==="
ls -la python/caffe_ffi/_caffe_ffi.so
python -c "import caffe_ffi; print('import OK, so:', caffe_ffi.__file__)"