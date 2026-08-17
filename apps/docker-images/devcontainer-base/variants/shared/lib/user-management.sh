#!/usr/bin/env bash
# =============================================================================
# user-management.sh — 用户管理模块
#
# 提供可配置的目标用户管理能力：自定义用户名/UID/GID、用户重命名、
# sudo 权限配置、密码设置。支持从基础镜像默认的 devuser 迁移到自定义用户。
#
# 环境变量（均有合理默认值，保持向后兼容）：
#   DEVTARGET_USER - 目标用户名，默认 "devuser"
#   DEVTARGET_UID  - 目标用户 UID，默认 "1000"
#   DEVTARGET_GID  - 目标用户 GID，默认 "1000"
#   GRANT_SUDO     - 是否授予 sudo NOPASSWD 权限，默认 "yes"
#   USER_PASSWORD  - 用户密码（可选，默认不设置）
#
# 依赖：logging.sh（variant_log_* 函数）
# 不修改 shell errexit/nounset 选项
# =============================================================================

# 防止重复 source
[[ -n "${_VARIANT_USER_MANAGEMENT_LOADED:-}" ]] && return 0
_VARIANT_USER_MANAGEMENT_LOADED=1

# 默认值设置（向后兼容：默认是 devuser/1000/1000）
: "${DEVTARGET_USER:=devuser}"
: "${DEVTARGET_UID:=1000}"
: "${DEVTARGET_GID:=1000}"
: "${GRANT_SUDO:=yes}"
: "${USER_PASSWORD:=}"

# ---------------------------------------------------------------------------
# 内部辅助：查找下一个可用的 UID
# ---------------------------------------------------------------------------
_get_next_available_uid() {
    local start_uid="$1"
    local uid="$start_uid"
    while id -u "${uid}" &>/dev/null; do
        uid=$((uid + 1))
    done
    echo "${uid}"
}

# ---------------------------------------------------------------------------
# 内部辅助：查找下一个可用的 GID
# ---------------------------------------------------------------------------
_get_next_available_gid() {
    local start_gid="$1"
    local gid="$start_gid"
    while getent group "${gid}" &>/dev/null; do
        gid=$((gid + 1))
    done
    echo "${gid}"
}

# ---------------------------------------------------------------------------
# variant_create_user: 创建新用户
# 用法: variant_create_user <name> <uid> <gid> [additional_groups...]
#
# 创建用户并自动加入 docker、sudo 组以及额外指定的组。
# UID/GID 已被占用时自动查找下一个可用 ID 并输出 WARN 日志。
# ---------------------------------------------------------------------------
variant_create_user() {
    local username="$1"
    local requested_uid="$2"
    local requested_gid="$3"
    shift 3
    local extra_groups=("$@")

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CREATE USER] ${username}"
    echo "└─────────────────────────────────────────────────┘"

    local actual_uid actual_gid

    # 处理 UID 冲突
    if id -u "${requested_uid}" &>/dev/null; then
        local existing_user
        existing_user=$(id -nu "${requested_uid}" 2>/dev/null || echo "unknown")
        variant_log_info "UID ${requested_uid} is already taken by '${existing_user}', finding next available..."
        actual_uid=$(_get_next_available_uid "${requested_uid}")
        variant_log_info "Using UID ${actual_uid} instead of requested ${requested_uid}"
    else
        actual_uid="${requested_uid}"
    fi

    # 处理 GID 冲突
    if getent group "${requested_gid}" &>/dev/null; then
        local existing_group
        existing_group=$(getent group "${requested_gid}" | cut -d: -f1)
        variant_log_info "GID ${requested_gid} is already taken by '${existing_group}', finding next available..."
        actual_gid=$(_get_next_available_gid "${requested_gid}")
        variant_log_info "Using GID ${actual_gid} instead of requested ${requested_gid}"
    else
        actual_gid="${requested_gid}"
    fi

    # 创建用户组
    groupadd --gid "${actual_gid}" "${username}" || {
        variant_log_error "Failed to create group '${username}' with GID ${actual_gid}"
        return 1
    }

    # 创建用户
    local groups="sudo,docker"
    if [[ ${#extra_groups[@]} -gt 0 ]]; then
        groups="${groups},$(IFS=,; echo "${extra_groups[*]}")"
    fi

    useradd \
        --uid "${actual_uid}" \
        --gid "${username}" \
        --groups "${groups}" \
        --shell /bin/bash \
        --create-home \
        --home-dir "/home/${username}" \
        "${username}" || {
        variant_log_error "Failed to create user '${username}'"
        return 1
    }

    variant_log_ok "User '${username}' created (UID=${actual_uid}, GID=${actual_gid}, groups=${groups})"
    echo ""
}

# ---------------------------------------------------------------------------
# variant_rename_user: 重命名用户（包括组名和主目录）
# 用法: variant_rename_user <old_name> <new_name>
# ---------------------------------------------------------------------------
variant_rename_user() {
    local old_name="$1"
    local new_name="$2"

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [RENAME USER] ${old_name} → ${new_name}"
    echo "└─────────────────────────────────────────────────┘"

    # 检查旧用户是否存在
    if ! id "${old_name}" &>/dev/null; then
        variant_log_error "Old user '${old_name}' does not exist"
        return 1
    fi

    # 检查新用户是否已存在
    if id "${new_name}" &>/dev/null; then
        variant_log_error "New user '${new_name}' already exists"
        return 1
    fi

    # 重命名用户组
    groupmod -n "${new_name}" "${old_name}" || {
        variant_log_error "Failed to rename group '${old_name}' to '${new_name}'"
        return 1
    }

    # 重命名用户
    usermod -l "${new_name}" -d "/home/${new_name}" -m "${old_name}" || {
        variant_log_error "Failed to rename user '${old_name}' to '${new_name}'"
        return 1
    }

    variant_log_ok "User renamed: ${old_name} → ${new_name} (home dir moved)"
    echo ""
}

# ---------------------------------------------------------------------------
# variant_configure_sudo: 配置 sudo NOPASSWD 权限
# 用法: variant_configure_sudo <username> [yes|no]
#
# 写入 /etc/sudoers.d/<username>，权限设置为 0440。
# ---------------------------------------------------------------------------
variant_configure_sudo() {
    local username="$1"
    local grant="${2:-yes}"

    if [[ "${grant}" != "yes" && "${grant}" != "no" ]]; then
        variant_log_error "variant_configure_sudo: second argument must be 'yes' or 'no'"
        return 1
    fi

    local sudoers_file="/etc/sudoers.d/${username}"

    if [[ "${grant}" == "yes" ]]; then
        variant_log_info "Granting sudo NOPASSWD to '${username}'..."
        echo "${username} ALL=(ALL) NOPASSWD:ALL" > "${sudoers_file}"
        chmod 0440 "${sudoers_file}"
        variant_log_ok "Sudo NOPASSWD configured for '${username}'"
    else
        rm -f "${sudoers_file}"
        variant_log_info "Sudo permissions removed for '${username}'"
    fi
}

# ---------------------------------------------------------------------------
# variant_set_user_password: 设置用户密码
# 用法: variant_set_user_password <username> <password>
#
# ⚠️  安全警告：构建期设置密码会将明文密码写入镜像层历史！
#     推荐做法：
#       1. 运行时通过 docker exec 设置（不写入镜像层）
#       2. 使用 SSH 密钥登录（调用 variant_lock_user_password 禁用密码）
#       3. 仅在受控内网环境下使用构建期密码设置
# ---------------------------------------------------------------------------
variant_set_user_password() {
    local username="$1"
    local password="$2"

    variant_log_info "Setting password for user '${username}'..."
    echo "${username}:${password}" | chpasswd || {
        variant_log_error "Failed to set password for '${username}'"
        return 1
    }
    variant_log_ok "Password set for '${username}'"
}

# ---------------------------------------------------------------------------
# variant_lock_user_password: 锁定用户密码（仅允许 SSH 密钥登录）
# 用法: variant_lock_user_password <username>
#
# 这是比设置密码更安全的做法：禁用密码登录，只能通过 SSH 密钥认证。
# ---------------------------------------------------------------------------
variant_lock_user_password() {
    local username="$1"

    variant_log_info "Locking password for user '${username}' (SSH key only)..."
    passwd -l "${username}" &>/dev/null || {
        variant_log_error "Failed to lock password for '${username}'"
        return 1
    }
    variant_log_ok "Password locked for '${username}' - only SSH key auth allowed"
}

# ---------------------------------------------------------------------------
# variant_get_target_user_info: 输出最终用户信息（user:uid:gid）
# 用法: variant_get_target_user_info
#
# 在用户创建/重命名后调用，获取实际生效的用户信息。
# ---------------------------------------------------------------------------
variant_get_target_user_info() {
    local username="${DEVTARGET_USER}"
    if id "${username}" &>/dev/null; then
        echo "${username}:$(id -u "${username}"):$(id -g "${username}")"
    else
        echo "${username}:${DEVTARGET_UID}:${DEVTARGET_GID}"
    fi
}

# ---------------------------------------------------------------------------
# variant_get_target_user_group: 输出最终用户组名
# ---------------------------------------------------------------------------
variant_get_target_user_group() {
    local username="${DEVTARGET_USER}"
    if id "${username}" &>/dev/null; then
        id -gn "${username}"
    else
        echo "${username}"
    fi
}

# ---------------------------------------------------------------------------
# variant_configure_target_user: 一键配置目标用户（推荐主入口）
# 用法: variant_configure_target_user
#
# 智能处理：
#   1. 如果目标用户已存在（可能是自定义UID/GID与默认用户冲突），检查UID/GID
#   2. 如果存在同名不同UID的用户，进行重命名处理（常见场景：devuser→自定义名）
#   3. 如果目标用户不存在，创建新用户
#   4. 配置 sudo 权限（根据 GRANT_SUDO）
#   5. 如果设置了 USER_PASSWORD，设置密码
#
# 典型场景：
#   - 保持默认devuser：什么都不做（用户已存在，UID匹配）
#   - 重命名为ai：重命名devuser→ai，调整主目录
#   - 完全自定义用户：创建新用户
# ---------------------------------------------------------------------------
variant_configure_target_user() {
    local username="${DEVTARGET_USER}"
    local target_uid="${DEVTARGET_UID}"
    local target_gid="${DEVTARGET_GID}"

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CONFIGURE TARGET USER] ${username} (UID=${target_uid}, GID=${target_gid})"
    echo "└─────────────────────────────────────────────────┘"

    # 检查目标用户是否已存在
    if id "${username}" &>/dev/null; then
        local existing_uid existing_gid
        existing_uid=$(id -u "${username}")
        existing_gid=$(id -g "${username}")

        if [[ "${existing_uid}" == "${target_uid}" && "${existing_gid}" == "${target_gid}" ]]; then
            # 用户已存在且UID/GID匹配，无需创建
            variant_log_info "User '${username}' already exists with matching UID/GID, skipping creation"
        else
            # 存在同名用户但UID/GID不匹配，调整UID/GID
            variant_log_info "User '${username}' exists with UID=${existing_uid} (expected ${target_uid}), adjusting..."
            usermod -u "${target_uid}" "${username}"
            groupmod -g "${target_gid}" "${username}"
            variant_log_ok "User '${username}' UID/GID adjusted to ${target_uid}/${target_gid}"
        fi
    else
        # 检查是否需要重命名现有默认用户
        if [[ "${username}" != "devuser" ]] && id devuser &>/dev/null; then
            # 默认用户 devuser 存在，目标用户不同 → 重命名
            variant_rename_user "devuser" "${username}"
        else
            # 没有默认用户或用户名相同，创建新用户
            variant_create_user "${username}" "${target_uid}" "${target_gid}"
        fi
    fi

    # 配置 sudo 权限
    variant_configure_sudo "${username}" "${GRANT_SUDO}"

    # 处理密码
    if [[ -n "${USER_PASSWORD}" ]]; then
        variant_set_user_password "${username}" "${USER_PASSWORD}"
    fi

    # 更新全局变量为实际值（供后续模块使用）
    local actual_info
    actual_info=$(variant_get_target_user_info)
    DEVTARGET_USER=$(echo "${actual_info}" | cut -d: -f1)
    # 注意：不更新 DEVTARGET_UID/GID，因为可能有冲突调整

    local final_user final_uid final_gid
    final_user=$(echo "${actual_info}" | cut -d: -f1)
    final_uid=$(echo "${actual_info}" | cut -d: -f2)
    final_gid=$(echo "${actual_info}" | cut -d: -f3)

    echo ""
    variant_log_ok "Target user configured: ${final_user} (UID=${final_uid}, GID=${final_gid})"
    echo ""
}
