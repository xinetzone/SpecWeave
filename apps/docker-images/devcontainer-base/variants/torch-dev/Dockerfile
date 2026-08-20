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

# Update framework libs (cleanup.sh with cleanup_torch_dev + r2-dtneeded-analysis + verify.sh slim functions)
COPY shared/lib/cleanup.sh /usr/local/share/variant-framework/cleanup.sh
COPY shared/lib/verify.sh /usr/local/share/variant-framework/verify.sh
COPY --chmod=755 shared/scripts/r2-dtneeded-analysis.sh /usr/local/share/variant-framework/r2-dtneeded-analysis.sh

# Override shared install-helpers.sh to pick up --extra-index-url support without
# full chain rebuild (conda-llvm→onnx-dev→onnx-quantized). Safe because helpers
# are sourced at RUN time (not baked into earlier layers' binaries).
# Remove this COPY after the next full dependency-chain rebuild.
COPY shared/lib/install-helpers.sh /usr/local/share/variant-framework/install-helpers.sh

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
    --extra-index-url "https://mirrors.aliyun.com/pypi/simple/" \
    "G1: PyTorch Core" \
    "torch + torchvision (cp314t free-threading, CUDA ${TORCH_CUDA_INDEX})" \
    torch torchvision

echo "  torch:        $(python -c 'import torch; print(torch.__version__)' 2>&1)"
echo "  torchvision:  $(python -c 'import torchvision; print(torchvision.__version__)' 2>&1)"
echo "  torch cuda:   $(python -c 'import torch; print(f"available={torch.cuda.is_available()}, devices={torch.cuda.device_count()}")' 2>&1)"

assert_python_cp314t
assert_free_threading
assert_package_present torch
assert_package_present torchvision
assert_package_absent onnxoptimizer

# ── 激进瘦身（必须在 pip install 同层，避免 CoW 膨胀）────────────
# cleanup_binaries: strip 所有 .so 共享库 (~460MB saved) + 删除非必要静态库
# cleanup_torch_dev: 删除冗余 CUDA 库 (nvrtc.alt, nvperf, nvshmem-bitcode, amd-backend ~180MB)
cleanup_binaries
cleanup_torch_dev

# 轻量级权限修复（不做 chmod -R /opt/conda，避免 CoW 膨胀）
ensure_user_bashrc
ensure_profile_d_executable

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
    "TORCH_CUDA_AVAILABLE=$(python -c 'import torch;print("yes" if torch.cuda.is_available() else "no")')" \
    "PACKAGES_INSTALLED=torch,torchvision" \
    "PACKAGES_INHERITED=onnx,onnxruntime,onnxconverter-common,onnxsim,onnxscript,LLVM" \
    "PACKAGES_EXCLUDED=onnxoptimizer (ft-incompatible: CPython#111506)" \
    "KERNEL_REGISTERED=false (kernel in downstream ai-dev)" \
    "DOWNSTREAM_VARIANTS=ai-dev" \
    "SLIMMING=R1:strip-bins(.so~508MB)+del-nvrtc.alt+nvperf+nvshmem-device+triton-amd+no-chmod-R(CoW); R2:del-cusolverMg(100MB)+cudnn-jit(29MB)+nvshmem-plugins(4MB)+small-utils(3MB)+protoc(10MB)+strip-triton-bins; SOP:docker-gpu-slimming-sop.md"

# ── Variant-specific assertions (继承+GIL+排除项) ──
verify_validation_header "PyTorch Verification"
python -c "import torch, torchvision; print(f'[OK] torch {torch.__version__}, torchvision {torchvision.__version__}')"
python -c "from onnxruntime.quantization import quantize_dynamic; print('[OK] quantization API inherited')"
assert_python_cp314t
assert_free_threading
assert_package_present torch
assert_package_present torchvision
assert_package_absent onnxoptimizer

# ── P1 硬断言：torch 必须为 CUDA 编译版（防 extra-index 静默降级）──
# 构建环境无 GPU → torch.cuda.is_available() 恒为 False，不可作为断言依据；
# 用 torch.version.cuda（编译时 CUDA 版本）：CUDA 构建返回非空（如 13.0），
# CPU 降级版返回 None。主索引不可达时 extra-index 只会提供 CPU 版，此断言强制构建 FAIL。
echo -n "  [VERIFY] torch CUDA build (torch.version.cuda)... "
CUDA_BUILD=$(python -c 'import torch; v = torch.version.cuda; print(v if v else "NONE")' 2>&1)
if [ -z "${CUDA_BUILD}" ] || [ "${CUDA_BUILD}" = "NONE" ]; then
    echo "[FAIL] torch is CPU build (silent downgrade via extra-index?) - expected CUDA ${TORCH_CUDA_INDEX}"
    variant_log_error "CUDA build assertion failed: torch.version.cuda is empty (CPU downgrade detected)"
    exit 1
fi
echo "[OK] torch CUDA build version: ${CUDA_BUILD} (index ${TORCH_CUDA_INDEX})"

llvm-config --version 2>&1 | head -1 && echo "  [OK] LLVM inherited"
verify_base_services
python -c "import sys; print(f'[INFO] GIL enabled: {sys._is_gil_enabled()}')"

# ── SOP Step 4: 框架级 GPU/ML slim 验证（CPU+CUDA冒烟+删除/保留断言+devuser）──
verify_all_slim_gpu

# ── 变体专项验证：devuser可import torch ──
echo -n "  [VERIFY] devuser torch import... "
su - devuser -c "python -c 'import torch;print(f\"torch {torch.__version__} OK\")'" >/dev/null 2>&1 \
    && echo "[OK]" || { echo "[FAIL]"; exit 1; }

# ── SOP Step 4 末：Post-verification cleanup（清理测试产生的pycache）──
cleanup_post_tests

echo ""
variant_timer_summary "torch-dev Variant (add-on)"
echo "########################################################################"
echo "# TORCH-DEV BUILD COMPLETE - PyTorch cp314t free-threading, GIL off"
echo "# Quick: /opt/conda/envs/main/bin/python -c \"import torch;print(torch.__version__)\""
echo "# Downstream: ai-dev (AI/ML/NLP full stack)"
echo "########################################################################"
S3
