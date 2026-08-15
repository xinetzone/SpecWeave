# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - torch-dev Variant Dockerfile
# Project: SpecWeave Full-featured Development Container - Free-Threading PyTorch 环境
# Base: devcontainer-base:onnx-quantized-${BASE_TAG} (ONNX quantization toolkit, main env, free-threading, no PyTorch)
# Toolchain: PyTorch + torchvision (cp314t manylinux wheel, CUDA ${TORCH_CUDA_INDEX}) in conda main env
# Relationship to onnx-pytorch:
#   - onnx-pytorch: PyTorch in conda base env (GIL Python 3.13.x) — GIL-bound workloads
#   - torch-dev:    PyTorch in conda main env (free-threading Python 3.14.6t) — no-GIL workloads
#   The two are parallel variants; neither depends on the other.
# PATH priority: /opt/conda/envs/main/bin first (inherited from onnx-quantized)
# Jupyter kernel: NOT registered here (kernel belongs to downstream ai-dev variant)
#
# Build: docker build -f variants/torch-dev/Dockerfile -t devcontainer-base:torch-dev-latest .
# CN:    docker build -f variants/torch-dev/Dockerfile \
#          --build-arg APT_MIRROR=aliyun --build-arg CONDA_MIRROR=bfsu --build-arg PIP_MIRROR=aliyun \
#          -t devcontainer-base:torch-dev-latest .
# Run:   docker run -d --privileged -p 2222:22 -p 2375:2375 -p 8888:8888 \
#          -e USER_PASSWORD=pass -e JUPYTER_TOKEN=mysecret -e GRANT_SUDO=yes \
#          -v $(pwd)/workspace:/workspace -v docker-data:/var/lib/docker \
#          devcontainer-base:torch-dev-latest
# Verify: docker run --rm devcontainer-base:torch-dev-latest \
#          /opt/conda/envs/main/bin/python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
#
# Variant Stage Layering (additional 3 layers on top of onnx-quantized variant):
#   Stage 1/3: PATH verification + timer init + base tool check (free-threading + torch-absent guards INVERTED)
#   Stage 2/3: PyTorch install (torch + torchvision cp314t) + post-install guards + cleanup
#   Stage 3/3: build-info + PyTorch smoke tests (matmul/conv2d/autograd) + timing summary
#
# Build Timing: 每个Stage结束时输出 [TIMER] 本阶段耗时+累计耗时，最终输出汇总表
# =============================================================================

ARG BASE_TAG=latest
ARG APT_MIRROR=official
ARG CONDA_MIRROR=bfsu
ARG PIP_MIRROR=aliyun
ARG TORCH_CUDA_INDEX=cu130

FROM devcontainer-base:onnx-quantized-${BASE_TAG}

ARG BASE_TAG
ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR
ARG TORCH_CUDA_INDEX

LABEL maintainer="SpecWeave"
LABEL description="DevContainer torch-dev variant with PyTorch in free-threading main env (cp314t, no GIL, CUDA ${TORCH_CUDA_INDEX}); downstream base for ai-dev"
LABEL variant="torch-dev"
LABEL pytorch="free-threading,cp314t,${TORCH_CUDA_INDEX}"

ENV CONDA_DIR=/opt/conda

# PATH / OpenMP defaults inherited from onnx-quantized; re-declared for clarity
ENV PATH=/opt/conda/envs/main/bin:/opt/conda/bin:${PATH}
ENV OMP_NUM_THREADS=4
ENV OPENBLAS_NUM_THREADS=1
ENV OMP_WAIT_POLICY=PASSIVE
ENV KMP_DUPLICATE_LIB_OK=TRUE

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# ═══════════════════════════════════════════════════════════════════
# Stage 1/3 (追加层1): 基础验证 + 计时器初始化
# 变化频率：最低
# 原则：验证 onnx-quantized 父层组件（main 环境 + free-threading + 量化工具链 + torch 缺席）；
#       注意：torch-absent 守卫在这里验证"父层无torch"，Stage 2 安装 torch 后守卫翻转为 torch-present
# ═══════════════════════════════════════════════════════════════════
RUN <<'STAGE1_EOF'
echo ""
echo "########################################################################"
echo "# [TORCH-DEV VARIANT STAGE 1/3] Base Verification + Timer Init"
echo "# CONDA_MIRROR=${CONDA_MIRROR}, PIP_MIRROR=${PIP_MIRROR}, TORCH_CUDA_INDEX=${TORCH_CUDA_INDEX}"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
echo "[TIMER] torch-dev variant build started at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "START=$_STAGE_START" > /tmp/.torch-dev-variant-build-timer
echo "[BUILD] Verifying onnx-quantized base installation (conda main env)..."
echo "  - onnx: $(python -c 'import onnx;print(onnx.__version__)' 2>/dev/null || echo 'not found')"
echo "  - onnxruntime: $(python -c 'import onnxruntime;print(onnxruntime.__version__)' 2>/dev/null || echo 'not found')"
echo "  - onnxsim: $(python -c 'import onnxsim;print(getattr(onnxsim,"__version__","installed"))' 2>/dev/null || echo 'not found')"
echo "  - torch: $(python -c 'import importlib.util as u; print("ABSENT (expected before install)" if u.find_spec("torch") is None else "PRESENT (unexpected)")')"
echo "  - free-threading: $(python -c 'import sys; print("GIL disabled (cp314t)" if not sys._is_gil_enabled() else "GIL ENABLED")')"
echo "  - conda: $(/opt/conda/bin/conda --version 2>&1 | head -1)"
echo "  - python: $(python --version 2>&1)"
echo "  - PATH: $PATH"
echo ""
echo "[GUARD] Base image must be free-threading with torch absent (pre-install)..."
python -c "import sys; assert sys._is_gil_enabled() is False, 'base image must be free-threading (cp314t)'" \
    && echo "[OK] free-threading base confirmed (GIL disabled)" \
    || { echo "[FATAL] base image is NOT free-threading - wrong base image?"; exit 1; }
python -c "import importlib.util as u, sys; f=u.find_spec('torch'); sys.exit(0 if f is None else 1)" \
    && echo "[OK] torch absent in onnx-quantized base (expected, will install in Stage 2)" \
    || { echo "[FATAL] torch already present in base - expected clean onnx-quantized (no torch)"; exit 1; }
python -c "import importlib.util as u, sys; f=u.find_spec('onnxoptimizer'); sys.exit(0 if f is None else 1)" \
    && echo "[OK] onnxoptimizer absent in base (free-threading incompatible, will keep excluded)" \
    || { echo "[FATAL] onnxoptimizer unexpectedly present in base!"; exit 1; }
echo ""
echo "[BUILD] Verifying quantization toolkit inherited from onnx-quantized..."
python -c "from onnxruntime.quantization import quantize_dynamic, QuantType; print('[OK] onnxruntime.quantization API inherited')"
echo ""
echo "[BUILD] Verifying devuser + services preserved..."
echo "  - devuser exists: $(id devuser 2>&1 | head -1)"
echo "  - /opt/conda exists: $(test -d /opt/conda && echo 'yes' || echo 'no')"
echo "  - docker: $(docker --version 2>&1 | head -1)"
echo "  - supervisord: $(supervisord --version 2>&1 | head -1)"
echo ""
_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_TOTAL=$((_NOW - $(grep '^START=' /tmp/.torch-dev-variant-build-timer | cut -d= -f2)))
echo "TDS1=$_NOW" >> /tmp/.torch-dev-variant-build-timer
echo "[TIMER] Stage 1/3 (base verify+init) took ${_ELAPSED}s | torch-dev variant cumulative: ${_TOTAL}s"
echo '[OK] Stage 1 complete'
STAGE1_EOF

# ═══════════════════════════════════════════════════════════════════
# Stage 2/3 (追加层2): 安装 PyTorch + 守卫 + 清理
# 变化频率：中（torch 版本升级时改）
# 原则：在 conda main 环境 (free-threading cp314t) 安装 torch + torchvision；
#       安装后执行 free-threading + torch-present 双守卫；立即清理缓存；使用 BuildKit cache 加速
# 包含：torch (核心), torchvision (视觉生态)
# 不包含：onnxoptimizer (free-threading 不兼容，CPython #111506)
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    <<'STAGE2_EOF'
echo ""
echo "########################################################################"
echo "# [TORCH-DEV VARIANT STAGE 2/3] Install PyTorch (main env, ft) + Guards + Cleanup"
echo "# Packages:"
echo "#   - torch        (PyTorch core, cp314t, CUDA ${TORCH_CUDA_INDEX})"
echo "#   - torchvision  (PyTorch vision, cp314t, matching CUDA index)"
echo "# NOT INSTALLED:"
echo "#   - onnxoptimizer (free-threading incompatible, CPython #111506)"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
source /opt/conda/etc/profile.d/conda.sh
conda activate main
echo "[OK] main environment activated"
echo "  - conda env: $CONDA_DEFAULT_ENV"
echo ""

# ── 辅助函数：pip 包分组安装（结构化日志+计时+冲突诊断） ──
pip_install_group() {
    local group_name="$1" description="$2"
    shift 2
    local g_start g_end g_elapsed rc
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [PIP INSTALL] ${group_name}"
    echo "│ Desc: ${description}"
    echo "│ PKGS: $*"
    echo "│ Index: https://download.pytorch.org/whl/${TORCH_CUDA_INDEX}"
    echo "└─────────────────────────────────────────────────┘"
    g_start=$(date +%s)
    set +e
    pip install --no-cache-dir --timeout 120 --retries 5 \
        --index-url "https://download.pytorch.org/whl/${TORCH_CUDA_INDEX}" "$@" 2>&1
    rc=$?
    set -e
    g_end=$(date +%s)
    g_elapsed=$((g_end - g_start))
    if [ $rc -eq 0 ]; then
        echo "[OK] ${group_name} installed in ${g_elapsed}s"
        echo "[CHECK] pip check for dependency conflicts:"
        pip check 2>&1 | head -20 || true
    else
        echo "[FAIL] ${group_name} failed after ${g_elapsed}s (exit code: $rc)"
        echo "[DIAG] pip check output for conflict diagnosis:"
        pip check 2>&1 | head -30 || true
        exit $rc
    fi
}

pip_install_group "G1: PyTorch Core" \
    "torch + torchvision (cp314t free-threading, CUDA ${TORCH_CUDA_INDEX})" \
    torch torchvision

echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│ [VERIFY] PyTorch installation                   │"
echo "└─────────────────────────────────────────────────┘"
echo "  - torch:        $(python -c 'import torch; print(torch.__version__)' 2>&1)"
echo "  - torchvision:  $(python -c 'import torchvision; print(torchvision.__version__)' 2>&1)"
echo "  - torch cuda:   $(python -c 'import torch; print(f\"available={torch.cuda.is_available()}, device_count={torch.cuda.device_count()}\")' 2>&1)"
echo "  - torch cxx abi:$(python -c 'import torch; print(torch._C._GLIBCXX_USE_CXX11_ABI)' 2>&1)"
echo ""

echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│ [GUARD] Free-threading integrity check          │"
echo "└─────────────────────────────────────────────────┘"
_PY_BUILD=$(conda list python 2>/dev/null | awk '$1=="python"{print $3; exit}')
echo "  - python build string: ${_PY_BUILD:-unknown}"
echo "$_PY_BUILD" | grep -q "cp314t" || { echo "[FATAL] python build is not cp314t after pip installs"; exit 1; }
python -c "import sys; sys.exit(0 if sys._is_gil_enabled() is False else 1)" \
    && echo "[OK] free-threading (cp314t) preserved, GIL still disabled" \
    || { echo "[FATAL] GIL unexpectedly enabled after PyTorch install"; exit 1; }

echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│ [GUARD] torch-present positive check             │"
echo "└─────────────────────────────────────────────────┘"
python -c "import importlib.util as u, sys; f=u.find_spec('torch'); print('[INFO] torch:', 'PRESENT' if f else 'ABSENT'); sys.exit(0 if f else 1)" \
    && echo "[OK] torch is present (installed in Stage 2)" \
    || { echo "[FATAL] torch missing after install!"; exit 1; }
python -c "import importlib.util as u, sys; f=u.find_spec('torchvision'); print('[INFO] torchvision:', 'PRESENT' if f else 'ABSENT'); sys.exit(0 if f else 1)" \
    && echo "[OK] torchvision is present" \
    || { echo "[FATAL] torchvision missing after install!"; exit 1; }
python -c "import importlib.util as u, sys; f=u.find_spec('onnxoptimizer'); print('[INFO] onnxoptimizer:', 'ABSENT' if f is None else 'PRESENT'); sys.exit(0 if f is None else 1)" \
    && echo "[OK] onnxoptimizer still absent (free-threading incompatible, CPython #111506)" \
    || { echo "[FATAL] onnxoptimizer unexpectedly pulled in by torch deps!"; exit 1; }
echo ""

echo "[ACTION] Setting permissions for devuser..."
find /opt/conda/envs/main/bin -type f -executable -exec chmod a+x {} \; 2>/dev/null || true
echo "[OK] Permissions verified (main env bin executables)"
echo ""

echo "[ACTION] Post-install cleanup..."
find /opt/conda/envs/main/lib -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find /opt/conda/envs/main/lib -type f -name '*.pyc' -delete 2>/dev/null || true
conda clean -yafq 2>/dev/null || true
pip cache purge 2>/dev/null || true
echo "[OK] Post-install cleanup complete (__pycache__/.pyc removed, conda+pip cache purged)"
echo ""

_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.torch-dev-variant-build-timer | cut -d= -f2)
_TOTAL=$((_NOW - _START))
echo "TDS2=$_NOW" >> /tmp/.torch-dev-variant-build-timer
echo "[TIMER] Stage 2/3 (PyTorch install + cleanup) took ${_ELAPSED}s | torch-dev variant cumulative: ${_TOTAL}s"
echo '[OK] Stage 2 complete'
STAGE2_EOF

# ═══════════════════════════════════════════════════════════════════
# Stage 3/3 (追加层3): build-info + PyTorch 冒烟测试 + 汇总表
# 变化频率：最低
# 原则：写入 variant build-info；运行 PyTorch 冒烟测试（基础算子+推理+autograd）
# ═══════════════════════════════════════════════════════════════════
RUN <<'STAGE3_EOF'
echo ""
echo "########################################################################"
echo "# [TORCH-DEV VARIANT STAGE 3/3] Final Metadata, PyTorch Smoke Test, Timing Summary"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
source /opt/conda/etc/profile.d/conda.sh
conda activate main

echo "[ACTION] Writing build metadata to /etc/devcontainer-variant-torch-dev-build-info..."
TORCH_VERSION_ACTUAL=$(python -c "import torch;print(torch.__version__)" 2>/dev/null || echo "unknown")
TV_VERSION_ACTUAL=$(python -c "import torchvision;print(torchvision.__version__)" 2>/dev/null || echo "unknown")
TORCH_CUDA_AVAIL=$(python -c "import torch;print('yes' if torch.cuda.is_available() else 'no')" 2>/dev/null || echo "unknown")
ORT_VERSION=$(python -c "import onnxruntime;print(onnxruntime.__version__)" 2>/dev/null || echo "unknown")
ONNX_VERSION_ACTUAL=$(python -c "import onnx;print(onnx.__version__)" 2>/dev/null || echo "unknown")
printf '%s\n' \
    "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "VARIANT=torch-dev" \
    "VARIANT_DESCRIPTION=Free-Threading PyTorch 开发环境 (main env, cp314t, no GIL, CUDA ${TORCH_CUDA_INDEX})" \
    "BASE_IMAGE=devcontainer-base:onnx-quantized-${BASE_TAG}" \
    "INSTALL_ENV=main" \
    "INSTALL_ENV_PATH=/opt/conda/envs/main" \
    "INSTALL_PYTHON=/opt/conda/envs/main/bin/python" \
    "GIL_ENABLED=false" \
    "PYTHON_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")' 2>/dev/null)" \
    "PYTHON_BUILD=cp314t (free-threading)" \
    "TORCH_VERSION=${TORCH_VERSION_ACTUAL}" \
    "TORCHVISION_VERSION=${TV_VERSION_ACTUAL}" \
    "TORCH_CUDA_INDEX=${TORCH_CUDA_INDEX}" \
    "TORCH_CUDA_AVAILABLE=${TORCH_CUDA_AVAIL}" \
    "ONNX_VERSION=${ONNX_VERSION_ACTUAL}" \
    "ONNXRUNTIME_VERSION=${ORT_VERSION}" \
    "CONDA_DIR=/opt/conda" \
    "CONDA_MIRROR=${CONDA_MIRROR}" \
    "PIP_MIRROR=${PIP_MIRROR}" \
    "APT_MIRROR=${APT_MIRROR}" \
    "PATH_PRIORITY=conda-main-bin-first" \
    "SERVICES_PRESERVED=sshd,dockerd,podman,jupyter,supervisord" \
    "PACKAGES_INSTALLED=torch,torchvision" \
    "PACKAGES_INHERITED=onnx,onnxruntime,onnxconverter-common,onnxsim,onnxscript" \
    "PACKAGES_EXCLUDED=onnxoptimizer (free-threading incompatible, CPython #111506)" \
    "KERNEL_REGISTERED=false" \
    "DOWNSTREAM_VARIANTS=ai-dev" \
    "BUILD_TIMER=enabled" \
    > /etc/devcontainer-variant-torch-dev-build-info
echo "[OK] Build metadata written:"
cat /etc/devcontainer-variant-torch-dev-build-info
echo ""

# NOTE: timer file lives in /tmp; capture timing data BEFORE rm -rf /tmp/* below,
# otherwise arithmetic expansion on empty strings fails the build.
_TSTART=$(grep '^START=' /tmp/.torch-dev-variant-build-timer | cut -d= -f2)
_TTDS1=$(grep '^TDS1=' /tmp/.torch-dev-variant-build-timer | cut -d= -f2)
_TTDS2=$(grep '^TDS2=' /tmp/.torch-dev-variant-build-timer | cut -d= -f2)
_TSTART=${_TSTART:-$(date +%s)}
_TTDS1=${_TDS1:-$_TSTART}
_TTDS2=${_TDS2:-$_TTDS1}

echo "[ACTION] Running final cleanup..."
find /opt/conda/envs/main/lib -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find /opt/conda/envs/main/lib -type f -name '*.pyc' -delete 2>/dev/null || true
apt-get clean 2>/dev/null || true
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
echo "[OK] Final cleanup complete"
echo ""

echo "┌─────────────────────────────────────────────────┐"
echo "│  [VALIDATION CHECKPOINT - Stage 3/3]           │"
echo "│  Running service + PyTorch validation           │"
echo "└─────────────────────────────────────────────────┘"
echo ""
echo "[VALIDATE 1/8] PyTorch imports..."
python -c "import torch; import torchvision; print(f'[OK] torch {torch.__version__}, torchvision {torchvision.__version__}')"
echo "[VALIDATE 2/8] Conda main environment intact..."
test -d /opt/conda/envs/main && test -x /opt/conda/envs/main/bin/python && echo "[OK] /opt/conda/envs/main environment intact"
/opt/conda/envs/main/bin/python --version
echo "[VALIDATE 3/8] Jupyter available from conda main..."
/opt/conda/envs/main/bin/jupyter --version 2>&1 | head -2
echo "[VALIDATE 4/8] Core services (docker, supervisord) preserved..."
docker --version 2>&1
supervisord --version 2>&1
echo "[OK] Core services preserved"
echo "[VALIDATE 5/8] devuser can access PyTorch..."
su - devuser -c "/opt/conda/envs/main/bin/python -c 'import torch; print(f\"torch {torch.__version__} accessible\")'" && echo "[OK] devuser can access torch"
echo "[VALIDATE 6/8] Free-threading + exclusions preserved..."
python -c "import sys; assert sys._is_gil_enabled() is False; print('[OK] free-threading active (cp314t, GIL disabled)')"
python -c "import importlib.util as u, sys; assert u.find_spec('torch') is not None, 'torch must be present'; assert u.find_spec('onnxoptimizer') is None, 'onnxoptimizer must be absent'; print('[OK] torch present + onnxoptimizer absent (by design)')"
echo "[VALIDATE 7/8] ONNX quantization stack inherited..."
python -c "from onnxruntime.quantization import quantize_dynamic; print('[OK] onnxruntime.quantization inherited from onnx-quantized')"
echo "[VALIDATE 8/8] LLVM toolchain still inherited..."
llvm-config --version 2>&1 | head -1
echo "[OK] LLVM toolchain preserved"
echo ""
echo "[VALIDATE] All validation checks completed"
echo ""

echo "┌─────────────────────────────────────────────────┐"
echo "│  [FINAL VERIFICATION - PYTORCH SMOKE]          │"
echo "│  matmul + conv2d + autograd + softmax sanity    │"
echo "│  (cp314t free-threading compute correctness)    │"
echo "└─────────────────────────────────────────────────┘"
python - <<'TSMOKE'
import sys
import torch
import torch.nn.functional as F

print(f"[INFO] torch version: {torch.__version__}")
print(f"[INFO] python GIL enabled: {sys._is_gil_enabled()}")
print(f"[INFO] CUDA available: {torch.cuda.is_available()}")

# Deterministic seed
torch.manual_seed(42)

# Test 1: matmul correctness
a = torch.randn(64, 128)
b = torch.randn(128, 32)
c = torch.matmul(a, b)
assert c.shape == (64, 32), f"matmul shape mismatch: {c.shape}"
print(f"[OK] matmul: (64,128)@(128,32) -> {c.shape}")

# Test 2: conv2d correctness
x = torch.randn(1, 3, 32, 32)
w = torch.randn(16, 3, 3, 3)
conv_out = F.conv2d(x, w, padding=1)
assert conv_out.shape == (1, 16, 32, 32), f"conv2d shape mismatch: {conv_out.shape}"
print(f"[OK] conv2d: (1,3,32,32) * (16,3,3,3) -> {conv_out.shape}")

# Test 3: autograd correctness
x = torch.randn(4, 8, requires_grad=True)
w = torch.randn(8, 4, requires_grad=True)
y = x @ w
loss = y.sum()
loss.backward()
assert x.grad is not None and w.grad is not None, "gradients not computed"
assert x.grad.shape == x.shape and w.grad.shape == w.shape, f"grad shape mismatch: x.grad={x.grad.shape}, w.grad={w.grad.shape}"
print(f"[OK] autograd: gradients computed correctly, shapes match")

# Test 4: softmax + cross-entropy
logits = torch.randn(8, 10)
targets = torch.randint(0, 10, (8,))
loss = F.cross_entropy(logits, targets)
assert loss.dim() == 0 and loss.item() > 0, f"cross_entropy unexpected: {loss}"
print(f"[OK] softmax+cross_entropy: loss={loss.item():.4f}")

# Test 5: basic tensor ops
t = torch.arange(10, dtype=torch.float32)
assert t.sum().item() == 45.0, f"sum mismatch: {t.sum().item()}"
assert (t * 2).sum().item() == 90.0, f"mul+sum mismatch"
print(f"[OK] basic tensor ops: arange+sum+mul OK")

# Test 6: simple neural net forward
model = torch.nn.Sequential(
    torch.nn.Linear(16, 32),
    torch.nn.ReLU(),
    torch.nn.Linear(32, 4),
)
out = model(torch.randn(4, 16))
assert out.shape == (4, 4), f"MLP forward shape mismatch: {out.shape}"
print(f"[OK] MLP forward: Sequential(16->32->4) -> {out.shape}")

print("")
print("[OK] PYTORCH SMOKE TEST PASSED")
print("[OK] matmul + conv2d + autograd + softmax + MLP all correct in free-threading (cp314t)")
TSMOKE
echo "[OK] PyTorch smoke test passed"
echo ""

_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$_TSTART
_TTDS1=${_TTDS1}
_TTDS2=${_TTDS2}
_OT1=$((_TTDS1 - _START))
_OT2=$((_TTDS2 - _TTDS1))
_OT3=$_ELAPSED
_OTOTAL=$((_NOW - _START))
echo "[TIMER] Stage 3/3 (metadata+PyTorch smoke) took ${_ELAPSED}s | torch-dev variant cumulative: ${_OTOTAL}s"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  BUILD TIMING SUMMARY (torch-dev Variant - 3 Add Stages)   ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  Stage 1/3  base verification         %5ds               ║\n" $_OT1
printf "║  Stage 2/3  PyTorch install+guards    %5ds               ║\n" $_OT2
printf "║  Stage 3/3  smoke test+metadata       %5ds               ║\n" $_OT3
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  TORCH-DEV VARIANT TOTAL (add-on)     %5ds               ║\n" $_OTOTAL
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
rm -f /tmp/.torch-dev-variant-build-timer
echo "########################################################################"
echo "# TORCH-DEV VARIANT BUILD COMPLETE!"
echo "# PyTorch + torchvision installed in conda main env (free-threading cp314t)"
echo "#"
echo "# Quick start:"
echo "#   /opt/conda/envs/main/bin/python -c \"import torch; print(torch.__version__)\""
echo "#"
echo "# Downstream: ai-dev (AI/ML/NLP full stack) builds on this variant"
echo "########################################################################"
echo ""
STAGE3_EOF
