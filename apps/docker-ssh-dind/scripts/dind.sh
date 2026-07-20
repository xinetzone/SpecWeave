#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

IMAGE_NAME="dind-ssh"
CONTAINER_NAME="dind-test"
DEFAULT_SSH_PORT=2222
RUNTIME=""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }
log_cmd()   { echo -e "${CYAN}[CMD]${NC}   $*"; }

detect_runtime() {
    if [ -f .env.detected ]; then
        source .env.detected
        RUNTIME="${RECOMMENDED_RUNTIME:-docker}"
    else
        if command -v docker &>/dev/null && docker info &>/dev/null 2>&1; then
            RUNTIME="docker"
        elif command -v wslc.exe &>/dev/null; then
            RUNTIME="wslc"
        else
            bash scripts/check-env.sh || true
            log_error "No container runtime available. Run scripts/check-env.sh for diagnostics."
            exit 1
        fi
    fi
}

usage() {
    echo "dind-ssh Management Script"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  check-env     Run environment detection"
    echo "  build         Build the container image"
    echo "  run           Start the container (default port 2222)"
    echo "  stop          Stop and remove the container"
    echo "  ssh [user]    SSH into the container (default: root)"
    echo "  logs          View container logs"
    echo "  status        Show container status"
    echo "  exec <cmd>    Execute command in container"
    echo "  clean         Remove container and image"
    echo "  help          Show this help"
    echo ""
    echo "Options:"
    echo "  --runtime=<docker|wslc|auto>  Force runtime (default: auto-detect)"
    echo "  --port=<port>                 SSH port mapping (default: 2222)"
    echo "  --name=<name>                 Container name (default: dind-test)"
    echo "  --password=<pwd>              Root password (default: auto-generated)"
    echo "  --ssh-key=<key>               SSH public key for auth"
    echo ""
    echo "Examples:"
    echo "  $0 check-env"
    echo "  $0 build"
    echo "  $0 run"
    echo "  $0 run --port=2222 --password=MySecret123"
    echo "  $0 ssh ai"
    echo "  $0 exec docker ps"
}

load_env() {
    if [ -f .env.detected ]; then
        source .env.detected
    fi
}

parse_args() {
    SSH_PORT="$DEFAULT_SSH_PORT"
    ROOT_PASSWORD=""
    SSH_KEY=""
    EXTRA_ARGS=""

    for arg in "$@"; do
        case "$arg" in
            --runtime=*)
                RUNTIME="${arg#*=}"
                ;;
            --port=*)
                SSH_PORT="${arg#*=}"
                ;;
            --name=*)
                CONTAINER_NAME="${arg#*=}"
                ;;
            --password=*)
                ROOT_PASSWORD="${arg#*=}"
                ;;
            --ssh-key=*)
                SSH_KEY="${arg#*=}"
                ;;
            *)
                EXTRA_ARGS="$EXTRA_ARGS $arg"
                ;;
        esac
    done
}

cmd_check_env() {
    bash scripts/check-env.sh
}

cmd_build() {
    detect_runtime
    log_info "Building image '${IMAGE_NAME}' using runtime: ${RUNTIME}"
    case "$RUNTIME" in
        docker)
            log_cmd "docker build -t ${IMAGE_NAME} -f Containerfile ."
            docker build -t "${IMAGE_NAME}" -f Containerfile .
            ;;
        wslc)
            log_warn "wslc.exe image build - note: wslc build may have limited Dockerfile compatibility"
            local CONTEXT_PATH="$PROJECT_DIR"
            if [ "$OS_DETAIL" = "wsl" ] && command -v wslpath &>/dev/null; then
                CONTEXT_PATH=$(wslpath -w "$PROJECT_DIR")
            fi
            log_cmd "wslc.exe build -t ${IMAGE_NAME} ${CONTEXT_PATH}"
            wslc.exe build -t "${IMAGE_NAME}" "${CONTEXT_PATH}" 2>&1 || {
                log_warn "wslc build failed; wslc may have limited Containerfile support"
                log_info "Falling back: build with docker, or use pre-built image"
                log_info "Alternatively, pull the image first and use wslc run"
                exit 1
            }
            ;;
        *)
            log_error "Unknown runtime: ${RUNTIME}"
            exit 1
            ;;
    esac
    log_ok "Build complete!"
}

get_wslc_port_args() {
    local port="$1"
    echo "--publish ${port}:22"
}

cmd_run() {
    detect_runtime
    log_info "Starting container '${CONTAINER_NAME}' using runtime: ${RUNTIME}"

    local env_args=""
    local port_args="-p ${SSH_PORT}:22"
    local vol_args="-v dind-data:/var/lib/docker"
    local priv_args="--privileged"

    [ -n "$ROOT_PASSWORD" ] && env_args="$env_args -e ROOT_PASSWORD=${ROOT_PASSWORD}"
    [ -n "$SSH_KEY" ] && env_args="$env_args -e SSH_PUBLIC_KEY=\"${SSH_KEY}\""

    case "$RUNTIME" in
        docker)
            if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
                log_warn "Container '${CONTAINER_NAME}' already exists, stopping first..."
                docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true
            fi
            log_cmd "docker run -d ${priv_args} ${port_args} ${vol_args} ${env_args} --name ${CONTAINER_NAME} ${IMAGE_NAME}"
            docker run -d ${priv_args} ${port_args} ${vol_args} ${env_args} --name "${CONTAINER_NAME}" "${IMAGE_NAME}"
            log_info "Waiting for container to start..."
            sleep 3
            log_ok "Container started!"
            log_info "To view logs: $0 logs"
            log_info "To SSH: $0 ssh"
            log_info "SSH port: ${SSH_PORT}"
            ;;
        wslc)
            log_warn "wslc mode: DinD functionality may be limited (privileged mode not fully supported)"
            log_warn "wslc mode: primarily for SSH access; nested dockerd may not start"
            local wslc_port_args
            wslc_port_args=$(get_wslc_port_args "$SSH_PORT")
            log_cmd "wslc.exe run -d ${wslc_port_args} ${env_args} --name ${CONTAINER_NAME} ${IMAGE_NAME}"
            wslc.exe run -d ${wslc_port_args} ${env_args} --name "${CONTAINER_NAME}" "${IMAGE_NAME}" 2>&1 || {
                log_error "wslc run failed. Ensure WSL2 is up to date (wsl --update)"
                exit 1
            }
            log_info "Waiting for container to start..."
            sleep 5
            log_ok "Container started in wslc mode!"
            log_info "Note: Check logs for dockerd startup status: $0 logs"
            ;;
        *)
            log_error "Unknown runtime: ${RUNTIME}"
            exit 1
            ;;
    esac
    echo ""
    log_info "SSH connection: ssh -p ${SSH_PORT} root@localhost"
}

cmd_stop() {
    detect_runtime
    log_info "Stopping container '${CONTAINER_NAME}'..."
    case "$RUNTIME" in
        docker)
            docker rm -f "${CONTAINER_NAME}" 2>/dev/null || log_warn "Container not found or already stopped"
            ;;
        wslc)
            wslc.exe rm -f "${CONTAINER_NAME}" 2>/dev/null || log_warn "Container not found or already stopped"
            ;;
    esac
    log_ok "Container stopped"
}

cmd_ssh() {
    detect_runtime
    local ssh_user="${1:-root}"
    log_info "Connecting via SSH as ${ssh_user}..."
    case "$RUNTIME" in
        docker)
            local ssh_port="${SSH_PORT:-$DEFAULT_SSH_PORT}"
            local root_pwd=""
            if docker inspect "${CONTAINER_NAME}" &>/dev/null 2>&1; then
                root_pwd=$(docker logs "${CONTAINER_NAME}" 2>&1 | grep -oP 'Root password: \K[A-Za-z0-9]+' | tail -1 || echo "")
            fi
            if [ -n "$root_pwd" ] && [ "$ssh_user" = "root" ]; then
                log_info "Root password (from logs): ${root_pwd}"
            fi
            log_cmd "ssh -p ${ssh_port} -o StrictHostKeyChecking=no ${ssh_user}@localhost"
            exec ssh -p "${ssh_port}" -o StrictHostKeyChecking=no "${ssh_user}@localhost"
            ;;
        wslc)
            local ssh_port="${SSH_PORT:-$DEFAULT_SSH_PORT}"
            log_cmd "ssh -p ${ssh_port} -o StrictHostKeyChecking=no ${ssh_user}@localhost"
            exec ssh -p "${ssh_port}" -o StrictHostKeyChecking=no "${ssh_user}@localhost"
            ;;
    esac
}

cmd_logs() {
    detect_runtime
    case "$RUNTIME" in
        docker)
            docker logs -f "${CONTAINER_NAME}"
            ;;
        wslc)
            wslc.exe logs -f "${CONTAINER_NAME}"
            ;;
    esac
}

cmd_status() {
    detect_runtime
    echo "=========================================="
    echo "  dind-ssh Status"
    echo "=========================================="
    echo ""
    log_info "Runtime: ${RUNTIME}"
    echo ""
    case "$RUNTIME" in
        docker)
            if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
                local state
                state=$(docker inspect -f '{{.State.Status}}' "${CONTAINER_NAME}" 2>/dev/null || echo "unknown")
                log_ok "Container '${CONTAINER_NAME}': ${state}"
                docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || true
            else
                log_warn "Container '${CONTAINER_NAME}': not created"
            fi
            echo ""
            docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" 2>/dev/null || echo "Image not built yet"
            ;;
        wslc)
            if wslc.exe inspect "${CONTAINER_NAME}" &>/dev/null 2>&1; then
                log_ok "Container '${CONTAINER_NAME}': running"
                wslc.exe ps -a 2>&1 | grep "${CONTAINER_NAME}" || true
            else
                log_warn "Container '${CONTAINER_NAME}': not created"
            fi
            ;;
    esac
    echo ""
}

cmd_exec() {
    detect_runtime
    local exec_cmd="$*"
    if [ -z "$exec_cmd" ]; then
        log_error "No command specified for exec"
        exit 1
    fi
    case "$RUNTIME" in
        docker)
            log_cmd "docker exec -it ${CONTAINER_NAME} ${exec_cmd}"
            exec docker exec -it "${CONTAINER_NAME}" ${exec_cmd}
            ;;
        wslc)
            log_cmd "wslc.exe exec -it ${CONTAINER_NAME} ${exec_cmd}"
            exec wslc.exe exec -it "${CONTAINER_NAME}" ${exec_cmd}
            ;;
    esac
}

cmd_clean() {
    detect_runtime
    log_warn "Cleaning up container and image..."
    case "$RUNTIME" in
        docker)
            docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true
            docker rmi "${IMAGE_NAME}" 2>/dev/null || true
            ;;
        wslc)
            wslc.exe rm -f "${CONTAINER_NAME}" 2>/dev/null || true
            wslc.exe rmi "${IMAGE_NAME}" 2>/dev/null || true
            ;;
    esac
    rm -f .env.detected
    log_ok "Cleanup complete"
}

load_env
parse_args "$@"

COMMAND=""
if [ -n "$EXTRA_ARGS" ]; then
    COMMAND=$(echo "$EXTRA_ARGS" | awk '{print $1}')
    EXTRA_ARGS=$(echo "$EXTRA_ARGS" | cut -d' ' -f2-)
fi

case "${COMMAND:-help}" in
    check-env)    cmd_check_env ;;
    build)        cmd_build ;;
    run)          cmd_run ;;
    stop)         cmd_stop ;;
    ssh)          cmd_ssh $EXTRA_ARGS ;;
    logs)         cmd_logs ;;
    status)       cmd_status ;;
    exec)         cmd_exec $EXTRA_ARGS ;;
    clean)        cmd_clean ;;
    help|--help|-h) usage ;;
    *)
        log_error "Unknown command: ${COMMAND}"
        echo ""
        usage
        exit 1
        ;;
esac
