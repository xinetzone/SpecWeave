# syntax=docker/dockerfile:1.7
# =============================================================================
# PyTorch Base Docker Image - Miniconda3 + Python 3.14 + PyTorch
# =============================================================================
# Base image:  ubuntu:26.04 (LTS)
# Python:      3.14 (via Miniconda3, supports 3.10-3.14)
# PyTorch:     2.13.0 (latest stable, per pytorch.org/get-started/locally/)
#
# Install command per official guide:
#   CPU:   pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu
#   CUDA:  pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
#
# Optimized for unreliable network environments:
#   - Aliyun apt mirror (HTTP first, then HTTPS after ca-certificates)
#   - Tsinghua TUNA conda mirror
#   - Aliyun pip mirror
#   - Retry logic for all downloads
#   - BuildKit cache mounts for conda/pip
#   - Offline installation support via offline/ directory
#
# Build log prefixes:
#   [STAGE]  - Current build stage marker
#   [BRANCH] - Branch decision point (if/else path taken)
#   [ACTION] - Action being performed
#   [OK]     - Action completed successfully
#   [WARN]   - Non-fatal warning
#   [ERROR]  - Fatal error (should cause exit)
#   [FALLBACK] - Falling back to alternative method
# =============================================================================

ARG BASE_IMAGE=ubuntu:26.04
ARG USE_GPU=0
ARG PYTHON_VERSION=3.14
ARG PYTORCH_VERSION=2.13.0
ARG CUDA_VERSION=12.6
ARG MINICONDA_VERSION=latest
ARG QUIET=0

FROM ${BASE_IMAGE} AS base

ARG MINICONDA_VERSION
ARG BASE_IMAGE
ARG USE_GPU
ARG PYTHON_VERSION
ARG PYTORCH_VERSION
ARG CUDA_VERSION
ARG QUIET=0

LABEL maintainer="SpecWeave Team" \
      description="PyTorch base image with Miniconda3 + Python 3.14, optimized for CN network" \
      version="2.1.0"

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai \
    LANG=zh_CN.UTF-8 \
    LANGUAGE=zh_CN:zh \
    LC_ALL=zh_CN.UTF-8 \
    CONDA_DIR=/opt/conda \
    CONDA_ENVS_DIRS=/opt/conda/envs \
    CONDA_PKGS_DIRS=/opt/conda/pkgs \
    PATH=/opt/conda/envs/pytorch/bin:/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ \
    PIP_TRUSTED_HOST=mirrors.aliyun.com \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENV_NAME=pytorch \
    ENV_PATH=/opt/conda/envs/pytorch \
    ENTRYPOINT_QUIET=""

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

WORKDIR /workspace

# ==================== Stage 1: System Packages + Chinese Locale ====================
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 1/7] System Packages + Chinese Locale" && \
    echo "# BASE_IMAGE=${BASE_IMAGE}, TZ=Asia/Shanghai, LANG=zh_CN.UTF-8" && \
    echo "########################################################################" && \
    echo "" && \
    echo "[ACTION] Detecting sources.list format..." && \
    (cp /etc/apt/sources.list.d/ubuntu.sources /etc/apt/sources.list.d/ubuntu.sources.bak 2>/dev/null || true) && \
    if [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then \
        echo "[BRANCH] Using deb822 format (ubuntu.sources)"; \
        SOURCES_FILE="/etc/apt/sources.list.d/ubuntu.sources"; \
        sed -i 's|http://archive.ubuntu.com|http://mirrors.aliyun.com|g' "$SOURCES_FILE"; \
        sed -i 's|http://security.ubuntu.com|http://mirrors.aliyun.com|g' "$SOURCES_FILE"; \
        sed -i 's|https://archive.ubuntu.com|http://mirrors.aliyun.com|g' "$SOURCES_FILE"; \
        sed -i 's|https://security.ubuntu.com|http://mirrors.aliyun.com|g' "$SOURCES_FILE"; \
    else \
        echo "[BRANCH] Using traditional sources.list format"; \
        SOURCES_FILE="/etc/apt/sources.list"; \
        sed -i 's|http://archive.ubuntu.com|http://mirrors.aliyun.com|g' "$SOURCES_FILE"; \
        sed -i 's|http://security.ubuntu.com|http://mirrors.aliyun.com|g' "$SOURCES_FILE"; \
        sed -i 's|https://archive.ubuntu.com|http://mirrors.aliyun.com|g' "$SOURCES_FILE"; \
        sed -i 's|https://security.ubuntu.com|http://mirrors.aliyun.com|g' "$SOURCES_FILE"; \
    fi && \
    echo "[OK] Apt mirror configured to mirrors.aliyun.com (HTTP, pre-ca-certificates)" && \
    echo '[ACTION] Configuring apt retries (5 retries, 30s timeout)...' && \
    echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::http::Timeout "30";' >> /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::https::Timeout "30";' >> /etc/apt/apt.conf.d/80-retries && \
    echo '[OK] Apt retry config written' && \
    echo '[ACTION] apt-get update...' && \
    apt-get update && \
    echo '[OK] apt-get update succeeded' && \
    echo '[ACTION] Installing system packages (ca-certificates, tzdata, locales, tini, gosu, wget, build-essential, etc.)...' && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        tzdata \
        locales \
        tini \
        sudo \
        wget \
        curl \
        bzip2 \
        gzip \
        tar \
        git \
        build-essential \
        gosu \
    && \
    echo '[OK] System packages installed' && \
    echo '[ACTION] Switching apt mirror to HTTPS (ca-certificates now available)...' && \
    if [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then \
        sed -i 's|http://mirrors.aliyun.com|https://mirrors.aliyun.com|g' /etc/apt/sources.list.d/ubuntu.sources; \
    else \
        sed -i 's|http://mirrors.aliyun.com|https://mirrors.aliyun.com|g' /etc/apt/sources.list; \
    fi && \
    echo '[OK] Apt mirror switched to HTTPS' && \
    echo '[ACTION] Generating zh_CN.UTF-8 locale...' && \
    locale-gen zh_CN.UTF-8 && \
    update-locale LANG=zh_CN.UTF-8 && \
    echo '[OK] Locale zh_CN.UTF-8 generated' && \
    echo '[ACTION] Setting timezone to Asia/Shanghai...' && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
    echo '[OK] Timezone set to Asia/Shanghai' && \
    echo '[ACTION] Cleaning apt cache...' && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    echo '[OK] Stage 1 complete'

# ==================== Stage 2: Install Miniconda3 ====================
COPY offline/ /tmp/offline/

RUN echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 2/7] Install Miniconda3" && \
    echo "# MINICONDA_VERSION=${MINICONDA_VERSION}, CONDA_DIR=/opt/conda" && \
    echo "########################################################################" && \
    echo "" && \
    ARCH=$(uname -m) && \
    echo "[ACTION] Detecting architecture..." && \
    if [ "$ARCH" = "x86_64" ]; then \
        MINICONDA_ARCH="x86_64"; \
        echo "[BRANCH] Architecture: x86_64 (amd64)"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        MINICONDA_ARCH="aarch64"; \
        echo "[BRANCH] Architecture: aarch64 (arm64)"; \
    else \
        echo "[ERROR] Unsupported architecture: $ARCH"; \
        exit 1; \
    fi && \
    echo "[ACTION] Checking for local Miniconda installer in offline/miniconda/..." && \
    LOCAL_INSTALLER=$(ls /tmp/offline/miniconda/Miniconda3-*-Linux-${MINICONDA_ARCH}.sh 2>/dev/null | head -1 || true) && \
    if [ -n "$LOCAL_INSTALLER" ] && [ -s "$LOCAL_INSTALLER" ]; then \
        echo "[BRANCH] Found local installer: $LOCAL_INSTALLER ($(du -h "$LOCAL_INSTALLER" | cut -f1))"; \
        echo "[ACTION] Using local Miniconda installer (offline mode)"; \
        cp "$LOCAL_INSTALLER" /tmp/miniconda.sh; \
        echo "[OK] Local installer copied to /tmp/miniconda.sh"; \
    else \
        echo "[BRANCH] No local installer found, will download from network"; \
        echo "[ACTION] Downloading Miniconda3 (${MINICONDA_VERSION}) for Linux-${MINICONDA_ARCH}..."; \
        echo "[FALLBACK] Attempt 1: Tsinghua TUNA mirror (mirrors.tuna.tsinghua.edu.cn)..."; \
        if wget --tries=5 --timeout=120 --waitretry=5 \
            "https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-${MINICONDA_ARCH}.sh" \
            -O /tmp/miniconda.sh 2>&1; then \
            echo "[OK] Downloaded from TUNA mirror: $(du -h /tmp/miniconda.sh | cut -f1)"; \
        else \
            echo "[WARN] TUNA mirror failed, trying official repo..."; \
            echo "[FALLBACK] Attempt 2: Official Anaconda repo (repo.anaconda.com)..."; \
            wget --tries=5 --timeout=120 --waitretry=5 \
                "https://repo.anaconda.com/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-${MINICONDA_ARCH}.sh" \
                -O /tmp/miniconda.sh || { \
                echo "[ERROR] Failed to download Miniconda from both mirrors!"; \
                exit 1; \
            }; \
            echo "[OK] Downloaded from official repo: $(du -h /tmp/miniconda.sh | cut -f1)"; \
        fi; \
    fi && \
    echo "[ACTION] Verifying installer integrity (size check)..." && \
    INSTALLER_SIZE=$(stat -c%s /tmp/miniconda.sh 2>/dev/null || wc -c < /tmp/miniconda.sh) && \
    echo "[INFO] Installer size: ${INSTALLER_SIZE} bytes" && \
    if [ "$INSTALLER_SIZE" -lt 10000000 ]; then \
        echo "[WARN] Installer file seems too small (<10MB), may be corrupted"; \
    fi && \
    echo "[ACTION] Running Miniconda3 installer (batch mode, prefix=${CONDA_DIR})..." && \
    bash /tmp/miniconda.sh -b -p "${CONDA_DIR}" && \
    echo "[OK] Miniconda3 installed to ${CONDA_DIR}" && \
    rm -f /tmp/miniconda.sh && \
    echo "[ACTION] Initializing conda..." && \
    "${CONDA_DIR}/bin/conda" config --system --set auto_activate_base false && \
    echo "[OK] base auto-activation disabled" && \
    "${CONDA_DIR}/bin/conda" init bash && \
    echo "[OK] conda bash init complete" && \
    echo "[ACTION] Verifying conda installation..." && \
    "${CONDA_DIR}/bin/conda" --version && \
    echo '[OK] Stage 2 complete'

# ==================== Stage 3: Configure Mirrors (conda + pip) ====================
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 3/7] Configure Mirror Sources (conda + pip)" && \
    echo "# conda: Tsinghua TUNA (mirrors.tuna.tsinghua.edu.cn)" && \
    echo "# pip:   Aliyun (mirrors.aliyun.com)" && \
    echo "########################################################################" && \
    echo "" && \
    echo "[ACTION] Writing ${CONDA_DIR}/.condarc (TUNA mirror + pytorch/nvidia channels)..." && \
    printf '%s\n' \
        'channels:' \
        '  - conda-forge' \
        '  - pytorch' \
        '  - nvidia' \
        '  - defaults' \
        'show_channel_urls: true' \
        'default_channels:' \
        '  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main' \
        '  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r' \
        'custom_channels:' \
        '  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud' \
        '  pytorch: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud' \
        '  nvidia: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud' \
        'ssl_verify: true' \
        > "${CONDA_DIR}/.condarc" && \
    echo "[OK] .condarc written:" && \
    cat "${CONDA_DIR}/.condarc" && \
    echo "" && \
    echo "[ACTION] Writing /root/.config/pip/pip.conf (Aliyun mirror)..." && \
    mkdir -p /root/.config/pip && \
    printf '%s\n' \
        '[global]' \
        'index-url = https://mirrors.aliyun.com/pypi/simple/' \
        'trusted-host = mirrors.aliyun.com' \
        'retries = 10' \
        'timeout = 120' \
        > /root/.config/pip/pip.conf && \
    echo "[OK] pip.conf written:" && \
    cat /root/.config/pip/pip.conf && \
    echo "" && \
    echo '[OK] Stage 3 complete'

# ==================== Stage 4: Create conda environment and install PyTorch ====================
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 4/7] Create Conda Env + Install PyTorch (per pytorch.org)" && \
    echo "# USE_GPU=${USE_GPU}" && \
    echo "# PYTHON_VERSION=${PYTHON_VERSION}" && \
    echo "# PYTORCH_VERSION=${PYTORCH_VERSION}" && \
    echo "# CUDA_VERSION=${CUDA_VERSION}" && \
    echo "# Install strategy: local wheels -> PyTorch official index -> Aliyun -> conda fallback" && \
    echo "########################################################################" && \
    echo "" && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && \
    echo "[ACTION] Checking for local conda package cache..." && \
    if [ -d /tmp/offline/conda-pkgs ] && [ -n "$(ls -A /tmp/offline/conda-pkgs/ 2>/dev/null | grep -v '^\.gitkeep$')" ]; then \
        echo "[BRANCH] Found local conda packages in offline/conda-pkgs/, copying to ${CONDA_DIR}/pkgs/"; \
        mkdir -p "${CONDA_DIR}/pkgs"; \
        CONDA_PKG_COUNT=$(ls /tmp/offline/conda-pkgs/*.tar.bz2 2>/dev/null | wc -l); \
        echo "[INFO] Copying ${CONDA_PKG_COUNT} conda packages..."; \
        cp -rn /tmp/offline/conda-pkgs/* "${CONDA_DIR}/pkgs/" 2>/dev/null || true; \
        echo "[OK] Local conda packages copied"; \
    else \
        echo "[BRANCH] No local conda packages found, will download from network"; \
    fi && \
    echo "[ACTION] Creating '${ENV_NAME}' conda environment with Python ${PYTHON_VERSION}..." && \
    echo "[CMD] conda create -y -n ${ENV_NAME} python=${PYTHON_VERSION} pip setuptools wheel numpy" && \
    conda create -y -n "${ENV_NAME}" python="${PYTHON_VERSION}" pip setuptools wheel numpy && \
    echo "[OK] conda env '${ENV_NAME}' created" && \
    conda activate "${ENV_NAME}" && \
    echo "[OK] conda env '${ENV_NAME}' activated, Python: $(python --version)" && \
    echo "[ACTION] Determining PyTorch pip index URL (per pytorch.org/get-started/locally/)..." && \
    if [ "${USE_GPU}" = "1" ]; then \
        CUDA_INDEX="${CUDA_VERSION//./}"; \
        PYTORCH_INDEX="https://download.pytorch.org/whl/cu${CUDA_INDEX}"; \
        echo "[BRANCH] GPU mode: CUDA_VERSION=${CUDA_VERSION} -> index URL: ${PYTORCH_INDEX}"; \
        echo "[INFO] Official install command: pip3 install torch torchvision --index-url ${PYTORCH_INDEX}"; \
    else \
        PYTORCH_INDEX="https://download.pytorch.org/whl/cpu"; \
        echo "[BRANCH] CPU mode -> index URL: ${PYTORCH_INDEX}"; \
        echo "[INFO] Official install command: pip3 install torch torchvision --index-url ${PYTORCH_INDEX}"; \
    fi && \
    echo "" && \
    echo "[ACTION] Installing PyTorch (4-stage fallback strategy)..." && \
    echo "" && \
    PYTORCH_INSTALLED=0 && \
    echo "[STAGE 4.1] Attempt 1/4: Local wheels from offline/wheels/..." && \
    if ls /tmp/offline/wheels/torch-*.whl &>/dev/null 2>&1; then \
        LOCAL_TORCH_COUNT=$(ls /tmp/offline/wheels/torch-*.whl 2>/dev/null | wc -l); \
        LOCAL_TV_COUNT=$(ls /tmp/offline/wheels/torchvision-*.whl 2>/dev/null | wc -l); \
        echo "[BRANCH] Found ${LOCAL_TORCH_COUNT} torch wheel(s) and ${LOCAL_TV_COUNT} torchvision wheel(s) locally"; \
        echo "[CMD] pip install --no-index --find-links=/tmp/offline/wheels torch torchvision"; \
        if pip install --no-cache-dir --no-index --find-links=/tmp/offline/wheels \
            /tmp/offline/wheels/torch-*.whl \
            /tmp/offline/wheels/torchvision-*.whl 2>&1; then \
            echo "[OK] Local torch + torchvision installed"; \
            if ls /tmp/offline/wheels/torchaudio-*.whl &>/dev/null; then \
                echo "[ACTION] Installing torchaudio from local wheels (optional)..."; \
                pip install --no-cache-dir --no-index --find-links=/tmp/offline/wheels \
                    /tmp/offline/wheels/torchaudio-*.whl 2>/dev/null || echo "[WARN] torchaudio install skipped (optional)"; \
            fi; \
            PYTORCH_INSTALLED=1; \
        else \
            echo "[WARN] Local wheel installation failed, will try network..."; \
        fi; \
    else \
        echo "[BRANCH] No local torch wheels found, skipping local install"; \
    fi && \
    if [ "${PYTORCH_INSTALLED}" = "0" ]; then \
        echo ""; \
        echo "[STAGE 4.2] Attempt 2/4: pip from official PyTorch index (${PYTORCH_INDEX})..."; \
        echo "[CMD] pip install torch==${PYTORCH_VERSION} torchvision --index-url ${PYTORCH_INDEX}"; \
        if pip install --no-cache-dir \
            "torch==${PYTORCH_VERSION}" \
            "torchvision" \
            --index-url "${PYTORCH_INDEX}" 2>&1; then \
            echo "[OK] PyTorch installed from official PyTorch index"; \
            PYTORCH_INSTALLED=1; \
        else \
            echo "[WARN] Official PyTorch index failed, trying Aliyun mirror..."; \
        fi; \
    fi && \
    if [ "${PYTORCH_INSTALLED}" = "0" ]; then \
        echo ""; \
        echo "[STAGE 4.3] Attempt 3/4: pip from default (Aliyun mirror)..."; \
        echo "[CMD] pip install torch==${PYTORCH_VERSION} torchvision (uses configured Aliyun index)"; \
        echo "[WARN] Note: Aliyun mirror wheels may be CPU-only; GPU builds should use official index"; \
        if pip install --no-cache-dir \
            "torch==${PYTORCH_VERSION}" \
            "torchvision" 2>&1; then \
            echo "[OK] PyTorch installed from Aliyun mirror"; \
            PYTORCH_INSTALLED=1; \
        else \
            echo "[WARN] Aliyun mirror failed, trying conda as final fallback..."; \
        fi; \
    fi && \
    if [ "${PYTORCH_INSTALLED}" = "0" ]; then \
        echo ""; \
        echo "[STAGE 4.4] Attempt 4/4: conda install (final fallback)..."; \
        if [ "${USE_GPU}" = "1" ]; then \
            echo "[BRANCH] GPU mode: conda install pytorch=${PYTORCH_VERSION} torchvision pytorch-cuda=${CUDA_VERSION}"; \
            echo "[CMD] conda install -y -n ${ENV_NAME} pytorch=${PYTORCH_VERSION} torchvision pytorch-cuda=${CUDA_VERSION} -c nvidia -c pytorch -c conda-forge"; \
            conda install -y -n "${ENV_NAME}" \
                "pytorch=${PYTORCH_VERSION}" \
                "torchvision" \
                "pytorch-cuda=${CUDA_VERSION}" \
                -c nvidia -c pytorch -c conda-forge || { \
                echo "[ERROR] All PyTorch installation methods failed!"; \
                exit 1; \
            }; \
        else \
            echo "[BRANCH] CPU mode: conda install pytorch=${PYTORCH_VERSION} torchvision cpuonly"; \
            echo "[CMD] conda install -y -n ${ENV_NAME} pytorch=${PYTORCH_VERSION} torchvision cpuonly -c pytorch -c conda-forge"; \
            conda install -y -n "${ENV_NAME}" \
                "pytorch=${PYTORCH_VERSION}" \
                "torchvision" \
                cpuonly \
                -c pytorch -c conda-forge || { \
                echo "[ERROR] All PyTorch installation methods failed!"; \
                exit 1; \
            }; \
        fi; \
        echo "[OK] PyTorch installed via conda fallback"; \
        PYTORCH_INSTALLED=1; \
    fi && \
    echo "" && \
    if [ "${PYTORCH_INSTALLED}" = "1" ]; then \
        echo "[OK] PyTorch installation succeeded"; \
    fi && \
    echo "[ACTION] Installing additional local wheels (if any remain)..."; \
    if ls /tmp/offline/wheels/*.whl &>/dev/null 2>&1; then \
        ADDITIONAL_WHEELS=$(ls /tmp/offline/wheels/*.whl 2>/dev/null | grep -v -E 'torch-|torchvision-|torchaudio-' | wc -l); \
        if [ "$ADDITIONAL_WHEELS" -gt 0 ]; then \
            echo "[INFO] Found ${ADDITIONAL_WHEELS} additional wheel(s), installing..."; \
            pip install --no-cache-dir --no-index --find-links=/tmp/offline/wheels \
                $(ls /tmp/offline/wheels/*.whl 2>/dev/null | grep -v -E 'torch-|torchvision-|torchaudio-') 2>/dev/null || \
                echo "[WARN] Some additional wheels failed to install (non-critical)"; \
            echo "[OK] Additional wheels processed"; \
        else \
            echo "[INFO] No additional wheels to install (all were torch-related)"; \
        fi; \
    fi && \
    echo "" && \
    echo "[ACTION] Verifying PyTorch import (post-install check)..." && \
    python -c "import torch; print(f'[OK] PyTorch {torch.__version__} loaded successfully')" && \
    python -c "import torch; print(f'[OK] CUDA available: {torch.cuda.is_available()}')" && \
    python -c "import torchvision; print(f'[OK] torchvision {torchvision.__version__} loaded')" && \
    echo "" && \
    echo "[ACTION] Cleaning up..." && \
    echo "[INFO] Removing /tmp/offline to reduce image size..."; \
    rm -rf /tmp/offline && \
    echo "[INFO] Running conda clean -ya..."; \
    conda clean -ya && \
    echo "[INFO] Running pip cache purge..."; \
    pip cache purge 2>/dev/null || true && \
    echo '[OK] Stage 4 complete'

# ==================== Stage 5: Create non-root user 'ai' ====================
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 5/7] Create Non-Root User 'ai' (UID 1000)" && \
    echo "########################################################################" && \
    echo "" && \
    echo "[ACTION] Checking for existing ubuntu user (UID 1000 conflict)..." && \
    if id ubuntu &>/dev/null; then \
        echo "[BRANCH] Found default 'ubuntu' user (UID 1000), removing to avoid conflict..."; \
        userdel -r ubuntu 2>/dev/null || true; \
        echo "[OK] Default ubuntu user removed"; \
    else \
        echo "[BRANCH] No ubuntu user found, no conflict"; \
    fi && \
    echo "[ACTION] Creating user 'ai' (UID 1000, GID 1000, bash shell, sudo group)..."; \
    useradd -m -s /bin/bash -u 1000 -U -G sudo ai && \
    echo "[OK] User 'ai' created" && \
    echo "[ACTION] Configuring passwordless sudo for 'ai'..."; \
    echo "ai ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ai && \
    chmod 0440 /etc/sudoers.d/ai && \
    echo "[OK] Passwordless sudo configured" && \
    echo "[ACTION] Copying pip/conda configs to /home/ai/..."; \
    mkdir -p /home/ai/.config/pip && \
    cp /root/.config/pip/pip.conf /home/ai/.config/pip/pip.conf && \
    cp "${CONDA_DIR}/.condarc" /home/ai/.condarc && \
    echo "[OK] Configs copied for user 'ai'" && \
    echo "[ACTION] Configuring conda auto-activation in /home/ai/.bashrc..."; \
    echo "source ${CONDA_DIR}/etc/profile.d/conda.sh" >> /home/ai/.bashrc && \
    echo "conda activate ${ENV_NAME}" >> /home/ai/.bashrc && \
    echo "[OK] ai .bashrc configured" && \
    echo "[ACTION] Configuring conda auto-activation in /root/.bashrc..."; \
    echo "source ${CONDA_DIR}/etc/profile.d/conda.sh" >> /root/.bashrc && \
    echo "conda activate ${ENV_NAME}" >> /root/.bashrc && \
    echo "[OK] root .bashrc configured" && \
    echo "[ACTION] Creating /etc/profile.d/conda-init.sh for login shell activation..."; \
    printf '%s\n' \
        '#!/bin/bash' \
        'source /opt/conda/etc/profile.d/conda.sh' \
        'conda activate pytorch 2>/dev/null || true' \
        > /etc/profile.d/conda-init.sh && \
    chmod +x /etc/profile.d/conda-init.sh && \
    echo "[OK] conda-init.sh created in profile.d/" && \
    echo "[ACTION] Setting ownership of /home/ai and /workspace to ai:ai..."; \
    chown -R ai:ai /home/ai /workspace && \
    echo "[OK] Ownership set" && \
    echo '[OK] Stage 5 complete'

# ==================== Stage 6: Install entrypoint ====================
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 6/7] Install Entrypoint" && \
    echo "########################################################################" && \
    echo "" && \
    echo "[ACTION] Setting entrypoint.sh permissions..."; \
    chmod +x /usr/local/bin/entrypoint.sh && \
    echo "[OK] Entrypoint installed at /usr/local/bin/entrypoint.sh" && \
    ls -la /usr/local/bin/entrypoint.sh && \
    echo '[OK] Stage 6 complete'

# ==================== Stage 7: Final validation and metadata ====================
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 7/7] Final Validation + Metadata" && \
    echo "########################################################################" && \
    echo "" && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && \
    conda activate "${ENV_NAME}" && \
    echo "[VALIDATE] Python version..."; \
    python --version && \
    PYTHON_PATH=$(which python) && \
    echo "[VALIDATE] Python binary: ${PYTHON_PATH}"; \
    if [[ "$PYTHON_PATH" != "${ENV_PATH}/bin/python" ]]; then \
        echo "[WARN] Python not from expected conda env path (${ENV_PATH}/bin/python)"; \
    fi && \
    echo "[VALIDATE] Conda environments:"; \
    conda info --envs && \
    echo "" && \
    echo "[VALIDATE] PyTorch import and version..."; \
    python -c "import torch; print(f'  PyTorch version: {torch.__version__}')" && \
    python -c "import torchvision; print(f'  torchvision version: {torchvision.__version__}')" && \
    python -c "import numpy; print(f'  numpy version: {numpy.__version__}')" && \
    echo "" && \
    echo "[VALIDATE] Tensor operations per official guide (x = torch.rand(5,3))..."; \
    python -c "import torch; x = torch.rand(5, 3); print(x); assert x.shape == (5, 3), f'Expected (5,3), got {x.shape}'; print('  Shape check PASSED: (5, 3)')" && \
    echo "" && \
    echo "[VALIDATE] CUDA availability..."; \
    python -c "import torch; print(f'  CUDA available: {torch.cuda.is_available()}'); import os; gpu_build=os.environ.get('USE_GPU','0'); print(f'  GPU build flag: {gpu_build}')" && \
    echo "" && \
    echo "[ACTION] Writing build metadata to /etc/pytorch-base-build-info..."; \
    printf 'PYTORCH_BASE_IMAGE=%s\nUSE_GPU=%s\nPYTHON_VERSION=%s\nPYTORCH_VERSION=%s\nCUDA_VERSION=%s\nCONDA_DIR=%s\nENV_NAME=%s\nBUILD_DATE=%s\nENTRYPOINT_QUIET=%s\n' \
        "${BASE_IMAGE}" "${USE_GPU}" "${PYTHON_VERSION}" "${PYTORCH_VERSION}" \
        "${CUDA_VERSION}" "${CONDA_DIR}" "${ENV_NAME}" \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        "${QUIET}" \
        > /etc/pytorch-base-build-info && \
    echo "[OK] Build metadata written:" && \
    cat /etc/pytorch-base-build-info && \
    echo "" && \
    echo "[ACTION] Fixing executable stack flags on PyTorch .so files (prevents warnings)..."; \
    python -c " \
import os, struct, glob \
lib_dir = os.path.join('${ENV_PATH}', 'lib', 'python${PYTHON_VERSION}', 'site-packages', 'torch', 'lib') \
fixed = 0 \
if os.path.isdir(lib_dir): \
    for so_path in glob.glob(os.path.join(lib_dir, '*.so')): \
        with open(so_path, 'r+b') as f: \
            magic = f.read(4) \
            if magic != b'\x7fELF': continue \
            f.seek(0) \
            hdr = f.read(64) \
            if len(hdr) < 64 or hdr[4] != 2: continue \
            e_phoff = struct.unpack('<Q', hdr[32:40])[0] \
            e_phentsize = struct.unpack('<H', hdr[54:56])[0] \
            e_phnum = struct.unpack('<H', hdr[56:58])[0] \
            for i in range(e_phnum): \
                f.seek(e_phoff + i * e_phentsize) \
                phdr = f.read(e_phentsize) \
                p_type = struct.unpack('<I', phdr[0:4])[0] \
                if p_type == 0x6474e551: \
                    p_flags = struct.unpack('<I', phdr[4:8])[0] \
                    if p_flags & 1: \
                        f.seek(e_phoff + i * e_phentsize + 4) \
                        f.write(struct.pack('<I', p_flags & ~1)) \
                        fixed += 1 \
print(f'[OK] Fixed executable stack flag on {fixed} .so files') \
" 2>/dev/null || echo "[INFO] Stack flag fix skipped (non-critical on some platforms)" && \
    echo "" && \
    echo "########################################################################" && \
    echo "# ALL 7 STAGES COMPLETED SUCCESSFULLY!" && \
    echo "########################################################################"

# ==================== Runtime Configuration ====================
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["/bin/bash", "-l"]
USER ai
