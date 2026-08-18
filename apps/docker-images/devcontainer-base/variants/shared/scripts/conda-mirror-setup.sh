#!/usr/bin/env bash
# =============================================================================
# conda-mirror-setup.sh — 共享 conda + pip + APT 镜像源配置脚本
#
# 版本：v2.0（基于mirror.sh框架模块重构，保持100%向后兼容）
#
# 用途：根据 CONDA_MIRROR / PIP_MIRROR / APT_MIRROR 环境变量统一配置：
#   1. 写入 ${CONDA_DIR}/.condarc（系统级 conda 频道，含libmamba性能参数）
#   2. 写入 root 和 devuser 的 pip.conf
#   3. 配置 conda base 环境的 pip 镜像
#   4. 可选配置APT镜像源
#
# 用法（在 Dockerfile RUN 中调用）：
#   COPY shared/scripts/conda-mirror-setup.sh /usr/local/bin/
#   COPY shared/lib/ /usr/local/share/variant-framework/
#   RUN CONDA_DIR=/opt/conda CONDA_MIRROR=tuna PIP_MIRROR=aliyun \
#       /usr/local/bin/conda-mirror-setup.sh
#
# 依赖环境变量（全部可选，有默认值）：
#   CONDA_DIR      conda 安装根目录（默认 /opt/conda）
#   CONDA_MIRROR   official | tuna | aliyun | bfsu （默认 official）
#   PIP_MIRROR     official | aliyun | tuna （默认 official）
#   APT_MIRROR     official | tuna | aliyun （默认 official，为空则跳过APT配置）
#   DEVTARGET_USER 默认 pip 配置的用户（默认 devuser）
#
# 向后兼容性说明：
#   - 命令行参数和环境变量接口与v1完全一致
#   - 新增bfsu/aliyun conda源支持
#   - .condarc自动包含libmamba solver和性能参数（repodata_threads/execute_threads/超时/重试）
#   - 可独立执行，内部自动source框架模块（mirror.sh+logging.sh）
#   - 如果已在框架上下文中（variant_configure_mirrors已定义），直接复用
# =============================================================================

set -euo pipefail

CONDA_DIR="${CONDA_DIR:-/opt/conda}"
CONDA_MIRROR="${CONDA_MIRROR:-official}"
PIP_MIRROR="${PIP_MIRROR:-official}"
APT_MIRROR="${APT_MIRROR:-official}"
DEVTARGET_USER="${DEVTARGET_USER:-devuser}"

# ---------------------------------------------------------------------------
# 自动检测框架模块位置并source（独立执行模式）
# 如果函数已定义（在框架上下文中），跳过source
# ---------------------------------------------------------------------------
if ! declare -F variant_configure_mirrors >/dev/null 2>&1; then
    # 尝试多个可能的框架目录位置
    _SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    _FRAMEWORK_DIRS=(
        "${_SCRIPT_DIR}/../lib"                                    # scripts/../lib
        "/usr/local/share/variant-framework"                       # Dockerfile COPY目标
        "${CONDA_DIR}/../variants/shared/lib"                      # 备选路径
    )

    _SOURCED=0
    for _dir in "${_FRAMEWORK_DIRS[@]}"; do
        if [[ -f "${_dir}/logging.sh" ]] && [[ -f "${_dir}/mirror.sh" ]]; then
            # shellcheck source=/dev/null
            source "${_dir}/logging.sh"
            # shellcheck source=/dev/null
            source "${_dir}/mirror.sh"
            _SOURCED=1
            break
        fi
    done

    if [[ ${_SOURCED} -eq 0 ]]; then
        echo "[WARN] Framework modules not found, falling back to standalone mode (limited features)"
        # 降级：定义最小化日志函数
        variant_log_info()  { echo "[INFO] $*"; }
        variant_log_ok()    { echo "[OK] $*"; }
    fi
fi

echo ""
echo "########################################################################"
echo "# [SHARED] Configure Mirror Sources (conda + pip + apt)"
echo "# CONDA_MIRROR=${CONDA_MIRROR}, PIP_MIRROR=${PIP_MIRROR}, APT_MIRROR=${APT_MIRROR}"
echo "# CONDA_DIR=${CONDA_DIR}"
echo "########################################################################"
echo ""

# ---------------------------------------------------------------------------
# 调用框架的统一镜像源配置函数
# ---------------------------------------------------------------------------
variant_configure_mirrors

# ---------------------------------------------------------------------------
# 向后兼容：配置conda base环境pip镜像（mirror.sh不包含此步骤）
# ---------------------------------------------------------------------------
echo "[ACTION] Setting pip config for conda base environment..."
case "${PIP_MIRROR}" in
    aliyun)
        "${CONDA_DIR}/bin/pip" config set global.index-url https://mirrors.aliyun.com/pypi/simple/
        "${CONDA_DIR}/bin/pip" config set global.trusted-host mirrors.aliyun.com
        ;;
    tuna)
        "${CONDA_DIR}/bin/pip" config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
        "${CONDA_DIR}/bin/pip" config set global.trusted-host pypi.tuna.tsinghua.edu.cn
        ;;
    bfsu)
        "${CONDA_DIR}/bin/pip" config set global.index-url https://mirrors.bfsu.edu.cn/pypi/simple/
        "${CONDA_DIR}/bin/pip" config set global.trusted-host mirrors.bfsu.edu.cn
        ;;
    *)
        # official - no extra config needed
        ;;
esac
echo "[OK] Conda base pip configured"

# ---------------------------------------------------------------------------
# 验证：输出conda配置
# ---------------------------------------------------------------------------
"${CONDA_DIR}/bin/conda" config --show-sources
echo ""
echo '[OK] Shared mirror configuration complete'
