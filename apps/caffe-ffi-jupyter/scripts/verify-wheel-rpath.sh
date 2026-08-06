#!/bin/bash
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
pass() { echo -e "${GREEN}  PASS${NC} $*"; }
fail() { echo -e "${RED}  FAIL${NC} $*"; exit 1; }
info() { echo -e "${CYAN}==>${NC} $*"; }

SRC_ROOT=/SpecWeave
CAFFE_FFI_DIR="$SRC_ROOT/projects/xuanspace/libs/caffe-ffi"
WHEEL_DIR=/tmp/caffe-ffi-wheels
TEST_ENV=/tmp/caffe-ffi-test-install

echo "============================================================"
echo " caffe-ffi Wheel Build & RPATH/LDD Verification"
echo "============================================================"
echo "  Python: $(python --version 2>&1)"
echo "  Source: $CAFFE_FFI_DIR"
echo ""

# Fix CRLF
info "Fixing CRLF line endings..."
find "$CAFFE_FFI_DIR" -type f \
    \( -name '*.sh' -o -name '*.cmake' -o -name 'CMakeLists.txt' -o -name '*.py' \
    -o -name '*.cc' -o -name '*.cpp' -o -name '*.hpp' -o -name '*.h' \) \
    -not -path '*/build/*' -not -path '*/.git/*' \
    -exec sed -i 's/\r$//' {} \; 2>/dev/null || true
pass "CRLF fix done"

# Ensure scikit-build-core and build deps are available
info "Ensuring build dependencies..."
pip install --no-deps scikit-build-core ninja cmake patchelf 2>/dev/null || \
    conda install -y -c conda-forge scikit-build-core ninja patchelf 2>/dev/null || true
pip install scikit-build-core ninja cmake patchelf 2>&1 | tail -3
pass "Build deps installed"

# Also ensure tvm-ffi is available for the build
info "Setting up tvm-ffi..."
export CAFFE_FFI_TVM_FFI_DIR="$SRC_ROOT/projects/xuanspace/vendor/tvm-ffi"
pip install --no-deps -e "$CAFFE_FFI_TVM_FFI_DIR" 2>&1 | tail -3
pass "tvm-ffi setup done"

# Build wheel
echo ""
info "Building wheel with pip wheel..."
mkdir -p "$WHEEL_DIR"
rm -rf "$CAFFE_FFI_DIR"/build
cd "$CAFFE_FFI_DIR"
CAFFE_FFI_TVM_FFI_DIR="$CAFFE_FFI_TVM_FFI_DIR" \
    pip wheel . --no-deps -w "$WHEEL_DIR" --no-build-isolation -v 2>&1 | tail -30
WHEEL_FILE=$(ls -t "$WHEEL_DIR"/caffe_ffi*.whl 2>/dev/null | head -1)
if [ -z "$WHEEL_FILE" ] || [ ! -f "$WHEEL_FILE" ]; then
    fail "Wheel build failed - no wheel produced"
fi
WHEEL_SIZE=$(du -h "$WHEEL_FILE" | cut -f1)
pass "Wheel built: $(basename "$WHEEL_FILE") ($WHEEL_SIZE)"

# Install wheel to test location
echo ""
info "Installing wheel to test location: $TEST_ENV"
rm -rf "$TEST_ENV"
mkdir -p "$TEST_ENV"
pip install --no-deps --target="$TEST_ENV" "$WHEEL_FILE" 2>&1 | tail -5
pass "Wheel installed to $TEST_ENV"

# Install tvm-ffi Python package to test env too
pip install --no-deps --target="$TEST_ENV" apache-tvm-ffi 2>&1 | tail -3 || true
# Also copy libtvm_ffi.so to simulate proper packaging
TVM_FFI_SO="$CAFFE_FFI_TVM_FFI_DIR/build/lib/libtvm_ffi.so"
if [ -f "$TVM_FFI_SO" ]; then
    cp -ad "$TVM_FFI_SO"* "$TEST_ENV/caffe_ffi/" 2>/dev/null || true
    echo "  Copied libtvm_ffi.so to package directory"
fi

# Now verify
echo ""
info "=== Verifying installed wheel ==="
echo ""

CAFFE_SO=$(PYTHONPATH="$TEST_ENV" python -c "
import caffe_ffi, os, glob
sos = glob.glob(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi*.so'))
print(sos[0] if sos else '')
" 2>/dev/null)

if [ -z "$CAFFE_SO" ] || [ ! -f "$CAFFE_SO" ]; then
    echo "ERROR: _caffe_ffi.so not found in installed wheel"
    echo "Contents of $TEST_ENV/caffe_ffi/:"
    ls -la "$TEST_ENV/caffe_ffi/" || true
    exit 1
fi

echo "  Library: $CAFFE_SO"
echo ""
echo "  === RPATH ==="
patchelf --print-rpath "$CAFFE_SO" 2>/dev/null | sed 's/^/    /' || echo "    N/A"
echo ""
echo "  === ldd output ==="
ldd "$CAFFE_SO" 2>/dev/null | sed 's/^/    /'
echo "  === end ldd ==="
echo ""

if ldd "$CAFFE_SO" 2>/dev/null | grep -q 'not found'; then
    fail "Some shared library dependencies are NOT FOUND:"
    ldd "$CAFFE_SO" | grep 'not found'
else
    pass "All shared library dependencies resolved"
fi

echo ""
info "Checking libtvm_ffi.so linkage..."
if ldd "$CAFFE_SO" 2>/dev/null | grep -qi 'libtvm_ffi'; then
    _TVM_FFI_LINK=$(ldd "$CAFFE_SO" 2>/dev/null | grep -i 'libtvm_ffi' | head -1)
    pass "libtvm_ffi.so correctly linked: $_TVM_FFI_LINK"
else
    fail "libtvm_ffi.so NOT found in shared library dependencies!"
fi

# Check libtvm_ffi.so own deps
echo ""
TVM_FFI_IN_PKG=$(ls "$TEST_ENV/caffe_ffi"/libtvm_ffi*.so 2>/dev/null | head -1)
if [ -n "$TVM_FFI_IN_PKG" ] && [ -f "$TVM_FFI_IN_PKG" ]; then
    info "Checking libtvm_ffi.so in package..."
    echo "    File: $TVM_FFI_IN_PKG"
    echo "    RPATH: $(patchelf --print-rpath "$TVM_FFI_IN_PKG" 2>/dev/null || echo 'N/A')"
    echo "    --- ldd ---"
    ldd "$TVM_FFI_IN_PKG" 2>/dev/null | sed 's/^/      /'
    if ldd "$TVM_FFI_IN_PKG" 2>/dev/null | grep -q 'not found'; then
        fail "libtvm_ffi.so has unresolved dependencies!"
    else
        pass "libtvm_ffi.so all dependencies resolved"
    fi
else
    echo "    Note: libtvm_ffi.so not in package (expected for editable/dev builds)"
fi

# Check _libs directory
echo ""
info "Checking package structure..."
echo "  Package contents:"
ls -la "$TEST_ENV/caffe_ffi/" | sed 's/^/    /'
if [ -d "$TEST_ENV/caffe_ffi/_libs" ]; then
    echo ""
    echo "  _libs directory:"
    ls -la "$TEST_ENV/caffe_ffi/_libs/" | sed 's/^/    /'
else
    echo ""
    echo "  Note: _libs directory not present in pip wheel (conda recipe handles this)"
fi

echo ""
echo "============================================================"
echo -e " ${GREEN}WHEEL BUILD VERIFICATION COMPLETED${NC}"
echo "============================================================"
