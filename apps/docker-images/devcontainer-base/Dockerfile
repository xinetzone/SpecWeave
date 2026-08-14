# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - Dockerfile (Multi-stage build)
# Project: SpecWeave Full-featured Development Container Base Image
# Base: ubuntu:26.04 | OpenSSH + Docker DinD + Podman(rootless) + Jupyter + Miniforge3(conda-forge, libmamba)
# Locale: zh_CN.UTF-8 / Timezone: Asia/Shanghai
# Non-root user: devuser (UID 1000 if available, auto-assigned otherwise)
# Services: sshd(22) + dockerd(2375) + podman(rootless) + jupyter(8888), managed by supervisord
# Python: Miniforge3 (conda-forge) at /opt/conda (Python 3.14.6 free-threading cp314t, libgcc-ng 16.1.0运行时, libmamba solver), Jupyter在main环境
# BuildKit cache: pip (/root/.cache/pip) + conda pkgs (/opt/conda/pkgs) + libmamba solver (/root/.cache/conda) 持久化缓存
# Verify modes: BUILD_VERIFY_MODE=standard (default, full checks) | fast (essential only) | off (skip)
#
# Build: docker build -t devcontainer-base .
# CN:    docker build --build-arg APT_MIRROR=aliyun --build-arg PIP_MIRROR=aliyun --build-arg DOCKER_MIRROR=aliyun --build-arg CONDA_MIRROR=tuna -t devcontainer-base .
# Run:   docker run -d --privileged -p 2222:22 -p 2375:2375 -p 8888:8888 \
#          -e USER_PASSWORD=pass -e JUPYTER_TOKEN=mysecret -e GRANT_SUDO=yes \
#          -v $(pwd)/workspace:/workspace -v docker-data:/var/lib/docker devcontainer-base
# Debug: docker run -it --rm --privileged devcontainer-base bash
#
# Runtime Stage Layering (dockerfile-runtime-logical-layering pattern v1.3):
#   Stage 2.1/7: 系统包 + APT镜像 + locale/timezone (变化频率: 最低)
#   Stage 2.2/7: Docker CE 安装 (变化频率: 低)
#   Stage 2.3/7: Podman rootless 安装 (变化频率: 低)
#   Stage 2.4/7: Miniforge3 (conda-forge) 安装 + Python 3.14 cp314t + libmamba + Jupyter (变化频率: 中)
#   Stage 2.5/7: 用户/组 + subuid/subgid + 运行时目录 + daemon.json (变化频率: 中)
#   Stage 2.6/7: 配置文件 COPY + 权限 + 语法验证 (变化频率: 高)
#   Stage 2.7/7: build-info + 激进清理 + 最终验证 (变化频率: 最低)
#
# Build Timing: 每个Stage结束时输出 [TIMER] 本阶段耗时+累计耗时，最终输出汇总表
# =============================================================================

ARG APT_MIRROR=official
ARG PIP_MIRROR=official
ARG CONDA_MIRROR=official
ARG PYTHON_VERSION=3.14.6
ARG PYTHON_BUILD=cp314t
ARG BUILD_VERIFY_MODE=standard

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Minimal production image with Micromamba
# -----------------------------------------------------------------------------
FROM ubuntu:26.04

ARG APT_MIRROR
ARG DOCKER_MIRROR=official
ARG CONDA_MIRROR
ARG PIP_MIRROR
ARG PYTHON_VERSION
ARG PYTHON_BUILD
ARG BUILD_VERIFY_MODE

LABEL maintainer="SpecWeave"
LABEL description="Full-featured Ubuntu 26.04 dev container with SSH + Docker DinD + Podman(rootless) + Jupyter + Miniforge3(Python 3.14.6 free-threading cp314t, GCC 14.4.0编译, libgcc 16.1.0运行时, conda-forge, libmamba solver), managed by supervisord"
LABEL version="2.2-ft"

# ── 元数据层：环境变量声明（不产生层，仅元数据） ──
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai \
    LANG=zh_CN.UTF-8 \
    LANGUAGE=zh_CN:zh \
    LC_ALL=zh_CN.UTF-8 \
    CONDA_DIR=/opt/conda \
    CONDA_DEFAULT_ENV=main \
    PATH="/opt/conda/envs/main/bin:/opt/conda/bin:${PATH}" \
    NON_ROOT_USER=devuser \
    JUPYTER_PORT=8888 \
    SSH_PORT=22 \
    GRANT_SUDO=no \
    ALLOW_ROOT_SSH=no \
    JUPYTER_ALLOW_ORIGIN= \
    ENABLE_SSH=yes \
    ENABLE_DOCKER=yes \
    ENABLE_PODMAN=no \
    ENABLE_JUPYTER=yes

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# ═══════════════════════════════════════════════════════════════════
# Stage 2.1/7: 系统包安装 + APT镜像 + locale/timezone 配置
# 变化频率：最低（基础镜像确定后很少改）
# 原则：--no-install-recommends，同层完成APT镜像配置+locale+tz+清理
#       初始化计时器 /tmp/.build-timer
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    echo "=== Stage 1/7: Install base system packages + Chinese locale ===" && \
    _STAGE_START=$(date +%s) && \
    echo "[TIMER] Runtime stage started at $(date -u +%Y-%m-%dT%H:%M:%SZ)" && \
    echo "START=$_STAGE_START" > /tmp/.build-timer && \
    echo "[BUILD] Configuring APT mirror: ${APT_MIRROR:-official}" && \
    if [ "${APT_MIRROR}" = "aliyun" ]; then \
        sed -i 's|http://archive.ubuntu.com|http://mirrors.aliyun.com|g; s|http://security.ubuntu.com|http://mirrors.aliyun.com|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || \
        sed -i 's|http://archive.ubuntu.com|http://mirrors.aliyun.com|g; s|http://security.ubuntu.com|http://mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null || true; \
        echo "[BUILD] Using Aliyun APT mirror"; \
    elif [ "${APT_MIRROR}" = "tuna" ]; then \
        sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || \
        sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list 2>/dev/null || true; \
        echo "[BUILD] Using Tsinghua TUNA APT mirror"; \
    else \
        echo "[BUILD] Using official APT sources"; \
    fi && \
    echo "[INFO] Updating APT package lists..." && \
    apt-get update -qq && \
    echo "[INFO] Installing system packages (--no-install-recommends)..." && \
    apt-get install -y --no-install-recommends -qq \
        ca-certificates \
        curl \
        gnupg \
        iptables \
        iproute2 \
        kmod \
        locales \
        openssh-server \
        openssh-client \
        procps \
        pwgen \
        bzip2 \
        wget \
        sudo \
        supervisor \
        tini \
        tzdata \
        vim-tiny \
        xz-utils \
        uidmap \
        fuse-overlayfs \
        slirp4netns \
    && echo "[OK] Base system packages installed" && \
    echo "[INFO] Verifying key package versions:" && \
    echo "  - openssh-server: $(dpkg-query -W -f='${Version}' openssh-server 2>/dev/null || echo 'N/A')" && \
    echo "  - supervisor: $(supervisord --version 2>/dev/null || echo 'N/A')" && \
    echo "[BUILD] Generating zh_CN.UTF-8 locale..." && \
    sed -i 's/^# *zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen zh_CN.UTF-8 && \
    update-locale LANG=zh_CN.UTF-8 && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    echo "[BUILD] zh_CN locale + Asia/Shanghai timezone ready" && \
    rm -rf /var/lib/apt/lists/* && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _TOTAL=$((_NOW - $(grep '^START=' /tmp/.build-timer | cut -d= -f2))) && \
    echo "S1=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 1/7 (system+locale) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 2.2/7: Docker CE 安装
# 变化频率：低（Docker版本升级时改）
# 原则：GPG key + apt repo 配置 + 安装在同层完成，清理apt缓存
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    echo "=== Stage 2/7: Install Docker CE ===" && \
    _STAGE_START=$(date +%s) && \
    install -m 0755 -d /etc/apt/keyrings && \
    if [ "${DOCKER_MIRROR}" = "aliyun" ]; then \
        DOCKER_REPO="https://mirrors.aliyun.com/docker-ce/linux/ubuntu"; \
        echo "[BUILD] Using Aliyun Docker CE mirror: ${DOCKER_REPO}"; \
    else \
        DOCKER_REPO="https://download.docker.com/linux/ubuntu"; \
        echo "[BUILD] Using official Docker CE repo: ${DOCKER_REPO}"; \
    fi && \
    curl -fsSL ${DOCKER_REPO}/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo "[BUILD] Docker GPG key installed" && \
    . /etc/os-release && \
    echo "[BUILD] Ubuntu codename: ${VERSION_CODENAME}" && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] ${DOCKER_REPO} ${VERSION_CODENAME} stable" > /etc/apt/sources.list.d/docker.list && \
    echo "[INFO] Updating APT after adding Docker repo..." && \
    apt-get update -qq && \
    echo "[INFO] Installing Docker CE packages (docker-ce, containerd, buildx)..." && \
    apt-get install -y --no-install-recommends -qq \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
    && echo "[OK] Docker Engine installed" && \
    echo "[INFO] Docker component versions:" && \
    echo "  - docker: $(docker --version 2>/dev/null | awk '{print $3}' | tr -d ',')" && \
    echo "  - dockerd: $(dockerd --version 2>/dev/null | awk '{print $3}' | tr -d ',')" && \
    echo "  - containerd: $(containerd --version 2>/dev/null | awk '{print $3}')" && \
    echo "  - buildx: $(docker buildx version 2>/dev/null | awk '{print $2}')" && \
    rm -rf /var/lib/apt/lists/* && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S2=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 2/7 (Docker CE) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 2.3/7: Podman rootless 安装
# 变化频率：低（Podman版本升级时改）
# 原则：直接使用Ubuntu 26.04官方源，无需第三方repo
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    echo "=== Stage 3/7: Install Podman (rootless) ===" && \
    _STAGE_START=$(date +%s) && \
    echo "[INFO] Updating APT for Podman installation..." && \
    apt-get update -qq && \
    echo "[INFO] Installing Podman packages (podman, crun, conmon)..." && \
    apt-get install -y --no-install-recommends -qq \
        podman \
        crun \
        conmon \
    && echo "[OK] Podman installed" && \
    echo "[INFO] Podman version:" && \
    echo "  - podman: $(podman --version 2>/dev/null | awk '{print $3}')" && \
    echo "  - crun: $(crun --version 2>/dev/null | head -1 | awk '{print $2}')" && \
    rm -rf /var/lib/apt/lists/* && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S3=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 3/7 (Podman) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 2.4/7: Miniforge3 (conda-forge) 安装 + Python 3.14.6 cp314t free-threading + libmamba + Jupyter
# 变化频率：中（Python/包版本升级时改）
# 原则：Miniforge3（conda-forge官方发行版，无defaults channel/无Anaconda商业包）轻量安装到/opt/conda，
#       默认conda-forge channel + libmamba solver，Python 3.14.6使用cp314t free-threading构建（GIL默认禁用），
#       Python由GCC 14.4.0编译，运行时自动升级至libgcc 16.1.0（向后兼容，无ABI冲突），
#       Jupyter安装到main环境，安装后立即清理缓存，无ABI冲突
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,target=/root/.cache/conda,sharing=locked \
    --mount=type=bind,source=.cache,target=/tmp/local-cache,readonly \
    --mount=type=bind,source=variants/shared/scripts/conda-perf-setup.sh,target=/tmp/conda-perf-setup.sh,readonly \
    <<'STAGE4_EOF'
set -e
echo "=== Stage 4/7: Install Miniforge3 + Python ${PYTHON_VERSION} ${PYTHON_BUILD} (conda-forge, libmamba) + Jupyter ==="
_STAGE_START=$(date +%s)

# ── 辅助函数：conda 包分组安装（使用libmamba solver） ──
conda_install_group() {
    local group_name="$1" description="$2"
    shift 2
    local g_start g_end g_elapsed rc
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CONDA INSTALL] ${group_name}"
    echo "│ Desc: ${description}"
    echo "│ PKGS: $*"
    echo "└─────────────────────────────────────────────────┘"
    g_start=$(date +%s)
    set +e
    conda install -y -n base --solver=libmamba "$@" 2>&1
    rc=$?
    set -e
    g_end=$(date +%s)
    g_elapsed=$((g_end - g_start))
    if [ $rc -eq 0 ]; then
        echo "[OK] ${group_name} installed in ${g_elapsed}s"
    else
        echo "[FAIL] ${group_name} failed after ${g_elapsed}s (exit code: $rc)"
        exit $rc
    fi
}

# ── 辅助函数：pip 包分组安装 ──
pip_install_group() {
    local group_name="$1" description="$2"
    shift 2
    local g_start g_end g_elapsed rc
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [PIP INSTALL] ${group_name}"
    echo "│ Desc: ${description}"
    echo "│ PKGS: $*"
    echo "└─────────────────────────────────────────────────┘"
    g_start=$(date +%s)
    set +e
    pip install --timeout 120 --retries 5 "$@" 2>&1
    rc=$?
    set -e
    g_end=$(date +%s)
    g_elapsed=$((g_end - g_start))
    if [ $rc -eq 0 ]; then
        echo "[OK] ${group_name} installed in ${g_elapsed}s"
    else
        echo "[FAIL] ${group_name} failed after ${g_elapsed}s (exit code: $rc)"
        pip check 2>&1 | head -20 || true
        exit $rc
    fi
}

# ── 架构检测 + Miniforge3安装器URL ──
echo "[INFO] Detecting architecture..."
ARCH=$(uname -m)
case "$ARCH" in
    x86_64)  CONDA_ARCH="x86_64" ;;
    aarch64) CONDA_ARCH="aarch64" ;;
    *) echo "[ERROR] Unsupported architecture: $ARCH"; exit 1 ;;
esac
echo "[OK] Architecture: $ARCH ($CONDA_ARCH)"

# ── 下载并安装 Miniforge3（conda-forge官方发行版，无defaults包，原生libmamba支持） ──
echo "[INFO] Downloading Miniforge3 installer (conda-forge official)..."
_dl_start=$(date +%s)

LOCAL_INSTALLER=""
for f in /tmp/local-cache/Miniforge3-Latest-Linux-${CONDA_ARCH}.sh \
         /tmp/local-cache/Miniforge3-*-Linux-${CONDA_ARCH}.sh; do
    if [ -f "$f" ] && [ -s "$f" ]; then
        LOCAL_INSTALLER="$f"
        break
    fi
done

if [ -n "$LOCAL_INSTALLER" ]; then
    echo "[OK] Using local cached installer: $LOCAL_INSTALLER ($(du -h "$LOCAL_INSTALLER" | cut -f1))"
    cp "$LOCAL_INSTALLER" /tmp/miniforge.sh
    DL_OK=1
else
    echo "[INFO] No local cache found, downloading from network..."
    # Miniforge3下载源：GitHub官方 + 国内镜像
    if [ "${CONDA_MIRROR}" = "tuna" ]; then
        DL_URLS=(
            "https://mirrors.tuna.tsinghua.edu.cn/github-release/conda-forge/miniforge/LatestRelease/Miniforge3-Linux-${CONDA_ARCH}.sh"
            "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-${CONDA_ARCH}.sh"
        )
    elif [ "${CONDA_MIRROR}" = "aliyun" ]; then
        DL_URLS=(
            "https://mirrors.aliyun.com/github-release/conda-forge/miniforge/LatestRelease/Miniforge3-Linux-${CONDA_ARCH}.sh"
            "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-${CONDA_ARCH}.sh"
        )
    else
        DL_URLS=(
            "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-${CONDA_ARCH}.sh"
        )
    fi

    DL_OK=0
    for dl_url in "${DL_URLS[@]}"; do
        echo "[INFO] Trying: $dl_url"
        if curl -fsSL --connect-timeout 30 --max-time 300 --retry 3 --retry-delay 5 \
            -L -o /tmp/miniforge.sh "$dl_url" 2>/tmp/conda_dl_err.log; then
            echo "[OK] Downloaded from: $dl_url"
            DL_OK=1
            break
        else
            echo "[WARN] Failed, trying next source..."
            cat /tmp/conda_dl_err.log | tail -3
        fi
    done

    if [ "$DL_OK" = "0" ]; then
        echo "[ERROR] Failed to download Miniforge3 from all sources"
        cat /tmp/conda_dl_err.log
        exit 1
    fi
fi

_dl_elapsed=$(($(date +%s) - _dl_start))
echo "[OK] Installer ready: $(du -h /tmp/miniforge.sh | cut -f1) in ${_dl_elapsed}s"

echo "[INFO] Installing Miniforge3 to ${CONDA_DIR}..."
bash /tmp/miniforge.sh -b -p "${CONDA_DIR}" -f
rm -f /tmp/miniforge.sh
echo "[OK] Miniforge3 installed: $("${CONDA_DIR}/bin/conda" --version 2>&1)"

# ── Source conda.sh 使 conda 命令在当前 shell 完全可用 ──
. "${CONDA_DIR}/etc/profile.d/conda.sh"
echo "[OK] conda.sh sourced, conda available in build shell"

# ── Miniforge3默认已配置conda-forge channel和libmamba solver，无需额外ToS/defaults清理 ──
echo "[INFO] Miniforge3 defaults: conda-forge channel + libmamba solver pre-configured"

# ── 使用共享脚本配置性能参数 + 合并镜像源配置 ──
echo "[INFO] Configuring conda performance and mirror sources..."
chmod +x /tmp/conda-perf-setup.sh
# 运行性能配置（线程、超时、重试），输出到临时位置后合并镜像源配置
CONDA_DIR="${CONDA_DIR}" CONDA_MIRROR="${CONDA_MIRROR}" CONDA_THREADS=8 \
    CONDA_OUTPUT=/tmp/condarc-perf.yaml bash /tmp/conda-perf-setup.sh
echo ""
echo "[ACTION] Writing system-level ${CONDA_DIR}/.condarc with mirror sources..."
case "${CONDA_MIRROR}" in
    bfsu)
        echo "[INFO] Configuring conda for BFSU (Beijing Foreign Studies University) mirror (conda-forge only, no defaults)"
        printf '%s\n' \
            'channels:' \
            '  - conda-forge' \
            'show_channel_urls: true' \
            'channel_priority: strict' \
            'default_channels_alias: https://mirrors.bfsu.edu.cn/anaconda/cloud' \
            'custom_channels:' \
            '  conda-forge: https://mirrors.bfsu.edu.cn/anaconda/cloud' \
            'ssl_verify: true' \
            'auto_activate_base: false' \
            'remote_connect_timeout_secs: 30' \
            'remote_read_timeout_secs: 120' \
            'remote_max_retries: 5' \
            'remote_backoff_factor: 3' \
            'repodata_threads: 8' \
            'execute_threads: 8' \
            'solver: libmamba' \
            > "${CONDA_DIR}/.condarc"
        ;;
    tuna)
        echo "[INFO] Configuring conda for Tsinghua TUNA mirror (conda-forge only, no defaults)"
        printf '%s\n' \
            'channels:' \
            '  - conda-forge' \
            'show_channel_urls: true' \
            'channel_priority: strict' \
            'default_channels_alias: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud' \
            'custom_channels:' \
            '  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud' \
            'ssl_verify: true' \
            'auto_activate_base: false' \
            'remote_connect_timeout_secs: 30' \
            'remote_read_timeout_secs: 120' \
            'remote_max_retries: 5' \
            'remote_backoff_factor: 3' \
            'repodata_threads: 8' \
            'execute_threads: 8' \
            'solver: libmamba' \
            > "${CONDA_DIR}/.condarc"
        ;;
    *)
        echo "[INFO] Configuring conda for official channels (conda-forge only, no defaults)"
        printf '%s\n' \
            'channels:' \
            '  - conda-forge' \
            'show_channel_urls: true' \
            'channel_priority: strict' \
            'ssl_verify: true' \
            'auto_activate_base: false' \
            'remote_connect_timeout_secs: 30' \
            'remote_read_timeout_secs: 300' \
            'remote_max_retries: 5' \
            'remote_backoff_factor: 3' \
            'repodata_threads: 8' \
            'execute_threads: 8' \
            'solver: libmamba' \
            > "${CONDA_DIR}/.condarc"
        ;;
esac
echo "[OK] System-level .condarc written:"
cat "${CONDA_DIR}/.condarc"
echo "[INFO] mamba version: $(mamba --version 2>&1 | head -1)"

# ── Miniforge3自带Python，不要升级base Python（conda无cp314t构建） ──
_builtin_py=$("${CONDA_DIR}/bin/python" --version 2>&1 | awk '{print $2}')
echo "[INFO] Miniforge3 base Python (conda runtime): ${_builtin_py}"
echo "[INFO] Note: conda has no cp314t build on conda-forge yet, so we keep base Python ${_builtin_py}"
echo "[INFO] Creating a dedicated 'main' environment with Python ${PYTHON_VERSION} ${PYTHON_BUILD}..."

# ── Step 1: 一次性创建main环境（Python cp314t + pip + Jupyter生态，单次solver求解） ──
# 优化：使用mamba CLI直接调用libmamba（比conda --solver=libmamba少Python层开销）；
#       合并create+install为单次mamba create（减少一次solver运行）；
#       8线程并行下载+解压（repodata_threads/execute_threads=8在.condarc中配置）
echo "[INFO] Creating 'main' env with Python ${PYTHON_VERSION} ${PYTHON_BUILD} + Jupyter (single mamba solve)..."
_mamba_start=$(date +%s)
mamba create -y -n main -c conda-forge --override-channels -q \
    "python=${PYTHON_VERSION}=*_${PYTHON_BUILD}" \
    pip \
    "jupyterlab>=4.4" \
    "notebook>=7.3" \
    ipykernel \
    nbconvert \
    jupyter_server 2>&1
_mamba_elapsed=$(($(date +%s) - _mamba_start))
echo "[OK] main env created in ${_mamba_elapsed}s with Python $(/opt/conda/envs/main/bin/python --version 2>&1 | awk '{print $2}')"
echo "[OK] Jupyter ecosystem installed: $(/opt/conda/envs/main/bin/jupyter --version 2>&1 | head -1)"

# ── 配置 PyPI 镜像（root + base + main 环境，devuser 在 Stage 2.5 创建后配置） ──
echo "[ACTION] Configuring pip mirrors..."
mkdir -p /root/.config/pip
case "${PIP_MIRROR}" in
    aliyun)
        echo "[INFO] Configuring pip for Aliyun mirror"
        PIP_INDEX_URL="https://mirrors.aliyun.com/pypi/simple/"
        PIP_TRUSTED_HOST="mirrors.aliyun.com"
        ;;
    tuna)
        echo "[INFO] Configuring pip for Tsinghua TUNA mirror"
        PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple/"
        PIP_TRUSTED_HOST="pypi.tuna.tsinghua.edu.cn"
        ;;
    *)
        echo "[INFO] Configuring pip for official PyPI"
        PIP_INDEX_URL="https://pypi.org/simple/"
        PIP_TRUSTED_HOST=""
        ;;
esac
# 写入 root 全局 pip.conf
printf '%s\n' \
    '[global]' \
    "index-url = ${PIP_INDEX_URL}" \
    "retries = 5" \
    "timeout = 60" \
    > /root/.config/pip/pip.conf
if [ -n "${PIP_TRUSTED_HOST}" ]; then
    printf '%s\n' "trusted-host = ${PIP_TRUSTED_HOST}" >> /root/.config/pip/pip.conf
fi
# 配置 conda base 环境 pip
if [ "${PIP_MIRROR}" = "aliyun" ]; then
    "${CONDA_DIR}/bin/pip" config set global.index-url https://mirrors.aliyun.com/pypi/simple/
    "${CONDA_DIR}/bin/pip" config set global.trusted-host mirrors.aliyun.com
elif [ "${PIP_MIRROR}" = "tuna" ]; then
    "${CONDA_DIR}/bin/pip" config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
    "${CONDA_DIR}/bin/pip" config set global.trusted-host pypi.tuna.tsinghua.edu.cn
fi
# 配置 main 环境 pip
/opt/conda/envs/main/bin/pip config set global.index-url "${PIP_INDEX_URL}"
if [ -n "${PIP_TRUSTED_HOST}" ]; then
    /opt/conda/envs/main/bin/pip config set global.trusted-host "${PIP_TRUSTED_HOST}"
fi
echo "[OK] pip mirrors configured (root + base + main; devuser will be configured in Stage 2.5)"
# 将 PIP 配置变量导出到临时文件，供 Stage 2.5 使用
echo "PIP_INDEX_URL=${PIP_INDEX_URL}" > /tmp/pip-config.env
echo "PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST}" >> /tmp/pip-config.env

# ── 注册main环境为Jupyter默认kernel（Python 3.14 free-threading） ──
/opt/conda/envs/main/bin/python -m ipykernel install --name main --display-name "Python ${PYTHON_VERSION} (free-threading)" --prefix=/opt/conda/envs/main 2>&1
echo "[OK] Jupyter kernel registered: Python ${PYTHON_VERSION} (free-threading)"

# ── 验证free-threading构建 ──
if [ "${PYTHON_BUILD}" = "cp314t" ]; then
    /opt/conda/envs/main/bin/python -c "
import sys, sysconfig
ft = sysconfig.get_config_var('Py_GIL_DISABLED')
soabi = sysconfig.get_config_var('SOABI')
assert ft == 1, f'Expected free-threading build, got Py_GIL_DISABLED={ft}'
assert 'cpython-314t' in soabi, f'Expected cpython-314t in SOABI, got {soabi}'
print(f'[OK] Free-threading verified: Python {sys.version.split()[0]}, SOABI={soabi}, GIL disabled by default')
    "
fi

# ── main环境激活将在 Stage 2.5 通过 conda-init.sh 统一配置 ──
echo "[INFO] main environment activation will be configured via conda-init.sh in Stage 2.5"

# ── 清理临时文件（不清理BuildKit cache挂载目录：/root/.cache/pip, /opt/conda/pkgs, /root/.cache/conda） ──
echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│ [CLEAN] Removing temp/installer files          │"
echo "│ (BuildKit cache mounts preserved for reuse)    │"
echo "└─────────────────────────────────────────────────┘"
rm -f /tmp/miniforge.sh /tmp/conda_dl_err.log 2>/dev/null || true
echo "[OK] Temp files cleaned (conda/pip caches preserved in BuildKit mounts)"

# ── 验证安装 ──
echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│ [VERIFY] Conda + Python (main env) + Jupyter   │"
echo "└─────────────────────────────────────────────────┘"
"${CONDA_DIR}/bin/conda" --version
/opt/conda/envs/main/bin/python --version
/opt/conda/envs/main/bin/jupyter --version
echo "  - conda dir: ${CONDA_DIR}"
echo "  - main env python: /opt/conda/envs/main/bin/python"
echo "  - main env jupyter: $(/opt/conda/envs/main/bin/jupyter --version 2>&1 | head -1)"
echo "  - default solver: libmamba"

_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2)
_TOTAL=$((_NOW - _START))
echo "S4=$_NOW" >> /tmp/.build-timer
echo "[TIMER] Stage 4/7 (conda+libmamba+jupyter) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"
echo '[OK] Stage 4 complete'
STAGE4_EOF

# ═══════════════════════════════════════════════════════════════════
# Stage 2.5/7: 用户/组/工作目录创建 + subuid/subgid + 权限设置
# 变化频率：中（新增用户或目录时改）
# 原则：UID 优先固定值 1000；docker组必须存在；配置rootless podman的
#       subuid/subgid；chown在同层完成；写入~/.bashrc和/etc/environment
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== Stage 5/7: Create non-root user devuser ===" && \
    _STAGE_START=$(date +%s) && \
    groupadd -f docker && \
    if getent passwd devuser >/dev/null 2>&1; then \
        echo "[BUILD] User devuser already exists (UID=$(id -u devuser)), ensuring group membership..."; \
        usermod -aG docker,sudo devuser; \
    elif ! getent passwd 1000 >/dev/null 2>&1; then \
        echo "[BUILD] UID 1000 is free, creating devuser with UID 1000"; \
        useradd -m -s /bin/bash -u 1000 -G docker,sudo devuser; \
    else \
        EXISTING_USER=$(getent passwd 1000 | cut -d: -f1); \
        echo "[BUILD] UID 1000 occupied by '${EXISTING_USER}', auto-assigning UID for devuser"; \
        useradd -m -s /bin/bash -G docker,sudo devuser; \
    fi && \
    echo "[BUILD] User devuser created: UID=$(id -u devuser) GID=$(id -g devuser) groups=$(groups devuser)" && \
    echo "[BUILD] Configuring subuid/subgid for rootless podman..." && \
    echo "devuser:100000:65536" > /etc/subuid && \
    echo "devuser:100000:65536" > /etc/subgid && \
    cat /etc/subuid && cat /etc/subgid && \
    mkdir -p /workspace /home/devuser/.jupyter/jupyter_server_config.d /home/devuser/.ssh && \
    chmod 755 /workspace && \
    chmod 700 /home/devuser/.ssh && \
    chown -R devuser:devuser /workspace /home/devuser/.jupyter /home/devuser/.ssh && \
    echo "[BUILD] Working directory /workspace and .jupyter/.ssh directories created with proper permissions" && \
    echo "[BUILD] Configuring devuser pip mirror..." && \
    mkdir -p /home/devuser/.config/pip && \
    cp /root/.config/pip/pip.conf /home/devuser/.config/pip/pip.conf && \
    chown -R devuser:devuser /home/devuser/.config && \
    echo "[OK] devuser pip mirror configured" && \
    echo "[BUILD] Creating conda initialization script..." && \
    printf '%s\n' \
        '#!/bin/bash' \
        '# Conda main environment (Python 3.14 free-threading) activation' \
        'if [ -f /opt/conda/etc/profile.d/conda.sh ]; then' \
        '    . /opt/conda/etc/profile.d/conda.sh' \
        '    conda activate main 2>/dev/null || conda activate base 2>/dev/null || true' \
        'fi' \
        > /etc/profile.d/conda-init.sh && \
    chmod +x /etc/profile.d/conda-init.sh && \
    echo "source /etc/profile.d/conda-init.sh" >> /home/devuser/.bashrc && \
    echo "source /etc/profile.d/conda-init.sh" >> /root/.bashrc && \
    chown devuser:devuser /home/devuser/.bashrc && \
    echo "PATH=/opt/conda/envs/main/bin:/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >> /etc/environment && \
    echo "[BUILD] User .bashrc and /etc/environment configured (conda main env PATH priority)" && \
    echo "[BUILD] Preparing runtime directories and Docker daemon.json..." && \
    mkdir -p /run/sshd && chmod 755 /run/sshd && \
    mkdir -p /var/log/supervisor /etc/supervisor/conf.d /etc/docker && \
    printf '{\n  "storage-driver": "overlay2",\n  "iptables": false,\n  "log-driver": "json-file",\n  "log-opts": {"max-size": "10m", "max-file": "3"},\n  "userland-proxy": false\n}\n' > /etc/docker/daemon.json && \
    echo "[BUILD] Runtime directories + daemon.json ready" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S5=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 5/7 (user+subuid+dirs+daemon) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 2.6/7: 配置文件 COPY + 权限设置 + 语法验证
# 变化频率：高（配置调整时改，缓存不会让前面层失效）
# 原则：所有 COPY 集中在一处；同层 RUN 做权限 + 全部语法验证
# ═══════════════════════════════════════════════════════════════════
COPY config/sshd_config /etc/ssh/sshd_config
COPY config/supervisord.conf /etc/supervisor/supervisord.conf
COPY config/supervisor/conf.d/ /etc/supervisor/conf.d/
COPY config/jupyter_notebook_config.py /home/devuser/.jupyter/jupyter_notebook_config.py
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY scripts/healthcheck.sh /usr/local/bin/healthcheck.sh
COPY scripts/verify-cext.sh /usr/local/bin/verify-cext.sh
COPY scripts/ft-benchmark.sh /usr/local/bin/ft-benchmark.sh

RUN echo "=== Stage 6/7: Config permissions + syntax validation ===" && \
    _STAGE_START=$(date +%s) && \
    chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/healthcheck.sh /usr/local/bin/verify-cext.sh /usr/local/bin/ft-benchmark.sh && \
    chown -R devuser:devuser /home/devuser/.jupyter && \
    chown -R devuser:devuser /workspace && \
    echo "[BUILD] Permissions set: entrypoint.sh and healthcheck.sh executable" && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│  [VALIDATION CHECKPOINT - Stage 6/7]            │" && \
    echo "│  Running syntax validation for all configs      │" && \
    echo "└─────────────────────────────────────────────────┘" && \
    echo "[VALIDATE 1/5] sshd -t (SSH daemon config syntax)..." && \
    sshd -t && echo "[OK] sshd_config syntax valid" && \
    echo "[VALIDATE 2/5] bash -n entrypoint.sh..." && \
    bash -n /usr/local/bin/entrypoint.sh && echo "[OK] entrypoint.sh bash syntax valid" && \
    echo "[VALIDATE 3/5] bash -n healthcheck.sh..." && \
    bash -n /usr/local/bin/healthcheck.sh && echo "[OK] healthcheck.sh bash syntax valid" && \
    echo "[VALIDATE 4/5] bash -n verify-cext.sh..." && \
    bash -n /usr/local/bin/verify-cext.sh && echo "[OK] verify-cext.sh bash syntax valid" && \
    echo "[VALIDATE 5/5] bash -n ft-benchmark.sh..." && \
    bash -n /usr/local/bin/ft-benchmark.sh && echo "[OK] ft-benchmark.sh bash syntax valid" && \
    echo "" && \
    echo "[BUILD] All 5 syntax validation checks passed" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S6=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 6/7 (config+validation) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 2.7/7: 构建元数据 + 激进清理 + 最终验证
# 变化频率：最低（版本发布时改）
# 原则：写入build-info；激进清理doc/man/info/__pycache__/.pyc/静态库；
#       strip二进制；最终验证所有关键命令可执行；输出耗时汇总表
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== Stage 7/7: Final metadata, aggressive cleanup, and verification ===" && \
    _STAGE_START=$(date +%s) && \
    DEVUSER_UID=$(id -u devuser) && \
    CONDA_VERSION=$(conda --version 2>&1 | awk '{print $2}') && \
    PYTHON_VERSION_ACTUAL=$(python --version 2>&1 | awk '{print $2}') && \
    PYTHON_BUILD_TYPE=$(python -c 'import sysconfig; print("free-threading" if sysconfig.get_config_var("Py_GIL_DISABLED") else "standard")') && \
    echo "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /etc/devcontainer-build-info && \
    echo "BASE_IMAGE=ubuntu:26.04" >> /etc/devcontainer-build-info && \
    echo "BUILD_TYPE=multi-stage-slim" >> /etc/devcontainer-build-info && \
    echo "BUILD_VERIFY_MODE=${BUILD_VERIFY_MODE}" >> /etc/devcontainer-build-info && \
    echo "LOCALE=zh_CN.UTF-8" >> /etc/devcontainer-build-info && \
    echo "TIMEZONE=Asia/Shanghai" >> /etc/devcontainer-build-info && \
    echo "NON_ROOT_USER=devuser" >> /etc/devcontainer-build-info && \
    echo "NON_ROOT_UID=${DEVUSER_UID}" >> /etc/devcontainer-build-info && \
    echo "SERVICES=sshd,dockerd,podman,jupyter" >> /etc/devcontainer-build-info && \
    echo "SUPERVISOR=enabled" >> /etc/devcontainer-build-info && \
    echo "PYTHON_ENV=conda" >> /etc/devcontainer-build-info && \
    echo "CONDA_DIR=/opt/conda" >> /etc/devcontainer-build-info && \
    echo "CONDA_VERSION=${CONDA_VERSION}" >> /etc/devcontainer-build-info && \
    echo "PYTHON_VERSION=${PYTHON_VERSION_ACTUAL}" >> /etc/devcontainer-build-info && \
    echo "PYTHON_BUILD_TYPE=${PYTHON_BUILD_TYPE}" >> /etc/devcontainer-build-info && \
    echo "DOCKER_DIND=enabled" >> /etc/devcontainer-build-info && \
    echo "PODMAN_ROOTLESS=enabled" >> /etc/devcontainer-build-info && \
    echo "BUILD_TIMER=enabled" >> /etc/devcontainer-build-info && \
    echo "BUILDKIT_CACHE=enabled" >> /etc/devcontainer-build-info && \
    cat /etc/devcontainer-build-info && \
    echo "[BUILD] Build info written to /etc/devcontainer-build-info" && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│ [AGGRESSIVE CLEANUP] Removing unnecessary files│" && \
    echo "└─────────────────────────────────────────────────┘" && \
    echo "[CLEAN 1/9] APT cache + lists..." && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "[CLEAN 2/9] Documentation, man pages, info pages (system + conda)..." && \
    rm -rf /usr/share/doc/* /usr/share/man/* /usr/share/info/* /usr/share/lintian/* 2>/dev/null || true && \
    rm -rf /opt/conda/share/doc/* /opt/conda/share/man/* /opt/conda/share/info/* /opt/conda/share/gtk-doc/* 2>/dev/null || true && \
    echo "[CLEAN 3/9] Python __pycache__ and .pyc/.pyo files..." && \
    find /opt/conda -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find /opt/conda -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true && \
    find /usr -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    echo "[CLEAN 4/9] Conda static libs + non-Python dev headers..." && \
    find /opt/conda/lib -name "*.a" -delete 2>/dev/null || true && \
    find /opt/conda/lib -name "*.la" -delete 2>/dev/null || true && \
    find /opt/conda/include -mindepth 1 -maxdepth 1 ! -name "python*" -exec rm -rf {} + 2>/dev/null || true && \
    echo "[CLEAN 5/9] Stripping debug symbols from binaries..." && \
    find /opt/conda/bin -type f -executable ! -name "*.py" ! -name "*.sh" -exec strip --strip-unneeded {} \; 2>/dev/null || true && \
    find /opt/conda/lib -name "*.so*" ! -path "*/python3.14/site-packages/*" ! -path "*/envs/*/lib/python3.14/site-packages/*" -exec strip --strip-unneeded {} \; 2>/dev/null || true && \
    echo "[CLEAN 6/9] Removing conda telemetry + dev tools (preserving package cache)..." && \
    conda remove -y -n base anaconda-anon-usage --force 2>/dev/null || true && \
    rm -f /opt/conda/bin/x86_64-conda-linux-gnu-ld /opt/conda/bin/x86_64-conda-linux-gnu-ld.bfd 2>/dev/null || true && \
    rm -f /opt/conda/bin/c_rehash /opt/conda/bin/openssl-c_rehash 2>/dev/null || true && \
    conda clean -y -l -q 2>/dev/null || true && \
    echo "[CLEAN 7/9] Conda share bloat (terminfo db, locale unused)..." && \
    rm -rf /opt/conda/share/zoneinfo/leapseconds /opt/conda/share/zoneinfo/tzdata.zi 2>/dev/null || true && \
    for _loc in /opt/conda/share/locale/*; do \
        _bn=$(basename "$_loc"); \
        case "$_bn" in en|en_US|zh|zh_CN|zh_TW|ja) ;; *) rm -rf "$_loc" 2>/dev/null || true ;; esac; \
    done && \
    echo "[CLEAN 8/9] Package caches and tmp files (preserving BuildKit cache mounts)..." && \
    rm -rf /root/.conda/pkgs /tmp/* /var/tmp/* 2>/dev/null || true && \
    echo "  - Preserved BuildKit cache mounts: /root/.cache/pip, /root/.cache/conda, /opt/conda/pkgs" && \
    echo "  - These will be reused on subsequent builds for faster installs" && \
    echo "[CLEAN 9/9] Ensuring /opt/conda permissions..." && \
    chown -R root:root /opt/conda && \
    chmod -R a+rX /opt/conda && \
    find /opt/conda/bin -type f -executable -exec chmod a+x {} \; 2>/dev/null || true && \
    echo "[OK] Aggressive cleanup complete" && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│  [FINAL VERIFICATION - Stage 7/7]               │" && \
    echo "│  Mode: ${BUILD_VERIFY_MODE} (standard/fast/off)         │" && \
    echo "└─────────────────────────────────────────────────┘" && \
    if [ "${BUILD_VERIFY_MODE}" = "off" ]; then \
        echo "[SKIP] Build verification disabled (BUILD_VERIFY_MODE=off)"; \
    elif [ "${BUILD_VERIFY_MODE}" = "fast" ]; then \
        echo "[FAST MODE] Essential checks only..." && \
        python --version && echo "[OK] python available" && \
        python -c "import sysconfig; ft=sysconfig.get_config_var('Py_GIL_DISABLED'); soabi=sysconfig.get_config_var('SOABI'); assert ft==1, f'GIL not disabled: Py_GIL_DISABLED={ft}'; assert 'cpython-314t' in soabi, f'SOABI mismatch: {soabi}'; print(f'[OK] Python free-threading verified (SOABI={soabi})')" && \
        python -c "import brotli,cffi,sqlite3,ssl,zlib,hashlib; print('[OK] Core C extensions load OK')" && \
        conda --version && echo "[OK] conda available" && \
        echo "[FAST MODE] Essential checks passed"; \
    else \
        tini --version >/dev/null 2>&1 && echo "[OK] tini (init) available" && \
        supervisord --version && echo "[OK] supervisord available" && \
        sshd -t && echo "[OK] sshd config valid" && \
        python --version && echo "[OK] python (conda) available" && \
        python -c "import sysconfig; ft=sysconfig.get_config_var('Py_GIL_DISABLED'); assert ft==1, f'Expected free-threading build, got Py_GIL_DISABLED={ft}'; print(f'[OK] Python free-threading build (GIL disabled by default, PYTHON_GIL=1 to enable)')" && \
        echo "[C-EXT] Verifying C extension compatibility..." && \
        python -c "import brotli; d=b'hello'*100; c=brotli.compress(d); assert brotli.decompress(c)==d; print('[OK] brotli C ext (non-ft-safe, GIL warning expected)')" 2>/dev/null && \
        python -c "import cffi; ffi=cffi.FFI(); ffi.cdef('int printf(const char*, ...);'); C=ffi.dlopen(None); print('[OK] cffi C ext')" 2>/dev/null && \
        python -c "import sqlite3; c=sqlite3.connect(':memory:'); c.execute('CREATE TABLE t(id INT)'); c.execute('INSERT INTO t VALUES(1)'); assert c.execute('SELECT * FROM t').fetchone()==(1,); print('[OK] _sqlite3 C ext')" && \
        python -c "import ssl; ctx=ssl.create_default_context(); assert ctx.protocol==ssl.PROTOCOL_TLS_CLIENT; print('[OK] _ssl C ext')" && \
        python -c "import zlib; d=b'test'*50; c=zlib.compress(d); assert zlib.decompress(c)==d; print('[OK] zlib C ext')" && \
        python -c "import hashlib; assert len(hashlib.sha256(b'test').hexdigest())==64; print('[OK] hashlib C ext')" && \
        bash /usr/local/bin/verify-cext.sh -q --expect-soabi cpython-314t >/dev/null 2>&1 && echo "[OK] verify-cext.sh: all C ext checks passed" && \
        conda --version && echo "[OK] conda available" && \
        echo "[MIRROR] Verifying conda system .condarc exists..." && \
        test -f /opt/conda/.condarc && echo "[OK] System .condarc present" && \
        grep -q "conda-forge" /opt/conda/.condarc && echo "[OK] conda-forge channel configured" && \
        echo "[MIRROR] Verifying pip configurations..." && \
        test -f /root/.config/pip/pip.conf && echo "[OK] root pip.conf present" && \
        test -f /home/devuser/.config/pip/pip.conf && echo "[OK] devuser pip.conf present" && \
        su - devuser -c "pip config get global.index-url" && echo "[OK] devuser pip index URL configured" && \
        pip --version && echo "[OK] pip available" && \
        jupyter --version && echo "[OK] jupyter available" && \
        docker --version && echo "[OK] docker available" && \
        podman --version && echo "[OK] podman available" && \
        test ! -d /opt/venv && echo "[OK] /opt/venv removed (using conda only)" && \
        bash -n /usr/local/bin/entrypoint.sh && echo "[OK] entrypoint.sh syntax valid" && \
        bash -n /usr/local/bin/healthcheck.sh && echo "[OK] healthcheck.sh syntax valid" && \
        bash -n /usr/local/bin/verify-cext.sh && echo "[OK] verify-cext.sh syntax valid" && \
        bash -n /usr/local/bin/ft-benchmark.sh && echo "[OK] ft-benchmark.sh syntax valid" && \
        echo "[OK] All standard verification checks passed"; \
    fi && \
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
    echo "║         BUILD TIMING SUMMARY (Runtime Stage)               ║" && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  Stage 1/7  system packages + locale   %5ds               ║\n" $_T1 && \
    printf "║  Stage 2/7  Docker CE install          %5ds               ║\n" $_T2 && \
    printf "║  Stage 3/7  Podman rootless install    %5ds               ║\n" $_T3 && \
    printf "║  Stage 4/7  Miniforge3+libmamba+Pythonft %5ds               ║\n" $_T4 && \
    printf "║  Stage 5/7  user+subuid+dirs+daemon   %5ds               ║\n" $_T5 && \
    printf "║  Stage 6/7  config + validation       %5ds               ║\n" $_T6 && \
    printf "║  Stage 7/7  cleanup + final verify     %5ds               ║\n" $_T7 && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  RUNTIME TOTAL                         %5ds               ║\n" $_TOTAL && \
    echo "╚══════════════════════════════════════════════════════════════╝" && \
    echo "" && \
    rm -f /tmp/.build-timer && \
    echo "[BUILD] ========== BUILD COMPLETE (slim) ==========" && \
    echo ""

# ── 元数据声明（不产生镜像层） ──
WORKDIR /workspace
VOLUME ["/workspace", "/var/lib/docker"]
EXPOSE 22 8888

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD []
