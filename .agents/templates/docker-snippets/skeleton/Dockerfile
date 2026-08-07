# =============================================================================
# Docker Runtime Image 项目骨架 (dockerfile-runtime-logical-layering v1.3)
# Pattern: 01-build-env-reuse（基础镜像环境直用）
# Updated: 2026-04-07 — 新增构建耗时统计 + 语法验证检查点 + 分层缓存优化
#
# Runtime Stage Layering (6-stage pattern):
#   Stage 1/6: 系统包 + timezone + APT镜像配置 (变化频率: 最低)
#   Stage 2/6: pip额外依赖安装 (变化频率: 低)
#   Stage 3/6: ai用户/组创建 + workspace目录权限 (变化频率: 中)
#   Stage 4/6: COPY wheels/init文件 + wheel安装 + 依赖验证 (变化频率: 中高, ★热点)
#   Stage 5/6: COPY entrypoint/脚本 + chmod + 语法验证 (变化频率: 高)
#   Stage 6/6: build-info + 最终验证 + 耗时汇总表 + 清理 (变化频率: 最低)
#
# Build Timing: 每个Stage结束时输出 [TIMER] 本阶段耗时+累计耗时，最终输出汇总表
# 缓存设计：entrypoint等脚本变更(Stage5)不会导致wheel重装(Stage4)
#
# 使用方法：
#   1. 复制此目录到你的项目中（如 docker/runtime/）
#   2. 替换所有 {{PLACEHOLDER}} 变量
#   3. 根据实际情况调整可选依赖和验证步骤
#   4. 如果不需要功能验证，删除或注释掉 Stage 4 验证段
#   5. docker build -t <image_name> -f Dockerfile ..
#
# 变量替换清单见 CONFIG.md
# =============================================================================

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

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

# ═══════════════════════════════════════════════════════════════════
# Stage 1/6: 系统包安装 + timezone + APT镜像配置
# 变化频率：最低（基础镜像确定后很少改）
# 初始化计时器 /tmp/.build-timer
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== Stage 1/6: System packages + timezone + APT mirror ===" && \
    _STAGE_START=$(date +%s) && \
    echo "[TIMER] Runtime stage started at $(date -u +%Y-%m-%dT%H:%M:%SZ)" && \
    echo "START=$_STAGE_START" > /tmp/.build-timer && \
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
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime; \
    echo "Asia/Shanghai" > /etc/timezone; \
    echo "[BUILD] Timezone set to Asia/Shanghai" && \
    rm -rf /var/lib/apt/lists/* && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _TOTAL=$((_NOW - $(grep '^START=' /tmp/.build-timer | cut -d= -f2))) && \
    echo "S1=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 1/6 (system+tz) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 2/6: pip额外依赖安装
# 变化频率：低（Python依赖版本升级时改）
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== Stage 2/6: Install pip dependencies ===" && \
    _STAGE_START=$(date +%s) && \
    pip install --no-cache-dir \
        {{EXTRA_PIP_PACKAGES}}; \
    python -c "from importlib.metadata import version; \
deps=[{{VERIFY_PIP_DEPS}}]; \
[print(f'  {d}: {version(d)}') for d in deps if True]" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S2=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 2/6 (pip deps) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 3/6: ai用户/组创建 + sudoers + workspace目录权限
# 变化频率：中（新增用户/目录时改）
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== Stage 3/6: Create non-root user 'ai' + workspace ===" && \
    _STAGE_START=$(date +%s) && \
    if ! getent group ai >/dev/null; then \
        if getent group ${AI_GID} >/dev/null; then \
            EXISTING_GROUP=$(getent group ${AI_GID} | cut -d: -f1); \
            echo "[BUILD] GID ${AI_GID} taken by '${EXISTING_GROUP}', creating ai group with new GID"; \
            groupadd ai; \
        else \
            groupadd -g ${AI_GID} ai; \
        fi; \
    fi; \
    if ! id -u ai >/dev/null 2>&1; then \
        if getent passwd ${AI_UID} >/dev/null; then \
            echo "[BUILD] UID ${AI_UID} exists, creating ai user with auto UID"; \
            useradd -m -s /bin/bash -g ai ai; \
        else \
            useradd -m -s /bin/bash -u ${AI_UID} -g ai ai; \
        fi; \
    fi; \
    usermod -aG sudo ai; \
    echo "ai ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-ai; \
    chmod 0440 /etc/sudoers.d/90-ai; \
    mkdir -p ${WORKSPACE_DIR} /home/ai/.local /home/ai/.pip /home/ai/.cache; \
    chown -R ai:ai /home/ai ${WORKSPACE_DIR} && \
    echo "[BUILD] User 'ai' created: UID=$(id -u ai) GID=$(id -g ai)" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S3=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 3/6 (user+perms) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 4/6: COPY wheels/init文件 + wheel安装 + 依赖验证
# 变化频率：中高（代码变更时改，★热点阶段）
# 缓存设计：此阶段仅在wheels/init变化时失效，不受脚本变更影响
# ═══════════════════════════════════════════════════════════════════
COPY {{WHEEL_RELATIVE_PATH}}/{{WHEEL_NAME_PATTERN}} /tmp/wheels/
COPY docker/_{{PKG_NAME}}_init.py /tmp/_init/_{{PKG_NAME}}_init.py
COPY docker/{{PKG_NAME}}_init.pth /tmp/_init/{{PKG_NAME}}_init.pth

RUN echo "=== Stage 4/6: Install wheel + dependency verification ===" && \
    _STAGE_START=$(date +%s) && \
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
    rm -rf /tmp/wheels /tmp/_init && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S4=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 4/6 (wheel install+verify) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 5/6: COPY entrypoint/脚本 + chmod + 语法验证检查点
# 变化频率：高（脚本调整时改，缓存不会让Stage4重装层失效）
# ═══════════════════════════════════════════════════════════════════
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh

RUN echo "=== Stage 5/6: Entrypoint permissions + syntax validation ===" && \
    _STAGE_START=$(date +%s) && \
    chmod +x /usr/local/bin/entrypoint.sh && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│  [VALIDATION CHECKPOINT - Stage 5/6]            │" && \
    echo "│  Running syntax validation for entrypoint       │" && \
    echo "└─────────────────────────────────────────────────┘" && \
    echo "[VALIDATE] bash -n entrypoint.sh..." && \
    bash -n /usr/local/bin/entrypoint.sh && echo "[OK] entrypoint.sh bash syntax valid" && \
    echo "" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "S5=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage 5/6 (entrypoint+validate) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage 6/6: build-info + 最终验证 + 耗时汇总表 + 清理
# 变化频率：最低（版本发布时改）
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== Stage 6/6: Final metadata, cleanup, and verification ===" && \
    _STAGE_START=$(date +%s) && \
    BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) && \
    printf 'BUILD_DATE=%s\nBASE_IMAGE={{BUILD_IMAGE_NAME}}:{{BUILD_IMAGE_TAG}}\nCONDA_ENV_NAME=%s\nPYTHONUNBUFFERED=1\nWORKSPACE_DIR=%s\nBUILD_TIMER=enabled\n' \
        "$BUILD_DATE" "${CONDA_ENV_NAME}" "${WORKSPACE_DIR}" > /etc/{{PKG_NAME}}-runtime-build-info && \
    cat /etc/{{PKG_NAME}}-runtime-build-info && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│  [FINAL VERIFICATION - Stage 6/6]               │" && \
    echo "│  Verifying all critical components              │" && \
    echo "└─────────────────────────────────────────────────┘" && \
    python -c "import {{CORE_MODULE_COMMA_SEPARATED}}; print('[OK] Core imports verified')" && \
    python -c "from importlib.metadata import version; print(f'[OK] {{PYPI_PACKAGE_NAME}} version: {version(\"{{PYPI_PACKAGE_NAME}}\")}')" && \
    bash -n /usr/local/bin/entrypoint.sh && echo "[OK] entrypoint.sh syntax valid" && \
    chmod 2775 ${WORKSPACE_DIR} && \
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
    echo "║         BUILD TIMING SUMMARY ({{PROJECT_NAME}})            ║" && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  Stage 1/6  system packages + tz      %5ds               ║\n" $_T1 && \
    printf "║  Stage 2/6  pip dependencies          %5ds               ║\n" $_T2 && \
    printf "║  Stage 3/6  user ai + permissions     %5ds               ║\n" $_T3 && \
    printf "║  Stage 4/6  wheel install + verify    %5ds  ★ hotspot    ║\n" $_T4 && \
    printf "║  Stage 5/6  entrypoint + validate     %5ds               ║\n" $_T5 && \
    printf "║  Stage 6/6  metadata + final verify   %5ds               ║\n" $_T6 && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  BUILD TOTAL                          %5ds               ║\n" $_TOTAL && \
    echo "╚══════════════════════════════════════════════════════════════╝" && \
    echo "" && \
    rm -f /tmp/.build-timer && \
    echo "=== {{PROJECT_NAME}} Runtime image built successfully! ==="

WORKDIR ${WORKSPACE_DIR}
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["/bin/bash", "-l"]
