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

RUN echo "=== [Builder] Installing build dependencies ===" && \
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
RUN echo "=== [Builder] Installing Jupyter and Python packages ===" && \
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
LABEL version="1.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai
ENV LANG=zh_CN.UTF-8
ENV LANGUAGE=zh_CN:zh
ENV LC_ALL=zh_CN.UTF-8
ENV PATH="/opt/venv/bin:${PATH}"
ENV NON_ROOT_USER=jupyteruser
ENV JUPYTER_PORT=8888
ENV SSH_PORT=22
ENV GRANT_SUDO=no
ENV JUPYTER_TOKEN=
ENV JUPYTER_PASSWORD=
ENV USER_PASSWORD=
ENV ALLOW_ROOT_SSH=no
ENV JUPYTER_ALLOW_ORIGIN=

RUN echo "=== [Runtime] Configuring APT mirror: ${APT_MIRROR:-official} ===" && \
    if [ "${APT_MIRROR}" = "aliyun" ]; then \
        sed -i 's|http://archive.ubuntu.com|http://mirrors.aliyun.com|g; s|http://security.ubuntu.com|http://mirrors.aliyun.com|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || \
        sed -i 's|http://archive.ubuntu.com|http://mirrors.aliyun.com|g; s|http://security.ubuntu.com|http://mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null || true; \
        echo "[Runtime] Using Aliyun APT mirror"; \
    elif [ "${APT_MIRROR}" = "tuna" ]; then \
        sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || \
        sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list 2>/dev/null || true; \
        echo "[Runtime] Using Tsinghua TUNA APT mirror"; \
    else \
        echo "[Runtime] Using official APT sources"; \
    fi

# -----------------------------------------------------------------------------
# [Stage 2.1] Install runtime system packages + Chinese locale
# Packages: ca-certificates (HTTPS), curl (healthcheck), locales (zh_CN),
#   openssh-server (SSH), openssh-client (SSH tools), procps (pgrep for healthcheck),
#   pwgen (random passwords), python3+python3-venv (venv runtime),
#   sudo (privilege escalation), supervisor (process manager), tini (init),
#   tzdata (timezone), vim (editor), wget (downloads)
# NOT included: build-essential, python3-dev, gcc (kept in builder stage only)
# -----------------------------------------------------------------------------
RUN echo "=== Stage 1/6: Install base system packages + Chinese locale ===" && \
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
    rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# [Stage 2.2] Copy Python virtual environment from builder
# -----------------------------------------------------------------------------
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:${PATH}" \
    VIRTUAL_ENV="/opt/venv"

RUN echo "=== Stage 2/6: Copy Python venv from builder ===" && \
    echo "[BUILD] Python venv copied:" && \
    python3 --version && \
    pip --version && \
    jupyter --version && \
    echo "[BUILD] Jupyter available via venv at /opt/venv" && \
    echo "export PATH=/opt/venv/bin:\$PATH" > /etc/profile.d/venv.sh && \
    echo "export VIRTUAL_ENV=/opt/venv" >> /etc/profile.d/venv.sh && \
    chmod +x /etc/profile.d/venv.sh && \
    echo "[BUILD] System-wide profile.d/venv.sh created for login shell PATH"

# -----------------------------------------------------------------------------
# [Stage 2.3] Create non-root user jupyteruser
# Strategy:
#   1. Check if jupyteruser already exists
#   2. If UID 1000 is free -> create jupyteruser with UID 1000
#   3. Else -> auto-assign next available UID
#   4. User is in sudo group (NOPASSWD controlled at runtime via GRANT_SUDO)
# -----------------------------------------------------------------------------
RUN echo "=== Stage 3/6: Create non-root user jupyteruser ===" && \
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
    echo "[BUILD] User .bashrc and /etc/environment configured with venv PATH"

# -----------------------------------------------------------------------------
# [Stage 2.4] Configure SSH service
# Host keys are cleared here, regenerated at entrypoint to ensure uniqueness per container
# -----------------------------------------------------------------------------
RUN echo "=== Stage 4/6: Configure SSH service ===" && \
    mkdir -p /run/sshd && chmod 755 /run/sshd && \
    mkdir -p /var/log/supervisor /etc/supervisor/conf.d && \
    echo "[BUILD] Runtime directories created"

COPY config/sshd_config /etc/ssh/sshd_config
RUN echo "=== Stage 5/6: Install configuration files and scripts ===" && \
    ssh-keygen -A >/dev/null 2>&1 && \
    echo "[BUILD] Initial SSH host keys generated (will be regenerated at entrypoint)" && \
    echo "[BUILD] Installing supervisord and service configurations..."

COPY config/supervisord.conf /etc/supervisor/supervisord.conf
COPY config/supervisor/conf.d/ /etc/supervisor/conf.d/
COPY config/jupyter_notebook_config.py /home/jupyteruser/.jupyter/jupyter_notebook_config.py
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY scripts/healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/healthcheck.sh && \
    chown -R jupyteruser:jupyteruser /home/jupyteruser/.jupyter && \
    chown -R jupyteruser:jupyteruser /workspace && \
    echo "[BUILD] Permissions set: entrypoint.sh and healthcheck.sh executable" && \
    echo "[BUILD] Validating sshd_config..." && \
    sshd -t && echo "[BUILD] sshd_config syntax: OK"

# -----------------------------------------------------------------------------
# [Stage 2.5] Final configuration: build info, cleanup, verification
# -----------------------------------------------------------------------------
RUN echo "=== Stage 6/6: Final configuration ===" && \
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
    cat /etc/jupyter-ssh-build-info && \
    echo "[BUILD] Build info written to /etc/jupyter-ssh-build-info" && \
    echo "[BUILD] Running final cleanup..." && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    echo "[BUILD] Cleanup complete" && \
    echo "[BUILD] Running final verification..." && \
    sshd -t && echo "[OK] sshd config valid" && \
    supervisord --version && echo "[OK] supervisord available" && \
    python --version && echo "[OK] python available" && \
    pip --version && echo "[OK] pip available" && \
    jupyter --version && echo "[OK] jupyter available" && \
    bash -n /usr/local/bin/entrypoint.sh && echo "[OK] entrypoint.sh syntax valid" && \
    bash -n /usr/local/bin/healthcheck.sh && echo "[OK] healthcheck.sh syntax valid" && \
    echo "" && \
    echo "[BUILD] ========== BUILD COMPLETE ==========" && \
    echo ""

WORKDIR /workspace
VOLUME ["/workspace"]
EXPOSE 22 8888

HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD []
