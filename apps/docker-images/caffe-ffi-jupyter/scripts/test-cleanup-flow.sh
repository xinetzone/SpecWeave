#!/bin/bash
# Test the cleanup + install + verification flow (Steps 7-8 only, using existing package)
set -eux -o pipefail

source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export PATH="$CONDA_PREFIX/bin:/opt/conda/bin:$PATH"

SRC_ROOT="/SpecWeave"
CAFFE_FFI_DIR="$SRC_ROOT/projects/xuanspace/libs/caffe-ffi"
CONDA_BLD_DIR="$CONDA_PREFIX/conda-bld"

# First, simulate editable residuals (same as before)
echo "============================================================"
echo " Step 0: Simulate editable install residuals"
echo "============================================================"
pip install --no-deps -e "$CAFFE_FFI_DIR" 2>&1 | tail -3 || true
SP_DIR=$(python -c "import site; print(site.getsitepackages()[0])")
echo "Editable residuals created:"
ls -la "$SP_DIR"/_editable_skbc_caffe_ffi* 2>&1
echo ""

# Verify loading from source before cleanup
echo "Before cleanup - loading from:"
python -c "import caffe_ffi; print(' ', caffe_ffi.__file__)"
echo ""

# Now source the cleanup function from our script and run Step 7a+7b+8
echo "============================================================"
echo " Running Steps 7-8 from test-conda-build.sh"
echo "============================================================"

# Source the script's helper functions and variables
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
pass() { echo -e "${GREEN}  PASS${NC} $*"; }
fail() { echo -e "${RED}  FAIL${NC} $*"; exit 1; }
info() { echo -e "${CYAN}==>${NC} $*"; }
warn() { echo -e "${YELLOW} WARN${NC} $*"; }

# Source the clean_editable_residuals function
source <(sed -n '/^# ── Helper: thoroughly clean/,/^SRC_ROOT=/p' /SpecWeave/apps/docker-images/caffe-ffi-jupyter/scripts/test-conda-build.sh | head -n -1)

echo ""
info "Step 7a: Cleaning editable install residuals..."
_EDITABLE_CLEANED_COUNT=0
clean_editable_residuals "caffe_ffi"
echo "  Cleaned $_EDITABLE_CLEANED_COUNT editable residual file(s)"
echo ""

# Verify residuals are gone
echo "Checking for remaining residuals..."
_REMAINING=$(find "$SP_DIR" -maxdepth 1 -name '_editable_skbc_caffe_ffi*' -o -name '__editable__*caffe*' 2>/dev/null | grep -v scikit_build_core || true)
if [ -n "$_REMAINING" ]; then
    fail "Residuals still present: $_REMAINING"
else
    pass "No editable residuals remain"
fi
echo ""

# Uninstall apache-tvm-ffi pip (as Step 7a does)
pip uninstall -y apache-tvm-ffi 2>/dev/null || true

# Remove stale caffe_ffi from ALL site-packages
for _sp in $(python -c "import site; print(' '.join(site.getsitepackages()))" 2>/dev/null); do
    if [ -d "$_sp/caffe_ffi" ]; then
        echo "  Removing stale caffe_ffi from $_sp..."
        rm -rf "$_sp/caffe_ffi" 2>/dev/null
        rm -rf "$_sp"/caffe_ffi-*.dist-info 2>/dev/null
    fi
done

# Find existing package
_PKG_PATH=$(find "$CONDA_BLD_DIR" -name "caffe-ffi-*.conda" -type f 2>/dev/null | sort -V | tail -1)
echo "  Using existing package: $_PKG_PATH"

# Install with force-reinstall
info "Step 7b: Installing with --force-reinstall..."
conda install -y -n caffe-ffi --use-local --force-reinstall "$_PKG_PATH" 2>&1 | tail -5
pass "Package installed successfully"

# Install tvm-ffi pip package
pip install --no-deps apache-tvm-ffi 2>&1 | tail -2
echo ""

# === Step 8: Verify ===
info "Step 8: Verifying..."
echo ""

# Test 8a0: Load path
echo "  Test 8a0: Verifying package load path..."
_CAFFE_FILE=$(python -c "import caffe_ffi; print(caffe_ffi.__file__)" 2>/dev/null)
echo "    Loading from: $_CAFFE_FILE"
if echo "$_CAFFE_FILE" | grep -q "site-packages/caffe_ffi"; then
    pass "Loading from conda site-packages (correct!)"
else
    fail "Loading from wrong location: $_CAFFE_FILE"
fi
echo ""

# Test 8a: Import
echo "  Test 8a: Import caffe_ffi..."
python -c "
import caffe_ffi
print('    Version:', caffe_ffi.__version__)
print('    Native available:', caffe_ffi._ffi_api.is_available())
"
pass "Import test passed"
echo ""

# Test 8b: Blob
echo "  Test 8b: Basic Blob operations..."
python -c "
import numpy as np
from caffe_ffi import Blob
b = Blob([2, 3, 4, 5])
assert b.count() == 2*3*4*5
b.fill(3.14)
import numpy as np
val = float(np.asarray(b.data_tensor).flat[0])
assert abs(val - 3.14) < 1e-6, f'Blob value wrong: {val}'
print('    All Blob tests passed!')
"
pass "Blob functionality test passed"
echo ""

# Test 8c: ldd
echo "  Test 8c: Shared library dependencies..."
_CAFFE_SO=$(python -c "
import caffe_ffi, os, glob
sos = glob.glob(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi*.so'))
print(sos[0] if sos else '')
" 2>/dev/null)
echo "    Library: $_CAFFE_SO"
echo "    RPATH: $(patchelf --print-rpath "$_CAFFE_SO" 2>/dev/null)"
if ldd "$_CAFFE_SO" 2>/dev/null | grep -q 'not found'; then
    fail "Some dependencies NOT FOUND"
else
    pass "All shared library dependencies resolved"
fi
echo ""

echo "============================================================"
echo -e " ${GREEN}ALL TESTS PASSED - Cleanup logic works correctly!${NC}"
echo "============================================================"
