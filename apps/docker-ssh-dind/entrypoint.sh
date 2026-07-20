#!/bin/bash
set -e

if [ "${DEBUG:-0}" = "1" ]; then
    set -x
fi

log_info()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO]  $*"; }
log_warn()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN]  $*" >&2; }
log_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $*" >&2; }

print_banner() {
    echo ""
    echo "============================================================"
    echo "  Docker-in-Docker SSH Container starting..."
    echo "  Time: $(date)"
    echo "  Host: $(hostname)"
    echo "============================================================"
    echo ""
}

detect_container_env() {
    CONTAINER_ENV="unknown"
    CONTAINER_HYPERVISOR=""
    IN_WSL2_VM=0

    if [ "${CONTAINER_RUNTIME:-auto}" = "wslc" ]; then
        CONTAINER_ENV="wslc"
        log_info "Container runtime explicitly set to wslc via CONTAINER_RUNTIME env"
    elif [ "${CONTAINER_RUNTIME:-auto}" = "docker" ]; then
        CONTAINER_ENV="docker"
        log_info "Container runtime explicitly set to docker via CONTAINER_RUNTIME env"
    else
        if grep -qi "wsl" /proc/version 2>/dev/null || grep -qi "microsoft" /proc/version 2>/dev/null; then
            CONTAINER_HYPERVISOR="wsl2-vm"
            IN_WSL2_VM=1
        fi

        if [ -f /.dockerenv ]; then
            CONTAINER_ENV="docker"
        elif grep -q "docker\|containerd" /proc/1/cgroup 2>/dev/null; then
            if grep -qi "containerd" /proc/1/cgroup 2>/dev/null; then
                CONTAINER_ENV="containerd"
            else
                CONTAINER_ENV="docker"
            fi
        elif [ "$IN_WSL2_VM" = "1" ]; then
            CONTAINER_ENV="wslc"
            log_info "Detected WSL2 VM without Docker markers - assuming wslc runtime"
        else
            CONTAINER_ENV="docker"
        fi
    fi

    if [ -n "$CONTAINER_HYPERVISOR" ]; then
        log_info "Container host hypervisor: ${CONTAINER_HYPERVISOR}"
    fi
    log_info "Detected container runtime: ${CONTAINER_ENV}"
    if [ "$CONTAINER_ENV" = "wslc" ]; then
        log_warn "wslc runtime detected: DinD requires --privileged equivalent (may not be available)"
        log_warn "  Use -e DIND_SKIP_DOCKER=1 for SSH-only mode if Docker fails to start"
    fi
}

diagnose_system() {
    log_info "========== System Diagnostics =========="
    log_info "OS: $(grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '"')"
    log_info "Kernel: $(uname -r)"
    log_info "Arch: $(uname -m)"
    log_info "Timezone: ${TZ:-not set} (now: $(date))"
    log_info "Locale: ${LANG:-not set}"
    log_info "User: $(id)"

    detect_container_env

    if [ -f /sys/fs/cgroup/cgroup.controllers ]; then
        log_info "cgroup: v2"
    else
        log_info "cgroup: v1"
    fi
    log_info "Docker: $(docker --version 2>/dev/null || echo 'not found')"
    log_info "Containerd: $(containerd --version 2>/dev/null || echo 'not found')"
    if [ -f /etc/dind-build-info ]; then
        log_info "Build info:"
        while IFS= read -r line; do log_info "  $line"; done < /etc/dind-build-info
    fi
    log_info "Checking container privileges..."
    PRIVILEGED=0
    if ip link add dummy_diag0 type dummy 2>/dev/null; then
        ip link delete dummy_diag0 2>/dev/null
        PRIVILEGED=1
        log_info "[OK] Network admin capability present (likely --privileged)"
    else
        log_warn "[!] May lack privileges - ensure container runs with --privileged"
    fi
    log_info "Checking cgroup mount..."
    if mountpoint -q /sys/fs/cgroup 2>/dev/null; then
        log_info "[OK] /sys/fs/cgroup mounted"
    else
        log_warn "[!] /sys/fs/cgroup not mounted, attempting mount..."
        mount -t cgroup2 none /sys/fs/cgroup 2>/dev/null || log_warn "cgroup mount failed, Docker may not start"
    fi

    if [ "${DIND_SKIP_DOCKER:-0}" = "1" ]; then
        log_warn "DIND_SKIP_DOCKER=1: Docker daemon will NOT be started (SSH-only mode)"
    elif [ "$CONTAINER_ENV" = "wslc" ] && [ "$PRIVILEGED" = "0" ]; then
        log_warn "Running under wslc without --privileged equivalent"
        log_warn "  DinD may fail - use DIND_SKIP_DOCKER=1 for SSH-only mode if needed"
    fi
    log_info "========================================"
    echo ""
}

setup_passwords() {
    log_info "[Step 1/6] Configuring user passwords..."
    if [ -n "$ROOT_PASSWORD" ]; then
        echo "root:${ROOT_PASSWORD}" | chpasswd
        log_info "Root password set from ROOT_PASSWORD env var"
    else
        ROOT_PASSWORD=$(pwgen -s 16 1)
        echo "root:${ROOT_PASSWORD}" | chpasswd
        log_warn "ROOT_PASSWORD not set, generated random password"
        GENERATED_PASSWORD=1
    fi

    if [ -n "$AI_PASSWORD" ]; then
        echo "ai:${AI_PASSWORD}" | chpasswd
        log_info "ai user password set from AI_PASSWORD env var"
    else
        AI_PASSWORD="${ROOT_PASSWORD}"
        echo "ai:${AI_PASSWORD}" | chpasswd
        log_info "ai user password set to same as ROOT_PASSWORD (set AI_PASSWORD to override)"
    fi

    if [ "${GENERATED_PASSWORD:-0}" = "1" ]; then
        echo ""
        echo "    ************************************************"
        echo "    * [IMPORTANT] Root password: ${ROOT_PASSWORD}"
        echo "    * [IMPORTANT] ai   password: ${AI_PASSWORD}"
        echo "    * SSH login: ssh root@<host> -p <port>"
        echo "    * SSH login: ssh ai@<host>   -p <port>"
        echo "    ************************************************"
        echo ""
    fi
}

setup_ssh_keys() {
    log_info "[Step 4/6] Configuring SSH public key auth..."
    if [ -n "$SSH_PUBLIC_KEY" ]; then
        echo "$SSH_PUBLIC_KEY" >> /root/.ssh/authorized_keys
        echo "$SSH_PUBLIC_KEY" >> /home/ai/.ssh/authorized_keys
        chmod 600 /root/.ssh/authorized_keys
        chmod 600 /home/ai/.ssh/authorized_keys
        chown ai:docker /home/ai/.ssh/authorized_keys
        KEY_COUNT=$(grep -c "ssh-" /root/.ssh/authorized_keys 2>/dev/null || echo 0)
        log_info "SSH public keys injected (count: ${KEY_COUNT})"
    else
        log_info "No SSH_PUBLIC_KEY set, password auth only"
    fi
}

generate_host_keys() {
    log_info "[Step 2/6] Generating SSH host keys..."
    if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
        ssh-keygen -A
        log_info "SSH host keys generated:"
        ls -la /etc/ssh/ssh_host_*_key.pub 2>/dev/null | while IFS= read -r line; do log_info "  $line"; done
    else
        log_info "SSH host keys already exist, skipping"
    fi
}

configure_sshd() {
    log_info "[Step 3/6] Configuring SSH daemon..."
    mkdir -p /run/sshd && chmod 755 /run/sshd
    if [ "${ALLOW_ROOT_SSH:-yes}" = "no" ]; then
        sed -i "s/^PermitRootLogin.*/PermitRootLogin no/" /etc/ssh/sshd_config
        log_info "Root SSH login disabled (ALLOW_ROOT_SSH=no)"
    else
        sed -i "s/^PermitRootLogin.*/PermitRootLogin yes/" /etc/ssh/sshd_config
        log_info "Root SSH login enabled"
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

start_docker() {
    log_info "[Step 5/6] Starting Docker daemon..."

    if [ "${DIND_SKIP_DOCKER:-0}" = "1" ]; then
        log_warn "DIND_SKIP_DOCKER=1 is set, skipping Docker daemon startup (SSH-only mode)"
        return 0
    fi

    DOCKER_DAEMON_ARGS="-H unix:///var/run/docker.sock ${DOCKER_OPTS}"
    log_info "dockerd args: ${DOCKER_DAEMON_ARGS}"
    dockerd ${DOCKER_DAEMON_ARGS} > /var/log/dockerd.log 2>&1 &
    DOCKER_PID=$!
    log_info "dockerd started (PID: ${DOCKER_PID})"

    DOCKER_READY=0
    for i in $(seq 1 60); do
        if docker version >/dev/null 2>&1; then
            DOCKER_READY=1
            break
        fi
        sleep 1
        if [ $((i % 10)) -eq 0 ]; then
            log_info "Waiting for Docker... (${i}/60)"
            if [ $i -ge 20 ]; then
                log_warn "Docker is slow to start, recent logs:"
                tail -5 /var/log/dockerd.log 2>/dev/null | while IFS= read -r line; do log_warn "  $line"; done
            fi
        fi
    done

    if [ "$DOCKER_READY" -eq 1 ]; then
        log_info "[OK] Docker daemon is ready!"
        docker version 2>&1 | grep -E "Client|Server|Version" | while IFS= read -r line; do log_info "  $line"; done
        if [ -S /var/run/docker.sock ]; then
            chmod 666 /var/run/docker.sock
            log_info "docker.sock permissions set (666), ai user can access"
        fi
    else
        log_error "Docker daemon failed to start within 60 seconds!"
        log_error "=== Last 30 lines of dockerd.log ==="
        tail -30 /var/log/dockerd.log 2>/dev/null | while IFS= read -r line; do log_error "  $line"; done
        log_error "====================================="

        if [ "$CONTAINER_ENV" != "docker" ]; then
            log_warn "Running in non-standard Docker container environment (detected: ${CONTAINER_ENV})"
            log_warn "DinD may not work due to hypervisor/privilege limitations"
            log_warn "Continuing to SSH-only mode - use DIND_SKIP_DOCKER=1 to suppress this warning"
            log_warn "Set DIND_SKIP_DOCKER=1 if you only need SSH access without Docker"
            return 0
        fi

        log_error "Common causes:"
        log_error "  1. Container not running with --privileged"
        log_error "  2. overlay2 storage driver not supported (check kernel modules)"
        log_error "  3. cgroup not mounted correctly"
        log_error "  4. If running under wslc, try DIND_SKIP_DOCKER=1 for SSH-only mode"
        log_error "  5. Full log: cat /var/log/dockerd.log"
        exit 1
    fi
}

start_sshd() {
    log_info "[Step 6/6] Starting SSH daemon..."
    log_info "SSH listening on port: 22"
    log_info "================================================"
    log_info "Container ready! Connect via:"
    log_info "  ssh root@<host> -p <mapped-port>"
    log_info "  ssh ai@<host> -p <mapped-port>"
    log_info "================================================"
    echo ""
    exec /usr/sbin/sshd -D -e
}

cleanup() {
    log_info "Received shutdown signal, stopping services gracefully..."
    if [ -n "$DOCKER_PID" ]; then
        log_info "Stopping Docker daemon (PID: ${DOCKER_PID})..."
        kill -TERM "$DOCKER_PID" 2>/dev/null || true
        wait "$DOCKER_PID" 2>/dev/null || true
        log_info "Docker daemon stopped"
    fi
    log_info "Container shutdown complete"
    exit 0
}
trap cleanup SIGTERM SIGINT

print_banner
diagnose_system
setup_passwords
generate_host_keys
configure_sshd
setup_ssh_keys
start_docker
start_sshd