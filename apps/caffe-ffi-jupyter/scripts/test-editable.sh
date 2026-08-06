#!/bin/bash
# =============================================================================
# test-editable.sh — 一键验证 tvm-ffi + caffe-ffi editable 安装
# 用法: docker exec caffe-ffi-jupyter bash /path/to/test-editable.sh
#
# 注意：本脚本采用"增量验证"策略，不删除已有 build 目录。
# 在 Docker Desktop Windows 的 NTFS bind mount 上，autotools configure
# 无法从头创建临时文件（confdefs.h 等），因此必须依赖 entrypoint 首次
# 启动时已完成的构建，或做增量编译。
# =============================================================================

source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
pass() { echo -e "${GREEN}  PASS${NC} $*"; }
fail() { echo -e "${RED}  FAIL${NC} $*"; exit 1; }
info() { echo -e "${CYAN}==>${NC} $*"; }
warn() { echo -e "${YELLOW} WARN${NC} $*"; }

SRC_ROOT="${SRC_ROOT:-/SpecWeave}"
TVM_FFI_DIR="$SRC_ROOT/projects/xuanspace/vendor/tvm-ffi"
CAFFE_FFI_DIR="$SRC_ROOT/projects/xuanspace/libs/caffe-ffi"

echo "============================================================"
echo " caffe-ffi Editable Install Verification"
echo "============================================================"
echo ""

# ── Step 0: Fix CRLF (non-destructive, only fixes known build files) ──
info "Step 0: Fixing CRLF line endings..."
fix_crlf_in_dir() {
    local dir="$1"
    [ ! -d "$dir" ] && return 0
    local count=0
    for f in configure config.sub config.guess install-sh missing depcomp compile ltmain.sh; do
        local p="$dir/$f"
        if [ -f "$p" ] && grep -q $'\r' "$p" 2>/dev/null; then
            sed -i 's/\r$//' "$p" 2>/dev/null && count=$((count + 1))
        fi
    done
    if [ -d "$dir/3rdparty" ]; then
        for f in $(find "$dir/3rdparty" -maxdepth 4 -type f \( -name 'configure' -o -name 'config.sub' \
            -o -name 'config.guess' -o -name 'install-sh' -o -name 'ltmain.sh' -o -name '*.sh' \) 2>/dev/null); do
            if grep -q $'\r' "$f" 2>/dev/null; then
                sed -i 's/\r$//' "$f" 2>/dev/null && count=$((count + 1))
            fi
        done
    fi
    [ $count -gt 0 ] && echo "  Fixed CRLF in $count file(s)"
}
fix_crlf_in_dir "$TVM_FFI_DIR"
fix_crlf_in_dir "$CAFFE_FFI_DIR"
pass "CRLF check done"

# ── Step 1: Verify tvm-ffi (try import first, only rebuild if needed) ──
info "Step 1: Checking tvm-ffi..."
TVM_FFI_OK=0
if python -c "
import tvm_ffi, os
assert '/vendor/tvm-ffi' in tvm_ffi.__file__, 'not editable'
from tvm_ffi import _ffi_api
assert _ffi_api is not None, '_ffi_api not available'
" 2>/dev/null; then
    pass "tvm-ffi already OK (editable: $(python -c 'import tvm_ffi; print(tvm_ffi.__version__)' 2>/dev/null))"
    TVM_FFI_OK=1
else
    echo "  tvm-ffi not ready, attempting incremental install..."
    export SETUPTOOLS_SCM_PRETEND_VERSION=0.1.12
    if pip install --no-build-isolation -e "$TVM_FFI_DIR" 2>&1 | tail -5; then
        if python -c "
import tvm_ffi, os
assert '/vendor/tvm-ffi' in tvm_ffi.__file__
from tvm_ffi import _ffi_api
assert _ffi_api is not None
" 2>/dev/null; then
            pass "tvm-ffi installed OK"
            TVM_FFI_OK=1
        fi
    fi
fi
[ $TVM_FFI_OK -eq 0 ] && fail "tvm-ffi is not available (C++ extension failed to load)"

# ── Step 2: Verify caffe-ffi ──
info "Step 2: Checking caffe-ffi..."
CAFFE_FFI_OK=0
if python -c "
import caffe_ffi, os
assert '/libs/caffe-ffi' in caffe_ffi.__file__, 'not editable'
assert caffe_ffi._ffi_api.is_available(), '_ffi_api not available'
" 2>/dev/null; then
    pass "caffe-ffi already OK (editable: $(python -c 'import caffe_ffi; print(caffe_ffi.__version__)' 2>/dev/null))"
    CAFFE_FFI_OK=1
else
    echo "  caffe-ffi not ready, attempting incremental install..."
    TVM_FFI_CMAKE_DIR=$(python -c 'import tvm_ffi, os; print(os.path.dirname(tvm_ffi.__file__))' 2>/dev/null)
    export SETUPTOOLS_SCM_PRETEND_VERSION=0.1.0
    export SKBUILD_CMAKE_ARGS="-DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON;-DCMAKE_BUILD_RPATH_USE_ORIGIN=ON;-DCMAKE_SKIP_BUILD_RPATH=OFF;-DCMAKE_BUILD_WITH_INSTALL_RPATH=ON;-Dcaffe-ffi_DIR=${TVM_FFI_CMAKE_DIR};-DCMAKE_PREFIX_PATH=$CONDA_PREFIX;-DCAFFE_FFI_BUILD_TESTS=OFF"
    if pip install --no-build-isolation -e "$CAFFE_FFI_DIR" 2>&1 | tail -10; then
        if python -c "
import caffe_ffi, os
assert '/libs/caffe-ffi' in caffe_ffi.__file__
assert caffe_ffi._ffi_api.is_available()
" 2>/dev/null; then
            pass "caffe-ffi installed OK"
            CAFFE_FFI_OK=1
        fi
    fi
fi
[ $CAFFE_FFI_OK -eq 0 ] && fail "caffe-ffi is not available (C++ extension failed to load)"

# ── Step 3: Functional test ──
info "Step 3: Functional test (create Net from prototxt)..."
if python << 'PYEOF'
import caffe_ffi, tempfile, os
from caffe_ffi import Net
prototxt = 'name: "TestNet"\nlayer { name: "data" type: "Input" top: "data" input_param { shape { dim: 1 dim: 3 dim: 224 dim: 224 } } }'
with tempfile.NamedTemporaryFile(mode='w', suffix='.prototxt', delete=False) as f:
    f.write(prototxt); tmp = f.name
try:
    net = Net(tmp)
    assert net.name == 'TestNet', f"Expected 'TestNet', got {net.name!r}"
    print(f"  Net created: {net}")
finally:
    os.unlink(tmp)
PYEOF
then
    pass "Functional test passed (Net.name='TestNet')"
else
    fail "Functional test failed"
fi

echo ""
echo "============================================================"
echo -e " ${GREEN}ALL TESTS PASSED${NC} - editable installs work correctly"
echo "============================================================"
