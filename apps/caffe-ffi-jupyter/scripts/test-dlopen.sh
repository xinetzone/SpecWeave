#!/bin/bash
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export PATH="$CONDA_PREFIX/bin:/opt/conda/bin:$PATH"

SP_DIR=$(python -c "import site; print(site.getsitepackages()[0])")
CAFFE_SO="$SP_DIR/caffe_ffi/_caffe_ffi.so"
TVM_SO="$SP_DIR/caffe_ffi/libtvm_ffi.so"

echo "=== Manual dlopen test ==="
echo "Caffe SO: $CAFFE_SO"
echo "TVM SO: $TVM_SO"
echo ""

echo "Test 1: Load tvm_ffi first (as pip package does), then load _caffe_ffi.so"
python -c "
import ctypes
import os
sp_dir = '$SP_DIR'
tvmmm_ffi_so = os.path.join(sp_dir, 'caffe_ffi', 'libtvm_ffi.so')
caffe_so = os.path.join(sp_dir, 'caffe_ffi', '_caffe_ffi.so')
print('Loading libtvm_ffi.so first...')
libtvm = ctypes.CDLL(tvm_ffi_so, mode=ctypes.RTLD_GLOBAL)
print('  libtvm_ffi loaded:', libtvm)
print('Loading _caffe_ffi.so with RTLD_GLOBAL...')
try:
    libcaffe = ctypes.CDLL(caffe_so, mode=ctypes.RTLD_GLOBAL)
    print('  _caffe_ffi loaded successfully:', libcaffe)
except OSError as e:
    print('  FAILED:', e)
" 2>&1
echo ""

echo "Test 2: Check if tvm_ffi Python package loads its own lib first"
python -c "
import tvm_ffi
import os
print('tvm_ffi file:', tvm_ffi.__file__)
tvm_base = os.path.dirname(tvm_ffi.__file__)
print('tvm_ffi base dir:', tvm_base)
for root, dirs, files in os.walk(tvm_base):
    for f in files:
        if 'libtvm_ffi' in f:
            print('  Found tvm_ffi lib:', os.path.join(root, f))
" 2>&1
echo ""

echo "Test 3: Import tvm_ffi first, then try ctypes load of _caffe_ffi.so"
python -c "
import ctypes, tvm_ffi, os
sp_dir = '$SP_DIR'
caffe_so = os.path.join(sp_dir, 'caffe_ffi', '_caffe_ffi.so')
print('After importing tvm_ffi, loading _caffe_ffi.so...')
try:
    libcaffe = ctypes.CDLL(caffe_so, mode=ctypes.RTLD_GLOBAL)
    print('  SUCCESS:', libcaffe)
except OSError as e:
    print('  FAILED:', e)
" 2>&1
echo ""

echo "Test 4: Check LD_LIBRARY_PATH"
echo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH:-}(empty)"
echo ""

echo "Test 5: RPATH of _caffe_ffi.so"
patchelf --print-rpath "$CAFFE_SO" 2>/dev/null
echo ""

echo "Test 6: Try loading without importing tvm_ffi Python package first"
python -c "
import ctypes, os
sp_dir = '$SP_DIR'
# Set RPATH-like behavior by adding lib dir to LD_LIBRARY_PATH_PATH
caffe_dir = os.path.join(sp_dir, 'caffe_ffi')
os.environ['LD_LIBRARY_PATH'] = caffe_dir + ':' + os.environ.get('LD_LIBRARY_PATH', '')
caffe_so = os.path.join(caffe_dir, '_caffe_ffi.so')
print('Loading _caffe_ffi.so directly (no tvm_ffi import)...')
try:
    libcaffe = ctypes.CDLL(caffe_so)
    print('  SUCCESS:', libcaffe)
except OSError as e:
    print('  FAILED:', e)
" 2>&1
