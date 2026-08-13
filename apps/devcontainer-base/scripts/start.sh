#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# ── 加载统一日志库 ──
source "${SCRIPT_DIR}/lib/logging.sh"
LOG_SERVICE="devcontainer-start"
LOG_JSON_OUTPUT="/tmp/devcontainer-base-startup.jsonl"

PROFILE="${PROFILE:-dind}"
ACTION="start"
WAIT_TIMEOUT=90
POLL_INTERVAL=3

# ── 加载 .env 文件（如果存在） ──
load_env_file() {
    local env_file="$PROJECT_DIR/.env"
    if [ -f "$env_file" ]; then
        log_info "Loading environment from .env file..."
        set -a
        # shellcheck source=/dev/null
        source "$env_file"
        set +a
    fi
}

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
Usage: $0 [OPTIONS] [COMMAND]

One-click start/stop for devcontainer-base with health verification.

Commands:
  start              Start services (default)
  stop               Stop and remove containers
  restart            Stop then start
  status             Show container status and connection info

Options:
  -p, --profile PFT  Profile to use: dind (default), dood, ssh-only
  --no-verify        Skip post-start health verification
  -h, --help         Show this help message

Environment variables (can be set in .env file):
  PROFILE            Runtime profile (dind|dood|ssh-only)
  USER_PASSWORD      SSH password for devuser (auto-generated if empty)
  JUPYTER_TOKEN      Jupyter access token (auto-generated if empty)
  GRANT_SUDO         Grant NOPASSWD sudo to devuser (default: yes)
  SSH_PORT           Host SSH port (default: 2222[dind]/2223[dood]/2224[ssh-only])
  JUPYTER_PORT       Host Jupyter port (default: 8888[dind]/8889[dood])
  TZ                 Timezone (default: Asia/Shanghai)

Examples:
  $0                                    # Start DinD mode with random credentials
  $0 --profile dood                     # Start DooD mode (uses host Docker)
  USER_PASSWORD=mypass $0               # Start with custom password
  $0 stop                               # Stop services
  $0 restart                            # Restart services
EOF
}

# ── 解析日志参数 ──
eval "$(log_parse_args "$@")"

while [[ $# -gt 0 ]]; do
    case "$1" in
        start|stop|restart|status) ACTION="$1"; shift ;;
        -p|--profile) PROFILE="$2"; shift 2 ;;
        --no-verify) NO_VERIFY=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

cd "$PROJECT_DIR"

# ── 确定服务名和容器名 ──
case "$PROFILE" in
    dind)
        COMPOSE_SERVICE="devcontainer-dind"
        CONTAINER_NAME="devcontainer-base-dind"
        DEFAULT_SSH_PORT=2222
        DEFAULT_JUPYTER_PORT=8888
        ;;
    dood)
        COMPOSE_SERVICE="devcontainer-dood"
        CONTAINER_NAME="devcontainer-base-dood"
        DEFAULT_SSH_PORT=2223
        DEFAULT_JUPYTER_PORT=8889
        ;;
    ssh-only)
        COMPOSE_SERVICE="devcontainer-ssh"
        CONTAINER_NAME="devcontainer-base-ssh"
        DEFAULT_SSH_PORT=2224
        DEFAULT_JUPYTER_PORT=0
        ;;
    *)
        log_fatal "Unknown profile: $PROFILE (use dind|dood|ssh-only)"
        ;;
esac

SSH_PORT="${SSH_PORT:-$DEFAULT_SSH_PORT}"
JUPYTER_PORT="${JUPYTER_PORT:-$DEFAULT_JUPYTER_PORT}"

# ── 前置检查 ──
check_prerequisites() {
    if ! command -v docker &>/dev/null; then
        log_fatal "Docker is not installed or not in PATH"
    fi
    if ! docker compose version &>/dev/null && ! command -v docker-compose &>/dev/null; then
        log_fatal "Docker Compose (v2) is not available"
    fi
    log_ok "Docker + Compose available"
}

# ── 获取 docker compose 命令 ──
compose_cmd() {
    if docker compose version &>/dev/null; then
        echo "docker compose"
    else
        echo "docker-compose"
    fi
}
COMPOSE="$(compose_cmd)"

# ── 设置上下文字段 ──
log_set_field "profile" "$PROFILE"
log_set_field "container" "$CONTAINER_NAME"

# ==============================================================================
# 停止服务
# ==============================================================================
do_stop() {
    log_step "Stopping devcontainer ($PROFILE mode)"
    $COMPOSE --profile "$PROFILE" down 2>&1 | while IFS= read -r line; do log_info "$line"; done
    log_ok "Services stopped and containers removed"
}

# ==============================================================================
# 查看状态
# ==============================================================================
do_status() {
    log_step "devcontainer-base status"

    if ! docker ps -a --filter "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
        log_warn "Container $CONTAINER_NAME is not running"
        log_info "Start with: $0 --profile $PROFILE"
        return 1
    fi

    echo ""
    docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""

    local health
    health=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "unknown")

    local ssh_pass="${USER_PASSWORD:-changeme}"
    local jupyter_tok="${JUPYTER_TOKEN:-devcontainer123}"

    log_info "Health status: $health"
    echo ""
    echo -e "${_CLR_BOLD}  Connection info:${_CLR_RESET}"
    echo "    SSH:      ssh -p $SSH_PORT devuser@localhost"
    echo "    Password: $ssh_pass"
    if [ "$JUPYTER_PORT" != "0" ]; then
        echo "    Jupyter:  http://localhost:$JUPYTER_PORT/?token=$jupyter_tok"
    fi
    echo ""

    if [ "$health" = "healthy" ]; then
        log_ok "Services are healthy"
    else
        log_warn "Services not yet healthy (status: $health)"
    fi
}

# ==============================================================================
# 启动服务
# ==============================================================================
do_start() {
    load_env_file
    check_prerequisites

    log_step "Starting devcontainer-base ($PROFILE mode)"

    # ── 自动生成凭据 ──
    if [ -z "${USER_PASSWORD:-}" ]; then
        USER_PASSWORD=$(random_string 12)
        log_info "Auto-generated SSH password: $USER_PASSWORD"
    fi
    if [ -z "${JUPYTER_TOKEN:-}" ] && [ "$PROFILE" != "ssh-only" ]; then
        JUPYTER_TOKEN=$(random_string 24)
        log_info "Auto-generated Jupyter token: $JUPYTER_TOKEN"
    fi

    export USER_PASSWORD JUPYTER_TOKEN SSH_PORT JUPYTER_PORT

    # ── 创建 workspace 目录 ──
    mkdir -p "$PROJECT_DIR/workspace"

    # ── 确保镜像已构建 ──
    if ! docker image inspect devcontainer-base:1.0 &>/dev/null; then
        log_info "Image not found, building first..."
        bash "${SCRIPT_DIR}/build.sh"
    else
        log_ok "Image devcontainer-base:1.0 exists"
    fi

    # ── 清理旧容器（如果存在） ──
    if docker ps -a --filter "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
        log_info "Removing existing container..."
        $COMPOSE --profile "$PROFILE" down 2>&1 | while IFS= read -r line; do log_info "$line"; done
    fi

    # ── 启动 ──
    log_info "Launching containers with profile: $PROFILE"
    $COMPOSE --profile "$PROFILE" up -d 2>&1 | while IFS= read -r line; do log_info "$line"; done

    if [ "${NO_VERIFY:-0}" = "1" ]; then
        log_ok "Services started (verification skipped)"
        print_connection_info
        return 0
    fi

    # ── 等待健康检查通过 ──
    log_step "Waiting for services to be healthy"
    local waited=0
    local health="starting"
    local start_period=30

    while [ $waited -lt $WAIT_TIMEOUT ]; do
        sleep $POLL_INTERVAL
        waited=$((waited + POLL_INTERVAL))

        health=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "starting")

        if [ "$health" = "healthy" ]; then
            log_ok "All services healthy (waited ${waited}s)"
            break
        elif [ "$health" = "unhealthy" ]; then
            log_error "Services became unhealthy!"
            log_error "Container logs (last 30 lines):"
            docker logs --tail 30 "$CONTAINER_NAME" 2>&1 | tail -30
            exit 1
        fi

        if [ $((waited % 10)) -eq 0 ]; then
            log_info "Waiting... (${waited}s/${WAIT_TIMEOUT}s, status: $health)"
        fi
    done

    if [ "$health" != "healthy" ]; then
        log_warn "Timeout waiting for healthy status after ${WAIT_TIMEOUT}s"
        log_warn "Services may still be starting. Check with: $0 status"
        print_connection_info
        exit 1
    fi

    # ── 验证 SSH 连接 ──
    verify_ssh

    # ── 验证 Jupyter ──
    if [ "$JUPYTER_PORT" != "0" ]; then
        verify_jupyter
    fi

    # ── 验证 Docker DinD（如果适用） ──
    if [ "$PROFILE" = "dind" ]; then
        verify_docker_dind
    fi

    # ── 输出连接信息 ──
    print_connection_info
}

# ── 验证 SSH ──
verify_ssh() {
    log_info "Verifying SSH service..."

    # 方法1：容器内检查（pgrep进程 + /dev/tcp端口检测，与healthcheck保持一致）
    if docker exec "$CONTAINER_NAME" pgrep -x sshd &>/dev/null && \
       docker exec "$CONTAINER_NAME" timeout 2 bash -c "exec 3<>/dev/tcp/127.0.0.1/22 && exec 3>&-" 2>/dev/null; then
        log_ok "SSH port 22 is listening (internal)"
    else
        log_error "SSH port 22 is not responding!"
        return 1
    fi

    # 方法2：尝试从宿主机SSH（如果sshpass可用）
    if command -v sshpass &>/dev/null; then
        local known_hosts="/tmp/devcontainer-known_hosts-$$"
        if sshpass -p "$USER_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile="$known_hosts" -o ConnectTimeout=5 -p "$SSH_PORT" devuser@localhost "echo SSH_HOST_TEST" &>/dev/null; then
            log_ok "SSH connection from host: OK (port $SSH_PORT)"
        else
            log_warn "SSH from host not yet ready (port $SSH_PORT may still be mapping)"
        fi
        rm -f "$known_hosts"
    else
        log_info "sshpass not installed - skipping host-side SSH test"
        log_info "Test manually: ssh -p $SSH_PORT devuser@localhost"
    fi
}

# ── 验证 Jupyter ──
verify_jupyter() {
    log_info "Verifying Jupyter service..."

    # 容器内测试
    if docker exec "$CONTAINER_NAME" curl -sf http://localhost:8888/api &>/dev/null; then
        log_ok "Jupyter API responding (internal)"
    else
        log_error "Jupyter API not responding (internal)!"
        return 1
    fi

    # 宿主机端口映射测试
    sleep 2
    if curl -sf "http://localhost:${JUPYTER_PORT}/api" &>/dev/null; then
        log_ok "Jupyter accessible from host: http://localhost:$JUPYTER_PORT"
    else
        log_warn "Jupyter not yet accessible from host (port $JUPYTER_PORT may still be mapping)"
    fi
}

# ── 验证 Docker DinD ──
verify_docker_dind() {
    log_info "Verifying Docker DinD..."
    local docker_ver
    docker_ver=$(docker exec "$CONTAINER_NAME" docker version --format '{{.Server.Version}}' 2>/dev/null || echo "")
    if [ -n "$docker_ver" ]; then
        log_ok "Docker DinD daemon running (version $docker_ver)"
    else
        log_error "Docker DinD daemon not responding!"
        return 1
    fi
}

# ── 输出连接信息 ──
print_connection_info() {
    echo ""
    echo -e "${_CLR_BOLD}╔══════════════════════════════════════════════════════════╗${_CLR_RESET}"
    echo -e "${_CLR_BOLD}║          devcontainer-base is ready!                     ║${_CLR_RESET}"
    echo -e "${_CLR_BOLD}╠══════════════════════════════════════════════════════════╣${_CLR_RESET}"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  Mode:     $PROFILE"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  SSH:      ${_CLR_CYAN}ssh -p $SSH_PORT devuser@localhost${_CLR_RESET}"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  Password: ${_CLR_GREEN}$USER_PASSWORD${_CLR_RESET}"
    if [ "$JUPYTER_PORT" != "0" ]; then
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  Jupyter:  ${_CLR_CYAN}http://localhost:$JUPYTER_PORT/?token=$JUPYTER_TOKEN${_CLR_RESET}"
    fi
    if [ "$PROFILE" = "dind" ]; then
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  Docker:   DinD (fully isolated, --privileged)"
    elif [ "$PROFILE" = "dood" ]; then
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  Docker:   DooD (shared host Docker socket)"
    fi
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  Workspace: $(pwd)/workspace"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}  Commands:"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}    $0 status     # Check status"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}    $0 stop       # Stop services"
    echo -e "${_CLR_BOLD}║${_CLR_RESET}    $0 restart    # Restart services"
    echo -e "${_CLR_BOLD}╚══════════════════════════════════════════════════════════╝${_CLR_RESET}"
    echo ""
}

# ==============================================================================
# 主逻辑
# ==============================================================================
log_event "startup_init" "action=$ACTION" "profile=$PROFILE"

case "$ACTION" in
    start)   do_start ;;
    stop)    do_stop ;;
    restart) do_stop; do_start ;;
    status)  do_status ;;
esac

log_event "startup_complete" "action=$ACTION" "profile=$PROFILE" "status=success"
