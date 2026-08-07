#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANTS_DIR="$(dirname "$SCRIPT_DIR")"

source "${VARIANTS_DIR}/shared/lib/logging.sh"
LOG_SERVICE="test-onnx-pytorch"
LOG_JSON_OUTPUT="/tmp/test-onnx-pytorch-events.jsonl"

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

Unit test script for onnx-pytorch variant.

Options:
  --tag TAG        Image tag suffix (default: latest)
  --image IMAGE    Full image name (overrides --tag)
  -h, --help       Show this help message

Default image: devcontainer-base:onnx-pytorch-latest
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

# ─────────────────────────── L1 基础工具链版本 ───────────────────────────
test_torch_version() {
    local result
    result=$(docker_run /opt/conda/bin/python -c "import torch;print(torch.__version__)" 2>&1)
    local ver
    # 容器 entrypoint 会输出服务诊断日志，版本行混在其中，需从完整输出精确提取版本。
    ver=$(echo "$result" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+[a-z0-9+.]*' | head -1)
    if [ -n "$ver" ]; then
        pass "T1: torch version = $ver"
        return 0
    else
        fail "T1: torch not importable, output: $(echo "$result" | head -1)"
        return 1
    fi
}

test_torchvision_version() {
    local result
    result=$(docker_run /opt/conda/bin/python -c "import torchvision;print(torchvision.__version__)" 2>&1)
    local ver
    ver=$(echo "$result" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+[a-z0-9+.]*' | head -1)
    if [ -n "$ver" ]; then
        pass "T2: torchvision version = $ver"
        return 0
    else
        fail "T2: torchvision not importable, output: $(echo "$result" | head -1)"
        return 1
    fi
}

test_onnx_version() {
    local result
    result=$(docker_run /opt/conda/bin/python -c "import onnx;print(onnx.__version__)" 2>&1)
    local ver
    ver=$(echo "$result" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    if [ -n "$ver" ]; then
        pass "T3: onnx version = $ver"
        return 0
    else
        fail "T3: onnx not importable, output: $(echo "$result" | head -1)"
        return 1
    fi
}

test_onnxruntime_version() {
    local result
    result=$(docker_run /opt/conda/bin/python -c "import onnxruntime;print(onnxruntime.__version__)" 2>&1)
    local ver
    ver=$(echo "$result" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    if [ -n "$ver" ]; then
        pass "T4: onnxruntime version = $ver"
        return 0
    else
        fail "T4: onnxruntime not importable, output: $(echo "$result" | head -1)"
        return 1
    fi
}

# ─────────────────────────── L2 Hello World 冒烟 ───────────────────────────
test_torch_tensor_smoke() {
    local result
    result=$(docker_run /opt/conda/bin/python -c "import torch;a=torch.tensor([[1.,2.],[3.,4.]]);c=(a+a)*2;assert torch.allclose(c,torch.tensor([[4.,8.],[12.,16.]])),'mismatch';print('torch-op-ok',c.tolist())" 2>&1)
    if echo "$result" | grep -q "torch-op-ok"; then
        pass "T5: torch tensor operation smoke test (a+a)*2"
        return 0
    else
        fail "T5: torch tensor op failed, output: $(echo "$result" | head -3)"
        return 1
    fi
}

test_onnx_export_inference_smoke() {
    local result
    result=$(docker_run_bash 'cat > /tmp/smoke.py << EOF
import torch, onnxruntime, numpy as np
class Net(torch.nn.Module):
    def forward(self, x):
        return x * 2 + 1
torch.onnx.export(Net(), torch.randn(1,3), "/tmp/smoke.onnx", opset_version=13)
sess = onnxruntime.InferenceSession("/tmp/smoke.onnx", providers=["CPUExecutionProvider"])
inp = np.random.randn(1,3).astype("float32")
out = sess.run(None, {"input": inp})[0]
assert np.allclose(out, inp*2+1, atol=1e-5), "inference mismatch"
print("onnx-export-infer-ok")
EOF
/opt/conda/bin/python /tmp/smoke.py && rm -f /tmp/smoke.py /tmp/smoke.onnx' 2>&1)
    if echo "$result" | grep -q "onnx-export-infer-ok"; then
        pass "T6: torch ONNX export + onnxruntime CPU inference smoke"
        return 0
    else
        fail "T6: ONNX export/inference failed, output: $(echo "$result" | head -5)"
        return 1
    fi
}

# ─────────────────────────── L3 深度组件 ───────────────────────────
test_torchvision_model_load() {
    local result
    result=$(docker_run /opt/conda/bin/python -c "import torchvision.models as m;net=m.resnet18(pretrained=False);print('torchvision-model-ok')" 2>&1)
    if echo "$result" | grep -q "torchvision-model-ok"; then
        pass "T7: torchvision model loadable (resnet18)"
        return 0
    else
        fail "T7: torchvision model load failed, output: $(echo "$result" | head -3)"
        return 1
    fi
}

test_onnxruntime_session() {
    local result
    result=$(docker_run /opt/conda/bin/python -c "import onnxruntime as ort;print('providers',ort.get_available_providers())" 2>&1)
    if echo "$result" | grep -q "CPUExecutionProvider"; then
        pass "T8: onnxruntime InferenceSession providers include CPUExecutionProvider"
        return 0
    else
        fail "T8: onnxruntime CPU provider not found, output: $(echo "$result" | head -3)"
        return 1
    fi
}

test_cuda_not_available() {
    local result
    result=$(docker_run /opt/conda/bin/python -c "import torch;print(torch.cuda.is_available())" 2>&1)
    if echo "$result" | grep -q "False"; then
        pass "T9: torch.cuda.is_available() == False (CPU build)"
        return 0
    else
        fail "T9: torch.cuda.is_available() expected False, got: $(echo "$result" | head -1)"
        return 1
    fi
}

# ─────────────────────────── L4 基础服务继承 ───────────────────────────
test_sshd_config() {
    local result
    result=$(docker_run_bash 'test -f /etc/ssh/sshd_config && echo "exists"' 2>&1)
    if echo "$result" | grep -q "exists"; then
        pass "T10: SSH config file exists (/etc/ssh/sshd_config)"
        return 0
    else
        fail "T10: SSH config file not found"
        return 1
    fi
}

test_supervisord_config() {
    local result
    result=$(docker_run_bash 'test -f /etc/supervisord.conf && echo "exists"' 2>&1)
    if echo "$result" | grep -q "exists"; then
        pass "T11: supervisord config exists (/etc/supervisord.conf)"
        return 0
    else
        fail "T11: supervisord config not found"
        return 1
    fi
}

test_jupyter_executable() {
    local result
    result=$(docker_run_bash 'test -x /opt/venv/bin/jupyter && echo "executable"' 2>&1)
    if echo "$result" | grep -q "executable"; then
        pass "T12: Jupyter executable exists (/opt/venv/bin/jupyter)"
        return 0
    else
        fail "T12: Jupyter executable not found at /opt/venv/bin/jupyter"
        return 1
    fi
}

test_docker_cli() {
    local result
    result=$(docker_run docker --version 2>&1)
    if echo "$result" | grep -qi "docker version"; then
        pass "T13: Docker CLI available"
        return 0
    else
        fail "T13: Docker CLI not available, got: $result"
        return 1
    fi
}

test_devuser_exists() {
    local result
    result=$(docker_run id devuser 2>&1)
    if echo "$result" | grep -q "uid="; then
        pass "T14: devuser exists"
        return 0
    else
        fail "T14: devuser does not exist, got: $result"
        return 1
    fi
}

test_conda_version() {
    local result
    result=$(docker_run /opt/conda/bin/conda --version 2>&1)
    if echo "$result" | grep -q "conda"; then
        pass "T15: conda --version available: $result"
        return 0
    else
        fail "T15: conda not available, got: $result"
        return 1
    fi
}

# ─────────────────────────── L5 PATH 优先级与环境隔离 ───────────────────────────
test_python_path_priority() {
    local result
    result=$(docker_run_bash 'which python' 2>&1)
    if echo "$result" | grep -q "/opt/conda/bin/python"; then
        pass "T16: python points to conda: $result"
        return 0
    else
        fail "T16: python does not point to conda (expected /opt/conda/bin/python), got: $result"
        return 1
    fi
}

test_venv_preserved() {
    local result
    result=$(docker_run_bash 'test -x /opt/venv/bin/python && echo "exists"' 2>&1)
    if echo "$result" | grep -q "exists"; then
        pass "T17: /opt/venv/bin/python still exists (venv preserved)"
        return 0
    else
        fail "T17: /opt/venv/bin/python not found (venv broken?)"
        return 1
    fi
}

test_venv_jupyter_still_works() {
    local result
    result=$(docker_run /opt/venv/bin/jupyter --version 2>&1)
    if echo "$result" | grep -qi "jupyter"; then
        pass "T18: /opt/venv/bin/jupyter still usable"
        return 0
    else
        fail "T18: /opt/venv/bin/jupyter not usable, got: $(echo "$result" | head -1)"
        return 1
    fi
}

# ─────────────────────────── L6 build-info 与配置 ───────────────────────────
test_build_info_exists() {
    local result
    result=$(docker_run_bash 'test -f /etc/devcontainer-variant-onnx-pytorch-build-info && cat /etc/devcontainer-variant-onnx-pytorch-build-info' 2>&1)
    if echo "$result" | grep -q "VARIANT=onnx-pytorch" && echo "$result" | grep -q "TORCH_VERSION_ACTUAL" && echo "$result" | grep -q "ONNX_VERSION_ACTUAL"; then
        pass "T19: build-info exists and contains torch/onnx versions"
        return 0
    else
        fail "T19: build-info missing required fields, output: $(echo "$result" | head -3)"
        return 1
    fi
}

test_condarc_exists() {
    local result
    result=$(docker_run_bash 'test -f /opt/conda/.condarc && cat /opt/conda/.condarc | head -5' 2>&1)
    if [ -n "$result" ] && ! echo "$result" | grep -q "No such file"; then
        pass "T20: .condarc configuration exists"
        return 0
    else
        fail "T20: .condarc not found or not readable"
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
    IMAGE="devcontainer-base:onnx-pytorch-${TAG}"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       ONNX-PyTorch Variant Unit Test Suite                  ║"
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

log_step "1. Basic Toolchain Version Tests (L1)"
test_torch_version || true
test_torchvision_version || true
test_onnx_version || true
test_onnxruntime_version || true
echo ""

log_step "2. Hello World Smoke Tests (L2)"
test_torch_tensor_smoke || true
test_onnx_export_inference_smoke || true
echo ""

log_step "3. Deep Component Tests (L3)"
test_torchvision_model_load || true
test_onnxruntime_session || true
test_cuda_not_available || true
echo ""

log_step "4. Base Service Inheritance Tests (L4)"
test_sshd_config || true
test_supervisord_config || true
test_jupyter_executable || true
test_docker_cli || true
test_devuser_exists || true
test_conda_version || true
echo ""

log_step "5. PATH Priority & Environment Isolation Tests (L5)"
test_python_path_priority || true
test_venv_preserved || true
test_venv_jupyter_still_works || true
echo ""

log_step "6. Build Info & Configuration Tests (L6)"
test_build_info_exists || true
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
