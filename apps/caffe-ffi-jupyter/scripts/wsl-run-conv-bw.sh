#!/bin/bash
# WSL entry: Run Conv backward tests in Docker with enhanced logging + perf tracking
# Usage: bash scripts/run-conv-backward-tests.sh [pytest-k-filter]
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONTAINER="caffe-ffi-jupyter"
FILTER="${1:-}"

echo "=== Copying test script to container ==="
docker cp "$SCRIPT_DIR/run-conv-backward-tests.sh" "${CONTAINER}:/tmp/_run_conv_bw.sh"
docker exec "${CONTAINER}" chmod +x /tmp/_run_conv_bw.sh

echo "=== Running Conv backward tests ==="
if [ -n "$FILTER" ]; then
    # Override the pytest command with a filter
    docker exec "${CONTAINER}" bash -c "
source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && \
cd /SpecWeave/projects/xuanspace/libs/caffe-ffi && \
cp build/python/caffe_ffi/_caffe_ffi.so python/caffe_ffi/_caffe_ffi.so 2>/dev/null; \
rm -f tests/python/.temp/perf_log_*.csv; \
cd tests/python && \
export CAFFE_FFI_PERF_GC_MODE=quick CAFFE_FFI_CPP_LOG_LEVEL=4 CAFFE_FFI_LEAKCHECK_GC=quick \
       KMP_DUPLICATE_LIB_OK=TRUE PYTHONUNBUFFERED=1 && \
python -m pytest test_conv_backward.py -v --tb=long -k '$FILTER' 2>&1
"
else
    docker exec "${CONTAINER}" bash /tmp/_run_conv_bw.sh 2>&1
fi
echo ""
echo "=== Complete ==="
