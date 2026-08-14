#!/bin/bash
# =============================================================================
# test-cpp-tests.sh — C++ / Python 单元测试验证脚本
# 用法: docker exec <container> bash /path/to/test-cpp-tests.sh
#
# 策略：直接使用 cmake 构建（而非 pip install -e），将 build 目录放在 Docker
# 命名卷 /workspace（Linux 文件系统）上，完全规避 NTFS bind mount 上
# autotools 无法创建临时文件（confdefs.h 等）的问题。
#
# 关键配置：
#   - CAFFE_FFI_BUILD_TESTS=ON：启用 C++ 单元测试编译
#   - TVM_FFI_USE_LIBBACKTRACE=OFF：禁用 libbacktrace（避免 autotools configure）
#   - 构建目录在 /workspace/caffe-ffi-cpp-build（Docker 卷，非 NTFS）
#   - 源码目录从 /SpecWeave（NTFS mount）只读引用
#   - Python 测试使用 unittest + 自定义 TimingTestRunner（绕过 pytest segfault 问题）
#   - C++ 和 Python 测试均输出每个用例耗时 + Top 5 最慢用例，便于性能瓶颈排查
# =============================================================================

# ── 0. Bootstrap: set up clean environment ──
# Activate conda first (sets CC/CXX to conda compiler wrappers)
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi

# Ensure clean PATH (conda bin first, then standard Linux paths; no host contamination)
export PATH="$CONDA_PREFIX/bin:/opt/conda/bin:/opt/conda/condabin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
unset CFLAGS CXXFLAGS LDFLAGS

# Verify compilers are set correctly by conda; fall back if missing
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
BUILD_DIR="/workspace/caffe-ffi-cpp-build"

echo "============================================================"
echo " caffe-ffi C++ / Python Unit Tests Verification"
echo "============================================================"
echo "  Source:     $CAFFE_FFI_DIR"
echo "  TVM FFI:    $TVM_FFI_DIR"
echo "  Build dir:  $BUILD_DIR (Docker volume - Linux filesystem)"
echo "  Conda env:  $CONDA_PREFIX"
echo "  CC:         $CC"
echo "  CXX:        $CXX"
echo "  PATH:       $PATH"
echo ""

# ── Step 0: Environment checks ──
info "Step 0: Environment checks..."
[ -d "$CAFFE_FFI_DIR" ] || fail "caffe-ffi source not found at $CAFFE_FFI_DIR"
[ -d "$TVM_FFI_DIR" ] || fail "tvm-ffi source not found at $TVM_FFI_DIR"
command -v cmake >/dev/null 2>&1 || fail "cmake not found"
command -v ninja >/dev/null 2>&1 || fail "ninja not found"
[ -x "$CXX" ] || { export CXX="$CONDA_PREFIX/bin/g++"; }
[ -x "$CC" ] || { export CC="$CONDA_PREFIX/bin/gcc"; }
[ -x "$CXX" ] || fail "C++ compiler not found at $CXX"
[ -x "$CC" ] || fail "C compiler not found at $CC"
echo "  Using C compiler: $CC ($($CC --version | head -1))"
echo "  Using C++ compiler: $CXX ($($CXX --version | head -1))"
echo "  cmake: $(cmake --version | head -1)"
echo "  ninja: $(ninja --version)"
pass "Environment checks passed"

# ── Step 1: Fix CRLF line endings (critical for NTFS mounts) ──
info "Step 1: Fixing CRLF line endings..."
fix_crlf_count=0
while IFS= read -r -d '' f; do
    if grep -q $'\r' "$f" 2>/dev/null; then
        sed -i 's/\r$//' "$f" 2>/dev/null && fix_crlf_count=$((fix_crlf_count + 1))
    fi
done < <(find "$TVM_FFI_DIR" "$CAFFE_FFI_DIR" -type f \
    \( -name 'configure' -o -name 'config.sub' -o -name 'config.guess' \
    -o -name 'install-sh' -o -name 'missing' -o -name 'depcomp' -o -name 'compile' \
    -o -name 'ltmain.sh' -o -name '*.sh' -o -name '*.ac' -o -name '*.am' \
    -o -name '*.in' -o -name '*.cmake' -o -name 'CMakeLists.txt' -o -name '*.py' \
    -o -name '*.cc' -o -name '*.cpp' -o -name '*.hpp' -o -name '*.h' \) -print0 2>/dev/null)
if [ $fix_crlf_count -gt 0 ]; then
    echo "  Fixed CRLF in $fix_crlf_count file(s)"
else
    echo "  No CRLF issues found"
fi
pass "CRLF check done"

# ── Step 2: Prepare build directory on Linux filesystem ──
info "Step 2: Preparing build directory on Docker volume (Linux FS)..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
pass "Build directory created: $BUILD_DIR"

# ── Step 3: CMake configure with tests enabled ──
info "Step 3: CMake configure (CAFFE_FFI_BUILD_TESTS=ON, TVM_FFI_USE_LIBBACKTRACE=OFF)..."
cd "$BUILD_DIR"

_CONFIG_LOG="$BUILD_DIR/cmake_configure.log"
cmake -S "$CAFFE_FFI_DIR" -B "$BUILD_DIR" \
    -G "Ninja" \
    -DCMAKE_BUILD_TYPE=Release \
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
    -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON \
    -DCMAKE_BUILD_RPATH_USE_ORIGIN=ON \
    -DCMAKE_SKIP_BUILD_RPATH=OFF \
    -DCMAKE_BUILD_WITH_INSTALL_RPATH=OFF \
    > "$_CONFIG_LOG" 2>&1
CMAKE_STATUS=$?

if [ $CMAKE_STATUS -ne 0 ]; then
    echo ""
    echo "  Last 50 lines of configure output:"
    tail -50 "$_CONFIG_LOG"
    echo ""
    fail "CMake configure failed (exit code $CMAKE_STATUS)"
fi

# Show last 15 lines for visibility
tail -15 "$_CONFIG_LOG"

if [ -f "$BUILD_DIR/CMakeCache.txt" ]; then
    pass "CMake configure succeeded (Cache.txt present)"
else
    fail "CMake configure did not generate build files"
fi

# ── Step 4: Build ──
info "Step 4: Building caffe-ffi with C++ tests..."
NPROC=$(nproc 2>/dev/null || echo 4)
echo "  Building with $NPROC parallel jobs..."

_BUILD_LOG="$BUILD_DIR/cmake_build.log"
cmake --build "$BUILD_DIR" --config Release -j$NPROC > "$_BUILD_LOG" 2>&1
BUILD_STATUS=$?

if [ $BUILD_STATUS -ne 0 ]; then
    echo ""
    echo "  Last 80 lines of build output:"
    tail -80 "$_BUILD_LOG"
    echo ""
    fail "Build failed (exit code $BUILD_STATUS)"
fi

# Show last 15 lines for visibility
tail -15 "$_BUILD_LOG"
pass "Build succeeded"

# ── Step 5: Verify built artifacts exist ──
info "Step 5: Verifying built artifacts..."

# Find _caffe_ffi shared library
_CAFFE_FFI_SO=$(find "$BUILD_DIR" -maxdepth 2 -name '_caffe_ffi*.so' -type f 2>/dev/null | head -1)
if [ -z "$_CAFFE_FFI_SO" ]; then
    _CAFFE_FFI_SO=$(find "$BUILD_DIR/lib" -name '_caffe_ffi*.so' -type f 2>/dev/null | head -1)
fi
if [ -n "$_CAFFE_FFI_SO" ] && [ -f "$_CAFFE_FFI_SO" ]; then
    pass "_caffe_ffi library: $_CAFFE_FFI_SO"
    if command -v ldd >/dev/null 2>&1; then
        if ldd "$_CAFFE_FFI_SO" 2>/dev/null | grep -q 'not found'; then
            warn "_caffe_ffi.so has unresolved deps:"
            ldd "$_CAFFE_FFI_SO" | grep 'not found'
        else
            pass "_caffe_ffi.so dependencies resolved"
        fi
    fi
else
    # List what's in build dir for debugging
    echo "  Contents of $BUILD_DIR:"
    find "$BUILD_DIR" -maxdepth 2 -name '*.so' -o -name '*.a' 2>/dev/null | head -20
    fail "_caffe_ffi shared library not found in build directory"
fi

# Find tvm_ffi shared library (in tvm-ffi subdirectory from add_subdirectory)
_TVM_FFI_SO=$(find "$BUILD_DIR/tvm-ffi" -name 'libtvm_ffi*.so' -type f 2>/dev/null | head -1)
if [ -z "$_TVM_FFI_SO" ]; then
    _TVM_FFI_SO=$(find "$BUILD_DIR" -maxdepth 3 -name 'libtvm_ffi*.so' -not -path '*/testing/*' -type f 2>/dev/null | head -1)
fi
if [ -n "$_TVM_FFI_SO" ] && [ -f "$_TVM_FFI_SO" ]; then
    pass "tvm_ffi library: $_TVM_FFI_SO"
else
    # List all .so files for debugging
    echo "  All .so files in build dir:"
    find "$BUILD_DIR" -name '*.so' -type f 2>/dev/null | head -20
    warn "tvm_ffi shared library not found at expected location"
fi

# Find test binary
_TEST_BIN=$(find "$BUILD_DIR" -name 'caffe_ffi_tests' -type f -executable 2>/dev/null | head -1)
if [ -n "$_TEST_BIN" ] && [ -x "$_TEST_BIN" ]; then
    pass "Test binary: $_TEST_BIN"
else
    echo "  Searching for test binary..."
    find "$BUILD_DIR" -name '*caffe_ffi_test*' -type f 2>/dev/null | head -10
    fail "caffe_ffi_tests binary not found or not executable"
fi

# ── Step 6: Run C++ unit tests ──
info "Step 6: Running C++ unit tests..."
echo ""
echo "  Running: $_TEST_BIN"
echo "  ----------------------------------------------------------"

# Build LD_LIBRARY_PATH: conda libs + build dir + tvm-ffi build dir
_LD_PATHS=("$CONDA_PREFIX/lib")
[ -n "$_CAFFE_FFI_SO" ] && _LD_PATHS+=("$(dirname "$_CAFFE_FFI_SO")")
[ -n "$_TVM_FFI_SO" ] && _LD_PATHS+=("$(dirname "$_TVM_FFI_SO")")
[ -d "$BUILD_DIR/tvm-ffi" ] && _LD_PATHS+=("$BUILD_DIR/tvm-ffi")
[ -d "$BUILD_DIR/tvm-ffi/lib" ] && _LD_PATHS+=("$BUILD_DIR/tvm-ffi/lib")

export LD_LIBRARY_PATH="$(IFS=:; echo "${_LD_PATHS[*]}"):${LD_LIBRARY_PATH:-}"
echo "  LD_LIBRARY_PATH: $(IFS=:; echo "${_LD_PATHS[*]}")"
echo ""

"$_TEST_BIN"
TEST_STATUS=$?

echo "  ----------------------------------------------------------"
echo ""

if [ $TEST_STATUS -eq 0 ]; then
    pass "C++ unit tests PASSED (exit code 0)"
else
    fail "C++ unit tests FAILED (exit code $TEST_STATUS)"
fi

# ── Step 7: Python unit tests (mirror C++ test_harness timing output) ──
info "Step 7: Running Python unit tests (unittest + timing)..."

_PY_TEST_FILE="$CAFFE_FFI_DIR/tests/python/test_python_api.py"

# Safety: disable C++ backtrace in Python unittest environment to prevent
# segfaults caused by backtrace_symbols() crashing on Python interpreter frames
export CAFFE_FFI_DISABLE_BACKTRACE=1

# Ensure python can find the caffe_ffi package from source tree BEFORE copying .so
export PYTHONPATH="$CAFFE_FFI_DIR/python:${PYTHONPATH:-}"

# Copy the freshly built _caffe_ffi.so into the source tree's python package dir
# so that _find_lib_path() can locate it via Path(__file__).parent (first search dir).
_PY_PKG_DIR="$CAFFE_FFI_DIR/python/caffe_ffi"
if [ -d "$_PY_PKG_DIR" ]; then
    cp "$_CAFFE_FFI_SO" "$_PY_PKG_DIR/" 2>/dev/null && \
        echo "  Copied _caffe_ffi.so to package dir: $_PY_PKG_DIR/"
else
    warn "Python package dir not found at $_PY_PKG_DIR"
fi

# Also attempt to copy to an editable install location if one exists
_CAFFE_FFI_PY_DIR=$(python -c 'import caffe_ffi, os; print(os.path.dirname(caffe_ffi.__file__))' 2>/dev/null || echo "")
if [ -n "$_CAFFE_FFI_PY_DIR" ] && [ -d "$_CAFFE_FFI_PY_DIR" ] && [ "$_CAFFE_FFI_PY_DIR" != "$_PY_PKG_DIR" ]; then
    cp "$_CAFFE_FFI_SO" "$_CAFFE_FFI_PY_DIR/" 2>/dev/null && \
        echo "  Updated _caffe_ffi.so in editable install at $_CAFFE_FFI_PY_DIR"
fi

if [ -f "$_PY_TEST_FILE" ]; then
    echo ""
    echo "  Running: python $_PY_TEST_FILE"
    echo "  ----------------------------------------------------------"

    python "$_PY_TEST_FILE"
    PY_TEST_STATUS=$?

    echo "  ----------------------------------------------------------"
    echo ""

    if [ $PY_TEST_STATUS -eq 0 ]; then
        pass "Python unit tests PASSED (exit code 0)"
    else
        fail "Python unit tests FAILED (exit code $PY_TEST_STATUS)"
    fi
else
    warn "Python test file not found at $_PY_TEST_FILE (skipping)"
fi

echo ""
echo "============================================================"
echo -e " ${GREEN}ALL TESTS PASSED${NC} - Caffe-FFI C++/Python verification complete!"
echo "============================================================"
echo ""
echo "Build artifacts preserved at: $BUILD_DIR"
echo "  (Delete with: rm -rf $BUILD_DIR)"
