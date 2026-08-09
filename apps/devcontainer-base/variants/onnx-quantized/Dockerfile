# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - ONNX Quantized Variant Dockerfile
# Project: SpecWeave Full-featured Development Container - ONNX Model Quantization Toolkit
# Base: devcontainer-base:onnx-pytorch-${BASE_TAG} (PyTorch CPU + ONNX + ONNX Runtime + LLVM)
# Toolchain: onnxruntime.quantization (primary) + onnxconverter-common + onnxsim. Note: neural-compressor is NOT installed by default (optional PyTorch extension).
# Quantization: Dynamic/static quantization, QDQ format, INT8/FP16 calibration, accuracy validation
# PATH priority: /opt/conda/bin first (quantization tools directly available in base conda env)
#
# Build: docker build -f variants/onnx-quantized/Dockerfile -t devcontainer-base:onnx-quantized-latest .
# CN:    docker build -f variants/onnx-quantized/Dockerfile \
#          --build-arg APT_MIRROR=aliyun --build-arg CONDA_MIRROR=tuna --build-arg PIP_MIRROR=aliyun \
#          -t devcontainer-base:onnx-quantized-latest .
# Run:   docker run -d --privileged -p 2222:22 -p 2375:2375 -p 8888:8888 \
#          -e USER_PASSWORD=pass -e JUPYTER_TOKEN=mysecret -e GRANT_SUDO=yes \
#          -v $(pwd)/workspace:/workspace -v docker-data:/var/lib/docker \
#          devcontainer-base:onnx-quantized-latest
# Verify: docker run --rm devcontainer-base:onnx-quantized-latest \
#          /opt/conda/bin/python -c "from onnxruntime.quantization import quantize_dynamic;print('quantize OK')"
#
# Variant Stage Layering (additional 3 layers on top of onnx-pytorch variant):
#   Stage 1/3: PATH verification + timer initialization + base tool check
#   Stage 2/3: Install quantization packages (onnxconverter-common, onnxsim)
#   Stage 3/3: build-info + cleanup + quantization smoke test + timing summary
#
# Build Timing: 每个Stage结束时输出 [TIMER] 本阶段耗时+累计耗时，最终输出汇总表
# =============================================================================

ARG BASE_TAG=latest
ARG APT_MIRROR=official
ARG CONDA_MIRROR=tuna
ARG PIP_MIRROR=aliyun

FROM devcontainer-base:onnx-pytorch-${BASE_TAG}

ARG BASE_TAG
ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR

LABEL maintainer="SpecWeave"
LABEL description="DevContainer onnx-quantized variant with ONNX quantization toolkit (INT8/FP16 dynamic/static/QDQ via onnxruntime.quantization; neural-compressor optional)"
LABEL variant="onnx-quantized"
LABEL quantization="onnxruntime,int8,fp16,qdq"

ENV CONDA_DIR=/opt/conda

ENV PATH=/opt/conda/bin:${PATH}

# OpenMP defaults for quantized inference performance (prevents over-subscription)
ENV OMP_NUM_THREADS=4
ENV OPENBLAS_NUM_THREADS=1
ENV OMP_WAIT_POLICY=PASSIVE
ENV KMP_DUPLICATE_LIB_OK=TRUE

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# ═══════════════════════════════════════════════════════════════════
# Stage 1/3 (追加层1): 基础验证 + 计时器初始化
# 变化频率：最低
# 原则：验证 onnx-pytorch 基础组件；初始化追加层计时器
# ═══════════════════════════════════════════════════════════════════
RUN <<'STAGE1_EOF'
echo ""
echo "########################################################################"
echo "# [ONNX-QUANTIZED VARIANT STAGE 1/3] Base Verification + Timer Init"
echo "# CONDA_MIRROR=${CONDA_MIRROR}, PIP_MIRROR=${PIP_MIRROR}"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
echo "[TIMER] ONNX-Quantized variant build started at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "START=$_STAGE_START" > /tmp/.onnx-quantized-variant-build-timer
echo "[BUILD] Verifying base onnx-pytorch installation..."
echo "  - torch: $(python -c 'import torch;print(torch.__version__)' 2>/dev/null || echo 'not found')"
echo "  - onnx: $(python -c 'import onnx;print(onnx.__version__)' 2>/dev/null || echo 'not found')"
echo "  - onnxruntime: $(python -c 'import onnxruntime;print(onnxruntime.__version__)' 2>/dev/null || echo 'not found')"
echo "  - conda: $(/opt/conda/bin/conda --version 2>&1 | head -1)"
echo "  - python: $(python --version 2>&1)"
echo "  - PATH: $PATH"
echo ""
echo "[BUILD] Verifying devuser + services preserved..."
echo "  - devuser exists: $(id devuser 2>&1 | head -1)"
echo "  - /opt/venv exists: $(test -d /opt/venv && echo 'yes' || echo 'no')"
echo "  - docker: $(docker --version 2>&1 | head -1)"
echo "  - supervisord: $(supervisord --version 2>&1 | head -1)"
echo ""
_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_TOTAL=$((_NOW - $(grep '^START=' /tmp/.onnx-quantized-variant-build-timer | cut -d= -f2)))
echo "OQS1=$_NOW" >> /tmp/.onnx-quantized-variant-build-timer
echo "[TIMER] Stage 1/3 (base verify+init) took ${_ELAPSED}s | ONNX-Quantized variant cumulative: ${_TOTAL}s"
echo '[OK] Stage 1 complete'
STAGE1_EOF

# ═══════════════════════════════════════════════════════════════════
# Stage 2/3 (追加层2): 安装量化工具包
# 变化频率：中（工具版本升级时改）
# 原则：在 base conda 环境安装量化相关包；使用 BuildKit cache 加速
# 包含：onnxruntime.quantization (built-in 核心量化引擎), onnxconverter-common (FP16转换),
#       onnxsim (模型简化预处理)
# 不包含：neural-compressor (PyTorch场景可选，需手动 pip install neural-compressor)
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    <<'STAGE2_EOF'
echo ""
echo "########################################################################"
echo "# [ONNX-QUANTIZED VARIANT STAGE 2/3] Install Quantization Toolkit"
echo "# Packages:"
echo "#   - onnxconverter-common (ONNX FP16 conversion utilities)"
echo "#   - onnxsim              (ONNX model simplification, pre-quantization)"
echo "# NOT INSTALLED BY DEFAULT:"
echo "#   - neural-compressor    (Intel INC: PyTorch-only in 3.x, ONNX adaptor deprecated)"
echo "#     Install manually if needed: pip install neural-compressor"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
source /opt/conda/etc/profile.d/conda.sh
conda activate base
echo "[OK] base environment activated"
echo "  - conda env: $CONDA_DEFAULT_ENV"
echo ""

echo "[ACTION] Installing quantization packages via pip..."
echo "[INFO] onnxruntime already has built-in quantization (onnxruntime.quantization)"
echo "[INFO] Installing additional quantization utilities..."
echo ""
pip install --no-cache-dir \
    onnxconverter-common \
    onnxsim
echo ""
echo "[OK] Quantization toolkit installation complete"
echo ""

echo "[INFO] Installed package versions:"
echo "  - onnxruntime.quantization: $(python -c 'from onnxruntime.quantization import quantize_dynamic, QuantType; print("available (dynamic+static QDQ)")' 2>&1)"
echo "  - onnxconverter-common: $(python -c 'import onnxconverter_common; print(onnxconverter_common.__version__)' 2>&1)"
echo "  - neural-compressor: $(python -c 'import neural_compressor; print(neural_compressor.__version__)' 2>/dev/null || echo 'not installed (optional: pip install neural-compressor)')"
echo "  - onnxsim: $(python -c 'import onnxsim; print(onnxsim.__version__)' 2>&1)"
echo ""

echo "[ACTION] Setting permissions for devuser..."
# Only fix bin directory executables (fast, <1 sec); base image already handled /opt/conda
# Pip installs files with umask 022 (world-readable), so no recursive chmod needed
find /opt/conda/bin -type f -executable -exec chmod a+x {} \; 2>/dev/null || true
echo "[OK] Permissions verified (bin executables only, base image permissions preserved)"
echo ""

_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.onnx-quantized-variant-build-timer | cut -d= -f2)
_TOTAL=$((_NOW - _START))
echo "OQS2=$_NOW" >> /tmp/.onnx-quantized-variant-build-timer
echo "[TIMER] Stage 2/3 (install quantization toolkit) took ${_ELAPSED}s | ONNX-Quantized variant cumulative: ${_TOTAL}s"
echo '[OK] Stage 2 complete'
STAGE2_EOF

COPY scripts/ /opt/devcontainer-scripts/

# ═══════════════════════════════════════════════════════════════════
# Stage 3/3 (追加层3): build-info + 清理 + 量化冒烟测试 + 汇总表
# 变化频率：最低
# 原则：写入 variant build-info；清理缓存；运行量化冒烟测试（动态INT8量化+推理验证）
# ═══════════════════════════════════════════════════════════════════
RUN <<'STAGE3_EOF'
echo ""
echo "########################################################################"
echo "# [ONNX-QUANTIZED VARIANT STAGE 3/3] Final Metadata, Cleanup, Quantization Smoke Test"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
source /opt/conda/etc/profile.d/conda.sh
conda activate base

echo "[ACTION] Writing build metadata to /etc/devcontainer-variant-onnx-quantized-build-info..."
ORT_VERSION=$(python -c "import onnxruntime;print(onnxruntime.__version__)" 2>/dev/null || echo "unknown")
TORCH_VERSION_ACTUAL=$(python -c "import torch;print(torch.__version__)" 2>/dev/null || echo "unknown")
ONNX_VERSION_ACTUAL=$(python -c "import onnx;print(onnx.__version__)" 2>/dev/null || echo "unknown")
NC_VERSION=$(python -c "import neural_compressor;print(neural_compressor.__version__)" 2>/dev/null || echo "not installed (optional)")
OCC_VERSION=$(python -c "import onnxconverter_common;print(onnxconverter_common.__version__)" 2>/dev/null || echo "unknown")
ONNXSIM_VERSION=$(python -c "import onnxsim;print(onnxsim.__version__)" 2>/dev/null || echo "unknown")
printf '%s\n' \
    "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "VARIANT=onnx-quantized" \
    "VARIANT_DESCRIPTION=ONNX model quantization toolkit (INT8/FP16 dynamic/static/QDQ/QAT)" \
    "BASE_IMAGE=devcontainer-base:onnx-pytorch-${BASE_TAG}" \
    "ONNXRUNTIME_VERSION=${ORT_VERSION}" \
    "TORCH_VERSION_ACTUAL=${TORCH_VERSION_ACTUAL}" \
    "ONNX_VERSION_ACTUAL=${ONNX_VERSION_ACTUAL}" \
    "NEURAL_COMPRESSOR_VERSION=${NC_VERSION}" \
    "ONNXCONVERTER_COMMON_VERSION=${OCC_VERSION}" \
    "ONNXSIM_VERSION=${ONNXSIM_VERSION}" \
    "QUANTIZATION_MODES=dynamic_int8,static_int8,qdq_int8,fp16,calibration" \
    "QUANTIZATION_PROVIDERS=CPUExecutionProvider" \
    "CONDA_DIR=/opt/conda" \
    "CONDA_MIRROR=${CONDA_MIRROR}" \
    "PIP_MIRROR=${PIP_MIRROR}" \
    "APT_MIRROR=${APT_MIRROR}" \
    "INSTALL_ENV=base" \
    "PATH_PRIORITY=conda-bin-first" \
    "SYSTEM_VENV=/opt/venv" \
    "SERVICES_PRESERVED=sshd,dockerd,podman,jupyter,supervisord" \
    "PACKAGES_INSTALLED=torch,torchvision,onnx,onnxruntime,onnxconverter-common,onnxsim" \
    "OPTIONAL_PACKAGES=neural-compressor(pytorch-only),onnxruntime-tools(legacy)" \
    "BUILD_TIMER=enabled" \
    > /etc/devcontainer-variant-onnx-quantized-build-info
echo "[OK] Build metadata written:"
cat /etc/devcontainer-variant-onnx-quantized-build-info
echo ""

echo "[ACTION] Running cleanup..."
conda clean -ya -q 2>/dev/null || true
/opt/conda/bin/pip cache purge 2>/dev/null || true
/opt/venv/bin/pip cache purge 2>/dev/null || true
apt-get clean 2>/dev/null || true
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
echo "[OK] Cleanup complete"
echo ""

echo "┌─────────────────────────────────────────────────┐"
echo "│  [VALIDATION CHECKPOINT - Stage 3/3]           │"
echo "│  Running service + quantization validation     │"
echo "└─────────────────────────────────────────────────┘"
echo ""
echo "[VALIDATE 1/8] Quantization imports..."
python -c "from onnxruntime.quantization import quantize_dynamic, QuantType, quantize_static, CalibrationDataReader; print('[OK] onnxruntime.quantization imports')"
python -c "from onnxconverter_common import float16; print('[OK] onnxconverter_common.float16 imports')"
python - <<'NCIMPORT'
"""
Neural Compressor Status Check (Optional Extension)
==================================================
📌 Starting from INC 3.x, ONNX Runtime adaptor is deprecated (PR #2199).
   INC 3.x refactored to framework-specific APIs with PyTorch as primary focus.

This project uses onnxruntime.quantization as the SOLE ONNX quantization engine.
neural-compressor is NOT installed by default. To use it for PyTorch quantization:
   pip install neural-compressor
   from neural_compressor.torch.quantization import RTNConfig, quantize
"""
import sys
try:
    import neural_compressor
    nc_ver = neural_compressor.__version__
    print(f"[INFO] neural_compressor {nc_ver} detected (optional extension)")
    try:
        from neural_compressor.torch.quantization import RTNConfig, quantize
        print("[INFO] INC 3.x PyTorch API available: RTNConfig, quantize")
    except (ImportError, AttributeError):
        print(f"[INFO] INC PyTorch API paths differ in version {nc_ver}")
except ImportError:
    print("[INFO] neural-compressor not installed (optional, not required for ONNX quantization)")
    print("[INFO] ONNX quantization uses onnxruntime.quantization natively")
NCIMPORT
echo "[VALIDATE 2/8] System venv /opt/venv preserved..."
test -d /opt/venv && test -x /opt/venv/bin/python && echo "[OK] /opt/venv preserved"
/opt/venv/bin/python --version
echo "[VALIDATE 3/8] Jupyter available from venv..."
/opt/venv/bin/jupyter --version 2>&1 | head -2
echo "[VALIDATE 4/8] Core services (docker, supervisord) preserved..."
docker --version 2>&1
supervisord --version 2>&1
echo "[OK] Core services preserved"
echo "[VALIDATE 5/8] devuser can access quantization tools..."
su - devuser -c "/opt/conda/bin/python -c 'from onnxruntime.quantization import quantize_dynamic; print(\"quantize_dynamic accessible\")'" && echo "[OK] devuser can access quantization tools"
echo "[VALIDATE 6/8] PyTorch + ONNX still working (inherited)..."
python -c "import torch,onnx,onnxruntime; print(torch.__version__,onnx.__version__,onnxruntime.__version__)"
echo "[VALIDATE 7/8] LLVM toolchain still inherited..."
llvm-config --version 2>&1 | head -1
echo "[OK] LLVM toolchain preserved"
echo "[VALIDATE 8/8] ONNX init script preserved..."
bash -n /etc/profile.d/onnx-pytorch-init.sh && echo "[OK] onnx-pytorch-init.sh valid"
echo ""
echo "[VALIDATE] All validation checks completed"
echo ""

echo "┌─────────────────────────────────────────────────┐"
echo "│  [FINAL VERIFICATION - QUANTIZATION SMOKE]     │"
echo "│  Create model → dynamic INT8 quantize → run    │"
echo "└─────────────────────────────────────────────────┘"
python - <<'QSMOKE'
import torch
import onnx
import onnxsim
import onnxruntime as ort
import numpy as np
import os
from onnxruntime.quantization import quantize_dynamic, QuantType

# Fixed seeds for deterministic smoke test
torch.manual_seed(42)
np.random.seed(42)

# 1) Create a simple model
class LinearModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = torch.nn.Linear(10, 5)
    def forward(self, x):
        return self.fc(x)

model = LinearModel().eval()
dummy = torch.randn(1, 10)
onnx_path = "/tmp/test_model.onnx"
quant_path = "/tmp/test_model_int8.onnx"

torch.onnx.export(model, dummy, onnx_path,
                  input_names=["input"], output_names=["output"],
                  opset_version=18, do_constant_folding=True)
print(f"[OK] Exported FP32 ONNX model: {onnx_path}")

# 2) Simplify model with onnxsim to fix shape inference issues before quantization
model_onnx = onnx.load(onnx_path)
model_simp, check = onnxsim.simplify(model_onnx)
assert check, "onnxsim simplification failed"
onnx.save(model_simp, onnx_path)
print("[OK] Model simplified with onnxsim (shape inference compatible)")

# 3) Dynamic quantization (INT8 weights)
quantize_dynamic(
    model_input=onnx_path,
    model_output=quant_path,
    weight_type=QuantType.QInt8,
)
print(f"[OK] Dynamic INT8 quantization -> {quant_path}")

# 4) Verify quantized model loads and runs
quant_model = onnx.load(quant_path)
onnx.checker.check_model(quant_model)
print("[OK] Quantized model passes ONNX checker")

sess_fp32 = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
sess_int8 = ort.InferenceSession(quant_path, providers=["CPUExecutionProvider"])

inp = np.random.randn(1, 10).astype(np.float32)
out_fp32 = sess_fp32.run(None, {"input": inp})[0]
out_int8 = sess_int8.run(None, {"input": inp})[0]

max_diff = np.max(np.abs(out_fp32 - out_int8))
print(f"[OK] FP32 vs INT8 max diff: {max_diff:.6f} (smoke threshold: < 5.0)")
assert max_diff < 5.0, f"Quantization accuracy loss too high: {max_diff}"

fp32_size = os.path.getsize(onnx_path)
int8_size = os.path.getsize(quant_path)
ratio = int8_size / fp32_size
print(f"[OK] Model size: FP32={fp32_size}B, INT8={int8_size}B, ratio={ratio:.2%}")

os.remove(onnx_path)
os.remove(quant_path)
print("[OK] QUANTIZATION SMOKE TEST PASSED")
QSMOKE
echo "[OK] Quantization smoke test passed"
echo ""

echo "┌─────────────────────────────────────────────────┐"
echo "│  [FINAL VERIFICATION - FP16 SMOKE]             │"
echo "│  Create model → FP16 convert → run inference   │"
echo "└─────────────────────────────────────────────────┘"
python - <<'FP16SMOKE'
import torch
import onnx
import numpy as np
from onnxconverter_common import float16
import onnxruntime as ort

# Fixed seeds for deterministic smoke test
torch.manual_seed(42)
np.random.seed(42)

# Create FP32 model
class SimpleModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = torch.nn.Linear(8, 4)
    def forward(self, x):
        return self.fc(x) * 0.5 + 1.0

model = SimpleModel().eval()
dummy = torch.randn(1, 8)
fp32_path = "/tmp/test_fp32.onnx"
fp16_path = "/tmp/test_fp16.onnx"

torch.onnx.export(model, dummy, fp32_path,
                  input_names=["input"], output_names=["output"],
                  opset_version=18, do_constant_folding=True)
print("[OK] Exported FP32 model")

# Convert to FP16
fp32_model = onnx.load(fp32_path)
fp16_model = float16.convert_float_to_float16(fp32_model)
onnx.save(fp16_model, fp16_path)
print("[OK] Converted to FP16")

# Verify FP16 inference
fp16_model_loaded = onnx.load(fp16_path)
onnx.checker.check_model(fp16_model_loaded)
print("[OK] FP16 model passes ONNX checker")

sess = ort.InferenceSession(fp16_path, providers=["CPUExecutionProvider"])
inp = np.random.randn(1, 8).astype(np.float16)
out = sess.run(None, {"input": inp})[0]

# Compute expected (approximate)
with torch.no_grad():
    expected = model(torch.from_numpy(inp.astype(np.float32))).numpy()
max_diff = np.max(np.abs(out.astype(np.float32) - expected))
print(f"[OK] FP16 vs FP32 reference max diff: {max_diff:.6f} (smoke threshold: < 5.0)")
assert max_diff < 5.0, f"FP16 precision loss too high: {max_diff}"

import os
fp32_size = os.path.getsize(fp32_path)
fp16_size = os.path.getsize(fp16_path)
print(f"[OK] Model size: FP32={fp32_size}B, FP16={fp16_size}B, ratio={fp16_size/fp32_size:.2%}")

os.remove(fp32_path)
os.remove(fp16_path)
print("[OK] FP16 SMOKE TEST PASSED")
FP16SMOKE
echo "[OK] FP16 smoke test passed"
echo ""

echo "┌─────────────────────────────────────────────────┐"
echo "│  [FINAL VERIFICATION - ORT QUANT UNIT TESTS]   │"
echo "│  onnxruntime.quantization core API validation  │"
echo "│  (Primary quantization path - our main stack)  │"
echo "└─────────────────────────────────────────────────┘"
python - <<'ORTUNIT'
"""
onnxruntime.quantization Core API Unit Tests (Build-time Validation)
====================================================================
Validates the primary quantization stack: dynamic/static/FP16, QDQ/QOperator,
per-channel weights, calibration methods, and accuracy verification.
This is a focused subset of test_onnxruntime_quantization.py for build-time smoke.
"""
import sys, os, tempfile, shutil
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import numpy as np
import torch
import torch.nn as nn
import onnx
import onnxruntime as ort
from onnxruntime.quantization import (
    quantize_dynamic, quantize_static, QuantType, QuantFormat,
    CalibrationMethod, CalibrationDataReader,
)
try:
    from onnxconverter_common import float16
    HAS_FP16 = True
except ImportError:
    HAS_FP16 = False
try:
    import onnxsim
    HAS_ONNXSIM = True
except ImportError:
    HAS_ONNXSIM = False

passed = 0
failed = 0
def check(name, cond, msg=""):
    global passed, failed
    if cond:
        print(f"  ✅ {name}"); passed += 1
    else:
        print(f"  ❌ {name}: {msg}"); failed += 1

# Fixed seeds
torch.manual_seed(42); np.random.seed(42)
tmpdir = tempfile.mkdtemp()

# ── Create test models ──
class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(64,128),nn.ReLU(),nn.Linear(128,10))
    def forward(self,x): return self.net(x)

model = MLP().eval()
fp32_path = os.path.join(tmpdir, "mlp.onnx")
dyn_path = os.path.join(tmpdir, "mlp_dyn.onnx")
static_qdq_path = os.path.join(tmpdir, "mlp_qdq.onnx")
static_qop_path = os.path.join(tmpdir, "mlp_qop.onnx")
fp16_path = os.path.join(tmpdir, "mlp_fp16.onnx")

torch.onnx.export(model, torch.randn(1,64), fp32_path,
                  input_names=["input"], output_names=["output"],
                  opset_version=18, do_constant_folding=True)
if HAS_ONNXSIM:
    m = onnx.load(fp32_path); m2,ok = onnxsim.simplify(m)
    if ok: onnx.save(m2, fp32_path)
onnx.checker.check_model(onnx.load(fp32_path))
check("FP32 ONNX model export + checker", True)

# Helper: run inference with auto FP16 type adaptation
def infer(path, name, arr):
    s = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
    inp_meta = s.get_inputs()[0]
    if "float16" in inp_meta.type and arr.dtype == np.float32:
        arr = arr.astype(np.float16)
    out = s.run(None, {name: arr})[0]
    return out.astype(np.float32) if out.dtype == np.float16 else out

inp = np.random.randn(1,64).astype(np.float32)
fp32_out = infer(fp32_path, "input", inp)

# ── Test 1: Dynamic quantization (3 weight_type variants) ──
for wtype_name, wtype in [("QInt8_per_channel", QuantType.QInt8),
                            ("QUInt8_per_channel", QuantType.QUInt8)]:
    out_p = os.path.join(tmpdir, f"dyn_{wtype_name}.onnx")
    quantize_dynamic(fp32_path, out_p, weight_type=wtype, per_channel=True)
    onnx.checker.check_model(onnx.load(out_p))
    out = infer(out_p, "input", inp)
    md = np.max(np.abs(fp32_out - out))
    check(f"dynamic {wtype_name}: quantize+infer (max_diff={md:.5f})", md < 1.0, f"diff={md}")

# ── Test 2: Static QDQ quantization ──
class RandomCalib(CalibrationDataReader):
    def __init__(self, n=20):
        self.data = [{"input": np.random.randn(1,64).astype(np.float32)} for _ in range(n)]
        self.idx = 0
    def get_next(self):
        if self.idx >= len(self.data): return None
        d = self.data[self.idx]; self.idx += 1; return d
    def rewind(self): self.idx = 0

calib = RandomCalib(30)
quantize_static(fp32_path, static_qdq_path, calib, quant_format=QuantFormat.QDQ,
                per_channel=True, activation_type=QuantType.QInt8, weight_type=QuantType.QInt8,
                calibrate_method=CalibrationMethod.MinMax)
onnx.checker.check_model(onnx.load(static_qdq_path))
qdq_out = infer(static_qdq_path, "input", inp)
md = np.max(np.abs(fp32_out - qdq_out))
check(f"static QDQ MinMax: quantize+infer (max_diff={md:.5f})", md < 2.0, f"diff={md}")

# Verify QDQ nodes exist
m = onnx.load(static_qdq_path)
qdq_count = sum(1 for n in m.graph.node if n.op_type in ("QuantizeLinear","DequantizeLinear"))
check(f"static QDQ: QuantizeLinear/DequantizeLinear nodes exist ({qdq_count})", qdq_count > 0)

# ── Test 3: Static QOperator quantization ──
calib.rewind()
quantize_static(fp32_path, static_qop_path, calib, quant_format=QuantFormat.QOperator,
                per_channel=True, activation_type=QuantType.QUInt8, weight_type=QuantType.QInt8,
                calibrate_method=CalibrationMethod.MinMax)
onnx.checker.check_model(onnx.load(static_qop_path))
qop_out = infer(static_qop_path, "input", inp)
md = np.max(np.abs(fp32_out - qop_out))
check(f"static QOperator QUInt8: quantize+infer (max_diff={md:.5f})", md < 2.0, f"diff={md}")

# ── Test 4: FP16 conversion ──
if HAS_FP16:
    fp16_model = float16.convert_float_to_float16(onnx.load(fp32_path))
    onnx.save(fp16_model, fp16_path)
    onnx.checker.check_model(onnx.load(fp16_path))
    fp16_out = infer(fp16_path, "input", inp)
    md = np.max(np.abs(fp32_out - fp16_out))
    check(f"FP16 conversion: convert+infer (max_diff={md:.6f})", md < 0.01, f"diff={md}")
    fp32_size = os.path.getsize(fp32_path); fp16_size = os.path.getsize(fp16_path)
    ratio = fp16_size / fp32_size
    check(f"FP16 size ratio: {ratio:.1%} (expected ~50%)", 0.4 < ratio < 0.8, f"ratio={ratio:.1%}")
else:
    check("FP16 conversion", False, "onnxconverter_common not available")

# ── Test 5: File size compression ──
fp32_size = os.path.getsize(fp32_path)
dyn_size = os.path.getsize(os.path.join(tmpdir, "dyn_QInt8_per_channel.onnx"))
check(f"INT8 dynamic model is smaller than FP32 ({dyn_size}/{fp32_size} bytes)", dyn_size < fp32_size)

# ── Cleanup ──
shutil.rmtree(tmpdir, ignore_errors=True)

# ── Summary ──
print(f"\n  ─────────────────────────────────────")
print(f"  ORT QUANTIZATION TESTS: {passed} passed, {failed} failed")
print(f"  ─────────────────────────────────────")
if failed > 0:
    print("  ❌ ORT QUANTIZATION TESTS FAILED"); sys.exit(1)
else:
    print("  ✅ ORT QUANTIZATION TESTS PASSED")
ORTUNIT
echo "[OK] onnxruntime.quantization unit tests passed"
echo ""

echo "┌─────────────────────────────────────────────────┐"
echo "│  [REQUIRED] onnx_quantize_kit REGRESSION TESTS │"
echo "│  Full pipeline: quantize→accuracy→benchmark    │"
echo "└─────────────────────────────────────────────────┘"
mkdir -p /tmp/scripts
cp -r /opt/devcontainer-scripts/* /tmp/scripts/
python /tmp/scripts/test_ort_quantization_regression.py
echo "[OK] onnx_quantize_kit regression tests passed"
echo ""

echo "┌─────────────────────────────────────────────────┐"
echo "│  [OPTIONAL] INC 3.x UNIT TESTS                 │"
echo "│  Neural Compressor 3.x (PyTorch-only extension)│"
echo "│  Skipped if neural-compressor not installed    │"
echo "└─────────────────────────────────────────────────┘"
if python -c "import neural_compressor" 2>/dev/null; then
python - <<'NCUNIT'
"""
Neural Compressor 3.x API Unit Tests (Strict Mode)
==================================================
Runs comprehensive validation of INC 3.x APIs for the onnx-quantized variant.
This is the strict-mode version of test_neural_compressor.py.

Tests:
1. Package version >= 3.0
2. 3.x PyTorch API imports (RTNConfig, quantize, prepare, convert)
3. Weight-only quantization smoke test (RTN 4bit on PyTorch MLP)
4. 2.x legacy API deprecation verification (expected behavior)
5. onnxruntime.quantization primary path unaffected
"""
import sys
import os
import tempfile
import shutil
import traceback

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
passed = 0
failed = 0

def check(name, condition, msg=""):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}: {msg}")
        failed += 1

# ── Test 1: Package and version ──
import neural_compressor
nc_ver = neural_compressor.__version__
nc_tuple = tuple(map(int, nc_ver.split(".")[:2]))
check(f"neural_compressor installed (v{nc_ver})", nc_tuple >= (3, 0),
      f"Expected >= 3.0, got {nc_ver}")

# ── Test 2: 3.x PyTorch API imports ──
import torch
import torch.nn as nn
from neural_compressor.torch.quantization import RTNConfig, quantize, prepare, convert
check("RTNConfig (3.x weight-only config) importable", True)
check("quantize() (one-shot API) importable", True)
check("prepare()/convert() (standard workflow) importable", True)

# Optional advanced configs (may require extra dependencies)
optional_configs = ["AWQConfig", "GPTQConfig"]
for cfg in optional_configs:
    try:
        exec(f"from neural_compressor.torch.quantization import {cfg}")
        print(f"  ✅ {cfg} (advanced algorithm) available")
    except (ImportError, AttributeError):
        print(f"  ⏭️  {cfg} not available (may need extra dependencies)")

# ── Test 3: Weight-only quantization smoke test ──
tmpdir = tempfile.mkdtemp()
try:
    class TinyMLP(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(64, 128), nn.ReLU(), nn.Linear(128, 10)
            )
        def forward(self, x): return self.net(x)

    model = TinyMLP().eval()
    inp = torch.randn(1, 64)
    with torch.no_grad():
        fp32_out = model(inp)
    check("FP32 model forward pass", fp32_out.shape == (1, 10))

    # RTN 4bit weight-only quantization
    woq_cfg = RTNConfig(bits=4, group_size=32)
    qmodel = quantize(model, quant_config=woq_cfg, example_inputs=inp)
    check("RTN 4bit weight-only quantize() succeeded", qmodel is not None)

    with torch.no_grad():
        q_out = qmodel(inp)
    check("Quantized model forward pass", q_out.shape == (1, 10))

    max_diff = torch.max(torch.abs(fp32_out - q_out)).item()
    check(f"4bit quantization accuracy (max_diff={max_diff:.4f} < 1.0)",
          max_diff < 1.0, f"diff={max_diff}")
    print(f"     FP32 vs INT4 max_diff: {max_diff:.6f}")
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)

# ── Test 4: 2.x legacy API deprecation (expected in 3.x) ──
print("  ℹ️  Verifying 2.x legacy API behavior (expected to be unavailable/deprecated)...")
legacy_imports = [
    ("neural_compressor.config.PostTrainingQuantConfig",
     "PostTrainingQuantConfig (2.x unified config)"),
]
for path, desc in legacy_imports:
    try:
        exec(f"from {path} import *")
        print(f"  ⚠️  {desc}: still available via compatibility layer")
    except (ImportError, AttributeError):
        print(f"  ✅ {desc}: not available in 3.x (expected - API was refactored)")

# ── Test 5: Primary ONNX quantization path still works ──
import numpy as np
import onnx
import onnxsim
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic, QuantType

check("onnxruntime.quantization primary path importable", True)
tmpdir = tempfile.mkdtemp()
try:
    class LinModel(nn.Module):
        def __init__(self): super().__init__(); self.fc = nn.Linear(8,4)
        def forward(self,x): return self.fc(x)
    m = LinModel().eval()
    p1 = os.path.join(tmpdir, "t.onnx")
    p2 = os.path.join(tmpdir, "tq.onnx")
    torch.onnx.export(m, torch.randn(1,8), p1, input_names=["i"], output_names=["o"], opset_version=18)
    mm = onnx.load(p1); mm2,_ = onnxsim.simplify(mm); onnx.save(mm2,p1)
    quantize_dynamic(p1, p2, weight_type=QuantType.QInt8)
    sess = ort.InferenceSession(p2, providers=["CPUExecutionProvider"])
    o = sess.run(None, {"i": np.random.randn(1,8).astype(np.float32)})[0]
    check("ONNX dynamic quantize + inference (primary path)", o.shape == (1,4))
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)

# ── Summary ──
print(f"\n  ─────────────────────────────────────")
print(f"  INC 3.x UNIT TESTS: {passed} passed, {failed} failed")
print(f"  ─────────────────────────────────────")
if failed > 0:
    print("  ❌ INC 3.x UNIT TESTS FAILED")
    sys.exit(1)
else:
    print("  ✅ INC 3.x UNIT TESTS PASSED")
NCUNIT
echo "[OK] Neural Compressor 3.x unit tests completed"
else
echo "[SKIP] Neural Compressor not installed - skipping INC unit tests (expected)"
echo "[SKIP] ONNX quantization uses onnxruntime.quantization natively (no INC needed)"
fi
echo ""

_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.onnx-quantized-variant-build-timer | cut -d= -f2)
_OQS1=$(grep '^OQS1=' /tmp/.onnx-quantized-variant-build-timer | cut -d= -f2)
_OQS2=$(grep '^OQS2=' /tmp/.onnx-quantized-variant-build-timer | cut -d= -f2)
_OT1=$((_OQS1 - _START))
_OT2=$((_OQS2 - _OQS1))
_OT3=$_ELAPSED
_OTOTAL=$((_NOW - _START))
echo "[TIMER] Stage 3/3 (metadata+quantization smoke) took ${_ELAPSED}s | ONNX-Quantized variant cumulative: ${_OTOTAL}s"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  BUILD TIMING SUMMARY (ONNX-Quantized Variant - 3 Add Stages)║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  Stage 1/3  base verification         %5ds               ║\n" $_OT1
printf "║  Stage 2/3  install quantization      %5ds               ║\n" $_OT2
printf "║  Stage 3/3  smoke test+metadata       %5ds               ║\n" $_OT3
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  ONNX-QUANTIZED VARIANT TOTAL (add-on) %5ds               ║\n" $_OTOTAL
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
rm -f /tmp/.onnx-quantized-variant-build-timer
echo "########################################################################"
echo "# ONNX-QUANTIZED VARIANT BUILD COMPLETE!"
echo "# Quantization modes: dynamic INT8, static INT8, QDQ, FP16, Calibration"
if python -c "import neural_compressor" 2>/dev/null; then
echo "# Neural Compressor: available (optional PyTorch extension)"
else
echo "# Neural Compressor: not installed (optional, pip install neural-compressor for PyTorch quantization)"
fi
echo "#"
echo "# Quick start:"
echo "#   from onnxruntime.quantization import quantize_dynamic, QuantType"
echo "#   quantize_dynamic('model.onnx', 'model_int8.onnx', weight_type=QuantType.QInt8)"
echo "########################################################################"
echo ""
STAGE3_EOF
