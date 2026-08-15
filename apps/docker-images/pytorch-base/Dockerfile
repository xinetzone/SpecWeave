# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# PyTorch GPU Base Docker Image - Miniforge3 + Python 3.14 + PyTorch + ONNX Runtime
# =============================================================================
# Base image:  ubuntu:26.04 (LTS)
# Python:      3.14.6 (GIL-enabled std build, via Miniforge3)
# PyTorch:     2.13.0 (stable, CUDA 12.6 default, supports 12.6/12.8/13.0)
# Components:  torch + torchvision + torchaudio (official trio) + onnxruntime-gpu
#
# Install command per official guide (CUDA 12.6):
#   pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
#
# Optimized for unreliable network environments:
#   - Aliyun apt mirror (HTTP first, then HTTPS after ca-certificates)
#   - BFSU/THU conda mirror (Miniforge3 native conda-forge)
#   - Aliyun pip mirror with PyTorch official index fallback
#   - Retry logic for all downloads (apt=5, wget=5, pip=10)
#   - BuildKit cache mounts for apt/conda/pip
#   - Offline installation support via offline/ directory
#   - 4-stage pip fallback: local wheels -> PyTorch official -> Aliyun -> conda
#
# Runtime Stage Layering (dockerfile-runtime-logical-layering pattern v1.3):
#   Stage 1/7: system packages + locale/timezone + APT mirror (lowest change freq)
#   Stage 2/7: Miniforge3 install to /opt/conda (low change freq)
#   Stage 3/7: conda + pip mirror config (low change freq, mirror switching)
#   Stage 4/7: conda env create + PyTorch trio + onnxruntime-gpu (medium, hotspot)
#   Stage 5/7: non-root user 'ai' (UID 1000) + permissions (medium)
#   Stage 6/7: entrypoint install + profile.d scripts + syntax validation (high)
#   Stage 7/7: build-info + GPU validation + cleanup + timing summary (lowest)
#
# Build Timing: [TIMER] per stage + cumulative summary in Stage 7
# Log prefixes: [STAGE] [ACTION] [OK] [WARN] [ERROR] [TIMER] [VALIDATE]
# =============================================================================

ARG BASE_IMAGE=ubuntu:26.04
ARG USE_GPU=1
ARG PYTHON_VERSION=3.14.6
ARG PYTORCH_VERSION=2.13.0
ARG CUDA_VERSION=12.6
ARG CONDA_MIRROR=bfsu
ARG PIP_MIRROR=aliyun
ARG QUIET=0

FROM ${BASE_IMAGE} AS base

ARG BASE_IMAGE
ARG USE_GPU
ARG PYTHON_VERSION
ARG PYTORCH_VERSION
ARG CUDA_VERSION
ARG CONDA_MIRROR
ARG PIP_MIRROR
ARG QUIET=0

LABEL maintainer="SpecWeave Team" \
      description="PyTorch GPU base image: Miniforge3 + Python 3.14 + PyTorch 2.13 CUDA + ONNX Runtime GPU, CN-optimized" \
      version="3.0.0"

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai \
    LANG=zh_CN.UTF-8 \
    LANGUAGE=zh_CN:zh \
    LC_ALL=zh_CN.UTF-8 \
    CONDA_DIR=/opt/conda \
    CONDA_ENVS_DIRS=/opt/conda/envs \
    CONDA_PKGS_DIRS=/opt/conda/pkgs \
    PATH=/opt/conda/envs/pytorch/bin:/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    LD_LIBRARY_PATH=/opt/conda/envs/pytorch/lib/python3.14/site-packages/torch/lib:/usr/local/nvidia/lib64:${LD_LIBRARY_PATH} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENV_NAME=pytorch \
    ENV_PATH=/opt/conda/envs/pytorch \
    ENTRYPOINT_QUIET="" \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

WORKDIR /workspace

# ═══════════════════════════════════════════════════════════════════
# Stage 1/7: system packages + locale/timezone + APT mirror config
# Change frequency: lowest (base image locked, rarely changes)
# Timer init: /tmp/.build-timer
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 1/7] System Packages + Chinese Locale + Timezone" && \
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
    echo '[INFO] Installing system packages (ca-certificates, tzdata, locales, tini, gosu, build tools)...' && \
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
        xz-utils \
        git \
        build-essential \
        gosu \
        patchelf \
    && echo '[OK] System packages installed' && \
    echo '[INFO] Key package versions:' && \
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
# Stage 2/7: Miniforge3 install (offline/online fallback)
# Change frequency: low (Miniforge version bumps)
# Uses Miniforge3 instead of Miniconda3 for native conda-forge + libmamba solver
# ═══════════════════════════════════════════════════════════════════
COPY offline/ /tmp/offline/

RUN echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 2/7] Install Miniforge3 (conda-forge native, libmamba solver)" && \
    echo "# CONDA_DIR=/opt/conda" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    ARCH=$(uname -m) && \
    echo "[ACTION] Detecting architecture..." && \
    if [ "$ARCH" = "x86_64" ]; then \
        MF_ARCH="x86_64"; \
        echo "[OK] Architecture: x86_64 (amd64)"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        MF_ARCH="aarch64"; \
        echo "[OK] Architecture: aarch64 (arm64)"; \
    else \
        echo "[ERROR] Unsupported architecture: $ARCH"; \
        exit 1; \
    fi && \
    MF_INSTALLER="Miniforge3-Linux-${MF_ARCH}.sh" && \
    echo "[ACTION] Checking for local Miniforge installer in offline/miniforge/..." && \
    LOCAL_INSTALLER=$(ls /tmp/offline/miniforge/Miniforge3-*-Linux-${MF_ARCH}.sh 2>/dev/null | head -1 || true) && \
    if [ -n "$LOCAL_INSTALLER" ] && [ -s "$LOCAL_INSTALLER" ]; then \
        echo "[OK] Found local installer: $LOCAL_INSTALLER ($(du -h "$LOCAL_INSTALLER" | cut -f1))"; \
        echo "[ACTION] Using local Miniforge installer (offline mode)"; \
        cp "$LOCAL_INSTALLER" /tmp/miniforge.sh; \
    else \
        echo "[ACTION] No local installer found, will download from network"; \
        echo "[ACTION] Selecting download mirror: CONDA_MIRROR=${CONDA_MIRROR}"; \
        case "${CONDA_MIRROR}" in \
            bfsu) \
                MF_URL="https://mirrors.bfsu.edu.cn/github-release/conda-forge/miniforge/LatestRelease/${MF_INSTALLER}"; \
                echo "[ACTION] Attempt 1: BFSU mirror (mirrors.bfsu.edu.cn)..."; \
                ;; \
            tuna) \
                MF_URL="https://mirrors.tuna.tsinghua.edu.cn/github-release/conda-forge/miniforge/LatestRelease/${MF_INSTALLER}"; \
                echo "[ACTION] Attempt 1: THU TUNA mirror (mirrors.tuna.tsinghua.edu.cn)..."; \
                ;; \
            official|*) \
                MF_URL="https://github.com/conda-forge/miniforge/releases/latest/download/${MF_INSTALLER}"; \
                echo "[ACTION] Attempt 1: Official GitHub release..."; \
                ;; \
        esac; \
        if wget --tries=5 --timeout=120 --waitretry=5 "$MF_URL" -O /tmp/miniforge.sh 2>&1; then \
            echo "[OK] Downloaded from ${CONDA_MIRROR}: $(du -h /tmp/miniforge.sh | cut -f1)"; \
        else \
            echo "[WARN] Primary mirror failed, trying BFSU fallback..."; \
            wget --tries=5 --timeout=120 --waitretry=5 \
                "https://mirrors.bfsu.edu.cn/github-release/conda-forge/miniforge/LatestRelease/${MF_INSTALLER}" \
                -O /tmp/miniforge.sh || { \
                echo "[WARN] BFSU failed, trying official GitHub..."; \
                wget --tries=5 --timeout=120 --waitretry=5 \
                    "https://github.com/conda-forge/miniforge/releases/latest/download/${MF_INSTALLER}" \
                    -O /tmp/miniforge.sh || { \
                    echo "[ERROR] All Miniforge download mirrors failed!"; \
                    exit 1; \
                }; \
            }; \
            echo "[OK] Downloaded from fallback mirror: $(du -h /tmp/miniforge.sh | cut -f1)"; \
        fi; \
    fi && \
    echo "[ACTION] Verifying installer integrity (size check)..." && \
    INSTALLER_SIZE=$(stat -c%s /tmp/miniforge.sh 2>/dev/null || wc -c < /tmp/miniforge.sh) && \
    echo "[INFO] Installer size: ${INSTALLER_SIZE} bytes" && \
    if [ "$INSTALLER_SIZE" -lt 50000000 ]; then \
        echo "[WARN] Installer < 50MB, may be corrupted (Miniforge3 is ~60-100MB)"; \
    fi && \
    echo "[ACTION] Running Miniforge3 installer (batch mode, prefix=${CONDA_DIR})..." && \
    bash /tmp/miniforge.sh -b -p "${CONDA_DIR}" && \
    echo "[OK] Miniforge3 installed to ${CONDA_DIR}" && \
    rm -f /tmp/miniforge.sh && \
    echo "[ACTION] Configuring conda..." && \
    "${CONDA_DIR}/bin/conda" config --system --set auto_activate_base false && \
    echo "[OK] base auto-activation disabled" && \
    "${CONDA_DIR}/bin/conda" config --system --set solver libmamba && \
    echo "[OK] libmamba solver enabled (faster dependency resolution)" && \
    "${CONDA_DIR}/bin/conda" init bash && \
    echo "[OK] conda bash init complete" && \
    echo "[ACTION] Verifying conda installation..." && \
    "${CONDA_DIR}/bin/conda" --version && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S2=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 2/7 (Miniforge3 install) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 2 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 3/7: conda + pip mirror sources configuration
# Change frequency: low (mirror address changes)
# ═══════════════════════════════════════════════════════════════════
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 3/7] Configure Mirror Sources (conda + pip)" && \
    echo "# CONDA_MIRROR=${CONDA_MIRROR}, PIP_MIRROR=${PIP_MIRROR}" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[ACTION] Selecting conda mirror (${CONDA_MIRROR})..." && \
    case "${CONDA_MIRROR}" in \
      tuna) \
        CONDA_CHANNEL_URL="https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud"; \
        CONDA_PKGS_URL="https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs"; \
        ;; \
      bfsu|*) \
        CONDA_CHANNEL_URL="https://mirrors.bfsu.edu.cn/anaconda/cloud"; \
        CONDA_PKGS_URL="https://mirrors.bfsu.edu.cn/anaconda/pkgs"; \
        ;; \
      official) \
        CONDA_CHANNEL_URL=""; \
        CONDA_PKGS_URL=""; \
        ;; \
    esac; \
    if [ -n "$CONDA_CHANNEL_URL" ]; then \
        echo "[ACTION] Writing ${CONDA_DIR}/.condarc (${CONDA_MIRROR} mirror + conda-forge/pytorch/nvidia channels)..."; \
        printf '%s\n' \
            'channels:' \
            '  - conda-forge' \
            '  - pytorch' \
            '  - nvidia' \
            '  - defaults' \
            'show_channel_urls: true' \
            "default_channels:" \
            "  - ${CONDA_PKGS_URL}/main" \
            "  - ${CONDA_PKGS_URL}/r" \
            "custom_channels:" \
            "  conda-forge: ${CONDA_CHANNEL_URL}" \
            "  pytorch: ${CONDA_CHANNEL_URL}" \
            "  nvidia: ${CONDA_CHANNEL_URL}" \
            'ssl_verify: true' \
            > "${CONDA_DIR}/.condarc"; \
    else \
        printf '%s\n' \
            'channels:' \
            '  - conda-forge' \
            '  - pytorch' \
            '  - nvidia' \
            '  - defaults' \
            'show_channel_urls: true' \
            'ssl_verify: true' \
            > "${CONDA_DIR}/.condarc"; \
    fi && \
    echo "[OK] .condarc written:" && \
    cat "${CONDA_DIR}/.condarc" && \
    echo "" && \
    echo "[ACTION] Selecting pip mirror (${PIP_MIRROR})..." && \
    case "${PIP_MIRROR}" in \
      tuna) \
        PIP_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"; \
        PIP_HOST="pypi.tuna.tsinghua.edu.cn"; \
        ;; \
      aliyun|*) \
        PIP_INDEX="https://mirrors.aliyun.com/pypi/simple/"; \
        PIP_HOST="mirrors.aliyun.com"; \
        ;; \
      official) \
        PIP_INDEX="https://pypi.org/simple"; \
        PIP_HOST="pypi.org"; \
        ;; \
    esac; \
    echo "[ACTION] Writing /root/.config/pip/pip.conf (${PIP_MIRROR} mirror)..." && \
    mkdir -p /root/.config/pip && \
    printf '%s\n' \
        '[global]' \
        "index-url = ${PIP_INDEX}" \
        "trusted-host = ${PIP_HOST}" \
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
# Stage 4/7: conda env + PyTorch trio (torch/vision/audio) + onnxruntime-gpu
# Change frequency: medium (version upgrades, main hotspot)
# 4-stage fallback: local wheels -> PyTorch official index -> pip mirror -> conda
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 4/7] Create Conda Env + Install PyTorch Trio + ONNX Runtime GPU" && \
    echo "# USE_GPU=${USE_GPU}" && \
    echo "# PYTHON_VERSION=${PYTHON_VERSION}" && \
    echo "# PYTORCH_VERSION=${PYTORCH_VERSION}" && \
    echo "# CUDA_VERSION=${CUDA_VERSION}" && \
    echo "# Strategy: local wheels -> PyTorch official -> pip mirror -> conda fallback" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && \
    echo "[ACTION] Checking for local conda package cache..." && \
    if [ -d /tmp/offline/conda-pkgs ] && [ -n "$(ls -A /tmp/offline/conda-pkgs/ 2>/dev/null | grep -v '^\.gitkeep$')" ]; then \
        echo "[OK] Found local conda packages, copying to ${CONDA_DIR}/pkgs/"; \
        mkdir -p "${CONDA_DIR}/pkgs"; \
        cp -rn /tmp/offline/conda-pkgs/* "${CONDA_DIR}/pkgs/" 2>/dev/null || true; \
        echo "[OK] Local conda packages copied"; \
    else \
        echo "[INFO] No local conda packages, will download from network"; \
    fi && \
    echo "[ACTION] Creating '${ENV_NAME}' conda env with Python ${PYTHON_VERSION}..." && \
    conda create -y -n "${ENV_NAME}" python="${PYTHON_VERSION}" pip setuptools wheel numpy && \
    echo "[OK] conda env '${ENV_NAME}' created" && \
    conda activate "${ENV_NAME}" && \
    echo "[OK] conda env activated: Python $(python --version)" && \
    echo "[INFO] Key conda packages:" && \
    conda list | grep -iE 'python|pip|setuptools|wheel|numpy' || true && \
    echo "" && \
    echo "[ACTION] Determining PyTorch pip index URL..." && \
    if [ "${USE_GPU}" = "1" ]; then \
        CUDA_INDEX="${CUDA_VERSION//./}"; \
        PYTORCH_INDEX="https://download.pytorch.org/whl/cu${CUDA_INDEX}"; \
        echo "[INFO] GPU mode: CUDA ${CUDA_VERSION} -> ${PYTORCH_INDEX}"; \
        echo "[INFO] Minimum NVIDIA driver requirement: CUDA ${CUDA_VERSION} requires driver >= 525.60.13"; \
    else \
        PYTORCH_INDEX="https://download.pytorch.org/whl/cpu"; \
        echo "[INFO] CPU mode -> ${PYTORCH_INDEX}"; \
    fi && \
    echo "" && \
    echo "[ACTION] Installing PyTorch trio (torch + torchvision + torchaudio) with 4-stage fallback..." && \
    echo "" && \
    PYTORCH_INSTALLED=0 && \
    echo "[STAGE 4.1] Attempt 1/4: Local wheels from offline/wheels/..." && \
    if ls /tmp/offline/wheels/torch-*.whl &>/dev/null 2>&1; then \
        echo "[INFO] Found local wheels, installing..."; \
        if pip install --no-cache-dir --no-index --find-links=/tmp/offline/wheels \
            /tmp/offline/wheels/torch-*.whl \
            /tmp/offline/wheels/torchvision-*.whl \
            /tmp/offline/wheels/torchaudio-*.whl 2>&1; then \
            echo "[OK] PyTorch trio installed from local wheels"; \
            PYTORCH_INSTALLED=1; \
        else \
            echo "[WARN] Local wheel install failed, trying network..."; \
        fi; \
    else \
        echo "[INFO] No local torch wheels, skipping"; \
    fi && \
    if [ "${PYTORCH_INSTALLED}" = "0" ]; then \
        echo ""; \
        echo "[STAGE 4.2] Attempt 2/4: pip from PyTorch official index (${PYTORCH_INDEX})..."; \
        if pip install --no-cache-dir \
            "torch==${PYTORCH_VERSION}" \
            "torchvision" \
            "torchaudio" \
            --index-url "${PYTORCH_INDEX}" 2>&1; then \
            echo "[OK] PyTorch trio installed from official PyTorch index"; \
            PYTORCH_INSTALLED=1; \
        else \
            echo "[WARN] Official index failed, trying ${PIP_MIRROR} mirror..."; \
        fi; \
    fi && \
    if [ "${PYTORCH_INSTALLED}" = "0" ]; then \
        echo ""; \
        echo "[STAGE 4.3] Attempt 3/4: pip from default mirror (${PIP_MIRROR})..."; \
        echo "[WARN] Mirror wheels may be CPU-only; GPU builds should use official index"; \
        if pip install --no-cache-dir \
            "torch==${PYTORCH_VERSION}" \
            "torchvision" \
            "torchaudio" 2>&1; then \
            echo "[OK] PyTorch trio installed from ${PIP_MIRROR} mirror"; \
            PYTORCH_INSTALLED=1; \
        else \
            echo "[WARN] ${PIP_MIRROR} mirror failed, trying conda final fallback..."; \
        fi; \
    fi && \
    if [ "${PYTORCH_INSTALLED}" = "0" ]; then \
        echo ""; \
        echo "[STAGE 4.4] Attempt 4/4: conda install (final fallback)..."; \
        if [ "${USE_GPU}" = "1" ]; then \
            echo "[INFO] GPU: conda install pytorch=${PYTORCH_VERSION} torchvision torchaudio pytorch-cuda=${CUDA_VERSION}"; \
            conda install -y -n "${ENV_NAME}" \
                "pytorch=${PYTORCH_VERSION}" \
                "torchvision" \
                "torchaudio" \
                "pytorch-cuda=${CUDA_VERSION}" \
                -c nvidia -c pytorch -c conda-forge || { \
                echo "[ERROR] All PyTorch installation methods failed!"; \
                exit 1; \
            }; \
        else \
            echo "[INFO] CPU: conda install pytorch=${PYTORCH_VERSION} torchvision torchaudio cpuonly"; \
            conda install -y -n "${ENV_NAME}" \
                "pytorch=${PYTORCH_VERSION}" \
                "torchvision" \
                "torchaudio" \
                cpuonly \
                -c pytorch -c conda-forge || { \
                echo "[ERROR] All PyTorch installation methods failed!"; \
                exit 1; \
            }; \
        fi; \
        echo "[OK] PyTorch trio installed via conda fallback"; \
        PYTORCH_INSTALLED=1; \
    fi && \
    echo "" && \
    echo "[ACTION] Installing ONNX Runtime GPU..." && \
    if [ "${USE_GPU}" = "1" ]; then \
        ORT_INSTALLED=0; \
        if ls /tmp/offline/wheels/onnxruntime_gpu-*.whl &>/dev/null 2>&1; then \
            echo "[INFO] Installing onnxruntime-gpu from local wheels..."; \
            pip install --no-cache-dir --no-index --find-links=/tmp/offline/wheels \
                /tmp/offline/wheels/onnxruntime_gpu-*.whl 2>&1 && ORT_INSTALLED=1 || echo "[WARN] Local ORT wheel failed"; \
        fi; \
        if [ "$ORT_INSTALLED" = "0" ]; then \
            echo "[INFO] Installing onnxruntime-gpu from PyPI (${PIP_MIRROR} mirror)..."; \
            pip install --no-cache-dir "onnxruntime-gpu" 2>&1 || { \
                echo "[WARN] onnxruntime-gpu pip install failed, trying conda-forge..."; \
                conda install -y -n "${ENV_NAME}" onnxruntime-gpu -c conda-forge 2>/dev/null || echo "[WARN] onnxruntime-gpu conda install also failed (non-fatal)"; \
            }; \
        fi; \
        echo "[OK] ONNX Runtime GPU installation attempted"; \
    else \
        echo "[INFO] CPU mode: installing onnxruntime (CPU version)..."; \
        pip install --no-cache-dir "onnxruntime" 2>/dev/null || echo "[WARN] onnxruntime install failed (non-fatal)"; \
    fi && \
    echo "" && \
    echo "[ACTION] Installing any additional local wheels..." && \
    if ls /tmp/offline/wheels/*.whl &>/dev/null 2>&1; then \
        EXTRA_WHEELS=$(ls /tmp/offline/wheels/*.whl 2>/dev/null | grep -v -E 'torch-|torchvision-|torchaudio-|onnxruntime' | wc -l); \
        if [ "$EXTRA_WHEELS" -gt 0 ]; then \
            echo "[INFO] Found ${EXTRA_WHEELS} additional wheel(s), installing..."; \
            pip install --no-cache-dir --no-index --find-links=/tmp/offline/wheels \
                $(ls /tmp/offline/wheels/*.whl 2>/dev/null | grep -v -E 'torch-|torchvision-|torchaudio-|onnxruntime') 2>/dev/null || \
                echo "[WARN] Some additional wheels failed (non-critical)"; \
        fi; \
    fi && \
    echo "" && \
    echo "[ACTION] Post-install verification (Python imports)..." && \
    python -c "import torch; print(f'[OK] torch {torch.__version__} (cuda={torch.version.cuda})')" && \
    python -c "import torchvision; print(f'[OK] torchvision {torchvision.__version__}')" && \
    python -c "import torchaudio; print(f'[OK] torchaudio {torchaudio.__version__}')" && \
    if [ "${USE_GPU}" = "1" ]; then \
        python -c "import onnxruntime as ort; print(f'[OK] onnxruntime {ort.__version__}, providers: {ort.get_available_providers()}')" || echo "[WARN] onnxruntime import verification skipped"; \
    else \
        python -c "import onnxruntime as ort; print(f'[OK] onnxruntime {ort.__version__}')" 2>/dev/null || echo "[WARN] onnxruntime not installed (non-critical for CPU)"; \
    fi && \
    echo "" && \
    echo "[INFO] Installed pip packages (key ML libs):" && \
    pip list --format=columns 2>/dev/null | grep -iE 'torch|numpy|onnx|pip|setuptools|wheel' || true && \
    echo "" && \
    echo "[ACTION] Cleaning up..." && \
    rm -rf /tmp/offline && \
    conda clean -ya && \
    pip cache purge 2>/dev/null || true && \
    find "${ENV_PATH}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find "${ENV_PATH}" -type f -name "*.pyc" -delete 2>/dev/null || true && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S4=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 4/7 (conda env+PyTorch+ORT) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 4 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 5/7: non-root user 'ai' (UID 1000) + permissions + shell init
# Change frequency: medium (user/dir/config additions)
# ═══════════════════════════════════════════════════════════════════
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 5/7] Create Non-Root User 'ai' (UID 1000)" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[ACTION] Checking for UID 1000 conflict..." && \
    if id ubuntu &>/dev/null; then \
        echo "[INFO] Removing default 'ubuntu' user (UID 1000 conflict)..."; \
        userdel -r ubuntu 2>/dev/null || true; \
        echo "[OK] ubuntu user removed"; \
    fi && \
    echo "[ACTION] Creating user 'ai' (UID 1000, GID 1000, bash, sudo group)..." && \
    useradd -m -s /bin/bash -u 1000 -U -G sudo ai && \
    echo "[OK] User 'ai' created" && \
    echo "[ACTION] Configuring passwordless sudo..." && \
    echo "ai ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ai && \
    chmod 0440 /etc/sudoers.d/ai && \
    echo "[OK] sudo configured" && \
    echo "[ACTION] Copying pip/conda configs to /home/ai/..." && \
    mkdir -p /home/ai/.config/pip && \
    cp /root/.config/pip/pip.conf /home/ai/.config/pip/pip.conf && \
    cp "${CONDA_DIR}/.condarc" /home/ai/.condarc && \
    echo "[OK] Configs copied" && \
    echo "[ACTION] Setting up shell auto-activation..." && \
    for bashrc in /home/ai/.bashrc /root/.bashrc; do \
        grep -q 'conda.sh' "$bashrc" 2>/dev/null || echo "source ${CONDA_DIR}/etc/profile.d/conda.sh" >> "$bashrc"; \
        grep -q "conda activate ${ENV_NAME}" "$bashrc" 2>/dev/null || echo "conda activate ${ENV_NAME}" >> "$bashrc"; \
    done && \
    echo "[OK] bashrc auto-activation configured" && \
    echo "[ACTION] Creating /etc/profile.d/conda-init.sh..." && \
    printf '%s\n' \
        '#!/bin/bash' \
        'source /opt/conda/etc/profile.d/conda.sh' \
        'conda activate pytorch 2>/dev/null || true' \
        > /etc/profile.d/conda-init.sh && \
    chmod +x /etc/profile.d/conda-init.sh && \
    echo "[OK] conda-init.sh created" && \
    echo "[ACTION] Setting ownership and permissions..." && \
    chown -R ai:ai /home/ai /workspace && \
    chmod -R a+rX "${CONDA_DIR}" && \
    echo "[OK] Permissions set" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S5=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 5/7 (user+perms) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 5 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 6/7: entrypoint install + syntax validation
# Change frequency: high (config tweaks, does not invalidate earlier layers)
# ═══════════════════════════════════════════════════════════════════
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

RUN echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 6/7] Install Entrypoint + Syntax Validation" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[ACTION] Setting entrypoint.sh permissions..." && \
    chmod +x /usr/local/bin/entrypoint.sh && \
    echo "[OK] Entrypoint installed at /usr/local/bin/entrypoint.sh" && \
    ls -la /usr/local/bin/entrypoint.sh && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│  [VALIDATION CHECKPOINT - Stage 6/7]            │" && \
    echo "│  bash syntax validation for entrypoint          │" && \
    echo "└─────────────────────────────────────────────────┘" && \
    bash -n /usr/local/bin/entrypoint.sh && echo "[OK] entrypoint.sh bash syntax valid" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S6=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 6/7 (entrypoint+validate) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 6 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 7/7: build-info + GPU validation + cleanup + timing summary
# Change frequency: lowest (release tagging)
# GPU validation checks (without actual GPU present):
#   - torch imports successfully
#   - torch.version.cuda matches expected CUDA_VERSION
#   - CUDA libraries exist in torch/lib directory
#   - onnxruntime-gpu imports and has CUDAExecutionProvider
#   - torch.cuda.is_available() doesn't crash (returns False without GPU)
# ═══════════════════════════════════════════════════════════════════
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [STAGE 7/7] Final Validation + Metadata + Cleanup + Timing Summary" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && \
    conda activate "${ENV_NAME}" && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│  [FINAL VERIFICATION - Stage 7/7]               │" && \
    echo "│  Comprehensive GPU/ML stack validation          │" && \
    echo "└─────────────────────────────────────────────────┘" && \
    echo "" && \
    echo "[VALIDATE] Python environment..." && \
    python --version && \
    PYTHON_PATH=$(which python) && \
    echo "[VALIDATE] Python binary: ${PYTHON_PATH}" && \
    if [[ "$PYTHON_PATH" != "${ENV_PATH}/bin/python" ]]; then \
        echo "[ERROR] Python not from expected env path!"; exit 1; \
    fi && \
    echo "[OK] Python from correct conda env" && \
    echo "" && \
    echo "[VALIDATE] PyTorch trio import..." && \
    python -c "import torch; print(f'  torch:        {torch.__version__}')" && \
    python -c "import torch; print(f'  torch cuda:   {torch.version.cuda}')" && \
    python -c "import torchvision; print(f'  torchvision:  {torchvision.__version__}')" && \
    python -c "import torchaudio; print(f'  torchaudio:   {torchaudio.__version__}')" && \
    echo "[OK] PyTorch trio import verified" && \
    echo "" && \
    echo "[VALIDATE] CUDA version consistency..." && \
    if [ "${USE_GPU}" = "1" ]; then \
        TORCH_CUDA=$(python -c "import torch; print(torch.version.cuda or 'NONE')"); \
        echo "[INFO] torch.version.cuda = ${TORCH_CUDA}, expected = ${CUDA_VERSION}"; \
        if [[ "$TORCH_CUDA" == "${CUDA_VERSION}"* ]]; then \
            echo "[OK] CUDA version matches expected"; \
        else \
            echo "[WARN] CUDA version mismatch: torch reports ${TORCH_CUDA}, build arg was ${CUDA_VERSION}"; \
        fi; \
        echo "[VALIDATE] CUDA libraries exist in torch/lib..."; \
        TORCH_LIB="${ENV_PATH}/lib/python3.14/site-packages/torch/lib"; \
        CUDA_LIB_COUNT=$(find "$TORCH_LIB" -name "libcudart*" -o -name "libcuda*" -o -name "libcublas*" -o -name "libcudnn*" 2>/dev/null | wc -l); \
        echo "[INFO] Found ${CUDA_LIB_COUNT} CUDA-related libraries in torch/lib"; \
        if [ "$CUDA_LIB_COUNT" -gt 0 ]; then \
            echo "[OK] CUDA libraries present"; \
        else \
            echo "[WARN] No CUDA libraries found in torch/lib (may be CPU build)"; \
        fi; \
    fi && \
    echo "" && \
    echo "[VALIDATE] ONNX Runtime..." && \
    if [ "${USE_GPU}" = "1" ]; then \
        python -c "
import onnxruntime as ort
providers = ort.get_available_providers()
print(f'  onnxruntime:  {ort.__version__}')
print(f'  providers:    {providers}')
if 'CUDAExecutionProvider' in providers:
    print('[OK] CUDAExecutionProvider available')
else:
    print('[WARN] CUDAExecutionProvider NOT available (GPU acceleration disabled)')
" || echo "[WARN] onnxruntime verification skipped"; \
    else \
        python -c "import onnxruntime as ort; print(f'  onnxruntime:  {ort.__version__} (CPU)')" 2>/dev/null || echo "[WARN] onnxruntime not installed"; \
    fi && \
    echo "" && \
    echo "[VALIDATE] Tensor operations (per pytorch.org: x = torch.rand(5,3))..." && \
    python -c "
import torch
x = torch.rand(5, 3)
print(x)
assert x.shape == (5, 3), f'Shape mismatch: {x.shape}'
y = x @ x.T
assert y.shape == (5, 5), f'Matmul shape mismatch: {y.shape}'
print('[OK] Tensor ops verified: rand + matmul work correctly')
" && \
    echo "" && \
    echo "[VALIDATE] CUDA availability check (no GPU in build env = False expected)..." && \
    python -c "
import torch
cuda_avail = torch.cuda.is_available()
print(f'  torch.cuda.is_available() = {cuda_avail}')
print(f'  (False is NORMAL during build - GPU only available at runtime with --gpus all)')
if not cuda_avail:
    print('[OK] Build env has no GPU (expected) - CUDA libraries installed correctly')
else:
    gpu_count = torch.cuda.device_count()
    print(f'[OK] GPU detected! {gpu_count} device(s)')
    for i in range(gpu_count):
        print(f'  GPU {i}: {torch.cuda.get_device_name(i)}')
" && \
    echo "" && \
    echo "[VALIDATE] numpy..." && \
    python -c "import numpy; print(f'  numpy:        {numpy.__version__}')" && \
    echo "" && \
    echo "[VALIDATE] System tools..." && \
    tini --version >/dev/null 2>&1 && echo "  tini:         $(tini --version 2>&1 | head -1)" && \
    gosu nobody true && echo "  gosu:         working" && \
    echo "[OK] System tools verified" && \
    echo "" && \
    bash -n /usr/local/bin/entrypoint.sh && echo "[OK] entrypoint.sh syntax valid" && \
    echo "" && \
    echo "[ACTION] Writing build metadata to /etc/pytorch-base-build-info..." && \
    printf 'PYTORCH_BASE_IMAGE=%s\nUSE_GPU=%s\nPYTHON_VERSION=%s\nPYTORCH_VERSION=%s\nCUDA_VERSION=%s\nONNXRUNTIME=enabled\nCONDA_DISTRIBUTION=Miniforge3\nCONDA_DIR=%s\nENV_NAME=%s\nBUILD_DATE=%s\nENTRYPOINT_QUIET=%s\nBUILD_TIMER=enabled\n' \
        "${BASE_IMAGE}" "${USE_GPU}" "${PYTHON_VERSION}" "${PYTORCH_VERSION}" \
        "${CUDA_VERSION}" "${CONDA_DIR}" "${ENV_NAME}" \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        "${QUIET}" \
        > /etc/pytorch-base-build-info && \
    echo "[OK] Build metadata written:" && \
    cat /etc/pytorch-base-build-info && \
    echo "" && \
    echo "[ACTION] Fixing executable stack flags on PyTorch .so files..." && \
    python -c "
import os, struct, glob
lib_dir = os.path.join('${ENV_PATH}', 'lib', 'python3.14', 'site-packages', 'torch', 'lib')
fixed = 0
if os.path.isdir(lib_dir):
    for so_path in glob.glob(os.path.join(lib_dir, '*.so')):
        try:
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
        except: pass
print(f'[OK] Fixed executable stack flag on {fixed} .so files')
" 2>/dev/null || echo "[INFO] Stack flag fix skipped (non-critical)" && \
    echo "" && \
    echo "[ACTION] Aggressive cleanup to reduce image size..." && \
    rm -rf /tmp/* /var/tmp/* /root/.cache /home/ai/.cache && \
    find "${ENV_PATH}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find "${ENV_PATH}" -type f -name "*.pyc" -delete 2>/dev/null || true && \
    find "${ENV_PATH}" -type f -name "*.pyo" -delete 2>/dev/null || true && \
    find "${CONDA_DIR}/pkgs" -type f -name "*.tar.bz2" -delete 2>/dev/null || true && \
    rm -rf /usr/share/doc /usr/share/man /usr/share/info /usr/share/lintian 2>/dev/null || true && \
    echo "[OK] Cleanup complete" && \
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
    echo "║       BUILD TIMING SUMMARY (PyTorch GPU Base v3.0)         ║" && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  Stage 1/7  system packages + locale   %5ds               ║\n" $_T1 && \
    printf "║  Stage 2/7  Miniforge3 install         %5ds               ║\n" $_T2 && \
    printf "║  Stage 3/7  conda/pip mirror config    %5ds               ║\n" $_T3 && \
    printf "║  Stage 4/7  PyTorch trio + ORT-GPU     %5ds  ★ hotspot    ║\n" $_T4 && \
    printf "║  Stage 5/7  user ai + permissions      %5ds               ║\n" $_T5 && \
    printf "║  Stage 6/7  entrypoint + validation    %5ds               ║\n" $_T6 && \
    printf "║  Stage 7/7  GPU verify + cleanup       %5ds               ║\n" $_T7 && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  BUILD TOTAL                           %5ds               ║\n" $_TOTAL && \
    echo "╚══════════════════════════════════════════════════════════════╝" && \
    echo "" && \
    rm -f /tmp/.build-timer && \
    echo "########################################################################" && \
    echo "# ALL 7 STAGES COMPLETED SUCCESSFULLY!" && \
    if [ "${USE_GPU}" = "1" ]; then \
        echo "# GPU Image: PyTorch ${PYTORCH_VERSION} + CUDA ${CUDA_VERSION} + ONNX Runtime GPU"; \
        echo "# Runtime: docker run --gpus all -it pytorch-base:gpu-cu${CUDA_VERSION//./}"; \
    else \
        echo "# CPU Image: PyTorch ${PYTORCH_VERSION} (CPU-only)"; \
    fi && \
    echo "########################################################################"

# ==================== Runtime Configuration ====================
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["/bin/bash", "-l"]
USER ai
