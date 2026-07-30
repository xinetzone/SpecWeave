#!/bin/bash
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export PATH="$CONDA_PREFIX/bin:/opt/conda/bin:$PATH"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
pass() { echo -e "${GREEN}  PASS${NC} $*"; }
fail() { echo -e "${RED}  FAIL${NC} $*"; exit 1; }
info() { echo -e "${CYAN}==>${NC} $*"; }

echo "============================================================"
echo " caffe-ffi Conda Build Verification"
echo "============================================================"
echo "  Python: $(python --version 2>&1)"
echo "  conda:  $(conda --version 2>&1)"
echo ""

SRC_ROOT=/SpecWeave
CAFFE_FFI_DIR="$SRC_ROOT/projects/xuanspace/libs/caffe-ffi"
RECIPE_DIR="$CAFFE_FFI_DIR/conda.recipe"
CONDA_BLD_DIR="$CONDA_PREFIX/conda-bld"
BUILD_LOG="$CONDA_BLD_DIR/build.log"

mkdir -p "$CONDA_BLD_DIR"

info "Fixing conda config to official sources..."
cat > /opt/conda/.condarc << 'EOF'
channels:
  - conda-forge
  - defaults
channel_priority: strict
auto_activate_base: false
EOF

info "Ensuring conda-build is available..."
if ! command -v conda-build >/dev/null 2>&1; then
    conda install -y -c conda-forge "conda-build>=3.28" 2>&1 | tail -5
fi
pass "conda-build: $(conda-build --version 2>&1 | head -1)"
echo ""

info "Fixing CRLF line endings..."
find "$CAFFE_FFI_DIR" -type f \
    \( -name '*.sh' -o -name '*.cmake' -o -name 'CMakeLists.txt' -o -name '*.py' \
    -o -name '*.cc' -o -name '*.cpp' -o -name '*.hpp' -o -name '*.h' \
    -o -name 'meta.yaml' -o -name 'build.sh' \) \
    -not -path '*/build/*' -not -path '*/.git/*' \
    -exec sed -i 's/\r$//' {} \; 2>/dev/null || true
pass "CRLF fix done"
echo ""

info "Validating recipe..."
conda-build --no-anaconda-upload --check "$RECIPE_DIR" 2>&1 | tail -10 || true
echo ""

info "Running conda build (this may take several minutes)..."
cd "$SRC_ROOT"
conda-build \
    --no-anaconda-upload \
    --prefix-length 80 \
    --no-test \
    -c conda-forge \
    "$RECIPE_DIR" 2>&1 | tee "$BUILD_LOG"
BUILD_STATUS=${PIPESTATUS[0]}

if [ $BUILD_STATUS -ne 0 ]; then
    echo ""
    echo "  === Last 100 lines of build output ==="
    tail -100 "$BUILD_LOG"
    fail "conda build failed (exit code $BUILD_STATUS)"
fi
pass "conda build succeeded"
echo ""

info "Locating built package..."
_PKG_PATH=""
for ext in ".conda" ".tar.bz2"; do
    _FOUND=$(find "$CONDA_BLD_DIR" -name "caffe-ffi-*${ext}" -type f 2>/dev/null | sort -V | tail -1)
    if [ -n "$_FOUND" ] && [ -f "$_FOUND" ]; then
        _PKG_PATH="$_FOUND"
        break
    fi
done

if [ -n "$_PKG_PATH" ] && [ -f "$_PKG_PATH" ]; then
    _PKG_SIZE=$(du -h "$_PKG_PATH" 2>/dev/null | cut -f1)
    pass "Built package: $_PKG_PATH ($_PKG_SIZE)"
else
    _PKG_PATH=$(conda-build --output "$RECIPE_DIR" 2>/dev/null | tail -1)
    if [ -n "$_PKG_PATH" ] && [ -f "$_PKG_PATH" ]; then
        _PKG_SIZE=$(du -h "$_PKG_PATH" 2>/dev/null | cut -f1)
        pass "Built package: $_PKG_PATH ($_PKG_SIZE)"
    else
        fail "Could not locate built package"
    fi
fi
echo ""

info "Installing built package for verification..."
pip uninstall -y caffe-ffi 2>/dev/null || true
conda install -y --offline --use-local "$_PKG_PATH" 2>&1 | tail -10 || \
    pip install "$_PKG_PATH" 2>&1 | tail -10 || \
    fail "Failed to install built package"
pass "Package installed successfully"
echo ""

if ! python -c "import tvm_ffi" 2>/dev/null; then
    info "Installing apache-tvm-ffi Python package..."
    pip install --no-deps apache-tvm-ffi 2>&1 | tail -5 || pip install apache-tvm-ffi 2>&1 | tail -5 || true
fi
echo ""

info "=== Verifying installation ==="
echo ""

info "Test 1: Import caffe_ffi..."
python -c "
import caffe_ffi
print('    Version:', caffe_ffi.__version__)
print('    Native available:', caffe_ffi._ffi_api.is_available())
" && pass "Import test passed" || fail "Import test failed"
echo ""

info "Test 2: Shared library dependencies (ldd + RPATH)..."
_CAFFE_SO=$(python -c "
import caffe_ffi, os, glob
sos = glob.glob(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi*.so'))
print(sos[0] if sos else '')
" 2>/dev/null)

echo "    Library: $_CAFFE_SO"
if [ -n "$_CAFFE_SO" ] && [ -f "$_CAFFE_SO" ]; then
    echo "    === RPATH ==="
    patchelf --print-rpath "$_CAFFE_SO" 2>/dev/null | sed 's/^/      /' || echo "      N/A"
    echo ""
    echo "    === ldd output ==="
    ldd "$_CAFFE_SO" 2>/dev/null | sed 's/^/      /'
    echo "    === end ldd ==="
    echo ""

    if ldd "$_CAFFE_SO" 2>/dev/null | grep -q 'not found'; then
        echo ""
        fail "Some shared library dependencies are NOT FOUND:"
        ldd "$_CAFFE_SO" | grep 'not found'
    else
        pass "All shared library dependencies resolved"
    fi

    echo ""
    info "Checking for libtvm_ffi.so linkage..."
    if ldd "$_CAFFE_SO" 2>/dev/null | grep -qi 'libtvm_ffi'; then
        _TVM_FFI_LINK=$(ldd "$_CAFFE_SO" 2>/dev/null | grep -i 'libtvm_ffi' | head -1)
        pass "libtvm_ffi.so correctly linked: $_TVM_FFI_LINK"
    else
        fail "libtvm_ffi.so NOT found in shared library dependencies!"
    fi

    echo ""
    info "Checking for libtvm_ffi.so file directly..."
    _TVM_FFI_SO=$(python -c "
import tvm_ffi, os, glob
sos = glob.glob(os.path.join(os.path.dirname(tvm_ffi.__file__), '_tvm_ffi*.so'))
print(sos[0] if sos else '')
" 2>/dev/null)
    if [ -n "$_TVM_FFI_SO" ] && [ -f "$_TVM_FFI_SO" ]; then
        echo "    libtvm_ffi.so location: $_TVM_FFI_SO"
        echo "    === libtvm_ffi.so RPATH ==="
        patchelf --print-rpath "$_TVM_FFI_SO" 2>/dev/null | sed 's/^/      /' || echo "      N/A"
        echo ""
        echo "    === libtvm_ffi.so ldd ==="
        ldd "$_TVM_FFI_SO" 2>/dev/null | sed 's/^/      /'
        echo ""
        if ldd "$_TVM_FFI_SO" 2>/dev/null | grep -q 'not found'; then
            fail "libtvm_ffi.so has unresolved dependencies!"
        else
            pass "libtvm_ffi.so all dependencies resolved"
        fi
    else
        echo "    Note: tvm_ffi is pure Python or native .so not found (PyPI wheel may be pure Python stub)"
    fi
else
    fail "Could not locate _caffe_ffi.so"
fi
echo ""

info "Test 3: Basic Blob functionality..."
python -c "
import numpy as np
from caffe_ffi import Blob
b = Blob([2, 3, 4, 5])
assert b.count() == 2*3*4*5, 'count mismatch'
b.fill(3.14)
data = b.data_tensor
assert abs(data[0] - 3.14) < 1e-6, 'fill failed'
b2 = Blob([100])
b2.from_numpy(np.arange(100, dtype=np.float32))
assert abs(b2.data_tensor[50] - 50.0) < 1e-6, 'from_numpy failed'
print('    All basic Blob tests passed!')
" && pass "Blob functionality test passed" || fail "Blob functionality test failed"
echo ""

echo "============================================================"
echo -e " ${GREEN}CONDA BUILD VERIFICATION COMPLETED${NC}"
echo "============================================================"
echo ""
echo "Build artifacts:"
echo "  Package:  $_PKG_PATH"
echo "  Build log: $BUILD_LOG"
echo ""
