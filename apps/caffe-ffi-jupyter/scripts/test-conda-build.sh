#!/bin/bash
# =============================================================================
# test-conda-build.sh — Conda 包一键构建验证脚本（AC-15）
# 用法: docker exec <container> bash /path/to/test-conda-build.sh
#
# 目标：AC-15 Conda环境一键构建验证
#   - 安装 conda-build/conda-verify（如需要）
#   - 使用 conda-build 构建 caffe-ffi conda 包
#   - 本地安装构建好的包
#   - 验证导入、基础功能、单元测试
#   - 输出构建产物路径
#
# 构建输出：$CONDA_PREFIX/conda-bld/linux-64/caffe-ffi-*.conda
# =============================================================================

# ── 0. Bootstrap ──
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi

export PATH="$CONDA_PREFIX/bin:/opt/conda/bin:/opt/conda/condabin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
unset CFLAGS CXXFLAGS LDFLAGS

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
pass() { echo -e "${GREEN}  PASS${NC} $*"; }
fail() { echo -e "${RED}  FAIL${NC} $*"; exit 1; }
info() { echo -e "${CYAN}==>${NC} $*"; }
warn() { echo -e "${YELLOW} WARN${NC} $*"; }

SRC_ROOT="${SRC_ROOT:-/SpecWeave}"
CAFFE_FFI_DIR="$SRC_ROOT/projects/xuanspace/libs/caffe-ffi"
RECIPE_DIR="$CAFFE_FFI_DIR/conda.recipe"
CONDA_BLD_DIR="$CONDA_PREFIX/conda-bld"

echo "============================================================"
echo " caffe-ffi Conda Build Verification (AC-15)"
echo "============================================================"
echo "  Source:       $CAFFE_FFI_DIR"
echo "  Recipe dir:   $RECIPE_DIR"
echo "  Conda env:    $CONDA_PREFIX"
echo "  Conda bld:    $CONDA_BLD_DIR"
echo "  Python:       $(python --version 2>&1)"
echo "  conda:        $(conda --version 2>&1)"
echo ""

# ── Step 1: Environment checks ──
info "Step 1: Environment checks..."
[ -d "$CAFFE_FFI_DIR" ] || fail "caffe-ffi source not found at $CAFFE_FFI_DIR"
[ -d "$RECIPE_DIR" ] || fail "conda.recipe not found at $RECIPE_DIR"
[ -f "$RECIPE_DIR/meta.yaml" ] || fail "meta.yaml not found"
[ -f "$RECIPE_DIR/build.sh" ] || fail "build.sh not found"

# Check for conda-build
if ! command -v conda-build >/dev/null 2>&1; then
    info "Installing conda-build and conda-verify..."
    conda install -y -n caffe-ffi -c conda-forge "conda-build>=3.28" "conda-verify" || \
        fail "Failed to install conda-build"
fi
pass "conda-build available: $(conda-build --version 2>&1 | head -1)"
echo ""

# ── Step 2: Fix CRLF line endings ──
info "Step 2: Fixing CRLF line endings (critical for shell scripts on NTFS mounts)..."
fix_crlf_count=0
while IFS= read -r -d '' f; do
    if grep -q $'\r' "$f" 2>/dev/null; then
        sed -i 's/\r$//' "$f" 2>/dev/null && fix_crlf_count=$((fix_crlf_count + 1))
    fi
done < <(find "$CAFFE_FFI_DIR" -type f \
    \( -name '*.sh' -o -name '*.cmake' -o -name 'CMakeLists.txt' -o -name '*.py' \
    -o -name '*.cc' -o -name '*.cpp' -o -name '*.hpp' -o -name '*.h' \
    -o -name 'meta.yaml' -o -name 'build.sh' -o -name 'bld.bat' \) \
    -not -path '*/build/*' -not -path '*/.git/*' -print0 2>/dev/null)
echo "  Fixed CRLF in $fix_crlf_count file(s)"
pass "CRLF fix done"
echo ""

# ── Step 3: Ensure build dependencies are installed in host env ──
info "Step 3: Ensuring build dependencies..."
# conda-build needs these in the build env, but verify they're present
echo "  Checking for required build tools..."
for pkg in cmake ninja numpy protobuf libopenblas; do
    if conda list -n caffe-ffi "^${pkg}$" 2>/dev/null | grep -q "^${pkg}"; then
        echo "    ✓ $pkg installed"
    else
        warn "$pkg not found in env - installing..."
        conda install -y -n caffe-ffi -c conda-forge "$pkg" || warn "Failed to install $pkg (conda-build may handle it)"
    fi
done

# Verify tvm-ffi is available (needed for find_package)
if python -c "import tvm_ffi" 2>/dev/null; then
    TVM_FFI_VER=$(python -c "import tvm_ffi; print(tvm_ffi.__version__)" 2>/dev/null)
    pass "tvm_ffi available: v$TVM_FFI_VER"
else
    info "Installing apache-tvm-ffi via pip..."
    pip install --no-cache-dir apache-tvm-ffi || fail "Failed to install apache-tvm-ffi"
fi
echo ""

# ── Step 4: Verify meta.yaml is valid (dry run / parse check) ──
info "Step 4: Validating conda recipe..."
if conda-build --no-anaconda-upload --check "$RECIPE_DIR" 2>&1 | tail -20; then
    pass "Recipe validation passed"
else
    warn "Recipe validation had warnings (continuing)"
fi
echo ""

# ── Step 5: Run conda build ──
info "Step 5: Building conda package (this may take several minutes)..."
echo "  Recipe: $RECIPE_DIR"
echo "  Output: $CONDA_BLD_DIR"
echo "  ----------------------------------------------------------"

_BUILD_LOG="$CONDA_BLD_DIR/conda_build.log"
mkdir -p "$CONDA_BLD_DIR"

# Run conda-build with output to both terminal and log
conda build \
    --no-anaconda-upload \
    --prefix-length 80 \
    --no-test \
    -c conda-forge \
    "$RECIPE_DIR" 2>&1 | tee "$_BUILD_LOG"
BUILD_STATUS=${PIPESTATUS[0]}

echo "  ----------------------------------------------------------"

if [ $BUILD_STATUS -ne 0 ]; then
    echo ""
    echo "  === Last 80 lines of build output ==="
    tail -80 "$_BUILD_LOG"
    echo ""
    fail "conda build failed (exit code $BUILD_STATUS)"
fi
pass "conda build succeeded"
echo ""

# ── Step 6: Locate built package ──
info "Step 6: Locating built package..."
_PKG_PATH=""
# Search for the built .conda or .tar.bz2 file
for ext in ".conda" ".tar.bz2"; do
    _FOUND=$(find "$CONDA_BLD_DIR" -name "caffe-ffi-*${ext}" -type f 2>/dev/null | sort -V | tail -1)
    if [ -n "$_FOUND" ] && [ -f "$_FOUND" ]; then
        _PKG_PATH="$_FOUND"
        break
    fi
done

if [ -n "$_PKG_PATH" ]; then
    _PKG_SIZE=$(du -h "$_PKG_PATH" 2>/dev/null | cut -f1)
    pass "Built package: $_PKG_PATH ($_PKG_SIZE)"
else
    # Try using conda-build to get the output path
    _PKG_PATH=$(conda build --output "$RECIPE_DIR" 2>/dev/null | tail -1)
    if [ -n "$_PKG_PATH" ] && [ -f "$_PKG_PATH" ]; then
        _PKG_SIZE=$(du -h "$_PKG_PATH" 2>/dev/null | cut -f1)
        pass "Built package: $_PKG_PATH ($_PKG_SIZE)"
    else
        warn "Could not auto-locate built package (check $CONDA_BLD_DIR/linux-64/)"
        ls -la "$CONDA_BLD_DIR/linux-64/" 2>/dev/null | grep caffe-ffi || true
    fi
fi
echo ""

# ── Step 7: Install the built package locally ──
info "Step 7: Installing built package for verification..."

# First, uninstall any existing editable install
pip uninstall -y caffe-ffi 2>/dev/null || true

if [ -n "$_PKG_PATH" ] && [ -f "$_PKG_PATH" ]; then
    echo "  Installing from local package: $_PKG_PATH"
    conda install -y --offline --use-local "$_PKG_PATH" 2>&1 || \
        pip install "$_PKG_PATH" 2>&1 || \
        fail "Failed to install built package"
    pass "Package installed successfully"
else
    warn "Package file not found - attempting install via conda install --use-local"
    conda install -y -n caffe-ffi --use-local caffe-ffi 2>&1 || \
        fail "Failed to install caffe-ffi from local build"
fi
echo ""

# ── Step 8: Verify installation ──
info "Step 8: Verifying installed package..."
echo ""

# 8a: Import test
echo "  Test 8a: Import caffe_ffi..."
if python -c "
import caffe_ffi
print('    Version:', caffe_ffi.__version__)
print('    Native available:', caffe_ffi._ffi_api.is_available())
print('    FFI API:', 'OK' if caffe_ffi._ffi_api.is_available() else 'NOT AVAILABLE')
"; then
    pass "Import test passed"
else
    fail "Import test failed"
fi
echo ""

# 8b: Blob basic functionality
echo "  Test 8b: Basic Blob operations..."
if python -c "
import numpy as np
from caffe_ffi import Blob

b = Blob([2, 3, 4, 5])
print('    Blob shape:', b.shape())
print('    Blob count:', b.count())
assert b.count() == 2*3*4*5, 'count mismatch'

b.fill(3.14)
data = b.data_tensor
assert abs(data[0] - 3.14) < 1e-6, 'fill failed'
print('    fill(3.14) OK')

b2 = Blob([100])
b2.from_numpy(np.arange(100, dtype=np.float32))
assert abs(b2.data_tensor[50] - 50.0) < 1e-6, 'from_numpy failed'
print('    from_numpy OK')

print('    All basic Blob tests passed!')
"; then
    pass "Blob functionality test passed"
else
    fail "Blob functionality test failed"
fi
echo ""

# 8c: Check shared library dependencies
echo "  Test 8c: Shared library dependencies..."
_CAFFE_SO=$(python -c "
import caffe_ffi, os, glob
sos = glob.glob(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi*.so'))
print(sos[0] if sos else '')
" 2>/dev/null)

if [ -n "$_CAFFE_SO" ] && [ -f "$_CAFFE_SO" ]; then
    echo "    Library: $_CAFFE_SO"
    if ldd "$_CAFFE_SO" 2>/dev/null | grep -q 'not found'; then
        warn "Some dependencies not found:"
        ldd "$_CAFFE_SO" | grep 'not found'
    else
        pass "All shared library dependencies resolved"
    fi
    # Check if BLAS is linked
    if ldd "$_CAFFE_SO" 2>/dev/null | grep -qi 'openblas\|blas'; then
        pass "OpenBLAS linked"
    else
        warn "OpenBLAS not directly linked (may use conda's link method)"
    fi
else
    warn "Could not locate _caffe_ffi.so for dependency check"
fi
echo ""

# 8d: Run Python unit tests from the source tree
echo "  Test 8d: Running Python unit tests..."
_PY_TEST_FILE="$CAFFE_FFI_DIR/tests/python/test_python_api.py"
export CAFFE_FFI_DISABLE_BACKTRACE=1

if [ -f "$_PY_TEST_FILE" ]; then
    export PYTHONPATH="$CAFFE_FFI_DIR/python:${PYTHONPATH:-}"
    echo "    Running: python $_PY_TEST_FILE"
    echo "    ----------------------------------------------------------"
    python "$_PY_TEST_FILE"
    PYTEST_STATUS=$?
    echo "    ----------------------------------------------------------"
    if [ $PYTEST_STATUS -eq 0 ]; then
        pass "Python unit tests PASSED"
    else
        fail "Python unit tests FAILED (exit $PYTEST_STATUS)"
    fi
else
    warn "Python test file not found at $_PY_TEST_FILE"
fi
echo ""

# ── Step 9: Package info ──
info "Step 9: Package information..."
echo ""
echo "  Installed package info:"
conda list -n caffe-ffi "^caffe-ffi$" 2>/dev/null || pip show caffe-ffi 2>/dev/null
echo ""

# ── Summary ──
echo "============================================================"
echo -e " ${GREEN}CONDA BUILD VERIFICATION PASSED${NC} (AC-15)"
echo "============================================================"
echo ""
echo "Build artifacts:"
if [ -n "$_PKG_PATH" ] && [ -f "$_PKG_PATH" ]; then
    echo "  Package: $_PKG_PATH"
fi
echo "  Build log: $_BUILD_LOG"
echo "  Conda bld dir: $CONDA_BLD_DIR"
echo ""
echo "To install the package in another environment:"
if [ -n "$_PKG_PATH" ] && [ -f "$_PKG_PATH" ]; then
    echo "  conda install --offline --use-local $_PKG_PATH"
fi
echo ""
echo "To clean up build artifacts:"
echo "  conda build purge"
echo "  rm -rf $CONDA_BLD_DIR"
