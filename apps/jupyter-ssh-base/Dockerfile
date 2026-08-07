# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# Jupyter SSH Base - Dockerfile (Multi-stage build)
# Project: SpecWeave Jupyter + OpenSSH Base Image
# Base: ubuntu:26.04 | OpenSSH Server + Jupyter Notebook/Lab | zh_CN.UTF-8 / Asia/Shanghai
# Non-root user: jupyteruser (UID 1000 if available, auto-assigned otherwise)
# Services: sshd (port 22) + Jupyter (port 8888), managed by supervisord
#
# Build: docker build -t jupyter-ssh-base .
# CN:    docker build --build-arg APT_MIRROR=aliyun --build-arg PIP_MIRROR=aliyun -t jupyter-ssh-base .
# Run:   docker run -d -p 2222:22 -p 8888:8888 -v $(pwd)/workspace:/workspace \
#          -e USER_PASSWORD=pass -e JUPYTER_TOKEN=mysecret jupyter-ssh-base
# Debug: docker run -it --rm jupyter-ssh-base bash (interactive shell, no services started)
#
# Runtime Stage Layering (dockerfile-runtime-logical-layering pattern v1.3):
#   Stage 2.1/6: 系统包安装 + APT镜像 + locale/timezone (变化频率: 最低)
#   Stage 2.2/6: COPY venv from builder + PATH 配置 (变化频率: 低)
#   Stage 2.3/6: 用户/组/目录创建 + 权限设置 (变化频率: 中)
#   Stage 2.4/6: 运行时目录准备 (变化频率: 中)
#   Stage 2.5/6: 配置文件/脚本 COPY + 语法验证 (变化频率: 高)
#   Stage 2.6/6: build-info + 清理 + 最终验证 (变化频率: 最低)
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
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN echo "=== [Builder] Creating Python virtual environment ===" && \
    python3 -m venv /opt/venv && \
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
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    echo "=== [Builder] Installing Jupyter and Python packages ===" && \
    /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt && \
    echo "=== [Builder] Python packages installed ===" && \
    /opt/venv/bin/jupyter --version

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Minimal production image
# -----------------------------------------------------------------------------
FROM ubuntu:26.04

ARG APT_MIRROR

LABEL maintainer="SpecWeave"
LABEL description="Standardized Ubuntu 26.04 base image with OpenSSH Server + Jupyter Notebook, managed by supervisord"
LABEL version="1.3"

# ── 元数据层：环境变量声明（不产生层，仅元数据） ──
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai \
    LANG=zh_CN.UTF-8 \
    LANGUAGE=zh_CN:zh \
    LC_ALL=zh_CN.UTF-8 \
    PATH="/opt/venv/bin:${PATH}" \
    VIRTUAL_ENV="/opt/venv" \
    NON_ROOT_USER=jupyteruser \
    JUPYTER_PORT=8888 \
    SSH_PORT=22 \
    GRANT_SUDO=no \
    ALLOW_ROOT_SSH=no \
    JUPYTER_ALLOW_ORIGIN=

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# ═══════════════════════════════════════════════════════════════════
# Stage 2.1/6: 系统包安装 + APT镜像 + locale/timezone 配置
# 变化频率：最低（基础镜像确定后很少改）
# 原则：--no-install-recommends，同层内完成镜像配置+locale+timezone+清理
#       初始化计时器文件 /tmp/.build-timer（记录各阶段完成时间戳）
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    echo "=== Stage 1/6: Install base system packages + Chinese locale ===" && \
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
    apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
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
    && echo "[BUILD] Runtime packages installed" && \
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
    echo "[TIMER] Stage 1/6 (system+locale) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 2.2/6: 语言运行时复制（从 builder 阶段 COPY venv）
# 变化频率：低（依赖版本升级时改）
# 原则：COPY --from=builder 后立即验证二进制可用，配置 profile.d
# ═══════════════════════════════════════════════════════════════════
COPY --from=builder /opt/venv /opt/venv

RUN echo "=== Stage 2/6: Copy Python venv from builder ===" && \
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
    echo "S2=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 2/6 (venv+PATH) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 2.3/6: 用户/组/工作目录创建 + 权限设置
# 变化频率：中（新增用户或目录时改）
# 原则：UID 优先固定值 1000，被占用时自动 fallback；
#       chown 在同层完成；同时写入 ~/.bashrc 和 /etc/environment
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== Stage 3/6: Create non-root user jupyteruser ===" && \
    _STAGE_START=$(date +%s) && \
    if getent passwd jupyteruser >/dev/null 2>&1; then \
        echo "[BUILD] User jupyteruser already exists (UID=$(id -u jupyteruser)), ensuring group membership..."; \
        usermod -aG sudo jupyteruser; \
    elif ! getent passwd 1000 >/dev/null 2>&1; then \
        echo "[BUILD] UID 1000 is free, creating jupyteruser with UID 1000"; \
        useradd -m -s /bin/bash -u 1000 -G sudo jupyteruser; \
    else \
        EXISTING_USER=$(getent passwd 1000 | cut -d: -f1); \
        echo "[BUILD] UID 1000 occupied by '${EXISTING_USER}', auto-assigning UID for jupyteruser"; \
        useradd -m -s /bin/bash -G sudo jupyteruser; \
    fi && \
    echo "[BUILD] User jupyteruser created: UID=$(id -u jupyteruser) GID=$(id -g jupyteruser) groups=$(groups jupyteruser)" && \
    mkdir -p /workspace /home/jupyteruser/.jupyter/jupyter_server_config.d /home/jupyteruser/.ssh && \
    chmod 755 /workspace && \
    chmod 700 /home/jupyteruser/.ssh && \
    chown -R jupyteruser:jupyteruser /workspace /home/jupyteruser/.jupyter /home/jupyteruser/.ssh && \
    echo "[BUILD] Working directory /workspace and .jupyter/.ssh directories created with proper permissions" && \
    echo "export PATH=/opt/venv/bin:\$PATH" >> /home/jupyteruser/.bashrc && \
    echo "export VIRTUAL_ENV=/opt/venv" >> /home/jupyteruser/.bashrc && \
    chown jupyteruser:jupyteruser /home/jupyteruser/.bashrc && \
    echo "PATH=/opt/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >> /etc/environment && \
    echo "[BUILD] User .bashrc and /etc/environment configured with venv PATH (PATH layer 2+3)" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S3=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 3/6 (user+perms) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 2.4/6: 运行时空目录准备
# 变化频率：中（新增服务需要新目录时改）
# 原则：mkdir -p 所有 runtime 需要的空目录（/run/sshd 等必须存在
#       但 apt 安装后可能不存在或权限不对的目录）
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== Stage 4/6: Prepare runtime directories ===" && \
    _STAGE_START=$(date +%s) && \
    mkdir -p /run/sshd && chmod 755 /run/sshd && \
    mkdir -p /var/log/supervisor /etc/supervisor/conf.d && \
    echo "[BUILD] Runtime directories ready: /run/sshd /var/log/supervisor /etc/supervisor/conf.d" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S4=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 4/6 (runtime dirs) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 2.5/6: 配置文件 + 脚本复制 + 语法验证（关键验证节点）
# 变化频率：高（配置调整时改，缓存不会让前面的层失效）
# 原则：所有 COPY 集中在一起；同层 RUN 做权限设置 + 全部语法验证
#       （sshd -t、bash -n 等），构建即测试，问题早发现
# ═══════════════════════════════════════════════════════════════════
COPY config/sshd_config /etc/ssh/sshd_config
COPY config/supervisord.conf /etc/supervisor/supervisord.conf
COPY config/supervisor/conf.d/ /etc/supervisor/conf.d/
COPY config/jupyter_notebook_config.py /home/jupyteruser/.jupyter/jupyter_notebook_config.py
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY scripts/healthcheck.sh /usr/local/bin/healthcheck.sh

RUN echo "=== Stage 5/6: Install configs and validate syntax ===" && \
    _STAGE_START=$(date +%s) && \
    chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/healthcheck.sh && \
    chown -R jupyteruser:jupyteruser /home/jupyteruser/.jupyter && \
    chown -R jupyteruser:jupyteruser /workspace && \
    echo "[BUILD] Permissions set: entrypoint.sh and healthcheck.sh executable" && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│  [VALIDATION CHECKPOINT - Stage 5/6]            │" && \
    echo "│  Running syntax validation for all configs      │" && \
    echo "└─────────────────────────────────────────────────┘" && \
    echo "[VALIDATE 1/3] sshd -t (SSH daemon config syntax)..." && \
    sshd -t && echo "[OK] sshd_config syntax valid" && \
    echo "[VALIDATE 2/3] bash -n entrypoint.sh (shell syntax)..." && \
    bash -n /usr/local/bin/entrypoint.sh && echo "[OK] entrypoint.sh bash syntax valid" && \
    echo "[VALIDATE 3/3] bash -n healthcheck.sh (shell syntax)..." && \
    bash -n /usr/local/bin/healthcheck.sh && echo "[OK] healthcheck.sh bash syntax valid" && \
    echo "" && \
    echo "[BUILD] All 3 syntax validation checks passed" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S5=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 5/6 (config+validation) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 2.6/6: 构建元数据 + 最终清理 + 最终可用性验证
# 变化频率：最低（版本发布时改）
# 原则：写入 build-info 便于追溯；清理 apt/tmp 缓存减小镜像体积；
#       最终验证关键命令可执行；输出耗时汇总表；删除计时器文件
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== Stage 6/6: Final metadata, cleanup, and verification ===" && \
    _STAGE_START=$(date +%s) && \
    JUPYTER_UID=$(id -u jupyteruser) && \
    echo "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /etc/jupyter-ssh-build-info && \
    echo "BASE_IMAGE=ubuntu:26.04" >> /etc/jupyter-ssh-build-info && \
    echo "BUILD_TYPE=multi-stage" >> /etc/jupyter-ssh-build-info && \
    echo "LOCALE=zh_CN.UTF-8" >> /etc/jupyter-ssh-build-info && \
    echo "TIMEZONE=Asia/Shanghai" >> /etc/jupyter-ssh-build-info && \
    echo "NON_ROOT_USER=jupyteruser" >> /etc/jupyter-ssh-build-info && \
    echo "NON_ROOT_UID=${JUPYTER_UID}" >> /etc/jupyter-ssh-build-info && \
    echo "SERVICES=sshd,jupyter" >> /etc/jupyter-ssh-build-info && \
    echo "SUPERVISOR=enabled" >> /etc/jupyter-ssh-build-info && \
    echo "PYTHON_VENV=/opt/venv" >> /etc/jupyter-ssh-build-info && \
    echo "PATH_LAYERS=4(docker-env+etc-environment+profile.d+supervisor)" >> /etc/jupyter-ssh-build-info && \
    echo "BUILD_TIMER=enabled" >> /etc/jupyter-ssh-build-info && \
    cat /etc/jupyter-ssh-build-info && \
    echo "[BUILD] Build info written to /etc/jupyter-ssh-build-info" && \
    echo "[BUILD] Running final cleanup..." && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "[BUILD] APT cache cleaned" && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│  [FINAL VERIFICATION - Stage 6/6]               │" && \
    echo "│  Verifying all critical binaries are runnable   │" && \
    echo "└─────────────────────────────────────────────────┘" && \
    tini --version >/dev/null 2>&1 && echo "[OK] tini (init) available" && \
    supervisord --version && echo "[OK] supervisord available" && \
    sshd -t && echo "[OK] sshd config valid" && \
    python --version && echo "[OK] python available" && \
    pip --version && echo "[OK] pip available" && \
    jupyter --version && echo "[OK] jupyter available" && \
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
    _T1=$((_S1 - _START)) && \
    _T2=$((_S2 - _S1)) && \
    _T3=$((_S3 - _S2)) && \
    _T4=$((_S4 - _S3)) && \
    _T5=$((_S5 - _S4)) && \
    _T6=$_ELAPSED && \
    _TOTAL=$((_NOW - _START)) && \
    echo "╔══════════════════════════════════════════════════════════════╗" && \
    echo "║         BUILD TIMING SUMMARY (Runtime Stage)               ║" && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  Stage 1/6  system packages + locale   %5ds               ║\n" $_T1 && \
    printf "║  Stage 2/6  venv copy + PATH config    %5ds               ║\n" $_T2 && \
    printf "║  Stage 3/6  user creation + perms      %5ds               ║\n" $_T3 && \
    printf "║  Stage 4/6  runtime directories        %5ds               ║\n" $_T4 && \
    printf "║  Stage 5/6  config + syntax validate   %5ds               ║\n" $_T5 && \
    printf "║  Stage 6/6  metadata + final verify    %5ds               ║\n" $_T6 && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  RUNTIME TOTAL                         %5ds               ║\n" $_TOTAL && \
    echo "╚══════════════════════════════════════════════════════════════╝" && \
    echo "" && \
    rm -f /tmp/.build-timer /tmp/* /var/tmp/* && \
    echo "[BUILD] ========== BUILD COMPLETE ==========" && \
    echo ""

# ── 元数据声明（不产生镜像层） ──
WORKDIR /workspace
VOLUME ["/workspace"]
EXPOSE 22 8888

HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD []
