# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - Torch-Dev (Free-Threading PyTorch cp314t)
# Base: devcontainer-base:onnx-quantized-${BASE_TAG} (ONNX quantization, main env, free-threading)
# Toolchain: torch + torchvision (cp314t, CUDA ${TORCH_CUDA_INDEX}) in main env
# PATH priority: /opt/conda/envs/main/bin first (inherited from onnx-quantized)
# Kernel: NOT registered here (kernel belongs to downstream ai-dev)
# Build (CN): docker build -f variants/torch-dev/Dockerfile --build-arg PIP_MIRROR=aliyun -t devcontainer-base:torch-dev-latest .
# Verify: docker run --rm devcontainer-base:torch-dev-latest /opt/conda/envs/main/bin/python -c "import torch;print(torch.__version__)"
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
LABEL description="DevContainer torch-dev: PyTorch+torchvision in free-threading main env (cp314t, no GIL, CUDA ${TORCH_CUDA_INDEX})"
LABEL variant="torch-dev"
LABEL pytorch="free-threading,cp314t,${TORCH_CUDA_INDEX}"

ENV CONDA_DIR=/opt/conda \
    OMP_NUM_THREADS=4 \
    OPENBLAS_NUM_THREADS=1 \
    OMP_WAIT_POLICY=PASSIVE \
    KMP_DUPLICATE_LIB_OK=TRUE
ENV PATH=/opt/conda/envs/main/bin:/opt/conda/bin:${PATH}

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# Framework already inherited from onnx-quantized base layer.

# ── Stage 1/3: Base verification (torch absent pre-install) ──────
RUN <<'S1'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_start "torch-dev"
variant_timer_stage 1 "Base verification (torch absent pre-install)"

assert_package_present onnx
assert_package_present onnxruntime
assert_package_present onnxsim "onnx-simplifier"
assert_python_cp314t
assert_free_threading
assert_package_absent torch
assert_package_absent onnxoptimizer
python -c "from onnxruntime.quantization import quantize_dynamic,QuantType;print('[OK] quantization API inherited')"
llvm-config --version 2>&1 | head -1
echo "[OK] onnx-quantized base verified (free-threading, torch absent, ONNX quant + LLVM inherited)"
S1

# ── Stage 2/3: PyTorch install + guards ──────────────────────────
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    <<'S2'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 2 "PyTorch install + guards"
variant_activate_main_env

pip_install_group --index-url "https://download.pytorch.org/whl/${TORCH_CUDA_INDEX}" \
    "G1: PyTorch Core" \
    "torch + torchvision (cp314t free-threading, CUDA ${TORCH_CUDA_INDEX})" \
    torch torchvision

echo "  torch:        $(python -c 'import torch; print(torch.__version__)' 2>&1)"
echo "  torchvision:  $(python -c 'import torchvision; print(torchvision.__version__)' 2>&1)"
echo "  torch cuda:   $(python -c 'import torch; print(f\"available={torch.cuda.is_available()}, devices={torch.cuda.device_count()}\")' 2>&1)"

assert_python_cp314t
assert_free_threading
assert_package_present torch
assert_package_present torchvision
assert_package_absent onnxoptimizer

ensure_all_permissions
cleanup_pycache
cleanup_conda_pip_cache
S2

# ── Stage 3/3: Build-info + PyTorch smoke tests ──────────────────
RUN <<'S3'
set +o pipefail
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 3 "Build-info + PyTorch smoke tests"
variant_activate_main_env

variant_write_build_info "torch-dev" "onnx-quantized-${BASE_TAG}" \
    "VARIANT_DESCRIPTION=Free-Threading PyTorch dev env (main env, cp314t, no GIL, CUDA ${TORCH_CUDA_INDEX})" \
    "INSTALL_ENV=main (/opt/conda/envs/main)" \
    "GIL_ENABLED=false" \
    "PYTHON_BUILD=cp314t (free-threading)" \
    "TORCH_VERSION=$(python -c 'import torch;print(torch.__version__)')" \
    "TORCHVISION_VERSION=$(python -c 'import torchvision;print(torchvision.__version__)')" \
    "TORCH_CUDA_INDEX=${TORCH_CUDA_INDEX}" \
    "TORCH_CUDA_AVAILABLE=$(python -c 'import torch;print(\"yes\" if torch.cuda.is_available() else \"no\")')" \
    "PACKAGES_INSTALLED=torch,torchvision" \
    "PACKAGES_INHERITED=onnx,onnxruntime,onnxconverter-common,onnxsim,onnxscript,LLVM" \
    "PACKAGES_EXCLUDED=onnxoptimizer (ft-incompatible: CPython#111506)" \
    "KERNEL_REGISTERED=false (kernel in downstream ai-dev)" \
    "DOWNSTREAM_VARIANTS=ai-dev"

cleanup_all

verify_validation_header "PyTorch Verification"
python -c "import torch, torchvision; print(f'[OK] torch {torch.__version__}, torchvision {torchvision.__version__}')"
python -c "from onnxruntime.quantization import quantize_dynamic; print('[OK] quantization API inherited')"
assert_python_cp314t
assert_free_threading
assert_package_present torch
assert_package_present torchvision
assert_package_absent onnxoptimizer
llvm-config --version 2>&1 | head -1 && echo "  [OK] LLVM inherited"
verify_base_services
echo -n "  [VERIFY] devuser PyTorch access... "
su - devuser -c "python -c 'import torch;print(f\"torch {torch.__version__} OK\")'" >/dev/null 2>&1 \
    && echo "[OK]" || { echo "[FAIL]"; exit 1; }

# ── PyTorch Smoke Test (6 sub-tests: matmul/conv2d/autograd/softmax/tensor/MLP) ──
echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│  [SMOKE] PyTorch compute (cp314t ft)           │"
echo "└─────────────────────────────────────────────────┘"
python - <<'TSMOKE'
import sys, torch, torch.nn.functional as F
print(f"[INFO] torch {torch.__version__}, GIL enabled: {sys._is_gil_enabled()}, CUDA: {torch.cuda.is_available()}")
torch.manual_seed(42)

a, b = torch.randn(64,128), torch.randn(128,32)
c = torch.matmul(a,b); assert c.shape==(64,32); print(f"[OK] matmul (64,128)@(128,32)->{c.shape}")

x, w = torch.randn(1,3,32,32), torch.randn(16,3,3,3)
conv = F.conv2d(x,w,padding=1); assert conv.shape==(1,16,32,32); print(f"[OK] conv2d (1,3,32,32)->{conv.shape}")

x2 = torch.randn(4,8,requires_grad=True); w2 = torch.randn(8,4,requires_grad=True)
y = x2@w2; y.sum().backward()
assert x2.grad is not None and w2.grad is not None; print("[OK] autograd gradients computed")

logits, targets = torch.randn(8,10), torch.randint(0,10,(8,))
loss = F.cross_entropy(logits,targets); assert loss.dim()==0 and loss.item()>0; print(f"[OK] cross_entropy loss={loss.item():.4f}")

t = torch.arange(10,dtype=torch.float32); assert t.sum().item()==45.0; print("[OK] tensor arange+sum")

model = torch.nn.Sequential(torch.nn.Linear(16,32), torch.nn.ReLU(), torch.nn.Linear(32,4))
out = model(torch.randn(4,16)); assert out.shape==(4,4); print(f"[OK] MLP forward (4,16)->{out.shape}")

print("[OK] PYTORCH SMOKE PASSED (matmul+conv2d+autograd+softmax+tensor+MLP)")
TSMOKE

echo ""
variant_timer_summary "torch-dev Variant (add-on)"
echo "########################################################################"
echo "# TORCH-DEV BUILD COMPLETE - PyTorch cp314t free-threading, GIL off"
echo "# Quick: /opt/conda/envs/main/bin/python -c \"import torch;print(torch.__version__)\""
echo "# Downstream: ai-dev (AI/ML/NLP full stack)"
echo "########################################################################"
S3
