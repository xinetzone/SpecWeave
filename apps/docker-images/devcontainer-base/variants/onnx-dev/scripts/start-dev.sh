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
#
# 调试模式:
#   START_DEV_DEBUG=1 ./scripts/start-dev.sh ... # 启用详细DEBUG日志
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

# ── 颜色 ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m'

# ── 日志函数 ──
DEBUG_MODE="${START_DEV_DEBUG:-0}"

debug() {
    if [[ "$DEBUG_MODE" == "1" ]]; then
        echo -e "${GRAY}[DEBUG]${NC} $*" >&2
    fi
}
info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ── 路径解析与初始化 ──
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$VARIANT_ROOT"

debug "========== 启动脚本初始化 =========="
debug "BASH_SOURCE[0] = ${BASH_SOURCE[0]}"
debug "SCRIPT_DIR     = $SCRIPT_DIR"
debug "VARIANT_ROOT   = $VARIANT_ROOT"
debug "PWD (after cd) = $(pwd)"
debug "DEBUG_MODE     = $DEBUG_MODE"
debug ""
debug "目录结构检查:"
debug "  scripts/ 存在: $([[ -d "$VARIANT_ROOT/scripts" ]] && echo '✅' || echo '❌')"
debug "  examples/ 存在: $([[ -d "$VARIANT_ROOT/examples" ]] && echo '✅' || echo '❌')"
debug "  tools/    存在: $([[ -d "$VARIANT_ROOT/tools" ]] && echo '✅' || echo '❌')"
debug "  docs/     存在: $([[ -d "$VARIANT_ROOT/docs" ]] && echo '✅' || echo '❌')"
debug ""
if [[ "$DEBUG_MODE" == "1" ]]; then
    debug "scripts/ 内容: $(ls -1 "$VARIANT_ROOT/scripts/" 2>/dev/null | tr '\n' ' ')"
    debug "examples/ 内容: $(ls -1 "$VARIANT_ROOT/examples/" 2>/dev/null | tr '\n' ' ')"
    debug "tools/    内容: $(ls -1 "$VARIANT_ROOT/tools/" 2>/dev/null | tr '\n' ' ')"
    debug ""
fi

# 智能解析脚本路径：支持直接写文件名（自动查找 examples/ tools/）或显式路径
resolve_script_path() {
    local input="$1"
    debug "resolve_script_path: 输入='$input'"

    # 1. 检查绝对路径（容器内）
    if [[ "$input" == /* ]]; then
        debug "resolve_script_path: 检测到绝对路径，直接返回 '$input'"
        echo "$input"
        return
    fi

    # 2. 检查相对于 VARIANT_ROOT 的路径
    local candidates=(
        "$VARIANT_ROOT/$input"
        "$VARIANT_ROOT/examples/$input"
        "$VARIANT_ROOT/tools/$input"
        "$VARIANT_ROOT/scripts/$input"
    )
    local labels=("根目录" "examples/" "tools/" "scripts/")

    for i in "${!candidates[@]}"; do
        local cand="${candidates[$i]}"
        local label="${labels[$i]}"
        debug "resolve_script_path: 检查[$i] $label: $cand"
        if [[ -f "$cand" ]]; then
            local resolved
            if [[ $i -eq 0 ]]; then
                resolved="$input"
            else
                resolved="${label%/}/$input"
            fi
            debug "resolve_script_path: ✅ 找到! 解析为 '$resolved'"
            echo "$resolved"
            return
        fi
    done

    # 3. 没找到，返回原始输入（docker run时会报错）
    debug "resolve_script_path: ❌ 未找到文件，返回原始输入 '$input'（docker run时将报文件不存在）"
    echo "$input"
}

check_docker() {
    debug "check_docker: 检查 docker 命令..."
    if ! command -v docker &>/dev/null; then
        error "Docker 未安装或不在 PATH 中"
        error "当前 PATH: $PATH"
        exit 1
    fi
    debug "check_docker: docker 命令存在: $(command -v docker)"
    if ! docker info &>/dev/null; then
        error "Docker daemon 未运行或无权限"
        error "请尝试: sudo service docker start 或检查 Docker Desktop"
        exit 1
    fi
    debug "check_docker: docker daemon 可访问"
}

check_image() {
    debug "check_image: 检查镜像 $IMAGE ..."
    if ! docker image inspect "$IMAGE" &>/dev/null; then
        error "镜像 $IMAGE 不存在，请先构建："
        echo "  cd variants && bash build.sh --variant onnx-dev --cn"
        exit 1
    fi
    local img_size
    img_size=$(docker images "$IMAGE" --format '{{.Size}}' 2>/dev/null | head -1)
    debug "check_image: 镜像存在，大小=$img_size"
}

stop_existing() {
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        info "停止并删除已有容器 $CONTAINER_NAME ..."
        debug "stop_existing: 执行 docker rm -f $CONTAINER_NAME"
        docker rm -f "$CONTAINER_NAME" &>/dev/null || true
        ok "已清理"
    else
        debug "stop_existing: 无已有容器 $CONTAINER_NAME"
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
    echo -e "${CYAN}═══ 快速验证（import onnx + onnxruntime）═══${NC}"
    debug "show_info: 执行快速验证 docker run..."
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
  <script.py>       Ephemeral 模式：运行指定 Python 脚本（自动查找 examples/ tools/ scripts/）
  --bash            Ephemeral 模式：进入 bash shell
  -d, --daemon      Persistent 模式：后台启动（SSH+Jupyter）
  -d --stop         停止并删除 Persistent 容器
  -d --logs         查看 Persistent 容器日志
  --info            显示镜像/容器信息和快速验证
  -h, --help        显示此帮助

调试:
  START_DEV_DEBUG=1 ./scripts/start-dev.sh ...  启用详细 DEBUG 日志（路径解析、docker命令等）

示例:
  ./scripts/start-dev.sh                        # Python 交互环境
  ./scripts/start-dev.sh simple_verify.py       # 运行 examples/simple_verify.py
  ./scripts/start-dev.sh inference_demo.py      # 运行 examples/inference_demo.py
  ./scripts/start-dev.sh ft_compat_check.py     # 运行 tools/ft_compat_check.py
  ./scripts/start-dev.sh scripts/run_all_tests.sh  # 运行脚本（bash）
  ./scripts/start-dev.sh --bash                 # 进入 bash
  ./scripts/start-dev.sh -d                     # 启动长期开发容器
  ./scripts/start-dev.sh -d --stop              # 停止容器
  ./scripts/start-dev.sh --info                 # 查看信息
HELP
}

# ── 参数解析 ──
debug "========== 参数解析 =========="
debug "原始参数: $*"

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
        -d|--daemon)
            debug "参数: -d/--daemon (Persistent模式)"
            PERSISTENT=true; shift ;;
        --stop)
            debug "参数: --stop"
            ACTION_STOP=true; PERSISTENT=true; shift ;;
        --logs)
            debug "参数: --logs"
            ACTION_LOGS=true; PERSISTENT=true; shift ;;
        -p|--ssh-port)
            debug "参数: -p/--ssh-port = $2"
            SSH_PORT="$2"; shift 2 ;;
        -P|--jupyter-port)
            debug "参数: -P/--jupyter-port = $2"
            JUPYTER_PORT="$2"; shift 2 ;;
        --password)
            debug "参数: --password = (hidden)"
            PASSWORD="$2"; shift 2 ;;
        --token)
            debug "参数: --token = (hidden)"
            TOKEN="$2"; shift 2 ;;
        --name)
            debug "参数: --name = $2"
            CONTAINER_NAME="$2"; shift 2 ;;
        --info)
            debug "参数: --info"
            ACTION_INFO=true; shift ;;
        --bash)
            debug "参数: --bash"
            EPHEMERAL_ARGS=("--bash"); shift ;;
        -h|--help)
            show_help; exit 0 ;;
        -*)
            error "未知选项: $1"; exit 1 ;;
        *)
            debug "参数: 位置参数 '$1'"
            EPHEMERAL_ARGS+=("$1"); shift ;;
    esac
done

debug "解析结果: PERSISTENT=$PERSISTENT ACTION_STOP=$ACTION_STOP ACTION_LOGS=$ACTION_LOGS ACTION_INFO=$ACTION_INFO"
debug "  SSH_PORT=$SSH_PORT JUPYTER_PORT=$JUPYTER_PORT"
debug "  EPHEMERAL_ARGS=(${EPHEMERAL_ARGS[*]:-})"
debug ""

# ── 主流程 ──
debug "========== 主流程 =========="
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
        debug "执行: docker logs -f $CONTAINER_NAME"
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
    persistent_cmd=(
        docker run -d
        --name "$CONTAINER_NAME"
        --privileged
        -p "${SSH_PORT}:22"
        -p "${JUPYTER_PORT}:8888"
        -e "USER_PASSWORD=$PASSWORD"
        -e "JUPYTER_TOKEN=$TOKEN"
        -e "GRANT_SUDO=yes"
        -e "TZ=Asia/Shanghai"
        -v "$VARIANT_ROOT:$WORKSPACE_DIR"
        "$IMAGE"
    )
    debug "Persistent docker 命令:"
    debug "  ${persistent_cmd[*]}"
    "${persistent_cmd[@]}"
    sleep 2
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        ok "容器启动成功！"
        echo ""
        show_persistent_info
    else
        error "容器启动失败"
        error "查看日志: docker logs $CONTAINER_NAME"
        exit 1
    fi
else
    # Ephemeral 模式
    IT_FLAG="-i"
    if [ -t 0 ] && [ -t 1 ]; then
        IT_FLAG="-it"
    fi
    debug "TTY检测: IT_FLAG=$IT_FLAG (stdin_tty=$([ -t 0 ] && echo yes || echo no) stdout_tty=$([ -t 1 ] && echo yes || echo no))"

    if [[ ${#EPHEMERAL_ARGS[@]} -eq 0 ]]; then
        info "启动 Ephemeral 模式（Python 交互环境，退出即删）..."
        DOCKER_CMD="$PYTHON_BIN"
    elif [[ "${EPHEMERAL_ARGS[0]}" == "--bash" ]]; then
        info "启动 Ephemeral 模式（bash shell，退出即删）..."
        DOCKER_CMD="bash"
    else
        # 智能解析脚本路径
        script_path="$(resolve_script_path "${EPHEMERAL_ARGS[0]}")"

        # 判断是Python脚本还是shell脚本（基于扩展名或显式路径）
        if [[ "$script_path" == *.py ]]; then
            CMD_BIN="$PYTHON_BIN"
        elif [[ "$script_path" == scripts/*.sh ]]; then
            CMD_BIN="bash"
        else
            CMD_BIN="$PYTHON_BIN"
            debug "默认使用 Python 解释器运行: $script_path"
        fi

        if [[ ${#EPHEMERAL_ARGS[@]} -gt 1 ]]; then
            script_args="${EPHEMERAL_ARGS[@]:1}"
            info "启动 Ephemeral 模式运行: $script_path $script_args"
            DOCKER_CMD="$CMD_BIN $script_path $script_args"
        else
            info "启动 Ephemeral 模式运行: $script_path"
            DOCKER_CMD="$CMD_BIN $script_path"
        fi
    fi
    echo ""
    ephemeral_cmd=(
        docker run --rm $IT_FLAG
        -e "WORKSPACE_CHOWN_MODE=named-only"
        -v "$VARIANT_ROOT:$WORKSPACE_DIR"
        -w "$WORKSPACE_DIR"
        "$IMAGE"
        $DOCKER_CMD
    )
    debug "Ephemeral docker 命令:"
    debug "  ${ephemeral_cmd[*]}"
    debug ""
    "${ephemeral_cmd[@]}"
fi
