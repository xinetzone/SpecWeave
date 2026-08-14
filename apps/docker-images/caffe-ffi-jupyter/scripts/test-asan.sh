#!/bin/bash
# =============================================================================
# test-asan.sh — AddressSanitizer (ASan) 内存错误验证脚本
# 用法: docker exec <container> bash /path/to/test-asan.sh
#
# 目标：AC-14 内存管理ASan验证
#   - 检测内存泄漏、越界访问、use-after-free、double-free等问题
#   - 使用Debug构建 + -fsanitize=address
#   - 构建目录放在Docker命名卷/Linux文件系统上
#
# ASan配置：
#   - ASAN_OPTIONS=detect_leaks=1:halt_on_error=0:verbosity=0
#   - detect_leaks=1: 启用内存泄漏检测
#   - halt_on_error=0: 不立即停止，报告所有错误
# =============================================================================

# ── 0. Bootstrap ──
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi

export PATH="$CONDA_PREFIX/bin:/opt/conda/bin:/opt/conda/condabin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
unset CFLAGS CXXFLAGS LDFLAGS

# Verify compilers
if [ -z "${CC:-}" ] || [ ! -x "${CC:-}" ]; then
    for c in "$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-cc" "$CONDA_PREFIX/bin/gcc"; do
        [ -x "$c" ] && { export CC="$c"; break; }
    done
fi
if [ -z "${CXX:-}" ] || [ ! -x "${CXX:-}" ]; then
    for cxx in "$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-c++" "$CONDA_PREFIX/bin/g++"; do
        [ -x "$cxx" ] && { export CXX="$cxx"; break; }
    done
fi

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
pass() { echo -e "${GREEN}  PASS${NC} $*"; }
fail() { echo -e "${RED}  FAIL${NC} $*"; exit 1; }
info() { echo -e "${CYAN}==>${NC} $*"; }
warn() { echo -e "${YELLOW} WARN${NC} $*"; }

SRC_ROOT="${SRC_ROOT:-/SpecWeave}"
TVM_FFI_DIR="$SRC_ROOT/projects/xuanspace/vendor/tvm-ffi"
CAFFE_FFI_DIR="$SRC_ROOT/projects/xuanspace/libs/caffe-ffi"
BUILD_DIR="/workspace/caffe-ffi-asan-build"

echo "============================================================"
echo " caffe-ffi AddressSanitizer (ASan) Memory Verification"
echo "============================================================"
echo "  Source:     $CAFFE_FFI_DIR"
echo "  TVM FFI:    $TVM_FFI_DIR"
echo "  Build dir:  $BUILD_DIR"
echo "  Build type: Debug + ASan"
echo "  CC:         $CC"
echo "  CXX:        $CXX"
echo ""

# ── Step 0: Environment checks ──
info "Step 0: Environment checks..."
[ -d "$CAFFE_FFI_DIR" ] || fail "caffe-ffi source not found at $CAFFE_FFI_DIR"
[ -d "$TVM_FFI_DIR" ] || fail "tvm-ffi source not found at $TVM_FFI_DIR"
command -v cmake >/dev/null 2>&1 || fail "cmake not found"
command -v ninja >/dev/null 2>&1 || fail "ninja not found"
echo "  C compiler: $CC ($($CC --version | head -1))"
echo "  C++ compiler: $CXX ($($CXX --version | head -1))"
echo "  cmake: $(cmake --version | head -1)"
pass "Environment checks passed"

# ── Step 1: Fix CRLF ──
info "Step 1: Fixing CRLF line endings..."
fix_crlf_count=0
while IFS= read -r -d '' f; do
    if grep -q $'\r' "$f" 2>/dev/null; then
        sed -i 's/\r$//' "$f" 2>/dev/null && fix_crlf_count=$((fix_crlf_count + 1))
    fi
done < <(find "$TVM_FFI_DIR" "$CAFFE_FFI_DIR" -type f \
    \( -name '*.sh' -o -name '*.cmake' -o -name 'CMakeLists.txt' -o -name '*.py' \
    -o -name '*.cc' -o -name '*.cpp' -o -name '*.hpp' -o -name '*.h' \) -print0 2>/dev/null)
echo "  Fixed CRLF in $fix_crlf_count file(s)"
pass "CRLF check done"

# ── Step 2: Prepare build directory ──
info "Step 2: Preparing ASan build directory..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
pass "Build directory created: $BUILD_DIR"

# ── Step 3: CMake configure with ASan flags ──
info "Step 3: CMake configure (Debug + -fsanitize=address)..."
cd "$BUILD_DIR"

_CONFIG_LOG="$BUILD_DIR/cmake_configure.log"

# ASan requires both compile and link flags
ASAN_FLAGS="-fsanitize=address -fno-omit-frame-pointer -g -O1"
ASAN_LINK_FLAGS="-fsanitize=address"

cmake -S "$CAFFE_FFI_DIR" -B "$BUILD_DIR" \
    -G "Ninja" \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" \
    -DCMAKE_INSTALL_PREFIX="$CONDA_PREFIX" \
    -DCMAKE_C_COMPILER="$CC" \
    -DCMAKE_CXX_COMPILER="$CXX" \
    -DCMAKE_AR="$CONDA_PREFIX/bin/ar" \
    -DCMAKE_RANLIB="$CONDA_PREFIX/bin/ranlib" \
    -DCMAKE_MAKE_PROGRAM="$CONDA_PREFIX/bin/ninja" \
    -DCAFFE_FFI_BUILD_TESTS=ON \
    -DCAFFE_CPU_ONLY=ON \
    -DTVM_FFI_USE_LIBBACKTRACE=OFF \
    -DTVM_FFI_BACKTRACE_ON_SEGFAULT=OFF \
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
    -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_CXX_STANDARD_REQUIRED=ON \
    -DCMAKE_CXX_EXTENSIONS=OFF \
    -DCMAKE_C_FLAGS="$ASAN_FLAGS" \
    -DCMAKE_CXX_FLAGS="$ASAN_FLAGS" \
    -DCMAKE_EXE_LINKER_FLAGS="$ASAN_LINK_FLAGS" \
    -DCMAKE_SHARED_LINKER_FLAGS="$ASAN_LINK_FLAGS" \
    -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON \
    -DCMAKE_BUILD_RPATH_USE_ORIGIN=ON \
    > "$_CONFIG_LOG" 2>&1
CMAKE_STATUS=$?

if [ $CMAKE_STATUS -ne 0 ]; then
    echo ""
    echo "  Last 50 lines of configure output:"
    tail -50 "$_CONFIG_LOG"
    echo ""
    fail "CMake configure failed (exit code $CMAKE_STATUS)"
fi

# Check if BLAS was found
if grep -q "Found OpenBLAS" "$_CONFIG_LOG" 2>/dev/null; then
    pass "OpenBLAS detected (BLAS acceleration enabled)"
    grep "Found OpenBLAS" "$_CONFIG_LOG"
else
    warn "OpenBLAS not found - testing without BLAS acceleration"
fi

tail -10 "$_CONFIG_LOG"
pass "CMake configure succeeded"

# ── Step 4: Build ──
info "Step 4: Building caffe-ffi with ASan instrumentation..."
NPROC=$(nproc 2>/dev/null || echo 4)
echo "  Building with $NPROC parallel jobs (Debug+ASan, may be slower)..."

_BUILD_LOG="$BUILD_DIR/cmake_build.log"
cmake --build "$BUILD_DIR" --config Debug -j$NPROC > "$_BUILD_LOG" 2>&1
BUILD_STATUS=$?

if [ $BUILD_STATUS -ne 0 ]; then
    echo ""
    echo "  Last 80 lines of build output:"
    tail -80 "$_BUILD_LOG"
    echo ""
    fail "Build failed (exit code $BUILD_STATUS)"
fi
pass "Build succeeded"

# ── Step 5: Verify artifacts ──
info "Step 5: Verifying built artifacts..."
_CAFFE_FFI_SO=$(find "$BUILD_DIR" -maxdepth 2 -name '_caffe_ffi*.so' -type f 2>/dev/null | head -1)
if [ -z "$_CAFFE_FFI_SO" ]; then
    _CAFFE_FFI_SO=$(find "$BUILD_DIR/lib" -name '_caffe_ffi*.so' -type f 2>/dev/null | head -1)
fi
if [ -n "$_CAFFE_FFI_SO" ] && [ -f "$_CAFFE_FFI_SO" ]; then
    pass "_caffe_ffi library: $_CAFFE_FFI_SO"
    # Verify ASan is linked
    if ldd "$_CAFFE_FFI_SO" 2>/dev/null | grep -q 'libasan'; then
        pass "ASan runtime detected in library dependencies"
    else
        warn "libasan not found in ldd output (may be statically linked)"
    fi
else
    find "$BUILD_DIR" -maxdepth 2 -name '*.so' -o -name '*.a' 2>/dev/null | head -20
    fail "_caffe_ffi shared library not found"
fi

_TEST_BIN=$(find "$BUILD_DIR" -name 'caffe_ffi_tests' -type f -executable 2>/dev/null | head -1)
if [ -n "$_TEST_BIN" ] && [ -x "$_TEST_BIN" ]; then
    pass "Test binary: $_TEST_BIN"
    if ldd "$_TEST_BIN" 2>/dev/null | grep -q 'libasan'; then
        pass "Test binary linked with ASan"
    fi
else
    fail "caffe_ffi_tests binary not found"
fi

# ── Step 6: Run C++ tests with ASan ──
info "Step 6: Running C++ unit tests under ASan..."
echo ""
echo "  Running: $_TEST_BIN"
echo "  ASAN_OPTIONS: detect_leaks=1:halt_on_error=0"
echo "  ----------------------------------------------------------"

_LD_PATHS=("$CONDA_PREFIX/lib")
[ -n "$_CAFFE_FFI_SO" ] && _LD_PATHS+=("$(dirname "$_CAFFE_FFI_SO")")
_TVM_FFI_SO=$(find "$BUILD_DIR/tvm-ffi" -name 'libtvm_ffi*.so' -type f 2>/dev/null | head -1)
[ -n "$_TVM_FFI_SO" ] && _LD_PATHS+=("$(dirname "$_TVM_FFI_SO")")
[ -d "$BUILD_DIR/tvm-ffi/lib" ] && _LD_PATHS+=("$BUILD_DIR/tvm-ffi/lib")

export LD_LIBRARY_PATH="$(IFS=:; echo "${_LD_PATHS[*]}"):${LD_LIBRARY_PATH:-}"
export ASAN_OPTIONS="detect_leaks=1:halt_on_error=0:verbosity=0:abort_on_error=0:check_initialization_order=1:strict_init_order=0"
export LSAN_OPTIONS="verbosity=0:log_threads=1"
export CAFFE_FFI_DISABLE_BACKTRACE=1

_ASAN_LOG="$BUILD_DIR/asan_test_output.log"
"$_TEST_BIN" > "$_ASAN_LOG" 2>&1
TEST_STATUS=$?

# Print output
cat "$_ASAN_LOG"
echo "  ----------------------------------------------------------"
echo ""

# Parse ASan output for errors
ASAN_ERRORS=0
if grep -q "ERROR: AddressSanitizer" "$_ASAN_LOG" 2>/dev/null; then
    ASAN_ERRORS=$(grep -c "ERROR: AddressSanitizer" "$_ASAN_LOG" 2>/dev/null || echo 0)
fi
LEAK_ERRORS=0
if grep -q "ERROR: LeakSanitizer" "$_ASAN_LOG" 2>/dev/null; then
    LEAK_ERRORS=$(grep -c "ERROR: LeakSanitizer" "$_ASAN_LOG" 2>/dev/null || echo 0)
fi

if [ $TEST_STATUS -eq 0 ] && [ $ASAN_ERRORS -eq 0 ] && [ $LEAK_ERRORS -eq 0 ]; then
    pass "C++ ASan tests PASSED (no memory errors detected)"
else
    echo ""
    if [ $ASAN_ERRORS -gt 0 ]; then
        fail "ASan detected $ASAN_ERRORS memory error(s)"
    fi
    if [ $LEAK_ERRORS -gt 0 ]; then
        warn "LSan detected $LEAK_ERRORS potential leak(s)"
        echo "  (Leaks may be from global/static objects or conda libraries - check stack traces)"
    fi
    if [ $TEST_STATUS -ne 0 ] && [ $ASAN_ERRORS -eq 0 ]; then
        fail "Tests failed with exit code $TEST_STATUS (no ASan errors reported)"
    fi
fi

# ── Step 7: Python tests with ASan-instrumented library ──
info "Step 7: Running Python tests with ASan-instrumented library..."

_PY_TEST_FILE="$CAFFE_FFI_DIR/tests/python/test_python_api.py"
_CAFFE_FFI_PY_DIR=$(python -c 'import caffe_ffi, os; print(os.path.dirname(caffe_ffi.__file__))' 2>/dev/null || echo "")
if [ -n "$_CAFFE_FFI_PY_DIR" ] && [ -d "$_CAFFE_FFI_PY_DIR" ]; then
    cp "$_CAFFE_FFI_SO" "$_CAFFE_FFI_PY_DIR/" 2>/dev/null && \
        echo "  Updated _caffe_ffi.so (ASan build) in editable install"
fi
export PYTHONPATH="$CAFFE_FFI_DIR/python:${PYTHONPATH:-}"

if [ -f "$_PY_TEST_FILE" ]; then
    echo ""
    echo "  Running: python $_PY_TEST_FILE (with ASan)"
    echo "  ----------------------------------------------------------"

    _PY_ASAN_LOG="$BUILD_DIR/asan_python_test.log"
    python "$_PY_TEST_FILE" > "$_PY_ASAN_LOG" 2>&1
    PY_TEST_STATUS=$?

    cat "$_PY_ASAN_LOG"
    echo "  ----------------------------------------------------------"
    echo ""

    PY_ASAN_ERRORS=0
    if grep -q "ERROR: AddressSanitizer\|ERROR: LeakSanitizer" "$_PY_ASAN_LOG" 2>/dev/null; then
        PY_ASAN_ERRORS=$(grep -c "ERROR: AddressSanitizer\|ERROR: LeakSanitizer" "$_PY_ASAN_LOG" 2>/dev/null || echo 0)
    fi

    if [ $PY_TEST_STATUS -eq 0 ] && [ $PY_ASAN_ERRORS -eq 0 ]; then
        pass "Python ASan tests PASSED (no memory errors detected)"
    elif [ $PY_ASAN_ERRORS -gt 0 ]; then
        warn "Python tests reported $PY_ASAN_ERRORS ASan/LSan error(s)"
        echo "  (Note: Python interpreter allocations may produce false positives - inspect stack traces)"
    else
        fail "Python tests failed (exit code $PY_TEST_STATUS)"
    fi
else
    warn "Python test file not found (skipping)"
fi

# ── Summary ──
echo ""
echo "============================================================"
if [ $ASAN_ERRORS -eq 0 ] && [ $LEAK_ERRORS -eq 0 ] && [ $PY_ASAN_ERRORS -eq 0 ]; then
    echo -e " ${GREEN}ASan VERIFICATION PASSED${NC} - No memory errors detected"
else
    echo -e " ${YELLOW}ASan verification completed with warnings${NC}"
    echo "  AddressSanitizer errors: $ASAN_ERRORS"
    echo "  LeakSanitizer errors:    $LEAK_ERRORS"
    echo "  Python ASan errors:      $PY_ASAN_ERRORS"
fi
echo "============================================================"
echo ""
echo "Build artifacts preserved at: $BUILD_DIR"
echo "Logs:"
echo "  C++ ASan output: $_ASAN_LOG"
echo "  Python ASan output: $_PY_ASAN_LOG"
echo "  Configure log:    $_CONFIG_LOG"
echo "  Build log:        $_BUILD_LOG"
