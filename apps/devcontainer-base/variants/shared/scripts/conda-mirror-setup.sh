#!/bin/bash
# conda-mirror-setup.sh — 共享 conda + pip 镜像源配置脚本
#
# 用途：根据 CONDA_MIRROR / PIP_MIRROR 环境变量统一配置：
#   1. 写入 ${CONDA_DIR}/.condarc（系统级 conda 频道）
#   2. 写入 root 和 devuser 的 pip.conf
#   3. 配置 conda base 环境的 pip 镜像
#
# 适用场景：conda / conda-llvm 等所有继承 Miniconda 环境的变体，
#           避免在各 Dockerfile 中重复相同的镜像源配置逻辑。
#
# 用法（在 Dockerfile RUN 中调用）：
#   COPY shared/scripts/conda-mirror-setup.sh /usr/local/bin/
#   RUN CONDA_DIR=/opt/conda CONDA_MIRROR=tuna PIP_MIRROR=aliyun \
#       /usr/local/bin/conda-mirror-setup.sh
#
# 依赖环境变量：
#   CONDA_DIR      conda 安装根目录（默认 /opt/conda）
#   CONDA_MIRROR   official | tuna （默认 official）
#   PIP_MIRROR     official | aliyun | tuna （默认 official）
#   DEVTARGET_USER 默认 pip 配置的用户（默认 devuser）

set -euo pipefail

CONDA_DIR="${CONDA_DIR:-/opt/conda}"
CONDA_MIRROR="${CONDA_MIRROR:-official}"
PIP_MIRROR="${PIP_MIRROR:-official}"
DEVTARGET_USER="${DEVTARGET_USER:-devuser}"

echo ""
echo "########################################################################"
echo "# [SHARED] Configure Mirror Sources (conda + pip)"
echo "# CONDA_MIRROR=${CONDA_MIRROR}, PIP_MIRROR=${PIP_MIRROR}, CONDA_DIR=${CONDA_DIR}"
echo "########################################################################"
echo ""

# ── 1. 写入系统级 .condarc ──────────────────────────────────────────────────
echo "[ACTION] Writing ${CONDA_DIR}/.condarc (system-level)..."
if [ "${CONDA_MIRROR}" = "tuna" ]; then
    echo "[INFO] Configuring conda for Tsinghua TUNA mirror"
    printf '%s\n' \
        'channels:' \
        '  - conda-forge' \
        '  - defaults' \
        'show_channel_urls: true' \
        'default_channels:' \
        '  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main' \
        '  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r' \
        'custom_channels:' \
        '  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud' \
        'ssl_verify: true' \
        'auto_activate_base: false' \
        > "${CONDA_DIR}/.condarc"
else
    echo "[INFO] Configuring conda for official/default channels"
    printf '%s\n' \
        'channels:' \
        '  - conda-forge' \
        '  - defaults' \
        'show_channel_urls: true' \
        'ssl_verify: true' \
        'auto_activate_base: false' \
        > "${CONDA_DIR}/.condarc"
fi
echo "[OK] .condarc written:"
cat "${CONDA_DIR}/.condarc"
echo ""

# ── 2. 配置 pip 镜像（root + devuser） ──────────────────────────────────────
echo "[ACTION] Configuring pip mirrors..."
mkdir -p /root/.config/pip /home/${DEVTARGET_USER}/.config/pip
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
printf '%s\n' \
    '[global]' \
    "index-url = ${PIP_INDEX_URL}" \
    "retries = 5" \
    "timeout = 60" \
    > /root/.config/pip/pip.conf
if [ -n "${PIP_TRUSTED_HOST}" ]; then
    printf '%s\n' "trusted-host = ${PIP_TRUSTED_HOST}" >> /root/.config/pip/pip.conf
fi
cp /root/.config/pip/pip.conf /home/${DEVTARGET_USER}/.config/pip/pip.conf
echo "[OK] pip.conf written for root and ${DEVTARGET_USER}:"
cat /root/.config/pip/pip.conf
echo ""

# ── 3. 配置 conda base 环境 pip 镜像 ────────────────────────────────────────
echo "[ACTION] Setting pip config for conda base environment..."
if [ "${PIP_MIRROR}" = "aliyun" ]; then
    "${CONDA_DIR}/bin/pip" config set global.index-url https://mirrors.aliyun.com/pypi/simple/
    "${CONDA_DIR}/bin/pip" config set global.trusted-host mirrors.aliyun.com
elif [ "${PIP_MIRROR}" = "tuna" ]; then
    "${CONDA_DIR}/bin/pip" config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
    "${CONDA_DIR}/bin/pip" config set global.trusted-host pypi.tuna.tsinghua.edu.cn
fi
echo "[OK] Conda base pip configured"
"${CONDA_DIR}/bin/conda" config --show-sources
echo ""
echo '[OK] Shared mirror configuration complete'
