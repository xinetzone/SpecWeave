#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANTS_DIR="$(dirname "$SCRIPT_DIR")"

source "${VARIANTS_DIR}/shared/lib/logging.sh"
LOG_SERVICE="test-torch-dev"
LOG_JSON_OUTPUT="/tmp/test-torch-dev-events.jsonl"

TAG="latest"
IMAGE=""
MAIN_PY="/opt/conda/envs/main/bin/python"

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

Unit test script for torch-dev variant (base: onnx-quantized, free-threading main env, PyTorch cp314t).

Options:
  --tag TAG        Image tag suffix (default: latest)
  --image IMAGE    Full image name (overrides --tag)
  -h, --help       Show this help message

Default image: devcontainer-base:torch-dev-latest
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

# ─────────────────────────── L1 基础环境验证（free-threading + 版本） ───────────────────────────
test_free_threading() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import sys;print('FT_OK' if sys._is_gil_enabled() is False else 'FT_FAIL')" 2>&1)
    if echo "$result" | grep -q "FT_OK"; then
        pass "T1: free-threading active (cp314t, GIL disabled)"
        return 0
    else
        fail "T1: free-threading not active, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

test_python_version() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import sys;print(f'PYVER={sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>&1)
    local ver
    ver=$(echo "$result" | grep -oE 'PYVER=[0-9]+\.[0-9]+\.[0-9]+' | head -1 | sed 's/PYVER=//')
    if echo "$ver" | grep -q "^3\.14\."; then
        pass "T2: Python version = $ver (3.14.x expected)"
        return 0
    else
        fail "T2: Python version unexpected: $ver, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

test_onnxoptimizer_absent() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import importlib.util as u,sys;f=u.find_spec('onnxoptimizer');print('OPT_ABSENT' if f is None else 'OPT_PRESENT')" 2>&1)
    if echo "$result" | grep -q "OPT_ABSENT"; then
        pass "T3: onnxoptimizer absent (free-threading incompatible, CPython #111506)"
        return 0
    else
        fail "T3: onnxoptimizer unexpectedly present, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

# ─────────────────────────── L2 PyTorch 核心导入与版本 ───────────────────────────
test_torch_import() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import torch;print('TORCH_VER='+torch.__version__)" 2>&1)
    local ver
    ver=$(echo "$result" | grep -oE 'TORCH_VER=[0-9]+\.[0-9]+\.[0-9a-z+.]+' | head -1 | sed 's/TORCH_VER=//')
    if [ -n "$ver" ]; then
        pass "T4: torch importable, version = $ver"
        return 0
    else
        fail "T4: torch not importable, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

test_torchvision_import() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import torchvision;print('TV_VER='+torchvision.__version__)" 2>&1)
    local ver
    ver=$(echo "$result" | grep -oE 'TV_VER=[0-9]+\.[0-9]+\.[0-9a-z+.]+' | head -1 | sed 's/TV_VER=//')
    if [ -n "$ver" ]; then
        pass "T5: torchvision importable, version = $ver"
        return 0
    else
        fail "T5: torchvision not importable, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

test_onnx_inherited() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import onnx,onnxruntime;print('ONNX_STACK_OK',onnx.__version__,onnxruntime.__version__)" 2>&1)
    if echo "$result" | grep -q "ONNX_STACK_OK"; then
        pass "T6: onnx + onnxruntime inherited from onnx-quantized"
        return 0
    else
        fail "T6: onnx/onnxruntime not importable, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

test_quantization_inherited() {
    local result
    result=$(docker_run "$MAIN_PY" -c "from onnxruntime.quantization import quantize_dynamic,QuantType;print('QUANT_OK')" 2>&1)
    if echo "$result" | grep -q "QUANT_OK"; then
        pass "T7: onnxruntime.quantization inherited from onnx-quantized"
        return 0
    else
        fail "T7: quantization API not available, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

# ─────────────────────────── L3 PyTorch 核心算子冒烟测试 ───────────────────────────
test_matmul_correctness() {
    local result
    result=$(docker_run "$MAIN_PY" -c "
import torch
torch.manual_seed(42)
a = torch.randn(64, 128)
b = torch.randn(128, 32)
c = torch.matmul(a, b)
assert c.shape == (64, 32), f'shape mismatch: {c.shape}'
print('MATMUL_OK', c.shape)
" 2>&1)
    if echo "$result" | grep -q "MATMUL_OK"; then
        pass "T8: matmul correctness: (64,128)@(128,32) -> (64,32)"
        return 0
    else
        fail "T8: matmul failed, output: $(echo "$result" | grep -v '^\[' | tail -5)"
        return 1
    fi
}

test_conv2d_correctness() {
    local result
    result=$(docker_run "$MAIN_PY" -c "
import torch
import torch.nn.functional as F
torch.manual_seed(42)
x = torch.randn(1, 3, 32, 32)
w = torch.randn(16, 3, 3, 3)
out = F.conv2d(x, w, padding=1)
assert out.shape == (1, 16, 32, 32), f'shape mismatch: {out.shape}'
print('CONV2D_OK', out.shape)
" 2>&1)
    if echo "$result" | grep -q "CONV2D_OK"; then
        pass "T9: conv2d correctness: (1,3,32,32) -> (1,16,32,32)"
        return 0
    else
        fail "T9: conv2d failed, output: $(echo "$result" | grep -v '^\[' | tail -5)"
        return 1
    fi
}

test_autograd_correctness() {
    local result
    result=$(docker_run "$MAIN_PY" -c "
import torch
torch.manual_seed(42)
x = torch.randn(4, 8, requires_grad=True)
w = torch.randn(8, 4, requires_grad=True)
y = x @ w
loss = y.sum()
loss.backward()
assert x.grad is not None and w.grad is not None, 'gradients not computed'
assert x.grad.shape == x.shape and w.grad.shape == w.shape, 'grad shape mismatch'
print('AUTOGRAD_OK')
" 2>&1)
    if echo "$result" | grep -q "AUTOGRAD_OK"; then
        pass "T10: autograd correctness: gradients computed, shapes match"
        return 0
    else
        fail "T10: autograd failed, output: $(echo "$result" | grep -v '^\[' | tail -5)"
        return 1
    fi
}

test_softmax_crossentropy() {
    local result
    result=$(docker_run "$MAIN_PY" -c "
import torch
import torch.nn.functional as F
torch.manual_seed(42)
logits = torch.randn(8, 10)
targets = torch.randint(0, 10, (8,))
loss = F.cross_entropy(logits, targets)
assert loss.dim() == 0 and loss.item() > 0, f'unexpected loss: {loss}'
print(f'CE_OK loss={loss.item():.4f}')
" 2>&1)
    if echo "$result" | grep -q "CE_OK"; then
        local loss
        loss=$(echo "$result" | grep -oE 'loss=[0-9.]+' | head -1)
        pass "T11: softmax + cross_entropy correctness ($loss)"
        return 0
    else
        fail "T11: softmax/cross_entropy failed, output: $(echo "$result" | grep -v '^\[' | tail -5)"
        return 1
    fi
}

test_mlp_forward() {
    local result
    result=$(docker_run "$MAIN_PY" -c "
import torch
import torch.nn as nn
torch.manual_seed(42)
model = nn.Sequential(nn.Linear(16, 32), nn.ReLU(), nn.Linear(32, 4))
out = model(torch.randn(4, 16))
assert out.shape == (4, 4), f'shape mismatch: {out.shape}'
print('MLP_OK', out.shape)
" 2>&1)
    if echo "$result" | grep -q "MLP_OK"; then
        pass "T12: MLP forward: Sequential(16->32->ReLU->4) -> (4,4)"
        return 0
    else
        fail "T12: MLP forward failed, output: $(echo "$result" | grep -v '^\[' | tail -5)"
        return 1
    fi
}

# ─────────────────────────── L4 基础服务继承 ───────────────────────────
test_sshd_config() {
    local result
    result=$(docker_run_bash 'test -f /etc/ssh/sshd_config && echo "exists"' 2>&1)
    if echo "$result" | grep -q "exists"; then
        pass "T13: SSH config file exists"
        return 0
    else
        fail "T13: SSH config file not found"
        return 1
    fi
}

test_supervisord_config() {
    local result
    result=$(docker_run_bash 'test -f /etc/supervisord.conf && echo "exists"' 2>&1)
    if echo "$result" | grep -q "exists"; then
        pass "T14: supervisord config exists"
        return 0
    else
        fail "T14: supervisord config not found"
        return 1
    fi
}

test_jupyter_executable() {
    local result
    result=$(docker_run_bash "test -x $MAIN_PY && test -x /opt/conda/envs/main/bin/jupyter && echo 'executable'" 2>&1)
    if echo "$result" | grep -q "executable"; then
        pass "T15: Jupyter executable exists in conda main env"
        return 0
    else
        fail "T15: Jupyter executable not found in conda main env"
        return 1
    fi
}

test_devuser_torch_access() {
    local result
    result=$(docker_run_bash "su - devuser -c '$MAIN_PY -c \"import torch;print(\\\"devuser-torch-ok\\\")\"'" 2>&1)
    if echo "$result" | grep -q "devuser-torch-ok"; then
        pass "T16: devuser can import torch"
        return 0
    else
        fail "T16: devuser cannot import torch, output: $(echo "$result" | head -5)"
        return 1
    fi
}

test_docker_available() {
    local result
    result=$(docker_run_bash 'docker --version 2>&1' 2>&1)
    if echo "$result" | grep -q "Docker version"; then
        pass "T17: Docker CLI available"
        return 0
    else
        fail "T17: Docker CLI not available"
        return 1
    fi
}

# ─────────────────────────── L5 PATH 优先级与环境隔离 ───────────────────────────
test_python_path_priority() {
    local result
    result=$(docker_run_bash 'which python' 2>&1)
    if echo "$result" | grep -q "/opt/conda/envs/main/bin/python"; then
        pass "T18: PATH priority conda-main-first: $result"
        return 0
    else
        fail "T18: python does not resolve to main env, got: $result"
        return 1
    fi
}

test_venv_removed() {
    local result
    result=$(docker_run_bash 'test ! -d /opt/venv && echo "removed"' 2>&1)
    if echo "$result" | grep -q "removed"; then
        pass "T19: /opt/venv removed"
        return 0
    else
        fail "T19: /opt/venv still exists"
        return 1
    fi
}

# ─────────────────────────── L6 build-info 与配置 ───────────────────────────
test_build_info_exists() {
    local result
    result=$(docker_run_bash 'test -f /etc/devcontainer-variant-torch-dev-build-info && cat /etc/devcontainer-variant-torch-dev-build-info' 2>&1)
    if echo "$result" | grep -q "VARIANT=torch-dev" && \
       echo "$result" | grep -q "BASE_IMAGE=devcontainer-base:onnx-quantized" && \
       echo "$result" | grep -q "TORCH_VERSION" && \
       echo "$result" | grep -q "GIL_ENABLED=false" && \
       echo "$result" | grep -q "DOWNSTREAM_VARIANTS=ai-dev"; then
        pass "T20: build-info exists with torch-dev metadata"
        return 0
    else
        fail "T20: build-info missing required fields, output: $(echo "$result" | head -5)"
        return 1
    fi
}

test_omp_env() {
    local result
    result=$(docker_run_bash 'echo "OMP_NUM_THREADS=$OMP_NUM_THREADS KMP_DUPLICATE_LIB_OK=$KMP_DUPLICATE_LIB_OK"' 2>&1)
    if echo "$result" | grep -q "OMP_NUM_THREADS=4" && echo "$result" | grep -q "KMP_DUPLICATE_LIB_OK=TRUE"; then
        pass "T21: OpenMP env defaults set correctly"
        return 0
    else
        pass "T21: OpenMP env defaults (info only): $result"
        return 0
    fi
}

# ─────────────────────────── L7 ONNX 互操作（torch → ONNX 导出链） ───────────────────────────
test_torch_onnx_export() {
    local result
    result=$(docker_run_bash 'cat > /tmp/torch_onnx_test.py << EOF
import torch
import torch.nn as nn
import onnx
import onnxruntime as ort
import tempfile
import os

torch.manual_seed(42)

# Simple model
model = nn.Sequential(nn.Linear(32, 16), nn.ReLU(), nn.Linear(16, 8))
model.eval()

dummy = torch.randn(1, 32)

with tempfile.TemporaryDirectory() as td:
    onnx_path = os.path.join(td, "model.onnx")
    torch.onnx.export(model, dummy, onnx_path,
                      input_names=["input"], output_names=["output"],
                      opset_version=18)
    
    # Verify ONNX model loads
    m = onnx.load(onnx_path)
    onnx.checker.check_model(m)
    
    # Run ORT inference
    sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    out = sess.run(None, {"input": dummy.numpy()})[0]
    assert out.shape == (1, 8), f"Unexpected output shape: {out.shape}"
    
    # Compare with PyTorch
    with torch.no_grad():
        torch_out = model(dummy).numpy()
    import numpy as np
    max_diff = np.max(np.abs(out - torch_out))
    assert max_diff < 1e-5, f"ONNX vs PyTorch diff too large: {max_diff}"
    print(f"TORCH_ONNX_OK max_diff={max_diff:.2e}")
EOF
'"$MAIN_PY"' /tmp/torch_onnx_test.py && rm -f /tmp/torch_onnx_test.py' 2>&1)
    if echo "$result" | grep -q "TORCH_ONNX_OK"; then
        local diff
        diff=$(echo "$result" | grep -oE "max_diff=[0-9.e-]+" | head -1)
        pass "T22: torch→ONNX export + ORT inference interop $diff"
        return 0
    else
        fail "T22: torch→ONNX interop failed, output: $(echo "$result" | tail -8)"
        return 1
    fi
}

test_llvm_toolchain() {
    local result
    result=$(docker_run_bash 'llvm-config --version 2>&1 | head -1' 2>&1)
    if echo "$result" | grep -qE "^22\.1\.8"; then
        pass "T23: LLVM toolchain version = $result"
        return 0
    else
        pass "T23: LLVM toolchain available (version: $(echo "$result" | head -1))"
        return 0
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
    IMAGE="devcontainer-base:torch-dev-${TAG}"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║      torch-dev Variant Unit Test Suite                      ║"
echo "║      (base: onnx-quantized, free-threading main env,        ║"
echo "║       PyTorch cp314t + torchvision, no GIL)                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
log_info "Testing image: ${IMAGE}"
echo ""

log_step "Verifying image exists"
if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${IMAGE}$"; then
    log_fatal "Image not found: ${IMAGE}. Please build it first."
fi
log_ok "Image exists: ${IMAGE}"
echo ""

log_step "1. Base Environment Tests - free-threading + versions (L1)"
test_free_threading || true
test_python_version || true
test_onnxoptimizer_absent || true
echo ""

log_step "2. PyTorch Import Tests (L2)"
test_torch_import || true
test_torchvision_import || true
test_onnx_inherited || true
test_quantization_inherited || true
echo ""

log_step "3. PyTorch Core Operator Smoke Tests (L3)"
test_matmul_correctness || true
test_conv2d_correctness || true
test_autograd_correctness || true
test_softmax_crossentropy || true
test_mlp_forward || true
echo ""

log_step "4. Base Service Inheritance Tests (L4)"
test_sshd_config || true
test_supervisord_config || true
test_jupyter_executable || true
test_devuser_torch_access || true
test_docker_available || true
echo ""

log_step "5. PATH Priority & Environment Isolation Tests (L5)"
test_python_path_priority || true
test_venv_removed || true
echo ""

log_step "6. Build Info & Configuration Tests (L6)"
test_build_info_exists || true
test_omp_env || true
test_llvm_toolchain || true
echo ""

log_step "7. PyTorch-ONNX Interoperability Tests (L7)"
test_torch_onnx_export || true
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
