# Docker Runtime Image 项目骨架
# Pattern: 01-build-env-reuse（基础镜像环境直用）
# Verified: 2026-07-22 — 五条红线全通（xmnn-runtime:test）
#
# 使用方法：
#   1. 复制此目录到你的项目中（如 docker/runtime/）
#   2. 替换所有 {{PLACEHOLDER}} 变量
#   3. 根据实际情况调整可选依赖和验证步骤
#   4. 如果不需要功能验证，删除或注释掉 R3 验证段
#   5. docker build -t <image_name> -f Dockerfile ..
#
# 变量替换清单见 CONFIG.md

FROM {{BUILD_IMAGE_NAME}}:{{BUILD_IMAGE_TAG}} AS runtime

ARG DEBIAN_FRONTEND=noninteractive
ARG CONDA_ENV_NAME={{CONDA_ENV_NAME}}
ARG AI_UID=1000
ARG AI_GID=1000
ARG WORKSPACE_DIR=/workspace

USER root

ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple \
    PIP_TRUSTED_HOST=mirrors.aliyun.com \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin:/opt/conda/bin:${PATH} \
    LD_LIBRARY_PATH=/opt/conda/envs/${CONDA_ENV_NAME}/lib:/opt/conda/lib:/usr/local/lib

# ------------------------------------------------------------------
# 系统依赖（仅 runtime 需要的额外包，不装 Python 包）
# ------------------------------------------------------------------
RUN set -eux; \
    for f in /etc/apt/sources.list /etc/apt/sources.list.d/*.list; do \
        if [ -f "$f" ]; then \
            sed -i -E 's@http://(deb|security).debian.org@https://mirrors.aliyun.com@g' "$f" || true; \
            sed -i -E 's@https?://(deb|security).debian.org@https://mirrors.aliyun.com@g' "$f" || true; \
        fi; \
    done; \
    apt-get update -qq; \
    apt-get install -y --no-install-recommends -qq \
        tzdata sudo acl passwd gosu \
        libstdc++6 libgomp1 libgcc-s1 \
        findutils; \
    {{TIMEZONE_SETUP}} \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------------
# 远程 pip 依赖（利用 Docker 层缓存，wheel 变更不影响此层）
# ------------------------------------------------------------------
RUN set -eux; \
    pip install --no-cache-dir \
        {{EXTRA_PIP_PACKAGES}}; \
    python -c "from importlib.metadata import version; \
deps=[{{VERIFY_PIP_DEPS}}]; \
[print(f'  {d}: {version(d)}') for d in deps if True]"

# ------------------------------------------------------------------
# 创建非root用户（处理UID/GID冲突）
# ------------------------------------------------------------------
RUN set -eux; \
    if ! getent group ai >/dev/null; then \
        if getent group ${AI_GID} >/dev/null; then \
            EXISTING_GROUP=$(getent group ${AI_GID} | cut -d: -f1); \
            echo "GID ${AI_GID} taken by '${EXISTING_GROUP}', creating ai group with auto GID"; \
            groupadd ai; \
        else \
            groupadd -g ${AI_GID} ai; \
        fi; \
    fi; \
    AI_GID_ACTUAL=$(getent group ai | cut -d: -f3); \
    if ! id -u ai >/dev/null 2>&1; then \
        if getent passwd ${AI_UID} >/dev/null; then \
            echo "UID ${AI_UID} exists, creating ai user with auto UID"; \
            useradd -m -s /bin/bash -g ai ai; \
        else \
            useradd -m -s /bin/bash -u ${AI_UID} -g ai ai; \
        fi; \
    fi; \
    usermod -aG sudo ai; \
    echo "ai ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-ai; \
    chmod 0440 /etc/sudoers.d/90-ai; \
    mkdir -p ${WORKSPACE_DIR} /home/ai/.local /home/ai/.pip /home/ai/.cache; \
    chown -R ai:ai /home/ai ${WORKSPACE_DIR}

# ------------------------------------------------------------------
# 复制本地 wheel 和 entrypoint
# ------------------------------------------------------------------
COPY {{WHEEL_RELATIVE_PATH}}/{{WHEEL_NAME_PATTERN}} /tmp/wheels/
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY docker/_{{PKG_NAME}}_init.py /tmp/_init/_{{PKG_NAME}}_init.py
COPY docker/{{PKG_NAME}}_init.pth /tmp/_init/{{PKG_NAME}}_init.pth
RUN chmod +x /usr/local/bin/entrypoint.sh

# ------------------------------------------------------------------
# 安装 wheel + .pth 自初始化 + 内置验证
# ------------------------------------------------------------------
RUN set -eux; \
    WHEEL_FILE=$(ls /tmp/wheels/{{WHEEL_NAME_PATTERN}} | head -1); \
    echo "Installing wheel: $WHEEL_FILE"; \
    pip install --no-cache-dir "$WHEEL_FILE"; \
    SITE_PKGS=$(python -c "import site; print(site.getsitepackages()[0])"); \
    cp /tmp/_init/_{{PKG_NAME}}_init.py "$SITE_PKGS/"; \
    cp /tmp/_init/{{PKG_NAME}}_init.pth "$SITE_PKGS/"; \
    echo "Verifying installation..."; \
    python -c "from importlib.metadata import version; print('  {{PYPI_PACKAGE_NAME}}:', version('{{PYPI_PACKAGE_NAME}}'))"; \
    echo "Verifying shared library dependencies (ldd)..."; \
    for so in "$SITE_PKGS"/{{LIB_DIR}}/_libs/*.so*; do \
        if [ -f "$so" ]; then \
            MISSING=$(ldd "$so" 2>/dev/null | grep "not found" || true); \
            if [ -n "$MISSING" ]; then \
                echo "ERROR: Missing deps for $so:"; echo "$MISSING"; exit 1; \
            fi; \
        fi; \
    done; \
    echo "All shared library dependencies OK"; \
    echo "Verifying core imports..."; \
    python -c "import {{CORE_MODULE_COMMA_SEPARATED}}; print('  Core imports OK')"; \
    {{BUILTIN_VERIFY_EXTRA}} \
    chown -R ai:ai "$SITE_PKGS" /home/ai/.local /home/ai/.cache; \
    CONDA_ENV_BIN="/opt/conda/envs/${CONDA_ENV_NAME}/bin"; \
    if [ -d "$CONDA_ENV_BIN" ]; then chown -R ai:ai "$CONDA_ENV_BIN"; fi; \
    rm -rf /tmp/wheels /tmp/_init; \
    echo "=== {{PROJECT_NAME}} Runtime image built successfully! ==="

WORKDIR ${WORKSPACE_DIR}
RUN chmod 2775 ${WORKSPACE_DIR}
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["/bin/bash", "-l"]