#!/bin/bash
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export PATH="$CONDA_PREFIX/bin:/opt/conda/bin:$PATH"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'
pass() { echo -e "${GREEN}  PASS${NC} $*"; }
fail() { echo -e "${RED}  FAIL${NC} $*"; exit 1; }
info() { echo -e "${CYAN}==>${NC} $*"; }
warn() { echo -e "${YELLOW} WARN${NC} $*"; }

SP_DIR=$(python -c "import site; print(site.getsitepackages()[0])")

info "=== Final Verification ==="
echo ""

# Install tvm-ffi if not available
if ! python -c "import tvm_ffi" 2>/dev/null; then
    info "Installing apache-tvm-ffi..."
    pip install --no-deps apache-tvm-ffi 2>&1 | tail -3
fi
echo ""

# Test 8a0: Load path
echo "Test 8a0: Verifying package load path..."
_CAFFE_FILE=$(python -c "import caffe_ffi; print(caffe_ffi.__file__)" 2>&1)
echo "  Loading from: $_CAFFE_FILE"
echo "$_CAFFE_FILE" | grep -q "site-packages/caffe_ffi" && \
    pass "Loading from conda site-packages (correct)" || \
    fail "Loading from wrong location: $_CAFFE_FILE"
echo ""

# Test 8a: Import
echo "Test 8a: Import caffe_ffi..."
python -c "
import caffe_ffi
print('  Version:', caffe_ffi.__version__)
print('  Native available:', caffe_ffi._ffi_api.is_available())
assert caffe_ffi._ffi_api.is_available(), 'Native FFI not available!'
print('  caffe_pb2 available:', hasattr(caffe_ffi, 'caffe_pb2'))
" && pass "Import test passed" || fail "Import test failed"
echo ""

# Test 8b: Blob
echo "Test 8b: Blob operations..."
python -c "
import numpy as np
from caffe_ffi import Blob
b = Blob([2, 3, 4, 5])
assert b.count() == 2*3*4*5, 'count mismatch'
b.fill(3.14)
assert abs(b.data_tensor[0] - 3.14) < 1e-6, 'fill failed'
b2 = Blob([100])
b2.from_numpy(np.arange(100, dtype=np.float32))
assert abs(b2.data_tensor[50] - 50.0) < 1e-6, 'from_numpy failed'
print('  All Blob tests passed!')
" && pass "Blob test passed" || fail "Blob test failed"
echo ""

# Test 8c: ldd
echo "Test 8c: Shared library dependencies..."
_CAFFE_SO=$(python -c "
import caffe_ffi, os, glob
sos = glob.glob(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi*.so'))
print(sos[0] if sos else '')
")
if [ -n "$_CAFFE_SO" ] && [ -f "$_CAFFE_SO" ]; then
    echo "  Library: $_CAFFE_SO"
    echo "  RPATH: $(patchelf --print-rpath "$_CAFFE_SO" 2>/dev/null || echo 'N/A')"
    echo "  --- ldd (key deps) ---"
    ldd "$_CAFFE_SO" 2>/dev/null | grep -E 'libtvm_ffi|libopenblas|libprotobuf|not found' | sed 's/^/    /'
    echo "  --- end ---"
    if ldd "$_CAFFE_SO" 2>/dev/null | grep -q 'not found'; then
        fail "Unresolved dependencies found!"
    else
        pass "All dependencies resolved"
    fi
    if ldd "$_CAFFE_SO" 2>/dev/null | grep -qi 'libtvm_ffi'; then
        pass "libtvm_ffi.so correctly linked"
    else
        fail "libtvm_ffi.so NOT linked!"
    fi
else
    fail "Could not find _caffe_ffi.so"
fi
echo ""

# Check no editable residuals
echo "Final check: No editable residuals..."
if ls "$SP_DIR"/_editable_*.pth "$SP_DIR"/__editable__*.pth 2>/dev/null; then
    fail "Editable .pth files still present!"
else
    pass "Environment is clean - no editable residuals"
fi

echo ""
echo "============================================================"
echo -e " ${GREEN}ALL VERIFICATION TESTS PASSED${NC}"
echo "============================================================"
echo ""
echo "Package contents:"
ls -la "$SP_DIR/caffe_ffi/" | grep -v __pycache__ | grep -v '\.modified$'
echo ""
echo "Subdirectories:"
find "$SP_DIR/caffe_ffi" -mindepth 1 -type d | sort
