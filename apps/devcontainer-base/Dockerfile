# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - Dockerfile (Multi-stage build)
# Project: SpecWeave Full-featured Development Container Base Image
# Base: ubuntu:26.04 | OpenSSH + Docker DinD + Podman(rootless) + Jupyter
# Locale: zh_CN.UTF-8 / Timezone: Asia/Shanghai
# Non-root user: devuser (UID 1000 if available, auto-assigned otherwise)
# Services: sshd(22) + dockerd(2375) + podman(rootless) + jupyter(8888), managed by supervisord
#
# Build: docker build -t devcontainer-base .
# CN:    docker build --build-arg APT_MIRROR=aliyun --build-arg PIP_MIRROR=aliyun --build-arg DOCKER_MIRROR=aliyun -t devcontainer-base .
# Run:   docker run -d --privileged -p 2222:22 -p 2375:2375 -p 8888:8888 \
#          -e USER_PASSWORD=pass -e JUPYTER_TOKEN=mysecret -e GRANT_SUDO=yes \
#          -v $(pwd)/workspace:/workspace -v docker-data:/var/lib/docker devcontainer-base
# Debug: docker run -it --rm --privileged devcontainer-base bash
#
# Runtime Stage Layering (adapted dockerfile-runtime-logical-layering pattern v1.3):
#   Stage 2.1/7: 系统包 + APT镜像 + locale/timezone (变化频率: 最低)
#   Stage 2.2/7: Docker CE 安装 (变化频率: 低)
#   Stage 2.3/7: Podman rootless 安装 (变化频率: 低)
#   Stage 2.4/7: COPY venv from builder + PATH 配置 (变化频率: 低)
#   Stage 2.5/7: 用户/组 + subuid/subgid + 运行时目录 + daemon.json (变化频率: 中)
#   Stage 2.6/7: 配置文件 COPY + 权限 + 语法验证 (变化频率: 高)
#   Stage 2.7/7: build-info + 清理 + 最终验证 (变化频率: 最低)
#
# Build Timing: 每个Stage结束时输出 [TIMER] 本阶段耗时+累计耗时，最终输出汇总表
# =============================================================================

ARG APT_MIRROR=official
ARG PIP_MIRROR=official

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install Python dependencies with build toolchain
# -----------------------------------------------------------------------------
FROM ubuntu:26.04 AS builder

ARG APT_MIRROR
ARG PIP_MIRROR

ENV DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

RUN echo "=== [Builder] Configuring APT mirror: ${APT_MIRROR} ===" && \
    if [ "${APT_MIRROR}" = "aliyun" ]; then \
        sed -i 's|http://archive.ubuntu.com|http://mirrors.aliyun.com|g; s|http://security.ubuntu.com|http://mirrors.aliyun.com|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || \
        sed -i 's|http://archive.ubuntu.com|http://mirrors.aliyun.com|g; s|http://security.ubuntu.com|http://mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null || true; \
        echo "[Builder] Using Aliyun APT mirror"; \
    elif [ "${APT_MIRROR}" = "tuna" ]; then \
        sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || \
        sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list 2>/dev/null || true; \
        echo "[Builder] Using Tsinghua TUNA APT mirror"; \
    else \
        echo "[Builder] Using official APT sources"; \
    fi

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    echo "=== [Builder] Installing build dependencies ===" && \
    echo "[INFO] Updating APT package lists for builder..." && \
    apt-get update -qq && \
    echo "[INFO] Installing 6 build packages (build-essential, python3-dev, pip, etc.)..." && \
    apt-get install -y --no-install-recommends -qq \
        build-essential \
        ca-certificates \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
    && echo "[OK] Build dependencies installed" && \
    echo "  - python3: $(python3 --version 2>&1 | awk '{print $2}')" && \
    rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    echo "=== [Builder] Creating Python virtual environment ===" && \
    python3 -m venv /opt/venv && \
    echo "[INFO] Virtual environment created at /opt/venv" && \
    if [ "${PIP_MIRROR}" = "aliyun" ]; then \
        /opt/venv/bin/pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
        /opt/venv/bin/pip config set global.trusted-host mirrors.aliyun.com; \
        echo "[Builder] Using Aliyun PyPI mirror"; \
    elif [ "${PIP_MIRROR}" = "tuna" ]; then \
        /opt/venv/bin/pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
        /opt/venv/bin/pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn; \
        echo "[Builder] Using Tsinghua TUNA PyPI mirror"; \
    else \
        echo "[Builder] Using official PyPI"; \
    fi && \
    echo "[INFO] Upgrading pip, setuptools, wheel..." && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    echo "[OK] pip upgraded: $(/opt/venv/bin/pip --version | awk '{print $2}')"

COPY requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    echo "=== [Builder] Installing Jupyter and Python packages ===" && \
    echo "[INFO] Installing packages from requirements.txt..." && \
    echo "[INFO] Package list:" && cat /tmp/requirements.txt | sed 's/^/  - /' && \
    /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt && \
    echo "[OK] Python packages installed, verifying jupyter..." && \
    /opt/venv/bin/jupyter --version && \
    echo "[INFO] Key pip packages:" && \
    /opt/venv/bin/pip list --format=columns 2>/dev/null | grep -iE 'jupyter|notebook|ipykernel|docker|podman|supervisor' || true

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Minimal production image
# -----------------------------------------------------------------------------
FROM ubuntu:26.04

ARG APT_MIRROR
ARG DOCKER_MIRROR=official

LABEL maintainer="SpecWeave"
LABEL description="Full-featured Ubuntu 26.04 dev container with SSH + Docker DinD + Podman(rootless) + Jupyter, managed by supervisord"
LABEL version="1.3"

# ── 元数据层：环境变量声明（不产生层，仅元数据） ──
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai \
    LANG=zh_CN.UTF-8 \
    LANGUAGE=zh_CN:zh \
    LC_ALL=zh_CN.UTF-8 \
    PATH="/opt/venv/bin:${PATH}" \
    VIRTUAL_ENV="/opt/venv" \
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
    echo "[INFO] Installing 21 system packages (openssh-server, python3, supervisor, uidmap, etc.)..." && \
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
        python3 \
        python3-venv \
        sudo \
        supervisor \
        tini \
        tzdata \
        vim \
        wget \
        xz-utils \
        uidmap \
        fuse-overlayfs \
        slirp4netns \
    && echo "[OK] Base system packages installed" && \
    echo "[INFO] Verifying key package versions:" && \
    echo "  - openssh-server: $(dpkg-query -W -f='${Version}' openssh-server 2>/dev/null || echo 'N/A')" && \
    echo "  - python3: $(python3 --version 2>&1 | awk '{print $2}')" && \
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
# Stage 2.4/7: 语言运行时复制（从 builder 阶段 COPY venv）
# 变化频率：低（依赖版本升级时改）
# 原则：COPY --from=builder 后立即验证二进制可用，配置 profile.d
# ═══════════════════════════════════════════════════════════════════
COPY --from=builder /opt/venv /opt/venv

RUN echo "=== Stage 4/7: Copy Python venv from builder ===" && \
    _STAGE_START=$(date +%s) && \
    python3 --version && \
    pip --version && \
    jupyter --version && \
    echo "[BUILD] Jupyter available via venv at /opt/venv" && \
    echo "export PATH=/opt/venv/bin:\$PATH" > /etc/profile.d/venv.sh && \
    echo "export VIRTUAL_ENV=/opt/venv" >> /etc/profile.d/venv.sh && \
    chmod +x /etc/profile.d/venv.sh && \
    echo "[BUILD] System-wide profile.d/venv.sh created for login shell PATH" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S4=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 4/7 (venv+PATH) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

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
    echo "export PATH=/opt/venv/bin:\$PATH" >> /home/devuser/.bashrc && \
    echo "export VIRTUAL_ENV=/opt/venv" >> /home/devuser/.bashrc && \
    chown devuser:devuser /home/devuser/.bashrc && \
    echo "PATH=/opt/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >> /etc/environment && \
    echo "[BUILD] User .bashrc and /etc/environment configured with venv PATH (PATH layer 2+3)" && \
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
#       （sshd -t、bash -n 等），构建即测试，问题早发现
# ═══════════════════════════════════════════════════════════════════
COPY config/sshd_config /etc/ssh/sshd_config
COPY config/supervisord.conf /etc/supervisor/supervisord.conf
COPY config/supervisor/conf.d/ /etc/supervisor/conf.d/
COPY config/jupyter_notebook_config.py /home/devuser/.jupyter/jupyter_notebook_config.py
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY scripts/healthcheck.sh /usr/local/bin/healthcheck.sh

RUN echo "=== Stage 6/7: Config permissions + syntax validation ===" && \
    _STAGE_START=$(date +%s) && \
    chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/healthcheck.sh && \
    chown -R devuser:devuser /home/devuser/.jupyter && \
    chown -R devuser:devuser /workspace && \
    echo "[BUILD] Permissions set: entrypoint.sh and healthcheck.sh executable" && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│  [VALIDATION CHECKPOINT - Stage 6/7]            │" && \
    echo "│  Running syntax validation for all configs      │" && \
    echo "└─────────────────────────────────────────────────┘" && \
    echo "[VALIDATE 1/3] sshd -t (SSH daemon config syntax)..." && \
    sshd -t && echo "[OK] sshd_config syntax valid" && \
    echo "[VALIDATE 2/3] bash -n entrypoint.sh..." && \
    bash -n /usr/local/bin/entrypoint.sh && echo "[OK] entrypoint.sh bash syntax valid" && \
    echo "[VALIDATE 3/3] bash -n healthcheck.sh..." && \
    bash -n /usr/local/bin/healthcheck.sh && echo "[OK] healthcheck.sh bash syntax valid" && \
    echo "" && \
    echo "[BUILD] All 3 syntax validation checks passed" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S6=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 6/7 (config+validation) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 2.7/7: 构建元数据 + 最终清理 + 最终可用性验证
# 变化频率：最低（版本发布时改）
# 原则：写入build-info；清理apt/tmp缓存；最终验证所有关键命令可执行；
#       输出耗时汇总表；删除计时器文件
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== Stage 7/7: Final metadata, cleanup, and verification ===" && \
    _STAGE_START=$(date +%s) && \
    DEVUSER_UID=$(id -u devuser) && \
    echo "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /etc/devcontainer-build-info && \
    echo "BASE_IMAGE=ubuntu:26.04" >> /etc/devcontainer-build-info && \
    echo "BUILD_TYPE=multi-stage" >> /etc/devcontainer-build-info && \
    echo "LOCALE=zh_CN.UTF-8" >> /etc/devcontainer-build-info && \
    echo "TIMEZONE=Asia/Shanghai" >> /etc/devcontainer-build-info && \
    echo "NON_ROOT_USER=devuser" >> /etc/devcontainer-build-info && \
    echo "NON_ROOT_UID=${DEVUSER_UID}" >> /etc/devcontainer-build-info && \
    echo "SERVICES=sshd,dockerd,podman,jupyter" >> /etc/devcontainer-build-info && \
    echo "SUPERVISOR=enabled" >> /etc/devcontainer-build-info && \
    echo "PYTHON_VENV=/opt/venv" >> /etc/devcontainer-build-info && \
    echo "DOCKER_DIND=enabled" >> /etc/devcontainer-build-info && \
    echo "PODMAN_ROOTLESS=enabled" >> /etc/devcontainer-build-info && \
    echo "PATH_LAYERS=4(docker-env+etc-environment+profile.d+supervisor)" >> /etc/devcontainer-build-info && \
    echo "BUILD_TIMER=enabled" >> /etc/devcontainer-build-info && \
    cat /etc/devcontainer-build-info && \
    echo "[BUILD] Build info written to /etc/devcontainer-build-info" && \
    echo "[BUILD] Running final cleanup..." && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "[BUILD] APT cache cleaned" && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│  [FINAL VERIFICATION - Stage 7/7]               │" && \
    echo "│  Verifying all critical binaries are runnable   │" && \
    echo "└─────────────────────────────────────────────────┘" && \
    tini --version >/dev/null 2>&1 && echo "[OK] tini (init) available" && \
    supervisord --version && echo "[OK] supervisord available" && \
    sshd -t && echo "[OK] sshd config valid" && \
    python --version && echo "[OK] python available" && \
    pip --version && echo "[OK] pip available" && \
    jupyter --version && echo "[OK] jupyter available" && \
    docker --version && echo "[OK] docker available" && \
    podman --version && echo "[OK] podman available" && \
    bash -n /usr/local/bin/entrypoint.sh && echo "[OK] entrypoint.sh syntax valid" && \
    bash -n /usr/local/bin/healthcheck.sh && echo "[OK] healthcheck.sh syntax valid" && \
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
    printf "║  Stage 4/7  venv copy + PATH config    %5ds               ║\n" $_T4 && \
    printf "║  Stage 5/7  user+subuid+dirs+daemon   %5ds               ║\n" $_T5 && \
    printf "║  Stage 6/7  config + validation       %5ds               ║\n" $_T6 && \
    printf "║  Stage 7/7  metadata + final verify    %5ds               ║\n" $_T7 && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  RUNTIME TOTAL                         %5ds               ║\n" $_TOTAL && \
    echo "╚══════════════════════════════════════════════════════════════╝" && \
    echo "" && \
    rm -f /tmp/.build-timer /tmp/* /var/tmp/* && \
    echo "[BUILD] ========== BUILD COMPLETE ==========" && \
    echo ""

# ── 元数据声明（不产生镜像层） ──
WORKDIR /workspace
VOLUME ["/workspace", "/var/lib/docker"]
EXPOSE 22 8888

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD []
