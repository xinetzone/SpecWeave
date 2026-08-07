# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - Conda Variant Dockerfile
# Project: SpecWeave Full-featured Development Container - Miniconda3 Variant
# Base: devcontainer-base:${BASE_TAG} (Ubuntu 26.04 + SSH + Docker DinD + Podman + Jupyter)
# Conda: Miniconda3 at /opt/conda, default Python ${PYTHON_VERSION}
# PATH priority: /opt/venv/bin first (system venv for services), conda via source only
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
# Verify: docker run --rm devcontainer-base:conda-latest /opt/conda/bin/conda --version
#
# Variant Stage Layering (additional layers on top of devcontainer-base 7 stages):
#   Stage 1/5: Extra system packages check/install + timer initialization
#   Stage 2/5: Miniconda3 installation to /opt/conda
#   Stage 3/5: conda + pip mirror source configuration
#   Stage 4/5: Conda activation script + bashrc config + permissions
#   Stage 5/5: build-info + cleanup + final verification + timing summary
#
# Build Timing: 每个Stage结束时输出 [TIMER] 本阶段耗时+累计耗时，最终输出汇总表
# =============================================================================

ARG BASE_TAG=latest
ARG APT_MIRROR=official
ARG CONDA_MIRROR=tuna
ARG PIP_MIRROR=aliyun
ARG MINICONDA_VERSION=latest
ARG PYTHON_VERSION=3.14

FROM devcontainer-base:${BASE_TAG}

# 重新声明 ARG BASE_TAG：FROM 前的 ARG 不会自动带入后续阶段，
# 否则 build-info 中 BASE_IMAGE 会退化为空标签。
ARG BASE_TAG
ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR
ARG MINICONDA_VERSION
ARG PYTHON_VERSION

LABEL maintainer="SpecWeave"
LABEL description="DevContainer base with Miniconda3 at /opt/conda, system venv preserved for services"
LABEL variant="conda"
LABEL conda.version="${MINICONDA_VERSION}"
LABEL python.version="${PYTHON_VERSION}"

ENV CONDA_DIR=/opt/conda \
    CONDA_ENVS_DIRS=/opt/conda/envs \
    CONDA_PKGS_DIRS=/opt/conda/pkgs

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# ═══════════════════════════════════════════════════════════════════
# Stage 1/5: 额外系统包检查/安装 + 计时器初始化
# 变化频率：最低
# 原则：检查 wget curl bzip2 是否已安装（基础镜像已有，仅做确认），
#       初始化追加层计时器 /tmp/.variant-build-timer
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    echo "" && \
    echo "########################################################################" && \
    echo "# [CONDA VARIANT STAGE 1/5] System Packages Check + Timer Init" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[TIMER] Conda variant build started at $(date -u +%Y-%m-%dT%H:%M:%SZ)" && \
    echo "START=$_STAGE_START" > /tmp/.variant-build-timer && \
    echo "[BUILD] Checking required system packages..." && \
    _INSTALL_PKGS="" && \
    for pkg in wget curl bzip2 ca-certificates; do \
        if ! dpkg -s "$pkg" >/dev/null 2>&1; then \
            echo "[INFO] $pkg not found, will install"; \
            _INSTALL_PKGS="$_INSTALL_PKGS $pkg"; \
        else \
            echo "[OK] $pkg already installed: $(dpkg-query -W -f='${Version}' $pkg 2>/dev/null || echo 'present')"; \
        fi; \
    done && \
    if [ -n "$_INSTALL_PKGS" ]; then \
        echo "[BUILD] Configuring APT mirror: ${APT_MIRROR}..."; \
        if [ "${APT_MIRROR}" = "aliyun" ]; then \
            sed -i 's|http://archive.ubuntu.com|https://mirrors.aliyun.com|g; s|http://security.ubuntu.com|https://mirrors.aliyun.com|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || \
            sed -i 's|http://archive.ubuntu.com|https://mirrors.aliyun.com|g; s|http://security.ubuntu.com|https://mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null || true; \
            echo "[BUILD] Using Aliyun APT mirror"; \
        elif [ "${APT_MIRROR}" = "tuna" ]; then \
            sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || \
            sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list 2>/dev/null || true; \
            echo "[BUILD] Using Tsinghua TUNA APT mirror"; \
        else \
            echo "[BUILD] Using official APT sources"; \
        fi; \
        echo "[BUILD] Installing missing packages:$_INSTALL_PKGS"; \
        apt-get update -qq && \
        apt-get install -y --no-install-recommends -qq $_INSTALL_PKGS && \
        echo "[OK] Missing packages installed"; \
        rm -rf /var/lib/apt/lists/*; \
    else \
        echo "[OK] All required system packages already present in base image"; \
    fi && \
    echo "" && \
    echo "[INFO] Base image verification:" && \
    echo "  - devuser exists: $(id devuser 2>&1 | head -1)" && \
    echo "  - /opt/venv exists: $(test -d /opt/venv && echo 'yes' || echo 'no')" && \
    echo "  - python (venv): $(python --version 2>&1)" && \
    echo "  - PATH: $PATH" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _TOTAL=$((_NOW - $(grep '^START=' /tmp/.variant-build-timer | cut -d= -f2))) && \
    echo "VS1=$_NOW" >> /tmp/.variant-build-timer && \
    echo "[TIMER] Stage 1/5 (system check) took ${_ELAPSED}s | Variant cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 1 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 2/5: Miniconda3 安装到 /opt/conda
# 变化频率：低（Miniconda版本升级时改）
# 原则：在线安装（简化版本），支持 CONDA_MIRROR 选择 tuna 或 official；
#       -b 批处理模式，不修改 PATH，不自动激活 base；
#       设置 auto_activate_base false
# ⚠️  注意：此处禁止使用 --mount=type=cache,target=/opt/conda/pkgs。
#       该缓存挂载会预创建 /opt/conda 目录，导致 Miniconda 安装器报
#       "File or directory already exists" 而中止安装。基础 Miniconda
#       只在镜像首次构建时安装一次，pkgs 缓存收益甚微，故不挂载缓存。
# ═══════════════════════════════════════════════════════════════════
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [CONDA VARIANT STAGE 2/5] Install Miniconda3 to /opt/conda" && \
    echo "# MINICONDA_VERSION=${MINICONDA_VERSION}, PYTHON_VERSION=${PYTHON_VERSION}" && \
    echo "# CONDA_MIRROR=${CONDA_MIRROR}" && \
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
    if [ "${MINICONDA_VERSION}" = "latest" ]; then \
        echo "[ACTION] Resolving latest Miniconda3 version..."; \
        CONDA_INSTALLER="Miniconda3-latest-Linux-${MINICONDA_ARCH}.sh"; \
    else \
        CONDA_INSTALLER="Miniconda3-${MINICONDA_VERSION}-Linux-${MINICONDA_ARCH}.sh"; \
    fi && \
    echo "[ACTION] Downloading Miniconda3: ${CONDA_INSTALLER}..." && \
    if [ "${CONDA_MIRROR}" = "tuna" ]; then \
        echo "[INFO] Using Tsinghua TUNA mirror: mirrors.tuna.tsinghua.edu.cn"; \
        CONDA_URL="https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/${CONDA_INSTALLER}"; \
    else \
        echo "[INFO] Using official Anaconda repo: repo.anaconda.com"; \
        CONDA_URL="https://repo.anaconda.com/miniconda/${CONDA_INSTALLER}"; \
    fi && \
    echo "[ACTION] Download URL: ${CONDA_URL}"; \
    wget --tries=3 --timeout=120 --waitretry=5 -q "${CONDA_URL}" -O /tmp/miniconda.sh && \
    echo "[OK] Downloaded: $(du -h /tmp/miniconda.sh | cut -f1)"; \
    echo "[ACTION] Verifying installer size..."; \
    INSTALLER_SIZE=$(stat -c%s /tmp/miniconda.sh 2>/dev/null || wc -c < /tmp/miniconda.sh); \
    echo "[INFO] Installer size: ${INSTALLER_SIZE} bytes"; \
    if [ "$INSTALLER_SIZE" -lt 50000000 ]; then \
        echo "[WARN] Installer seems smaller than expected (<50MB), may be corrupted or network error"; \
    fi; \
    echo "[ACTION] Running Miniconda3 installer (batch mode, prefix=/opt/conda)..."; \
    bash /tmp/miniconda.sh -b -p "${CONDA_DIR}" && \
    echo "[OK] Miniconda3 installed to ${CONDA_DIR}"; \
    rm -f /tmp/miniconda.sh; \
    echo "[ACTION] Disabling conda base auto-activation..."; \
    "${CONDA_DIR}/bin/conda" config --system --set auto_activate_base false && \
    echo "[OK] auto_activate_base set to false (system-wide)"; \
    echo "[ACTION] Setting default Python version in base environment to ${PYTHON_VERSION}..."; \
    "${CONDA_DIR}/bin/conda" install -y -n base "python=${PYTHON_VERSION}" && \
    echo "[OK] Base environment Python set to ${PYTHON_VERSION}"; \
    "${CONDA_DIR}/bin/conda" clean -ya && \
    echo "[ACTION] Verifying conda installation..."; \
    "${CONDA_DIR}/bin/conda" --version && \
    echo "  - conda path: ${CONDA_DIR}/bin/conda"; \
    echo "  - python (conda base): $("${CONDA_DIR}/bin/python" --version 2>&1)"; \
    echo "  - conda info --base: $("${CONDA_DIR}/bin/conda" info --base)"; \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.variant-build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "VS2=$_NOW" >> /tmp/.variant-build-timer && \
    echo "[TIMER] Stage 2/5 (Miniconda install) took ${_ELAPSED}s | Variant cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 2 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 3/5: conda + pip 镜像源配置
# 变化频率：低（镜像源地址变更时改）
# 原则：调用共享脚本 variants/shared/scripts/conda-mirror-setup.sh 完成配置，
#       避免与其它 conda 类变体重复相同的镜像源逻辑
# ═══════════════════════════════════════════════════════════════════
COPY shared/scripts/conda-mirror-setup.sh /usr/local/bin/conda-mirror-setup.sh
RUN chmod +x /usr/local/bin/conda-mirror-setup.sh && \
    echo "" && \
    echo "########################################################################" && \
    echo "# [CONDA VARIANT STAGE 3/5] Configure Mirror Sources (conda + pip)" && \
    echo "# CONDA_MIRROR=${CONDA_MIRROR}, PIP_MIRROR=${PIP_MIRROR}" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    CONDA_DIR=${CONDA_DIR} CONDA_MIRROR=${CONDA_MIRROR} PIP_MIRROR=${PIP_MIRROR} \
        /usr/local/bin/conda-mirror-setup.sh && \
    echo "" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.variant-build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "VS3=$_NOW" >> /tmp/.variant-build-timer && \
    echo "[TIMER] Stage 3/5 (mirror config) took ${_ELAPSED}s | Variant cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 3 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 4/5: Conda 激活脚本 + bashrc 配置 + 权限设置
# 变化频率：中
# 原则：
#   - 创建 /etc/profile.d/conda-init.sh（source 即可激活 conda）
#   - 不修改系统 PATH，保持 /opt/venv/bin 优先
#   - devuser 的 .bashrc 添加注释示例（不自动激活）
#   - 确保 /opt/conda 权限正确（devuser 可读）
# ═══════════════════════════════════════════════════════════════════
RUN <<'STAGE4_EOF'
echo ""
echo "########################################################################"
echo "# [CONDA VARIANT STAGE 4/5] Activation Script + Permissions"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
echo "[ACTION] Creating /etc/profile.d/conda-init.sh activation script..."
cat > /etc/profile.d/conda-init.sh << 'CONDA_INIT_EOF'
#!/bin/bash
# =============================================================================
# Conda Initialization Script for DevContainer Conda Variant
# Usage: source /etc/profile.d/conda-init.sh && conda activate base
# Note: This does NOT modify PATH by default. System venv (/opt/venv) remains
#       the default Python for services like Jupyter. Source this script
#       explicitly when you need conda environments.
# =============================================================================

if [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then
    source "/opt/conda/etc/profile.d/conda.sh"
else
    echo "[WARN] conda.sh not found at /opt/conda/etc/profile.d/conda.sh" >&2
    return 1 2>/dev/null || exit 1
fi
CONDA_INIT_EOF
chmod +x /etc/profile.d/conda-init.sh
echo "[OK] /etc/profile.d/conda-init.sh created"
echo ""
echo "=== /etc/profile.d/conda-init.sh contents ==="
cat /etc/profile.d/conda-init.sh
echo "=== end ==="
echo ""
echo "[ACTION] Configuring devuser .bashrc (no auto-activation, example only)..."
cat >> /home/devuser/.bashrc << 'BASHRC_EOF'

# ── Conda (miniconda3 at /opt/conda) ──────────────────────────────────────
# To use conda, uncomment the following lines or run:
#   source /etc/profile.d/conda-init.sh && conda activate base
# Note: System venv (/opt/venv) is the default Python for Jupyter and services.
#       Conda is NOT auto-activated to avoid breaking service PATH priority.
#
# source /etc/profile.d/conda-init.sh
# conda activate base
BASHRC_EOF
echo "[OK] devuser .bashrc updated with conda section (commented, manual activation only)"
echo ""
echo "[ACTION] Configuring root .bashrc similarly..."
cat >> /root/.bashrc << 'BASHRC_EOF'

# ── Conda (miniconda3 at /opt/conda) ──────────────────────────────────────
# source /etc/profile.d/conda-init.sh && conda activate base
BASHRC_EOF
echo "[OK] root .bashrc updated"
echo ""
echo "[ACTION] Setting /opt/conda permissions..."
chown -R root:root /opt/conda
chmod -R a+rX /opt/conda
find /opt/conda -type d -exec chmod 755 {} \;
echo "[OK] /opt/conda permissions set (world-readable, root-owned)"
echo ""
echo "[ACTION] Verifying PATH priority (venv before conda in default PATH)..."
echo "  Default PATH: $PATH"
echo "  Default python: $(which python) -> $(python --version 2>&1)"
echo "  Default pip: $(which pip) -> $(pip --version 2>&1 | awk '{print $2}')"
echo "  Conda python (absolute): /opt/conda/bin/python -> $(/opt/conda/bin/python --version 2>&1)"
echo "  System venv python (absolute): /opt/venv/bin/python -> $(/opt/venv/bin/python --version 2>&1)"
echo ""
echo "[ACTION] Verifying activation script works..."
bash -c 'source /etc/profile.d/conda-init.sh && conda --version && echo "[OK] conda activation via profile.d works in non-interactive shell"'
echo ""
chown devuser:devuser /home/devuser/.bashrc /home/devuser/.config/pip/pip.conf
echo "[OK] devuser ownership restored for .bashrc and pip.conf"
_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.variant-build-timer | cut -d= -f2)
_TOTAL=$((_NOW - _START))
echo "VS4=$_NOW" >> /tmp/.variant-build-timer
echo "[TIMER] Stage 4/5 (activation+perms) took ${_ELAPSED}s | Variant cumulative: ${_TOTAL}s"
echo '[OK] Stage 4 complete'
STAGE4_EOF

# ═══════════════════════════════════════════════════════════════════
# Stage 5/5: build-info + 清理 + 最终验证 + 计时器汇总表
# 变化频率：最低
# 原则：写入 variant build-info；清理缓存；最终验证所有关键组件；
#       确认 /opt/venv 仍然存在且是默认 Python；输出耗时汇总表
# ═══════════════════════════════════════════════════════════════════
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [CONDA VARIANT STAGE 5/5] Final Metadata, Cleanup, Verification" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[ACTION] Writing build metadata to /etc/devcontainer-variant-conda-build-info..."; \
    CONDA_VERSION=$(/opt/conda/bin/conda --version 2>&1 | awk '{print $2}'); \
    CONDA_PYTHON_VERSION=$(/opt/conda/bin/python --version 2>&1 | awk '{print $2}'); \
    printf '%s\n' \
        "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        "VARIANT=conda" \
        "BASE_IMAGE=devcontainer-base:${BASE_TAG}" \
        "MINICONDA_VERSION=${MINICONDA_VERSION}" \
        "CONDA_VERSION=${CONDA_VERSION}" \
        "PYTHON_VERSION_REQUESTED=${PYTHON_VERSION}" \
        "CONDA_PYTHON_VERSION=${CONDA_PYTHON_VERSION}" \
        "CONDA_DIR=/opt/conda" \
        "CONDA_MIRROR=${CONDA_MIRROR}" \
        "PIP_MIRROR=${PIP_MIRROR}" \
        "APT_MIRROR=${APT_MIRROR}" \
        "AUTO_ACTIVATE_BASE=false" \
        "ACTIVATION_SCRIPT=/etc/profile.d/conda-init.sh" \
        "SYSTEM_VENV=/opt/venv" \
        "PATH_PRIORITY=venv-first" \
        "SERVICES_PRESERVED=sshd,dockerd,podman,jupyter,supervisord" \
        "BUILD_TIMER=enabled" \
        > /etc/devcontainer-variant-conda-build-info && \
    echo "[OK] Build metadata written:"; \
    cat /etc/devcontainer-variant-conda-build-info; \
    echo ""; \
    echo "[ACTION] Running cleanup..."; \
    "${CONDA_DIR}/bin/conda" clean -ya -q 2>/dev/null || true; \
    /opt/venv/bin/pip cache purge 2>/dev/null || true; \
    apt-get clean 2>/dev/null || true; \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*; \
    echo "[OK] Cleanup complete (conda clean, pip cache purge, apt clean, tmp)"; \
    echo ""; \
    echo "┌─────────────────────────────────────────────────┐"; \
    echo "│  [VALIDATION CHECKPOINT - Stage 5/5]           │"; \
    echo "│  Running final syntax + availability checks     │"; \
    echo "└─────────────────────────────────────────────────┘"; \
    echo ""; \
    echo "[VALIDATE 1/7] bash -n /etc/profile.d/conda-init.sh..."; \
    bash -n /etc/profile.d/conda-init.sh && echo "[OK] conda-init.sh bash syntax valid"; \
    echo "[VALIDATE 2/7] conda binary exists and is executable..."; \
    test -x /opt/conda/bin/conda && echo "[OK] /opt/conda/bin/conda is executable"; \
    /opt/conda/bin/conda --version; \
    echo "[VALIDATE 3/7] System venv /opt/venv preserved..."; \
    test -d /opt/venv && test -x /opt/venv/bin/python && echo "[OK] /opt/venv exists with python binary"; \
    /opt/venv/bin/python --version; \
    echo "[VALIDATE 4/7] Default PATH python is from venv (not conda)..."; \
    DEFAULT_PYTHON=$(which python); \
    echo "  which python -> $DEFAULT_PYTHON"; \
    if [[ "$DEFAULT_PYTHON" == /opt/venv/bin/python ]]; then \
        echo "[OK] Default python is correctly from system venv (/opt/venv)"; \
    else \
        echo "[WARN] Default python is not from /opt/venv! PATH priority may be wrong: $DEFAULT_PYTHON"; \
    fi; \
    echo "[VALIDATE 5/7] Jupyter still available via venv..."; \
    /opt/venv/bin/jupyter --version 2>&1 | head -3; \
    echo "[OK] Jupyter available from venv"; \
    echo "[VALIDATE 6/7] Docker and supervisord still present..."; \
    docker --version 2>&1; \
    supervisord --version 2>&1; \
    echo "[OK] Core services preserved"; \
    echo "[VALIDATE 7/7] devuser can read conda directory..."; \
    su - devuser -c "test -r /opt/conda/bin/conda && /opt/conda/bin/conda --version" && echo "[OK] devuser can access conda"; \
    echo ""; \
    echo "[VALIDATE] All validation checks completed"; \
    echo ""; \
    echo "┌─────────────────────────────────────────────────┐"; \
    echo "│  [FINAL VERIFICATION - ACTIVATION TEST]         │"; \
    echo "│  Testing source /etc/profile.d/conda-init.sh    │"; \
    echo "└─────────────────────────────────────────────────┘"; \
    bash -l -c 'source /etc/profile.d/conda-init.sh && conda activate base && echo "  Activated conda base successfully" && echo "  Python after activation: $(which python) -> $(python --version)" && conda info --envs' && \
    echo ""; \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.variant-build-timer | cut -d= -f2) && \
    _VS1=$(grep '^VS1=' /tmp/.variant-build-timer | cut -d= -f2) && \
    _VS2=$(grep '^VS2=' /tmp/.variant-build-timer | cut -d= -f2) && \
    _VS3=$(grep '^VS3=' /tmp/.variant-build-timer | cut -d= -f2) && \
    _VS4=$(grep '^VS4=' /tmp/.variant-build-timer | cut -d= -f2) && \
    _VT1=$((_VS1 - _START)) && \
    _VT2=$((_VS2 - _VS1)) && \
    _VT3=$((_VS3 - _VS2)) && \
    _VT4=$((_VS4 - _VS3)) && \
    _VT5=$_ELAPSED && \
    _VTOTAL=$((_NOW - _START)) && \
    echo "[TIMER] Stage 5/5 (metadata+final verify) took ${_ELAPSED}s | Variant cumulative: ${_VTOTAL}s" && \
    echo "╔══════════════════════════════════════════════════════════════╗"; \
    echo "║     BUILD TIMING SUMMARY (Conda Variant - 5 Add Stages)    ║"; \
    echo "╠══════════════════════════════════════════════════════════════╣"; \
    printf "║  Stage 1/5  system packages check     %5ds               ║\n" $_VT1; \
    printf "║  Stage 2/5  Miniconda3 install        %5ds               ║\n" $_VT2; \
    printf "║  Stage 3/5  conda/pip mirror config   %5ds               ║\n" $_VT3; \
    printf "║  Stage 4/5  activation script+perms   %5ds               ║\n" $_VT4; \
    printf "║  Stage 5/5  metadata+final verify     %5ds               ║\n" $_VT5; \
    echo "╠══════════════════════════════════════════════════════════════╣"; \
    printf "║  VARIANT TOTAL (add-on layers)        %5ds               ║\n" $_VTOTAL; \
    echo "╚══════════════════════════════════════════════════════════════╝"; \
    echo ""; \
    rm -f /tmp/.variant-build-timer; \
    echo "########################################################################"; \
    echo "# CONDA VARIANT BUILD COMPLETE!"; \
    echo "# Conda available at /opt/conda (not in default PATH)"; \
    echo "# Activate with: source /etc/profile.d/conda-init.sh && conda activate base"; \
    echo "# System venv /opt/venv preserved as default Python for services"; \
    echo "########################################################################"; \
    echo ""
