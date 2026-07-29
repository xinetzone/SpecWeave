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

log_info()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO]  $*"; }
log_warn()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN]  $*" >&2; }
log_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $*" >&2; }

print_banner() {
    echo ""
    echo "============================================================"
    echo "  Jupyter SSH Base Container starting..."
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
    log_info "Non-root user: ${NON_ROOT_USER:-jupyteruser}"

    if [ -f /etc/jupyter-ssh-build-info ]; then
        log_info "Build info:"
        while IFS= read -r line; do log_info "  $line"; done < /etc/jupyter-ssh-build-info
    fi
    log_info "========================================"
    echo ""
}

setup_passwords() {
    log_info "[Step 1/6] Configuring user passwords..."
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
        echo "${NON_ROOT_USER:-jupyteruser}:${USER_PASSWORD}" | chpasswd
        log_info "${NON_ROOT_USER:-jupyteruser} password set from USER_PASSWORD env var"
    else
        USER_PASSWORD=$(pwgen -s 16 1)
        echo "${NON_ROOT_USER:-jupyteruser}:${USER_PASSWORD}" | chpasswd
        log_warn "USER_PASSWORD not set, generated random password for ${NON_ROOT_USER:-jupyteruser}"
        generated_password=1
    fi

    if [ "${GRANT_SUDO:-no}" = "yes" ]; then
        echo "${NON_ROOT_USER:-jupyteruser} ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/${NON_ROOT_USER:-jupyteruser}"
        chmod 0440 "/etc/sudoers.d/${NON_ROOT_USER:-jupyteruser}"
        log_info "Sudo NOPASSWD enabled for ${NON_ROOT_USER:-jupyteruser}"
    fi

    if [ "$generated_password" = "1" ]; then
        echo ""
        echo "    ************************************************"
        if [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
            echo "    * [IMPORTANT] Root password:      ${ROOT_PASSWORD}"
        fi
        echo "    * [IMPORTANT] ${NON_ROOT_USER:-jupyteruser} password: ${USER_PASSWORD}"
        echo "    * SSH login: ssh ${NON_ROOT_USER:-jupyteruser}@<host> -p <port>"
        echo "    ************************************************"
        echo ""
    fi
}

generate_host_keys() {
    log_info "[Step 2/6] Generating SSH host keys..."
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
    log_info "[Step 3/6] Configuring SSH daemon..."
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
    log_info "[Step 4/6] Configuring SSH public key auth..."
    local user="${NON_ROOT_USER:-jupyteruser}"
    if [ -n "${SSH_PUBLIC_KEY:-}" ]; then
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

setup_jupyter() {
    log_info "[Step 5/6] Configuring Jupyter..."
    local user="${NON_ROOT_USER:-jupyteruser}"
    local jupyter_config_dir="/home/${user}/.jupyter"
    local jupyter_runtime_config="${jupyter_config_dir}/jupyter_server_config.d/runtime.py"

    mkdir -p "/workspace" "${jupyter_config_dir}/jupyter_server_config.d"
    chown -R "${user}:${user}" "/workspace" "${jupyter_config_dir}" 2>/dev/null || true
    chmod 755 "/workspace"
    chmod 700 "/home/${user}/.ssh"

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
c.ServerApp.root_dir = '/workspace'
c.ServerApp.allow_root = False
c.ServerApp.allow_origin = '${JUPYTER_ALLOW_ORIGIN:-}'
c.ServerApp.allow_credentials = True
JUPYTER_RUNTIME_EOF

    chown -R "${user}:${user}" "${jupyter_config_dir}" 2>/dev/null || true
    log_info "Jupyter runtime config written to ${jupyter_runtime_config}"
    log_info "Jupyter configured (root_dir: /workspace, port: ${JUPYTER_PORT:-8888})"
}

print_access_info() {
    log_info "[Step 6/6] Preparing access information..."
    echo ""
    echo "============================================================"
    echo "  Container ready! Services managed by supervisord"
    echo ""
    echo "  SSH access:"
    echo "    ssh ${NON_ROOT_USER:-jupyteruser}@<host> -p <mapped-port>"
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
    echo "  Working directory: /workspace (mount a volume here for persistence)"
    echo "============================================================"
    echo ""
}

print_banner

if [ $# -gt 0 ]; then
    log_info "Command mode detected: '$*' - skipping service startup, exec user command directly"
    diagnose_system
    setup_passwords
    log_info "Entering user command (tini as init, signals forwarded)..."
    echo ""
    exec "$@"
fi

diagnose_system
setup_passwords
generate_host_keys
configure_sshd
setup_ssh_keys
setup_jupyter
print_access_info

log_info "Starting supervisord (nodaemon mode)..."
# NOTE: No trap needed — supervisord handles SIGTERM/SIGINT natively.
# exec replaces the shell process, so any trap set before exec would be lost.
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
