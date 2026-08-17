#!/usr/bin/env bash
# =============================================================================
# shell-profile.sh — Shell 环境配置模块
#
# 提供标准化的 Shell 环境配置能力：umask、bashrc 幂等追加、PATH 持久化、
# SSH 环境变量配置。所有追加操作使用标记包裹保证幂等性。
#
# 幂等性标记：
#   # >>> variant-framework >>>
#   ... content ...
#   # <<< variant-framework <<<
#
# 依赖：logging.sh（variant_log_* 函数）
# 依赖：user-management.sh（DEVTARGET_USER 变量）
# 不修改 shell errexit/nounset 选项
# =============================================================================

# 防止重复 source
[[ -n "${_VARIANT_SHELL_PROFILE_LOADED:-}" ]] && return 0
_VARIANT_SHELL_PROFILE_LOADED=1

# 幂等性标记
_VARIANT_MARKER_START="# >>> variant-framework >>>"
_VARIANT_MARKER_END="# <<< variant-framework <<<"

# ---------------------------------------------------------------------------
# 内部辅助：幂等追加内容到文件
# 用法: _idempotent_append <file> <content>
#
# 如果文件中已有 variant-framework 标记，先删除旧标记块再追加新内容；
# 否则直接追加。自动创建不存在的文件。
# ---------------------------------------------------------------------------
_idempotent_append() {
    local file="$1"
    local content="$2"

    # 确保文件存在
    touch "${file}"

    # 移除已存在的标记块（如果有）
    if grep -q "${_VARIANT_MARKER_START}" "${file}" 2>/dev/null; then
        local tmpfile
        tmpfile=$(mktemp)
        sed "/${_VARIANT_MARKER_START}/,/${_VARIANT_MARKER_END}/d" "${file}" > "${tmpfile}"
        # 清理可能产生的连续空行
        cat -s "${tmpfile}" > "${file}"
        rm -f "${tmpfile}"
        variant_log_info "Removed previous variant-framework block from ${file}"
    fi

    # 追加新内容（带标记）
    {
        echo ""
        echo "${_VARIANT_MARKER_START}"
        echo -e "${content}"
        echo "${_VARIANT_MARKER_END}"
    } >> "${file}"
}

# ---------------------------------------------------------------------------
# variant_configure_umask: 配置全局 umask
# 用法: variant_configure_umask <umask_value>
#
# 写入4个位置保证所有 Shell 场景生效：
#   1. /etc/profile（登录Shell）
#   2. /etc/bash.bashrc（交互式非登录Shell）
#   3. /root/.bashrc（root用户）
#   4. /home/<user>/.bashrc（目标用户，默认 DEVTARGET_USER）
#
# 默认 umask 0022（文件644/目录755）
# ---------------------------------------------------------------------------
variant_configure_umask() {
    local umask_val="${1:-0022}"

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CONFIGURE UMASK] ${umask_val}"
    echo "└─────────────────────────────────────────────────┘"

    local umask_line="umask ${umask_val}"

    # /etc/profile
    _idempotent_append "/etc/profile" "${umask_line}"
    variant_log_info "Updated /etc/profile with umask ${umask_val}"

    # /etc/bash.bashrc
    _idempotent_append "/etc/bash.bashrc" "${umask_line}"
    variant_log_info "Updated /etc/bash.bashrc with umask ${umask_val}"

    # root .bashrc
    mkdir -p /root
    _idempotent_append "/root/.bashrc" "${umask_line}"
    variant_log_info "Updated /root/.bashrc with umask ${umask_val}"

    # 目标用户 .bashrc
    local target_user="${DEVTARGET_USER:-devuser}"
    local user_home="/home/${target_user}"
    if [[ -d "${user_home}" ]] || id "${target_user}" &>/dev/null; then
        mkdir -p "${user_home}"
        _idempotent_append "${user_home}/.bashrc" "${umask_line}"
        chown "${target_user}:${target_user}" "${user_home}/.bashrc" 2>/dev/null || true
        variant_log_info "Updated ${user_home}/.bashrc with umask ${umask_val}"
    fi

    # 设置当前会话 umask
    umask "${umask_val}"

    variant_log_ok "umask ${umask_val} configured globally"
    echo ""
}

# ---------------------------------------------------------------------------
# variant_append_user_bashrc: 追加内容到目标用户 bashrc（幂等）
# 用法: variant_append_user_bashrc <content> [username]
# ---------------------------------------------------------------------------
variant_append_user_bashrc() {
    local content="$1"
    local username="${2:-${DEVTARGET_USER:-devuser}}"
    local user_home="/home/${username}"

    mkdir -p "${user_home}"
    _idempotent_append "${user_home}/.bashrc" "${content}"
    chown "${username}:${username}" "${user_home}/.bashrc" 2>/dev/null || true
    variant_log_info "Appended to ${user_home}/.bashrc (idempotent)"
}

# ---------------------------------------------------------------------------
# variant_append_root_bashrc: 追加内容到 root bashrc（幂等）
# 用法: variant_append_root_bashrc <content>
# ---------------------------------------------------------------------------
variant_append_root_bashrc() {
    local content="$1"
    mkdir -p /root
    _idempotent_append "/root/.bashrc" "${content}"
    variant_log_info "Appended to /root/.bashrc (idempotent)"
}

# ---------------------------------------------------------------------------
# variant_persist_path: 持久化 PATH 条目到 /etc/environment（幂等）
# 用法: variant_persist_path <path_entry> [position]
#
# position: prepend（默认，高优先级，插入到PATH开头）或 append（追加到末尾）
# ---------------------------------------------------------------------------
variant_persist_path() {
    local path_entry="$1"
    local position="${2:-prepend}"

    local env_file="/etc/environment"

    # 读取当前PATH
    local current_path=""
    if [[ -f "${env_file}" ]] && grep -q "^PATH=" "${env_file}"; then
        current_path=$(grep "^PATH=" "${env_file}" | sed 's/^PATH=//;s/"//g')
    else
        current_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    fi

    # 检查是否已存在
    if echo ":${current_path}:" | tr ':' '\n' | grep -qx "${path_entry}"; then
        variant_log_info "PATH entry '${path_entry}' already exists, skipping"
        return 0
    fi

    local new_path
    if [[ "${position}" == "prepend" ]]; then
        new_path="${path_entry}:${current_path}"
    else
        new_path="${current_path}:${path_entry}"
    fi

    # 更新 /etc/environment
    if [[ -f "${env_file}" ]]; then
        if grep -q "^PATH=" "${env_file}"; then
            sed -i "s|^PATH=.*|PATH=\"${new_path}\"|" "${env_file}"
        else
            echo "PATH=\"${new_path}\"" >> "${env_file}"
        fi
    else
        echo "PATH=\"${new_path}\"" > "${env_file}"
    fi

    # 同时更新当前会话 PATH
    export PATH="${new_path}"

    variant_log_ok "PATH ${position}ed: ${path_entry}"
}

# ---------------------------------------------------------------------------
# variant_configure_ssh_env: 配置 SSH ~/.ssh/environment 文件
# 用法: variant_configure_ssh_env <username> [env_vars...]
#
# env_vars 格式: KEY=VALUE（多个参数）
# 自动设置文件权限为 600，所有者为目标用户。
# ---------------------------------------------------------------------------
variant_configure_ssh_env() {
    local username="$1"
    shift
    local env_vars=("$@")

    local user_home="/home/${username}"
    local ssh_dir="${user_home}/.ssh"
    local env_file="${ssh_dir}/environment"

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CONFIGURE SSH ENV] ${username}"
    echo "└─────────────────────────────────────────────────┘"

    mkdir -p "${ssh_dir}"
    chmod 700 "${ssh_dir}"

    # 写入环境变量
    : > "${env_file}"
    for var in "${env_vars[@]}"; do
        echo "${var}" >> "${env_file}"
    done

    chmod 600 "${env_file}"
    chown "${username}:${username}" "${ssh_dir}" "${env_file}" 2>/dev/null || true

    # 启用 SSH PermitUserEnvironment（如未启用）
    local sshd_config="/etc/ssh/sshd_config"
    if [[ -f "${sshd_config}" ]]; then
        if ! grep -q "^PermitUserEnvironment" "${sshd_config}"; then
            echo "PermitUserEnvironment yes" >> "${sshd_config}"
            variant_log_info "Enabled PermitUserEnvironment in sshd_config"
        fi
    fi

    variant_log_ok "SSH environment configured for '${username}' with ${#env_vars[@]} variables"
    echo ""
}

# ---------------------------------------------------------------------------
# variant_configure_shell_profile: 一键配置标准 Shell 环境（推荐主入口）
# 用法: variant_configure_shell_profile [umask_value]
#
# 配置项：
#   1. umask（默认 0022）
#   2. 确保 .bashrc 存在且权限正确
# ---------------------------------------------------------------------------
variant_configure_shell_profile() {
    local umask_val="${1:-0022}"

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CONFIGURE SHELL PROFILE]"
    echo "│ umask: ${umask_val}"
    echo "└─────────────────────────────────────────────────┘"

    variant_configure_umask "${umask_val}"

    variant_log_ok "Shell profile configured"
    echo ""
}
