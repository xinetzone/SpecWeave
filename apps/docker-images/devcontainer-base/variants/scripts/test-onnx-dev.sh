#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANTS_DIR="$(dirname "$SCRIPT_DIR")"

source "${VARIANTS_DIR}/shared/lib/logging.sh"
LOG_SERVICE="test-onnx-dev"
LOG_JSON_OUTPUT="/tmp/test-onnx-dev-events.jsonl"

TAG="latest"
IMAGE=""

TEST_PASS=0
TEST_FAIL=0
TEST_TOTAL=0

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Unit test script for onnx-dev variant (pure ONNX ecosystem, no PyTorch).
All Python checks use the conda main environment
(/opt/conda/envs/main/bin/python, Python 3.14t free-threading).

Options:
  --tag TAG        Image tag suffix (default: latest)
  --image IMAGE    Full image name (overrides --tag)
  -h, --help       Show this help message

Default image: devcontainer-base:onnx-dev-latest
EOF
}

pass() {
    local msg="$1"
    echo -e "  ${GREEN}PASS${NC}: $msg"
    TEST_PASS=$((TEST_PASS + 1))
    TEST_TOTAL=$((TEST_TOTAL + 1))
}

fail() {
    local msg="$1"
    echo -e "  ${RED}FAIL${NC}: $msg"
    TEST_FAIL=$((TEST_FAIL + 1))
    TEST_TOTAL=$((TEST_TOTAL + 1))
}

skip() {
    local msg="$1"
    echo -e "  ${YELLOW}SKIP${NC}: $msg"
}

docker_run() {
    docker run --rm "$IMAGE" "$@" 2>&1
}

docker_run_bash() {
    docker run --rm "$IMAGE" bash -c "$1" 2>&1
}

# main 环境 python 绝对路径（与变体 PATH 优先级一致）
MAIN_PY="/opt/conda/envs/main/bin/python"

# ─────────────────────────── L1 ONNX 生态版本 ───────────────────────────
test_onnx_version() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import onnx;print('VER_ONNX='+onnx.__version__)" 2>&1)
    local ver
    ver=$(echo "$result" | grep -oE 'VER_ONNX=[0-9]+\.[0-9]+\.[0-9a-z+.]+' | head -1 | sed 's/VER_ONNX=//')
    if [ -n "$ver" ]; then
        pass "T1: onnx version = $ver"
        return 0
    else
        fail "T1: onnx not importable, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

test_onnxruntime_version() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import onnxruntime;print('VER_ORT='+onnxruntime.__version__)" 2>&1)
    local ver
    ver=$(echo "$result" | grep -oE 'VER_ORT=[0-9]+\.[0-9]+\.[0-9a-z+.]+' | head -1 | sed 's/VER_ORT=//')
    if [ -n "$ver" ]; then
        pass "T2: onnxruntime version = $ver"
        return 0
    else
        fail "T2: onnxruntime not importable, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

test_onnxsim_version() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import onnxsim;print('VER_SIM='+getattr(onnxsim,'__version__','installed'))" 2>&1)
    if echo "$result" | grep -q "VER_SIM="; then
        pass "T3: onnx-simplifier importable ($(echo "$result" | grep -oE 'VER_SIM=.*' | sed 's/VER_SIM=//'))"
        return 0
    else
        fail "T3: onnxsim not importable, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

test_onnxoptimizer_version() {
    # NEGATIVE check: onnxoptimizer is intentionally EXCLUDED from onnx-dev.
    # Its sdist declares py_limited_api='cp312', fundamentally incompatible with
    # free-threading builds (Py_LIMITED_API x Py_GIL_DISABLED, CPython #111506).
    # This guard fails if any future dependency silently pulls it back in.
    local result
    result=$(docker_run "$MAIN_PY" -c "import importlib.util as u; import sys; f=u.find_spec('onnxoptimizer'); print('ABSENT' if f is None else 'PRESENT'); sys.exit(0 if f is None else 1)" 2>&1)
    if echo "$result" | grep -q "ABSENT"; then
        pass "T4: onnxoptimizer is ABSENT (by design: free-threading incompatible, negative check)"
        return 0
    else
        fail "T4: onnxoptimizer unexpectedly PRESENT (free-threading incompatible!), output: $(echo "$result" | head -3)"
        return 1
    fi
}

test_onnxscript_version() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import onnxscript;print('VER_SCR='+getattr(onnxscript,'__version__','installed'))" 2>&1)
    if echo "$result" | grep -q "VER_SCR="; then
        pass "T5: onnxscript importable ($(echo "$result" | grep -oE 'VER_SCR=.*' | sed 's/VER_SCR=//'))"
        return 0
    else
        fail "T5: onnxscript not importable, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

# ─────────────────────────── L2 纯 ONNX 冒烟（无 torch） ───────────────────────────
test_pure_onnx_smoke() {
    local result
    result=$(docker_run_bash "cat > /tmp/smoke.py << 'EOF'
import numpy as np
import onnx
from onnx import helper, TensorProto
import onnxruntime as ort

a = helper.make_tensor_value_info('a', TensorProto.FLOAT, [2])
b = helper.make_tensor_value_info('b', TensorProto.FLOAT, [2])
c = helper.make_tensor_value_info('c', TensorProto.FLOAT, [2])
node = helper.make_node('Add', ['a', 'b'], ['c'])
graph = helper.make_graph([node], 'add_graph', [a, b], [c])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid('', 13)])
onnx.checker.check_model(model)
onnx.save(model, '/tmp/add.onnx')
sess = ort.InferenceSession('/tmp/add.onnx', providers=['CPUExecutionProvider'])
out = sess.run(None, {
    'a': np.array([1.0, 2.0], dtype=np.float32),
    'b': np.array([3.0, 4.0], dtype=np.float32),
})[0]
assert np.allclose(out, [4.0, 6.0]), 'inference mismatch: %s' % out
print('pure-onnx-ok')
EOF
$MAIN_PY /tmp/smoke.py && rm -f /tmp/smoke.py /tmp/add.onnx" 2>&1)
    if echo "$result" | grep -q "pure-onnx-ok"; then
        pass "T6: pure-ONNX smoke (onnx.helper build -> checker -> ORT CPU inference)"
        return 0
    else
        fail "T6: pure-ONNX smoke failed, output: $(echo "$result" | head -5)"
        return 1
    fi
}

test_onnxsim_simplify_smoke() {
    local result
    result=$(docker_run_bash "cat > /tmp/sim.py << 'EOF'
import numpy as np
import onnx
from onnx import helper, TensorProto
import onnxsim

a = helper.make_tensor_value_info('a', TensorProto.FLOAT, [2])
c = helper.make_tensor_value_info('c', TensorProto.FLOAT, [2])
id_node = helper.make_node('Identity', ['a'], ['c'])
graph = helper.make_graph([id_node], 'id_graph', [a], [c])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid('', 13)])
model_simp, ok = onnxsim.simplify(model)
assert ok, 'simplify returned check=False'
onnx.checker.check_model(model_simp)
print('onnxsim-ok')
EOF
$MAIN_PY /tmp/sim.py && rm -f /tmp/sim.py" 2>&1)
    if echo "$result" | grep -q "onnxsim-ok"; then
        pass "T7: onnxsim.simplify smoke (Identity graph simplified + re-checked)"
        return 0
    else
        fail "T7: onnxsim simplify failed, output: $(echo "$result" | head -5)"
        return 1
    fi
}

# ─────────────────────────── L3 深度组件与负向验证 ───────────────────────────
test_torch_absent() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import importlib.util as u; import sys; f=u.find_spec('torch'); print('ABSENT' if f is None else 'PRESENT'); sys.exit(0 if f is None else 1)" 2>&1)
    if echo "$result" | grep -q "ABSENT"; then
        pass "T8: torch is ABSENT (by design, negative check)"
        return 0
    else
        fail "T8: torch unexpectedly PRESENT, output: $(echo "$result" | head -3)"
        return 1
    fi
}

test_torchvision_absent() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import importlib.util as u; import sys; f=u.find_spec('torchvision'); print('ABSENT' if f is None else 'PRESENT'); sys.exit(0 if f is None else 1)" 2>&1)
    if echo "$result" | grep -q "ABSENT"; then
        pass "T9: torchvision is ABSENT (by design, negative check)"
        return 0
    else
        fail "T9: torchvision unexpectedly PRESENT, output: $(echo "$result" | head -3)"
        return 1
    fi
}

test_free_threading() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import sys; print('GIL='+str(sys._is_gil_enabled())); sys.exit(0 if sys._is_gil_enabled() is False else 1)" 2>&1)
    if echo "$result" | grep -q "GIL=False"; then
        pass "T10: python is free-threading (GIL disabled) in main env"
        return 0
    else
        fail "T10: GIL not disabled, output: $(echo "$result" | head -3)"
        return 1
    fi
}

test_ort_providers() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import onnxruntime as ort;print('providers',ort.get_available_providers())" 2>&1)
    if echo "$result" | grep -q "CPUExecutionProvider"; then
        pass "T11: onnxruntime providers include CPUExecutionProvider"
        return 0
    else
        fail "T11: onnxruntime CPU provider not found, output: $(echo "$result" | head -3)"
        return 1
    fi
}

# ─────────────────────────── L4 基础服务继承 ───────────────────────────
test_sshd_config() {
    local result
    result=$(docker_run_bash 'test -f /etc/ssh/sshd_config && echo "exists"' 2>&1)
    if echo "$result" | grep -q "exists"; then
        pass "T12: SSH config file exists (/etc/ssh/sshd_config)"
        return 0
    else
        fail "T12: SSH config file not found"
        return 1
    fi
}

test_supervisord_config() {
    local result
    result=$(docker_run_bash 'test -f /etc/supervisord.conf && echo "exists"' 2>&1)
    if echo "$result" | grep -q "exists"; then
        pass "T13: supervisord config exists (/etc/supervisord.conf)"
        return 0
    else
        fail "T13: supervisord config not found"
        return 1
    fi
}

test_jupyter_executable() {
    local result
    result=$(docker_run_bash "test -x /opt/conda/envs/main/bin/jupyter && echo 'executable'" 2>&1)
    if echo "$result" | grep -q "executable"; then
        pass "T14: Jupyter executable exists (/opt/conda/envs/main/bin/jupyter)"
        return 0
    else
        fail "T14: Jupyter executable not found at /opt/conda/envs/main/bin/jupyter"
        return 1
    fi
}

test_docker_cli() {
    local result
    result=$(docker_run docker --version 2>&1)
    if echo "$result" | grep -qi "docker version"; then
        pass "T15: Docker CLI available"
        return 0
    else
        fail "T15: Docker CLI not available, got: $result"
        return 1
    fi
}

test_devuser_exists() {
    local result
    result=$(docker_run id devuser 2>&1)
    if echo "$result" | grep -q "uid="; then
        pass "T16: devuser exists"
        return 0
    else
        fail "T16: devuser does not exist, got: $result"
        return 1
    fi
}

test_conda_version() {
    local result
    result=$(docker_run /opt/conda/bin/conda --version 2>&1)
    if echo "$result" | grep -q "conda"; then
        pass "T17: conda --version available: $result"
        return 0
    else
        fail "T17: conda not available, got: $result"
        return 1
    fi
}

# ─────────────────────────── L5 PATH 优先级与 LLVM 继承 ───────────────────────────
test_python_path_priority() {
    local result
    result=$(docker_run_bash 'which python' 2>&1)
    if echo "$result" | grep -q "/opt/conda/envs/main/bin/python"; then
        pass "T18: python points to conda main env: $result"
        return 0
    else
        fail "T18: python does not point to /opt/conda/envs/main/bin/python, got: $result"
        return 1
    fi
}

test_main_env_python_version() {
    local result
    result=$(docker_run "$MAIN_PY" --version 2>&1)
    if echo "$result" | grep -q "Python 3.14"; then
        pass "T19: main env python version: $(echo "$result" | head -1)"
        return 0
    else
        fail "T19: unexpected python version: $result"
        return 1
    fi
}

test_llvm_toolchain_inherited() {
    local result
    result=$(docker_run bash -lc 'llvm-config --version' 2>&1)
    if echo "$result" | grep -qE "^[0-9]+\.[0-9]+"; then
        pass "T20: LLVM toolchain inherited from conda-llvm (llvm-config $result)"
        return 0
    else
        fail "T20: llvm-config not available, got: $result"
        return 1
    fi
}

# ─────────────────────────── L6 build-info 与配置 ───────────────────────────
test_build_info_exists() {
    local result
    result=$(docker_run_bash 'test -f /etc/devcontainer-variant-onnx-dev-build-info && cat /etc/devcontainer-variant-onnx-dev-build-info' 2>&1)
    if echo "$result" | grep -q "VARIANT=onnx-dev" && echo "$result" | grep -q "ONNX_VERSION_ACTUAL" && echo "$result" | grep -q "PACKAGES_EXCLUDED=torch"; then
        pass "T21: build-info exists with onnx versions + torch exclusion record"
        return 0
    else
        fail "T21: build-info missing required fields, output: $(echo "$result" | head -3)"
        return 1
    fi
}

test_init_script_valid() {
    local result
    result=$(docker_run_bash 'bash -n /etc/profile.d/onnx-dev-init.sh && echo "syntax-ok"' 2>&1)
    if echo "$result" | grep -q "syntax-ok"; then
        pass "T22: onnx-dev-init.sh exists and bash syntax valid"
        return 0
    else
        fail "T22: onnx-dev-init.sh invalid, output: $(echo "$result" | head -3)"
        return 1
    fi
}

test_condarc_exists() {
    local result
    result=$(docker_run_bash 'test -f /opt/conda/.condarc && cat /opt/conda/.condarc | head -5' 2>&1)
    if [ -n "$result" ] && ! echo "$result" | grep -q "No such file"; then
        pass "T23: .condarc configuration exists"
        return 0
    else
        fail "T23: .condarc not found or not readable"
        return 1
    fi
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --tag)
            if [ -z "$2" ]; then
                log_error "--tag requires a TAG argument"
                usage
                exit 1
            fi
            TAG="$2"
            shift 2
            ;;
        --image)
            if [ -z "$2" ]; then
                log_error "--image requires an IMAGE argument"
                usage
                exit 1
            fi
            IMAGE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

if [ -z "$IMAGE" ]; then
    IMAGE="devcontainer-base:onnx-dev-${TAG}"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       ONNX-Dev Variant Unit Test Suite (no PyTorch)         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
log_info "Testing image: ${IMAGE}"
log_info "Python env:   conda main (/opt/conda/envs/main, free-threading)"
echo ""

log_step "Verifying image exists"
if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${IMAGE}$"; then
    log_fatal "Image not found: ${IMAGE}. Please build it first."
fi
log_ok "Image exists: ${IMAGE}"
echo ""

log_step "1. ONNX Ecosystem Version Tests (L1)"
test_onnx_version || true
test_onnxruntime_version || true
test_onnxsim_version || true
test_onnxoptimizer_version || true
test_onnxscript_version || true
echo ""

log_step "2. Pure-ONNX Smoke Tests (L2, torch-free)"
test_pure_onnx_smoke || true
test_onnxsim_simplify_smoke || true
echo ""

log_step "3. Negative Checks & Deep Component Tests (L3)"
test_torch_absent || true
test_torchvision_absent || true
test_free_threading || true
test_ort_providers || true
echo ""

log_step "4. Base Service Inheritance Tests (L4)"
test_sshd_config || true
test_supervisord_config || true
test_jupyter_executable || true
test_docker_cli || true
test_devuser_exists || true
test_conda_version || true
echo ""

log_step "5. PATH Priority & LLVM Inheritance Tests (L5)"
test_python_path_priority || true
test_main_env_python_version || true
test_llvm_toolchain_inherited || true
echo ""

log_step "6. Build Info & Configuration Tests (L6)"
test_build_info_exists || true
test_init_script_valid || true
test_condarc_exists || true
echo ""

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    TEST SUMMARY                              ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  %-20s %3d tests                           ║\n" "TOTAL:" "$TEST_TOTAL"
printf "║  %-20s %3d tests                           ║\n" "PASSED:" "$TEST_PASS"
printf "║  %-20s %3d tests                           ║\n" "FAILED:" "$TEST_FAIL"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

if [ $TEST_FAIL -gt 0 ]; then
    echo -e "${RED}${TEST_FAIL} test(s) failed!${NC}"
    exit 1
else
    echo -e "${GREEN}All ${TEST_PASS} tests passed!${NC}"
    exit 0
fi
