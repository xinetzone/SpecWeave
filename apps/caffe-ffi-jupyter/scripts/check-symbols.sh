#!/bin/bash
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export PATH="$CONDA_PREFIX/bin:/opt/conda/bin:$PATH"

# Check which libtvm_ffi has the symbol
echo "=== Checking libtvm_ffi.so versions ==="
SP_DIR=$(python -c "import site; print(site.getsitepackages()[0])")

echo "libtvm_ffi.so in caffe_ffi/ (bundled):"
nm -D "$SP_DIR/caffe_ffi/libtvm_ffi.so" 2>/dev/null | grep -i CustomAllocator || echo "  TVMFFIGetCustomAllocator NOT FOUND"
echo ""

echo "libtvm_ffi.so in PREFIX/lib:"
nm -D "$CONDA_PREFIX/lib/libtvm_ffi.so" 2>/dev/null | grep -i CustomAllocator || echo "  TVMFFIGetCustomAllocator NOT FOUND"
echo ""

echo "libtvm_ffi.so from pip tvm_ffi package:"
TVM_FFI_LIB=$(python -c "
import tvm_ffi, os
base = os.path.dirname(tvm_ffi.__file__)
for root, dirs, files in os.walk(base):
    for f in files:
        if 'libtvm_ffi' in f and f.endswith('.so'):
            print(os.path.join(root, f))
            break
" 2>/dev/null)
if [ -n "$TVM_FFI_LIB" ]; then
    echo "  Path: $TVM_FFI_LIB"
    nm -D "$TVM_FFI_LIB" 2>/dev/null | grep -i CustomAllocator || echo "  TVMFFIGetCustomAllocator NOT FOUND"
fi
echo ""

echo "=== _caffe_ffi.so imports ==="
nm -D "$SP_DIR/caffe_ffi/_caffe_ffi.so" 2>/dev/null | grep -i TVMFFI | head -10
echo ""

echo "=== ldd _caffe_ffi.so (which libtvm_ffi does it pick up?) ==="
ldd "$SP_DIR/caffe_ffi/_caffe_ffi.so" 2>/dev/null | grep -i tvm
