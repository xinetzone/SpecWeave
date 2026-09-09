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

CONDA_DIR="/opt/conda"
CONDA_ENV="main"
CONDA_ENV_PATH="${CONDA_DIR}/envs/${CONDA_ENV}"
CONDA_PYTHON="${CONDA_ENV_PATH}/bin/python"
CONDA_JUPYTER="${CONDA_ENV_PATH}/bin/jupyter"
NON_ROOT_USER="${NON_ROOT_USER:-devuser}"
NON_ROOT_HOME="/home/${NON_ROOT_USER}"
BUILD_INFO_FILE="/etc/jupyter-podman-build-info"
SUPERVISORD_CONF="/etc/supervisor/supervisord.conf"

log_info()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO]  $*"; }
log_warn()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN]  $*" >&2; }
log_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $*" >&2; }

run_as_user() {
    if command -v gosu >/dev/null 2>&1; then
        exec gosu "${NON_ROOT_USER}" "$@"
    else
        exec su - "${NON_ROOT_USER}" -c "exec \"\$@\"" -- "$@"
    fi
}

print_banner() {
    echo ""
    echo "============================================================"
    echo "  Jupyter Podman Rootless Container starting..."
    echo "  Time: $(date)"
    echo "  Host: $(hostname)"
    echo "============================================================"
    echo ""
}

diagnose_system() {
    log_info "========== System Diagnostics =========="
    log_info "OS: $(grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '"')"
    log_info "Kernel: $(uname -r)"
    log_info "Arch: $(uname -m)"
    log_info "Timezone: ${TZ:-not set} (now: $(date))"
    log_info "Locale: ${LANG:-not set}"
    log_info "User: $(id)"
    log_info "Non-root user: ${NON_ROOT_USER}"

    log_info "Python version: $("${CONDA_PYTHON}" --version 2>&1)"
    if "${CONDA_PYTHON}" -c "import sys, sysconfig; sys.exit(0 if sysconfig.get_config_var('Py_GIL_DISABLED') == 1 and not sys._is_gil_enabled() else 1)" 2>/dev/null; then
        log_info "Python build: cp314t (free-threading) confirmed"
    else
        log_warn "Python is NOT free-threading build"
    fi
    log_info "Conda version: $("${CONDA_DIR}/bin/conda" --version 2>&1)"
    if command -v podman >/dev/null 2>&1; then
        log_info "Podman version: $(podman --version 2>&1 | awk '{print $3}')"
    else
        log_warn "Podman not found in PATH"
    fi

    if [ -f "${BUILD_INFO_FILE}" ]; then
        log_info "Build info:"
        while IFS= read -r line; do log_info "  $line"; done < "${BUILD_INFO_FILE}"
    fi
    log_info "========================================"
    echo ""
}

setup_passwords() {
    log_info "[Step 1/7] Configuring user passwords..."
    local generated_password=0

    if [ -n "${ROOT_PASSWORD:-}" ] && [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
        echo "root:${ROOT_PASSWORD}" | chpasswd
        log_info "Root password set from ROOT_PASSWORD env var"
    elif [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
        ROOT_PASSWORD=$(pwgen -s 16 1)
        echo "root:${ROOT_PASSWORD}" | chpasswd
        log_warn "ROOT_PASSWORD not set, generated random password for root"
        generated_password=1
    fi

    if [ -n "${USER_PASSWORD:-}" ]; then
        echo "${NON_ROOT_USER}:${USER_PASSWORD}" | chpasswd
        log_info "${NON_ROOT_USER} password set from USER_PASSWORD env var"
    else
        USER_PASSWORD=$(pwgen -s 16 1)
        echo "${NON_ROOT_USER}:${USER_PASSWORD}" | chpasswd
        log_warn "USER_PASSWORD not set, generated random password for ${NON_ROOT_USER}"
        generated_password=1
    fi

    if [ "${GRANT_SUDO:-no}" = "yes" ]; then
        echo "${NON_ROOT_USER} ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/${NON_ROOT_USER}"
        chmod 0440 "/etc/sudoers.d/${NON_ROOT_USER}"
        log_info "Sudo NOPASSWD enabled for ${NON_ROOT_USER}"
    fi

    if [ "$generated_password" = "1" ]; then
        echo ""
        echo "    ************************************************"
        if [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
            echo "    * [IMPORTANT] Root password:      ${ROOT_PASSWORD}"
        fi
        echo "    * [IMPORTANT] ${NON_ROOT_USER} password: ${USER_PASSWORD}"
        echo "    * SSH login: ssh ${NON_ROOT_USER}@<host> -p <port>"
        echo "    ************************************************"
        echo ""
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

setup_podman() {
    log_info "[Step 4/7] Setting up Podman rootless environment..."

    if [ -c /dev/fuse ]; then
        chmod 666 /dev/fuse 2>/dev/null || true
        log_info "/dev/fuse device permissions set"
    else
        log_warn "/dev/fuse not found - FUSE may not be available; make sure to run container with --device /dev/fuse"
    fi

    local containers_config_dir="${NON_ROOT_HOME}/.config/containers"
    mkdir -p "${containers_config_dir}"
    chown -R "${NON_ROOT_USER}:${NON_ROOT_USER}" "${containers_config_dir}" 2>/dev/null || true
    chmod 700 "${containers_config_dir}" 2>/dev/null || true
    log_info "User containers config dir ready: ${containers_config_dir}"

    local podman_storage_dir="${NON_ROOT_HOME}/.local/share/containers"
    mkdir -p "${podman_storage_dir}"
    chown -R "${NON_ROOT_USER}:${NON_ROOT_USER}" "${NON_ROOT_HOME}/.local" 2>/dev/null || true
    log_info "Podman storage dir ready: ${podman_storage_dir}"

    local podman_run_dir="/run/user/$(id -u ${NON_ROOT_USER})"
    mkdir -p "${podman_run_dir}"
    chown -R "${NON_ROOT_USER}:${NON_ROOT_USER}" "${podman_run_dir}" 2>/dev/null || true
    chmod 700 "${podman_run_dir}" 2>/dev/null || true
    log_info "Podman run dir ready: ${podman_run_dir}"

    # rootless podman 需把管理进程 pause.pid 写入 ${XDG_RUNTIME_DIR}/libpod/tmp，
    # 目录缺失会触发 `open .../libpod/tmp/pause.pid: no such file or directory`
    # 与 `error creating temporary file: Permission denied`（见 README §5.4 C-I1 扩展）。
    # 属主必须与运行时用户一致（devuser UID 动态分配，禁止硬编码 1000）。
    local podman_libpod="${podman_run_dir}/libpod"
    local podman_libpod_tmp="${podman_libpod}/tmp"
    mkdir -p "${podman_libpod_tmp}"
    # libpod 父目录同样必须属于运行时用户；否则 rootless podman 对 /run/user/<uid>/libpod
    # 设置 sticky bit 时会被拒绝（`set sticky bit on: chmod .../libpod: operation not permitted`）。
    # 必须先 chown 父目录再 chmod，避免 devuser UID 动态分配下仍残留 root 属主。
    chown -R "${NON_ROOT_USER}:${NON_ROOT_USER}" "${podman_libpod}" 2>/dev/null || true
    chmod 700 "${podman_libpod}" 2>/dev/null || true
    chown -R "${NON_ROOT_USER}:${NON_ROOT_USER}" "${podman_libpod_tmp}" 2>/dev/null || true
    chmod 700 "${podman_libpod_tmp}" 2>/dev/null || true
    log_info "Podman libpod tmp dir ready: ${podman_libpod_tmp}"

    export XDG_RUNTIME_DIR="${podman_run_dir}"

    # ── B-scheme: 宿主 rootless daemon socket 直连（绕过嵌套 userns）──
    # 若启动时已注入 HOST_PODMAN_SOCK（宿主 socket 已在同一绝对路径 bind-mount 进
    # 容器），则在 devuser 可控目录内为其建立符号链接，并显式设置 CONTAINER_HOST，
    # 使容器内 podman SDK/CLI 直接复用宿主 daemon。此后绝不再尝试容器内自建 daemon
    # （自建 daemon 在 WSL 三层 userns 嵌套下会触发 newuidmap Operation not permitted）。
    local host_sock="${HOST_PODMAN_SOCK:-}"
    if [ -n "${host_sock}" ] && [ -S "${host_sock}" ]; then
        # ── devuser 路径（默认 XDG_RUNTIME_DIR）──
        local run_sock_dir="${podman_run_dir}/podman"
        mkdir -p "${run_sock_dir}"
        chown -R "${NON_ROOT_USER}:${NON_ROOT_USER}" "${run_sock_dir}" 2>/dev/null || true
        chmod 700 "${run_sock_dir}" 2>/dev/null || true
        ln -sf "${host_sock}" "${run_sock_dir}/podman.sock"

        # ── root 路径（容错）──
        # root 用户下 XDG_RUNTIME_DIR 通常为 /run/user/0（不存在）或空，
        # podman-py SDK 会回落到 /tmp/podmanpy-runtime-dir-fallback-root/...。
        # 为避免 Notebook 以 root 身份启动时 from_env() 找不到 socket，
        # 在这里也建立一份根可写的链接（同宿 socket，不影响权限）。
        local root_sock_dir="/tmp/podman-runtime-dir"
        mkdir -p "${root_sock_dir}/podman"
        chmod 777 "${root_sock_dir}" 2>/dev/null || true
        chmod 777 "${root_sock_dir}/podman" 2>/dev/null || true
        ln -sf "${host_sock}" "${root_sock_dir}/podman/podman.sock"

        # 显式覆盖两个关键 env：无论谁调用 from_env() 都命中宿主 socket
        export CONTAINER_HOST="unix://${run_sock_dir}/podman.sock"
        export XDG_RUNTIME_DIR="${podman_run_dir}"
        log_info "[B-scheme] Host podman socket linked: ${run_sock_dir}/podman.sock -> ${host_sock}"
        log_info "[B-scheme] root fallback socket: ${root_sock_dir}/podman/podman.sock -> ${host_sock}"
        log_info "[B-scheme] CONTAINER_HOST=${CONTAINER_HOST} (XDG_RUNTIME_DIR=${podman_run_dir})"
        log_info "Podman rootless setup complete (host socket pass-through)"
        return 0
    fi

    log_info "No host socket detected (HOST_PODMAN_SOCK unset/absent), falling back to in-container rootless daemon..."

    log_info "Triggering Podman rootless initialization (podman info)..."
    if su - "${NON_ROOT_USER}" -c "export XDG_RUNTIME_DIR=${podman_run_dir}; podman info >/dev/null 2>&1"; then
        log_info "[OK] Podman rootless environment initialized successfully"
    else
        log_warn "Podman info command returned non-zero (this may be normal if subuid/subgid not fully configured on host)"
        log_info "Attempting podman system migrate..."
        su - "${NON_ROOT_USER}" -c "export XDG_RUNTIME_DIR=${podman_run_dir}; podman system migrate 2>/dev/null" || true
    fi

    log_info "Starting rootless podman system service (background)..."
    local podman_sock="${podman_run_dir}/podman/podman.sock"
    if su - "${NON_ROOT_USER}" -c "export XDG_RUNTIME_DIR=${podman_run_dir}; test -S ${podman_sock}" 2>/dev/null; then
        log_info "[OK] rootless podman system service already online: ${podman_sock}"
    else
        su - "${NON_ROOT_USER}" -c "export XDG_RUNTIME_DIR=${podman_run_dir}; nohup podman system service --time=0 >/tmp/podman-service.log 2>&1 </dev/null &" || true
        for _i in $(seq 1 30); do
            if su - "${NON_ROOT_USER}" -c "export XDG_RUNTIME_DIR=${podman_run_dir}; test -S ${podman_sock}" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        if su - "${NON_ROOT_USER}" -c "export XDG_RUNTIME_DIR=${podman_run_dir}; test -S ${podman_sock}" 2>/dev/null; then
            log_info "[OK] rootless podman system service online: ${podman_sock}"
        else
            log_warn "podman system service failed to start within 30s, last log lines:"
            tail -n 20 /tmp/podman-service.log 2>/dev/null || true
        fi
    fi

    log_info "Podman rootless setup complete"
}

setup_ssh_keys() {
    log_info "[Step 5/7] Configuring SSH public key auth..."
    local user="${NON_ROOT_USER}"
    if [ -n "${SSH_PUBLIC_KEY:-}" ]; then
        echo "$SSH_PUBLIC_KEY" >> "${NON_ROOT_HOME}/.ssh/authorized_keys"
        chmod 600 "${NON_ROOT_HOME}/.ssh/authorized_keys"
        chown "${user}:${user}" "${NON_ROOT_HOME}/.ssh/authorized_keys"
        if [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
            mkdir -p /root/.ssh
            echo "$SSH_PUBLIC_KEY" >> /root/.ssh/authorized_keys
            chmod 600 /root/.ssh/authorized_keys
        fi
        local key_count
        key_count=$(grep -c "ssh-" "${NON_ROOT_HOME}/.ssh/authorized_keys" 2>/dev/null || echo 0)
        log_info "SSH public keys injected (count: ${key_count})"
    else
        log_info "No SSH_PUBLIC_KEY set, password auth only"
    fi
}

setup_jupyter() {
    log_info "[Step 6/7] Configuring Jupyter..."
    local jupyter_config_dir="${NON_ROOT_HOME}/.jupyter"
    local jupyter_runtime_config="${jupyter_config_dir}/jupyter_server_config.d/runtime.py"

    mkdir -p "${jupyter_config_dir}/jupyter_server_config.d"
    chown -R "${NON_ROOT_USER}:${NON_ROOT_USER}" "${jupyter_config_dir}" 2>/dev/null || true
    chmod 700 /root/.ssh 2>/dev/null || true

    cat > "$jupyter_runtime_config" << 'JUPYTER_RUNTIME_EOF'
c = get_config()
JUPYTER_RUNTIME_EOF

    if [ -n "${JUPYTER_PASSWORD:-}" ]; then
        log_info "Setting Jupyter password from JUPYTER_PASSWORD env var..."
        local jupyter_password_hash
        jupyter_password_hash=$(JUPYTER_PASSWORD="${JUPYTER_PASSWORD}" "${CONDA_PYTHON}" -c "
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
c.ServerApp.root_dir = '/workspace'
c.ServerApp.allow_root = True
c.ServerApp.allow_origin = '${JUPYTER_ALLOW_ORIGIN:-}'
c.ServerApp.allow_credentials = True
c.ContentsManager.allow_hidden = True
c.FileContentsManager.allow_hidden = True
JUPYTER_RUNTIME_EOF

    chmod 777 /workspace 2>/dev/null || true
    log_info "Jupyter runtime config written to ${jupyter_runtime_config}"
    log_info "Jupyter configured (root_dir: /workspace, port: ${JUPYTER_PORT:-8888}, python: ${CONDA_PYTHON})"
}

print_access_info() {
    log_info "[Step 7/7] Preparing access information..."
    echo ""
    echo "============================================================"
    echo "  Container ready! Services managed by supervisord"
    echo ""
    echo "  SSH access:"
    echo "    ssh ${NON_ROOT_USER}@<host> -p <mapped-port>"
    echo "    Password: ${USER_PASSWORD:-<set via USER_PASSWORD env>}"
    if [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
        echo "    ssh root@<host> -p <mapped-port>"
        echo "    Root password: ${ROOT_PASSWORD:-<set via ROOT_PASSWORD env>}"
    fi
    echo ""
    echo "  Jupyter access:"
    echo "    URL: http://<host>:<mapped-port>/"
    if [ -n "${JUPYTER_TOKEN:-}" ]; then
        echo "    Token: ${JUPYTER_TOKEN}"
    fi
    if [ -n "${JUPYTER_PASSWORD:-}" ]; then
        echo "    Password: (use JUPYTER_PASSWORD you set)"
    fi
    echo ""
    echo "  Podman (rootless): available for ${NON_ROOT_USER}"
    echo "    (Run 'podman info' after login to verify)"
    echo ""
    echo "  Working directory: /workspace (mount a volume here for persistence)"
    echo "  Conda environment: ${CONDA_ENV} (${CONDA_ENV_PATH})"
    echo "============================================================"
    echo ""
}

print_banner

if [ $# -gt 0 ]; then
    log_info "Command mode detected: '$*' - skipping service startup, exec user command as ${NON_ROOT_USER}"
    diagnose_system
    setup_passwords
    setup_podman
    log_info "Entering user command (tini as init, signals forwarded)..."
    echo ""
    run_as_user "$@"
fi

diagnose_system
setup_passwords
generate_host_keys
configure_sshd
setup_podman
setup_ssh_keys
setup_jupyter
print_access_info

log_info "Starting supervisord (nodaemon mode)..."
log_info "  - sshd runs as root (required for port 22)"
log_info "  - jupyter runs as ${NON_ROOT_USER} (configured in supervisor conf)"
exec /usr/bin/supervisord -c "${SUPERVISORD_CONF}"
