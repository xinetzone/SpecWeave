#!/bin/bash
set -euo pipefail

if [ "${DEBUG:-0}" = "1" ]; then
    set -x
fi

if [ -n "${ENABLE_SUDO_NOPASSWD:-}" ] && [ "${GRANT_SUDO:-no}" = "no" ]; then
    if [ "${ENABLE_SUDO_NOPASSWD}" = "1" ] || [ "${ENABLE_SUDO_NOPASSWD}" = "yes" ] || [ "${ENABLE_SUDO_NOPASSWD}" = "true" ]; then
        export GRANT_SUDO=yes
    fi
fi

if [ -n "${JUPYTER_CORS_ORIGIN:-}" ] && [ -z "${JUPYTER_ALLOW_ORIGIN:-}" ]; then
    export JUPYTER_ALLOW_ORIGIN="${JUPYTER_CORS_ORIGIN}"
fi

DOCKER_DOD_MODE=0
ENABLE_DOCKER_ORIG="${ENABLE_DOCKER:-yes}"

log_info()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO]  $*" >&2; }
log_warn()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN]  $*" >&2; }
log_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $*" >&2; }
log_debug() {
    if [ "${FIXUID_DEBUG:-0}" = "1" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [DEBUG] $*" >&2
    fi
}

_is_docker_named_volume() {
    local dir="$1"
    local mount_src
    if [ ! -f /proc/mounts ]; then
        return 1
    fi
    mount_src=$(awk -v dir="$dir" '$2 == dir {print $1; exit}' /proc/mounts 2>/dev/null || true)
    case "$mount_src" in
        /var/lib/docker/volumes/*/_data) return 0 ;;
        *) return 1 ;;
    esac
}

# Check if a directory is a bind mount (mounted from host, not a named volume or internal dir)
_is_bind_mount() {
    local dir="$1"
    local mount_src
    if [ ! -f /proc/mounts ]; then
        return 1
    fi
    # Check if dir is listed as a mount point in /proc/mounts
    mount_src=$(awk -v dir="$dir" '$2 == dir {print $1; exit}' /proc/mounts 2>/dev/null || true)
    if [ -z "$mount_src" ]; then
        return 1
    fi
    # Named volumes are not bind mounts
    case "$mount_src" in
        /var/lib/docker/volumes/*/_data) return 1 ;;
        overlay|proc|sysfs|tmpfs|devpts|mqueue|cgroup*|nsfs) return 1 ;;
        *) return 0 ;;
    esac
}

_is_sensitive_system_dir() {
    local dir="$1"
    case "$dir" in
        /|/home|/home/*|/etc|/etc/*|/usr|/usr/*|/bin|/sbin|/dev|/proc|/sys|/var|/root|/boot)
            return 0 ;;
        *)
            return 1 ;;
    esac
}

resolve_jupyter_root_dir() {
    local root_dir="${JUPYTER_ROOT_DIR:-}"
    local chown_mode="${JUPYTER_ROOT_CHOWN:-auto}"
    if [ -z "$root_dir" ]; then
        local cwd="$(pwd)"
        if [ "$cwd" != "/" ] && [ -d "$cwd" ]; then
            root_dir="$cwd"
            log_info "Auto-detected working directory as Jupyter root: $root_dir (from Docker -w or current dir)"
        else
            root_dir="/workspace"
            log_info "Using default Jupyter root: $root_dir"
        fi
    else
        log_info "Using Jupyter root from JUPYTER_ROOT_DIR env: $root_dir"
    fi
    if [ ! -d "$root_dir" ]; then
        log_warn "Jupyter root dir '$root_dir' does not exist, creating it..."
        mkdir -p "$root_dir" 2>/dev/null || {
            log_error "Failed to create $root_dir, falling back to /workspace"
            root_dir="/workspace"
            chown_mode="named-only"
            mkdir -p "$root_dir"
        }
    fi
    if _is_sensitive_system_dir "$root_dir"; then
        log_error "========================================"
        log_error "⚠️  SECURITY WARNING: Jupyter root dir '$root_dir' is a system directory!"
        log_error "    chown will be FORCIBLY SKIPPED to prevent damaging host system permissions."
        log_error "    Please use a dedicated data directory instead (e.g. /workspace, /data, /media/...)."
        log_error "========================================"
        chown_mode="no"
        JUPYTER_ROOT_SENSITIVE=1
    fi
    if [ "$root_dir" = "/workspace" ]; then
        :
    elif [ "$chown_mode" = "auto" ]; then
        if ! _is_docker_named_volume "$root_dir" 2>/dev/null; then
            chown_mode="no"
            JUPYTER_ROOT_BIND_MOUNT=1
        fi
    fi
    JUPYTER_ROOT_DIR="$root_dir"
    JUPYTER_ROOT_CHOWN="$chown_mode"
    JUPYTER_ROOT_SENSITIVE="${JUPYTER_ROOT_SENSITIVE:-0}"
    JUPYTER_ROOT_BIND_MOUNT="${JUPYTER_ROOT_BIND_MOUNT:-0}"
    export JUPYTER_ROOT_DIR JUPYTER_ROOT_CHOWN JUPYTER_ROOT_SENSITIVE JUPYTER_ROOT_BIND_MOUNT
}

print_banner() {
    echo "" >&2
    echo "============================================================" >&2
    echo "  DevContainer Base starting..." >&2
    echo "  Time: $(date)" >&2
    echo "  Host: $(hostname)" >&2
    echo "============================================================" >&2
    echo "" >&2
}

diagnose_system() {
    log_info "========== System Diagnostics =========="
    log_info "OS: $(grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '"')"
    log_info "Kernel: $(uname -r)"
    log_info "Arch: $(uname -m)"
    log_info "Timezone: ${TZ:-not set} (now: $(date))"
    log_info "Locale: ${LANG:-not set}"
    log_info "User: $(id)"
    log_info "Non-root user: ${NON_ROOT_USER:-devuser}"

    if [ -f /sys/fs/cgroup/cgroup.controllers ]; then
        log_info "cgroup: v2"
    else
        log_info "cgroup: v1"
    fi

    log_info "Docker: $(docker --version 2>/dev/null || echo 'not found')"
    log_info "Podman: $(podman --version 2>/dev/null || echo 'not found')"

    log_info "Enabled services:"
    log_info "  SSH:      ${ENABLE_SSH:-yes}"
    log_info "  Docker:   ${ENABLE_DOCKER:-yes}"
    log_info "  Podman:   ${ENABLE_PODMAN:-no}"
    log_info "  Jupyter:  ${ENABLE_JUPYTER:-yes}"
    log_info "  Sudo:     ${GRANT_SUDO:-no}"

    if [ -f /etc/devcontainer-build-info ]; then
        log_info "Build info:"
        while IFS= read -r line; do log_info "  $line"; done < /etc/devcontainer-build-info
    fi
    log_info "========================================"
    echo "" >&2
}

set_user_password() {
    local target_user="$1"
    local target_pass="$2"
    local hashed
    if [ -x /usr/bin/openssl ]; then
        hashed=$(/usr/bin/openssl passwd -6 "${target_pass}")
    else
        # Fallback to chpasswd if openssl not available
        echo "${target_user}:${target_pass}" | chpasswd
        return $?
    fi
    usermod -p "${hashed}" "${target_user}"
}

# -----------------------------------------------------------------------------
# adjust_user_uid_gid: 运行时动态调整 devuser 的 UID/GID 以匹配宿主机用户
# 这是解决 Docker bind mount 跨 UID 权限问题的核心函数
# 执行顺序：必须在 setup_passwords/setup_workspace 之前，服务启动之后
# -----------------------------------------------------------------------------
adjust_user_uid_gid() {
    local user="${NON_ROOT_USER:-devuser}"
    local target_uid="${LOCAL_USER_ID:-}"
    local target_gid="${LOCAL_GROUP_ID:-}"
    local default_uid=1000
    local default_gid=1000
    local user_grp ws_uid ws_gid occupied_by occupied_grp new_uid_for_existing new_gid_for_existing _d _is_mount final_uid final_gid
    local uid_source="default"  # 追踪UID来源: env / auto / default / blocked

    log_info "[FixUID] Adjusting user UID/GID for ${user}..."

    # 确保用户存在（如果不存在则先创建）
    if ! getent passwd "${user}" >/dev/null 2>&1; then
        log_info "[FixUID] User '${user}' does not exist, creating first with default UID=${default_uid}..."
        groupadd -f docker
        local _create_uid="${default_uid}"
        # 如果 default_uid 被占用，主动寻找下一个可用 UID（>=1000）
        if getent passwd "${default_uid}" >/dev/null 2>&1; then
            _create_uid=$((default_uid + 1))
            while getent passwd "${_create_uid}" >/dev/null 2>&1; do
                _create_uid=$((_create_uid + 1))
            done
            log_warn "[FixUID] Default UID ${default_uid} occupied, creating user with UID=${_create_uid} instead"
        fi
        local _create_gid="${_create_uid}"
        if ! getent group "${_create_gid}" >/dev/null 2>&1; then
            groupadd -g "${_create_gid}" "${user}"
        fi
        useradd -m -s /bin/bash -u "${_create_uid}" -g "${_create_gid}" -G docker,sudo "${user}"
        mkdir -p "/home/${user}/.ssh" "/home/${user}/.jupyter/jupyter_server_config.d"
        chmod 700 "/home/${user}/.ssh" 2>/dev/null || true
        echo "${user}:100000:65536" > /etc/subuid
        echo "${user}:100000:65536" > /etc/subgid
        if [ ! -f "/home/${user}/.bashrc" ] || ! grep -q "conda-init.sh" "/home/${user}/.bashrc" 2>/dev/null; then
            echo "source /etc/profile.d/conda-init.sh" >> "/home/${user}/.bashrc"
        fi
    fi

    local current_uid current_gid
    current_uid=$(id -u "${user}")
    current_gid=$(id -g "${user}")
    log_debug "[FixUID] Current state: ${user} UID=${current_uid} GID=${current_gid}"
    user_grp=$(id -gn "${user}" 2>/dev/null || echo "${user}")

    # 智能自动检测：如果未设置 LOCAL_USER_ID，尝试从 /workspace 目录属主检测
    if [ -n "${LOCAL_USER_ID:-}" ]; then
        uid_source="env"  # 显式通过环境变量指定
    fi
    if [ -z "${target_uid}" ]; then
        log_debug "[FixUID] LOCAL_USER_ID not set, attempting auto-detection from /workspace..."
        if [ -d "/workspace" ]; then
            ws_uid=$(stat -c '%u' /workspace 2>/dev/null || echo "")
            ws_gid=$(stat -c '%g' /workspace 2>/dev/null || echo "")
            log_debug "[FixUID] /workspace owner: UID=${ws_uid} GID=${ws_gid}"
            # 仅当检测到有效且非默认的 UID 时才自动使用（非 root=0，非当前=1000）
            if [ -n "${ws_uid}" ] && [ "${ws_uid}" != "0" ] && [ "${ws_uid}" != "${current_uid}" ] && [ "${ws_uid}" -ge 1000 ] 2>/dev/null; then
                target_uid="${ws_uid}"
                target_gid="${ws_gid:-${ws_uid}}"
                uid_source="auto"  # 从/workspace属主自动检测
                log_info "[FixUID] Auto-detected UID=${target_uid} GID=${target_gid} from /workspace directory owner"
            else
                log_debug "[FixUID] Auto-detection: /workspace owned by root or already matching, keeping defaults"
            fi
        fi
    fi

    # 回退到默认值
    target_uid="${target_uid:-${current_uid}}"
    target_gid="${target_gid:-${current_gid}}"

    # 安全保护：禁止设置为 root UID=0
    if [ "${target_uid}" = "0" ]; then
        log_warn "[FixUID] Attempt to set UID=0 (root) detected, falling back to current UID=${current_uid}"
        log_warn "[FixUID] For security, ${user} cannot be root. Use 'docker exec -u root ...' for root operations."
        uid_source="blocked"  # UID=0被安全阻止
        target_uid="${current_uid}"
        target_gid="${current_gid}"
    fi

    # 验证 UID/GID 是数字
    if ! [[ "${target_uid}" =~ ^[0-9]+$ ]] || ! [[ "${target_gid}" =~ ^[0-9]+$ ]]; then
        log_warn "[FixUID] Invalid UID/GID (must be numeric), keeping current UID=${current_uid} GID=${current_gid}"
        FIXUID_USER="${user}"
        FIXUID_FINAL_UID="${current_uid}"
        FIXUID_FINAL_GID="${current_gid}"
        FIXUID_ORIG_UID="${current_uid}"
        FIXUID_ORIG_GID="${current_gid}"
        FIXUID_SOURCE="invalid"
        FIXUID_CHANGED="no"
        export FIXUID_USER FIXUID_FINAL_UID FIXUID_FINAL_GID FIXUID_ORIG_UID FIXUID_ORIG_GID FIXUID_SOURCE FIXUID_CHANGED
        return 0
    fi

    # 如果已经匹配，无需调整
    if [ "${target_uid}" = "${current_uid}" ] && [ "${target_gid}" = "${current_gid}" ]; then
        log_info "[FixUID] ${user} UID/GID already matches target (${current_uid}:${current_gid}), no adjustment needed"
        # 导出全局变量供启动横幅使用
        FIXUID_USER="${user}"
        FIXUID_FINAL_UID="${current_uid}"
        FIXUID_FINAL_GID="${current_gid}"
        FIXUID_ORIG_UID="${current_uid}"
        FIXUID_ORIG_GID="${current_gid}"
        FIXUID_SOURCE="${uid_source}"
        FIXUID_CHANGED="no"
        export FIXUID_USER FIXUID_FINAL_UID FIXUID_FINAL_GID FIXUID_ORIG_UID FIXUID_ORIG_GID FIXUID_SOURCE FIXUID_CHANGED
        # 醒目的UID映射摘要日志（与调整完成时格式一致）
        log_info "[FixUID] ═════════════════════════════════════════"
        log_info "[FixUID]   User: ${user}"
        log_info "[FixUID]   UID/GID mapping: ${current_uid}:${current_gid} (no change)"
        log_info "[FixUID]   Source: ${uid_source} (env=环境变量 / auto=自动检测 / default=镜像默认 / blocked=安全阻止)"
        log_info "[FixUID] ═════════════════════════════════════════"
        return 0
    fi

    log_info "[FixUID] Adjusting ${user} UID: ${current_uid} -> ${target_uid}, GID: ${current_gid} -> ${target_gid}"

    # 检查目标 UID 是否已被其他用户占用
    if getent passwd "${target_uid}" >/dev/null 2>&1; then
        occupied_by=$(getent passwd "${target_uid}" | cut -d: -f1)
        if [ "${occupied_by}" != "${user}" ]; then
            new_uid_for_existing=$((target_uid + 1000))
            while getent passwd "${new_uid_for_existing}" >/dev/null 2>&1; do
                new_uid_for_existing=$((new_uid_for_existing + 1))
            done
            log_warn "[FixUID] UID ${target_uid} occupied by '${occupied_by}', moving to UID=${new_uid_for_existing}"
            usermod -u "${new_uid_for_existing}" "${occupied_by}" 2>/dev/null || true
        fi
    fi

    # 检查目标 GID 是否已被其他组占用
    if getent group "${target_gid}" >/dev/null 2>&1; then
        occupied_grp=$(getent group "${target_gid}" | cut -d: -f1)
        if [ "${occupied_grp}" != "${user_grp}" ]; then
            new_gid_for_existing=$((target_gid + 1000))
            while getent group "${new_gid_for_existing}" >/dev/null 2>&1; do
                new_gid_for_existing=$((new_gid_for_existing + 1))
            done
            log_warn "[FixUID] GID ${target_gid} occupied by '${occupied_grp}', moving to GID=${new_gid_for_existing}"
            groupmod -g "${new_gid_for_existing}" "${occupied_grp}" 2>/dev/null || true
        fi
    fi

    # 执行 GID 调整（先调组，再调用户）
    if [ "${target_gid}" != "${current_gid}" ]; then
        log_debug "[FixUID] Running groupmod -g ${target_gid} ${user_grp}"
        groupmod -g "${target_gid}" "${user_grp}" || {
            log_error "[FixUID] Failed to adjust GID for group ${user_grp}"
            return 1
        }
    fi

    # 执行 UID 调整（usermod 会自动调整用户主目录的文件属主）
    if [ "${target_uid}" != "${current_uid}" ]; then
        log_debug "[FixUID] Running usermod -u ${target_uid} ${user}"
        usermod -u "${target_uid}" "${user}" || {
            log_error "[FixUID] Failed to adjust UID for user ${user}"
            return 1
        }
    fi

    # 调整容器内部 devuser 拥有的文件属主（限定安全范围，不碰挂载点和系统目录）
    log_debug "[FixUID] Fixing ownership of ${user}'s files in safe directories..."
    local _safe_dirs=(
        "/home/${user}"
        "/run/user/${current_uid}"
        "/run/user/${target_uid}"
        "/tmp"
        "/var/log/supervisor"
    )
    for _d in "${_safe_dirs[@]}"; do
        if [ -d "$_d" ]; then
            _is_mount=0
            if mountpoint -q "$_d" 2>/dev/null; then
                _is_mount=1
                log_debug "[FixUID] Skipping mountpoint: $_d"
            fi
            if [ "$_is_mount" = "0" ]; then
                log_debug "[FixUID] Adjusting ownership in: $_d"
                find "$_d" -xdev -user "${current_uid}" -exec chown -h "${target_uid}:${target_gid}" {} \; 2>/dev/null || true
            fi
        fi
    done

    # 确保 /run/user/<uid> 目录存在且权限正确
    mkdir -p "/run/user/${target_uid}" 2>/dev/null || true
    chown "${target_uid}:${target_gid}" "/run/user/${target_uid}" 2>/dev/null || true
    chmod 700 "/run/user/${target_uid}" 2>/dev/null || true

    final_uid=$(id -u "${user}")
    final_gid=$(id -g "${user}")

    # 导出全局变量供启动横幅使用
    FIXUID_USER="${user}"
    FIXUID_FINAL_UID="${final_uid}"
    FIXUID_FINAL_GID="${final_gid}"
    FIXUID_ORIG_UID="${current_uid}"
    FIXUID_ORIG_GID="${current_gid}"
    FIXUID_SOURCE="${uid_source}"
    FIXUID_CHANGED="no"
    if [ "${final_uid}" != "${current_uid}" ] || [ "${final_gid}" != "${current_gid}" ]; then
        FIXUID_CHANGED="yes"
    fi
    export FIXUID_USER FIXUID_FINAL_UID FIXUID_FINAL_GID FIXUID_ORIG_UID FIXUID_ORIG_GID FIXUID_SOURCE FIXUID_CHANGED

    # 醒目的UID映射摘要日志
    local _change_desc=""
    if [ "${FIXUID_CHANGED}" = "yes" ]; then
        _change_desc="${current_uid}:${current_gid} -> ${final_uid}:${final_gid}"
    else
        _change_desc="${final_uid}:${final_gid} (no change)"
    fi
    log_info "[FixUID] ═════════════════════════════════════════"
    log_info "[FixUID]   User: ${user}"
    log_info "[FixUID]   UID/GID mapping: ${_change_desc}"
    log_info "[FixUID]   Source: ${uid_source} (env=环境变量 / auto=自动检测 / default=镜像默认 / blocked=安全阻止)"
    log_info "[FixUID] ═════════════════════════════════════════"

    # 验证最终状态
    if [ "${final_uid}" != "${target_uid}" ] || [ "${final_gid}" != "${target_gid}" ]; then
        log_warn "[FixUID] Warning: Final UID/GID (${final_uid}:${final_gid}) differs from target (${target_uid}:${target_gid})"
    fi

    return 0
}

setup_passwords() {
    log_info "[Step 1/7] Configuring user passwords..."
    local user="${NON_ROOT_USER:-devuser}"
    local generated_password=0
    local default_user="devuser"

    groupadd -f docker

    if ! getent passwd "${user}" >/dev/null 2>&1; then
        log_info "User '${user}' does not exist, creating at runtime..."

        if getent passwd "${default_user}" >/dev/null 2>&1 && [ "${user}" != "${default_user}" ]; then
            local default_uid=$(id -u "${default_user}")
            log_info "Renaming default user '${default_user}' (UID ${default_uid}) to '${user}'..."
            usermod -l "${user}" "${default_user}"
            local old_group=$(id -gn "${user}" 2>/dev/null || echo "${default_user}")
            if [ "${old_group}" = "${default_user}" ]; then
                groupmod -n "${user}" "${default_user}" 2>/dev/null || true
            fi
            usermod -d "/home/${user}" -m "${user}"
            if [ -d "/home/${default_user}" ] && [ ! -e "/home/${user}" ]; then
                ln -sf "/home/${user}" "/home/${default_user}" 2>/dev/null || true
            fi
            log_info "User renamed successfully"
        else
            if ! getent passwd 1000 >/dev/null 2>&1; then
                useradd -m -s /bin/bash -u 1000 -G docker,sudo "${user}"
                log_info "Created user '${user}' with UID 1000"
            else
                useradd -m -s /bin/bash -G docker,sudo "${user}"
                log_info "Created user '${user}' with auto-assigned UID $(id -u ${user})"
            fi

            if [ -d "/home/${default_user}" ]; then
                log_info "Copying configs from ${default_user} to ${user}..."
                for cfg in .bashrc .profile .config .conda .jupyter .ssh; do
                    if [ -e "/home/${default_user}/${cfg}" ] && [ ! -e "/home/${user}/${cfg}" ]; then
                        cp -a "/home/${default_user}/${cfg}" "/home/${user}/" 2>/dev/null || true
                    fi
                done
            fi
        fi

        mkdir -p "/home/${user}/.ssh" "/home/${user}/.jupyter/jupyter_server_config.d"
        chmod 700 "/home/${user}/.ssh" 2>/dev/null || true
        chown -R "${user}:${user}" "/home/${user}" 2>/dev/null || true

        echo "${user}:100000:65536" > /etc/subuid
        echo "${user}:100000:65536" > /etc/subgid

        if [ ! -f "/home/${user}/.bashrc" ] || ! grep -q "conda-init.sh" "/home/${user}/.bashrc" 2>/dev/null; then
            echo "source /etc/profile.d/conda-init.sh" >> "/home/${user}/.bashrc"
            chown "${user}:${user}" "/home/${user}/.bashrc" 2>/dev/null || true
        fi
        log_info "[OK] Runtime user '${user}' created and configured"
    else
        log_info "User '${user}' already exists (UID=$(id -u ${user})), ensuring group membership..."
        usermod -aG docker,sudo "${user}" 2>/dev/null || true
    fi

    if [ -n "${ROOT_PASSWORD:-}" ] && [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
        set_user_password root "${ROOT_PASSWORD}"
        log_info "Root password set from ROOT_PASSWORD env var"
    elif [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
        ROOT_PASSWORD=$(pwgen -s 16 1)
        set_user_password root "${ROOT_PASSWORD}"
        log_warn "ROOT_PASSWORD not set, generated random password for root"
        generated_password=1
    fi

    if [ -n "${USER_PASSWORD:-}" ]; then
        set_user_password "${user}" "${USER_PASSWORD}"
        log_info "${user} password set from USER_PASSWORD env var"
    else
        USER_PASSWORD=$(pwgen -s 16 1)
        set_user_password "${user}" "${USER_PASSWORD}"
        log_warn "USER_PASSWORD not set, generated random password for ${user}"
        generated_password=1
    fi

    if getent group docker >/dev/null 2>&1; then
        if ! id -nG "${user}" 2>/dev/null | grep -qw docker; then
            usermod -aG docker "${user}"
            log_info "Added ${user} to docker group"
        else
            log_info "${user} already in docker group"
        fi
    fi

    if [ "${GRANT_SUDO:-no}" = "yes" ]; then
        cat > "/etc/sudoers.d/${user}" << SUDOERS_EOF
${user} ALL=(ALL) NOPASSWD:ALL
SUDOERS_EOF
        chmod 0440 "/etc/sudoers.d/${user}"
        log_info "Sudo NOPASSWD enabled for ${user}"
    fi

    if [ "$generated_password" = "1" ]; then
        echo "" >&2
        echo "    ************************************************" >&2
        if [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
            echo "    * [IMPORTANT] Root password:      ${ROOT_PASSWORD}" >&2
        fi
        echo "    * [IMPORTANT] ${user} password: ${USER_PASSWORD}" >&2
        echo "    * SSH login: ssh ${user}@<host> -p <port>" >&2
        echo "    ************************************************" >&2
        echo "" >&2
    fi
}

generate_host_keys() {
    log_info "[Step 2/7] Generating SSH host keys..."
    rm -f /etc/ssh/ssh_host_*_key /etc/ssh/ssh_host_*_key.pub 2>/dev/null || true
    ssh-keygen -A
    log_info "SSH host keys generated:"
    ls -la /etc/ssh/ssh_host_*_key.pub 2>/dev/null | while IFS= read -r line; do log_info "  $line"; done || true
    if [ ! -f /etc/ssh/ssh_host_ed25519_key ]; then
        log_warn "ED25519 key not found, generating explicitly..."
        ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N "" -q
    fi
}

configure_sshd() {
    log_info "[Step 3/7] Configuring SSH daemon..."
    mkdir -p /run/sshd && chmod 755 /run/sshd
    if [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
        sed -i "s/^#*PermitRootLogin.*/PermitRootLogin yes/" /etc/ssh/sshd_config
        log_info "Root SSH login enabled (ALLOW_ROOT_SSH=yes)"
    else
        sed -i "s/^#*PermitRootLogin.*/PermitRootLogin no/" /etc/ssh/sshd_config
        log_info "Root SSH login disabled (ALLOW_ROOT_SSH=no)"
    fi
    log_info "Validating sshd_config..."
    if /usr/sbin/sshd -t; then
        log_info "[OK] sshd_config syntax valid"
    else
        log_error "sshd_config syntax error! Details:"
        /usr/sbin/sshd -T 2>&1 | head -20 | while IFS= read -r line; do log_error "  $line"; done
        exit 1
    fi
}

setup_ssh_keys() {
    log_info "[Step 4/7] Configuring SSH public key auth..."
    local user="${NON_ROOT_USER:-devuser}"
    if [ -n "${SSH_PUBLIC_KEY:-}" ]; then
        mkdir -p "/home/${user}/.ssh"
        echo "$SSH_PUBLIC_KEY" >> "/home/${user}/.ssh/authorized_keys"
        chmod 600 "/home/${user}/.ssh/authorized_keys"
        chown "${user}:${user}" "/home/${user}/.ssh/authorized_keys"
        if [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
            mkdir -p /root/.ssh
            echo "$SSH_PUBLIC_KEY" >> /root/.ssh/authorized_keys
            chmod 600 /root/.ssh/authorized_keys
        fi
        local key_count
        key_count=$(grep -c "ssh-" "/home/${user}/.ssh/authorized_keys" 2>/dev/null || echo 0)
        log_info "SSH public keys injected (count: ${key_count})"
    else
        log_info "No SSH_PUBLIC_KEY set, password auth only"
    fi
}

setup_container_runtimes() {
    log_info "[Step 5/7] Configuring container runtimes..."
    local user="${NON_ROOT_USER:-devuser}"

    if [ "${ENABLE_DOCKER:-yes}" = "yes" ]; then
        log_info "--- Docker DinD Setup ---"

        if ! command -v dockerd >/dev/null 2>&1; then
            log_error "dockerd binary not found but ENABLE_DOCKER=yes"
            exit 1
        fi

        mkdir -p /var/lib/docker /var/run
        log_info "Docker directories ensured: /var/lib/docker, /var/run"

        if [ -S /var/run/docker.sock ]; then
            log_warn "Pre-existing /var/run/docker.sock detected (DooD mode - host socket mounted)"
            if getent group docker >/dev/null 2>&1; then
                chgrp docker /var/run/docker.sock 2>/dev/null || chmod 666 /var/run/docker.sock 2>/dev/null || true
                log_info "Docker socket permissions adjusted for docker group access"
            else
                chmod 666 /var/run/docker.sock 2>/dev/null || true
                log_info "Docker socket permissions set to 666"
            fi
            DOCKER_DOD_MODE=1
            ENABLE_DOCKER=no
            log_warn "dockerd service disabled (using host Docker socket via DooD)"
        else
            if [ -f /etc/docker/daemon.json ]; then
                log_info "Docker daemon.json exists:"
                while IFS= read -r line; do log_info "  $line"; done < /etc/docker/daemon.json
            else
                log_warn "/etc/docker/daemon.json not found, creating default..."
                mkdir -p /etc/docker
                cat > /etc/docker/daemon.json << 'DOCKER_DAEMON_EOF'
{
  "storage-driver": "overlay2",
  "iptables": false,
  "log-driver": "json-file",
  "log-opts": {"max-size": "10m", "max-file": "3"},
  "userland-proxy": false
}
DOCKER_DAEMON_EOF
            fi

            if getent group docker >/dev/null 2>&1; then
                usermod -aG docker "${user}"
                log_info "Ensured ${user} is in docker group"
            fi

            local cgroup_version="unknown"
            if [ -f /sys/fs/cgroup/cgroup.controllers ]; then
                cgroup_version="v2"
            else
                cgroup_version="v1"
            fi
            log_info "Docker cgroup mode: ${cgroup_version}"

            local priv_check=0
            if ip link add dummy_diag0 type dummy 2>/dev/null; then
                ip link delete dummy_diag0 2>/dev/null
                priv_check=1
                log_info "[OK] Container appears to have --privileged capabilities"
            else
                log_warn "[!] Container may lack --privileged flag - Docker DinD may fail to start"
                log_warn "    Use docker run --privileged ... for full DinD support"
            fi
        fi
    else
        log_info "Docker disabled (ENABLE_DOCKER=no)"
    fi

    if [ "${ENABLE_PODMAN:-no}" = "yes" ]; then
        log_info "--- Podman Rootless Setup ---"

        if [ "${ENABLE_DOCKER:-yes}" = "yes" ]; then
            log_warn "Both Docker and Podman enabled - they may conflict on cgroupv2 hosts"
            log_warn "  If you encounter issues, disable one via ENABLE_DOCKER=no or ENABLE_PODMAN=no"
        fi

        if ! command -v podman >/dev/null 2>&1; then
            log_error "podman binary not found but ENABLE_PODMAN=yes"
            exit 1
        fi

        if ! grep -q "^${user}:" /etc/subuid 2>/dev/null; then
            log_warn "${user} not found in /etc/subuid, adding entry..."
            echo "${user}:100000:65536" >> /etc/subuid
        fi
        if ! grep -q "^${user}:" /etc/subgid 2>/dev/null; then
            log_warn "${user} not found in /etc/subgid, adding entry..."
            echo "${user}:100000:65536" >> /etc/subgid
        fi
        log_info "subuid entries:"
        grep "^${user}:" /etc/subuid 2>/dev/null | while IFS= read -r line; do log_info "  $line"; done || true
        log_info "subgid entries:"
        grep "^${user}:" /etc/subgid 2>/dev/null | while IFS= read -r line; do log_info "  $line"; done || true

        local user_uid
        user_uid=$(id -u "${user}")
        mkdir -p "/run/user/${user_uid}"
        chown "${user}:${user}" "/run/user/${user_uid}"
        chmod 700 "/run/user/${user_uid}"
        log_info "Rootless runtime directory created: /run/user/${user_uid}"

        local containers_config_dir="/home/${user}/.config/containers"
        mkdir -p "${containers_config_dir}"
        cat > "${containers_config_dir}/registries.conf" << 'REGISTRIES_EOF'
unqualified-search-registries = ["docker.io", "quay.io"]
REGISTRIES_EOF
        chown -R "${user}:${user}" "/home/${user}/.config"
        log_info "Podman registries.conf configured"

        if su - "${user}" -c "podman system migrate" >/dev/null 2>&1; then
            log_info "Podman storage migration completed (or already fresh)"
        else
            log_warn "podman system migrate returned non-zero (may be normal for fresh setup)"
        fi

        log_info "Podman rootless setup complete for ${user}"
        log_info "  Usage: su - ${user} -c 'podman run ...' or login as ${user} via SSH"
    else
        log_info "Podman disabled (ENABLE_PODMAN=no)"
    fi

    log_info "Container runtime configuration complete"
}

_do_chown_dir() {
    local dir="$1"
    local mode="$2"
    local user="${NON_ROOT_USER:-devuser}"
    local label="$3"

    [ -d "$dir" ] || mkdir -p "$dir" 2>/dev/null || true
    if [ "${mode}" = "no" ]; then
        log_info "  ${dir}: skip chown (${label})"
        return 0
    fi
    if [ "${mode}" = "named-only" ] || [ "${mode}" = "auto" ]; then
        if _is_bind_mount "$dir"; then
            log_warn "  ${dir}: skip chown (bind mount detected, ${label}) — host directory permissions will NOT be modified"
            return 0
        fi
    fi
    if [ "${mode}" = "yes" ]; then
        if _is_bind_mount "$dir"; then
            log_warn "  ${dir}: bind mount detected — chown WILL MODIFY HOST DIRECTORY OWNERSHIP!"
            log_warn "    If this is a shared data directory, cancel and restart with:"
            log_warn "    -e JUPYTER_ROOT_CHOWN=named-only (recommended) or -e WORKSPACE_CHOWN_MODE=named-only"
        fi
    fi
    chown -R "${user}:${user}" "$dir" 2>/dev/null || {
        local ro_err=0
        touch "$dir/.chown_test_$$" 2>/dev/null || ro_err=1
        rm -f "$dir/.chown_test_$$" 2>/dev/null || true
        if [ "$ro_err" -eq 1 ]; then
            log_info "  ${dir}: chown skipped (read-only volume)"
            return 0
        else
            log_warn "  ${dir}: chown ${user}:${user} failed — directory may not be writable by devuser."
            return 1
        fi
    }
    log_info "  ${dir}: owner ensured ${user}:${user}"
    return 0
}

_print_permission_help() {
    local dir="$1"
    local user="${NON_ROOT_USER:-devuser}"
    local uid=$(id -u "${user}" 2>/dev/null || echo 1000)
    local gid=$(id -g "${user}" 2>/dev/null || echo 1000)
    echo "" >&2
    log_warn "┌────────────────────────────────────────────────────────────────────┐"
    log_warn "│  📂 Directory permissions notice for: $dir"
    log_warn "│"
    log_warn "│  This is a bind-mounted host directory — chown was skipped to"
    log_warn "│  prevent modifying host file ownership."
    log_warn "│"
    log_warn "│  Solutions if you get 'Permission denied' inside the container:"
    log_warn "│"
    log_warn "│  1. (Recommended) Fix permissions ON THE HOST once:"
    log_warn "│     sudo chown -R ${uid}:${gid} \"$dir\""
    log_warn "│"
    log_warn "│  2. Or run inside container with sudo when needed:"
    log_warn "│     sudo chown -R ${user}:${user} \"$dir\""
    log_warn "│"
    log_warn "│  3. Or explicitly allow chown (modifies host files!):"
    log_warn "│     Add to docker run: -e JUPYTER_ROOT_CHOWN=yes"
    log_warn "│"
    log_warn "│  Note: For read-only dataset/model directories, no fix needed."
    log_warn "└────────────────────────────────────────────────────────────────────┘"
    echo "" >&2
}

setup_workspace() {
    log_info "[Init] Initializing workspace and user directory permissions..."
    local user="${NON_ROOT_USER:-devuser}"
    local ws_chown_mode="${WORKSPACE_CHOWN_MODE:-auto}"
    local jupyter_dir="${JUPYTER_ROOT_DIR:-/workspace}"
    local jupyter_chown_mode="${JUPYTER_ROOT_CHOWN:-auto}"
    local ws_chmod="${WORKSPACE_CHMOD:-755}"

    mkdir -p "/workspace" "/home/${user}/.ssh" "${jupyter_dir}"

    local ssh_dir="/home/${user}/.ssh"
    chown "${user}:${user}" "${ssh_dir}" 2>/dev/null || true
    chmod 700 "${ssh_dir}" 2>/dev/null || true
    log_info "  SSH dir: ${ssh_dir} ensured (chmod 700, owner ${user})"

    _do_chown_dir "/workspace" "${ws_chown_mode}" "WORKSPACE_CHOWN_MODE=${ws_chown_mode}" || true
    if [ -n "${ws_chmod}" ]; then
        chmod "${ws_chmod}" "/workspace" 2>/dev/null || true
        log_info "  /workspace: mode ensured ${ws_chmod}"
    fi

    local extra_dir
    for extra_dir in ${CHOWN_DIRS:-}; do
        [ "$extra_dir" = "/workspace" ] && continue
        [ "$extra_dir" = "$jupyter_dir" ] && continue
        _do_chown_dir "$extra_dir" "${ws_chown_mode}" "CHOWN_DIRS, WORKSPACE_CHOWN_MODE=${ws_chown_mode}" || true
    done

    local chown_ret=0
    if [ "$jupyter_dir" != "/workspace" ]; then
        _do_chown_dir "$jupyter_dir" "$jupyter_chown_mode" "JUPYTER_ROOT_CHOWN=${jupyter_chown_mode}" || chown_ret=$?
        if [ "$chown_ret" -ne 0 ] && [ "${JUPYTER_ROOT_SENSITIVE:-0}" != "1" ] && [ "${JUPYTER_ROOT_PERM_HELP_PRINTED:-0}" != "1" ]; then
            _print_permission_help "$jupyter_dir"
            JUPYTER_ROOT_PERM_HELP_PRINTED=1
            export JUPYTER_ROOT_PERM_HELP_PRINTED
        fi
    fi

    log_info "Workspace initialization complete"
}

setup_jupyter() {
    if [ "${ENABLE_JUPYTER:-yes}" != "yes" ]; then
        log_info "[Step 6/7] Jupyter disabled (ENABLE_JUPYTER=no), skipping configuration"
        return 0
    fi

    log_info "[Step 6/7] Configuring Jupyter..."
    local user="${NON_ROOT_USER:-devuser}"
    local jupyter_config_dir="/home/${user}/.jupyter"
    local jupyter_runtime_config="${jupyter_config_dir}/jupyter_server_config.d/runtime.py"

    mkdir -p "${jupyter_config_dir}/jupyter_server_config.d"

    cat > "$jupyter_runtime_config" << 'JUPYTER_RUNTIME_EOF'
c = get_config()
JUPYTER_RUNTIME_EOF

    if [ -n "${JUPYTER_PASSWORD:-}" ]; then
        log_info "Setting Jupyter password from JUPYTER_PASSWORD env var..."
        local jupyter_password_hash
        jupyter_password_hash=$(JUPYTER_PASSWORD="${JUPYTER_PASSWORD}" python -c "
import os
from jupyter_server.auth import passwd
print(passwd(os.environ['JUPYTER_PASSWORD']))
")
        cat >> "$jupyter_runtime_config" << JUPYTER_RUNTIME_EOF
c.ServerApp.password = '${jupyter_password_hash}'  # nosec B105 - variable hash, not hardcoded
c.ServerApp.token = ''
c.IdentityProvider.token = ''
JUPYTER_RUNTIME_EOF
        log_info "Jupyter password authentication configured"
    elif [ -n "${JUPYTER_TOKEN:-}" ]; then
        log_info "Using JUPYTER_TOKEN from env var..."
        cat >> "$jupyter_runtime_config" << JUPYTER_RUNTIME_EOF
c.ServerApp.token = '${JUPYTER_TOKEN}'
c.ServerApp.password = ''
c.IdentityProvider.token = '${JUPYTER_TOKEN}'
JUPYTER_RUNTIME_EOF
    else
        JUPYTER_TOKEN=$(pwgen -s 32 1)
        cat >> "$jupyter_runtime_config" << JUPYTER_RUNTIME_EOF
c.ServerApp.token = '${JUPYTER_TOKEN}'
c.ServerApp.password = ''
c.IdentityProvider.token = '${JUPYTER_TOKEN}'
JUPYTER_RUNTIME_EOF
        log_warn "JUPYTER_TOKEN not set, generated random token"
    fi

    cat >> "$jupyter_runtime_config" << JUPYTER_RUNTIME_EOF
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = ${JUPYTER_PORT:-8888}
c.ServerApp.open_browser = False
c.ServerApp.root_dir = '${JUPYTER_ROOT_DIR:-/workspace}'
c.ServerApp.allow_root = False
c.ServerApp.allow_origin = '${JUPYTER_ALLOW_ORIGIN:-}'
c.ServerApp.allow_credentials = True
JUPYTER_RUNTIME_EOF

    chown -R "${user}:${user}" "${jupyter_config_dir}" 2>/dev/null || true
    log_info "Jupyter runtime config written to ${jupyter_runtime_config}"
    log_info "Jupyter configured (root_dir: ${JUPYTER_ROOT_DIR:-/workspace}, port: ${JUPYTER_PORT:-8888})"
}

configure_supervisor_and_start() {
    log_info "[Step 7/7] Configuring supervisord services..."
    local user="${NON_ROOT_USER:-devuser}"

    local jupyter_conf="/etc/supervisor/conf.d/jupyter.conf"
    if [ -f "$jupyter_conf" ] && [ "${ENABLE_JUPYTER:-yes}" = "yes" ]; then
        local jupyter_dir="${JUPYTER_ROOT_DIR:-/workspace}"
        if grep -q "^directory=" "$jupyter_conf" 2>/dev/null; then
            sed -i "s|^directory=.*|directory=${jupyter_dir}|" "$jupyter_conf"
            log_info "Updated supervisor jupyter directory to: ${jupyter_dir}"
        fi
    fi

    local priv_warn=0
    if [ "${ENABLE_DOCKER:-yes}" = "yes" ]; then
        if ! ip link add dummy_chk type dummy 2>/dev/null; then
            priv_warn=1
        else
            ip link delete dummy_chk 2>/dev/null
        fi
    fi

    for svc in sshd dockerd jupyter; do
        local conf_file="/etc/supervisor/conf.d/${svc}.conf"
        if [ -f "$conf_file" ]; then
            local enabled="no"
            case $svc in
                sshd) enabled="${ENABLE_SSH:-yes}" ;;
                dockerd) enabled="${ENABLE_DOCKER:-yes}" ;;
                jupyter) enabled="${ENABLE_JUPYTER:-yes}" ;;
            esac
            if [ "${enabled}" != "yes" ]; then
                mv "$conf_file" "${conf_file}.disabled"
                log_info "Disabled supervisor service: ${svc}"
            else
                log_info "Enabled supervisor service: ${svc}"
            fi
        fi
    done

    echo "" >&2
    echo "============================================================" >&2
    echo "  Container ready! Services managed by supervisord" >&2
    echo "" >&2

    # UID 映射摘要（由 adjust_user_uid_gid 设置 FIXUID_* 全局变量）
    local _uid_user="${FIXUID_USER:-${user}}"
    local _uid_final="${FIXUID_FINAL_UID:-$(id -u ${user} 2>/dev/null || echo 1000)}"
    local _uid_final_g="${FIXUID_FINAL_GID:-$(id -g ${user} 2>/dev/null || echo 1000)}"
    local _uid_source="${FIXUID_SOURCE:-unknown}"
    local _uid_changed="${FIXUID_CHANGED:-no}"
    local _uid_source_cn="未知"
    case "${_uid_source}" in
        env)     _uid_source_cn="环境变量(LOCAL_USER_ID)" ;;
        auto)    _uid_source_cn="自动检测(/workspace属主)" ;;
        default) _uid_source_cn="镜像默认" ;;
        blocked) _uid_source_cn="安全阻止(UID=0不允许)" ;;
        invalid) _uid_source_cn="无效值(已回退默认)" ;;
    esac
    echo "  User/UID mapping:" >&2
    echo "    User:  ${_uid_user} (UID:GID = ${_uid_final}:${_uid_final_g})" >&2
    if [ "${_uid_changed}" = "yes" ]; then
        echo "    Changed: ${FIXUID_ORIG_UID:-?}:${FIXUID_ORIG_GID:-?} -> ${_uid_final}:${_uid_final_g}" >&2
    fi
    echo "    Source: ${_uid_source_cn}" >&2
    echo "" >&2

    if [ "${ENABLE_SSH:-yes}" = "yes" ]; then
        echo "  SSH access:" >&2
        echo "    ssh ${user}@<host> -p <mapped-port>" >&2
        echo "    Password: ${USER_PASSWORD:-<set via USER_PASSWORD env>}" >&2
        if [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
            echo "    ssh root@<host> -p <mapped-port>" >&2
            echo "    Root password: ${ROOT_PASSWORD:-<set via ROOT_PASSWORD env>}" >&2
        fi
        echo "" >&2
    fi

    if [ "${DOCKER_DOD_MODE}" = "1" ]; then
        echo "  Docker access:" >&2
        echo "    Mode: DooD (host Docker socket mounted)" >&2
        echo "    Usage: docker ps (via host daemon)" >&2
        echo "" >&2
    elif [ "${ENABLE_DOCKER_ORIG:-yes}" = "yes" ]; then
        echo "  Docker access:" >&2
        echo "    Mode: DinD (Docker-in-Docker)" >&2
        echo "    Socket: unix:///var/run/docker.sock" >&2
        echo "    Usage: docker ps (as ${user} or root)" >&2
        echo "" >&2
    fi

    if [ "${ENABLE_PODMAN:-no}" = "yes" ]; then
        echo "  Podman access (rootless, on-demand):" >&2
        echo "    Usage: su - ${user} -c 'podman ps'" >&2
        echo "    Or: SSH as ${user} and run podman commands directly" >&2
        echo "" >&2
    fi

    if [ "${ENABLE_JUPYTER:-yes}" = "yes" ]; then
        echo "  Jupyter access:" >&2
        echo "    URL: http://<host>:<mapped-port>/" >&2
        if [ -n "${JUPYTER_TOKEN:-}" ]; then
            echo "    Token: ${JUPYTER_TOKEN}" >&2
        fi
        if [ -n "${JUPYTER_PASSWORD:-}" ]; then
            echo "    Password: (use JUPYTER_PASSWORD you set)" >&2
        fi
        echo "" >&2
    fi

    echo "  Working directory: ${JUPYTER_ROOT_DIR:-/workspace} (Jupyter/SSH default, mount volumes here)" >&2

    if [ "$priv_warn" = "1" ] && [ "${DOCKER_DOD_MODE}" != "1" ]; then
        echo "" >&2
        echo "  [WARNING] Container may not be running with --privileged flag" >&2
        echo "            Docker DinD requires --privileged to function correctly" >&2
        echo "            Use: docker run --privileged ..." >&2
    fi

    echo "============================================================" >&2
    echo "" >&2
}

print_banner

resolve_jupyter_root_dir

if [ $# -gt 0 ]; then
    log_info "Command mode detected: '$*' - skipping service startup, exec user command directly"
    diagnose_system
    adjust_user_uid_gid
    setup_passwords
    setup_workspace
    setup_container_runtimes
    log_info "Entering user command (tini as init, signals forwarded)..."
    echo "" >&2
    cd "${JUPYTER_ROOT_DIR:-/workspace}" || true
    exec "$@"
fi

diagnose_system
adjust_user_uid_gid
setup_passwords
setup_workspace
generate_host_keys
configure_sshd
setup_ssh_keys
setup_container_runtimes
setup_jupyter
configure_supervisor_and_start

log_info "Starting supervisord (nodaemon mode)..."
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
