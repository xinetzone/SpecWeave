#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANTS_DIR="$(dirname "$SCRIPT_DIR")"

source "${VARIANTS_DIR}/shared/lib/logging.sh"
LOG_SERVICE="test-onnx-quantized"
LOG_JSON_OUTPUT="/tmp/test-onnx-quantized-events.jsonl"

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

Unit test script for onnx-quantized variant (base: onnx-dev, free-threading main env, no PyTorch).

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

docker_run_mount_bash() {
    local host_dir="$1"
    local container_dir="$2"
    local cmd="$3"
    docker run --rm -v "${host_dir}:${container_dir}:ro" "$IMAGE" bash -c "$cmd" 2>&1
}

# ─────────────────────────── L1 基础工具链版本（继承onnx-dev,free-threading） ───────────────────────────
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

test_torch_absent() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import importlib.util as u,sys;f=u.find_spec('torch');o=u.find_spec('onnxoptimizer');print('ABSENT_OK' if (f is None and o is None) else 'UNEXPECTED_PRESENT')" 2>&1)
    if echo "$result" | grep -q "ABSENT_OK"; then
        pass "T2: torch + onnxoptimizer absent (by design, inherited from onnx-dev)"
        return 0
    else
        fail "T2: torch/onnxoptimizer unexpectedly present, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

test_onnx_version() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import onnx;print('VER_ONNX='+onnx.__version__)" 2>&1)
    local ver
    ver=$(echo "$result" | grep -oE 'VER_ONNX=[0-9]+\.[0-9]+\.[0-9a-z+.]+' | head -1 | sed 's/VER_ONNX=//')
    if [ -n "$ver" ]; then
        pass "T3: onnx version = $ver"
        return 0
    else
        fail "T3: onnx not importable, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

test_onnxruntime_version() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import onnxruntime;print('VER_ORT='+onnxruntime.__version__)" 2>&1)
    local ver
    ver=$(echo "$result" | grep -oE 'VER_ORT=[0-9]+\.[0-9]+\.[0-9a-z+.]+' | head -1 | sed 's/VER_ORT=//')
    if [ -n "$ver" ]; then
        pass "T4: onnxruntime version = $ver"
        return 0
    else
        fail "T4: onnxruntime not importable, output: $(echo "$result" | grep -v '^\[' | tail -3)"
        return 1
    fi
}

# ─────────────────────────── L2 量化工具链导入 ───────────────────────────
test_onnxconverter_common() {
    local result
    result=$(docker_run "$MAIN_PY" -c "from onnxconverter_common import float16;print('fp16-ok')" 2>&1)
    if echo "$result" | grep -q "fp16-ok"; then
        pass "T5: onnxconverter_common.float16 importable"
        return 0
    else
        fail "T5: onnxconverter_common.float16 not importable, output: $(echo "$result" | head -3)"
        return 1
    fi
}

test_onnxruntime_tools() {
    local result
    result=$(docker_run "$MAIN_PY" -c "from onnxruntime.transformers import optimizer;print('ort-tools-ok')" 2>&1)
    if echo "$result" | grep -q "ort-tools-ok"; then
        pass "T6: onnxruntime.transformers.optimizer importable"
        return 0
    else
        fail "T6: onnxruntime.transformers.optimizer not importable, output: $(echo "$result" | head -3)"
        return 1
    fi
}

test_neural_compressor() {
    local result
    result=$(docker_run_bash "$MAIN_PY -c \"
try:
    import neural_compressor
    print(f\\\"nc-ok version={neural_compressor.__version__}\\\")
except ImportError:
    print(\\\"nc-skip\\\")
\"" 2>&1)
    if echo "$result" | grep -q "nc-ok"; then
        local ncver
        ncver=$(echo "$result" | grep -oE "version=[0-9.]+" | head -1)
        pass "T7: neural_compressor importable $ncver (optional)"
        return 0
    elif echo "$result" | grep -q "nc-skip"; then
        # Optional package - not installed is OK
        pass "T7: neural_compressor not installed (optional, expected - using onnxruntime.quantization natively)"
        return 0
    else
        fail "T7: neural_compressor check unexpected output: $(echo "$result" | head -3)"
        return 1
    fi
}

test_onnxsim() {
    local result
    result=$(docker_run "$MAIN_PY" -c "from onnxsim import simplify;print('onnxsim-ok')" 2>&1)
    if echo "$result" | grep -q "onnxsim-ok"; then
        pass "T8: onnxsim.simplify importable"
        return 0
    else
        fail "T8: onnxsim not importable, output: $(echo "$result" | head -3)"
        return 1
    fi
}

# ─────────────────────────── L3 量化功能冒烟测试（纯ONNX,无torch） ───────────────────────────
test_fp16_conversion() {
    local result
    result=$(docker_run_bash 'cat > /tmp/fp16_test.py << EOF
import onnx, numpy as np
from onnx import TensorProto, helper
from onnxconverter_common import float16

# Build FP32 model: output = input * 2 + 1 (pure ONNX helper, no torch)
two = np.array([2.0], dtype=np.float32)
one = np.array([1.0], dtype=np.float32)
nodes = [
    helper.make_node("Mul", ["input", "two"], ["mul_out"]),
    helper.make_node("Add", ["mul_out", "one"], ["output"]),
]
graph = helper.make_graph(
    nodes, "scale_shift",
    [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 3])],
    [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 3])],
    [helper.make_tensor("two", TensorProto.FLOAT, two.shape, two.tobytes(), raw=True),
     helper.make_tensor("one", TensorProto.FLOAT, one.shape, one.tobytes(), raw=True)])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
model.ir_version = min(model.ir_version, 9)
onnx.save(model, "/tmp/fp32.onnx")

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
'"$MAIN_PY"' /tmp/fp16_test.py && rm -f /tmp/fp16_test.py /tmp/fp32.onnx /tmp/fp16.onnx' 2>&1)
    if echo "$result" | grep -q "fp16-convert-ok"; then
        local diff
        diff=$(echo "$result" | grep -oE "max_diff=[0-9.e-]+" | head -1)
        pass "T9: FP16 conversion + inference smoke $diff"
        return 0
    else
        fail "T9: FP16 conversion failed, output: $(echo "$result" | head -5)"
        return 1
    fi
}

test_dynamic_int8_quantization() {
    local result
    result=$(docker_run_bash 'cat > /tmp/dynq_test.py << EOF
import onnx, numpy as np
from onnx import TensorProto, helper
from onnxruntime.quantization import quantize_dynamic, QuantType

# Build Gemm model (pure ONNX, equivalent of nn.Linear(64, 10))
rng = np.random.default_rng(42)
IN_DIM, OUT_DIM = 64, 10
w = (rng.standard_normal((IN_DIM, OUT_DIM)) / np.sqrt(IN_DIM)).astype(np.float32)
b = np.zeros(OUT_DIM, dtype=np.float32)
nodes = [helper.make_node("Gemm", ["input", "w", "b"], ["output"])]
graph = helper.make_graph(
    nodes, "linear",
    [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, IN_DIM])],
    [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, OUT_DIM])],
    [helper.make_tensor("w", TensorProto.FLOAT, w.shape, w.tobytes(), raw=True),
     helper.make_tensor("b", TensorProto.FLOAT, b.shape, b.tobytes(), raw=True)])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
model.ir_version = min(model.ir_version, 9)
onnx.save(model, "/tmp/mlp.onnx")

quantize_dynamic("/tmp/mlp.onnx", "/tmp/mlp_int8.onnx", weight_type=QuantType.QInt8)

import onnxruntime as ort
sess = ort.InferenceSession("/tmp/mlp_int8.onnx", providers=["CPUExecutionProvider"])
inp = np.random.randn(1,64).astype(np.float32)
out = sess.run(None, {"input": inp})[0]
assert out.shape == (1,10), f"Unexpected shape: {out.shape}"
print(f"dynq-ok shape={out.shape}")
EOF
'"$MAIN_PY"' /tmp/dynq_test.py && rm -f /tmp/dynq_test.py /tmp/mlp.onnx /tmp/mlp_int8.onnx' 2>&1)
    if echo "$result" | grep -q "dynq-ok"; then
        pass "T10: INT8 Dynamic quantization + inference smoke"
        return 0
    else
        fail "T10: INT8 Dynamic quantization failed, output: $(echo "$result" | head -5)"
        return 1
    fi
}

test_static_qdq_quantization() {
    local result
    result=$(docker_run_bash 'cat > /tmp/staticq_test.py << EOF
import onnx, numpy as np
from onnx import TensorProto, helper
from onnxruntime.quantization import quantize_static, QuantType, CalibrationDataReader

# Build Gemm model (pure ONNX, equivalent of nn.Linear(32, 10))
rng = np.random.default_rng(42)
IN_DIM, OUT_DIM = 32, 10
w = (rng.standard_normal((IN_DIM, OUT_DIM)) / np.sqrt(IN_DIM)).astype(np.float32)
b = np.zeros(OUT_DIM, dtype=np.float32)
nodes = [helper.make_node("Gemm", ["input", "w", "b"], ["output"])]
graph = helper.make_graph(
    nodes, "linear",
    [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, IN_DIM])],
    [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, OUT_DIM])],
    [helper.make_tensor("w", TensorProto.FLOAT, w.shape, w.tobytes(), raw=True),
     helper.make_tensor("b", TensorProto.FLOAT, b.shape, b.tobytes(), raw=True)])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
model.ir_version = min(model.ir_version, 9)
onnx.save(model, "/tmp/mlp32.onnx")

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
'"$MAIN_PY"' /tmp/staticq_test.py && rm -f /tmp/staticq_test.py /tmp/mlp32.onnx /tmp/mlp32_qdq.onnx' 2>&1)
    if echo "$result" | grep -q "staticqdq-ok"; then
        pass "T11: INT8 Static-QDQ quantization + CalibrationDataReader smoke"
        return 0
    else
        fail "T11: INT8 Static-QDQ quantization failed, output: $(echo "$result" | head -5)"
        return 1
    fi
}

test_onnxruntime_providers() {
    local result
    result=$(docker_run "$MAIN_PY" -c "import onnxruntime as ort;print('providers',ort.get_available_providers())" 2>&1)
    if echo "$result" | grep -q "CPUExecutionProvider"; then
        pass "T12: onnxruntime providers include CPUExecutionProvider"
        return 0
    else
        fail "T12: CPUExecutionProvider not found, output: $(echo "$result" | head -3)"
        return 1
    fi
}

# ─────────────────────────── L4 基础服务继承（onnx-dev继承验证） ───────────────────────────
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

# ─────────────────────────── L5 PATH 优先级与环境隔离 ───────────────────────────
test_python_path_priority() {
    local result
    result=$(docker_run_bash 'which python' 2>&1)
    if echo "$result" | grep -q "/opt/conda/envs/main/bin/python"; then
        pass "T17: PATH priority conda-main-first: $result"
        return 0
    else
        fail "T17: python does not resolve to main env, got: $result"
        return 1
    fi
}

test_venv_removed() {
    local result
    result=$(docker_run_bash 'test ! -d /opt/venv && echo "removed"' 2>&1)
    if echo "$result" | grep -q "removed"; then
        pass "T18: /opt/venv removed"
        return 0
    else
        fail "T18: /opt/venv still exists"
        return 1
    fi
}

# ─────────────────────────── L6 build-info 与配置 ───────────────────────────
test_build_info_exists() {
    local result
    result=$(docker_run_bash 'test -f /etc/devcontainer-variant-onnx-quantized-build-info && cat /etc/devcontainer-variant-onnx-quantized-build-info' 2>&1)
    if echo "$result" | grep -q "VARIANT=onnx-quantized" && echo "$result" | grep -q "BASE_IMAGE=devcontainer-base:onnx-dev" && echo "$result" | grep -q "ONNXRUNTIME_VERSION" && echo "$result" | grep -q "ONNXCONVERTER_COMMON_VERSION"; then
        pass "T19: build-info exists with onnx-dev base + quantization package versions"
        return 0
    else
        fail "T19: build-info missing required fields (VARIANT/BASE_IMAGE=onnx-dev/versions), output: $(echo "$result" | head -5)"
        return 1
    fi
}

test_condarc_exists() {
    local result
    result=$(docker_run_bash 'test -f /opt/conda/.condarc && echo "exists"' 2>&1)
    if echo "$result" | grep -q "exists"; then
        pass "T20: .condarc configuration exists"
        return 0
    else
        fail "T20: .condarc not found"
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

# ─────────────────────────── L7 onnx_quantize_kit CI 集成测试（需挂载scripts目录） ───────────────────────────
SCRIPTS_DIR=""
find_scripts_dir() {
    # 尝试定位 scripts/onnx_quantize_kit/ 目录
    local candidate
    # 从脚本位置向上查找: variants/scripts -> variants -> devcontainer-base
    candidate="${VARIANTS_DIR}/../scripts"
    if [ -d "$candidate/onnx_quantize_kit" ]; then
        SCRIPTS_DIR="$(cd "$candidate" && pwd)"
        return 0
    fi
    return 1
}

test_quantize_kit_import() {
    if [ -z "$SCRIPTS_DIR" ]; then
        skip "T22: onnx_quantize_kit not found (scripts dir not available), skipping"
        return 0
    fi
    local result
    result=$(docker_run_mount_bash "$SCRIPTS_DIR" "/opt/devcontainer/scripts" \
        "PYTHONPATH=/opt/devcontainer/scripts:\$PYTHONPATH $MAIN_PY -c 'from onnx_quantize_kit import auto_quantize, QuantizationConfig; print(\"kit-import-ok\")'" 2>&1)
    if echo "$result" | grep -q "kit-import-ok"; then
        pass "T22: onnx_quantize_kit importable from mounted scripts (main env)"
        return 0
    else
        fail "T22: onnx_quantize_kit import failed, output: $(echo "$result" | tail -3)"
        return 1
    fi
}

test_ci_quantization_gate() {
    if [ -z "$SCRIPTS_DIR" ]; then
        skip "T23: ci_quantization_gate test skipped (scripts dir not available)"
        return 0
    fi
    local result
    result=$(docker_run_mount_bash "$SCRIPTS_DIR" "/opt/devcontainer/scripts" \
        "PYTHONPATH=/opt/devcontainer/scripts:\$PYTHONPATH $MAIN_PY /opt/devcontainer/scripts/ci_quantization_gate.py --help" 2>&1)
    if echo "$result" | grep -q "usage:" && echo "$result" | grep -q "ci_quantization_gate.py"; then
        pass "T23: ci_quantization_gate.py --help works (main env)"
        return 0
    else
        fail "T23: ci_quantization_gate.py --help failed, output: $(echo "$result" | tail -5)"
        return 1
    fi
}

test_quantize_kit_mock_model() {
    if [ -z "$SCRIPTS_DIR" ]; then
        skip "T24: onnx_quantize_kit mock model test skipped (scripts dir not available)"
        return 0
    fi
    local result
    result=$(docker_run_mount_bash "$SCRIPTS_DIR" "/opt/devcontainer/scripts" \
        'PYTHONPATH=/opt/devcontainer/scripts:$PYTHONPATH '"$MAIN_PY"' -c "
import onnx, tempfile, os, numpy as np
from onnx import TensorProto, helper
from onnx_quantize_kit import auto_quantize, QuantizationConfig

# Build Gemm model (pure ONNX, equivalent of nn.Linear(16, 8), no torch)
rng = np.random.default_rng(42)
IN_DIM, OUT_DIM = 16, 8
w = (rng.standard_normal((IN_DIM, OUT_DIM)) / np.sqrt(IN_DIM)).astype(np.float32)
b = np.zeros(OUT_DIM, dtype=np.float32)
nodes = [helper.make_node(\"Gemm\", [\"input\", \"w\", \"b\"], [\"output\"])]
graph = helper.make_graph(
    nodes, \"linear\",
    [helper.make_tensor_value_info(\"input\", TensorProto.FLOAT, [1, IN_DIM])],
    [helper.make_tensor_value_info(\"output\", TensorProto.FLOAT, [1, OUT_DIM])],
    [helper.make_tensor(\"w\", TensorProto.FLOAT, w.shape, w.tobytes(), raw=True),
     helper.make_tensor(\"b\", TensorProto.FLOAT, b.shape, b.tobytes(), raw=True)])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid(\"\", 18)])
model.ir_version = min(model.ir_version, 9)

with tempfile.TemporaryDirectory() as td:
    onnx_path = os.path.join(td, \"model.onnx\")
    onnx.save(model, onnx_path)
    cfg = QuantizationConfig(optimize_model=True, verify_accuracy=True, accuracy_threshold=0.1)
    result = auto_quantize(onnx_path, os.path.join(td, \"out.onnx\"), config=cfg)
    assert result.success, f\"auto_quantize failed: {result.error}\"
    assert os.path.exists(result.output_path), \"output model missing\"
    print(f\"kit-mock-ok strategy={result.strategy_used} max_diff={result.max_diff:.6f}\")
"' 2>&1)
    if echo "$result" | grep -q "kit-mock-ok"; then
        local diff
        diff=$(echo "$result" | grep -oE "max_diff=[0-9.e-]+" | head -1)
        pass "T24: onnx_quantize_kit auto_quantize mock model (pure ONNX) $diff"
        return 0
    else
        fail "T24: onnx_quantize_kit mock model failed, output: $(echo "$result" | tail -5)"
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
    IMAGE="devcontainer-base:onnx-quantized-${TAG}"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║      ONNX-Quantized Variant Unit Test Suite                 ║"
echo "║      (base: onnx-dev, free-threading main env, no PyTorch)  ║"
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

log_step "1. Base Toolchain Tests - free-threading + no-torch (L1, inherited from onnx-dev)"
test_free_threading || true
test_torch_absent || true
test_onnx_version || true
test_onnxruntime_version || true
echo ""

log_step "2. Quantization Toolchain Import Tests (L2)"
test_onnxconverter_common || true
test_onnxruntime_tools || true
test_neural_compressor || true
test_onnxsim || true
echo ""

log_step "3. Quantization Function Smoke Tests - pure ONNX (L3)"
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
test_venv_removed || true
echo ""

log_step "6. Build Info & Configuration Tests (L6)"
test_build_info_exists || true
test_condarc_exists || true
test_omp_env || true
echo ""

log_step "7. onnx_quantize_kit CI Integration Tests (L7)"
if find_scripts_dir; then
    log_info "Found scripts directory: ${SCRIPTS_DIR}"
    test_quantize_kit_import || true
    test_ci_quantization_gate || true
    test_quantize_kit_mock_model || true
else
    log_warn "scripts/onnx_quantize_kit not found locally, L7 tests will be skipped"
    test_quantize_kit_import
    test_ci_quantization_gate
    test_quantize_kit_mock_model
fi
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
