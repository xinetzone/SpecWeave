#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

source "${SCRIPT_DIR}/lib/logging.sh"
LOG_SERVICE="jupyter-ide"

CONTAINER_NAME="${CONTAINER_NAME:-devcontainer-jupyter}"
IMAGE_NAME="${IMAGE_NAME:-devcontainer-base:1.0}"
SSH_PORT="${SSH_PORT:-2222}"
JUPYTER_PORT="${JUPYTER_PORT:-8888}"
USER_PASSWORD="${USER_PASSWORD:-}"
JUPYTER_TOKEN="${JUPYTER_TOKEN:-}"
JUPYTER_ALLOW_ORIGIN="${JUPYTER_ALLOW_ORIGIN:-*}"
GRANT_SUDO="${GRANT_SUDO:-yes}"
WORKSPACE_DIR="${WORKSPACE_DIR:-${PROJECT_DIR}/workspace}"
ACTION="start"
WAIT_TIMEOUT=60
POLL_INTERVAL=3

# ── 生成随机字符串 ──
random_string() {
    local len="${1:-16}"
    if command -v openssl &>/dev/null; then
        openssl rand -hex "$((len / 2))" 2>/dev/null || head -c "$len" /dev/urandom | xxd -p | head -c "$len"
    else
        head -c "$len" /dev/urandom | xxd -p | head -c "$len"
    fi
}

usage() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Quick-start devcontainer for host IDE Jupyter integration.
Starts container with Jupyter exposed for VSCode/Trae Jupyter plugins.

Commands:
  start     Start container for IDE Jupyter use (default)
  stop      Stop and remove container
  status    Show container status and IDE connection URL
  logs      Show container logs (tail -f)

Environment variables (with defaults):
  CONTAINER_NAME    Container name (default: devcontainer-jupyter)
  IMAGE_NAME        Image name (default: devcontainer-base:1.0)
  JUPYTER_PORT      Host Jupyter port (default: 8888)
  SSH_PORT          Host SSH port (default: 2222)
  JUPYTER_TOKEN     Jupyter access token (auto-generated if empty)
  USER_PASSWORD     SSH password (auto-generated if empty)
  WORKSPACE_DIR     Host directory to mount as /workspace
                    (default: ./workspace)

Examples:
  $0                              # Start with auto-generated credentials
  JUPYTER_TOKEN=mysecret $0       # Start with custom Jupyter token
  JUPYTER_PORT=9999 $0            # Use custom port
  WORKSPACE_DIR=~/projects $0     # Mount custom workspace dir
  $0 stop                         # Stop and remove
  $0 status                       # Check status + get connection URL
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        start|stop|status|logs) ACTION="$1"; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# ── 前置检查 ──
check_prerequisites() {
    if ! command -v docker &>/dev/null; then
        log_fatal "Docker is not installed or not in PATH"
    fi
    log_ok "Docker is available"
}

# ── 确保镜像存在 ──
ensure_image() {
    if ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
        log_info "Image $IMAGE_NAME not found, building first..."
        bash "${SCRIPT_DIR}/build.sh"
    else
        log_ok "Image $IMAGE_NAME exists"
    fi
}

# ==============================================================================
# 停止容器
# ==============================================================================
do_stop() {
    log_step "Stopping container: $CONTAINER_NAME"
    if docker ps -a --filter "name=^/${CONTAINER_NAME}$" --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
        docker rm -f "$CONTAINER_NAME" 2>&1 | while IFS= read -r line; do log_info "$line"; done
        log_ok "Container removed"
    else
        log_info "Container $CONTAINER_NAME does not exist"
    fi
}

# ==============================================================================
# 查看状态
# ==============================================================================
do_status() {
    log_step "Container status"

    if ! docker ps -a --filter "name=^/${CONTAINER_NAME}$" --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
        log_warn "Container $CONTAINER_NAME is not running"
        log_info "Start with: $0 start"
        return 1
    fi

    echo ""
    docker ps --filter "name=^/${CONTAINER_NAME}$" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""

    local health
    health=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "unknown")

    local ssh_pass="${USER_PASSWORD:-*(auto-generated)*}"
    local jupyter_tok="${JUPYTER_TOKEN:-*(check logs)*}"

    # 尝试从容器日志获取实际token（如果自动生成了）
    if [ -z "${JUPYTER_TOKEN:-}" ]; then
        local actual_token
        actual_token=$(docker logs "$CONTAINER_NAME" 2>&1 | grep -oP 'token=\K[a-f0-9]+' | head -1 || true)
        if [ -n "$actual_token" ]; then
            jupyter_tok="$actual_token"
        fi
    fi

    log_info "Health status: $health"
    echo ""
    echo -e "${_CLR_BOLD}  IDE Connection Setup:${_CLR_RESET}"
    echo ""
    echo -e "  ${_CLR_CYAN}1. Jupyter Server URL for IDE:${_CLR_RESET}"
    echo -e "     http://localhost:${JUPYTER_PORT}/?token=${jupyter_tok}"
    echo ""
    echo -e "  ${_CLR_CYAN}2. VSCode / Trae steps:${_CLR_RESET}"
    echo -e "     - Ctrl+Shift+P → Jupyter: Specify Jupyter Server for Connections"
    echo -e "     - Select 'Existing' → paste the URL above"
    echo -e "     - Open/create a .ipynb file → select Python 3.14 kernel"
    echo ""
    echo -e "  ${_CLR_CYAN}3. Browser JupyterLab (optional):${_CLR_RESET}"
    echo -e "     http://localhost:${JUPYTER_PORT}/lab?token=${jupyter_tok}"
    echo ""
    echo -e "  ${_CLR_CYAN}4. SSH access:${_CLR_RESET}"
    echo -e "     ssh -p $SSH_PORT devuser@localhost"
    echo ""

    if [ "$health" = "healthy" ]; then
        log_ok "Jupyter is ready for IDE connection"
    else
        log_warn "Container not yet healthy (status: $health)"
    fi
}

# ==============================================================================
# 查看日志
# ==============================================================================
do_logs() {
    if ! docker ps -a --filter "name=^/${CONTAINER_NAME}$" --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
        log_fatal "Container $CONTAINER_NAME does not exist"
    fi
    docker logs -f "$CONTAINER_NAME"
}

# ==============================================================================
# 启动容器
# ==============================================================================
do_start() {
    check_prerequisites
    ensure_image

    log_step "Starting devcontainer for IDE Jupyter integration"

    # ── 自动生成凭据 ──
    if [ -z "$USER_PASSWORD" ]; then
        USER_PASSWORD=$(random_string 12)
        log_info "Auto-generated SSH password: $USER_PASSWORD"
    fi
    if [ -z "$JUPYTER_TOKEN" ]; then
        JUPYTER_TOKEN=$(random_string 24)
        log_info "Auto-generated Jupyter token: $JUPYTER_TOKEN"
    fi

    # ── 创建 workspace 目录 ──
    mkdir -p "$WORKSPACE_DIR"
    log_info "Workspace: $WORKSPACE_DIR → /workspace"

    # ── 清理旧容器 ──
    if docker ps -a --filter "name=^/${CONTAINER_NAME}$" --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
        log_info "Removing existing container..."
        docker rm -f "$CONTAINER_NAME" &>/dev/null
    fi

    # ── 启动容器 ──
    log_info "Launching container: $CONTAINER_NAME"
    docker run -d \
        --privileged \
        --name "$CONTAINER_NAME" \
        -p "${SSH_PORT}:22" \
        -p "${JUPYTER_PORT}:8888" \
        -e USER_PASSWORD="$USER_PASSWORD" \
        -e JUPYTER_TOKEN="$JUPYTER_TOKEN" \
        -e JUPYTER_ALLOW_ORIGIN="$JUPYTER_ALLOW_ORIGIN" \
        -e GRANT_SUDO="$GRANT_SUDO" \
        -e TZ=Asia/Shanghai \
        -v "${WORKSPACE_DIR}:/workspace" \
        -v devcontainer-jupyter-docker:/var/lib/docker \
        --restart unless-stopped \
        -t \
        "$IMAGE_NAME" \
        2>&1 | while IFS= read -r line; do log_info "$line"; done

    log_info "Container started, waiting for Jupyter to be ready..."

    # ── 等待健康检查通过 ──
    local waited=0
    local health="starting"

    while [ $waited -lt $WAIT_TIMEOUT ]; do
        sleep $POLL_INTERVAL
        waited=$((waited + POLL_INTERVAL))

        health=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "$CONTAINER_NAME" 2>/dev/null || echo "starting")

        if [ "$health" = "healthy" ]; then
            log_ok "Container is healthy (waited ${waited}s)"
            break
        elif [ "$health" = "unhealthy" ]; then
            log_error "Container became unhealthy!"
            docker logs --tail 20 "$CONTAINER_NAME"
            exit 1
        fi

        if [ $((waited % 10)) -eq 0 ]; then
            log_info "Waiting... (${waited}s/${WAIT_TIMEOUT}s, status: $health)"
        fi
    done

    if [ "$health" != "healthy" ]; then
        log_warn "Timeout waiting for healthy status after ${WAIT_TIMEOUT}s"
        log_warn "Jupyter may still be starting. Check status with: $0 status"
    fi

    # ── 验证 Jupyter 可从宿主机访问 ──
    sleep 2
    if curl -sf "http://localhost:${JUPYTER_PORT}/api?token=${JUPYTER_TOKEN}" &>/dev/null; then
        log_ok "Jupyter verified from host: http://localhost:${JUPYTER_PORT}"
    else
        log_warn "Jupyter port may still be mapping, try: curl http://localhost:${JUPYTER_PORT}/api?token=${JUPYTER_TOKEN}"
    fi

    # ── 输出连接信息 ──
    print_connection_info
}

# ── 输出连接信息 ──
print_connection_info() {
    echo ""
    echo -e "${_CLR_BOLD}╔══════════════════════════════════════════════════════════════╗${_CLR_RESET}"
    echo -e "${_CLR_BOLD}║     devcontainer Jupyter is ready for your IDE!             ║${_CLR_RESET}"
    echo -e "${_CLR_BOLD}╠══════════════════════════════════════════════════════════════╣${_CLR_RESET}"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  ${_CLR_CYAN}Jupyter Server URL (copy this for IDE):${_CLR_RESET}"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  ${_CLR_GREEN}http://localhost:${JUPYTER_PORT}/?token=${JUPYTER_TOKEN}${_CLR_RESET}"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  ${_CLR_CYAN}IDE Setup (VSCode / Trae):${_CLR_RESET}"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  1. Ctrl+Shift+P → Jupyter: Specify Jupyter Server for Connections"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  2. Select 'Existing' → paste the URL above"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  3. Open a .ipynb → select 'Python 3.14' kernel"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  ${_CLR_CYAN}Other access:${_CLR_RESET}"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  - Browser Lab: http://localhost:${JUPYTER_PORT}/lab?token=${JUPYTER_TOKEN}"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  - SSH:         ssh -p ${SSH_PORT} devuser@localhost"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  - SSH pass:    ${USER_PASSWORD}"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  - Workspace:   ${WORKSPACE_DIR}"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  ${_CLR_CYAN}Management:${_CLR_RESET}"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}    $0 status     # Check status"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}    $0 logs       # Follow logs"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}    $0 stop       # Stop and remove"
    echo -e "${_CLR_BOLD}╚══════════════════════════════════════════════════════════════╝${_CLR_RESET}"
    echo ""
}

# ==============================================================================
# 主逻辑
# ==============================================================================
log_event "jupyter_ide_init" "action=$ACTION"

case "$ACTION" in
    start)   do_start ;;
    stop)    do_stop ;;
    status)  do_status ;;
    logs)    do_logs ;;
esac

log_event "jupyter_ide_complete" "action=$ACTION" "status=success"
