# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - Example Custom Variant
# Description: v1.1.0框架功能演示：自定义用户+Shell配置+Jupyter内核+文档部署
# Base: devcontainer-base:${BASE_TAG}
#
# 本变体是 variant-framework v1.1.0 新功能的参考实现，展示：
#   1. 自定义非root用户（ai:1001替代默认devuser:1000）
#   2. Shell环境标准化（umask、PATH持久化、bashrc配置）
#   3. 自定义Jupyter内核注册
#   4. 文档容器内部署
#   5. PIP_USER构建/运行时模式切换
#
# Build: docker build -f variants/example-custom/Dockerfile \
#          --build-arg DEVTARGET_USER=ai --build-arg DEVTARGET_UID=1001 \
#          -t devcontainer-base:example-custom-latest .
# =============================================================================

ARG BASE_TAG=latest
ARG APT_MIRROR=official
ARG CONDA_MIRROR=tuna
ARG PIP_MIRROR=aliyun

# ── 自定义用户参数（v1.1.0新功能）──────────────────────────────────
ARG DEVTARGET_USER=ai
ARG DEVTARGET_UID=1001
ARG DEVTARGET_GID=1001
ARG GRANT_SUDO=yes
# ⚠️ USER_PASSWORD: 构建期设置密码会写入镜像层历史，生产环境推荐SSH密钥
# ARG USER_PASSWORD=

FROM devcontainer-base:${BASE_TAG}

ARG BASE_TAG
ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR
ARG DEVTARGET_USER
ARG DEVTARGET_UID
ARG DEVTARGET_GID
ARG GRANT_SUDO
# ARG USER_PASSWORD

LABEL maintainer="SpecWeave"
LABEL description="Example variant demonstrating v1.1.0 framework features (custom user/Jupyter/shell/docs)"
LABEL variant="example-custom"
LABEL framework.version="1.1.0"

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# Copy shared framework (v1.1.0, 13 modules)
COPY shared/lib/ /usr/local/share/variant-framework/
COPY shared/scripts/conda-mirror-setup.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/conda-mirror-setup.sh

# ── Stage 0/5: Custom user configuration (v1.1.0新功能) ──────────
# 在S1之前配置自定义用户，确保后续模块使用正确的用户名
RUN <<'S0_USER'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_start "example-custom"
variant_timer_stage 0 "Custom user configuration"

# 一键配置目标用户：创建/重命名 + sudo + 密码（如设置）
variant_configure_target_user

# 配置标准Shell环境（umask 0022）
variant_configure_shell_profile 0022

# 持久化额外PATH（示例：将/opt/tools/bin加入PATH）
mkdir -p /opt/tools/bin
variant_persist_path "/opt/tools/bin" prepend

# 追加自定义bashrc内容（示例：欢迎信息、别名）
variant_append_user_bashrc '
# ── Custom example settings ──
alias ll="ls -alF"
export EXAMPLE_VARIANT="example-custom"
echo "[example-custom] Welcome, $(whoami)! Framework v1.1.0 loaded."
'

variant_log_ok "Custom user '${DEVTARGET_USER}' configured with shell profile"
S0_USER

# ── Stage 1/5: Framework init + mirrors ────────────────────────────
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    <<'S1'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 1 "Framework init + mirror configuration"
variant_log_info "Framework version: v${variant_framework_version}"
variant_log_info "Target user: ${DEVTARGET_USER} (UID=${DEVTARGET_UID})"
/opt/conda/bin/conda --version
test -d /opt/conda/envs/main && variant_log_ok "main env exists"
/opt/conda/envs/main/bin/python --version
variant_configure_mirrors

# 安装一些额外的Jupyter/数据科学包用于演示
apt-get update -qq
apt_install_group "Demo: Jupyter + utilities" jupyter-server less
S1

# ── Stage 2/5: Demo packages ───────────────────────────────────────
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    <<'S2'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 2 "Demo packages installation"
variant_activate_main_env
variant_pip_build_mode

pip_install_group "G1: Jupyter ecosystem" "Jupyter kernel/extensions" ipykernel jupyterlab

variant_pip_runtime_mode
S2

# ── Stage 3/5: Jupyter kernel registration + docs (v1.1.0新功能) ──
RUN <<'S3'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 3 "Jupyter kernel + docs deployment"
variant_activate_main_env

# ── 注册自定义Jupyter内核（v1.1.0新功能）──
variant_register_jupyter_kernel \
    "example-custom" \
    "Python 3 (Example Custom)" \
    "/opt/conda/envs/main/bin/python" \
    "EXAMPLE_VARIANT=example-custom" \
    "OMP_NUM_THREADS=4"

# ── 创建并部署文档到容器内（v1.1.0新功能）──
mkdir -p /tmp/example-docs
cat > /tmp/example-docs/README.md <<'DOC'
# Example Custom Variant

This is a demo variant showcasing variant-framework v1.1.0 features:
- Custom user configuration (non-devuser)
- Shell environment standardization
- Custom Jupyter kernel registration
- Document deployment to /opt/docs/

## Usage
- Default user: ai (UID 1001)
- Jupyter kernel: "Python 3 (Example Custom)"
- Docs location: /opt/docs/example-custom/
DOC
variant_deploy_docs "/tmp/example-docs" "example-custom"
rm -rf /tmp/example-docs
S3

# ── Stage 4/5: Permissions + cleanup ───────────────────────────────
RUN <<'S4'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 4 "Permissions + cleanup"
ensure_all_permissions
cleanup_all
S4

# ── Stage 5/5: Metadata + verification ─────────────────────────────
RUN <<'S5'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 5 "Final metadata + verification"
variant_activate_main_env

variant_write_build_info "example-custom" "${BASE_TAG}" \
    "VARIANT_DESCRIPTION=Example variant demonstrating v1.1.0 features (custom user/Jupyter/shell/docs)" \
    "FRAMEWORK_VERSION=${variant_framework_version}" \
    "CUSTOM_USER=${DEVTARGET_USER}" \
    "CUSTOM_UID=${DEVTARGET_UID}" \
    "JUPYTER_KERNEL=example-custom" \
    "DOCS_LOCATION=/opt/docs/example-custom/" \
    "FEATURES_DEMO=custom-user,shell-profile,jupyter-kernel,docs-deploy"

# ── 验证 ──
verify_validation_header "Example Custom Verification"

# 1. 验证自定义用户存在
echo -n "  [VERIFY] Custom user '${DEVTARGET_USER}'... "
if id -u "${DEVTARGET_USER}" >/dev/null 2>&1; then
    echo "[OK] (uid: $(id -u "${DEVTARGET_USER}"))"
else
    echo "[FAIL]"
    exit 1
fi

# 2. 通用用户验证（v1.1.0新函数）
verify_user_access "${DEVTARGET_USER}"

# 3. 验证Jupyter内核注册（v1.1.0新函数）
verify_jupyter_kernel "example-custom"

# 4. 验证文档已部署
echo -n "  [VERIFY] Docs deployed... "
if [[ -f /opt/docs/example-custom/README.md ]]; then
    echo "[OK]"
else
    echo "[FAIL]"
    exit 1
fi

# 5. 验证PATH持久化
echo -n "  [VERIFY] PATH persisted... "
if grep -q "/opt/tools/bin" /etc/environment 2>/dev/null; then
    echo "[OK]"
else
    echo "[FAIL]"
    exit 1
fi

# 6. 验证bashrc配置
echo -n "  [VERIFY] User bashrc configured... "
if [[ -f "/home/${DEVTARGET_USER}/.bashrc" ]] && grep -q "example-custom" "/home/${DEVTARGET_USER}/.bashrc"; then
    echo "[OK]"
else
    echo "[FAIL]"
    exit 1
fi

# 7. 验证sshd配置（如果存在）
if command -v sshd >/dev/null 2>&1; then
    verify_ssh_config
fi

# 8. 验证基础服务
verify_base_services

# 9. 用户可执行Python（非函数内不用local）
echo -n "  [VERIFY] ${DEVTARGET_USER} python access... "
su - "${DEVTARGET_USER}" -c "python --version" >/dev/null 2>&1 && {
    py_ver=$(su - "${DEVTARGET_USER}" -c "python --version" 2>&1)
    echo "[OK] (${py_ver})"
} || echo "[WARN] python activation check (non-login shell expected)"

variant_log_ok "All example-custom verifications passed"

variant_timer_summary "example-custom Variant (Framework v1.1.0 Demo)"
echo ""
echo "########################################################################"
echo "# EXAMPLE-CUSTOM BUILD COMPLETE (Framework v1.1.0 demo)"
echo "# User: ${DEVTARGET_USER} | Kernel: example-custom | Docs: /opt/docs/example-custom/"
echo "########################################################################"
S5
