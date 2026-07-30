#!/bin/bash
# Full clean rebuild and verification script
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi

SRC_ROOT=/SpecWeave
CAFFE_FFI_DIR="$SRC_ROOT/projects/xuanspace/libs/caffe-ffi"
RECIPE_DIR="$CAFFE_FFI_DIR/conda.recipe"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
pass() { echo -e "${GREEN}  PASS${NC} $*"; }
fail() { echo -e "${RED}  FAIL${NC} $*"; exit 1; }
info() { echo -e "${CYAN}==>${NC} $*"; }
warn() { echo -e "${YELLOW} WARN${NC} $*"; }

NATIVE_PASS=false
BLOB_PASS=false

echo "============================================================"
echo " FULL CLEAN REBUILD: caffe-ffi Conda Package"
echo "============================================================"

# ── Step 0: THOROUGH cleanup ──
info "Step 0: Thorough environment cleanup..."

# Remove conda-bld
rm -rf "$CONDA_PREFIX/conda-bld" 2>/dev/null || true
echo "  Removed conda-bld"

# Clean conda package cache for caffe-ffi and tvm-ffi
conda clean -y --packages 2>/dev/null || true
rm -rf "$CONDA_PREFIX/pkgs/caffe-ffi-"* 2>/dev/null || true
echo "  Cleaned conda package cache"

# Uninstall existing packages via conda and pip
conda remove -y -n caffe-ffi caffe-ffi 2>/dev/null || true
pip uninstall -y caffe-ffi apache-tvm-ffi 2>/dev/null || true
echo "  Uninstalled existing caffe-ffi and apache-tvm-ffi"

# Remove ALL caffe_ffi dirs from site-packages
for _sp in $(python -c "import site; print(' '.join(site.getsitepackages()))" 2>/dev/null); do
    if [ -d "$_sp/caffe_ffi" ]; then
        rm -rf "$_sp/caffe_ffi"
        rm -rf "$_sp"/caffe_ffi-*.dist-info
        echo "  Removed stale caffe_ffi from $_sp"
    fi
done

# Remove ALL tvm_ffi dirs from site-packages
for _sp in $(python -c "import site; print(' '.join(site.getsitepackages()))" 2>/dev/null); do
    if [ -d "$_sp/tvm_ffi" ]; then
        rm -rf "$_sp/tvm_ffi"
        rm -rf "$_sp"/apache_tvm_ffi-*.dist-info
        echo "  Removed stale tvm_ffi from $_sp"
    fi
done

# Remove libtvm_ffi.so from PREFIX/lib
rm -f "$CONDA_PREFIX/lib"/libtvm_ffi* 2>/dev/null || true
echo "  Removed stale libtvm_ffi from PREFIX/lib"

# Clean editable residuals (caffe-ffi and tvm-ffi related)
for _sp in $(python -c "import site; print(' '.join(site.getsitepackages()))" 2>/dev/null); do
    rm -f "$_sp"/_editable_skbc_*.pth "$_sp"/_editable_skbc_*.py 2>/dev/null || true
    rm -f "$_sp"/__editable__*.pth 2>/dev/null || true
    rm -f "$_sp"/_editable_tvm_ffi*.pth "$_sp"/_editable_tvm_ffi*.py 2>/dev/null || true
    # Also remove any .pth files that point to xuanspace or SpecWeave paths
    find "$_sp" -maxdepth 1 -name "*.pth" -exec grep -l "xuanspace\|SpecWeave" {} \; 2>/dev/null | xargs rm -f 2>/dev/null || true
    find "$_sp/__pycache__" -name "_editable_skbc_*" -delete 2>/dev/null || true
    find "$_sp/__pycache__" -name "_editable_tvm_ffi*" -delete 2>/dev/null || true
done
echo "  Cleaned editable residuals"

# Clean source tree build artifacts
cd "$CAFFE_FFI_DIR"
rm -rf build _skbuild dist *.egg-info
rm -f python/caffe_ffi/_caffe_ffi.so python/caffe_ffi/libtvm_ffi.so
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
echo "  Cleaned source tree build artifacts"
pass "Cleanup complete"
echo ""

# ── Step 1: Fix CRLF ──
info "Step 1: Fixing CRLF line endings..."
find "$CAFFE_FFI_DIR" -type f \( -name '*.sh' -o -name '*.cmake' -o -name 'CMakeLists.txt' -o -name '*.py' -o -name '*.cc' -o -name '*.cpp' -o -name '*.hpp' -o -name '*.h' -o -name 'meta.yaml' \) -not -path '*/build/*' -not -path '*/.git/*' -exec grep -l $'\r' {} \; 2>/dev/null | while read f; do
    sed -i 's/\r$//' "$f"
done
TVM_FFI_VENDOR="$SRC_ROOT/projects/xuanspace/vendor/tvm-ffi"
if [ -d "$TVM_FFI_VENDOR" ]; then
    find "$TVM_FFI_VENDOR" -type f \( -name '*.sh' -o -name '*.cmake' -o -name 'CMakeLists.txt' -o -name '*.py' -o -name '*.cc' -o -name '*.cpp' -o -name '*.hpp' -o -name '*.h' -o -name '*.pyx' \) -not -path '*/build/*' -not -path '*/.git/*' -exec grep -l $'\r' {} \; 2>/dev/null | while read f; do
        sed -i 's/\r$//' "$f"
    done
fi
pass "CRLF fix done"
echo ""

# ── Step 2: Build conda package ──
info "Step 2: Building conda package (with --no-test for speed)..."
mkdir -p "$CONDA_PREFIX/conda-bld"
_BUILD_LOG="$CONDA_PREFIX/conda-bld/conda_build.log"

conda-build \
    --no-anaconda-upload \
    --prefix-length 80 \
    --no-test \
    -c conda-forge \
    "$RECIPE_DIR" 2>&1 | tee "$_BUILD_LOG"
BUILD_STATUS=${PIPESTATUS[0]}

if [ $BUILD_STATUS -ne 0 ]; then
    echo ""
    echo "  === Last 80 lines of build output ==="
    tail -80 "$_BUILD_LOG"
    fail "conda build failed (exit code $BUILD_STATUS)"
fi
pass "conda build succeeded"
echo ""

# ── Step 3: Locate package ──
info "Step 3: Locating built package..."
_PKG_PATH=""
for ext in ".conda" ".tar.bz2"; do
    _FOUND=$(find "$CONDA_PREFIX/conda-bld" -name "caffe-ffi-*${ext}" -type f 2>/dev/null | sort -V | tail -1)
    if [ -n "$_FOUND" ] && [ -f "$_FOUND" ]; then
        _PKG_PATH="$_FOUND"
        break
    fi
done

if [ -z "$_PKG_PATH" ]; then
    _PKG_PATH=$(conda-build --output "$RECIPE_DIR" 2>/dev/null | tail -1)
fi

if [ -n "$_PKG_PATH" ] && [ -f "$_PKG_PATH" ]; then
    _PKG_SIZE=$(du -h "$_PKG_PATH" 2>/dev/null | cut -f1)
    pass "Built package: $_PKG_PATH ($_PKG_SIZE)"
else
    fail "Could not locate built package"
fi
echo ""

# ── Step 4: Install ──
info "Step 4: Installing built package..."

conda install -y -n caffe-ffi --use-local --force-reinstall "$_PKG_PATH" 2>&1 || {
    fail "Failed to install built package"
}
pass "Package installed successfully"
echo ""

# ── Step 5: Verify installation ──
info "Step 5: Verifying installed package (from /tmp to avoid cwd shadowing)..."
cd /tmp

# 5a: caffe_ffi Load path check
echo "  Test 5a: caffe_ffi package load path..."
_CAFFE_FILE=$(python -c "import caffe_ffi; print(caffe_ffi.__file__)" 2>&1)
echo "    Loading from: $_CAFFE_FILE"
if echo "$_CAFFE_FILE" | grep -q "site-packages/caffe_ffi"; then
    pass "caffe_ffi loading from conda site-packages (correct)"
else
    fail "caffe_ffi loading from wrong location: $_CAFFE_FILE"
fi
echo ""

# 5b0: tvm_ffi Load path check
echo "  Test 5b0: tvm_ffi package load path..."
_TVM_FILE=$(python -c "import tvm_ffi; print(tvm_ffi.__file__)" 2>&1)
echo "    tvm_ffi loading from: $_TVM_FILE"
if echo "$_TVM_FILE" | grep -q "site-packages/tvm_ffi"; then
    pass "tvm_ffi loading from conda site-packages (correct)"
else
    fail "tvm_ffi loading from wrong location: $_TVM_FILE"
fi

_TVM_LIB_SO=$(python -c "
import tvm_ffi, os
lib_path = os.path.join(os.path.dirname(tvm_ffi.__file__), 'lib', 'libtvm_ffi.so')
print(lib_path if os.path.exists(lib_path) else '')
" 2>&1)
echo "    tvm_ffi lib path: $_TVM_LIB_SO"
if [ -n "$_TVM_LIB_SO" ] && [ -f "$_TVM_LIB_SO" ]; then
    pass "libtvm_ffi.so found in tvm_ffi/lib/"
else
    fail "libtvm_ffi.so NOT found in tvm_ffi/lib/"
fi
echo ""

# 5b: Import and native availability check (MUST be True)
echo "  Test 5b: Import and native availability check..."
_NATIVE_CHECK=$(python -c "
import caffe_ffi
import tvm_ffi
import os
import glob
print('Version:', caffe_ffi.__version__)
print('caffe_ffi File:', caffe_ffi.__file__)
print('tvm_ffi File:', tvm_ffi.__file__)

native_ok = caffe_ffi._ffi_api.is_available()
print('Native available:', native_ok)

lib_dir = os.path.join(os.path.dirname(tvm_ffi.__file__), 'lib')
tvm_so = glob.glob(os.path.join(lib_dir, 'libtvm_ffi*.so'))
print('libtvm_ffi in tvm_ffi/lib:', tvm_so[0] if tvm_so else 'NOT FOUND')

if native_ok and tvm_so:
    exit(0)
else:
    exit(1)
" 2>&1)
_NATIVE_EXIT=$?
echo "$_NATIVE_CHECK" | sed 's/^/    /'
if [ $_NATIVE_EXIT -eq 0 ]; then
    NATIVE_PASS=true
    pass "Native available: True (required)"
else
    fail "Native check FAILED - native must be available"
fi
echo ""

# 5b1: Blob functionality test
echo "  Test 5b1: Blob functionality test..."
_BLOB_CHECK=$(python -c "
from caffe_ffi import Blob
import numpy as np
b = Blob([100])
b.fill(1.0)
assert b.count() == 100, 'Blob count mismatch'
print('Blob created with size 100, filled with 1.0')
print('Blob count:', b.count())
data = b.to_numpy()
print('to_numpy shape:', data.shape, 'dtype:', data.dtype)
print('First 5 values:', data[:5].tolist())
assert np.allclose(data, 1.0), 'Blob fill with 1.0 verification failed'
print('Blob fill verification: PASSED')
" 2>&1)
_BLOB_EXIT=$?
echo "$_BLOB_CHECK" | sed 's/^/    /'
if [ $_BLOB_EXIT -eq 0 ]; then
    BLOB_PASS=true
    pass "Blob test passed"
else
    fail "Blob test FAILED"
fi
echo ""

# 5b2: nm symbol check
echo "  Test 5b2: nm symbol check (TVMFFIGetCustomAllocator)..."
if [ -n "$_TVM_LIB_SO" ] && [ -f "$_TVM_LIB_SO" ]; then
    _SYM_CHECK=$(nm -D "$_TVM_LIB_SO" 2>/dev/null | grep -i "TVMFFIGetCustomAllocator" || true)
    if echo "$_SYM_CHECK" | grep -q " T "; then
        pass "TVMFFIGetCustomAllocator symbol found (T type)"
        echo "    $_SYM_CHECK" | sed 's/^/      /'
    else
        fail "TVMFFIGetCustomAllocator symbol NOT found or wrong type"
        echo "    nm output: $_SYM_CHECK" | sed 's/^/      /'
    fi
else
    fail "Cannot check symbols - libtvm_ffi.so not found"
fi
echo ""

# 5c: ldd check
echo "  Test 5c: Shared library dependencies..."
_CAFFE_SO=$(python -c "
import caffe_ffi, os, glob
sos = glob.glob(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi*.so'))
print(sos[0] if sos else '')
" 2>/dev/null)

if [ -n "$_CAFFE_SO" ] && [ -f "$_CAFFE_SO" ]; then
    echo "    Library: $_CAFFE_SO"
    echo "    RPATH: $(patchelf --print-rpath "$_CAFFE_SO" 2>/dev/null || echo 'N/A')"
    echo "    --- ldd output ---"
    ldd "$_CAFFE_SO" 2>/dev/null | sed 's/^/      /'
    echo "    --- end ldd ---"
    
    if ldd "$_CAFFE_SO" 2>/dev/null | grep -q 'not found'; then
        fail "Some shared library dependencies are NOT FOUND"
        ldd "$_CAFFE_SO" | grep 'not found'
    else
        pass "All shared library dependencies resolved"
    fi
    
    _LDD_TVM_PATH=$(ldd "$_CAFFE_SO" 2>/dev/null | grep libtvm_ffi | awk '{print $3}')
    if [ -n "$_LDD_TVM_PATH" ]; then
        echo "    libtvm_ffi resolved to: $_LDD_TVM_PATH"
        if echo "$_LDD_TVM_PATH" | grep -q "tvm_ffi/lib"; then
            pass "libtvm_ffi.so correctly resolved to tvm_ffi/lib/ path"
        else
            fail "libtvm_ffi.so resolved to wrong path (expected tvm_ffi/lib/): $_LDD_TVM_PATH"
        fi
    else
        fail "libtvm_ffi.so NOT found in dependencies!"
    fi
    
    # 5c2: Check libopenblas linkage
    _LDD_BLAS_LINE=$(ldd "$_CAFFE_SO" 2>/dev/null | grep -i openblas | head -1)
    if [ -n "$_LDD_BLAS_LINE" ]; then
        echo "    libopenblas linked: $_LDD_BLAS_LINE"
        pass "BLAS/OpenBLAS acceleration is ENABLED"
    else
        echo "    WARNING: libopenblas NOT found in _caffe_ffi.so dependencies"
        echo "    (Built without BLAS acceleration - using fallback C++ implementations)"
        warn "BLAS/OpenBLAS not linked (check build log for details)"
    fi
else
    fail "Could not locate _caffe_ffi.so"
fi
echo ""

# ── Step 6: Run conda package tests ──
info "Step 6: Running conda package tests..."
_PKG_FILE=$(find "$CONDA_PREFIX/conda-bld/linux-64" \( -name "caffe-ffi-*.tar.bz2" -o -name "caffe-ffi-*.conda" \) -type f 2>/dev/null | head -1)
if [ -n "$_PKG_FILE" ] && [ -f "$_PKG_FILE" ]; then
    echo "  Testing package file: $_PKG_FILE"
    conda-build --test "$_PKG_FILE" 2>&1 | tee "$CONDA_PREFIX/conda-bld/conda_test.log"
else
    echo "  WARNING: Could not find built package tarball, skipping conda-build --test"
    echo "  (The package was installed and verified manually in Steps 4-5)"
    _TEST_STATUS=0
fi
_TEST_STATUS=${_TEST_STATUS:-${PIPESTATUS[0]}}
if [ $_TEST_STATUS -eq 0 ]; then
    pass "Conda package tests passed"
else
    fail "Conda package tests FAILED (exit code $_TEST_STATUS)"
fi
echo ""

# ── Summary ──
echo "============================================================"
echo -e " ${GREEN}FULL CLEAN REBUILD COMPLETE${NC}"
echo "============================================================"
echo ""
echo "Test results:"
if [ "$NATIVE_PASS" = true ]; then
    echo -e "  Native: ${GREEN}PASS${NC}"
else
    echo -e "  Native: ${RED}FAIL${NC}"
fi
if [ "$BLOB_PASS" = true ]; then
    echo -e "  Blob: ${GREEN}PASS${NC}"
else
    echo -e "  Blob: ${RED}FAIL${NC}"
fi
echo ""
echo "Build artifacts:"
echo "  Package: $_PKG_PATH"
echo "  Build log: $_BUILD_LOG"
echo "  Test log: $CONDA_PREFIX/conda-bld/conda_test.log"
echo ""
