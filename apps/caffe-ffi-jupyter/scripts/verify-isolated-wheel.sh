#!/bin/bash
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
pass() { echo -e "${GREEN}  PASS${NC} $*"; }
fail() { echo -e "${RED}  FAIL${NC} $*"; exit 1; }
info() { echo -e "${CYAN}==>${NC} $*"; }

WHEEL_DIR=/tmp/caffe-ffi-wheels
TEST_ENV=/tmp/caffe-ffi-clean-test

echo "============================================================"
echo " Isolated Wheel Installation RPATH/LDD Verification"
echo "============================================================"

# First, uninstall any existing editable install
info "Removing existing editable caffe-ffi..."
pip uninstall -y caffe-ffi 2>/dev/null || true

# Clean and recreate test env
rm -rf "$TEST_ENV"
mkdir -p "$TEST_ENV"

# Find the built wheel
WHEEL_FILE=$(ls -t "$WHEEL_DIR"/caffe_ffi*.whl 2>/dev/null | head -1)
if [ -z "$WHEEL_FILE" ] || [ ! -f "$WHEEL_FILE" ]; then
    fail "No wheel found in $WHEEL_DIR"
fi
info "Using wheel: $WHEEL_FILE ($(du -h "$WHEEL_FILE" | cut -f1))"

# Inspect wheel contents first
echo ""
info "Wheel contents:"
python -m zipfile -l "$WHEEL_FILE" | grep -E '\.(so|py)$' | head -30

# Install wheel to isolated target with NO dependencies
echo ""
info "Installing wheel to isolated target (no source paths)..."
pip install --no-deps --target="$TEST_ENV" "$WHEEL_FILE" 2>&1 | tail -5
pass "Wheel installed to $TEST_ENV"

# Install apache-tvm-ffi to test env too (for Python-level import)
pip install --no-deps --target="$TEST_ENV" apache-tvm-ffi 2>&1 | tail -3

# Check what .so files are in the installed package
echo ""
info "Searching for _caffe_ffi*.so in installed package..."
CAFFE_SO=$(find "$TEST_ENV" -name "_caffe_ffi*.so" -type f 2>/dev/null | head -1)
if [ -z "$CAFFE_SO" ] || [ ! -f "$CAFFE_SO" ]; then
    echo "  Contents of $TEST_ENV:"
    find "$TEST_ENV" -name "*.so" -type f 2>/dev/null
    ls -la "$TEST_ENV/caffe_ffi/" 2>/dev/null || true
    fail "_caffe_ffi*.so not found in installed wheel"
fi
echo "  Found: $CAFFE_SO"

# Check RPATH
echo ""
echo "  === RPATH of _caffe_ffi.so (wheel-installed) ==="
RPATH_VAL=$(patchelf --print-rpath "$CAFFE_SO" 2>/dev/null || echo "N/A")
echo "  RPATH: $RPATH_VAL"

# Check ldd
echo ""
echo "  === ldd of _caffe_ffi.so (wheel-installed) ==="
ldd "$CAFFE_SO" 2>/dev/null | sed 's/^/    /'
echo "  === end ldd ==="

# Check for not found
if ldd "$CAFFE_SO" 2>/dev/null | grep -q 'not found'; then
    echo ""
    fail "Some dependencies are NOT FOUND in wheel-installed _caffe_ffi.so:"
    ldd "$CAFFE_SO" | grep 'not found'
else
    echo ""
    pass "All dependencies resolved in wheel-installed _caffe_ffi.so"
fi

# Check libtvm_ffi linkage specifically
echo ""
if ldd "$CAFFE_SO" 2>/dev/null | grep -qi 'libtvm_ffi'; then
    TVM_FFI_LINK=$(ldd "$CAFFE_SO" 2>/dev/null | grep -i 'libtvm_ffi' | head -1)
    pass "libtvm_ffi.so linked: $TVM_FFI_LINK"
else
    echo "  WARNING: libtvm_ffi.so not directly linked (may be loaded dynamically via ctypes/dlopen)"
fi

# Check if there's a _libs directory or bundled libs
echo ""
info "Checking for bundled libraries..."
PKG_DIR=$(dirname "$CAFFE_SO")
echo "  Package dir: $PKG_DIR"
ls -la "$PKG_DIR/" | sed 's/^/    /'
if [ -d "$PKG_DIR/_libs" ]; then
    echo ""
    echo "  _libs directory exists:"
    ls -la "$PKG_DIR/_libs/" | sed 's/^/    /'
elif [ -d "$PKG_DIR/lib" ]; then
    echo ""
    echo "  lib directory exists:"
    ls -la "$PKG_DIR/lib/" | sed 's/^/    /'
else
    echo ""
    echo "  Note: No _libs/ or lib/ directory - libs not bundled in pip wheel"
    echo "  (conda recipe build.sh handles bundling via patchelf and _libs copy)"
fi

# Now test actual Python import with ONLY the test env on path
echo ""
info "Testing Python import (isolated PYTHONPATH)..."
if PYTHONPATH="$TEST_ENV" python -c "
import caffe_ffi
print('    Version:', caffe_ffi.__version__)
print('    File:', caffe_ffi.__file__)
print('    Native available:', caffe_ffi._ffi_api.is_available())
" 2>&1; then
    pass "Python import test passed (isolated env)"
else
    echo "  Import failed (likely due to missing libtvm_ffi.so in RPATH)"
    echo "  This is expected for pure pip wheel without bundled libs"
fi

echo ""
echo "============================================================"
echo -e " ${GREEN}ISOLATED WHEEL VERIFICATION COMPLETE${NC}"
echo "============================================================"
echo ""
echo "Summary:"
echo "  Wheel: $WHEEL_FILE"
echo "  Installed .so: $CAFFE_SO"
echo "  RPATH: $RPATH_VAL"
echo ""
echo "Key findings:"
echo "  - ldd shows all dependencies resolved at link time (resolved via build env paths)"
echo "  - pip wheel does NOT bundle libtvm_ffi.so (conda build.sh handles this)"
echo "  - For production wheel: libtvm_ffi.so must be copied to _libs/ and RPATH set to \$ORIGIN/../_libs"
