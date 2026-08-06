#!/bin/bash
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi

echo "=== Python version ==="
python --version

echo ""
echo "=== caffe_ffi import check ==="
python -c "import caffe_ffi; print('caffe_ffi version:', caffe_ffi.__version__)"

echo ""
echo "=== Find _caffe_ffi.so ==="
CAFFE_SO=$(python -c "import caffe_ffi, os, glob; sos=glob.glob(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi*.so')); print(sos[0] if sos else '')")
if [ -z "$CAFFE_SO" ] || [ ! -f "$CAFFE_SO" ]; then
    echo "ERROR: _caffe_ffi*.so not found!"
    exit 1
fi
echo "Found: $CAFFE_SO"

echo ""
echo "=== RPATH ==="
patchelf --print-rpath "$CAFFE_SO" 2>/dev/null || echo "N/A (patchelf failed)"

echo ""
echo "=== ldd output ==="
ldd "$CAFFE_SO"

echo ""
echo "=== Check for 'not found' ==="
if ldd "$CAFFE_SO" 2>/dev/null | grep -q 'not found'; then
    echo "FAIL: Some shared library dependencies are NOT FOUND"
    ldd "$CAFFE_SO" | grep 'not found'
    exit 1
else
    echo "PASS: All shared library dependencies resolved"
fi

echo ""
echo "=== Check libtvm_ffi.so specifically ==="
if ldd "$CAFFE_SO" 2>/dev/null | grep -q 'libtvm_ffi'; then
    echo "libtvm_ffi.so is linked:"
    ldd "$CAFFE_SO" | grep 'libtvm_ffi'
else
    echo "WARNING: libtvm_ffi.so not directly linked (may be loaded dynamically)"
fi

echo ""
echo "=== LD_LIBRARY_PATH ==="
echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH"

echo ""
echo "=== Check _libs directory ==="
PKG_DIR=$(python -c "import caffe_ffi, os; print(os.path.dirname(caffe_ffi.__file__))")
LIBS_DIR="$PKG_DIR/_libs"
if [ -d "$LIBS_DIR" ]; then
    echo "_libs directory exists: $LIBS_DIR"
    ls -la "$LIBS_DIR"
else
    echo "_libs directory not found at $LIBS_DIR"
fi
