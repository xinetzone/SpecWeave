# syntax=docker/dockerfile:1.7-labs
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
# Runtime Stage Layering (dockerfile-runtime-logical-layering pattern v1.3):
#   Stage 1/7: 系统包 + locale/timezone + APT镜像配置 (变化频率: 最低)
#   Stage 2/7: Miniconda3 安装 (变化频率: 低)
#   Stage 3/7: conda + pip 镜像源配置 (变化频率: 低)
#   Stage 4/7: conda环境创建 + PyTorch安装 (变化频率: 中, 主要耗时阶段)
#   Stage 5/7: 非root用户'ai'创建 + 权限配置 (变化频率: 中)
#   Stage 6/7: entrypoint安装 + 集中配置COPY + 语法验证 (变化频率: 高)
#   Stage 7/7: build-info + 最终验证 + 耗时汇总表 (变化频率: 最低)
#
# Build Timing: 每个Stage结束时输出 [TIMER] 本阶段耗时+累计耗时，最终输出汇总表
#
# Build log prefixes:
#   [STAGE]  - Current build stage marker
#   [ACTION] - Action being performed
#   [OK]     - Action completed successfully
#   [WARN]   - Non-fatal warning
#   [ERROR]  - Fatal error (should cause exit)
#   [TIMER]  - Timing statistics
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
      version="2.2.0"

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

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

WORKDIR /workspace

# ═══════════════════════════════════════════════════════════════════
# Stage 1/7: 系统包安装 + locale/timezone + APT镜像配置
# 变化频率：最低（基础镜像确定后很少改）
# 初始化计时器 /tmp/.build-timer
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 1/7] System Packages + Chinese Locale" && \
    echo "# BASE_IMAGE=${BASE_IMAGE}, TZ=Asia/Shanghai, LANG=zh_CN.UTF-8" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[TIMER] Build started at $(date -u +%Y-%m-%dT%H:%M:%SZ)" && \
    echo "START=$_STAGE_START" > /tmp/.build-timer && \
    echo "[ACTION] Detecting sources.list format..." && \
    (cp /etc/apt/sources.list.d/ubuntu.sources /etc/apt/sources.list.d/ubuntu.sources.bak 2>/dev/null || true) && \
    if [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then \
        echo "[ACTION] Using deb822 format (ubuntu.sources)"; \
        SOURCES_FILE="/etc/apt/sources.list.d/ubuntu.sources"; \
        sed -i 's|http://archive.ubuntu.com|http://mirrors.aliyun.com|g' "$SOURCES_FILE"; \
        sed -i 's|http://security.ubuntu.com|http://mirrors.aliyun.com|g' "$SOURCES_FILE"; \
        sed -i 's|https://archive.ubuntu.com|http://mirrors.aliyun.com|g' "$SOURCES_FILE"; \
        sed -i 's|https://security.ubuntu.com|http://mirrors.aliyun.com|g' "$SOURCES_FILE"; \
    else \
        echo "[ACTION] Using traditional sources.list format"; \
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
    echo '[INFO] Updating APT package lists...' && \
    apt-get update -qq && \
    echo '[OK] APT package lists updated' && \
    echo '[INFO] Installing 12 system packages (ca-certificates, tzdata, locales, tini, gosu, wget, build-essential, etc.)...' && \
    apt-get install -y --no-install-recommends -qq \
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
    && echo '[OK] System packages installed' && \
    echo '[INFO] Verifying key package versions:' && \
    echo "  - ca-certificates: $(dpkg-query -W -f='${Version}' ca-certificates 2>/dev/null || echo 'N/A')" && \
    echo "  - tini: $(dpkg-query -W -f='${Version}' tini 2>/dev/null || echo 'N/A')" && \
    echo "  - build-essential: $(dpkg-query -W -f='${Version}' build-essential 2>/dev/null || echo 'N/A')" && \
    echo "  - git: $(git --version 2>&1 | awk '{print $3}')" && \
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
    rm -rf /var/lib/apt/lists/* && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _TOTAL=$((_NOW - $(grep '^START=' /tmp/.build-timer | cut -d= -f2))) && \
    echo "S1=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 1/7 (system+locale) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 1 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 2/7: Miniconda3 安装（支持离线/在线 fallback）
# 变化频率：低（Miniconda版本升级时改）
# ═══════════════════════════════════════════════════════════════════
COPY offline/ /tmp/offline/

RUN echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 2/7] Install Miniconda3" && \
    echo "# MINICONDA_VERSION=${MINICONDA_VERSION}, CONDA_DIR=/opt/conda" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    ARCH=$(uname -m) && \
    echo "[ACTION] Detecting architecture..." && \
    if [ "$ARCH" = "x86_64" ]; then \
        MINICONDA_ARCH="x86_64"; \
        echo "[OK] Architecture: x86_64 (amd64)"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        MINICONDA_ARCH="aarch64"; \
        echo "[OK] Architecture: aarch64 (arm64)"; \
    else \
        echo "[ERROR] Unsupported architecture: $ARCH"; \
        exit 1; \
    fi && \
    echo "[ACTION] Checking for local Miniconda installer in offline/miniconda/..." && \
    LOCAL_INSTALLER=$(ls /tmp/offline/miniconda/Miniconda3-*-Linux-${MINICONDA_ARCH}.sh 2>/dev/null | head -1 || true) && \
    if [ -n "$LOCAL_INSTALLER" ] && [ -s "$LOCAL_INSTALLER" ]; then \
        echo "[OK] Found local installer: $LOCAL_INSTALLER ($(du -h "$LOCAL_INSTALLER" | cut -f1))"; \
        echo "[ACTION] Using local Miniconda installer (offline mode)"; \
        cp "$LOCAL_INSTALLER" /tmp/miniconda.sh; \
        echo "[OK] Local installer copied to /tmp/miniconda.sh"; \
    else \
        echo "[ACTION] No local installer found, will download from network"; \
        echo "[ACTION] Downloading Miniconda3 (${MINICONDA_VERSION}) for Linux-${MINICONDA_ARCH}..."; \
        echo "[ACTION] Attempt 1: Tsinghua TUNA mirror (mirrors.tuna.tsinghua.edu.cn)..."; \
        if wget --tries=5 --timeout=120 --waitretry=5 \
            "https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-${MINICONDA_ARCH}.sh" \
            -O /tmp/miniconda.sh 2>&1; then \
            echo "[OK] Downloaded from TUNA mirror: $(du -h /tmp/miniconda.sh | cut -f1)"; \
        else \
            echo "[WARN] TUNA mirror failed, trying official repo..."; \
            echo "[ACTION] Attempt 2: Official Anaconda repo (repo.anaconda.com)..."; \
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
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S2=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 2/7 (Miniconda install) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 2 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 3/7: conda + pip 镜像源配置
# 变化频率：低（镜像源地址变更时改）
# ═══════════════════════════════════════════════════════════════════
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 3/7] Configure Mirror Sources (conda + pip)" && \
    echo "# conda: Tsinghua TUNA (mirrors.tuna.tsinghua.edu.cn)" && \
    echo "# pip:   Aliyun (mirrors.aliyun.com)" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
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
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S3=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 3/7 (mirror config) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 3 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 4/7: conda环境创建 + PyTorch安装（4级fallback策略）
# 变化频率：中（PyTorch版本升级时改，主要耗时阶段）
# ═══════════════════════════════════════════════════════════════════
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
    _STAGE_START=$(date +%s) && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && \
    echo "[ACTION] Checking for local conda package cache..." && \
    if [ -d /tmp/offline/conda-pkgs ] && [ -n "$(ls -A /tmp/offline/conda-pkgs/ 2>/dev/null | grep -v '^\.gitkeep$')" ]; then \
        echo "[OK] Found local conda packages in offline/conda-pkgs/, copying to ${CONDA_DIR}/pkgs/"; \
        mkdir -p "${CONDA_DIR}/pkgs"; \
        CONDA_PKG_COUNT=$(ls /tmp/offline/conda-pkgs/*.tar.bz2 2>/dev/null | wc -l); \
        echo "[INFO] Copying ${CONDA_PKG_COUNT} conda packages..."; \
        cp -rn /tmp/offline/conda-pkgs/* "${CONDA_DIR}/pkgs/" 2>/dev/null || true; \
        echo "[OK] Local conda packages copied"; \
    else \
        echo "[INFO] No local conda packages found, will download from network"; \
    fi && \
    echo "[ACTION] Creating '${ENV_NAME}' conda environment with Python ${PYTHON_VERSION}..." && \
    echo "[INFO] Installing conda packages: python=${PYTHON_VERSION}, pip, setuptools, wheel, numpy" && \
    echo "[CMD] conda create -y -n ${ENV_NAME} python=${PYTHON_VERSION} pip setuptools wheel numpy" && \
    conda create -y -n "${ENV_NAME}" python="${PYTHON_VERSION}" pip setuptools wheel numpy && \
    echo "[OK] conda env '${ENV_NAME}' created" && \
    conda activate "${ENV_NAME}" && \
    echo "[OK] conda env '${ENV_NAME}' activated, Python: $(python --version)" && \
    echo "[INFO] Verifying conda key packages:" && \
    conda list | grep -iE 'python|pip|setuptools|wheel|numpy' || true && \
    echo "[ACTION] Determining PyTorch pip index URL (per pytorch.org/get-started/locally/)..." && \
    if [ "${USE_GPU}" = "1" ]; then \
        CUDA_INDEX="${CUDA_VERSION//./}"; \
        PYTORCH_INDEX="https://download.pytorch.org/whl/cu${CUDA_INDEX}"; \
        echo "[INFO] GPU mode: CUDA_VERSION=${CUDA_VERSION} -> index URL: ${PYTORCH_INDEX}"; \
    else \
        PYTORCH_INDEX="https://download.pytorch.org/whl/cpu"; \
        echo "[INFO] CPU mode -> index URL: ${PYTORCH_INDEX}"; \
    fi && \
    echo "" && \
    echo "[ACTION] Installing PyTorch (4-stage fallback strategy)..." && \
    echo "" && \
    PYTORCH_INSTALLED=0 && \
    echo "[STAGE 4.1] Attempt 1/4: Local wheels from offline/wheels/..." && \
    if ls /tmp/offline/wheels/torch-*.whl &>/dev/null 2>&1; then \
        LOCAL_TORCH_COUNT=$(ls /tmp/offline/wheels/torch-*.whl 2>/dev/null | wc -l); \
        LOCAL_TV_COUNT=$(ls /tmp/offline/wheels/torchvision-*.whl 2>/dev/null | wc -l); \
        echo "[INFO] Found ${LOCAL_TORCH_COUNT} torch wheel(s) and ${LOCAL_TV_COUNT} torchvision wheel(s) locally"; \
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
        echo "[INFO] No local torch wheels found, skipping local install"; \
    fi && \
    if [ "${PYTORCH_INSTALLED}" = "0" ]; then \
        echo ""; \
        echo "[STAGE 4.2] Attempt 2/4: pip from official PyTorch index (${PYTORCH_INDEX})..."; \
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
            echo "[INFO] GPU mode: conda install pytorch=${PYTORCH_VERSION} torchvision pytorch-cuda=${CUDA_VERSION}"; \
            conda install -y -n "${ENV_NAME}" \
                "pytorch=${PYTORCH_VERSION}" \
                "torchvision" \
                "pytorch-cuda=${CUDA_VERSION}" \
                -c nvidia -c pytorch -c conda-forge || { \
                echo "[ERROR] All PyTorch installation methods failed!"; \
                exit 1; \
            }; \
        else \
            echo "[INFO] CPU mode: conda install pytorch=${PYTORCH_VERSION} torchvision cpuonly"; \
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
    echo "[INFO] Key pip packages:" && \
    pip list --format=columns 2>/dev/null | grep -iE 'torch|numpy|pip|setuptools|wheel' || true && \
    echo "" && \
    echo "[ACTION] Cleaning up..." && \
    echo "[INFO] Removing /tmp/offline to reduce image size..."; \
    rm -rf /tmp/offline && \
    echo "[INFO] Running conda clean -ya..."; \
    conda clean -ya && \
    echo "[INFO] Running pip cache purge..."; \
    pip cache purge 2>/dev/null || true && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S4=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 4/7 (conda env+PyTorch) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 4 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 5/7: 非root用户 'ai' 创建 + 权限配置 + shell初始化
# 变化频率：中（新增用户/目录/配置时改）
# ═══════════════════════════════════════════════════════════════════
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 5/7] Create Non-Root User 'ai' (UID 1000)" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[ACTION] Checking for existing ubuntu user (UID 1000 conflict)..." && \
    if id ubuntu &>/dev/null; then \
        echo "[INFO] Found default 'ubuntu' user (UID 1000), removing to avoid conflict..."; \
        userdel -r ubuntu 2>/dev/null || true; \
        echo "[OK] Default ubuntu user removed"; \
    else \
        echo "[INFO] No ubuntu user found, no conflict"; \
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
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S5=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 5/7 (user+perms) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 5 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 6/7: entrypoint安装 + 语法验证
# 变化频率：高（配置调整时改，缓存不会让前面层失效）
# ═══════════════════════════════════════════════════════════════════
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

RUN echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 6/7] Install Entrypoint + Syntax Validation" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[ACTION] Setting entrypoint.sh permissions..."; \
    chmod +x /usr/local/bin/entrypoint.sh && \
    echo "[OK] Entrypoint installed at /usr/local/bin/entrypoint.sh" && \
    ls -la /usr/local/bin/entrypoint.sh && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│  [VALIDATION CHECKPOINT - Stage 6/7]            │" && \
    echo "│  Running syntax validation for entrypoint       │" && \
    echo "└─────────────────────────────────────────────────┘" && \
    echo "[VALIDATE] bash -n entrypoint.sh..." && \
    bash -n /usr/local/bin/entrypoint.sh && echo "[OK] entrypoint.sh bash syntax valid" && \
    echo "" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S6=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 6/7 (entrypoint+validate) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 6 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 7/7: build-info + 最终验证 + 耗时汇总表 + 清理
# 变化频率：最低（版本发布时改）
# ═══════════════════════════════════════════════════════════════════
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 7/7] Final Validation + Metadata + Timing Summary" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && \
    conda activate "${ENV_NAME}" && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│  [FINAL VERIFICATION - Stage 7/7]               │" && \
    echo "│  Verifying all critical components              │" && \
    echo "└─────────────────────────────────────────────────┘" && \
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
    echo "[VALIDATE] tini available..."; \
    tini --version >/dev/null 2>&1 && echo "[OK] tini (init) available" && \
    bash -n /usr/local/bin/entrypoint.sh && echo "[OK] entrypoint.sh syntax valid" && \
    echo "" && \
    echo "[ACTION] Writing build metadata to /etc/pytorch-base-build-info..."; \
    printf 'PYTORCH_BASE_IMAGE=%s\nUSE_GPU=%s\nPYTHON_VERSION=%s\nPYTORCH_VERSION=%s\nCUDA_VERSION=%s\nCONDA_DIR=%s\nENV_NAME=%s\nBUILD_DATE=%s\nENTRYPOINT_QUIET=%s\nBUILD_TIMER=enabled\n' \
        "${BASE_IMAGE}" "${USE_GPU}" "${PYTHON_VERSION}" "${PYTORCH_VERSION}" \
        "${CUDA_VERSION}" "${CONDA_DIR}" "${ENV_NAME}" \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        "${QUIET}" \
        > /etc/pytorch-base-build-info && \
    echo "[OK] Build metadata written:" && \
    cat /etc/pytorch-base-build-info && \
    echo "" && \
    echo "[ACTION] Fixing executable stack flags on PyTorch .so files (prevents warnings)..."; \
    python -c "
import os, struct, glob
lib_dir = os.path.join('${ENV_PATH}', 'lib', 'python${PYTHON_VERSION}', 'site-packages', 'torch', 'lib')
fixed = 0
if os.path.isdir(lib_dir):
    for so_path in glob.glob(os.path.join(lib_dir, '*.so')):
        with open(so_path, 'r+b') as f:
            magic = f.read(4)
            if magic != b'\x7fELF': continue
            f.seek(0)
            hdr = f.read(64)
            if len(hdr) < 64 or hdr[4] != 2: continue
            e_phoff = struct.unpack('<Q', hdr[32:40])[0]
            e_phentsize = struct.unpack('<H', hdr[54:56])[0]
            e_phnum = struct.unpack('<H', hdr[56:58])[0]
            for i in range(e_phnum):
                f.seek(e_phoff + i * e_phentsize)
                phdr = f.read(e_phentsize)
                p_type = struct.unpack('<I', phdr[0:4])[0]
                if p_type == 0x6474e551:
                    p_flags = struct.unpack('<I', phdr[4:8])[0]
                    if p_flags & 1:
                        f.seek(e_phoff + i * e_phentsize + 4)
                        f.write(struct.pack('<I', p_flags & ~1))
                        fixed += 1
print(f'[OK] Fixed executable stack flag on {fixed} .so files')
" 2>/dev/null || echo "[INFO] Stack flag fix skipped (non-critical on some platforms)" && \
    echo "" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _S1=$(grep '^S1=' /tmp/.build-timer | cut -d= -f2) && \
    _S2=$(grep '^S2=' /tmp/.build-timer | cut -d= -f2) && \
    _S3=$(grep '^S3=' /tmp/.build-timer | cut -d= -f2) && \
    _S4=$(grep '^S4=' /tmp/.build-timer | cut -d= -f2) && \
    _S5=$(grep '^S5=' /tmp/.build-timer | cut -d= -f2) && \
    _S6=$(grep '^S6=' /tmp/.build-timer | cut -d= -f2) && \
    _T1=$((_S1 - _START)) && \
    _T2=$((_S2 - _S1)) && \
    _T3=$((_S3 - _S2)) && \
    _T4=$((_S4 - _S3)) && \
    _T5=$((_S5 - _S4)) && \
    _T6=$((_S6 - _S5)) && \
    _T7=$_ELAPSED && \
    _TOTAL=$((_NOW - _START)) && \
    echo "╔══════════════════════════════════════════════════════════════╗" && \
    echo "║         BUILD TIMING SUMMARY (PyTorch Base)                ║" && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  Stage 1/7  system packages + locale   %5ds               ║\n" $_T1 && \
    printf "║  Stage 2/7  Miniconda3 install         %5ds               ║\n" $_T2 && \
    printf "║  Stage 3/7  conda/pip mirror config    %5ds               ║\n" $_T3 && \
    printf "║  Stage 4/7  conda env + PyTorch        %5ds  ★ hotspot    ║\n" $_T4 && \
    printf "║  Stage 5/7  user ai + permissions      %5ds               ║\n" $_T5 && \
    printf "║  Stage 6/7  entrypoint + validation    %5ds               ║\n" $_T6 && \
    printf "║  Stage 7/7  metadata + final verify    %5ds               ║\n" $_T7 && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  BUILD TOTAL                           %5ds               ║\n" $_TOTAL && \
    echo "╚══════════════════════════════════════════════════════════════╝" && \
    echo "" && \
    rm -f /tmp/.build-timer /tmp/* /var/tmp/* && \
    echo "########################################################################" && \
    echo "# ALL 7 STAGES COMPLETED SUCCESSFULLY!" && \
    echo "########################################################################"

# ==================== Runtime Configuration ====================
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["/bin/bash", "-l"]
USER ai
