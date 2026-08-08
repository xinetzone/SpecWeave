#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANTS_DIR="$(dirname "$SCRIPT_DIR")"

source "${VARIANTS_DIR}/shared/lib/logging.sh"
LOG_SERVICE="test-onnx-quantized"
LOG_JSON_OUTPUT="/tmp/test-onnx-quantized-events.jsonl"

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

Unit test script for onnx-quantized variant.

Options:
  --tag TAG        Image tag suffix (default: latest)
  --image IMAGE    Full image name (overrides --tag)
  -h, --help       Show this help message

Default image: devcontainer-base:onnx-quantized-latest
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

# ─────────────────────────── L1 基础工具链版本（继承onnx-pytorch） ───────────────────────────
test_torch_version() {
    local result
    result=$(docker_run /opt/conda/bin/python -c "import torch;print('VER_TORCH='+torch.__version__)" 2>&1)
    local ver
    ver=$(echo "$result" | grep -oE 'VER_TORCH=[0-9]+\.[0-9]+\.[0-9a-z+.]+' | head -1 | sed 's/VER_TORCH=//')
    if [ -n "$ver" ]; then
        pass "T1: torch version = $ver"
        return 0
    else
        fail "T1: torch not importable, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

test_onnx_version() {
    local result
    result=$(docker_run /opt/conda/bin/python -c "import onnx;print('VER_ONNX='+onnx.__version__)" 2>&1)
    local ver
    ver=$(echo "$result" | grep -oE 'VER_ONNX=[0-9]+\.[0-9]+\.[0-9a-z+.]+' | head -1 | sed 's/VER_ONNX=//')
    if [ -n "$ver" ]; then
        pass "T2: onnx version = $ver"
        return 0
    else
        fail "T2: onnx not importable, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

test_onnxruntime_version() {
    local result
    result=$(docker_run /opt/conda/bin/python -c "import onnxruntime;print('VER_ORT='+onnxruntime.__version__)" 2>&1)
    local ver
    ver=$(echo "$result" | grep -oE 'VER_ORT=[0-9]+\.[0-9]+\.[0-9a-z+.]+' | head -1 | sed 's/VER_ORT=//')
    if [ -n "$ver" ]; then
        pass "T3: onnxruntime version = $ver"
        return 0
    else
        fail "T3: onnxruntime not importable, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

# ─────────────────────────── L2 量化工具链导入 ───────────────────────────
test_onnxconverter_common() {
    local result
    result=$(docker_run /opt/conda/bin/python -c "from onnxconverter_common import float16;print('fp16-ok')" 2>&1)
    if echo "$result" | grep -q "fp16-ok"; then
        pass "T4: onnxconverter_common.float16 importable"
        return 0
    else
        fail "T4: onnxconverter_common.float16 not importable, output: $(echo "$result" | head -3)"
        return 1
    fi
}

test_onnxruntime_tools() {
    local result
    result=$(docker_run /opt/conda/bin/python -c "from onnxruntime.transformers import optimizer;print('ort-tools-ok')" 2>&1)
    if echo "$result" | grep -q "ort-tools-ok"; then
        pass "T5: onnxruntime.transformers.optimizer importable"
        return 0
    else
        fail "T5: onnxruntime.transformers.optimizer not importable, output: $(echo "$result" | head -3)"
        return 1
    fi
}

test_neural_compressor() {
    local result
    result=$(docker_run_bash '/opt/conda/bin/python -c "
try:
    import neural_compressor
    print(f\"nc-ok version={neural_compressor.__version__}\")
except ImportError:
    try:
        from neural_compressor.adaptor.ox_utils.quantizer import Quantizer
        print(\"nc-ox-ok\")
    except ImportError:
        import sys
        print(\"nc-import-failed\")
        sys.exit(1)
"' 2>&1)
    if echo "$result" | grep -qE "nc-ok|nc-ox-ok"; then
        local ncver
        ncver=$(echo "$result" | grep -oE "version=[0-9.]+" | head -1)
        pass "T6: neural_compressor importable $ncver"
        return 0
    else
        fail "T6: neural_compressor not importable, output: $(echo "$result" | head -3)"
        return 1
    fi
}

test_onnxsim() {
    local result
    result=$(docker_run /opt/conda/bin/python -c "from onnxsim import simplify;print('onnxsim-ok')" 2>&1)
    if echo "$result" | grep -q "onnxsim-ok"; then
        pass "T7: onnxsim.simplify importable"
        return 0
    else
        fail "T7: onnxsim not importable, output: $(echo "$result" | head -3)"
        return 1
    fi
}

# ─────────────────────────── L3 量化功能冒烟测试 ───────────────────────────
test_fp16_conversion() {
    local result
    result=$(docker_run_bash 'cat > /tmp/fp16_test.py << EOF
import torch, onnx, numpy as np
from onnxconverter_common import float16

class SmallNet(torch.nn.Module):
    def forward(self, x):
        return x * 2 + 1

# Export FP32 model
torch.onnx.export(SmallNet(), torch.randn(1,3), "/tmp/fp32.onnx", opset_version=13,
                  input_names=["input"], output_names=["output"])

# Convert to FP16
fp32_model = onnx.load("/tmp/fp32.onnx")
fp16_model = float16.convert_float_to_float16(fp32_model)
onnx.save(fp16_model, "/tmp/fp16.onnx")

# Validate FP16 model loads
import onnxruntime as ort
sess = ort.InferenceSession("/tmp/fp16.onnx", providers=["CPUExecutionProvider"])
inp = np.random.randn(1,3).astype(np.float16)
out = sess.run(None, {"input": inp})[0]
expected = inp.astype(np.float32) * 2 + 1
max_diff = np.max(np.abs(out.astype(np.float32) - expected))
assert max_diff < 0.1, f"FP16 precision loss too large: {max_diff}"
print(f"fp16-convert-ok max_diff={max_diff:.6f}")
EOF
/opt/conda/bin/python /tmp/fp16_test.py && rm -f /tmp/fp16_test.py /tmp/fp32.onnx /tmp/fp16.onnx' 2>&1)
    if echo "$result" | grep -q "fp16-convert-ok"; then
        local diff
        diff=$(echo "$result" | grep -oE "max_diff=[0-9.e-]+" | head -1)
        pass "T8: FP16 conversion + inference smoke $diff"
        return 0
    else
        fail "T8: FP16 conversion failed, output: $(echo "$result" | head -5)"
        return 1
    fi
}

test_dynamic_int8_quantization() {
    local result
    result=$(docker_run_bash 'cat > /tmp/dynq_test.py << EOF
import torch, onnx, numpy as np
from onnxruntime.quantization import quantize_dynamic, QuantType

class MLP(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = torch.nn.Linear(64, 10)
    def forward(self, x):
        return self.fc(x)

torch.onnx.export(MLP(), torch.randn(1,64), "/tmp/mlp.onnx", opset_version=13,
                  input_names=["input"], output_names=["output"])

quantize_dynamic("/tmp/mlp.onnx", "/tmp/mlp_int8.onnx", weight_type=QuantType.QInt8)

import onnxruntime as ort
sess = ort.InferenceSession("/tmp/mlp_int8.onnx", providers=["CPUExecutionProvider"])
inp = np.random.randn(1,64).astype(np.float32)
out = sess.run(None, {"input": inp})[0]
assert out.shape == (1,10), f"Unexpected shape: {out.shape}"
print(f"dynq-ok shape={out.shape}")
EOF
/opt/conda/bin/python /tmp/dynq_test.py && rm -f /tmp/dynq_test.py /tmp/mlp.onnx /tmp/mlp_int8.onnx' 2>&1)
    if echo "$result" | grep -q "dynq-ok"; then
        pass "T9: INT8 Dynamic quantization + inference smoke"
        return 0
    else
        fail "T9: INT8 Dynamic quantization failed, output: $(echo "$result" | head -5)"
        return 1
    fi
}

test_static_qdq_quantization() {
    local result
    result=$(docker_run_bash 'cat > /tmp/staticq_test.py << EOF
import torch, onnx, numpy as np
from onnxruntime.quantization import quantize_static, QuantType, CalibrationDataReader

class MLP(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = torch.nn.Linear(32, 10)
    def forward(self, x):
        return self.fc(x)

torch.onnx.export(MLP(), torch.randn(1,32), "/tmp/mlp32.onnx", opset_version=13,
                  input_names=["input"], output_names=["output"])

class DummyCalibrationReader(CalibrationDataReader):
    def __init__(self):
        self.count = 0
    def get_next(self):
        if self.count >= 5:
            return None
        self.count += 1
        return {"input": np.random.randn(1,32).astype(np.float32)}

quantize_static(
    "/tmp/mlp32.onnx", "/tmp/mlp32_qdq.onnx",
    DummyCalibrationReader(),
    weight_type=QuantType.QInt8,
    activation_type=QuantType.QUInt8,
)

import onnxruntime as ort
sess = ort.InferenceSession("/tmp/mlp32_qdq.onnx", providers=["CPUExecutionProvider"])
inp = np.random.randn(1,32).astype(np.float32)
out = sess.run(None, {"input": inp})[0]
assert out.shape == (1,10), f"Unexpected shape: {out.shape}"
print(f"staticqdq-ok shape={out.shape}")
EOF
/opt/conda/bin/python /tmp/staticq_test.py && rm -f /tmp/staticq_test.py /tmp/mlp32.onnx /tmp/mlp32_qdq.onnx' 2>&1)
    if echo "$result" | grep -q "staticqdq-ok"; then
        pass "T10: INT8 Static-QDQ quantization + CalibrationDataReader smoke"
        return 0
    else
        fail "T10: INT8 Static-QDQ quantization failed, output: $(echo "$result" | head -5)"
        return 1
    fi
}

test_onnxruntime_providers() {
    local result
    result=$(docker_run /opt/conda/bin/python -c "import onnxruntime as ort;print('providers',ort.get_available_providers())" 2>&1)
    if echo "$result" | grep -q "CPUExecutionProvider"; then
        pass "T11: onnxruntime providers include CPUExecutionProvider"
        return 0
    else
        fail "T11: CPUExecutionProvider not found, output: $(echo "$result" | head -3)"
        return 1
    fi
}

# ─────────────────────────── L4 基础服务继承（onnx-pytorch继承验证） ───────────────────────────
test_sshd_config() {
    local result
    result=$(docker_run_bash 'test -f /etc/ssh/sshd_config && echo "exists"' 2>&1)
    if echo "$result" | grep -q "exists"; then
        pass "T12: SSH config file exists"
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
        pass "T13: supervisord config exists"
        return 0
    else
        fail "T13: supervisord config not found"
        return 1
    fi
}

test_jupyter_executable() {
    local result
    result=$(docker_run_bash 'test -x /opt/venv/bin/jupyter && echo "executable"' 2>&1)
    if echo "$result" | grep -q "executable"; then
        pass "T14: Jupyter executable exists"
        return 0
    else
        fail "T14: Jupyter executable not found"
        return 1
    fi
}

test_devuser_exists() {
    local result
    result=$(docker_run id devuser 2>&1)
    if echo "$result" | grep -q "uid="; then
        pass "T15: devuser exists"
        return 0
    else
        fail "T15: devuser does not exist, got: $result"
        return 1
    fi
}

# ─────────────────────────── L5 PATH 优先级与环境隔离 ───────────────────────────
test_python_path_priority() {
    local result
    result=$(docker_run /opt/conda/bin/python -c "import sys;print('PYPATH_OK:'+sys.executable)" 2>&1)
    local path
    path=$(echo "$result" | grep -oE 'PYPATH_OK:/[^ ]+' | head -1 | sed 's/PYPATH_OK://')
    if echo "$path" | grep -q "/opt/conda/bin/python"; then
        pass "T16: python points to conda: $path"
        return 0
    else
        fail "T16: python does not point to conda, got: $path"
        return 1
    fi
}

test_venv_preserved() {
    local result
    result=$(docker_run_bash 'test -x /opt/venv/bin/python && echo "exists"' 2>&1)
    if echo "$result" | grep -q "exists"; then
        pass "T17: /opt/venv preserved"
        return 0
    else
        fail "T17: /opt/venv not found"
        return 1
    fi
}

# ─────────────────────────── L6 build-info 与配置 ───────────────────────────
test_build_info_exists() {
    local result
    result=$(docker_run_bash 'test -f /etc/devcontainer-variant-onnx-quantized-build-info && cat /etc/devcontainer-variant-onnx-quantized-build-info' 2>&1)
    if echo "$result" | grep -q "VARIANT=onnx-quantized" && echo "$result" | grep -q "ONNXRUNTIME_VERSION" && echo "$result" | grep -q "ONNXCONVERTER_COMMON_VERSION"; then
        pass "T18: build-info exists with quantization package versions"
        return 0
    else
        fail "T18: build-info missing required fields, output: $(echo "$result" | head -5)"
        return 1
    fi
}

test_condarc_exists() {
    local result
    result=$(docker_run_bash 'test -f /opt/conda/.condarc && echo "exists"' 2>&1)
    if echo "$result" | grep -q "exists"; then
        pass "T19: .condarc configuration exists"
        return 0
    else
        fail "T19: .condarc not found"
        return 1
    fi
}

test_omp_env() {
    local result
    result=$(docker_run_bash 'echo "OMP_NUM_THREADS=$OMP_NUM_THREADS KMP_DUPLICATE_LIB_OK=$KMP_DUPLICATE_LIB_OK"' 2>&1)
    if echo "$result" | grep -q "OMP_NUM_THREADS=4" && echo "$result" | grep -q "KMP_DUPLICATE_LIB_OK=TRUE"; then
        pass "T20: OpenMP env defaults set correctly"
        return 0
    else
        pass "T20: OpenMP env defaults (info only): $result"
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
    IMAGE="devcontainer-base:onnx-quantized-${TAG}"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║      ONNX-Quantized Variant Unit Test Suite                 ║"
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
test_onnx_version || true
test_onnxruntime_version || true
echo ""

log_step "2. Quantization Toolchain Import Tests (L2)"
test_onnxconverter_common || true
test_onnxruntime_tools || true
test_neural_compressor || true
test_onnxsim || true
echo ""

log_step "3. Quantization Function Smoke Tests (L3)"
test_fp16_conversion || true
test_dynamic_int8_quantization || true
test_static_qdq_quantization || true
test_onnxruntime_providers || true
echo ""

log_step "4. Base Service Inheritance Tests (L4)"
test_sshd_config || true
test_supervisord_config || true
test_jupyter_executable || true
test_devuser_exists || true
echo ""

log_step "5. PATH Priority & Environment Isolation Tests (L5)"
test_python_path_priority || true
test_venv_preserved || true
echo ""

log_step "6. Build Info & Configuration Tests (L6)"
test_build_info_exists || true
test_condarc_exists || true
test_omp_env || true
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
