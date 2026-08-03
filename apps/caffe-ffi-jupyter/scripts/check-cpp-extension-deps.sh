#!/bin/bash
# =============================================================================
# check-cpp-extension-deps.sh — Comprehensive C++ extension dependency check
#
# Purpose:
#   Diagnose and auto-fix shared library resolution issues for _caffe_ffi.so
#   across Docker, WSL, and local Linux environments.  Verifies that all
#   runtime dependencies (libprotobuf, libopenblas, libstdc++, libgomp, etc.)
#   are findable by the dynamic linker.
#
# Usage:
#   bash check-cpp-extension-deps.sh [--fix] [--smoke] [--verbose]
#
# Exit codes:
#   0  All checks passed (or fixes applied successfully)
#   1  Unrecoverable dependency error (missing .so, wrong protobuf ABI, etc.)
#   2  Usage error
#
# Environment variables:
#   CAFFE_FFI_DIR    Override caffe-ffi source root (auto-detected if unset)
#   CONDA_ENV_NAME   Conda env name (default: caffe-ffi)
#   CAFFE_FFI_PY     Python executable to use (default: python in PATH)
# =============================================================================
set -euo pipefail

# ── Colors ──
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

log_pass()  { echo -e "${GREEN}[PASS]${NC} $*"; }
log_fail()  { echo -e "${RED}[FAIL]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
log_step()  { echo -e "${BOLD}>>> $*${NC}"; }

# ── CLI args ──
AUTO_FIX=0
RUN_SMOKE=0
VERBOSE=0
for arg in "$@"; do
    case "$arg" in
        --fix)     AUTO_FIX=1 ;;
        --smoke)   RUN_SMOKE=1 ;;
        --verbose) VERBOSE=1 ;;
        -h|--help)
            grep '^#' "$0" | grep -v '#!/bin/bash' | sed 's/^# \?//'
            exit 0 ;;
        *) echo "Unknown option: $arg"; exit 2 ;;
    esac
done

ERRORS=0
WARNINGS=0
FIXES_APPLIED=()

# ── Detect environment ──
log_step "Step 1/7: Detecting environment"

IN_DOCKER=0
IN_WSL=0
if [ -f /.dockerenv ] || grep -q docker /proc/1/cgroup 2>/dev/null; then
    IN_DOCKER=1
    log_info "Running inside Docker container"
elif grep -qi microsoft /proc/version 2>/dev/null || grep -qi wsl /proc/version 2>/dev/null; then
    IN_WSL=1
    log_info "Running inside WSL"
else
    log_info "Running on native Linux"
fi

# ── Locate Python ──
PYTHON="${CAFFE_FFI_PY:-python}"
if ! command -v "$PYTHON" &>/dev/null; then
    # Try common conda paths
    for p in /opt/conda/envs/caffe-ffi/bin/python python3 python3.14; do
        if command -v "$p" &>/dev/null; then
            PYTHON="$p"
            break
        fi
    done
fi
if ! command -v "$PYTHON" &>/dev/null; then
    log_fail "Python not found. Set CAFFE_FFI_PY or activate the caffe-ffi conda env."
    exit 1
fi
PYTHON_VERSION=$("$PYTHON" --version 2>&1)
log_info "Python: $PYTHON_VERSION ($(command -v "$PYTHON"))"

# ── Activate conda if available ──
CONDA_ENV_NAME="${CONDA_ENV_NAME:-caffe-ffi}"
if [ -z "${CONDA_PREFIX:-}" ]; then
    for conda_sh in /opt/conda/etc/profile.d/conda.sh \
                    "$HOME/miniconda3/etc/profile.d/conda.sh" \
                    "$HOME/anaconda3/etc/profile.d/conda.sh" \
                    "$HOME/.local/share/miniconda3/etc/profile.d/conda.sh"; do
        if [ -f "$conda_sh" ]; then
            # shellcheck source=/dev/null
            source "$conda_sh" 2>/dev/null && conda activate "$CONDA_ENV_NAME" 2>/dev/null && break
        fi
    done
fi
if [ -n "${CONDA_PREFIX:-}" ]; then
    log_info "Conda env: ${CONDA_PREFIX} ($CONDA_ENV_NAME)"
    CONDA_LIB="${CONDA_PREFIX}/lib"
else
    log_warn "No conda environment detected — may need to set LD_LIBRARY_PATH manually"
    CONDA_LIB=""
fi

# ── Locate caffe-ffi source ──
log_step "Step 2/7: Locating _caffe_ffi.so"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CAFFE_FFI_DIR="${CAFFE_FFI_DIR:-}"

if [ -z "$CAFFE_FFI_DIR" ]; then
    # Search relative to script location (apps/caffe-ffi-jupyter/scripts/ → projects/.../caffe-ffi)
    for candidate in \
        "$SCRIPT_DIR/../../../projects/xuanspace/libs/caffe-ffi" \
        "$SCRIPT_DIR/../../projects/xuanspace/libs/caffe-ffi" \
        "/SpecWeave/projects/xuanspace/libs/caffe-ffi" \
        "/workspace/projects/xuanspace/libs/caffe-ffi" \
        "$PWD"; do
        if [ -f "$candidate/pyproject.toml" ]; then
            CAFFE_FFI_DIR="$candidate"
            break
        fi
    done
fi

if [ ! -d "$CAFFE_FFI_DIR" ]; then
    log_fail "caffe-ffi source directory not found. Set CAFFE_FFI_DIR."
    exit 1
fi
log_info "Source dir: $CAFFE_FFI_DIR"

# Find _caffe_ffi.so: try import first, then build directories
CAFFE_SO=""
if "$PYTHON" -c "import caffe_ffi; import glob, os; \
    sos=glob.glob(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi*.so')); \
    print(sos[0] if sos else '')" 2>/dev/null | grep -q '_caffe_ffi'; then
    CAFFE_SO=$("$PYTHON" -c "import caffe_ffi, glob, os; \
        sos=glob.glob(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi*.so')); \
        print(sos[0])" 2>/dev/null)
    log_info "Found _caffe_ffi.so via Python import: $CAFFE_SO"
else
    # Search build directories
    for build_dir in "$CAFFE_FFI_DIR/build_cpp" "$CAFFE_FFI_DIR/build" \
                     "$CAFFE_FFI_DIR/cmake-build-debug" "$CAFFE_FFI_DIR/cmake-build-release"; do
        if [ -d "$build_dir" ]; then
            found=$(find "$build_dir" -name '_caffe_ffi*.so' -type f 2>/dev/null | head -1)
            if [ -n "$found" ]; then
                CAFFE_SO="$found"
                log_info "Found _caffe_ffi.so in build dir: $CAFFE_SO"
                break
            fi
        fi
    done
fi

if [ -z "$CAFFE_SO" ] || [ ! -f "$CAFFE_SO" ]; then
    log_fail "_caffe_ffi.so not found! The C++ extension may not be compiled yet."
    echo ""
    echo "  Build it inside Docker with:"
    echo "    cd $CAFFE_FFI_DIR && pip install --no-build-isolation -e ."
    echo ""
    echo "  Or run the editable-install entrypoint:"
    echo "    bash /usr/local/bin/editable-install.sh"
    exit 1
fi

# ── Check build directories for additional .so search paths ──
BUILD_LIB_DIRS=()
CAFFE_SO_DIR="$(dirname "$CAFFE_SO")"
BUILD_LIB_DIRS+=("$CAFFE_SO_DIR")
for build_dir in "$CAFFE_FFI_DIR/build_cpp" "$CAFFE_FFI_DIR/build"; do
    if [ -d "$build_dir" ]; then
        # Collect all directories containing .so files under build/
        while IFS= read -r d; do
            BUILD_LIB_DIRS+=("$d")
        done < <(find "$build_dir" -name '*.so*' -type f -exec dirname {} \; 2>/dev/null | sort -u)
    fi
done

# ── Step 3: Check LD_LIBRARY_PATH ──
log_step "Step 3/7: Checking LD_LIBRARY_PATH"

EXISTING_LD="${LD_LIBRARY_PATH:-}"
NEEDED_DIRS=()

# Conda lib dir
if [ -n "$CONDA_LIB" ] && [ -d "$CONDA_LIB" ]; then
    NEEDED_DIRS+=("$CONDA_LIB")
fi
# Build directories with .so files
for d in "${BUILD_LIB_DIRS[@]}"; do
    NEEDED_DIRS+=("$d")
done
# System lib dirs (in case of custom OpenBLAS)
for d in /usr/lib/x86_64-linux-gnu /usr/local/lib; do
    [ -d "$d" ] && NEEDED_DIRS+=("$d")
done

# Remove duplicates
declare -A _seen_dirs
UNIQUE_DIRS=()
for d in "${NEEDED_DIRS[@]}"; do
    if [ -z "${_seen_dirs[$d]:-}" ]; then
        _seen_dirs[$d]=1
        UNIQUE_DIRS+=("$d")
    fi
done

MISSING_FROM_LD=()
for d in "${UNIQUE_DIRS[@]}"; do
    if [[ ":$EXISTING_LD:" != *":$d:"* ]]; then
        MISSING_FROM_LD+=("$d")
    fi
done

if [ ${#MISSING_FROM_LD[@]} -gt 0 ]; then
    log_warn "LD_LIBRARY_PATH missing ${#MISSING_FROM_LD[@]} director(y/ies):"
    for d in "${MISSING_FROM_LD[@]}"; do
        echo "    - $d"
    done
    if [ $AUTO_FIX -eq 1 ]; then
        NEW_LD=""
        for d in "${UNIQUE_DIRS[@]}"; do
            NEW_LD="$d:$NEW_LD"
        done
        NEW_LD="${NEW_LD}${EXISTING_LD}"
        export LD_LIBRARY_PATH="$NEW_LD"
        log_info "Auto-fixed LD_LIBRARY_PATH (length: ${#LD_LIBRARY_PATH})"
        FIXES_APPLIED+=("LD_LIBRARY_PATH updated with ${#MISSING_FROM_LD[@]} directories")
    fi
else
    log_pass "LD_LIBRARY_PATH contains all needed directories"
fi

if [ $VERBOSE -eq 1 ]; then
    echo "  LD_LIBRARY_PATH=${LD_LIBRARY_PATH:-<empty>}"
fi

# ── Step 4: ldd check on _caffe_ffi.so ──
log_step "Step 4/7: Running ldd on _caffe_ffi.so"

LDD_OUTPUT=$(ldd "$CAFFE_SO" 2>&1) || true
if [ $VERBOSE -eq 1 ]; then
    echo "$LDD_OUTPUT" | sed 's/^/  /'
fi

MISSING_LIBS=$(echo "$LDD_OUTPUT" | grep 'not found' || true)
if [ -n "$MISSING_LIBS" ]; then
    log_fail "Unresolved shared library dependencies:"
    echo "$MISSING_LIBS" | sed 's/^/    /'
    ERRORS=$((ERRORS + 1))

    # ── Attempt to locate missing libs ──
    log_info "Searching for missing libraries..."
    while IFS= read -r line; do
        libname=$(echo "$line" | awk '{print $1}')
        found_paths=()
        search_dirs=("${UNIQUE_DIRS[@]}" /lib /usr/lib /lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu)
        if [ -n "$CONDA_LIB" ]; then
            search_dirs+=("$CONDA_LIB")
        fi
        for sd in "${search_dirs[@]}"; do
            if [ -d "$sd" ]; then
                while IFS= read -r p; do
                    found_paths+=("$p")
                done < <(find "$sd" -name "${libname}*" -type f -o -name "${libname}*" -type l 2>/dev/null | head -5)
            fi
        done
        if [ ${#found_paths[@]} -gt 0 ]; then
            libdir=$(dirname "${found_paths[0]}")
            log_info "  Found $libname in: $libdir"
            if [[ ":$LD_LIBRARY_PATH:" != *":$libdir:"* ]]; then
                if [ $AUTO_FIX -eq 1 ]; then
                    export LD_LIBRARY_PATH="$libdir:$LD_LIBRARY_PATH"
                    FIXES_APPLIED+=("Added $libdir to LD_LIBRARY_PATH for $libname")
                    log_info "  -> Added $libdir to LD_LIBRARY_PATH"
                else
                    log_warn "  -> Add $libdir to LD_LIBRARY_PATH: export LD_LIBRARY_PATH=$libdir:\$LD_LIBRARY_PATH"
                fi
            fi
        else
            # Try conda/pip install for known missing libs
            case "$libname" in
                libprotobuf*)
                    log_warn "  $libname not found. Install via: conda install -c conda-forge libprotobuf"
                    if [ $AUTO_FIX -eq 1 ] && [ -n "${CONDA_PREFIX:-}" ]; then
                        log_info "  Attempting: conda install -y -c conda-forge libprotobuf"
                        conda install -y -c conda-forge "libprotobuf>=7.0.0" 2>&1 | tail -5 || true
                        FIXES_APPLIED+=("Attempted conda install libprotobuf")
                    fi
                    ;;
                libopenblas*)
                    log_warn "  $libname not found. Install via: conda install -c conda-forge libopenblas"
                    ;;
                libgomp*)
                    log_warn "  $libname not found. Install via: apt-get install -y libgomp1"
                    if [ $AUTO_FIX -eq 1 ] && [ $IN_DOCKER -eq 1 ] && [ "$(id -u)" -eq 0 ]; then
                        apt-get update -qq && apt-get install -y -qq libgomp1 2>&1 | tail -3 || true
                        FIXES_APPLIED+=("Installed libgomp1 via apt")
                    fi
                    ;;
                libstdc++*)
                    log_warn "  $libname not found. Install via: conda install -c conda-forge cxx-compiler"
                    ;;
                *)
                    log_warn "  $libname not found in standard locations"
                    ;;
            esac
        fi
    done <<< "$MISSING_LIBS"
else
    log_pass "All shared library dependencies resolved"
fi

# ── Step 5: Protobuf ABI version check ──
log_step "Step 5/7: Checking protobuf ABI compatibility"

# Check Python protobuf version matches C++ libprotobuf
if "$PYTHON" -c "import google.protobuf" 2>/dev/null; then
    PY_PROTOBUF_VER=$("$PYTHON" -c "import google.protobuf; print(google.protobuf.__version__)" 2>/dev/null || echo "unknown")
    log_info "Python protobuf: $PY_PROTOBUF_VER"
else
    log_warn "Python protobuf not installed"
    WARNINGS=$((WARNINGS + 1))
fi

# Check what libprotobuf the .so links against
LIBPROTOBUF_LINE=$(echo "$LDD_OUTPUT" | grep -i 'libprotobuf' || true)
if [ -n "$LIBPROTOBUF_LINE" ]; then
    LIBPROTOBUF_PATH=$(echo "$LIBPROTOBUF_LINE" | awk '{print $3}')
    if [ -n "$LIBPROTOBUF_PATH" ] && [ -f "$LIBPROTOBUF_PATH" ]; then
        log_info "C++ libprotobuf: $LIBPROTOBUF_PATH"
        SO_VER=$(basename "$LIBPROTOBUF_PATH" | grep -oP 'libprotobuf\.so\.\K[0-9]+' || echo "unknown")
        log_info "  SONAME version: libprotobuf.so.$SO_VER"
    else
        # libprotobuf is not found (already reported above)
        :
    fi
else
    log_warn "libprotobuf not directly linked (may be loaded dynamically)"
fi

# ── Step 6: Python import test ──
log_step "Step 6/7: Python import test"

IMPORT_OK=0
if "$PYTHON" -c "
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import caffe_ffi
print('caffe_ffi version:', caffe_ffi.__version__)
from caffe_ffi import _ffi_api
print('C++ extension available:', _ffi_api.is_available())
" 2>&1; then
    log_pass "caffe_ffi import succeeded"
    IMPORT_OK=1
else
    IMPORT_ERR=$?
    log_fail "caffe_ffi import failed (exit code: $IMPORT_ERR)"
    ERRORS=$((ERRORS + 1))

    # Try with LD_LIBRARY_PATH fix
    if [ ${#MISSING_FROM_LD[@]} -gt 0 ] && [ $AUTO_FIX -eq 0 ]; then
        echo ""
        log_info "Tip: Re-run with --fix to auto-configure LD_LIBRARY_PATH:"
        echo "    bash $0 --fix"
    fi
fi

# ── Step 7: Smoke test (optional) ──
if [ $RUN_SMOKE -eq 1 ] && [ $IMPORT_OK -eq 1 ]; then
    log_step "Step 7/7: Smoke test (Forward + Backward on a simple net)"

    SMOKE_SCRIPT='
import os, sys, numpy as np
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["CAFFE_FFI_CPP_LOG_LEVEL"] = "4"
from caffe_ffi import Net

proto = """
name: "smoke"
input: "data"
input_dim: 1
input_dim: 1
input_dim: 4
input_dim: 4
layer {
  name: "pool"
  type: "Pooling"
  bottom: "data"
  top: "pool"
  pooling_param { pool: MAX kernel_size: 2 stride: 2 }
}
"""
try:
    net = Net(proto)
    x = np.array([[[[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]]], dtype=np.float32)
    dy = np.array([[[[1,2],[3,4]]]], dtype=np.float32)
    out = net.forward({"data": x})
    net.backward({"pool": dy})
    y = out["pool"]
    dX = net.blob_by_name("data").diff
    assert y.shape == (1,1,2,2), f"Wrong output shape: {y.shape}"
    assert dX.shape == (1,1,4,4), f"Wrong dX shape: {dX.shape}"
    # MAX pool winners: 6,8,14,16
    assert y[0,0,0,0] == 6.0 and y[0,0,1,1] == 16.0
    print(f"Forward OK: y={y.flatten()}")
    print(f"Backward OK: dX nonzero at {np.count_nonzero(dX)} positions")
    print("SMOKE TEST PASSED")
except Exception as e:
    print(f"SMOKE TEST FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)
'
    if "$PYTHON" -c "$SMOKE_SCRIPT" 2>&1; then
        log_pass "Smoke test passed (Forward + Backward working)"
    else
        log_fail "Smoke test failed"
        ERRORS=$((ERRORS + 1))
    fi
else
    log_step "Step 7/7: Smoke test (skipped — pass --smoke to run)"
fi

# ── Summary ──
echo ""
echo "========================================================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}${BOLD}All dependency checks passed!${NC}"
else
    echo -e "${RED}${BOLD}$ERRORS error(s) detected${NC}"
fi
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}$WARNINGS warning(s)${NC}"
fi
if [ ${#FIXES_APPLIED[@]} -gt 0 ]; then
    echo ""
    echo "Fixes applied:"
    for f in "${FIXES_APPLIED[@]}"; do
        echo "  • $f"
    done
fi
echo "========================================================================"

exit $ERRORS
