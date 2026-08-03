#!/bin/bash
# Recompile caffe-ffi C++ extension and run Dropout Backward tests in Docker
set -e

CONTAINER="${CONTAINER:-caffe-ffi}"
CAFFE_FFI_DIR="/SpecWeave/projects/xuanspace/libs/caffe-ffi"

echo "=== Checking container ==="
docker ps --filter "name=$CONTAINER" --format "{{.Names}} {{.Status}}"

echo ""
echo "=== Step 1: Recompile C++ extension (editable rebuild) ==="
docker exec "$CONTAINER" bash -lc "source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && cd $CAFFE_FFI_DIR && pip install -e . --no-build-isolation -v 2>&1 | tail -30"

echo ""
echo "=== Step 2: Verify .so is updated ==="
docker exec "$CONTAINER" bash -lc "source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && cd $CAFFE_FFI_DIR && ls -la build/python/caffe_ffi/_caffe_ffi.so python/caffe_ffi/_caffe_ffi.so && cp build/python/caffe_ffi/_caffe_ffi.so python/caffe_ffi/_caffe_ffi.so && python -c 'from caffe_ffi import _ffi_api; print(\"cpp_available:\", _ffi_api.is_available())'"

echo ""
echo "=== Step 3: Run Dropout Backward tests ==="
docker exec "$CONTAINER" bash -lc "source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && cd $CAFFE_FFI_DIR/tests/python && export CAFFE_FFI_PERF_GC_MODE=quick && export CAFFE_FFI_CPP_LOG_LEVEL=3 && export KMP_DUPLICATE_LIB_OK=TRUE && export PYTHONUNBUFFERED=1 && python -m pytest test_dropout_backward.py -v --tb=short 2>&1"

echo ""
echo "=== Step 4: Quick regression - run other backward tests to verify no breakage ==="
docker exec "$CONTAINER" bash -lc "source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && cd $CAFFE_FFI_DIR/tests/python && export CAFFE_FFI_PERF_GC_MODE=quick && export KMP_DUPLICATE_LIB_OK=TRUE && python -m pytest test_pooling_backward.py test_batch_norm_backward.py test_conv_backward.py test_inner_product_backward.py -v --tb=short 2>&1 | tail -40"

echo ""
echo "=== Done ==="
