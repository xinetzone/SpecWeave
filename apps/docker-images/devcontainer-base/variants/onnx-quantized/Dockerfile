# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - ONNX-Quantized (ONNX quantization toolkit: INT8/FP16/QDQ)
# Base: devcontainer-base:onnx-dev-${BASE_TAG} (pure ONNX, free-threading, no PyTorch)
# Primary: onnxruntime.quantization + onnxconverter-common (FP16) + onnxsim
# Optional: neural-compressor (needs torch, install on demand, NOT installed by default)
# Excluded: torch/torchvision/onnxoptimizer (inherited from onnx-dev)
# Build (CN): docker build -f variants/onnx-quantized/Dockerfile --build-arg APT_MIRROR=aliyun --build-arg PIP_MIRROR=aliyun -t devcontainer-base:onnx-quantized-latest .
# Verify: docker run --rm devcontainer-base:onnx-quantized-latest /opt/conda/envs/main/bin/python -c "from onnxruntime.quantization import quantize_dynamic;print('quantize OK')"
# =============================================================================

ARG BASE_TAG=latest
ARG APT_MIRROR=official
ARG CONDA_MIRROR=bfsu
ARG PIP_MIRROR=aliyun

FROM devcontainer-base:onnx-dev-${BASE_TAG}

ARG BASE_TAG
ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR

LABEL maintainer="SpecWeave"
LABEL description="DevContainer onnx-quantized: ONNX quantization toolkit (INT8/FP16/QDQ, free-threading, no PyTorch)"
LABEL variant="onnx-quantized"
LABEL quantization="onnxruntime,int8,fp16,qdq"

ENV CONDA_DIR=/opt/conda \
    CONDA_DEFAULT_ENV=main \
    OMP_NUM_THREADS=4 \
    OPENBLAS_NUM_THREADS=1 \
    OMP_WAIT_POLICY=PASSIVE \
    KMP_DUPLICATE_LIB_OK=TRUE
ENV PATH=/opt/conda/envs/main/bin:/opt/conda/bin:${PATH}

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# Framework already inherited from onnx-dev base layer.

# ── Stage 1/3: Init + base verification ────────────────────────────
RUN <<'S1'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_start "onnx-quantized"
variant_timer_stage 1 "Init + base verification"
assert_package_present onnx
assert_package_present onnxruntime
assert_package_present onnxsim "onnx-simplifier"
assert_package_present onnxscript
assert_python_cp314t
assert_free_threading
assert_package_absent torch
assert_package_absent onnxoptimizer
llvm-config --version 2>&1 | head -1
echo "[OK] onnx-dev base verified (free-threading, torch absent, LLVM inherited)"
S1

# ── Stage 2/3: Quantization toolkit install + guards ──────────────
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    <<'S2'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 2 "Quantization toolkit install + guards"
variant_activate_main_env

# onnxruntime.quantization is built-in to onnxruntime (inherited from onnx-dev).
# onnxsim already installed by onnx-dev base; pip install is idempotent.
# NOTE: neural-compressor NOT installed by default (needs torch; INC 3.x is PyTorch-focused).
# NOTE: onnxoptimizer NOT installed (free-threading incompatible: Py_LIMITED_API x Py_GIL_DISABLED, CPython #111506).
pip_install_group "G3: Quantization Utilities" \
    "onnxconverter-common (FP16 conversion) + onnxsim (idempotent, inherited from onnx-dev)" \
    onnxconverter-common onnxsim

echo "  onnxruntime.quantization: built-in"
echo "  onnxconverter-common: $(python -c 'import onnxconverter_common;print(onnxconverter_common.__version__)' 2>&1)"
echo "  neural-compressor: $(python -c 'import neural_compressor;print(neural_compressor.__version__)' 2>/dev/null || echo 'not installed (optional, needs torch)')"

assert_python_cp314t
assert_free_threading
assert_package_absent torch
assert_package_absent onnxoptimizer

cleanup_pycache
cleanup_conda_pip_cache
S2

COPY scripts/ /opt/devcontainer-scripts/

# ── Stage 3/3: Build-info + verification + quantization smoke ─────
RUN <<'S3'
set +o pipefail
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 3 "Build-info + verification + quantization smoke"
variant_activate_main_env

ensure_all_permissions

variant_write_build_info "onnx-quantized" "onnx-dev-${BASE_TAG}" \
    "VARIANT_DESCRIPTION=ONNX quantization toolkit (INT8/FP16/QDQ/dynamic/static, pure ONNX, free-threading)" \
    "ONNXRUNTIME_VERSION=$(python -c 'import onnxruntime;print(onnxruntime.__version__)')" \
    "ONNXCONVERTER_COMMON_VERSION=$(python -c 'import onnxconverter_common;print(onnxconverter_common.__version__)' 2>/dev/null || echo unknown)" \
    "QUANTIZATION_MODES=dynamic_int8,static_int8,qdq_int8,fp16,calibration" \
    "QUANTIZATION_PROVIDERS=CPUExecutionProvider" \
    "PACKAGES_INSTALLED=onnx,onnxruntime,onnxconverter-common,onnxsim,onnxscript" \
    "PACKAGES_EXCLUDED=torch,torchvision(by design);onnxoptimizer(ft-incompatible:CPython#111506);neural-compressor(optional,needs torch)" \
    "OPTIONAL_PACKAGES=neural-compressor(needs torch: pip install neural-compressor torch)" \
    "BASE_VARIANT=onnx-dev(LLVM+ONNX inherited)" \
    "SCRIPTS_DIR=/opt/devcontainer-scripts/"

cleanup_all

verify_validation_header "Quantization Toolkit Verification"
python -c "from onnxruntime.quantization import quantize_dynamic,QuantType,quantize_static,CalibrationDataReader,QuantFormat,CalibrationMethod; print('[OK] onnxruntime.quantization imports')"
python -c "from onnxconverter_common import float16; print('[OK] onnxconverter_common.float16 imports')"
echo "  neural-compressor: $(python -c 'import neural_compressor;print(neural_compressor.__version__)' 2>/dev/null || echo 'not installed (optional)')"
assert_package_present onnx
assert_package_present onnxruntime
assert_package_present onnxconverter_common
assert_python_cp314t
assert_free_threading
assert_package_absent torch
assert_package_absent onnxoptimizer
llvm-config --version 2>&1 | head -1 && echo "  [OK] LLVM inherited"
verify_base_services
echo -n "  [VERIFY] devuser quantization access... "
su - devuser -c "python -c 'from onnxruntime.quantization import quantize_dynamic;print(\"OK\")'" >/dev/null 2>&1 \
    && echo "[OK]" || { echo "[FAIL]"; exit 1; }
test -d /opt/devcontainer-scripts && echo "  [OK] /opt/devcontainer-scripts/ present" || echo "  [WARN] scripts dir not found"

# ── Smoke Test 1: Dynamic INT8 quantization ──
echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│  [SMOKE] Dynamic INT8 quantization              │"
echo "└─────────────────────────────────────────────────┘"
python - <<'QSMOKE'
import onnx, onnxruntime as ort, numpy as np, os
from onnx import TensorProto, helper
from onnxruntime.quantization import quantize_dynamic, QuantType
rng = np.random.default_rng(42)
IN_DIM, OUT_DIM = 10, 5
w = (rng.standard_normal((IN_DIM, OUT_DIM)) * 0.1).astype(np.float32)
b = np.zeros(OUT_DIM, dtype=np.float32)
nodes = [helper.make_node("Gemm", ["input", "w", "b"], ["output"])]
graph = helper.make_graph(nodes, "linear",
    [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, IN_DIM])],
    [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, OUT_DIM])],
    [helper.make_tensor("w", TensorProto.FLOAT, w.shape, w.tobytes(), raw=True),
     helper.make_tensor("b", TensorProto.FLOAT, b.shape, b.tobytes(), raw=True)])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
model.ir_version = min(model.ir_version, 9)
onnx_path, quant_path = "/tmp/test_model.onnx", "/tmp/test_model_int8.onnx"
onnx.save(model, onnx_path)
quantize_dynamic(onnx_path, quant_path, weight_type=QuantType.QInt8)
onnx.checker.check_model(onnx.load(quant_path))
sess_fp32 = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
sess_int8 = ort.InferenceSession(quant_path, providers=["CPUExecutionProvider"])
inp = rng.standard_normal((1, IN_DIM)).astype(np.float32)
out_fp32 = sess_fp32.run(None, {"input": inp})[0]
out_int8 = sess_int8.run(None, {"input": inp})[0]
md = np.max(np.abs(out_fp32 - out_int8))
assert md < 5.0, f"Quantization accuracy loss too high: {md}"
fp32_sz, int8_sz = os.path.getsize(onnx_path), os.path.getsize(quant_path)
print(f"[OK] Dynamic INT8: max_diff={md:.6f}, size FP32={fp32_sz}B INT8={int8_sz}B ({int8_sz/fp32_sz:.1%})")
os.remove(onnx_path); os.remove(quant_path)
QSMOKE

# ── Smoke Test 2: FP16 conversion ──
echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│  [SMOKE] FP16 conversion                       │"
echo "└─────────────────────────────────────────────────┘"
python - <<'FP16SMOKE'
import onnx, onnxruntime as ort, numpy as np, os
from onnx import TensorProto, helper
from onnxconverter_common import float16
rng = np.random.default_rng(42)
IN_DIM, OUT_DIM = 8, 4
w = (rng.standard_normal((IN_DIM, OUT_DIM)) * 0.1).astype(np.float32)
b = np.zeros(OUT_DIM, dtype=np.float32)
half = np.array([0.5], dtype=np.float32); one = np.array([1.0], dtype=np.float32)
nodes = [helper.make_node("Gemm", ["input","w","b"], ["gemm_out"]),
         helper.make_node("Mul", ["gemm_out","half"], ["mul_out"]),
         helper.make_node("Add", ["mul_out","one"], ["output"])]
graph = helper.make_graph(nodes, "simple",
    [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, IN_DIM])],
    [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, OUT_DIM])],
    [helper.make_tensor("w",TensorProto.FLOAT,w.shape,w.tobytes(),raw=True),
     helper.make_tensor("b",TensorProto.FLOAT,b.shape,b.tobytes(),raw=True),
     helper.make_tensor("half",TensorProto.FLOAT,half.shape,half.tobytes(),raw=True),
     helper.make_tensor("one",TensorProto.FLOAT,one.shape,one.tobytes(),raw=True)])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
model.ir_version = min(model.ir_version, 9)
fp32_path, fp16_path = "/tmp/test_fp32.onnx", "/tmp/test_fp16.onnx"
onnx.save(model, fp32_path)
fp16_model = float16.convert_float_to_float16(onnx.load(fp32_path))
onnx.save(fp16_model, fp16_path)
onnx.checker.check_model(onnx.load(fp16_path))
sess_fp32 = ort.InferenceSession(fp32_path, providers=["CPUExecutionProvider"])
sess_fp16 = ort.InferenceSession(fp16_path, providers=["CPUExecutionProvider"])
inp = rng.standard_normal((1, IN_DIM)).astype(np.float32)
out_fp32 = sess_fp32.run(None, {"input": inp})[0]
out_fp16 = sess_fp16.run(None, {"input": inp.astype(np.float16)})[0]
md = np.max(np.abs(out_fp16.astype(np.float32) - out_fp32))
assert md < 5.0, f"FP16 precision loss too high: {md}"
fp32_sz, fp16_sz = os.path.getsize(fp32_path), os.path.getsize(fp16_path)
print(f"[OK] FP16 conversion: max_diff={md:.6f}, size FP32={fp32_sz}B FP16={fp16_sz}B ({fp16_sz/fp32_sz:.1%})")
os.remove(fp32_path); os.remove(fp16_path)
FP16SMOKE

# ── Smoke Test 3: Static QDQ quantization ──
echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│  [SMOKE] Static QDQ quantization                │"
echo "└─────────────────────────────────────────────────┘"
python - <<'STATICSMOKE'
import onnx, onnxruntime as ort, numpy as np, os
from onnx import TensorProto, helper
from onnxruntime.quantization import quantize_static, QuantType, QuantFormat, CalibrationMethod, CalibrationDataReader
rng = np.random.default_rng(42)
IN_DIM, HID_DIM, OUT_DIM = 16, 32, 8
w1 = (rng.standard_normal((IN_DIM,HID_DIM))/np.sqrt(IN_DIM)).astype(np.float32); b1 = np.zeros(HID_DIM,dtype=np.float32)
w2 = (rng.standard_normal((HID_DIM,OUT_DIM))/np.sqrt(HID_DIM)).astype(np.float32); b2 = np.zeros(OUT_DIM,dtype=np.float32)
nodes = [helper.make_node("Gemm",["input","w1","b1"],["g1"]), helper.make_node("Relu",["g1"],["r1"]),
         helper.make_node("Gemm",["r1","w2","b2"],["output"])]
graph = helper.make_graph(nodes, "mlp",
    [helper.make_tensor_value_info("input",TensorProto.FLOAT,[1,IN_DIM])],
    [helper.make_tensor_value_info("output",TensorProto.FLOAT,[1,OUT_DIM])],
    [helper.make_tensor("w1",TensorProto.FLOAT,w1.shape,w1.tobytes(),raw=True),
     helper.make_tensor("b1",TensorProto.FLOAT,b1.shape,b1.tobytes(),raw=True),
     helper.make_tensor("w2",TensorProto.FLOAT,w2.shape,w2.tobytes(),raw=True),
     helper.make_tensor("b2",TensorProto.FLOAT,b2.shape,b2.tobytes(),raw=True)])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("",18)])
model.ir_version = min(model.ir_version, 9)
fp32_path, qdq_path = "/tmp/mlp.onnx", "/tmp/mlp_qdq.onnx"
onnx.save(model, fp32_path)
class RandomCalib(CalibrationDataReader):
    def __init__(self, n=10): self.data=[{"input":rng.standard_normal((1,IN_DIM)).astype(np.float32)} for _ in range(n)]; self.idx=0
    def get_next(self):
        if self.idx>=len(self.data): return None
        d=self.data[self.idx]; self.idx+=1; return d
    def rewind(self): self.idx=0
quantize_static(fp32_path, qdq_path, RandomCalib(15), quant_format=QuantFormat.QDQ,
    per_channel=True, activation_type=QuantType.QInt8, weight_type=QuantType.QInt8,
    calibrate_method=CalibrationMethod.MinMax)
onnx.checker.check_model(onnx.load(qdq_path))
m = onnx.load(qdq_path)
qdq_count = sum(1 for n in m.graph.node if n.op_type in ("QuantizeLinear","DequantizeLinear"))
assert qdq_count > 0, "No QDQ nodes found"
sess_fp32 = ort.InferenceSession(fp32_path, providers=["CPUExecutionProvider"])
sess_qdq = ort.InferenceSession(qdq_path, providers=["CPUExecutionProvider"])
inp = rng.standard_normal((1,IN_DIM)).astype(np.float32)
out_fp32 = sess_fp32.run(None,{"input":inp})[0]
out_qdq = sess_qdq.run(None,{"input":inp})[0]
md = np.max(np.abs(out_fp32 - out_qdq))
assert md < 5.0, f"Static QDQ accuracy loss: {md}"
print(f"[OK] Static QDQ: QDQ nodes={qdq_count}, max_diff={md:.6f}")
os.remove(fp32_path); os.remove(qdq_path)
STATICSMOKE

# ── Optional: neural-compressor status (skipped if not installed) ──
if python -c "import neural_compressor" 2>/dev/null; then
    echo "[INFO] neural-compressor detected (optional PyTorch extension present)"
else
    echo "[SKIP] neural-compressor not installed (expected: pip install neural-compressor torch for PyTorch quantization)"
fi

echo ""
variant_timer_summary "onnx-quantized Variant (add-on)"
echo "########################################################################"
echo "# ONNX-QUANTIZED BUILD COMPLETE - INT8/FP16/QDQ, pure ONNX, GIL off"
echo "# Quick: from onnxruntime.quantization import quantize_dynamic, QuantType"
echo "#        quantize_dynamic('model.onnx','model_int8.onnx',weight_type=QuantType.QInt8)"
echo "########################################################################"
S3
