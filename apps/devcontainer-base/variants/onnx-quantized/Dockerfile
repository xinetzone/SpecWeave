# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - ONNX Quantized Variant Dockerfile
# Project: SpecWeave Full-featured Development Container - ONNX Model Quantization Toolkit
# Base: devcontainer-base:onnx-pytorch-${BASE_TAG} (PyTorch CPU + ONNX + ONNX Runtime + LLVM)
# Toolchain: ONNX Runtime quantization + onnxconverter-common + onnxruntime-tools + Intel Neural Compressor
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
#   Stage 2/3: Install quantization packages (onnxruntime-tools, neural-compressor, etc.)
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
LABEL description="DevContainer onnx-quantized variant with ONNX quantization toolkit (INT8/FP16 dynamic/static quantization + Intel Neural Compressor)"
LABEL variant="onnx-quantized"
LABEL quantization="onnxruntime,neural-compressor,int8,fp16"

ENV CONDA_DIR=/opt/conda

ENV PATH=/opt/conda/bin:${PATH}

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
# 包含：onnxruntime.quantization (built-in), onnxconverter-common,
#       onnxruntime-tools, neural-compressor (Intel INC), onnxsim
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    <<'STAGE2_EOF'
echo ""
echo "########################################################################"
echo "# [ONNX-QUANTIZED VARIANT STAGE 2/3] Install Quantization Toolkit"
echo "# Packages:"
echo "#   - onnxconverter-common (ONNX model conversion utilities)"
echo "#   - onnxruntime-tools    (ONNX Runtime quantization tools, including calibrators)"
echo "#   - neural-compressor    (Intel Neural Compressor: PTQ/QAT, INT8/FP16/BF16)"
echo "#   - onnxsim              (ONNX model simplification, pre-quantization)"
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
    onnxruntime-tools \
    neural-compressor \
    onnxsim
echo ""
echo "[OK] Quantization toolkit installation complete"
echo ""

echo "[INFO] Installed package versions:"
echo "  - onnxruntime.quantization: $(python -c 'from onnxruntime.quantization import quantize_dynamic, QuantType; print("available (dynamic+static QDQ)")' 2>&1)"
echo "  - onnxconverter-common: $(python -c 'import onnxconverter_common; print(onnxconverter_common.__version__)' 2>&1)"
echo "  - onnxruntime-tools: $(python -c 'from onnxruntime_tools import optimizer; print("available")' 2>&1)"
echo "  - neural-compressor: $(python -c 'import neural_compressor; print(neural_compressor.__version__)' 2>&1)"
echo "  - onnxsim: $(python -c 'import onnxsim; print(onnxsim.__version__)' 2>&1)"
echo ""

echo "[ACTION] Setting permissions for devuser..."
chown -R root:root /opt/conda
chmod -R a+rX /opt/conda
find /opt/conda/bin -type f -executable -exec chmod a+x {} \; 2>/dev/null || true
echo "[OK] Permissions verified"
echo ""

_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.onnx-quantized-variant-build-timer | cut -d= -f2)
_TOTAL=$((_NOW - _START))
echo "OQS2=$_NOW" >> /tmp/.onnx-quantized-variant-build-timer
echo "[TIMER] Stage 2/3 (install quantization toolkit) took ${_ELAPSED}s | ONNX-Quantized variant cumulative: ${_TOTAL}s"
echo '[OK] Stage 2 complete'
STAGE2_EOF

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
NC_VERSION=$(python -c "import neural_compressor;print(neural_compressor.__version__)" 2>/dev/null || echo "unknown")
OCC_VERSION=$(python -c "import onnxconverter_common;print(onnxconverter_common.__version__)" 2>/dev/null || echo "unknown")
ONNXSIM_VERSION=$(python -c "import onnxsim;print(onnxsim.__version__)" 2>/dev/null || echo "unknown")
printf '%s\n' \
    "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "VARIANT=onnx-quantized" \
    "VARIANT_DESCRIPTION=ONNX model quantization toolkit (INT8/FP16 dynamic/static/QDQ/QAT)" \
    "BASE_IMAGE=devcontainer-base:onnx-pytorch-\${BASE_TAG}" \
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
    "PACKAGES_INSTALLED=torch,torchvision,onnx,onnxruntime,onnx-simplifier,onnxoptimizer,onnxconverter-common,onnxruntime-tools,neural-compressor,onnxsim" \
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
python -c "from neural_compressor import quantization; print('[OK] neural_compressor imports')"
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
su - devuser -c "python -c 'from onnxruntime.quantization import quantize_dynamic; print(\"quantize_dynamic accessible\")'" && echo "[OK] devuser can access quantization tools"
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
import onnxruntime as ort
import numpy as np
import os
from onnxruntime.quantization import quantize_dynamic, QuantType

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
                  opset_version=13, do_constant_folding=True)
print(f"[OK] Exported FP32 ONNX model: {onnx_path}")

# 2) Dynamic quantization (INT8 weights)
quantize_dynamic(
    model_input=onnx_path,
    model_output=quant_path,
    weight_type=QuantType.QInt8,
)
print(f"[OK] Dynamic INT8 quantization -> {quant_path}")

# 3) Verify quantized model loads and runs
quant_model = onnx.load(quant_path)
onnx.checker.check_model(quant_model)
print("[OK] Quantized model passes ONNX checker")

sess_fp32 = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
sess_int8 = ort.InferenceSession(quant_path, providers=["CPUExecutionProvider"])

inp = np.random.randn(1, 10).astype(np.float32)
out_fp32 = sess_fp32.run(None, {"input": inp})[0]
out_int8 = sess_int8.run(None, {"input": inp})[0]

max_diff = np.max(np.abs(out_fp32 - out_int8))
print(f"[OK] FP32 vs INT8 max diff: {max_diff:.6f} (expected < 0.1 for linear model)")
assert max_diff < 0.5, f"Quantization accuracy loss too high: {max_diff}"

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
echo "# Intel Neural Compressor ${NC_VERSION} available for advanced quantization workflows"
echo "#"
echo "# Quick start:"
echo "#   from onnxruntime.quantization import quantize_dynamic, QuantType"
echo "#   quantize_dynamic('model.onnx', 'model_int8.onnx', weight_type=QuantType.QInt8)"
echo "########################################################################"
echo ""
STAGE3_EOF
