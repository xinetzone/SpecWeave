#!/bin/bash
# 在 caffe-ffi (caffe-ffi-jupyter) 容器内运行 cross_ops 对比
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export KMP_DUPLICATE_LIB_OK=TRUE
export PATH="$CONDA_PREFIX/bin:$PATH"

ASSETS=/SpecWeave/.trae/specs/caffe-comprehensive-comparison-test/test-assets
OUT=/tmp/cross_ffi
mkdir -p "$OUT"
echo "=== numpy ==="
python -c "import numpy; print(numpy.__version__)"
echo "=== run cross_ops (caffe-ffi) ==="
python "$ASSETS/cross_ops.py" "$OUT" all 2>&1
echo "=== output files ==="
ls -la "$OUT"
echo "DONE_FFI_CROSS"