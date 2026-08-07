# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - __VARIANT_NAME__ Variant Dockerfile
# Project: SpecWeave Full-featured Development Container - __VARIANT_DESCRIPTION__
#
# =============================================================================
# ⚠️  TEMPLATE INSTRUCTIONS - 请在复制此模板后修改以下占位符：
#
# 1. __VARIANT_NAME__          : 变体名称（如 conda, conda-llvm）
# 2. __VARIANT_DESCRIPTION__   : 变体描述
# 3. __BASE_VARIANT__          : 基础变体（留空表示直接基于 devcontainer-base:latest，
#                                或填 "conda" 表示基于 devcontainer-base:conda-${BASE_TAG}）
# 4. __EXTRA_BUILD_ARGS__      : 额外构建参数声明（如 ARG LLVM_VERSION=22.1.8）
# 5. __EXTRA_INSTALL_STEPS__   : 额外安装阶段（用户自定义安装逻辑）
# 6. __EXTRA_VALIDATION__      : 额外验证命令
# 7. __VARIANT_BUILD_INFO_NAME__: build-info 文件名（如 devcontainer-variant-__VARIANT_NAME__-build-info）
#
# 请根据实际变体需求：
# - 修改 LABEL 中的 description 和 variant
# - 调整 ENV 环境变量
# - 在 __EXTRA_INSTALL_STEPS__ 区域添加自定义安装逻辑
# - 在 __EXTRA_VALIDATION__ 区域添加变体特有的验证
# - 修改 Stage 数量和命名（模板默认3个追加阶段）
# - 更新 BUILD TIMING SUMMARY 表格中的阶段描述
# =============================================================================
# Build: docker build -f variants/__VARIANT_NAME__/Dockerfile -t devcontainer-base:__VARIANT_NAME__-latest .
# CN:    docker build -f variants/__VARIANT_NAME__/Dockerfile \
#          --build-arg APT_MIRROR=aliyun --build-arg CONDA_MIRROR=tuna --build-arg PIP_MIRROR=aliyun \
#          -t devcontainer-base:__VARIANT_NAME__-latest .
# Run:   docker run -d --privileged -p 2222:22 -p 2375:2375 -p 8888:8888 \
#          -e USER_PASSWORD=pass -e JUPYTER_TOKEN=mysecret -e GRANT_SUDO=yes \
#          -v $(pwd)/workspace:/workspace -v docker-data:/var/lib/docker \
#          devcontainer-base:__VARIANT_NAME__-latest
# Verify: docker run --rm devcontainer-base:__VARIANT_NAME__-latest __EXTRA_VALIDATION__
#
# Variant Stage Layering (additional layers on top of base image):
#   Stage 1/3: Base verification + timer initialization
#   Stage 2/3: __EXTRA_INSTALL_STEPS__ (custom installation)
#   Stage 3/3: build-info + cleanup + final verification + timing summary
#
# Build Timing: 每个Stage结束时输出 [TIMER] 本阶段耗时+累计耗时，最终输出汇总表
# =============================================================================

ARG BASE_TAG=latest
ARG APT_MIRROR=official
ARG CONDA_MIRROR=tuna
ARG PIP_MIRROR=aliyun
__EXTRA_BUILD_ARGS__

FROM devcontainer-base:__BASE_VARIANT__${BASE_TAG}

ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR
__EXTRA_BUILD_ARGS__

LABEL maintainer="SpecWeave"
LABEL description="__VARIANT_DESCRIPTION__"
LABEL variant="__VARIANT_NAME__"

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# ═══════════════════════════════════════════════════════════════════
# Stage 1/3: 基础环境验证 + 计时器初始化
# 变化频率：最低
# 原则：验证基础镜像关键组件存在，初始化追加层计时器
# ═══════════════════════════════════════════════════════════════════
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [__VARIANT_NAME__ VARIANT STAGE 1/3] Base Verification + Timer Init" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[TIMER] __VARIANT_NAME__ variant build started at $(date -u +%Y-%m-%dT%H:%M:%SZ)" && \
    echo "START=$_STAGE_START" > /tmp/.variant-build-timer && \
    echo "[BUILD] Verifying base image components..." && \
    echo "  - devuser exists: $(id devuser 2>&1 | head -1)" && \
    echo "  - /opt/venv exists: $(test -d /opt/venv && echo 'yes' || echo 'no')" && \
    echo "  - python (venv): $(python --version 2>&1)" && \
    echo "  - PATH: $PATH" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _TOTAL=$((_NOW - $(grep '^START=' /tmp/.variant-build-timer | cut -d= -f2))) && \
    echo "VS1=$_NOW" >> /tmp/.variant-build-timer && \
    echo "[TIMER] Stage 1/3 (base verification) took ${_ELAPSED}s | Variant cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 1 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 2/3: 自定义安装步骤
# 变化频率：中
# 原则：在此处添加变体特有的安装逻辑
# ⚠️  请在以下区域添加你的安装代码
# ═══════════════════════════════════════════════════════════════════
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [__VARIANT_NAME__ VARIANT STAGE 2/3] Custom Installation Steps" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[INFO] __EXTRA_INSTALL_STEPS__ - Replace this comment with your installation logic" && \
    echo "[INFO] Example:" && \
    echo "[INFO]   - apt-get install packages" && \
    echo "[INFO]   - conda install packages" && \
    echo "[INFO]   - pip install packages" && \
    echo "[INFO]   - Download and extract archives" && \
    echo "[INFO]   - Configure settings" && \
    echo "" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.variant-build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "VS2=$_NOW" >> /tmp/.variant-build-timer && \
    echo "[TIMER] Stage 2/3 (custom install) took ${_ELAPSED}s | Variant cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 2 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 3/3: 构建元数据 + 清理 + 最终验证 + 计时器汇总表
# 变化频率：最低
# 原则：写入 variant build-info；清理缓存；最终验证所有关键组件；
#       确认核心服务未被破坏；输出耗时汇总表
# ═══════════════════════════════════════════════════════════════════
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [__VARIANT_NAME__ VARIANT STAGE 3/3] Final Metadata, Cleanup, Verification" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[ACTION] Writing build metadata to /etc/__VARIANT_BUILD_INFO_NAME__..."; \
    printf '%s\n' \
        "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        "VARIANT=__VARIANT_NAME__" \
        "VARIANT_DESCRIPTION=__VARIANT_DESCRIPTION__" \
        "BASE_IMAGE=devcontainer-base:__BASE_VARIANT__\${BASE_TAG}" \
        "APT_MIRROR=${APT_MIRROR}" \
        "CONDA_MIRROR=${CONDA_MIRROR}" \
        "PIP_MIRROR=${PIP_MIRROR}" \
        "SYSTEM_VENV=/opt/venv" \
        "SERVICES_PRESERVED=sshd,dockerd,podman,jupyter,supervisord" \
        "BUILD_TIMER=enabled" \
        > /etc/__VARIANT_BUILD_INFO_NAME__ && \
    echo "[OK] Build metadata written:"; \
    cat /etc/__VARIANT_BUILD_INFO_NAME__; \
    echo ""; \
    echo "[ACTION] Running cleanup..."; \
    apt-get clean 2>/dev/null || true; \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*; \
    echo "[OK] Cleanup complete"; \
    echo ""; \
    echo "┌─────────────────────────────────────────────────┐"; \
    echo "│  [VALIDATION CHECKPOINT - Stage 3/3]           │"; \
    echo "│  Running final service + availability checks    │"; \
    echo "└─────────────────────────────────────────────────┘"; \
    echo ""; \
    echo "[VALIDATE 1/5] System venv /opt/venv preserved..."; \
    test -d /opt/venv && test -x /opt/venv/bin/python && echo "[OK] /opt/venv exists with python binary"; \
    /opt/venv/bin/python --version; \
    echo "[VALIDATE 2/5] Jupyter still available via venv..."; \
    /opt/venv/bin/jupyter --version 2>&1 | head -3; \
    echo "[OK] Jupyter available from venv"; \
    echo "[VALIDATE 3/5] Docker and supervisord still present..."; \
    docker --version 2>&1; \
    supervisord --version 2>&1; \
    echo "[OK] Core services preserved"; \
    echo "[VALIDATE 4/5] devuser exists and is accessible..."; \
    id devuser 2>&1 | head -1; \
    echo "[OK] devuser available"; \
    echo "[VALIDATE 5/5] __VARIANT_NAME__ variant specific validation..."; \
    echo "[INFO] __EXTRA_VALIDATION__ - Replace this with your validation commands"; \
    echo "[INFO] Example: test -x /usr/local/bin/your-tool && your-tool --version"; \
    echo ""; \
    echo "[VALIDATE] All validation checks completed"; \
    echo ""; \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.variant-build-timer | cut -d= -f2) && \
    _VS1=$(grep '^VS1=' /tmp/.variant-build-timer | cut -d= -f2) && \
    _VS2=$(grep '^VS2=' /tmp/.variant-build-timer | cut -d= -f2) && \
    _VT1=$((_VS1 - _START)) && \
    _VT2=$((_VS2 - _VS1)) && \
    _VT3=$_ELAPSED && \
    _VTOTAL=$((_NOW - _START)) && \
    echo "╔══════════════════════════════════════════════════════════════╗"; \
    echo "║  BUILD TIMING SUMMARY (__VARIANT_NAME__ Variant - 3 Stages)║"; \
    echo "╠══════════════════════════════════════════════════════════════╣"; \
    printf "║  Stage 1/3  base verification         %5ds               ║\n" $_VT1; \
    printf "║  Stage 2/3  custom installation       %5ds               ║\n" $_VT2; \
    printf "║  Stage 3/3  metadata+final verify     %5ds               ║\n" $_VT3; \
    echo "╠══════════════════════════════════════════════════════════════╣"; \
    printf "║  VARIANT TOTAL (add-on layers)        %5ds               ║\n" $_VTOTAL; \
    echo "╚══════════════════════════════════════════════════════════════╝"; \
    echo ""; \
    rm -f /tmp/.variant-build-timer; \
    echo "########################################################################"; \
    echo "# __VARIANT_NAME__ VARIANT BUILD COMPLETE!"; \
    echo "# __VARIANT_DESCRIPTION__"; \
    echo "########################################################################"; \
    echo ""
