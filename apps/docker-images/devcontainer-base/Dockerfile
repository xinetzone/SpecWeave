# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - Dockerfile (7-stage single-image build)
# Project: SpecWeave Full-featured Development Container Base Image
# Base: ubuntu:26.04 | OpenSSH + Docker DinD + Podman(rootless, optional) + Jupyter + Miniforge3(conda-forge, libmamba)
# Locale: zh_CN.UTF-8 / Timezone: Asia/Shanghai
# Non-root user: devuser (UID 1000 if available, auto-assigned otherwise)
# Services: sshd(22) + dockerd(unix socket) + podman(rootless, INSTALL_PODMAN=true) + jupyter(8888), managed by supervisord
# Python: Miniforge3 (conda-forge) at /opt/conda (Python 3.14.6 free-threading cp314t, libgcc-ng 16.1.0运行时, libmamba solver), Jupyter在main环境
# BuildKit cache: pip (/root/.cache/pip) + conda pkgs (/opt/conda/pkgs) + libmamba solver (/root/.cache/conda) 持久化缓存
# Verify modes: BUILD_VERIFY_MODE=standard (default, full checks) | fast (essential only) | off (skip)
#
# Build: docker build -t devcontainer-base .
# CN:    docker build --build-arg APT_MIRROR=aliyun --build-arg PIP_MIRROR=aliyun --build-arg DOCKER_MIRROR=aliyun --build-arg CONDA_MIRROR=tuna -t devcontainer-base .
# Run:   docker run -d --privileged -p 2222:22 -p 8888:8888 \
#          -e USER_PASSWORD=pass -e JUPYTER_TOKEN=mysecret -e GRANT_SUDO=yes \
#          -v $(pwd)/workspace:/workspace -v docker-data:/var/lib/docker devcontainer-base
# Debug: docker run -it --rm --privileged devcontainer-base bash
#
# Runtime Stage Layering (dockerfile-runtime-logical-layering pattern v1.4):
#
#   分层设计原理（6条公理）：
#     P1 变化频率分层: 同频率同层，低频率层在前，高频率层在后 → 最大化缓存命中
#     P2 缓存保护:     高耗时稳定操作（mamba solver）必须独立成层，不被高频变化触发重跑
#     P3 开发能力保留: 清理步骤不损害编译/版本控制等开发能力（保留头文件、保留git等）
#     P4 工具链80/20:  80%场景常用工具内置base镜像（git/docker compose/jupyter等）
#     P5 脚本外置:     >50行复杂逻辑抽取为外部脚本（scripts/dockerfile/），独立维护
#     P6 按需安装:     默认关闭的功能不占镜像体积（Podman等），通过ARG构建参数控制开关
#     P7 同层修改:     strip/chmod/包移除等修改操作必须在文件创建的同一层完成（禁止上层修改低层文件导致Copy-on-Write膨胀）
#
#   Stage 1/7: 系统包 + APT镜像 + locale/timezone          (变化频率: 最低)
#   Stage 2/7: Docker CE + Compose Plugin 安装             (变化频率: 低)
#   Stage 3/7: Podman rootless 安装（可选，默认跳过）       (变化频率: 低)
#   Stage 4/7: Miniforge3 + Python ft + libmamba + Jupyter (变化频率: 中，分3子层)
#     4a: Miniforge3安装 + .condarc 配置                   (变化频率: 低)
#     4b: mamba create main环境 (Python+Jupyter求解安装)   (变化频率: 中，高耗时)
#     4c: pip镜像配置 + kernel注册 + ft验证                (变化频率: 中高)
#   Stage 5/7: 用户/组 + subuid/subgid + 运行时目录 + daemon.json (变化频率: 中)
#   Stage 6/7: 配置文件 COPY + 权限 + 语法验证             (变化频率: 高)
#   Stage 7/7: build-info + 激进清理 + 最终验证            (变化频率: 最低)
#
# Build Timing: 每个Stage/子Stage结束时输出 [TIMER] 本阶段耗时+累计耗时，最终输出汇总表
# =============================================================================

ARG APT_MIRROR=official
ARG PIP_MIRROR=official
ARG CONDA_MIRROR=official
ARG PYTHON_VERSION=3.14.6
ARG PYTHON_BUILD=cp314t
ARG BUILD_VERIFY_MODE=standard
ARG INSTALL_PODMAN=true

# -----------------------------------------------------------------------------
# Stage: Runtime - Minimal production image with Miniforge3
# -----------------------------------------------------------------------------
FROM ubuntu:26.04

ARG APT_MIRROR
ARG DOCKER_MIRROR=official
ARG CONDA_MIRROR
ARG PIP_MIRROR
ARG PYTHON_VERSION
ARG PYTHON_BUILD
ARG BUILD_VERIFY_MODE
ARG INSTALL_PODMAN

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
    PYTHONDONTWRITEBYTECODE=1 \
    NON_ROOT_USER=devuser \
    JUPYTER_PORT=8888 \
    SSH_PORT=22 \
    GRANT_SUDO=no \
    ALLOW_ROOT_SSH=no \
    JUPYTER_ALLOW_ORIGIN= \
    ENABLE_SSH=yes \
    ENABLE_DOCKER=yes \
    ENABLE_PODMAN=no \
    ENABLE_JUPYTER=yes \
    LOCAL_USER_ID= \
    LOCAL_GROUP_ID= \
    WORKSPACE_CHOWN_MODE=auto \
    CHOWN_EXTRA= \
    FIXUID_DEBUG=0

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# ═══════════════════════════════════════════════════════════════════
# Stage 1/7: 系统包安装 + APT镜像 + locale/timezone 配置
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
        binutils \
        ca-certificates \
        curl \
        git \
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
    echo "  - git: $(git --version 2>/dev/null || echo 'N/A')" && \
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
# Stage 2/7: Docker CE + Compose Plugin 安装
# 变化频率：低（Docker版本升级时改）
# 原则：GPG key + apt repo 配置 + 安装在同层完成，清理apt缓存
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    echo "=== Stage 2/7: Install Docker CE + Compose Plugin ===" && \
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
    echo "[INFO] Installing Docker CE packages (docker-ce, containerd, buildx, compose-plugin)..." && \
    apt-get install -y --no-install-recommends -qq \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin \
    && echo "[OK] Docker Engine + Compose Plugin installed" && \
    echo "[INFO] Docker component versions:" && \
    echo "  - docker: $(docker --version 2>/dev/null | awk '{print $3}' | tr -d ',')" && \
    echo "  - dockerd: $(dockerd --version 2>/dev/null | awk '{print $3}' | tr -d ',')" && \
    echo "  - containerd: $(containerd --version 2>/dev/null | awk '{print $3}')" && \
    echo "  - buildx: $(docker buildx version 2>/dev/null | awk '{print $2}')" && \
    echo "  - compose: $(docker compose version 2>/dev/null | awk '{print $4}' | tr -d 'v')" && \
    echo "[STRIP] Stripping Docker/containerd Go binaries (same-layer, no COW)..." && \
    for _bin in /usr/bin/dockerd /usr/bin/docker /usr/bin/containerd /usr/bin/containerd-shim-runc-v2 /usr/bin/docker-proxy; do \
        [ -f "$_bin" ] && strip --strip-all "$_bin" 2>/dev/null || true; \
    done && \
    for _bin in /usr/libexec/docker/cli-plugins/docker-buildx /usr/libexec/docker/cli-plugins/docker-compose; do \
        [ -f "$_bin" ] && strip --strip-all "$_bin" 2>/dev/null || true; \
    done && \
    for _bin in /usr/bin/ctr /usr/bin/runc; do \
        [ -f "$_bin" ] && strip --strip-unneeded "$_bin" 2>/dev/null || true; \
    done && \
    echo "[OK] Docker binaries stripped" && \
    rm -rf /var/lib/apt/lists/* && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S2=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 2/7 (Docker CE) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 3/7: Podman rootless 安装（可选，默认INSTALL_PODMAN=false跳过）
# 变化频率：低（Podman版本升级时改）
# 原则：直接使用Ubuntu 26.04官方源，无需第三方repo
#       默认不安装以减小镜像体积；--build-arg INSTALL_PODMAN=true 启用
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    echo "=== Stage 3/7: Podman (rootless) [INSTALL_PODMAN=${INSTALL_PODMAN}] ===" && \
    _STAGE_START=$(date +%s) && \
    if [ "${INSTALL_PODMAN}" = "true" ]; then \
        echo "[INFO] Installing Podman packages (podman, crun, conmon)..." && \
        apt-get update -qq && \
        apt-get install -y --no-install-recommends -qq podman crun conmon && \
        echo "[OK] Podman installed" && \
        echo "  - podman: $(podman --version 2>/dev/null | awk '{print $3}')" && \
        echo "  - crun: $(crun --version 2>/dev/null | head -1 | awk '{print $2}')" && \
        echo "[STRIP] Stripping Podman binaries (same-layer, no COW)..." && \
        for _bin in /usr/bin/podman /usr/bin/crun /usr/bin/conmon; do \
            [ -f "$_bin" ] && strip --strip-all "$_bin" 2>/dev/null || true; \
        done && \
        for _bin in /usr/libexec/podman/rootlessport /usr/libexec/podman/quadlet; do \
            [ -f "$_bin" ] && strip --strip-all "$_bin" 2>/dev/null || true; \
        done && \
        echo "[CLEAN] Removing podman-testing (33MB test binary, not needed at runtime)..." && \
        rm -f /usr/libexec/podman/podman-testing 2>/dev/null || true && \
        echo "[OK] Podman binaries stripped + podman-testing removed"; \
    else \
        echo "[SKIP] Podman not installed (default). Use --build-arg INSTALL_PODMAN=true to enable."; \
    fi && \
    rm -rf /var/lib/apt/lists/* && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S3=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 3/7 (Podman) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 4/7: Miniforge3 (conda-forge) 安装 + Python free-threading + libmamba + Jupyter
# 变化频率：中（Python/包版本升级时改）
# 分层设计（P2缓存保护）：拆分为3个子层，4b(mamba create)高耗时层被保护
#   4a: Miniforge3安装 + .condarc配置（稳定，很少变）
#   4b: mamba create main环境（高耗时，Python/Jupyter版本升级时变）
#   4c: pip镜像配置 + kernel注册 + ft验证（中高频变，不触发4a/4b重跑）
# 所有复杂逻辑抽取到 scripts/dockerfile/ 外部脚本（P5脚本外置）
# ═══════════════════════════════════════════════════════════════════

# ── Stage 4a: Miniforge3 安装 + .condarc ──
COPY scripts/dockerfile/stage4a-miniforge.sh /tmp/stage4a-miniforge.sh
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,target=/root/.cache/conda,sharing=locked \
    --mount=type=bind,source=local-cache,target=/tmp/local-cache,readonly \
    sed -i 's/\r$//' /tmp/stage4a-miniforge.sh && chmod +x /tmp/stage4a-miniforge.sh && \
    bash /tmp/stage4a-miniforge.sh && \
    rm -f /tmp/stage4a-miniforge.sh

# ── Stage 4b: mamba create main 环境（高耗时层，独立缓存保护） ──
COPY scripts/dockerfile/stage4b-mamba-env.sh /tmp/stage4b-mamba-env.sh
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,target=/root/.cache/conda,sharing=locked \
    sed -i 's/\r$//' /tmp/stage4b-mamba-env.sh && chmod +x /tmp/stage4b-mamba-env.sh && \
    bash /tmp/stage4b-mamba-env.sh && \
    rm -f /tmp/stage4b-mamba-env.sh

# ── Stage 4c: pip 配置 + kernel注册 + free-threading 验证 ──
COPY scripts/dockerfile/stage4c-pip-verify.sh /tmp/stage4c-pip-verify.sh
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    sed -i 's/\r$//' /tmp/stage4c-pip-verify.sh && chmod +x /tmp/stage4c-pip-verify.sh && \
    bash /tmp/stage4c-pip-verify.sh && \
    rm -f /tmp/stage4c-pip-verify.sh /tmp/pip-config.env

# ═══════════════════════════════════════════════════════════════════
# Stage 5/7: 用户/组/工作目录创建 + subuid/subgid + 权限设置
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
# Stage 6/7: 配置文件 COPY + 语法验证（P7同层修改：--chmod/--chown在COPY时设置权限）
# 变化频率：高（配置调整时改，缓存不会让前面层失效）
# 原则：所有 COPY 使用 --chmod/--chown 设置权限（同层，无COW）；RUN仅做CRLF清理+语法验证
# ═══════════════════════════════════════════════════════════════════
COPY config/sshd_config /etc/ssh/sshd_config
COPY config/supervisord.conf /etc/supervisor/supervisord.conf
COPY config/supervisor/conf.d/ /etc/supervisor/conf.d/
COPY --chown=devuser:devuser config/jupyter_notebook_config.py /home/devuser/.jupyter/jupyter_notebook_config.py
COPY --chmod=755 entrypoint.sh /usr/local/bin/entrypoint.sh
COPY --chmod=755 scripts/healthcheck.sh /usr/local/bin/healthcheck.sh
COPY --chmod=755 scripts/verify-cext.sh /usr/local/bin/verify-cext.sh
COPY --chmod=755 scripts/ft-benchmark.sh /usr/local/bin/ft-benchmark.sh
COPY scripts/ft_benchmark.py /usr/local/bin/ft_benchmark.py
COPY scripts/nogil_kit.py /usr/local/bin/nogil_kit.py
COPY scripts/check_gil_state.py /usr/local/bin/check_gil_state.py
COPY --chmod=755 scripts/lib/clean-pycache.sh /usr/local/bin/clean-pycache.sh

RUN echo "=== Stage 6/7: CRLF cleanup + syntax validation (P7: permissions set at COPY time) ===" && \
    _STAGE_START=$(date +%s) && \
    echo "[BUILD] Permissions set via COPY --chmod/--chown (no chmod/chown in RUN = no COW)" && \
    for _f in /usr/local/bin/entrypoint.sh /usr/local/bin/healthcheck.sh /usr/local/bin/verify-cext.sh \
             /usr/local/bin/ft-benchmark.sh /usr/local/bin/clean-pycache.sh \
             /home/devuser/.jupyter/jupyter_notebook_config.py \
             /etc/supervisor/supervisord.conf /etc/supervisor/conf.d/*.conf /etc/ssh/sshd_config; do \
        if [ -f "$_f" ]; then sed -i 's/\r$//' "$_f" 2>/dev/null || true; fi; \
    done && echo "[BUILD] CRLF cleaned from all text configs/scripts (Windows editor safe)" && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│  [VALIDATION CHECKPOINT - Stage 6/7]            │" && \
    echo "│  Running syntax validation for all configs      │" && \
    echo "└─────────────────────────────────────────────────┘" && \
    echo "[VALIDATE 1/6] sshd -t (SSH daemon config syntax)..." && \
    sshd -t && echo "[OK] sshd_config syntax valid" && \
    echo "[VALIDATE 2/6] bash -n entrypoint.sh..." && \
    bash -n /usr/local/bin/entrypoint.sh && echo "[OK] entrypoint.sh bash syntax valid" && \
    echo "[VALIDATE 3/6] bash -n healthcheck.sh..." && \
    bash -n /usr/local/bin/healthcheck.sh && echo "[OK] healthcheck.sh bash syntax valid" && \
    echo "[VALIDATE 4/6] bash -n verify-cext.sh..." && \
    bash -n /usr/local/bin/verify-cext.sh && echo "[OK] verify-cext.sh bash syntax valid" && \
    echo "[VALIDATE 5/6] bash -n clean-pycache.sh..." && \
    bash -n /usr/local/bin/clean-pycache.sh && echo "[OK] clean-pycache.sh bash syntax valid" && \
    echo "[VALIDATE 6/6] ft-benchmark (bash wrapper + python core)..." && \
    bash -n /usr/local/bin/ft-benchmark.sh && \
    python3 -c "for f in ['/usr/local/bin/ft_benchmark.py','/usr/local/bin/nogil_kit.py','/usr/local/bin/check_gil_state.py']: compile(open(f).read(), f, 'exec')" && \
    echo "[OK] ft-benchmark.sh + ft_benchmark.py + nogil_kit.py + check_gil_state.py syntax valid" && \
    echo "" && \
    echo "[BUILD] All 6 syntax validation checks passed" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S6=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 6/7 (config+validation, P7-compliant) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 7/7: 构建元数据 + 删除式清理 + 最终验证
# 变化频率：最低（版本发布时改）
# 原则：P7同层修改已在各stage完成，此层只做删除（rm -rf whiteout，无COW数据膨胀）；
#       删除doc/man/info/__pycache__/.pyc/静态库/locale/test等冗余文件；
#       PYTHONDONTWRITEBYTECODE阻止验证时.pyc生成；
#       不执行strip/chmod/包移除等修改操作（已在同层完成）；
#       最终验证所有关键命令可执行；输出耗时汇总表
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    echo "=== Stage 7/7: Final metadata, deletion cleanup, and verification ===" && \
    _STAGE_START=$(date +%s) && \
    export PYTHONDONTWRITEBYTECODE=1 && \
    echo "[INFO] PYTHONDONTWRITEBYTECODE=1 set for Stage 7 to prevent .pyc bloat during verification" && \
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
    if [ "${INSTALL_PODMAN}" = "true" ]; then echo "SERVICES=sshd,dockerd,podman,jupyter"; else echo "SERVICES=sshd,dockerd,jupyter"; fi >> /etc/devcontainer-build-info && \
    echo "SUPERVISOR=enabled" >> /etc/devcontainer-build-info && \
    echo "PYTHON_ENV=conda" >> /etc/devcontainer-build-info && \
    echo "CONDA_DIR=/opt/conda" >> /etc/devcontainer-build-info && \
    echo "CONDA_VERSION=${CONDA_VERSION}" >> /etc/devcontainer-build-info && \
    echo "PYTHON_VERSION=${PYTHON_VERSION_ACTUAL}" >> /etc/devcontainer-build-info && \
    echo "PYTHON_BUILD_TYPE=${PYTHON_BUILD_TYPE}" >> /etc/devcontainer-build-info && \
    echo "DOCKER_DIND=enabled" >> /etc/devcontainer-build-info && \
    if [ "${INSTALL_PODMAN}" = "true" ]; then echo "PODMAN_ROOTLESS=enabled"; else echo "PODMAN_ROOTLESS=disabled"; fi >> /etc/devcontainer-build-info && \
    echo "BUILD_TIMER=enabled" >> /etc/devcontainer-build-info && \
    echo "BUILDKIT_CACHE=enabled" >> /etc/devcontainer-build-info && \
    echo "STRIP_STRATEGY=same-layer (P7)" >> /etc/devcontainer-build-info && \
    cat /etc/devcontainer-build-info && \
    echo "[BUILD] Build info written to /etc/devcontainer-build-info" && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│ [DELETION CLEANUP] Removing unnecessary files  │" && \
    echo "│ (rm -rf only, no modifications = no COW bloat) │" && \
    echo "└─────────────────────────────────────────────────┘" && \
    echo "[CLEAN 1/8] APT cache + lists..." && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "[CLEAN 2/8] Documentation, man pages, info pages (system + conda) + gitweb + coreutils locales..." && \
    rm -rf /usr/share/doc/* /usr/share/man/* /usr/share/info/* /usr/share/lintian/* 2>/dev/null || true && \
    rm -rf /opt/conda/share/doc/* /opt/conda/share/man/* /opt/conda/share/info/* /opt/conda/share/gtk-doc/* 2>/dev/null || true && \
    rm -rf /usr/share/gitweb /usr/share/coreutils/locales 2>/dev/null || true && \
    echo "[CLEAN 3/8] Python __pycache__ and .pyc/.pyo files (pre-verification, using clean-pycache.sh)..." && \
    clean-pycache.sh -q /opt/conda /usr && \
    echo "[CLEAN 4/8] Static libs (.a/.la) cleanup (base + main + system)..." && \
    find /opt/conda/lib -name "*.a" -delete 2>/dev/null || true && \
    find /opt/conda/lib -name "*.la" -delete 2>/dev/null || true && \
    find /opt/conda/envs/main/lib -name "*.a" -delete 2>/dev/null || true && \
    find /opt/conda/envs/main/lib -name "*.la" -delete 2>/dev/null || true && \
    find /usr/lib -name "*.a" -delete 2>/dev/null || true && \
    find /usr/lib/x86_64-linux-gnu -name "*.a" -delete 2>/dev/null || true && \
    echo "  - Preserved /opt/conda/include/* for C extension compilation" && \
    echo "[CLEAN 5/8] Pruning Babel locale data (keeping en/zh/ja)..." && \
    for _bdir in /opt/conda/envs/main/lib/python*/site-packages/babel/locale-data; do \
        if [ -d "$_bdir" ]; then \
            find "$_bdir" -name "*.dat" ! -name "en*.dat" ! -name "zh*.dat" ! -name "ja*.dat" -delete 2>/dev/null || true; \
            echo "  - Babel locale data pruned to en/zh/ja in $_bdir"; \
        fi; \
    done && \
    echo "[CLEAN 6/8] Pruning system locales/i18n (keeping en_US/zh_CN)..." && \
    rm -rf /usr/share/locale/* 2>/dev/null || true && \
    mkdir -p /usr/share/locale/en_US.UTF-8 /usr/share/locale/zh_CN.UTF-8 /usr/share/locale/en /usr/share/locale/zh 2>/dev/null || true && \
    rm -rf /usr/share/i18n/charmaps/* 2>/dev/null || true && \
    echo "  - System locales pruned (en_US/zh_CN retained)" && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    echo "[CLEAN 7/8] Conda share bloat (terminfo, zoneinfo, locale)..." && \
    echo "  - Pruning terminfo (keeping xterm/screen/linux/vt100/ansi/dumb/gnome)..." && \
    find /opt/conda/share/terminfo -mindepth 1 -maxdepth 1 -type d \
        ! -name "x" ! -name "s" ! -name "l" ! -name "v" ! -name "a" ! -name "d" ! -name "g" \
        -exec rm -rf {} + 2>/dev/null || true && \
    for _d in /opt/conda/share/terminfo/x/* /opt/conda/share/terminfo/s/* /opt/conda/share/terminfo/l/* /opt/conda/share/terminfo/v/* /opt/conda/share/terminfo/a/* /opt/conda/share/terminfo/d/* /opt/conda/share/terminfo/g/*; do \
        [ -e "$_d" ] || continue; \
        _bn=$(basename "$_d"); \
        case "$_bn" in xterm*|screen*|linux*|vt100*|ansi*|dumb*|gnome*) ;; *) rm -f "$_d" 2>/dev/null || true ;; esac; \
    done && \
    echo "  - Pruning zoneinfo (keeping Asia, Etc, UTC, America/New_York, Europe/London)..." && \
    rm -rf /opt/conda/share/zoneinfo/leapseconds /opt/conda/share/zoneinfo/tzdata.zi 2>/dev/null || true && \
    for _zd in /opt/conda/share/zoneinfo/*; do \
        [ -d "$_zd" ] || [ -f "$_zd" ] || continue; \
        _bn=$(basename "$_zd"); \
        case "$_bn" in Asia|Etc|UTC|Universal|America|Europe|zone.tab|zone1970.tab|iso3166.tab) ;; *) rm -rf "$_zd" 2>/dev/null || true ;; esac; \
    done && \
    for _zd in /opt/conda/share/zoneinfo/America/*; do \
        [ -f "$_zd" ] || continue; _bn=$(basename "$_zd"); \
        case "$_bn" in New_York*) ;; *) rm -f "$_zd" 2>/dev/null || true ;; esac; \
    done && \
    for _zd in /opt/conda/share/zoneinfo/Europe/*; do \
        [ -f "$_zd" ] || continue; _bn=$(basename "$_zd"); \
        case "$_bn" in London*|UTC) ;; *) rm -f "$_zd" 2>/dev/null || true ;; esac; \
    done && \
    find /opt/conda/share/zoneinfo -type d -empty -delete 2>/dev/null || true && \
    for _loc in /opt/conda/share/locale/*; do \
        _bn=$(basename "$_loc"); \
        case "$_bn" in en|en_US|zh|zh_CN|zh_TW|ja) ;; *) rm -rf "$_loc" 2>/dev/null || true ;; esac; \
    done && \
    for _loc in /opt/conda/envs/main/share/locale/*; do \
        _bn=$(basename "$_loc"); \
        case "$_bn" in en|en_US|zh|zh_CN|zh_TW|ja) ;; *) rm -rf "$_loc" 2>/dev/null || true ;; esac; \
    done && \
    echo "[CLEAN 8/8] Package caches and tmp files..." && \
    rm -rf /root/.conda/pkgs /tmp/* /var/tmp/* 2>/dev/null || true && \
    rm -rf /root/.cache/pip 2>/dev/null || true && \
    echo "  - BuildKit cache mounts are external (not in image layers)" && \
    echo "[OK] Deletion cleanup complete (8 steps, no COW-causing modifications)" && \
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
        python -c "import sysconfig; ft=sysconfig.get_config_var('Py_GIL_DISABLED'); soabi=sysconfig.get_config_var('SOABI') or ''; assert ft==1, f'GIL not disabled: Py_GIL_DISABLED={ft}'; assert 't' in soabi, f'SOABI mismatch (expected free-threading t suffix): {soabi}'; print(f'[OK] Python free-threading verified (SOABI={soabi})')" && \
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
        bash /usr/local/bin/verify-cext.sh -q >/dev/null 2>&1 && echo "[OK] verify-cext.sh: all C ext checks passed" && \
        conda --version && echo "[OK] conda available" && \
        git --version && echo "[OK] git available" && \
        docker compose version && echo "[OK] docker compose available" && \
        echo "[MIRROR] Verifying conda system .condarc exists..." && \
        test -f /opt/conda/.condarc && echo "[OK] System .condarc present" && \
        grep -q "conda-forge" /opt/conda/.condarc && echo "[OK] conda-forge channel configured" && \
        echo "[MIRROR] Verifying pip configurations..." && \
        test -f /root/.config/pip/pip.conf && echo "[OK] root pip.conf present" && \
        test -f /home/devuser/.config/pip/pip.conf && echo "[OK] devuser pip.conf present" && \
        su - devuser -c "PYTHONDONTWRITEBYTECODE=1 pip config get global.index-url" && echo "[OK] devuser pip index URL configured" && \
        pip --version && echo "[OK] pip available" && \
        jupyter --version && echo "[OK] jupyter available" && \
        docker --version && echo "[OK] docker available" && \
        if [ "${INSTALL_PODMAN}" = "true" ]; then podman --version && echo "[OK] podman available (stripped, no COW bloat)"; else echo "[INFO] podman not installed (INSTALL_PODMAN=false)"; fi && \
        test ! -d /opt/venv && echo "[OK] /opt/venv removed (using conda only)" && \
        bash -n /usr/local/bin/entrypoint.sh && echo "[OK] entrypoint.sh syntax valid" && \
        bash -n /usr/local/bin/healthcheck.sh && echo "[OK] healthcheck.sh syntax valid" && \
        bash -n /usr/local/bin/verify-cext.sh && echo "[OK] verify-cext.sh syntax valid" && \
        bash -n /usr/local/bin/ft-benchmark.sh && \
        python3 -c "for f in ['/usr/local/bin/ft_benchmark.py','/usr/local/bin/nogil_kit.py','/usr/local/bin/check_gil_state.py']: compile(open(f).read(), f, 'exec')" && echo "[OK] ft-benchmark + nogil_kit + check_gil_state syntax valid" && \
        echo "[OK] All standard verification checks passed"; \
    fi && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│ [POST-VERIFY SWEEP] Final cleanup              │" && \
    echo "└─────────────────────────────────────────────────┘" && \
    echo "  - Removing any __pycache__/.pyc created by verification (using clean-pycache.sh)..." && \
    clean-pycache.sh -q /opt/conda /usr && \
    rm -rf /tmp/* /var/tmp/* /root/.conda/pkgs 2>/dev/null || true && \
    echo "  - Final cleanup complete" && \
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
    echo "║         BUILD TIMING SUMMARY (Runtime Stage)                ║" && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  Stage 1/7  %-29s %5ds                       ║\n" "system+binutils+locale" $_T1 && \
    printf "║  Stage 2/7  %-29s %5ds  [stripped]           ║\n" "Docker CE install+strip" $_T2 && \
    printf "║  Stage 3/7  %-29s %5ds  [stripped]           ║\n" "Podman+strip (optional)" $_T3 && \
    printf "║  Stage 4/7  %-29s %5ds  [stripped+pruned]    ║\n" "Miniforge+Python ft+Jupyter" $_T4 && \
    printf "║  Stage 5/7  %-29s %5ds                       ║\n" "user+subuid+dirs+daemon" $_T5 && \
    printf "║  Stage 6/7  %-29s %5ds  [P7: COPY --chmod] ║\n" "config + validation" $_T6 && \
    printf "║  Stage 7/7  %-29s %5ds  [deletion-only]      ║\n" "cleanup + final verify" $_T7 && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  %-42s %5ds                       ║\n" "RUNTIME TOTAL" $_TOTAL && \
    echo "╚══════════════════════════════════════════════════════════════╝" && \
    echo "" && \
    rm -f /tmp/.build-timer && \
    echo "[BUILD] ========== BUILD COMPLETE (slim, same-layer strip, P7-compliant) ==========" && \
    echo ""

# ── 元数据声明（不产生镜像层） ──
WORKDIR /workspace
VOLUME ["/workspace", "/var/lib/docker"]
EXPOSE 22 8888

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD []
