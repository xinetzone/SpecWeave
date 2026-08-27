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
# 框架版本：1.1.0
# 包含模块（按依赖顺序）：
#   logging         - 结构化日志（text+JSON双格式）
#   timer           - 构建阶段计时
#   user-management - 目标用户管理（自定义用户名/UID/GID/重命名/sudo）
#   mirror          - 镜像源配置（conda/pip/APT）
#   shell-profile   - Shell环境配置（umask/bashrc/PATH持久化/SSH）
#   install-helpers - conda/pip分组安装辅助（含PIP_USER模式切换）
#   jupyter-kernel  - Jupyter自定义内核注册
#   docs            - 文档部署到/opt/docs/
#   ft-guards       - free-threading完整性守卫
#   cleanup         - 统一清理（安全排除计时器目录）
#   build-info      - 构建元数据写入
#   verify          - 基础验证函数（sshd/用户/内核/语法检查）
#   permissions     - 权限设置函数
#
# v1.1.0 changelog:
#   + 新增 user-management 模块：自定义用户创建/重命名/UID冲突处理
#   + 新增 shell-profile 模块：umask/bashrc幂等追加/PATH持久化/SSH环境
#   + 新增 jupyter-kernel 模块：自定义Jupyter内核注册
#   + 新增 docs 模块：文档容器内部署
#   + install-helpers: 新增 PIP_USER 构建/运行时模式切换函数
#   + verify: 新增通用用户验证、sshd配置语法检查（旧函数保留wrapper）
#   + permissions: 新增通用用户bashrc权限设置（旧函数保留wrapper）
#   + build-info: 新增 TARGET_USER/TARGET_UID 元数据字段
#   + 默认值保持100%向后兼容（DEVTARGET_USER=devuser, UID/GID=1000）
# =============================================================================

# 防止重复source
[[ -n "${_VARIANT_FRAMEWORK_LOADED:-}" ]] && return 0
_VARIANT_FRAMEWORK_LOADED=1

# 框架版本号
variant_framework_version="1.1.0"

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
# 注意：user-management必须在mirror/permissions之前（它们依赖DEVTARGET_USER默认值）
# ---------------------------------------------------------------------------
_VARIANT_MODULES=(
    "logging"
    "timer"
    "user-management"
    "mirror"
    "shell-profile"
    "install-helpers"
    "jupyter-kernel"
    "docs"
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
