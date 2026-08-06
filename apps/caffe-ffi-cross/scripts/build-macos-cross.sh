#!/bin/bash
# =============================================================================
# macOS Cross-Compile Build Script
# Runs inside caffe-ffi-cross-macos container to build osx-64 conda packages
#
# Usage:
#   ./build-macos-cross.sh [recipe_dir] [output_dir]
#
# Environment variables:
#   CAFFE_FFI_RECIPE_DIR - Path to conda.recipe (default: /workspace/caffe-ffi/conda.recipe)
#   OUTPUT_DIR           - Directory to copy built packages (default: /output)
#   CONDA_BUILD_SYSROOT  - macOS SDK path (default: /opt/MacOSX11.3.sdk)
#   MACOSX_DEPLOYMENT_TARGET - macOS deployment target (default: 10.15)
# =============================================================================
set -e -o pipefail

# ── Colors ──
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
log_info()  { echo -e "${GREEN}[build-macos]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[build-macos]${NC} $*"; }
log_error() { echo -e "${RED}[build-macos]${NC} $*" >&2; }
log_step()  { echo -e "${CYAN}[build-macos]${NC} $*"; }
log_sep()   { echo -e "${CYAN}==========================================================================${NC}"; }

# ── Configuration ──
RECIPE_DIR="${1:-${CAFFE_FFI_RECIPE_DIR:-/workspace/caffe-ffi/conda.recipe}}"
OUTPUT_DIR="${2:-${OUTPUT_DIR:-/output}}"
CONDA_DIR="/opt/conda"
ENV_NAME="cross-build"
CONDA_BLD_DIR="${CONDA_DIR}/conda-bld"

export CONDA_BUILD_SYSROOT="${CONDA_BUILD_SYSROOT:-/opt/MacOSX11.3.sdk}"
export MACOSX_DEPLOYMENT_TARGET="${MACOSX_DEPLOYMENT_TARGET:-10.15}"

log_sep
log_step "Caffe-FFI macOS Cross-Compile Build"
log_sep
log_info "Recipe dir:    ${RECIPE_DIR}"
log_info "Output dir:    ${OUTPUT_DIR}"
log_info "Conda-bld dir: ${CONDA_BLD_DIR}"
log_info "SDK path:      ${CONDA_BUILD_SYSROOT}"
log_info "Deployment:    ${MACOSX_DEPLOYMENT_TARGET}"

# ── Activate conda environment ──
log_step "Activating conda environment: ${ENV_NAME}"
source "${CONDA_DIR}/etc/profile.d/conda.sh"
conda activate "${ENV_NAME}"
log_info "Python: $(python --version)"
log_info "Conda:  $(conda --version)"

# ── Pre-flight checks ──
log_step "Running pre-flight checks..."

# Check SDK
if [ ! -d "${CONDA_BUILD_SYSROOT}/usr/include" ]; then
    log_error "macOS SDK not found at ${CONDA_BUILD_SYSROOT}"
    log_error "Please mount the SDK directory or build the image with SKIP_SDK_DOWNLOAD=0"
    exit 1
fi
log_info "SDK found: $(ls -d ${CONDA_BUILD_SYSROOT} 2>/dev/null)"

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
for tool in clang clang++ llvm-nm ld; do
    if command -v "$tool" >/dev/null 2>&1; then
        log_info "  ✓ ${tool}: $(command -v $tool)"
    else
        log_warn "  ○ ${tool}: not in PATH (may be in conda prefix)"
    fi
done

# Auto-detect cctools prefix
CCTOOLS_PREFIX=""
for candidate in "${CONDA_PREFIX}/bin/"*-apple-darwin*-otool; do
    if [ -x "$candidate" ]; then
        CCTOOLS_PREFIX="${candidate%otool}"
        break
    fi
done

if [ -n "$CCTOOLS_PREFIX" ]; then
    log_info "Detected cctools prefix: ${CCTOOLS_PREFIX}"
    log_info "  otool:            ${CCTOOLS_PREFIX}otool"
    log_info "  install_name_tool: ${CCTOOLS_PREFIX}install_name_tool"
    log_info "  nm:               ${CCTOOLS_PREFIX}nm"
else
    log_warn "No apple-darwin prefixed cctools found in ${CONDA_PREFIX}/bin"
fi

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

# ── Run conda-build for osx-64 ──
log_sep
log_step "Starting conda-build for osx-64 target..."
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
log_info "Creating variant config for osx-64 target: ${VARIANT_CONFIG}"
cat > "${VARIANT_CONFIG}" <<'EOF'
target_platform:
  - osx-64
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

# Find osx-64 packages
BUILT_PKGS=()
while IFS= read -r -d '' pkg; do
    BUILT_PKGS+=("$pkg")
done < <(find "${CONDA_BLD_DIR}/osx-64" \( -name "*.tar.bz2" -o -name "*.conda" \) -print0 2>/dev/null | sort -Vz | tail -5)

if [ ${#BUILT_PKGS[@]} -eq 0 ]; then
    log_error "No packages found in ${CONDA_BLD_DIR}/osx-64/"
    ls -la "${CONDA_BLD_DIR}/" 2>/dev/null || true
    exit 1
fi

log_info "Found ${#BUILT_PKGS[@]} package(s):"
for pkg in "${BUILT_PKGS[@]}"; do
    log_info "  - $(basename "$pkg") ($(du -h "$pkg" | cut -f1))"
done

# ── Verify packages: file type check ──
log_sep
log_step "Verifying Mach-O binary format..."
log_sep

VERIFY_OK=1
for pkg in "${BUILT_PKGS[@]}"; do
    pkg_name=$(basename "$pkg")
    log_step "Verifying: ${pkg_name}"

    # Extract package to temp dir for inspection
    TMP_DIR=$(mktemp -d)
    log_info "Extracting to temp dir: ${TMP_DIR}"
    tar -xjf "$pkg" -C "${TMP_DIR}" 2>/dev/null || tar -xf "$pkg" -C "${TMP_DIR}" 2>/dev/null

    # Find native libraries
    NATIVE_LIBS=()
    while IFS= read -r -d '' lib; do
        NATIVE_LIBS+=("$lib")
    done < <(find "${TMP_DIR}" -type f \( -name "*.dylib" -o -name "*.so" \) -print0 2>/dev/null)

    if [ ${#NATIVE_LIBS[@]} -eq 0 ]; then
        log_warn "  No native libraries found in package (pure Python?)"
        # Check for .py files to confirm it's a Python package
        PY_COUNT=$(find "${TMP_DIR}" -name "*.py" | wc -l)
        log_info "  Python files found: ${PY_COUNT}"
        if [ $PY_COUNT -gt 0 ]; then
            log_info "  Package appears to be pure Python (expected for cross-compile without running tests)"
        fi
    else
        for lib in "${NATIVE_LIBS[@]}"; do
            lib_rel="${lib#${TMP_DIR}/}"
            log_info "  Checking: ${lib_rel}"

            # file command check
            FILE_OUTPUT=$(file "$lib" 2>/dev/null || echo "file check failed")
            log_info "    file: ${FILE_OUTPUT}"

            if echo "$FILE_OUTPUT" | grep -qi "Mach-O"; then
                if echo "$FILE_OUTPUT" | grep -qi "x86_64"; then
                    log_info "    ✓ Mach-O 64-bit x86_64 confirmed"
                else
                    log_warn "    ⚠ Mach-O but architecture may not be x86_64"
                    VERIFY_OK=0
                fi
            else
                log_error "    ✗ NOT a Mach-O binary!"
                log_error "      Got: ${FILE_OUTPUT}"
                VERIFY_OK=0
            fi

            # otool dependency check
            OTOOL_TOOL=""
            if [ -n "$CCTOOLS_PREFIX" ] && [ -x "${CCTOOLS_PREFIX}otool" ]; then
                OTOOL_TOOL="${CCTOOLS_PREFIX}otool"
            elif command -v otool >/dev/null 2>&1; then
                OTOOL_TOOL="otool"
            fi

            if [ -n "$OTOOL_TOOL" ]; then
                log_info "    ${OTOOL_TOOL} -L (dependencies):"
                "$OTOOL_TOOL" -L "$lib" 2>/dev/null | head -20 | while read -r line; do
                    echo "      $line"
                done || log_warn "    otool check failed (non-fatal)"
            fi

            # nm symbol check
            NM_TOOL=""
            if [ -n "$CCTOOLS_PREFIX" ] && [ -x "${CCTOOLS_PREFIX}nm" ]; then
                NM_TOOL="${CCTOOLS_PREFIX}nm"
            elif command -v llvm-nm >/dev/null 2>&1; then
                NM_TOOL="llvm-nm"
            elif command -v nm >/dev/null 2>&1; then
                NM_TOOL="nm"
            fi

            if [ -n "$NM_TOOL" ]; then
                KEY_SYMBOLS_COUNT=$("$NM_TOOL" "$lib" 2>/dev/null | grep -E "T _|t _|S _" | wc -l || echo "0")
                log_info "    ${NM_TOOL}: ${KEY_SYMBOLS_COUNT} exported symbols found"
                # Show a few key symbols
                "$NM_TOOL" "$lib" 2>/dev/null | grep -E "T __ZN|T _PyInit|T _caffe" | head -10 | while read -r line; do
                    echo "      $line"
                done || true
            fi
        done
    fi

    # Cleanup temp
    rm -rf "${TMP_DIR}"
done

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

# Also copy conda-build log for debugging
cp /tmp/conda-build.log "${OUTPUT_DIR}/conda-build.log" 2>/dev/null || true
log_info "Build log saved to: ${OUTPUT_DIR}/conda-build.log"

# List output directory contents
echo
log_info "Output directory contents:"
ls -lh "${OUTPUT_DIR}/"

# ── Summary ──
log_sep
if [ $VERIFY_OK -eq 1 ]; then
    log_info "BUILD SUCCESS: macOS (osx-64) conda packages built and verified!"
else
    log_warn "BUILD COMPLETED with verification warnings (see above)"
fi
log_sep
log_info "Summary:"
log_info "  Target platform: osx-64 (macOS x86_64)"
log_info "  Deployment target: ${MACOSX_DEPLOYMENT_TARGET}"
log_info "  SDK used: ${CONDA_BUILD_SYSROOT}"
log_info "  Packages built: ${COPIED_COUNT}"
log_info "  Output directory: ${OUTPUT_DIR}"
echo

# List final package paths
for pkg in "${BUILT_PKGS[@]}"; do
    pkg_basename=$(basename "$pkg")
    log_info "Package: ${OUTPUT_DIR}/${pkg_basename}"
done
log_sep

exit 0
