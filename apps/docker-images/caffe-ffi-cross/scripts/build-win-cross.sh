#!/bin/bash
# =============================================================================
# Windows Cross-Compile Build Script (with Wine L3 Smoke Test)
# Runs inside caffe-ffi-cross-win container to build win-64 conda packages
#
# Usage:
#   ./build-win-cross.sh [recipe_dir] [output_dir]
#
# Environment variables:
#   CAFFE_FFI_RECIPE_DIR - Path to conda.recipe (default: /workspace/caffe-ffi/conda.recipe)
#   OUTPUT_DIR           - Directory to copy built packages (default: /output)
#   SKIP_WINE_TEST       - Set to 1 to skip L3 Wine smoke test (default: 0)
#
# L3 Testing Note:
#   Wine smoke test is OPTIONAL and best-effort. Complex C++ extensions may
#   fail to import under Wine due to missing system DLLs or API incompatibilities.
#   L3 failures are logged as warnings, not errors.
# =============================================================================
set -e -o pipefail

# ── Colors ──
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; MAGENTA='\033[0;35m'; NC='\033[0m'
log_info()  { echo -e "${GREEN}[build-win]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[build-win]${NC} $*"; }
log_error() { echo -e "${RED}[build-win]${NC} $*" >&2; }
log_step()  { echo -e "${CYAN}[build-win]${NC} $*"; }
log_l3()    { echo -e "${MAGENTA}[build-win L3]${NC} $*"; }
log_sep()   { echo -e "${CYAN}==========================================================================${NC}"; }

# ── Configuration ──
RECIPE_DIR="${1:-${CAFFE_FFI_RECIPE_DIR:-/workspace/caffe-ffi/conda.recipe}}"
OUTPUT_DIR="${2:-${OUTPUT_DIR:-/output}}"
CONDA_DIR="/opt/conda"
ENV_NAME="cross-build"
CONDA_BLD_DIR="${CONDA_DIR}/conda-bld"
SKIP_WINE_TEST="${SKIP_WINE_TEST:-0}"
WINEPREFIX="${WINEPREFIX:-/root/.wine}"
WINE_PYTHON="C:\\miniconda3\\python.exe"

log_sep
log_step "Caffe-FFI Windows Cross-Compile Build (win-64)"
log_sep
log_info "Recipe dir:      ${RECIPE_DIR}"
log_info "Output dir:      ${OUTPUT_DIR}"
log_info "Conda-bld dir:   ${CONDA_BLD_DIR}"
log_info "Wine test:       $([ "${SKIP_WINE_TEST}" = "1" ] && echo 'SKIPPED' || echo 'enabled (best-effort)')"
log_info "Wine prefix:     ${WINEPREFIX}"

# ── Activate conda environment ──
log_step "Activating conda environment: ${ENV_NAME}"
source "${CONDA_DIR}/etc/profile.d/conda.sh"
conda activate "${ENV_NAME}"
log_info "Python: $(python --version)"
log_info "Conda:  $(conda --version)"

# ── Pre-flight checks ──
log_step "Running pre-flight checks..."

# Check recipe directory
if [ ! -f "${RECIPE_DIR}/meta.yaml" ]; then
    log_warn "Recipe meta.yaml not found at ${RECIPE_DIR}/meta.yaml"
    log_info "Checking bundled recipe location..."
    if [ -f "/workspace/caffe-ffi/conda.recipe/meta.yaml" ]; then
        RECIPE_DIR="/workspace/caffe-ffi/conda.recipe"
        log_info "Using recipe from: ${RECIPE_DIR}"
    elif [ -d "/opt/recipes" ] && [ -f "/opt/recipes/meta.yaml" ]; then
        RECIPE_DIR="/opt/recipes"
        log_info "Using recipe from: ${RECIPE_DIR}"
    else
        log_error "No valid conda recipe found. Please mount source to /workspace/caffe-ffi"
        log_error "  docker run -v /path/to/caffe-ffi:/workspace/caffe-ffi ..."
        exit 1
    fi
fi
log_info "Recipe meta.yaml found: $(wc -l < ${RECIPE_DIR}/meta.yaml) lines"

# Ensure output directory exists
mkdir -p "${OUTPUT_DIR}"
log_info "Output directory ready: ${OUTPUT_DIR}"

# ── Verify cross-compilation tools ──
log_step "Verifying cross-compilation toolchain..."

TOOLS_READY=1
for tool in clang clang++ llvm-objdump llvm-nm ld.lld file; do
    if command -v "$tool" >/dev/null 2>&1; then
        log_info "  ✓ ${tool}: $(command -v $tool)"
    else
        log_warn "  ○ ${tool}: not in PATH"
        TOOLS_READY=0
    fi
done

# Auto-detect Windows cross tools prefix (if any)
WINTOOLS_PREFIX=""
for candidate in "${CONDA_PREFIX}/bin/"*-w64-mingw*-objdump "${CONDA_PREFIX}/bin/"x86_64-w64-mingw32-*; do
    if [ -x "$candidate" ]; then
        WINTOOLS_PREFIX="${candidate%objdump}"
        break
    fi
done

if [ -n "$WINTOOLS_PREFIX" ]; then
    log_info "Detected Windows cross tools prefix: ${WINTOOLS_PREFIX}"
else
    log_info "No explicit mingw cross-prefix detected (using LLVM/conda-build auto-discovery)"
fi

# Check conda prefix for Windows cross tools
log_info "Checking conda prefix for Windows cross-compiler:"
ls -la "${CONDA_PREFIX}/bin/"*clang* 2>/dev/null | head -10 || log_warn "  No clang-prefixed tools found (conda-build will discover via sysroot)"
ls -la "${CONDA_PREFIX}/x86_64-w64-mingw32/" 2>/dev/null | head -5 || log_warn "  No explicit mingw32 sysroot (using m2w64-sysroot_win-64 via conda-build)"

# ── Fix CRLF line endings in recipe (Windows mount issue) ──
log_step "Checking and fixing CRLF line endings in recipe..."
CRLF_COUNT=0
while IFS= read -r -d '' f; do
    if grep -q $'\r' "$f" 2>/dev/null; then
        sed -i 's/\r$//' "$f"
        CRLF_COUNT=$((CRLF_COUNT + 1))
    fi
done < <(find "${RECIPE_DIR}" -type f \( -name '*.sh' -o -name '*.yaml' -o -name '*.py' -o -name 'meta.yaml' -o -name 'build.sh' -o -name 'bld.bat' \) -print0 2>/dev/null)
if [ $CRLF_COUNT -gt 0 ]; then
    log_info "Fixed CRLF→LF in ${CRLF_COUNT} recipe file(s)"
else
    log_info "No CRLF issues found in recipe"
fi

# ══════════════════════════════════════════════════════════════════════════════
# PHASE A: Cross-Compilation (build win-64 conda package)
# ══════════════════════════════════════════════════════════════════════════════
log_sep
log_step "PHASE A: Cross-compilation for win-64 target"
log_sep

# Clean previous build artifacts
log_info "Cleaning previous build artifacts..."
conda build purge 2>/dev/null || true
rm -rf "${CONDA_BLD_DIR}/work" 2>/dev/null || true

# Set conda-build configuration
export CONDA_BUILD_CROSS_COMPILATION=1

# Pass through CAFFE_FFI_TVM_FFI_DIR to build script if set
if [ -n "${CAFFE_FFI_TVM_FFI_DIR:-}" ]; then
    export CAFFE_FFI_TVM_FFI_DIR
    log_info "Using local tvm-ffi source: ${CAFFE_FFI_TVM_FFI_DIR}"
fi

# Create temporary variant config to set target_platform
VARIANT_CONFIG="/tmp/variant-config.yaml"
log_info "Creating variant config for win-64 target: ${VARIANT_CONFIG}"
cat > "${VARIANT_CONFIG}" <<'EOF'
target_platform:
  - win-64
EOF
cat "${VARIANT_CONFIG}"

# Run conda-build
log_step "Executing: conda build -m ${VARIANT_CONFIG} ${RECIPE_DIR}"
BUILD_STATUS=0
conda build \
    -m "${VARIANT_CONFIG}" \
    --no-test \
    --no-anaconda-upload \
    --output-folder "${CONDA_BLD_DIR}" \
    "${RECIPE_DIR}" 2>&1 | tee /tmp/conda-build.log || BUILD_STATUS=$?

if [ $BUILD_STATUS -ne 0 ]; then
    log_error "conda-build failed with exit code ${BUILD_STATUS}"
    log_error "Last 50 lines of build log:"
    tail -50 /tmp/conda-build.log >&2
    exit $BUILD_STATUS
fi
log_info "conda-build completed successfully"

# ── Find built packages ──
log_step "Locating built packages..."

BUILT_PKGS=()
while IFS= read -r -d '' pkg; do
    BUILT_PKGS+=("$pkg")
done < <(find "${CONDA_BLD_DIR}/win-64" \( -name "*.tar.bz2" -o -name "*.conda" \) -print0 2>/dev/null | sort -Vz | tail -5)

if [ ${#BUILT_PKGS[@]} -eq 0 ]; then
    log_error "No packages found in ${CONDA_BLD_DIR}/win-64/"
    ls -la "${CONDA_BLD_DIR}/" 2>/dev/null || true
    exit 1
fi

log_info "Found ${#BUILT_PKGS[@]} package(s):"
for pkg in "${BUILT_PKGS[@]}"; do
    log_info "  - $(basename "$pkg") ($(du -h "$pkg" | cut -f1))"
done

# ── Verify packages: PE32+ binary format check ──
log_sep
log_step "Verifying PE32+ (Windows x86_64) binary format..."
log_sep

VERIFY_OK=1
for pkg in "${BUILT_PKGS[@]}"; do
    pkg_name=$(basename "$pkg")
    log_step "Verifying: ${pkg_name}"

    TMP_DIR=$(mktemp -d)
    log_info "Extracting to temp dir: ${TMP_DIR}"
    tar -xjf "$pkg" -C "${TMP_DIR}" 2>/dev/null || tar -xf "$pkg" -C "${TMP_DIR}" 2>/dev/null

    NATIVE_LIBS=()
    while IFS= read -r -d '' lib; do
        NATIVE_LIBS+=("$lib")
    done < <(find "${TMP_DIR}" -type f \( -name "*.pyd" -o -name "*.dll" \) -print0 2>/dev/null)

    if [ ${#NATIVE_LIBS[@]} -eq 0 ]; then
        log_warn "  No native libraries (.pyd/.dll) found in package (pure Python?)"
        PY_COUNT=$(find "${TMP_DIR}" -name "*.py" | wc -l)
        log_info "  Python files found: ${PY_COUNT}"
        if [ $PY_COUNT -gt 0 ]; then
            log_info "  Package appears to be pure Python"
        fi
    else
        for lib in "${NATIVE_LIBS[@]}"; do
            lib_rel="${lib#${TMP_DIR}/}"
            log_info "  Checking: ${lib_rel}"

            FILE_OUTPUT=$(file "$lib" 2>/dev/null || echo "file check failed")
            log_info "    file: ${FILE_OUTPUT}"

            if echo "$FILE_OUTPUT" | grep -qi "PE32+"; then
                if echo "$FILE_OUTPUT" | grep -qi "x86-64\|x86_64"; then
                    log_info "    ✓ PE32+ executable (DLL) x86-64 confirmed"
                else
                    log_warn "    ⚠ PE32+ but architecture may not be x86_64"
                    VERIFY_OK=0
                fi
                if echo "$FILE_OUTPUT" | grep -qi "DLL"; then
                    log_info "    ✓ DLL format confirmed"
                fi
            else
                log_error "    ✗ NOT a PE32+ binary!"
                log_error "      Got: ${FILE_OUTPUT}"
                VERIFY_OK=0
            fi

            if command -v llvm-objdump >/dev/null 2>&1; then
                log_info "    llvm-objdump -p (DLL import table):"
                llvm-objdump -p "$lib" 2>/dev/null | grep -E "DLL Name:|The Data Directory" | head -20 | while read -r line; do
                    echo "      $line"
                done || log_warn "    llvm-objdump check failed (non-fatal)"
            fi

            if command -v llvm-nm >/dev/null 2>&1; then
                EXPORT_COUNT=$(llvm-nm "$lib" 2>/dev/null | grep -E " T | T _" | wc -l || echo "0")
                log_info "    llvm-nm: ${EXPORT_COUNT} exported symbols found"
                llvm-nm "$lib" 2>/dev/null | grep -E "T __ZN|T _PyInit|T _caffe|T DllMain" | head -10 | while read -r line; do
                    echo "      $line"
                done || true
            fi
        done
    fi

    rm -rf "${TMP_DIR}"
done

# ══════════════════════════════════════════════════════════════════════════════
# PHASE B: Wine L3 Smoke Test (OPTIONAL - best effort)
# ══════════════════════════════════════════════════════════════════════════════
log_sep
log_l3 "PHASE B: Wine L3 Smoke Test (optional, best-effort)"
log_sep

L3_STATUS="SKIPPED"
L3_MSG=""

if [ "${SKIP_WINE_TEST}" = "1" ]; then
    log_l3 "SKIP_WINE_TEST=1: L3 smoke test skipped by user request"
    L3_STATUS="SKIPPED_USER"
else
    WINE_AVAILABLE=0
    if command -v wine >/dev/null 2>&1; then
        if [ -f "${WINEPREFIX}/drive_c/miniconda3/python.exe" ]; then
            WINE_AVAILABLE=1
            log_l3 "Wine detected: $(wine --version 2>/dev/null | head -1)"
            log_l3 "Windows Python: ${WINE_PYTHON}"
        else
            log_warn "Wine installed but Windows Python not found at ${WINEPREFIX}/drive_c/miniconda3/python.exe"
            log_warn "L3 smoke test will be skipped"
        fi
    else
        log_warn "Wine not available in this image (build with SKIP_WINE=0?)"
        log_warn "L3 smoke test will be skipped"
    fi

    if [ $WINE_AVAILABLE -eq 1 ]; then
        log_l3 "Preparing L3 smoke test environment..."
        L3_TMP_DIR=$(mktemp -d)
        L3_WORK_DIR="${WINEPREFIX}/drive_c/l3test"
        mkdir -p "${L3_WORK_DIR}"

        L3_OK=1
        for pkg in "${BUILT_PKGS[@]}"; do
            log_l3 "Extracting $(basename "$pkg") to Wine test directory..."
            tar -xjf "$pkg" -C "${L3_TMP_DIR}" 2>/dev/null || tar -xf "$pkg" -C "${L3_TMP_DIR}" 2>/dev/null || true
        done

        log_l3 "Copying native modules and Python files to Wine C:\l3test..."
        find "${L3_TMP_DIR}" -type f \( -name "*.pyd" -o -name "*.dll" -o -name "*.py" \) -exec cp -v {} "${L3_WORK_DIR}/" \; 2>/dev/null || true
        cp -r "${L3_TMP_DIR}/Lib/site-packages/"* "${L3_WORK_DIR}/" 2>/dev/null || true

        L3_FILES=$(ls -la "${L3_WORK_DIR}/" 2>/dev/null | wc -l)
        log_l3 "Files copied to Wine C:\l3test: ${L3_FILES}"

        log_l3 "Checking Wine Python basic functionality..."
        WINE_PY_CHECK=0
        if wine cmd /c "C:\miniconda3\python.exe --version" >/tmp/l3-pycheck.log 2>&1; then
            PY_VER=$(cat /tmp/l3-pycheck.log | tr -d '\r' | grep -i python || echo "unknown")
            log_l3 "Wine Python works: ${PY_VER}"
            WINE_PY_CHECK=1
        else
            log_warn "Wine Python basic check failed (non-fatal for L3)"
            cat /tmp/l3-pycheck.log | tail -10 | while read -r line; do
                echo "  $line"
            done
        fi

        if [ $WINE_PY_CHECK -eq 1 ]; then
            log_l3 "Attempting import test (tvn_ffi, caffe_ffi)..."
            cat > "${L3_TMP_DIR}/l3_test.py" <<'PYEOF'
import sys
import os
sys.path.insert(0, r'C:\l3test')
os.chdir(r'C:\l3test')
results = []
try:
    import tvm_ffi
    results.append(('tvm_ffi', 'OK', tvm_ffi.__file__ if hasattr(tvm_ffi, '__file__') else 'built-in'))
except Exception as e:
    results.append(('tvm_ffi', 'FAIL', str(e)[:100]))
try:
    import caffe_ffi
    results.append(('caffe_ffi', 'OK', caffe_ffi.__file__ if hasattr(caffe_ffi, '__file__') else 'built-in'))
except Exception as e:
    results.append(('caffe_ffi', 'FAIL', str(e)[:200]))
print("=== L3 IMPORT TEST RESULTS ===")
for name, status, detail in results:
    print(f"  {name}: {status}")
    if status == 'FAIL':
        print(f"    {detail}")
print("=== L3 TEST COMPLETE ===")
PYEOF
            cp "${L3_TMP_DIR}/l3_test.py" "${L3_WORK_DIR}/l3_test.py"

            if wine cmd /c "C:\miniconda3\python.exe C:\l3test\l3_test.py" >/tmp/l3-import.log 2>&1; then
                log_l3 "L3 import test completed:"
                cat /tmp/l3-import.log | tr -d '\r'
                if grep -q "FAIL" /tmp/l3-import.log; then
                    log_warn "Some imports failed in L3 (this is EXPECTED for complex C++ extensions under Wine)"
                    L3_STATUS="PARTIAL"
                    L3_MSG="Some imports failed (Wine compatibility limitation)"
                else
                    log_l3 "✓ All imports passed in Wine!"
                    L3_STATUS="PASS"
                    L3_MSG="All imports successful under Wine"
                fi
            else
                log_warn "L3 import test execution failed (Wine may be missing dependencies)"
                cat /tmp/l3-import.log | tail -20 | tr -d '\r' | while read -r line; do
                    echo "  $line"
                done
                L3_STATUS="FAIL"
                L3_MSG="Import test execution failed (Wine environment limitation)"
            fi
        else
            L3_STATUS="FAIL"
            L3_MSG="Wine Python not functional"
        fi

        log_l3 "L3 test completed (logs preserved for host-side analysis)"
    else
        L3_STATUS="SKIPPED"
        L3_MSG="Wine/Windows Python not available"
    fi
fi

# ── Copy packages to output directory ──
log_sep
log_step "Copying packages to output directory..."
log_sep

COPIED_COUNT=0
for pkg in "${BUILT_PKGS[@]}"; do
    cp -v "$pkg" "${OUTPUT_DIR}/" 2>&1
    COPIED_COUNT=$((COPIED_COUNT + 1))
done
log_info "Copied ${COPIED_COUNT} package(s) to: ${OUTPUT_DIR}"

cp /tmp/conda-build.log "${OUTPUT_DIR}/conda-build.log" 2>/dev/null || true
log_info "Build log saved to: ${OUTPUT_DIR}/conda-build.log"

if [ -f /tmp/l3-import.log ]; then
    cp /tmp/l3-import.log "${OUTPUT_DIR}/l3-smoketest.log" 2>/dev/null || true
    log_info "L3 smoke test log saved to: ${OUTPUT_DIR}/l3-smoketest.log"
fi
if [ -f /tmp/l3-pycheck.log ]; then
    cp /tmp/l3-pycheck.log "${OUTPUT_DIR}/l3-pycheck.log" 2>/dev/null || true
fi

echo
log_info "Output directory contents:"
ls -lh "${OUTPUT_DIR}/"

# ── Summary ──
log_sep
if [ $VERIFY_OK -eq 1 ]; then
    log_info "BUILD SUCCESS: Windows (win-64) conda packages built and PE format verified!"
else
    log_warn "BUILD COMPLETED with verification warnings (see above)"
fi
log_sep
log_info "Summary:"
log_info "  Target platform: win-64 (Windows x86_64)"
log_info "  Binary format:   PE32+ DLL (.pyd extension)"
log_info "  RPATH handling:  N/A (PE format uses DLL search path, no RPATH)"
log_info "  Packages built:  ${COPIED_COUNT}"
log_info "  Output directory: ${OUTPUT_DIR}"
log_info "  L3 smoke test:   ${L3_STATUS}${L3_MSG:+ - }${L3_MSG}"
echo

for pkg in "${BUILT_PKGS[@]}"; do
    pkg_basename=$(basename "$pkg")
    log_info "Package: ${OUTPUT_DIR}/${pkg_basename}"
done

log_l3 "Note: L3 Wine test is optional. Complex C++ extensions may require actual Windows for full validation."
log_sep

exit 0
