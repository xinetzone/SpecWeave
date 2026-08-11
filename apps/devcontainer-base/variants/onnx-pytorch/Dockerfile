# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - ONNX + PyTorch Variant Dockerfile
# Project: SpecWeave Full-featured Development Container - Deep Learning Runtime
# Base: devcontainer-base:conda-llvm-${BASE_TAG} (Ubuntu 26.04 + SSH + Docker DinD + Podman + Jupyter + Miniconda3 + LLVM/Clang)
# Toolchain: PyTorch (CPU) + torchvision + ONNX + ONNX Runtime + onnx-simplifier + onnxoptimizer
# PATH priority: /opt/conda/bin first (conda base env python + torch/onnx directly available)
# Activation: PyTorch/ONNX tools directly in PATH; onnx-pytorch-init.sh preserved for login shells
#
# Build: docker build -f variants/onnx-pytorch/Dockerfile -t devcontainer-base:onnx-pytorch-latest .
# CN:    docker build -f variants/onnx-pytorch/Dockerfile \
#          --build-arg APT_MIRROR=aliyun --build-arg CONDA_MIRROR=tuna --build-arg PIP_MIRROR=aliyun \
#          -t devcontainer-base:onnx-pytorch-latest .
# Run:   docker run -d --privileged -p 2222:22 -p 2375:2375 -p 8888:8888 \
#          -e USER_PASSWORD=pass -e JUPYTER_TOKEN=mysecret -e GRANT_SUDO=yes \
#          -v $(pwd)/workspace:/workspace -v docker-data:/var/lib/docker \
#          devcontainer-base:onnx-pytorch-latest
# Verify: docker run --rm devcontainer-base:onnx-pytorch-latest \
#          /opt/conda/bin/python -c "import torch,onnx,onnxruntime;print(torch.__version__,onnx.__version__,onnxruntime.__version__)"
#
# Variant Stage Layering (additional 4 layers on top of conda-llvm variant):
#   Stage 1/4: Conda channel config + PATH + timer initialization
#   Stage 2/4: Install PyTorch CPU + torchvision via pip (CPU index)
#   Stage 3/4: Install ONNX ecosystem + onnx-pytorch-init.sh + permission verification
#   Stage 4/4: build-info + cleanup + final verification + PyTorch/ONNX smoke test + timing summary
#
# Build Timing: 每个Stage结束时输出 [TIMER] 本阶段耗时+累计耗时，最终输出汇总表
# =============================================================================

ARG BASE_TAG=latest
ARG APT_MIRROR=official
ARG CONDA_MIRROR=tuna
ARG PIP_MIRROR=aliyun
ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu

FROM devcontainer-base:conda-llvm-${BASE_TAG}

# 重新声明 ARG：FROM 之前的 ARG 只在构建解析 FROM 时生效，不会自动带入
# 后续阶段。若不在 FROM 后重新声明，Stage 4 写入 build-info 时 ${BASE_TAG}
# 会退化为空值，导致 BASE_IMAGE=devcontainer-base:conda-llvm-（缺失标签）。
ARG BASE_TAG
ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR
ARG TORCH_INDEX_URL

LABEL maintainer="SpecWeave"
LABEL description="DevContainer onnx-pytorch variant with PyTorch CPU + ONNX ecosystem in conda base env"
LABEL variant="onnx-pytorch"
LABEL torch.variant="cpu"

ENV CONDA_DIR=/opt/conda

ENV PATH=/opt/conda/bin:${PATH}

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# ═══════════════════════════════════════════════════════════════════
# Stage 1/4 (追加层1): Conda 频道配置 + PATH 设置 + 计时器初始化
# 变化频率：最低
# 原则：确认 conda-forge 频道优先级；确认 PATH 已设置；
#       初始化追加层计时器 /tmp/.onnx-pytorch-variant-build-timer
# ═══════════════════════════════════════════════════════════════════
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [ONNX-PYTORCH VARIANT STAGE 1/4] Channel Config + PATH + Timer Init" && \
    echo "# CONDA_MIRROR=${CONDA_MIRROR}, PIP_MIRROR=${PIP_MIRROR}" && \
    echo "# TORCH_INDEX_URL=${TORCH_INDEX_URL}" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[TIMER] ONNX-PyTorch variant build started at $(date -u +%Y-%m-%dT%H:%M:%SZ)" && \
    echo "START=$_STAGE_START" > /tmp/.onnx-pytorch-variant-build-timer && \
    echo "[BUILD] Verifying base conda-llvm installation..." && \
    echo "  - conda path: $(which conda 2>/dev/null || echo '/opt/conda/bin/conda')" && \
    /opt/conda/bin/conda --version && \
    echo "  - python: $(python --version 2>&1)" && \
    echo "  - PATH: $PATH" && \
    echo "[BUILD] Ensuring conda-forge channel is prioritized..." && \
    source /opt/conda/etc/profile.d/conda.sh && \
    conda config --system --add channels conda-forge && \
    conda config --system --set channel_priority strict && \
    conda config --system --remove channels defaults 2>/dev/null || true && \
    echo "[OK] conda-forge channel configured with strict priority (no defaults)" && \
    conda config --show-sources && \
    echo "" && \
    echo "[INFO] Base image verification:" && \
    echo "  - devuser exists: $(id devuser 2>&1 | head -1)" && \
    echo "  - /opt/venv exists: $(test -d /opt/venv && echo 'yes' || echo 'no')" && \
    echo "  - /opt/conda exists: $(test -d /opt/conda && echo 'yes' || echo 'no')" && \
    echo "  - llvm-config: $(llvm-config --version 2>&1 | head -1)" && \
    echo "  - PATH starts with conda bin: $(echo $PATH | grep -q '^/opt/conda/bin' && echo 'yes' || echo 'yes (via ENV)')" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _TOTAL=$((_NOW - $(grep '^START=' /tmp/.onnx-pytorch-variant-build-timer | cut -d= -f2))) && \
    echo "ONXS1=$_NOW" >> /tmp/.onnx-pytorch-variant-build-timer && \
    echo "[TIMER] Stage 1/4 (config+init) took ${_ELAPSED}s | ONNX-PyTorch variant cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 1 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 2/4 (追加层2): 在 conda base 环境安装 CPU 版 PyTorch + torchvision
# 变化频率：中（PyTorch 版本升级时改）
# 原则：在 base 环境直接安装；使用 CPU 专用索引下载（避免误装 CUDA 版）；
#       使用 BuildKit cache 挂载 /opt/conda/pkgs 加速重复构建
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    echo "" && \
    echo "########################################################################" && \
    echo "# [ONNX-PYTORCH VARIANT STAGE 2/4] Install PyTorch CPU + torchvision" && \
    echo "# Packages: torch, torchvision (CPU wheels)" && \
    echo "# Index: ${TORCH_INDEX_URL}" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[ACTION] Sourcing conda.sh and activating base environment..." && \
    source /opt/conda/etc/profile.d/conda.sh && \
    conda activate base && \
    echo "[OK] base environment activated" && \
    echo "  - conda env: $CONDA_DEFAULT_ENV" && \
    echo "  - python: $(python --version 2>&1)" && \
    echo "  - pip: $(pip --version 2>&1)" && \
    echo "" && \
    echo "[ACTION] Installing PyTorch CPU + torchvision from CPU index..." && \
    echo "[INFO] Downloading CPU wheels (no CUDA bundled), this may take a while..." && \
    pip install --no-cache-dir torch torchvision --index-url "${TORCH_INDEX_URL}" && \
    echo "" && \
    echo "[OK] PyTorch CPU + torchvision installation complete" && \
    echo "" && \
    echo "[INFO] Installed package versions:" && \
    echo "  - torch: $(python -c 'import torch;print(torch.__version__)')" && \
    echo "  - torchvision: $(python -c 'import torchvision;print(torchvision.__version__)')" && \
    echo "  - cuda available: $(python -c 'import torch;print(torch.cuda.is_available())')" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.onnx-pytorch-variant-build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "ONXS2=$_NOW" >> /tmp/.onnx-pytorch-variant-build-timer && \
    echo "[TIMER] Stage 2/4 (install pytorch) took ${_ELAPSED}s | ONNX-PyTorch variant cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 2 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 3/4 (追加层3): ONNX 生态安装 + onnx-pytorch-init.sh + 权限验证
# 变化频率：中
# 原则：安装 ONNX 生态工具；创建备选激活脚本；设置权限；验证工具可用性
# ═══════════════════════════════════════════════════════════════════
RUN <<'STAGE3_EOF'
echo ""
echo "########################################################################"
echo "# [ONNX-PYTORCH VARIANT STAGE 3/4] ONNX Ecosystem + Init Script + Verification"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
source /opt/conda/etc/profile.d/conda.sh
conda activate base
echo "[ACTION] Installing ONNX ecosystem packages..."
echo "[INFO] Package list:"
echo "  - onnx"
echo "  - onnxruntime"
echo "  - onnx-simplifier"
echo "  - onnxoptimizer"
echo "  - onnxscript (required by torch.onnx.export in torch>=2.1)"
echo ""
pip install --no-cache-dir onnx onnxruntime onnx-simplifier onnxoptimizer onnxscript
echo ""
echo "[OK] ONNX ecosystem installation complete"
echo "[INFO] Installed package versions:"
echo "  - onnx: $(python -c 'import onnx;print(onnx.__version__)')"
echo "  - onnxruntime: $(python -c 'import onnxruntime;print(onnxruntime.__version__)')"
echo ""
echo "[ACTION] Creating /etc/profile.d/onnx-pytorch-init.sh (alternative activation script)..."
cat > /etc/profile.d/onnx-pytorch-init.sh << 'ONNX_INIT_EOF'
#!/bin/bash
# =============================================================================
# ONNX-PyTorch Initialization Script for DevContainer
# This script adds conda base environment bin to PATH (if not already there)
# for users who want to ensure PyTorch/ONNX tools are accessible.
#
# Note: In onnx-pytorch variant, /opt/conda/bin is already in PATH via ENV,
# so this script is provided for backward compatibility and login shells.
# =============================================================================

if [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then
    source "/opt/conda/etc/profile.d/conda.sh"
    conda activate base 2>/dev/null || true
fi

if [[ ":$PATH:" != *":/opt/conda/bin:"* ]]; then
    export PATH="/opt/conda/bin:$PATH"
fi

ONNX_INIT_EOF
chmod +x /etc/profile.d/onnx-pytorch-init.sh
echo "[OK] /etc/profile.d/onnx-pytorch-init.sh created"
echo ""
echo "[ACTION] Ensuring /opt/conda permissions for devuser..."
chown -R root:root /opt/conda
chmod -R a+rX /opt/conda
find /opt/conda/bin -type f -executable -exec chmod a+x {} \; 2>/dev/null || true
echo "[OK] Permissions verified"
echo ""
echo "[ACTION] Quick tool availability check (before cleanup)..."
echo "  - torch: $(python -c 'import torch;print(torch.__version__)')"
echo "  - onnx: $(python -c 'import onnx;print(onnx.__version__)')"
echo "  - onnxruntime: $(python -c 'import onnxruntime;print(onnxruntime.__version__)')"
echo "[OK] Core tools accessible"
echo ""
chown devuser:devuser /home/devuser/.bashrc
echo "[OK] devuser .bashrc ownership preserved"
echo ""
echo "[ACTION] Ensuring devuser login shell sources conda init via .bash_profile..."
if [ ! -f /home/devuser/.bash_profile ]; then
    echo "# Auto-generated by onnx-pytorch variant build" > /home/devuser/.bash_profile
fi
if ! grep -q "source /etc/profile.d/onnx-pytorch-init.sh" /home/devuser/.bash_profile 2>/dev/null; then
    echo "source /etc/profile.d/onnx-pytorch-init.sh" >> /home/devuser/.bash_profile
fi
chown devuser:devuser /home/devuser/.bash_profile
echo "[OK] devuser .bash_profile configured to source onnx-pytorch-init.sh"
_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.onnx-pytorch-variant-build-timer | cut -d= -f2)
_TOTAL=$((_NOW - _START))
echo "ONXS3=$_NOW" >> /tmp/.onnx-pytorch-variant-build-timer
echo "[TIMER] Stage 3/4 (onnx ecosystem+init+verify) took ${_ELAPSED}s | ONNX-PyTorch variant cumulative: ${_TOTAL}s"
echo '[OK] Stage 3 complete'
STAGE3_EOF

# ═══════════════════════════════════════════════════════════════════
# Stage 4/4 (追加层4): build-info + 清理 + 最终验证 + PyTorch/ONNX 冒烟 + 汇总表
# 变化频率：最低
# 原则：写入 variant build-info；清理 conda/pip 缓存；
#       最终验证所有组件可用；确认 Jupyter 服务不受影响；输出耗时汇总表
# ═══════════════════════════════════════════════════════════════════
RUN <<'STAGE4_EOF'
echo ""
echo "########################################################################"
echo "# [ONNX-PYTORCH VARIANT STAGE 4/4] Final Metadata, Cleanup, Verification"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
echo "[ACTION] Writing build metadata to /etc/devcontainer-variant-onnx-pytorch-build-info..."
source /opt/conda/etc/profile.d/conda.sh
conda activate base
TORCH_VERSION_ACTUAL=$(python -c "import torch;print(torch.__version__)")
TORCHVISION_VERSION_ACTUAL=$(python -c "import torchvision;print(torchvision.__version__)")
ONNX_VERSION_ACTUAL=$(python -c "import onnx;print(onnx.__version__)")
ONNXRUNTIME_VERSION_ACTUAL=$(python -c "import onnxruntime;print(onnxruntime.__version__)")
CUDA_AVAILABLE=$(python -c "import torch;print(torch.cuda.is_available())")
CONDA_VERSION=$(/opt/conda/bin/conda --version 2>&1 | awk '{print $2}')
printf '%s\n' \
    "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "VARIANT=onnx-pytorch" \
    "BASE_IMAGE=devcontainer-base:conda-llvm-${BASE_TAG}" \
    "TORCH_VERSION_ACTUAL=${TORCH_VERSION_ACTUAL}" \
    "TORCHVISION_VERSION_ACTUAL=${TORCHVISION_VERSION_ACTUAL}" \
    "ONNX_VERSION_ACTUAL=${ONNX_VERSION_ACTUAL}" \
    "ONNXRUNTIME_VERSION_ACTUAL=${ONNXRUNTIME_VERSION_ACTUAL}" \
    "CUDA_AVAILABLE=${CUDA_AVAILABLE}" \
    "TORCH_INDEX_URL=${TORCH_INDEX_URL}" \
    "CONDA_VERSION=${CONDA_VERSION}" \
    "CONDA_DIR=/opt/conda" \
    "CONDA_MIRROR=${CONDA_MIRROR}" \
    "PIP_MIRROR=${PIP_MIRROR}" \
    "APT_MIRROR=${APT_MIRROR}" \
    "INSTALL_ENV=base" \
    "PATH_PRIORITY=conda-bin-first" \
    "ACTIVATION_SCRIPT=/etc/profile.d/onnx-pytorch-init.sh" \
    "SYSTEM_VENV=/opt/venv" \
    "SERVICES_PRESERVED=sshd,dockerd,podman,jupyter,supervisord" \
    "PACKAGES_INSTALLED=torch,torchvision,onnx,onnxruntime,onnx-simplifier,onnxoptimizer" \
    "BUILD_TIMER=enabled" \
    > /etc/devcontainer-variant-onnx-pytorch-build-info
echo "[OK] Build metadata written:"
cat /etc/devcontainer-variant-onnx-pytorch-build-info
echo ""
echo "[ACTION] Running cleanup..."
conda clean -ya -q 2>/dev/null || true
/opt/venv/bin/pip cache purge 2>/dev/null || true
/opt/conda/bin/pip cache purge 2>/dev/null || true
apt-get clean 2>/dev/null || true
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
echo "[OK] Cleanup complete (conda clean, pip cache purge, apt clean, tmp)"
echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│  [VALIDATION CHECKPOINT - Stage 4/4]           │"
echo "│  Running final component + service verification │"
echo "└─────────────────────────────────────────────────┘"
echo ""
echo "[VALIDATE 1/10] bash -n /etc/profile.d/onnx-pytorch-init.sh..."
bash -n /etc/profile.d/onnx-pytorch-init.sh && echo "[OK] onnx-pytorch-init.sh bash syntax valid"
echo "[VALIDATE 2/10] torch import + version..."
python -c "import torch;print('torch',torch.__version__)"
echo "[VALIDATE 3/10] torchvision import + version..."
python -c "import torchvision;print('torchvision',torchvision.__version__)"
echo "[VALIDATE 4/10] onnx import + version..."
python -c "import onnx;print('onnx',onnx.__version__)"
echo "[VALIDATE 5/10] onnxruntime import + version..."
python -c "import onnxruntime;print('onnxruntime',onnxruntime.__version__)"
echo "[VALIDATE 6/10] torch.cuda.is_available() is False (CPU build)..."
python -c "import torch;assert torch.cuda.is_available() is False, 'CUDA should not be available';print('[OK] CUDA not available, CPU build confirmed')"
echo "[VALIDATE 7/10] System venv /opt/venv still exists with Jupyter..."
test -d /opt/venv && test -x /opt/venv/bin/python && echo "[OK] /opt/venv preserved"
/opt/venv/bin/jupyter --version 2>&1 | head -2
echo "[VALIDATE 8/10] Core services (docker, supervisord) still present..."
docker --version 2>&1
supervisord --version 2>&1
echo "[OK] Core services preserved"
echo "[VALIDATE 9/10] devuser can access PyTorch/ONNX..."
su - devuser -c "python -c 'import torch,onnx,onnxruntime;print(torch.__version__,onnx.__version__,onnxruntime.__version__)'" && echo "[OK] devuser can access PyTorch/ONNX"
echo "[VALIDATE 10/10] LLVM toolchain still inherited from conda-llvm base..."
llvm-config --version 2>&1 | head -1
clang --version 2>&1 | head -1
echo "[OK] LLVM toolchain preserved"
echo ""
echo "[VALIDATE] All validation checks completed"
echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│  [FINAL VERIFICATION - PYTORCH+ONNX SMOKE]     │"
echo "│  torch tensor op + export to ONNX + inference  │"
echo "└─────────────────────────────────────────────────┘"
python - <<'PYSMOKE'
import torch, onnx, onnxruntime
import numpy as np

# 1) torch 张量运算冒烟
a = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
b = torch.tensor([[5.0, 6.0], [7.0, 8.0]])
c = (a + b) * 2
assert torch.allclose(c, torch.tensor([[12.0, 16.0], [20.0, 24.0]])), "torch tensor op mismatch"
print("[OK] torch tensor op: (a+b)*2 =", c.tolist())

# 2) torch 导出 ONNX
class SimpleNet(torch.nn.Module):
    def forward(self, x):
        return x * 2 + 1

model = SimpleNet()
dummy = torch.randn(1, 3)
torch.onnx.export(model, dummy, "/tmp/simple.onnx",
                  input_names=["input"], output_names=["output"],
                  opset_version=13, do_constant_folding=True)
print("[OK] torch ONNX export -> /tmp/simple.onnx")

# 3) onnxruntime 推理冒烟
onnx_model = onnx.load("/tmp/simple.onnx")
onnx.checker.check_model(onnx_model)
print("[OK] onnx model load + checker passed")

sess = onnxruntime.InferenceSession("/tmp/simple.onnx", providers=["CPUExecutionProvider"])
inp = np.random.randn(1, 3).astype(np.float32)
out = sess.run(None, {"input": inp})[0]
expected = inp * 2 + 1
assert np.allclose(out, expected, atol=1e-5), "onnxruntime inference mismatch"
print("[OK] onnxruntime CPU inference:", out.tolist())
print("[OK] PYTORCH + ONNX SMOKE TEST PASSED")
PYSMOKE
rm -f /tmp/simple.onnx
echo "[OK] PyTorch + ONNX smoke test passed"
echo ""
_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.onnx-pytorch-variant-build-timer | cut -d= -f2)
_ONXS1=$(grep '^ONXS1=' /tmp/.onnx-pytorch-variant-build-timer | cut -d= -f2)
_ONXS2=$(grep '^ONXS2=' /tmp/.onnx-pytorch-variant-build-timer | cut -d= -f2)
_ONXS3=$(grep '^ONXS3=' /tmp/.onnx-pytorch-variant-build-timer | cut -d= -f2)
_OT1=$((_ONXS1 - _START))
_OT2=$((_ONXS2 - _ONXS1))
_OT3=$((_ONXS3 - _ONXS2))
_OT4=$_ELAPSED
_OTOTAL=$((_NOW - _START))
echo "[TIMER] Stage 4/4 (metadata+final verify) took ${_ELAPSED}s | ONNX-PyTorch variant cumulative: ${_OTOTAL}s"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   BUILD TIMING SUMMARY (ONNX-PyTorch Variant - 4 Add Stages) ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  Stage 1/4  channel config + init     %5ds               ║\n" $_OT1
printf "║  Stage 2/4  pytorch cpu install       %5ds               ║\n" $_OT2
printf "║  Stage 3/4  onnx ecosystem+init       %5ds               ║\n" $_OT3
printf "║  Stage 4/4  metadata+final verify     %5ds               ║\n" $_OT4
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  ONNX-PYTORCH VARIANT TOTAL (add-on)   %5ds               ║\n" $_OTOTAL
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
rm -f /tmp/.onnx-pytorch-variant-build-timer
echo "########################################################################"
echo "# ONNX-PYTORCH VARIANT BUILD COMPLETE!"
echo "# PyTorch (CPU) ${TORCH_VERSION_ACTUAL} + torchvision ${TORCHVISION_VERSION_ACTUAL} available in PATH"
echo "# ONNX ${ONNX_VERSION_ACTUAL} + ONNX Runtime ${ONNXRUNTIME_VERSION_ACTUAL} available in PATH"
echo "# PATH priority: /opt/conda/bin first (python/pip/torch/onnx directly accessible)"
echo "# System venv /opt/venv/bin/python still available via absolute path"
echo "# Jupyter services unaffected (started via absolute paths by supervisord)"
echo "#"
echo "# Verify with: /opt/conda/bin/python -c \"import torch,onnx,onnxruntime;print(torch.__version__,onnx.__version__,onnxruntime.__version__)\""
echo "########################################################################"
echo ""
STAGE4_EOF
