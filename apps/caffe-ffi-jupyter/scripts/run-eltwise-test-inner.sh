#!/bin/bash
set -e
export KMP_DUPLICATE_LIB_OK=TRUE
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi

CAFFE_FFI_DIR="/SpecWeave/projects/xuanspace/libs/caffe-ffi"

echo "=== Step 1: Clean build ==="
cd "$CAFFE_FFI_DIR"
rm -rf build

echo "=== Step 2: Rebuild caffe-ffi (editable install) ==="
TVM_FFI_CMAKE_DIR=$(python -c "import tvm_ffi, os; print(os.path.dirname(tvm_ffi.__file__))")
echo "tvm_ffi cmake dir: $TVM_FFI_CMAKE_DIR"
CAFFE_FFI_CMAKE_ARGS="-DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON;-DCMAKE_BUILD_RPATH_USE_ORIGIN=ON;-DCMAKE_SKIP_BUILD_RPATH=OFF;-DCMAKE_BUILD_WITH_INSTALL_RPATH=ON"
CAFFE_FFI_CMAKE_ARGS="${CAFFE_FFI_CMAKE_ARGS};-DCAFFE_FFI_ENABLE_BACKTRACE=OFF"
CAFFE_FFI_CMAKE_ARGS="${CAFFE_FFI_CMAKE_ARGS};-Dcaffe-ffi_DIR=${TVM_FFI_CMAKE_DIR}"
CAFFE_FFI_CMAKE_ARGS="${CAFFE_FFI_CMAKE_ARGS};-DCMAKE_PREFIX_PATH=$CONDA_PREFIX;-DCAFFE_FFI_BUILD_TESTS=OFF"
SKBUILD_CMAKE_ARGS="$CAFFE_FFI_CMAKE_ARGS" pip install --no-cache-dir --no-build-isolation -e "$CAFFE_FFI_DIR" 2>&1 | tail -25

echo ""
echo "=== Step 3: Copy .so ==="
if [ -f "$CAFFE_FFI_DIR/build/python/caffe_ffi/_caffe_ffi.so" ]; then
    cp "$CAFFE_FFI_DIR/build/python/caffe_ffi/_caffe_ffi.so" "$CAFFE_FFI_DIR/python/caffe_ffi/_caffe_ffi.so"
    echo "Copied .so successfully"
fi

echo ""
echo "=== Step 4: Verify import ==="
python -c "from caffe_ffi import _ffi_api; print('cpp_available:', _ffi_api.is_available())"

echo ""
echo "=== Step 5: Run Eltwise Backward tests ==="
cd "$CAFFE_FFI_DIR/tests/python"
export CAFFE_FFI_PERF_GC_MODE=quick
export CAFFE_FFI_CPP_LOG_LEVEL=2
export PYTHONUNBUFFERED=1
python -m pytest test_eltwise_backward.py -v --tb=long 2>&1

echo ""
echo "=== Step 6: Regression - Scale + Bias + Dropout ==="
python -m pytest test_scale_backward.py test_bias_backward.py test_dropout_backward.py -v --tb=short 2>&1 | tail -40

echo ""
echo "=== ALL TESTS COMPLETED ==="
