#!/usr/bin/env bash
# =============================================================================
# onnx-dev 容器一键启动脚本
# 自动检测环境，默认 Ephemeral（一次性）模式，支持 Persistent（长期后台）模式
#
# 用法:
#   ./scripts/start-dev.sh                      # 一次性 Python 交互模式（--rm）
#   ./scripts/start-dev.sh inference_demo.py    # 一次性运行 examples/ 下的脚本
#   ./scripts/start-dev.sh ft_compat_check.py   # 一次性运行 tools/ 下的脚本
#   ./scripts/start-dev.sh -d                   # 长期后台模式（SSH+Jupyter+DinD）
#   ./scripts/start-dev.sh -d -p 2222 -P 8888   # 自定义端口的长期模式
#   ./scripts/start-dev.sh -d --stop            # 停止并删除已有容器
#   ./scripts/start-dev.sh -d --logs            # 查看后台容器日志
#   ./scripts/start-dev.sh --bash               # 一次性模式进入 bash shell
#   ./scripts/start-dev.sh --info               # 显示镜像和容器信息
# =============================================================================
set -euo pipefail

IMAGE="devcontainer-base:onnx-dev-latest"
CONTAINER_NAME="onnx-dev"
DEFAULT_SSH_PORT=2222
DEFAULT_JUPYTER_PORT=8888
DEFAULT_PASSWORD="onnxdev"
DEFAULT_TOKEN="onnxdev"
WORKSPACE_DIR="/workspace"
PYTHON_BIN="/opt/conda/envs/main/bin/python"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$VARIANT_ROOT"

# 智能解析脚本路径：支持直接写文件名（自动查找 examples/ tools/）或显式路径
resolve_script_path() {
    local input="$1"
    if [[ -f "$VARIANT_ROOT/$input" ]]; then
        echo "$input"
    elif [[ -f "$VARIANT_ROOT/examples/$input" ]]; then
        echo "examples/$input"
    elif [[ -f "$VARIANT_ROOT/tools/$input" ]]; then
        echo "tools/$input"
    else
        echo "$input"
    fi
}

check_docker() {
    if ! command -v docker &>/dev/null; then
        error "Docker 未安装或不在 PATH 中"
        exit 1
    fi
    if ! docker info &>/dev/null; then
        error "Docker daemon 未运行或无权限"
        exit 1
    fi
}

check_image() {
    if ! docker image inspect "$IMAGE" &>/dev/null; then
        error "镜像 $IMAGE 不存在，请先构建："
        echo "  cd variants && bash build.sh --variant onnx-dev --cn"
        exit 1
    fi
}

stop_existing() {
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        info "停止并删除已有容器 $CONTAINER_NAME ..."
        docker rm -f "$CONTAINER_NAME" &>/dev/null || true
        ok "已清理"
    fi
}

show_persistent_info() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  🚀 onnx-dev 长期开发容器已就绪${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${YELLOW}SSH 登录:${NC}"
    echo -e "    ssh devuser@localhost -p $SSH_PORT"
    echo -e "    密码: $PASSWORD"
    echo ""
    echo -e "  ${YELLOW}Jupyter Notebook:${NC}"
    echo -e "    http://localhost:$JUPYTER_PORT/?token=$TOKEN"
    echo ""
    echo -e "  ${YELLOW}进入容器:${NC}"
    echo -e "    docker exec -it $CONTAINER_NAME bash"
    echo ""
    echo -e "  ${YELLOW}目录结构:${NC}"
    echo -e "    /workspace/           ← 变体根目录（挂载点）"
    echo -e "    /workspace/examples/  ← 示例代码"
    echo -e "    /workspace/tools/     ← 工具脚本"
    echo -e "    /workspace/scripts/   ← 启动/运维脚本"
    echo ""
    echo -e "  ${YELLOW}常用命令:${NC}"
    echo -e "    查看日志:  $0 -d --logs"
    echo -e "    停止容器:  $0 -d --stop"
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
}

show_info() {
    echo -e "${CYAN}═══ onnx-dev 镜像信息 ═══${NC}"
    echo ""
    docker images "$IMAGE" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    echo ""
    echo -e "${CYAN}═══ 容器状态 ═══${NC}"
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        docker ps -a --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        echo "  无运行中的 $CONTAINER_NAME 容器"
    fi
    echo ""
    echo -e "${CYAN}═══ 快速验证 ═══${NC}"
    docker run --rm -i \
        -e WORKSPACE_CHOWN_MODE=named-only \
        -v "$VARIANT_ROOT:$WORKSPACE_DIR" \
        -w "$WORKSPACE_DIR" \
        "$IMAGE" \
        "$PYTHON_BIN" -c "import onnx,onnxruntime,sys;print(f'onnx {onnx.__version__}, onnxruntime {onnxruntime.__version__}, gil_disabled={not sys._is_gil_enabled()}')"
}

show_help() {
    cat << 'HELP'
onnx-dev 容器一键启动脚本

用法:
  ./scripts/start-dev.sh [选项] [命令/脚本...]

模式:
  (无参数)          Ephemeral 模式：启动 Python 交互环境（--rm 自动删除）
  <script.py>       Ephemeral 模式：运行指定 Python 脚本（自动查找 examples/ tools/）
  --bash            Ephemeral 模式：进入 bash shell
  -d, --daemon      Persistent 模式：后台启动（SSH+Jupyter）
  -d --stop         停止并删除 Persistent 容器
  -d --logs         查看 Persistent 容器日志
  --info            显示镜像/容器信息和快速验证
  -h, --help        显示此帮助

示例:
  ./scripts/start-dev.sh                        # Python 交互环境
  ./scripts/start-dev.sh simple_verify.py       # 运行 examples/simple_verify.py
  ./scripts/start-dev.sh inference_demo.py      # 运行 examples/inference_demo.py
  ./scripts/start-dev.sh ft_compat_check.py     # 运行 tools/ft_compat_check.py
  ./scripts/start-dev.sh --bash                 # 进入 bash
  ./scripts/start-dev.sh -d                     # 启动长期开发容器
  ./scripts/start-dev.sh -d --stop              # 停止容器
  ./scripts/start-dev.sh --info                 # 查看信息
HELP
}

# 参数解析
PERSISTENT=false
ACTION_STOP=false
ACTION_LOGS=false
ACTION_INFO=false
SSH_PORT="$DEFAULT_SSH_PORT"
JUPYTER_PORT="$DEFAULT_JUPYTER_PORT"
PASSWORD="$DEFAULT_PASSWORD"
TOKEN="$DEFAULT_TOKEN"
EPHEMERAL_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--daemon) PERSISTENT=true; shift ;;
        --stop) ACTION_STOP=true; PERSISTENT=true; shift ;;
        --logs) ACTION_LOGS=true; PERSISTENT=true; shift ;;
        -p|--ssh-port) SSH_PORT="$2"; shift 2 ;;
        -P|--jupyter-port) JUPYTER_PORT="$2"; shift 2 ;;
        --password) PASSWORD="$2"; shift 2 ;;
        --token) TOKEN="$2"; shift 2 ;;
        --name) CONTAINER_NAME="$2"; shift 2 ;;
        --info) ACTION_INFO=true; shift ;;
        --bash) EPHEMERAL_ARGS=("--bash"); shift ;;
        -h|--help) show_help; exit 0 ;;
        -*) error "未知选项: $1"; exit 1 ;;
        *) EPHEMERAL_ARGS+=("$1"); shift ;;
    esac
done

# 主流程
check_docker
check_image

if [[ "$ACTION_INFO" == true ]]; then
    show_info
    exit 0
fi

if [[ "$PERSISTENT" == true ]]; then
    if [[ "$ACTION_STOP" == true ]]; then
        stop_existing
        exit 0
    fi
    if [[ "$ACTION_LOGS" == true ]]; then
        docker logs -f "$CONTAINER_NAME"
        exit 0
    fi
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        warn "容器 $CONTAINER_NAME 已在运行中"
        show_persistent_info
        exit 0
    fi
    stop_existing
    info "启动 Persistent 模式（后台长期开发容器）..."
    info "  SSH 端口: $SSH_PORT, Jupyter 端口: $JUPYTER_PORT"
    info "  挂载目录: $VARIANT_ROOT -> $WORKSPACE_DIR"
    docker run -d \
        --name "$CONTAINER_NAME" \
        --privileged \
        -p "${SSH_PORT}:22" \
        -p "${JUPYTER_PORT}:8888" \
        -e "USER_PASSWORD=$PASSWORD" \
        -e "JUPYTER_TOKEN=$TOKEN" \
        -e "GRANT_SUDO=yes" \
        -e "TZ=Asia/Shanghai" \
        -v "$VARIANT_ROOT:$WORKSPACE_DIR" \
        "$IMAGE"
    sleep 2
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        ok "容器启动成功！"
        echo ""
        show_persistent_info
    else
        error "容器启动失败"
        exit 1
    fi
else
    IT_FLAG="-i"
    if [ -t 0 ] && [ -t 1 ]; then
        IT_FLAG="-it"
    fi

    if [[ ${#EPHEMERAL_ARGS[@]} -eq 0 ]]; then
        info "启动 Ephemeral 模式（Python 交互环境，退出即删）..."
        DOCKER_CMD="$PYTHON_BIN"
    elif [[ "${EPHEMERAL_ARGS[0]}" == "--bash" ]]; then
        info "启动 Ephemeral 模式（bash shell，退出即删）..."
        DOCKER_CMD="bash"
    else
        # 智能解析脚本路径
        script_path="$(resolve_script_path "${EPHEMERAL_ARGS[0]}")"
        if [[ ${#EPHEMERAL_ARGS[@]} -gt 1 ]]; then
            script_args="${EPHEMERAL_ARGS[@]:1}"
            info "启动 Ephemeral 模式运行: $script_path $script_args"
            DOCKER_CMD="$PYTHON_BIN $script_path $script_args"
        else
            info "启动 Ephemeral 模式运行: $script_path"
            DOCKER_CMD="$PYTHON_BIN $script_path"
        fi
    fi
    echo ""
    docker run --rm $IT_FLAG \
        -e "WORKSPACE_CHOWN_MODE=named-only" \
        -v "$VARIANT_ROOT:$WORKSPACE_DIR" \
        -w "$WORKSPACE_DIR" \
        "$IMAGE" \
        $DOCKER_CMD
fi
