#!/bin/bash
# =============================================================================
# Conv Backward Test Diagnostics & Repair Script
#
# Diagnoses and fixes common failure modes when running caffe-ffi tests
# in Docker. Run this BEFORE running test script if previous run failed.
#
# Usage (from WSL bash):
#   bash apps/docker-images/caffe-ffi-jupyter/scripts/fix-conv-test-env.sh
# =============================================================================
set -euo pipefail

CONTAINER="${CONTAINER:-caffe-ffi-jupyter}"
CAFFE_FFI_DIR="/SpecWeave/projects/xuanspace/libs/caffe-ffi"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
ok()   { echo -e "  ${GREEN}✓${NC} $*"; }
fail() { echo -e "  ${RED}✗${NC} $*"; }
warn() { echo -e "  ${YELLOW}⚠${NC} $*"; }
step() { echo -e "${CYAN}[DIAG]${NC} $*"; }
fix()  { echo -e "  ${GREEN}🔧${NC} $*"; }

# ── 1. Container liveness ──────────────────────────────────────────────────
step "1/7 Checking container liveness..."
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    ok "Container '${CONTAINER}' is running"
else
    fail "Container '${CONTAINER}' is NOT running"
    echo "     Fix: cd apps/docker-images/caffe-ffi-jupyter && docker-compose up -d"
    echo "     Wait ~30s for editable install to complete, then re-run this script."
    exit 1
fi

# ── 2. Conda environment activation ────────────────────────────────────────
step "2/7 Checking conda environment..."
ENV_CHECK=$(docker exec "${CONTAINER}" bash -c "
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi 2>&1 && echo 'OK' || echo 'FAIL'
python --version 2>&1
" 2>&1)
if echo "${ENV_CHECK}" | grep -q "Python 3.14"; then
    ok "conda env 'caffe-ffi' with Python 3.14"
else
    fail "conda env issue. Output: ${ENV_CHECK}"
    echo "     Fix: Rebuild image: cd apps/docker-images/caffe-ffi-jupyter && bash scripts/build.sh --cn"
    exit 1
fi

# ── 3. caffe-ffi import + C++ extension ────────────────────────────────────
step "3/8 Checking caffe-ffi import + C++ extension..."
FFI_CHECK=$(docker exec "${CONTAINER}" bash -c "
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
python -c '
import caffe_ffi
print(\"version:\", caffe_ffi.__version__)
from caffe_ffi import _ffi_api
print(\"cpp_available:\", _ffi_api.is_available())
' 2>&1")
echo "${FFI_CHECK}" | while IFS= read -r line; do echo "     $line"; done

if echo "${FFI_CHECK}" | grep -q "cpp_available: True"; then
    ok "C++ extension available"
else
    fail "C++ extension NOT available!"
    echo ""
    echo "     Root causes:"
    echo "       (a) Editable install failed (CMake/Ninja build error)"
    echo "       (b) Source not mounted at ${CAFFE_FFI_DIR}"
    echo "       (c) CRLF line endings in CMakeLists.txt or .py files"
    echo "       (d) Missing build dependencies (cmake, ninja, protobuf)"
    echo ""
    echo "     Attempting repair (rebuild caffe-ffi from source)..."
    fix "Re-running editable install inside container..."
    docker exec "${CONTAINER}" bash -c "
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
cd ${CAFFE_FFI_DIR}
# Fix CRLF
find . -name '*.py' -o -name 'CMakeLists.txt' -o -name '*.cmake' -o -name '*.sh' -o -name '*.cpp' -o -name '*.hpp' -o -name '*.cc' | head -500 | xargs -r sed -i 's/\r$//' 2>/dev/null || true
# Check build deps
which cmake && cmake --version | head -1 || echo 'cmake NOT found'
which ninja && ninja --version || echo 'ninja NOT found'
# Clean build artifacts for fresh rebuild
rm -rf build/ _skbuild/ dist/ *.egg-info/ 2>/dev/null || true
# Try editable install
pip install --no-build-isolation -e . -v 2>&1 | tail -80
" 2>&1 | tail -90 || true
    
    # Re-check after repair attempt
    FFI_CHECK2=$(docker exec "${CONTAINER}" bash -c "
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
python -c 'from caffe_ffi import _ffi_api; print(\"cpp_available:\", _ffi_api.is_available())' 2>&1")
    if echo "${FFI_CHECK2}" | grep -q "cpp_available: True"; then
        ok "C++ extension now available after repair!"
    else
        fail "Repair failed. Manual intervention needed."
        echo "     Try full rebuild:"
        echo "       cd apps/docker-images/caffe-ffi-jupyter && docker-compose build --no-cache && docker-compose up -d"
    fi
fi

# ── 3.5. Rebuild C++ extension if source changed (force rebuild) ───────────
if [ "${FORCE_REBUILD:-0}" = "1" ] || [ "${REBUILD_CPP:-0}" = "1" ]; then
    step "3.5/8 Force-rebuilding C++ extension (source code changed)..."
    fix "Clean rebuild of caffe-ffi C++ extension (with .so copy fix)..."
    docker exec "${CONTAINER}" bash /SpecWeave/apps/docker-images/caffe-ffi-jupyter/scripts/_rebuild.sh 2>&1 | tail -40
    
    FFI_CHECK3=$(docker exec "${CONTAINER}" bash -c "
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
python -c 'from caffe_ffi import _ffi_api; print(\"cpp_available:\", _ffi_api.is_available())' 2>&1")
    if echo "${FFI_CHECK3}" | grep -q "cpp_available: True"; then
        ok "C++ extension rebuilt successfully!"
    else
        fail "C++ rebuild failed. Check build errors above."
    fi
fi

# ── 4. Python dependency check ─────────────────────────────────────────────
step "4/8 Checking Python dependencies..."
DEPS_CHECK=$(docker exec "${CONTAINER}" bash -c "
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
python -c '
import numpy;        print(\"numpy\", numpy.__version__)
import pytest;       print(\"pytest\", pytest.__version__)
import google.protobuf; print(\"protobuf\", google.protobuf.__version__)
import tvm_ffi;      print(\"tvm_ffi\", tvm_ffi.__version__)
' 2>&1")
MISSING=""
echo "${DEPS_CHECK}" | while IFS= read -r line; do echo "     $line"; done
for pkg in numpy pytest; do
    if ! echo "${DEPS_CHECK}" | grep -q "^${pkg} "; then
        MISSING="${MISSING} ${pkg}"
    fi
done
if [ -n "${MISSING}" ]; then
    fix "Installing missing packages:${MISSING}"
    docker exec "${CONTAINER}" bash -c "
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
pip install ${MISSING} 2>&1 | tail -10
"
fi

# ── 5. Test file exists ────────────────────────────────────────────────────
step "5/8 Checking test files..."
if docker exec "${CONTAINER}" bash -c "[ -f ${CAFFE_FFI_DIR}/tests/python/test_conv_backward.py ]" 2>/dev/null; then
    ok "test_conv_backward.py exists"
else
    fail "test_conv_backward.py NOT found at ${CAFFE_FFI_DIR}/tests/python/"
    echo "     Check volume mount (SpecWeave repo must be mounted to /SpecWeave)"
fi

if docker exec "${CONTAINER}" bash -c "[ -f ${CAFFE_FFI_DIR}/tests/python/_grad_check_utils.py ]" 2>/dev/null; then
    ok "_grad_check_utils.py exists"
else
    fail "_grad_check_utils.py NOT found - run the first task to create it"
fi

if docker exec "${CONTAINER}" bash -c "[ -f ${CAFFE_FFI_DIR}/tests/python/_numpy_conv_reference.py ]" 2>/dev/null; then
    ok "_numpy_conv_reference.py exists"
else
    fail "_numpy_conv_reference.py NOT found"
fi

# ── 6. Check shared library dependencies ───────────────────────────────────
step "6/8 Checking shared library dependencies..."
LIB_CHECK=$(docker exec "${CONTAINER}" bash -c "
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
_SO=\$(python -c 'import caffe_ffi._caffe_ffi, os; print(os.path.join(os.path.dirname(caffe_ffi._caffe_ffi.__file__), \"_caffe_ffi\"))' 2>/dev/null || echo '')
if [ -n \"\$_SO\" ]; then
    # Find actual .so file (may have .cpython-314-x86_64-linux-gnu suffix)
    _SO_REAL=\$(ls \${_SO}*.so 2>/dev/null | head -1)
    if [ -n \"\$_SO_REAL\" ]; then
        echo \"Found: \$_SO_REAL\"
        if ldd \"\$_SO_REAL\" 2>/dev/null | grep -q 'not found'; then
            echo \"UNRESOLVED DEPS:\"
            ldd \"\$_SO_REAL\" | grep 'not found'
        else
            echo \"All shared library deps resolved\"
        fi
    else
        echo \"Could not locate _caffe_ffi .so file\"
    fi
else
    echo \"Could not import caffe_ffi._caffe_ffi\"
fi
" 2>&1)
echo "${LIB_CHECK}" | while IFS= read -r line; do echo "     $line"; done

# ── 7. Quick smoke test (single test) ─────────────────────────────────────
step "7/8 Running smoke test (test_conv_backward_shapes)..."
SMOKE_EXIT=0
docker exec "${CONTAINER}" bash -c "
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
cd ${CAFFE_FFI_DIR}
CAFFE_FFI_PERF_GC_MODE=quick CAFFE_FFI_CPP_LOG_LEVEL=4 \
python -m pytest tests/python/test_conv_backward.py::TestConvBackwardInvariants::test_conv_backward_shapes -v --tb=short 2>&1 | tail -10
" || SMOKE_EXIT=$?

if [ $SMOKE_EXIT -eq 0 ]; then
    ok "Smoke test PASSED - environment is ready!"
else
    fail "Smoke test FAILED (exit ${SMOKE_EXIT})"
    echo "     Check error output above for details."
fi

# ── 8. Performance log directory ──────────────────────────────────────────
step "8/8 Checking performance log directory..."
docker exec "${CONTAINER}" bash -c "
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
mkdir -p ${CAFFE_FFI_DIR}/tests/python/.temp
echo 'Performance log directory ready'
" && ok ".temp/ directory exists for CSV logs"

echo ""
echo "=========================================================================="
echo "Diagnostics complete. Run tests with:"
echo "  REBUILD_CPP=1 bash apps/docker-images/caffe-ffi-jupyter/scripts/run-conv-backward-tests.sh"
echo "=========================================================================="
