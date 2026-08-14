#!/bin/bash
# Quick verification: clean editable residuals, reinstall conda package, verify
set -eux -o pipefail

source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export PATH="$CONDA_PREFIX/bin:/opt/conda/bin:$PATH"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'
pass() { echo -e "${GREEN}  PASS${NC} $*"; }
fail() { echo -e "${RED}  FAIL${NC} $*"; exit 1; }
info() { echo -e "${CYAN}==>${NC} $*"; }

CONDA_BLD_DIR="$CONDA_PREFIX/conda-bld"
SP_DIR=$(python -c "import site; print(site.getsitepackages()[0])")

info "Pre-clean: Checking for editable residuals..."
_cleaned=0
for _pth in "$SP_DIR"/_editable_skbc_*.pth "$SP_DIR"/__editable__.*.pth; do
    if [ -f "$_pth" ]; then
        _pth_base=$(basename "$_pth" .pth)
        rm -f "$SP_DIR/${_pth_base}.py" 2>/dev/null
        rm -f "$_pth" 2>/dev/null
        _cleaned=$((_cleaned + 1))
        echo "  Removed: $(basename "$_pth")"
    fi
done
echo "  Cleaned $_cleaned editable files"

# Remove stale caffe_ffi directory
if [ -d "$SP_DIR/caffe_ffi" ]; then
    echo "  Removing stale caffe_ffi directory..."
    rm -rf "$SP_DIR/caffe_ffi" "$SP_DIR"/caffe_ffi-*.dist-info
fi

# Uninstall pip version of caffe-ffi only if installed via pip
pip uninstall -y caffe-ffi 2>/dev/null || true
pip uninstall -y apache-tvm-ffi 2>/dev/null || true

# Find the built package
_PKG_PATH=$(ls -t "$CONDA_BLD_DIR"/linux-64/caffe-ffi-*.conda 2>/dev/null | head -1)
if [ -z "$_PKG_PATH" ]; then
    fail "No built package found"
fi
info "Installing package: $_PKG_PATH"
conda install -y --offline --use-local --force-reinstall "$_PKG_PATH"

# Install apache-tvm-ffi for Python layer
info "Installing apache-tvm-ffi..."
pip install --no-deps apache-tvm-ffi 2>&1 || pip install apache-tvm-ffi 2>&1

info "=== Verification ==="
echo ""

# Test 8a0: Load path verification
echo "Test 8a0: Verifying package load path..."
_CAFFE_FILE=$(python -c "import caffe_ffi; print(caffe_ffi.__file__)" 2>&1)
echo "  Loading from: $_CAFFE_FILE"
if echo "$_CAFFE_FILE" | grep -q "site-packages/caffe_ffi"; then
    pass "Loading from conda site-packages (correct)"
else
    fail "Loading from wrong location: $_CAFFE_FILE"
fi
echo ""

# Test 8a: Import test
echo "Test 8a: Import caffe_ffi..."
python -c "
import caffe_ffi
print('  Version:', caffe_ffi.__version__)
print('  Native available:', caffe_ffi._ffi_api.is_available())
" && pass "Import test passed" || fail "Import test failed"
echo ""

# Test 8b: Blob functionality
echo "Test 8b: Blob operations..."
python -c "
import numpy as np
from caffe_ffi import Blob
b = Blob([2, 3, 4, 5])
assert b.count() == 2*3*4*5
b.fill(3.14)
assert abs(b.data_tensor[0] - 3.14) < 1e-6
print('  Blob tests passed!')
" && pass "Blob test passed" || fail "Blob test failed"
echo ""

# Test 8c: ldd check
echo "Test 8c: Shared library dependencies..."
_CAFFE_SO=$(python -c "
import caffe_ffi, os, glob
sos = glob.glob(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi*.so'))
print(sos[0] if sos else '')
")
if [ -n "$_CAFFE_SO" ] && [ -f "$_CAFFE_SO" ]; then
    echo "  Library: $_CAFFE_SO"
    echo "  RPATH: $(patchelf --print-rpath "$_CAFFE_SO" 2>/dev/null || echo 'N/A')"
    if ldd "$_CAFFE_SO" 2>/dev/null | grep -q 'not found'; then
        fail "Unresolved dependencies found:"
        ldd "$_CAFFE_SO" | grep 'not found'
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

# Final check: no editable .pth files
echo "Final check: editable residuals..."
if ls "$SP_DIR"/_editable_*.pth "$SP_DIR"/__editable__*.pth 2>/dev/null; then
    fail "Editable .pth files still present!"
else
    pass "No editable residuals - clean environment"
fi

echo ""
info "All verification tests passed!"
