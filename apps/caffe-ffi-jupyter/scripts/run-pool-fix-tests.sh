#!/bin/bash
set -e
export KMP_DUPLICATE_LIB_OK=TRUE
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi

CAFFE_FFI_DIR="/SpecWeave/projects/xuanspace/libs/caffe-ffi"

echo "=== Run Pooling Backward tests (fixed ceil_mode default) ==="
cd "$CAFFE_FFI_DIR/tests/python"
export CAFFE_FFI_PERF_GC_MODE=quick
export CAFFE_FFI_CPP_LOG_LEVEL=2
export PYTHONUNBUFFERED=1
python -m pytest test_pooling_backward.py -v --tb=long 2>&1

echo ""
echo "=== Quick regression: Scale + Bias + Dropout backward tests ==="
python -m pytest test_scale_backward.py test_bias_backward.py test_dropout_backward.py -v --tb=short 2>&1 | tail -20

echo ""
echo "=== ALL REGRESSION TESTS COMPLETED ==="
