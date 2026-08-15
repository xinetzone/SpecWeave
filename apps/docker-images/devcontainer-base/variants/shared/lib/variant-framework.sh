#!/usr/bin/env bash
# =============================================================================
# variant-framework.sh — devcontainer变体构建框架主入口
#
# 用法（在Dockerfile RUN heredoc开头）：
#   source /usr/local/share/variant-framework/variant-framework.sh
#
# 环境变量：
#   VARIANT_DEBUG=1  - 启用set -x调试输出
#   VARIANT_FRAMEWORK_DIR - 自定义框架目录（默认同目录下）
#
# 框架版本：1.0.0
# 包含模块（按依赖顺序）：
#   logging     - 结构化日志（text+JSON双格式）
#   timer       - 构建阶段计时
#   mirror      - 镜像源配置（conda/pip/APT）
#   install-helpers - conda/pip分组安装辅助
#   ft-guards   - free-threading完整性守卫
#   cleanup     - 统一清理（安全排除计时器目录）
#   build-info  - 构建元数据写入
#   verify      - 基础验证函数
#   permissions - 权限设置函数
# =============================================================================

# 防止重复source
[[ -n "${_VARIANT_FRAMEWORK_LOADED:-}" ]] && return 0
_VARIANT_FRAMEWORK_LOADED=1

# 框架版本号
variant_framework_version="1.0.0"

# ---------------------------------------------------------------------------
# 获取框架目录（支持自定义VARIANT_FRAMEWORK_DIR环境变量）
# ---------------------------------------------------------------------------
if [[ -n "${VARIANT_FRAMEWORK_DIR:-}" ]]; then
    _VARIANT_FRAMEWORK_DIR="${VARIANT_FRAMEWORK_DIR}"
else
    _VARIANT_FRAMEWORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# ---------------------------------------------------------------------------
# VARIANT_DEBUG模式：启用set -x调试输出（不修改其他shell选项）
# ---------------------------------------------------------------------------
_VARIANT_DEBUG_OLD_SETX=""
if [[ "${VARIANT_DEBUG:-0}" == "1" ]]; then
    echo "[FRAMEWORK] VARIANT_DEBUG=1 - enabling set -x trace"
    _VARIANT_DEBUG_OLD_SETX="$-"
    set -x
fi

# ---------------------------------------------------------------------------
# 按依赖顺序source所有模块
# ---------------------------------------------------------------------------
_VARIANT_MODULES=(
    "logging"
    "timer"
    "mirror"
    "install-helpers"
    "ft-guards"
    "cleanup"
    "build-info"
    "verify"
    "permissions"
)

for _module in "${_VARIANT_MODULES[@]}"; do
    _module_path="${_VARIANT_FRAMEWORK_DIR}/${_module}.sh"
    if [[ -f "${_module_path}" ]]; then
        # shellcheck source=/dev/null
        source "${_module_path}"
    else
        echo "[FRAMEWORK][ERROR] Required module not found: ${_module_path}" >&2
        exit 1
    fi
done

_VARIANT_MODULE_COUNT=${#_VARIANT_MODULES[@]}

# ---------------------------------------------------------------------------
# 清理临时变量
# ---------------------------------------------------------------------------
unset _module _module_path _VARIANT_MODULES _VARIANT_DEBUG_OLD_SETX

# ---------------------------------------------------------------------------
# 输出框架加载信息
# ---------------------------------------------------------------------------
if [[ "${VARIANT_DEBUG:-0}" == "1" ]] || [[ "${VARIANT_FRAMEWORK_VERBOSE:-0}" == "1" ]]; then
    echo "[FRAMEWORK] devcontainer variant framework v${variant_framework_version} loaded successfully"
    echo "[FRAMEWORK] Framework directory: ${_VARIANT_FRAMEWORK_DIR}"
    echo "[FRAMEWORK] Loaded ${_VARIANT_MODULE_COUNT} modules"
fi

unset _VARIANT_MODULE_COUNT
