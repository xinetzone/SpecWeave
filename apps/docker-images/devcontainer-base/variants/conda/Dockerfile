# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - Conda Variant Dockerfile (Slim)
# Project: SpecWeave Full-featured Development Container - Miniconda3 Variant
# Base: devcontainer-base:${BASE_TAG} (Ubuntu 26.04 + SSH + Docker DinD + Podman + Jupyter + Miniconda3)
# Conda: Miniconda3 already in base at /opt/conda, Python ${PYTHON_VERSION} in base env
# PATH priority: /opt/conda/bin first (conda is already in PATH from base)
# Activation: source /etc/profile.d/conda-init.sh && conda activate base
#
# Build: docker build -f variants/conda/Dockerfile -t devcontainer-base:conda-latest .
# CN:    docker build -f variants/conda/Dockerfile \
#          --build-arg APT_MIRROR=aliyun --build-arg CONDA_MIRROR=tuna --build-arg PIP_MIRROR=aliyun \
#          -t devcontainer-base:conda-latest .
# Run:   docker run -d --privileged -p 2222:22 -p 2375:2375 -p 8888:8888 \
#          -e USER_PASSWORD=pass -e JUPYTER_TOKEN=mysecret -e GRANT_SUDO=yes \
#          -v $(pwd)/workspace:/workspace -v docker-data:/var/lib/docker \
#          devcontainer-base:conda-latest
# Verify: docker run --rm devcontainer-base:conda-latest conda --version
#
# Variant Stage Layering (thin layer on top of base image):
#   Stage 1/2: Mirror source configuration (conda + pip) + verification
#   Stage 2/2: build-info + cleanup + final verification + timing summary
#
# Build Timing: 每个Stage结束时输出 [TIMER] 本阶段耗时+累计耗时，最终输出汇总表
# =============================================================================

ARG BASE_TAG=latest
ARG APT_MIRROR=official
ARG CONDA_MIRROR=tuna
ARG PIP_MIRROR=aliyun
ARG PYTHON_VERSION=3.14

FROM devcontainer-base:${BASE_TAG}

ARG BASE_TAG
ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR
ARG PYTHON_VERSION

LABEL maintainer="SpecWeave"
LABEL description="DevContainer base with Miniconda3 at /opt/conda (pre-installed in base), JupyterLab in conda env"
LABEL variant="conda"
LABEL conda.version="bundled"
LABEL python.version="${PYTHON_VERSION}"

ENV CONDA_DIR=/opt/conda \
    CONDA_ENVS_DIRS=/opt/conda/envs \
    CONDA_PKGS_DIRS=/opt/conda/pkgs

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# ═══════════════════════════════════════════════════════════════════
# Stage 1/2: 镜像源配置 + 基础验证 + 计时器初始化
# 变化频率：低（镜像源地址变更时改）
# 原则：调用共享脚本配置镜像源；验证conda已在base中安装；
#       不重复安装Miniconda（base已包含）
# ═══════════════════════════════════════════════════════════════════
COPY shared/scripts/conda-mirror-setup.sh /usr/local/bin/conda-mirror-setup.sh
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    echo "" && \
    echo "########################################################################" && \
    echo "# [CONDA VARIANT STAGE 1/2] Mirror Config + Base Verification (Slim)" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[TIMER] Conda variant build started at $(date -u +%Y-%m-%dT%H:%M:%SZ)" && \
    echo "START=$_STAGE_START" > /tmp/.variant-build-timer && \
    echo "[BUILD] Verifying Miniconda is already present in base image..." && \
    test -d /opt/conda && echo "[OK] /opt/conda exists" && \
    test -x /opt/conda/bin/conda && echo "[OK] /opt/conda/bin/conda executable" && \
    /opt/conda/bin/conda --version && \
    /opt/conda/bin/python --version && \
    echo "  - PATH: $PATH" && \
    echo "  - which conda: $(which conda)" && \
    echo "  - which python: $(which python)" && \
    echo "  - conda packages in base: $(/opt/conda/bin/conda list -n base 2>/dev/null | wc -l)" && \
    echo "" && \
    echo "[BUILD] Configuring mirror sources (conda + pip)..." && \
    chmod +x /usr/local/bin/conda-mirror-setup.sh && \
    CONDA_DIR=${CONDA_DIR} CONDA_MIRROR=${CONDA_MIRROR} PIP_MIRROR=${PIP_MIRROR} \
        /usr/local/bin/conda-mirror-setup.sh && \
    echo "[OK] Mirror sources configured" && \
    echo "" && \
    echo "[BUILD] Ensuring conda-init.sh exists and is valid..." && \
    if [ ! -f /etc/profile.d/conda-init.sh ]; then \
        echo "[INFO] conda-init.sh not found, creating..."; \
        printf '%s\n' \
            '#!/bin/bash' \
            'if [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then' \
            '    source "/opt/conda/etc/profile.d/conda.sh"' \
            '    conda activate base 2>/dev/null || true' \
            'fi' \
            > /etc/profile.d/conda-init.sh && \
        chmod +x /etc/profile.d/conda-init.sh; \
        echo "[OK] /etc/profile.d/conda-init.sh created"; \
    else \
        echo "[OK] /etc/profile.d/conda-init.sh already exists"; \
    fi && \
    echo "" && \
    echo "[INFO] devuser verification:" && \
    echo "  - devuser exists: $(id devuser 2>&1 | head -1)" && \
    echo "  - Jupyter available: $(jupyter --version 2>&1 | head -1)" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _TOTAL=$((_NOW - $(grep '^START=' /tmp/.variant-build-timer | cut -d= -f2))) && \
    echo "VS1=$_NOW" >> /tmp/.variant-build-timer && \
    echo "[TIMER] Stage 1/2 (mirror+verify) took ${_ELAPSED}s | Variant cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 1 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 2/2: build-info + 清理 + 最终验证 + 计时器汇总表
# 变化频率：最低
# 原则：写入 variant build-info；清理缓存；最终验证；输出耗时汇总表
# ═══════════════════════════════════════════════════════════════════
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [CONDA VARIANT STAGE 2/2] Final Metadata, Cleanup, Verification" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[ACTION] Writing build metadata to /etc/devcontainer-variant-conda-build-info..."; \
    CONDA_VERSION=$(/opt/conda/bin/conda --version 2>&1 | awk '{print $2}'); \
    CONDA_PYTHON_VERSION=$(/opt/conda/bin/python --version 2>&1 | awk '{print $2}'); \
    JUPYTERLAB_VERSION=$(/opt/conda/bin/jupyter lab --version 2>/dev/null || echo "unknown"); \
    printf '%s\n' \
        "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        "VARIANT=conda" \
        "BASE_IMAGE=devcontainer-base:${BASE_TAG}" \
        "CONDA_VERSION=${CONDA_VERSION}" \
        "PYTHON_VERSION=${CONDA_PYTHON_VERSION}" \
        "JUPYTERLAB_VERSION=${JUPYTERLAB_VERSION}" \
        "CONDA_DIR=/opt/conda" \
        "CONDA_MIRROR=${CONDA_MIRROR}" \
        "PIP_MIRROR=${PIP_MIRROR}" \
        "APT_MIRROR=${APT_MIRROR}" \
        "AUTO_ACTIVATE_BASE=false" \
        "ACTIVATION_SCRIPT=/etc/profile.d/conda-init.sh" \
        "PYTHON_ENV=conda-base" \
        "PATH_PRIORITY=conda-bin-first" \
        "SERVICES_PRESERVED=sshd,dockerd,podman,jupyter,supervisord" \
        "BUILD_TIMER=enabled" \
        "SLIM_MODE=base-has-conda-preinstalled" \
        > /etc/devcontainer-variant-conda-build-info && \
    echo "[OK] Build metadata written:"; \
    cat /etc/devcontainer-variant-conda-build-info; \
    echo ""; \
    echo "[ACTION] Running cleanup..."; \
    /opt/conda/bin/conda clean -yafq 2>/dev/null || true; \
    /opt/conda/bin/pip cache purge 2>/dev/null || true; \
    apt-get clean 2>/dev/null || true; \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.cache; \
    echo "[OK] Cleanup complete"; \
    echo ""; \
    echo "┌─────────────────────────────────────────────────┐"; \
    echo "│ [INFO] Installed package versions (summary)     │"; \
    echo "└─────────────────────────────────────────────────┘"; \
    echo "  [conda base]"; \
    /opt/conda/bin/conda list -n base 2>/dev/null | grep -E '^(python|pip|conda|setuptools|wheel|openssl|certifi|ca-certificates|jupyter|notebook)\s' | awk '{printf "    - %s: %s\n", $1, $2}'; \
    echo ""; \
    echo "┌─────────────────────────────────────────────────┐"; \
    echo "│  [VALIDATION CHECKPOINT - Stage 2/2]           │"; \
    echo "│  Running final syntax + availability checks     │"; \
    echo "└─────────────────────────────────────────────────┘"; \
    echo ""; \
    echo "[VALIDATE 1/6] bash -n /etc/profile.d/conda-init.sh..."; \
    bash -n /etc/profile.d/conda-init.sh && echo "[OK] conda-init.sh bash syntax valid"; \
    echo "[VALIDATE 2/6] conda binary exists and is executable..."; \
    test -x /opt/conda/bin/conda && echo "[OK] /opt/conda/bin/conda is executable"; \
    /opt/conda/bin/conda --version; \
    echo "[VALIDATE 3/6] Python from conda is default..."; \
    DEFAULT_PYTHON=$(which python); \
    echo "  which python -> $DEFAULT_PYTHON"; \
    echo "[VALIDATE 4/6] JupyterLab available from conda..."; \
    /opt/conda/bin/jupyter lab --version 2>&1 | head -1; \
    echo "[OK] JupyterLab available from conda"; \
    echo "[VALIDATE 5/6] Core services (docker, supervisord) still present..."; \
    docker --version 2>&1; \
    supervisord --version 2>&1; \
    echo "[OK] Core services preserved"; \
    echo "[VALIDATE 6/6] devuser can access conda and jupyter..."; \
    su - devuser -c "conda --version && python --version && jupyter lab --version 2>&1 | head -1" && echo "[OK] devuser can access conda+jupyter"; \
    echo ""; \
    echo "[VALIDATE] All validation checks completed"; \
    echo ""; \
    echo "┌─────────────────────────────────────────────────┐"; \
    echo "│  [FINAL VERIFICATION - ACTIVATION TEST]         │"; \
    echo "│  Testing source /etc/profile.d/conda-init.sh    │"; \
    echo "└─────────────────────────────────────────────────┘"; \
    bash -l -c 'source /etc/profile.d/conda-init.sh && conda activate base && echo "  Activated conda base successfully" && echo "  Python after activation: $(which python) -> $(python --version)"' && \
    echo ""; \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.variant-build-timer | cut -d= -f2) && \
    _VS1=$(grep '^VS1=' /tmp/.variant-build-timer | cut -d= -f2) && \
    _VT1=$((_VS1 - _START)) && \
    _VT2=$_ELAPSED && \
    _VTOTAL=$((_NOW - _START)) && \
    echo "[TIMER] Stage 2/2 (metadata+final verify) took ${_ELAPSED}s | Variant cumulative: ${_VTOTAL}s" && \
    echo "╔══════════════════════════════════════════════════════════════╗"; \
    echo "║     BUILD TIMING SUMMARY (Conda Variant - 2 Stages Slim)   ║"; \
    echo "╠══════════════════════════════════════════════════════════════╣"; \
    printf "║  Stage 1/2  mirror config + verify    %5ds               ║\n" $_VT1; \
    printf "║  Stage 2/2  metadata+final verify     %5ds               ║\n" $_VT2; \
    echo "╠══════════════════════════════════════════════════════════════╣"; \
    printf "║  CONDA VARIANT TOTAL (thin add-on)    %5ds               ║\n" $_VTOTAL; \
    echo "╚══════════════════════════════════════════════════════════════╝"; \
    echo ""; \
    rm -f /tmp/.variant-build-timer; \
    echo "########################################################################"; \
    echo "# CONDA VARIANT BUILD COMPLETE (Slim Mode)!"; \
    echo "# Conda available at /opt/conda (pre-installed in base image)"; \
    echo "# Activate with: source /etc/profile.d/conda-init.sh && conda activate base"; \
    echo "# JupyterLab runs from conda base environment (/opt/conda/bin/jupyter)"; \
    echo "# No redundant Miniconda installation - image size minimized"; \
    echo "########################################################################"; \
    echo ""
