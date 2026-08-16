#!/usr/bin/env bash
# =============================================================================
# torch-dev 容器一键启动脚本
# 包含：前置检查、自动端口冲突检测与解决、健康等待、test_torch.py 验证
#
# 用法:
#   ./scripts/start-torch-dev.sh                      # DinD 长期后台模式（默认）
#   ./scripts/start-torch-dev.sh --dood               # DooD 模式（共享宿主机Docker）
#   ./scripts/start-torch-dev.sh --ssh-only           # 仅 SSH 最小化模式
#   ./scripts/start-torch-dev.sh --test               # 一次性运行 test_torch.py 验证（--rm）
#   ./scripts/start-torch-dev.sh --bash               # 一次性进入 bash shell
#   ./scripts/start-torch-dev.sh -p 2300 -P 8900      # 自定义 SSH/Jupyter 端口
#   ./scripts/start-torch-dev.sh --no-auto-port       # 禁止自动端口调整，冲突时报错退出
#   ./scripts/start-torch-dev.sh --stop               # 停止并删除容器
#   ./scripts/start-torch-dev.sh --logs               # 查看容器日志
#   ./scripts/start-torch-dev.sh --info               # 显示镜像和容器信息
#   ./scripts/start-torch-dev.sh -h                   # 显示帮助
#
# 端口冲突自动处理：
#   默认检测默认端口(2226/8891)，如被占用则自动+1递增直到找到空闲端口
#   通过环境变量传递给 docker compose，不修改 compose 文件（避免配置漂移）
#
# 环境变量:
#   USER_PASSWORD      SSH密码（默认 torchdev）
#   JUPYTER_TOKEN      Jupyter token（默认 torchdev123）
#   SSH_PORT           SSH端口（默认自动检测）
#   JUPYTER_PORT       Jupyter端口（默认自动检测）
#   PROFILE            启动模式: dind(默认)|dood|ssh-only
#   START_DEV_DEBUG=1  启用DEBUG日志
# =============================================================================
set -euo pipefail

IMAGE="devcontainer-base:torch-dev-latest"
CONTAINER_NAME="torch-dev"
COMPOSE_FILE="docker-compose.torch.yml"
DEFAULT_SSH_PORT=2226
DEFAULT_JUPYTER_PORT=8891
DEFAULT_PASSWORD="torchdev"
DEFAULT_TOKEN="torchdev123"
WORKSPACE_DIR="/workspace"
PYTHON_BIN="/opt/conda/envs/main/bin/python"
# test_torch.py 在容器内的路径：
#   - daemon (compose) 模式: examples/ 只读挂载到 /opt/torch-dev/examples/
#   - ephemeral (docker run) 模式: VARIANT_ROOT 挂载到 /workspace，脚本在 /workspace/examples/
TEST_SCRIPT_DAEMON="/opt/torch-dev/examples/test_torch.py"
TEST_SCRIPT_EPHEMERAL="/workspace/examples/test_torch.py"
HEALTH_TIMEOUT=90
HEALTH_INTERVAL=3
MAX_PORT_INCREMENT=50

# ── 颜色 ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
GRAY='\033[0;90m'
NC='\033[0m'

# ── 日志 ──
DEBUG_MODE="${START_DEV_DEBUG:-0}"
debug() { if [[ "$DEBUG_MODE" == "1" ]]; then echo -e "${GRAY}[DEBUG]${NC} $*" >&2; fi; }
info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ── 路径解析 ──
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$VARIANT_ROOT"

debug "SCRIPT_DIR=$SCRIPT_DIR"
debug "VARIANT_ROOT=$VARIANT_ROOT"
debug "PWD=$(pwd)"

# ── WSL 路径适配 ──
# 如果在 WSL 中且 WORKSPACE_HOST_DIR 未设置，默认将 variant 根目录挂载为 workspace
detect_wsl() {
    if grep -qi microsoft /proc/version 2>/dev/null; then
        echo "wsl"
    elif grep -qi wsl /proc/version 2>/dev/null; then
        echo "wsl"
    else
        echo "linux"
    fi
}
HOST_ENV="$(detect_wsl)"
debug "HOST_ENV=$HOST_ENV"

# workspace 宿主机目录（挂载源）：优先使用 $WORKSPACE_HOST_DIR，否则用 ./workspace
WORKSPACE_HOST_DIR="${WORKSPACE_HOST_DIR:-$VARIANT_ROOT/workspace}"
mkdir -p "$WORKSPACE_HOST_DIR"
debug "WORKSPACE_HOST_DIR=$WORKSPACE_HOST_DIR"

# ── docker compose 命令检测 ──
compose_cmd() {
    if docker compose version &>/dev/null; then
        echo "docker compose"
    elif command -v docker-compose &>/dev/null; then
        echo "docker-compose"
    else
        error "Docker Compose v2 未安装"
        exit 1
    fi
}
COMPOSE="$(compose_cmd)"
debug "COMPOSE=$COMPOSE"

# ── 前置检查 ──
check_docker() {
    if ! command -v docker &>/dev/null; then
        error "Docker 未安装或不在 PATH 中"
        exit 1
    fi
    if ! docker info &>/dev/null; then
        error "Docker daemon 未运行或无权限"
        error "  WSL:  sudo service docker start"
        error "  Windows: 启动 Docker Desktop"
        exit 1
    fi
    debug "Docker OK"
}

check_image() {
    if ! docker image inspect "$IMAGE" &>/dev/null; then
        error "镜像 $IMAGE 不存在，请先构建："
        echo ""
        echo "  cd $VARIANT_ROOT/.."
        echo "  bash build.sh --variant torch-dev --cn"
        echo ""
        exit 1
    fi
    local img_size
    img_size=$(docker images "$IMAGE" --format '{{.Size}}' 2>/dev/null | head -1)
    debug "镜像存在: $IMAGE ($img_size)"
}

check_compose_file() {
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        error "Compose 文件不存在: $VARIANT_ROOT/$COMPOSE_FILE"
        exit 1
    fi
    debug "Compose 文件存在: $COMPOSE_FILE"
}

# ── 端口冲突检测 ──
# 检测指定端口是否被占用（宿主机进程 + 已运行的docker容器映射）
port_in_use() {
    local port="$1"
    # 方法1: ss / netstat 检测宿主机监听
    if command -v ss &>/dev/null; then
        if ss -tlnp 2>/dev/null | grep -qE "[:.]${port}[[:space:]]"; then
            return 0
        fi
    elif command -v netstat &>/dev/null; then
        if netstat -tlnp 2>/dev/null | grep -qE "[:.]${port}[[:space:]]"; then
            return 0
        fi
    fi
    # 方法2: docker ps 检测容器端口映射（防遗漏）
    if docker ps --format '{{.Ports}}' 2>/dev/null | grep -qE "0\\.0\\.0\\.0:${port}->|:::${port}->|:${port}->"; then
        return 0
    fi
    # 方法3: /dev/tcp 尝试连接（最通用兜底）
    if (echo >/dev/tcp/127.0.0.1/"$port") 2>/dev/null; then
        return 0
    fi
    return 1
}

# 自动寻找空闲端口：从 start_port 开始递增，最多 MAX_PORT_INCREMENT 次
find_free_port() {
    local start_port="$1"
    local port="$start_port"
    local attempts=0
    while port_in_use "$port" && [[ $attempts -lt $MAX_PORT_INCREMENT ]]; do
        debug "端口 $port 被占用，尝试 $((port+1))"
        port=$((port + 1))
        attempts=$((attempts + 1))
    done
    if [[ $attempts -ge $MAX_PORT_INCREMENT ]]; then
        error "无法在 $start_port~$((start_port+MAX_PORT_INCREMENT)) 范围内找到空闲端口"
        error "请手动指定端口: $0 -p <SSH_PORT> -P <JUPYTER_PORT>"
        exit 1
    fi
    echo "$port"
}

resolve_ports() {
    local auto_port="$1"
    if [[ -n "${SSH_PORT:-}" ]] && [[ -n "${JUPYTER_PORT:-}" ]]; then
        # 用户已手动指定两个端口
        debug "用户手动指定端口 SSH=$SSH_PORT JUPYTER=$JUPYTER_PORT"
        if port_in_use "$SSH_PORT"; then
            if [[ "$auto_port" == "1" ]]; then
                warn "SSH端口 $SSH_PORT 被占用，自动调整..."
                SSH_PORT=$(find_free_port "$SSH_PORT")
            else
                error "SSH端口 $SSH_PORT 被占用（使用 --auto-port 自动调整，或 -p 指定其他端口）"
                exit 1
            fi
        fi
        if port_in_use "$JUPYTER_PORT"; then
            if [[ "$auto_port" == "1" ]]; then
                warn "Jupyter端口 $JUPYTER_PORT 被占用，自动调整..."
                JUPYTER_PORT=$(find_free_port "$JUPYTER_PORT")
            else
                error "Jupyter端口 $JUPYTER_PORT 被占用（使用 --auto-port 自动调整，或 -P 指定其他端口）"
                exit 1
            fi
        fi
    else
        SSH_PORT="${SSH_PORT:-$DEFAULT_SSH_PORT}"
        JUPYTER_PORT="${JUPYTER_PORT:-$DEFAULT_JUPYTER_PORT}"
        if [[ "$auto_port" == "1" ]]; then
            SSH_PORT=$(find_free_port "$SSH_PORT")
            JUPYTER_PORT=$(find_free_port "$JUPYTER_PORT")
        else
            if port_in_use "$SSH_PORT"; then
                error "SSH端口 $SSH_PORT 被占用（使用默认自动端口调整或 --no-auto-port 确认）"
                exit 1
            fi
            if port_in_use "$JUPYTER_PORT"; then
                error "Jupyter端口 $JUPYTER_PORT 被占用（使用默认自动端口调整或 --no-auto-port 确认）"
                exit 1
            fi
        fi
    fi
    info "端口分配: SSH=$SSH_PORT, Jupyter=$JUPYTER_PORT"
}

# ── 获取服务名（根据profile）──
get_service_name() {
    case "$PROFILE" in
        dind)     echo "torch-dev-dind" ;;
        dood)     echo "torch-dev-dood" ;;
        ssh-only) echo "torch-dev-ssh" ;;
        *)        echo "torch-dev-dind" ;;
    esac
}

# ── 等待健康检查 ──
wait_for_healthy() {
    local container="$1"
    local timeout="$2"
    local waited=0
    local health="starting"
    info "等待容器健康（超时 ${timeout}s）..."
    while [[ $waited -lt $timeout ]]; do
        sleep "$HEALTH_INTERVAL"
        waited=$((waited + HEALTH_INTERVAL))
        health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "starting")
        case "$health" in
            healthy)
                ok "容器健康（等待 ${waited}s）"
                return 0
                ;;
            unhealthy)
                error "容器变为 unhealthy！"
                docker logs --tail 30 "$container" 2>&1 | tail -30
                return 1
                ;;
        esac
        if [[ $((waited % 15)) -eq 0 ]]; then
            info "等待中... (${waited}s/${timeout}s, status=$health)"
        fi
    done
    warn "等待健康检查超时（${timeout}s），容器可能仍在启动"
    warn "查看日志: $0 --logs"
    return 0
}

# ── 运行 test_torch.py 验证 ──
run_torch_test() {
    local quick="${1:-0}"
    local container="$CONTAINER_NAME"
    if [[ "$PROFILE" == "dood" ]]; then
        container="torch-dev-dood"
    fi
    info "运行 test_torch.py 综合验证..."
    echo ""
    local quick_flag=""
    [[ "$quick" == "1" ]] && quick_flag="--quick"
    if docker exec "$container" "$PYTHON_BIN" "$TEST_SCRIPT_DAEMON" $quick_flag; then
        echo ""
        ok "test_torch.py 验证通过"
        return 0
    else
        warn "test_torch.py 有失败项（容器已启动，可手动排查）"
        return 1
    fi
}

# ── 停止容器 ──
stop_container() {
    local service
    service=$(get_service_name)
    info "停止并删除 $PROFILE 模式的容器..."
    WORKSPACE_DIR="$WORKSPACE_HOST_DIR" \
    SSH_PORT="$SSH_PORT" JUPYTER_PORT="$JUPYTER_PORT" \
    $COMPOSE -f "$COMPOSE_FILE" --profile "$PROFILE" down 2>&1 | while IFS= read -r line; do debug "$line"; done
    # 同时清理其他profile的同名容器（防残留）
    for p in dind dood ssh-only; do
        docker rm -f "torch-dev" "torch-dev-dood" "torch-dev-ssh" 2>/dev/null || true
    done
    ok "已停止"
}

# ── 查看日志 ──
show_logs() {
    local container="$CONTAINER_NAME"
    if [[ "$PROFILE" == "dood" ]]; then container="torch-dev-dood"; fi
    if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        warn "容器 $container 未运行"
        exit 1
    fi
    docker logs -f "$container"
}

# ── 显示信息 ──
show_info() {
    echo ""
    echo -e "${CYAN}═══ torch-dev 镜像信息 ═══${NC}"
    docker images "$IMAGE" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" 2>/dev/null || echo "  镜像不存在"
    echo ""
    echo -e "${CYAN}═══ 容器状态 ═══${NC}"
    local found=0
    for c in torch-dev torch-dev-dood torch-dev-ssh; do
        if docker ps -a --format '{{.Names}}' | grep -q "^${c}$"; then
            docker ps -a --filter "name=$c" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
            found=1
        fi
    done
    [[ $found -eq 0 ]] && echo "  无运行中的 torch-dev 容器"
    echo ""
    echo -e "${CYAN}═══ 快速验证（test_torch.py）═══${NC}"
    docker run --rm -i \
        -e WORKSPACE_CHOWN_MODE=named-only \
        -v "$VARIANT_ROOT:$WORKSPACE_DIR" \
        -w "$WORKSPACE_DIR" \
        "$IMAGE" \
        "$PYTHON_BIN" "$TEST_SCRIPT_EPHEMERAL" --quick 2>&1 || true
}

# ── 显示连接信息 ──
show_connection_info() {
    local password="${USER_PASSWORD:-$DEFAULT_PASSWORD}"
    local token="${JUPYTER_TOKEN:-$DEFAULT_TOKEN}"
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  🚀 torch-dev 开发容器已就绪                                  ║${NC}"
    echo -e "${CYAN}╠══════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║${NC}  模式:     $PROFILE"
    echo -e "${CYAN}║${NC}  SSH:"
    echo -e "${CYAN}║${NC}    ssh devuser@localhost -p $SSH_PORT"
    echo -e "${CYAN}║${NC}    密码: $password"
    if [[ "$PROFILE" != "ssh-only" ]]; then
    echo -e "${CYAN}║${NC}  Jupyter:"
    echo -e "${CYAN}║${NC}    http://localhost:$JUPYTER_PORT/?token=$token"
    fi
    echo -e "${CYAN}║${NC}  进入容器:"
    echo -e "${CYAN}║${NC}    docker exec -it $CONTAINER_NAME bash"
    echo -e "${CYAN}║${NC}  挂载目录:"
    echo -e "${CYAN}║${NC}    $WORKSPACE_HOST_DIR -> $WORKSPACE_DIR"
    echo -e "${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}  常用命令:"
    echo -e "${CYAN}║${NC}    查看日志:  $0 --logs"
    echo -e "${CYAN}║${NC}    停止容器:  $0 --stop"
    echo -e "${CYAN}║${NC}    重新验证:  docker exec $CONTAINER_NAME $PYTHON_BIN $TEST_SCRIPT_DAEMON"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# ── 一次性模式（ephemeral）──
run_ephemeral() {
    local cmd="$1"
    local IT_FLAG="-i"
    [ -t 0 ] && [ -t 1 ] && IT_FLAG="-it"
    docker run --rm $IT_FLAG \
        -e WORKSPACE_CHOWN_MODE=named-only \
        -e PYTHONUNBUFFERED=1 \
        -v "$VARIANT_ROOT:$WORKSPACE_DIR" \
        -w "$WORKSPACE_DIR" \
        --gpus all \
        "$IMAGE" \
        $cmd
}

# ── 帮助 ──
show_help() {
    cat << 'HELP'
torch-dev 容器一键启动脚本

用法:
  ./scripts/start-torch-dev.sh [选项]

模式选项:
  (无参数)          DinD 长期后台模式（默认，含SSH+Jupyter+Docker）
  --dood            DooD 模式（共享宿主机Docker Socket，无需--privileged）
  --ssh-only        仅SSH最小化模式
  --test            一次性运行 test_torch.py 验证（--rm自动删除，支持GPU）
  --bash            一次性进入 bash shell（--rm自动删除）

操作选项:
  --stop            停止并删除容器
  --logs            查看容器日志（tail -f）
  --info            显示镜像/容器信息+快速验证
  -p, --ssh-port P  指定SSH端口（默认自动检测空闲端口）
  -P, --jupyter-port P  指定Jupyter端口（默认自动检测）
  --password PASS   指定SSH密码（默认 torchdev）
  --token TOKEN     指定Jupyter token（默认 torchdev123）
  --no-auto-port    禁止自动端口调整，冲突时报错退出
  --no-verify       启动后跳过 test_torch.py 自动验证
  --quick-test      启动后执行快速验证（跳过耗时算子测试）
  -h, --help        显示此帮助

环境变量:
  USER_PASSWORD     SSH密码（默认 torchdev）
  JUPYTER_TOKEN     Jupyter token（默认 torchdev123）
  SSH_PORT          SSH端口（不指定则自动检测）
  JUPYTER_PORT      Jupyter端口（不指定则自动检测）
  PROFILE           启动模式 (dind|dood|ssh-only)
  WORKSPACE_HOST_DIR 宿主机workspace目录（默认 ./workspace）
  START_DEV_DEBUG=1 启用DEBUG日志

示例:
  ./scripts/start-torch-dev.sh                        # 默认 DinD 模式，自动端口
  ./scripts/start-torch-dev.sh --dood                 # DooD 模式
  ./scripts/start-torch-dev.sh -p 2300 -P 8900        # 自定义端口
  ./scripts/start-torch-dev.sh --test                 # 运行完整验证（含GPU）
  ./scripts/start-torch-dev.sh --bash                 # 进入bash shell
  ./scripts/start-torch-dev.sh --stop                 # 停止容器
  START_DEV_DEBUG=1 ./scripts/start-torch-dev.sh      # 调试模式
HELP
}

# ── 参数解析 ──
PROFILE="dind"
ACTION_START=true
ACTION_STOP=false
ACTION_LOGS=false
ACTION_INFO=false
ACTION_TEST=false
ACTION_BASH=false
AUTO_PORT=1
RUN_VERIFY=1
QUICK_TEST=0
USER_PASSWORD="${USER_PASSWORD:-$DEFAULT_PASSWORD}"
JUPYTER_TOKEN="${JUPYTER_TOKEN:-$DEFAULT_TOKEN}"
SSH_PORT="${SSH_PORT:-}"
JUPYTER_PORT="${JUPYTER_PORT:-}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dood)      PROFILE="dood"; shift ;;
        --ssh-only)  PROFILE="ssh-only"; shift ;;
        --dind)      PROFILE="dind"; shift ;;
        --stop)      ACTION_STOP=true; ACTION_START=false; shift ;;
        --logs)      ACTION_LOGS=true; ACTION_START=false; shift ;;
        --info)      ACTION_INFO=true; ACTION_START=false; shift ;;
        --test)      ACTION_TEST=true; ACTION_START=false; shift ;;
        --bash)      ACTION_BASH=true; ACTION_START=false; shift ;;
        -p|--ssh-port)     SSH_PORT="$2"; shift 2 ;;
        -P|--jupyter-port) JUPYTER_PORT="$2"; shift 2 ;;
        --password)  USER_PASSWORD="$2"; shift 2 ;;
        --token)     JUPYTER_TOKEN="$2"; shift 2 ;;
        --no-auto-port) AUTO_PORT=0; shift ;;
        --no-verify) RUN_VERIFY=0; shift ;;
        --quick-test) QUICK_TEST=1; shift ;;
        -h|--help)   show_help; exit 0 ;;
        -*)          error "未知选项: $1"; echo ""; show_help; exit 1 ;;
        *)           error "未知参数: $1"; shift ;;
    esac
done

debug "PROFILE=$PROFILE ACTION_START=$ACTION_START ACTION_STOP=$ACTION_STOP"
debug "AUTO_PORT=$AUTO_PORT RUN_VERIFY=$RUN_VERIFY"

# ── 主流程 ──
check_docker
check_compose_file

# 信息/停止/日志 不需要镜像存在
if [[ "$ACTION_INFO" == true ]]; then
    check_image
    show_info
    exit 0
fi

if [[ "$ACTION_STOP" == true ]]; then
    check_image 2>/dev/null || true
    stop_container
    exit 0
fi

check_image

if [[ "$ACTION_LOGS" == true ]]; then
    show_logs
    exit 0
fi

# ── Ephemeral 模式：一次性执行 ──
if [[ "$ACTION_TEST" == true ]]; then
    info "一次性模式：运行 test_torch.py 综合验证（--rm，--gpus all）"
    run_ephemeral "$PYTHON_BIN $TEST_SCRIPT_EPHEMERAL"
    exit $?
fi

if [[ "$ACTION_BASH" == true ]]; then
    info "一次性模式：进入 bash shell（--rm）"
    run_ephemeral "bash"
    exit $?
fi

# ── Daemon 长期模式 ──
# 端口解析与冲突检测
resolve_ports "$AUTO_PORT"

# 停止已有容器
stop_container 2>/dev/null || true

info "启动 $PROFILE 模式..."
info "  SSH端口: $SSH_PORT"
[[ "$PROFILE" != "ssh-only" ]] && info "  Jupyter端口: $JUPYTER_PORT"
info "  挂载: $WORKSPACE_HOST_DIR -> $WORKSPACE_DIR"
info "  Compose: $COMPOSE_FILE (profile=$PROFILE)"

# 启动容器
export SSH_PORT JUPYTER_PORT USER_PASSWORD JUPYTER_TOKEN
if [[ "$PROFILE" == "dood" ]]; then
    SSH_PORT_DOOD="$SSH_PORT" JUPYTER_PORT_DOOD="$JUPYTER_PORT" \
    WORKSPACE_DIR="$WORKSPACE_HOST_DIR" \
    $COMPOSE -f "$COMPOSE_FILE" --profile "$PROFILE" up -d 2>&1 | while IFS= read -r line; do debug "$line"; done
else
    WORKSPACE_DIR="$WORKSPACE_HOST_DIR" \
    $COMPOSE -f "$COMPOSE_FILE" --profile "$PROFILE" up -d 2>&1 | while IFS= read -r line; do debug "$line"; done
fi

# 确定实际容器名
if [[ "$PROFILE" == "dood" ]]; then
    CONTAINER_NAME="torch-dev-dood"
elif [[ "$PROFILE" == "ssh-only" ]]; then
    CONTAINER_NAME="torch-dev-ssh"
fi

sleep 2
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    error "容器启动失败！"
    error "查看日志: docker logs $CONTAINER_NAME"
    exit 1
fi
ok "容器已启动"

# 等待健康
wait_for_healthy "$CONTAINER_NAME" "$HEALTH_TIMEOUT" || true

# 运行验证
if [[ "$RUN_VERIFY" == "1" ]] && [[ "$PROFILE" != "ssh-only" ]]; then
    run_torch_test "$QUICK_TEST" || true
fi

# 显示连接信息
show_connection_info
