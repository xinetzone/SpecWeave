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

log_info()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO]  $*"; }
log_warn()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN]  $*" >&2; }
log_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $*" >&2; }

print_banner() {
    echo ""
    echo "============================================================"
    echo "  DevContainer Base starting..."
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
    echo ""
}

setup_passwords() {
    log_info "[Step 1/7] Configuring user passwords..."
    local user="${NON_ROOT_USER:-devuser}"
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
        echo "${user}:${USER_PASSWORD}" | chpasswd
        log_info "${user} password set from USER_PASSWORD env var"
    else
        USER_PASSWORD=$(pwgen -s 16 1)
        echo "${user}:${USER_PASSWORD}" | chpasswd
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
        echo ""
        echo "    ************************************************"
        if [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
            echo "    * [IMPORTANT] Root password:      ${ROOT_PASSWORD}"
        fi
        echo "    * [IMPORTANT] ${user} password: ${USER_PASSWORD}"
        echo "    * SSH login: ssh ${user}@<host> -p <port>"
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

setup_jupyter() {
    if [ "${ENABLE_JUPYTER:-yes}" != "yes" ]; then
        log_info "[Step 6/7] Jupyter disabled (ENABLE_JUPYTER=no), skipping configuration"
        return 0
    fi

    log_info "[Step 6/7] Configuring Jupyter..."
    local user="${NON_ROOT_USER:-devuser}"
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

configure_supervisor_and_start() {
    log_info "[Step 7/7] Configuring supervisord services..."
    local user="${NON_ROOT_USER:-devuser}"

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

    echo ""
    echo "============================================================"
    echo "  Container ready! Services managed by supervisord"
    echo ""

    if [ "${ENABLE_SSH:-yes}" = "yes" ]; then
        echo "  SSH access:"
        echo "    ssh ${user}@<host> -p <mapped-port>"
        echo "    Password: ${USER_PASSWORD:-<set via USER_PASSWORD env>}"
        if [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
            echo "    ssh root@<host> -p <mapped-port>"
            echo "    Root password: ${ROOT_PASSWORD:-<set via ROOT_PASSWORD env>}"
        fi
        echo ""
    fi

    if [ "${DOCKER_DOD_MODE}" = "1" ]; then
        echo "  Docker access:"
        echo "    Mode: DooD (host Docker socket mounted)"
        echo "    Usage: docker ps (via host daemon)"
        echo ""
    elif [ "${ENABLE_DOCKER_ORIG:-yes}" = "yes" ]; then
        echo "  Docker access:"
        echo "    Mode: DinD (Docker-in-Docker)"
        echo "    Socket: unix:///var/run/docker.sock"
        echo "    Usage: docker ps (as ${user} or root)"
        echo ""
    fi

    if [ "${ENABLE_PODMAN:-no}" = "yes" ]; then
        echo "  Podman access (rootless, on-demand):"
        echo "    Usage: su - ${user} -c 'podman ps'"
        echo "    Or: SSH as ${user} and run podman commands directly"
        echo ""
    fi

    if [ "${ENABLE_JUPYTER:-yes}" = "yes" ]; then
        echo "  Jupyter access:"
        echo "    URL: http://<host>:<mapped-port>/"
        if [ -n "${JUPYTER_TOKEN:-}" ]; then
            echo "    Token: ${JUPYTER_TOKEN}"
        fi
        if [ -n "${JUPYTER_PASSWORD:-}" ]; then
            echo "    Password: (use JUPYTER_PASSWORD you set)"
        fi
        echo ""
    fi

    echo "  Working directory: /workspace (mount a volume here for persistence)"

    if [ "$priv_warn" = "1" ] && [ "${DOCKER_DOD_MODE}" != "1" ]; then
        echo ""
        echo "  [WARNING] Container may not be running with --privileged flag"
        echo "            Docker DinD requires --privileged to function correctly"
        echo "            Use: docker run --privileged ..."
    fi

    echo "============================================================"
    echo ""
}

print_banner

if [ $# -gt 0 ]; then
    log_info "Command mode detected: '$*' - skipping service startup, exec user command directly"
    diagnose_system
    setup_passwords
    setup_container_runtimes
    log_info "Entering user command (tini as init, signals forwarded)..."
    echo ""
    exec "$@"
fi

diagnose_system
setup_passwords
generate_host_keys
configure_sshd
setup_ssh_keys
setup_container_runtimes
setup_jupyter
configure_supervisor_and_start

log_info "Starting supervisord (nodaemon mode)..."
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
