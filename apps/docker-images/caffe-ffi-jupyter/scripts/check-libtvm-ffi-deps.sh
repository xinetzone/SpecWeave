#!/bin/bash
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi

TVM_FFI_SO="/SpecWeave/projects/xuanspace/vendor/tvm-ffi/build/lib/libtvm_ffi.so"

echo "=== libtvm_ffi.so exists check ==="
if [ -f "$TVM_FFI_SO" ]; then
    echo "Found: $TVM_FFI_SO"
else
    echo "NOT FOUND at $TVM_FFI_SO"
    # Try to find it
    echo "Searching..."
    find /opt/conda/envs/caffe-ffi -name "libtvm_ffi.so" 2>/dev/null
    find /SpecWeave -name "libtvm_ffi.so" 2>/dev/null
    exit 1
fi

echo ""
echo "=== libtvm_ffi.so RPATH ==="
patchelf --print-rpath "$TVM_FFI_SO" 2>/dev/null || echo "N/A"

echo ""
echo "=== libtvm_ffi.so ldd ==="
ldd "$TVM_FFI_SO"

echo ""
echo "=== libtvm_ffi.so 'not found' check ==="
if ldd "$TVM_FFI_SO" 2>/dev/null | grep -q 'not found'; then
    echo "FAIL: libtvm_ffi.so has unresolved dependencies!"
    ldd "$TVM_FFI_SO" | grep 'not found'
    exit 1
else
    echo "PASS: libtvm_ffi.so all dependencies resolved"
fi
