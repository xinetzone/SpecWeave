#!/usr/bin/env bash
# ==============================================================================
# Jupyter SSH Base 一键运行脚本
# ==============================================================================
# 用法:
#   ./run.sh [命令] [选项]
#
# 命令:
#   build     构建镜像
#   run       构建并启动容器（后台运行 Jupyter + SSH）
#   stop      停止运行中的容器
#   shell     进入运行中容器的 bash shell
#   ssh       显示 SSH 连接命令并尝试连接
#   logs      查看容器日志
#   verify    运行容器内验证脚本
#   clean     删除容器和镜像
#   rebuild   清理后从头构建（--no-cache）
#   info      显示访问信息
#
# 选项:
#   --no-cache            构建时不使用 Docker 缓存
#   --no-build            启动时跳过构建（镜像必须已存在）
#   --workdir <dir>       挂载指定目录到 /workspace（默认: ./workspace）
#   --ssh-port <port>     主机 SSH 端口（默认: 2223）
#   --jupyter-port <port> 主机 Jupyter 端口（默认: 8889）
#   --password <pwd>      设置 SSH 密码（默认: changeme）
#   --token <token>       设置 Jupyter token（默认: jupyter123）
#   --ssh-key <path>      SSH 公钥路径（默认自动检测 ~/.ssh/id_*.pub）
#   --no-ssh-key          禁用自动加载 SSH 公钥
#   --name <name>         容器名称（默认: jupyter-ssh-base）
#   --compose             使用 docker compose 模式（默认: docker run）
#   -h, --help            显示帮助
# ==============================================================================

set -euo pipefail

# ------------------------------------------------------------------------------
# 路径配置
# ------------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
cd "$PROJECT_DIR"

# ------------------------------------------------------------------------------
# 默认配置
# ------------------------------------------------------------------------------
IMAGE_NAME="${IMAGE_NAME:-jupyter-ssh-base}"
IMAGE_TAG="${IMAGE_TAG:-1.1}"
CONTAINER_NAME="jupyter-ssh-base"
SSH_PORT="2223"
JUPYTER_PORT="8889"
USER_PASSWORD="changeme"
JUPYTER_TOKEN="jupyter123"
MOUNT_WORKDIR=""
NO_CACHE=""
SKIP_BUILD=false
USE_COMPOSE=false
SSH_KEY_PATH=""

# ------------------------------------------------------------------------------
# SSH 公钥自动检测
# ------------------------------------------------------------------------------
detect_ssh_key() {
    if [ -n "${SSH_KEY_PATH}" ]; then
        return 0
    fi
    # 按优先级检测：ed25519 > rsa
    for key in "${HOME}/.ssh/id_ed25519.pub" "${HOME}/.ssh/id_rsa.pub"; do
        if [ -f "$key" ]; then
            SSH_KEY_PATH="$key"
            return 0
        fi
    done
    return 1
}

# ------------------------------------------------------------------------------
# 彩色输出
# ------------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

print_ok()    { echo -e "${GREEN}  [OK]${NC} $1"; }
print_warn()  { echo -e "${YELLOW}  [WARN]${NC} $1"; }
print_error() { echo -e "${RED}  [ERROR]${NC} $1"; }
print_info()  { echo -e "${MAGENTA}  [INFO]${NC} $1"; }
print_step()  { echo -e "${CYAN}==>${NC} $1"; }

# ------------------------------------------------------------------------------
# 帮助信息
# ------------------------------------------------------------------------------
usage() {
    cat << 'EOF'
Jupyter SSH Base 一键运行脚本

用法: ./run.sh [命令] [选项]

命令:
  build     构建镜像
  run       构建并启动容器（后台运行 Jupyter + SSH）
  stop      停止运行中的容器
  shell     进入运行中容器的 bash shell
  ssh       显示 SSH 连接命令并尝试连接
  logs      查看容器日志
  verify    运行容器内验证脚本
  clean     删除容器和镜像
  rebuild   清理后从头构建（--no-cache）
  info      显示访问信息

选项:
  --no-cache            构建时不使用 Docker 缓存
  --no-build            启动时跳过构建
  --workdir <dir>       挂载指定目录到 /workspace（默认: ./workspace）
  --ssh-port <port>     主机 SSH 端口（默认: 2223）
  --jupyter-port <port> 主机 Jupyter 端口（默认: 8889）
  --password <pwd>      设置 SSH 密码（默认: changeme）
  --token <token>       设置 Jupyter token（默认: jupyter123）
  --ssh-key <path>      SSH 公钥路径（默认自动检测 ~/.ssh/id_*.pub）
  --no-ssh-key          禁用自动加载 SSH 公钥
  --name <name>         容器名称（默认: jupyter-ssh-base）
  --compose             使用 docker compose 模式（默认: docker run）
  -h, --help            显示帮助

示例:
  ./run.sh run                              # 一键启动（自动检测 SSH 公钥）
  ./run.sh run --workdir ~/my-project       # 挂载指定目录
  ./run.sh run --ssh-port 2222 --jupyter-port 8888  # 自定义端口
  ./run.sh run --ssh-key ~/.ssh/id_ed25519.pub       # 指定公钥
  ./run.sh run --compose                    # 使用 docker compose 启动
  ./run.sh info                             # 查看访问信息
  ./run.sh logs                             # 查看日志
  ./run.sh ssh                              # SSH 连接
EOF
}

# ------------------------------------------------------------------------------
# 构建镜像
# ------------------------------------------------------------------------------
build_image() {
    local full_image="${IMAGE_NAME}:${IMAGE_TAG}"
    if docker image inspect "$full_image" &>/dev/null && [ -z "$NO_CACHE" ]; then
        print_ok "镜像已存在: $full_image (跳过构建，使用 --rebuild 强制重建)"
        return 0
    fi

    print_step "构建 ${full_image}..."
    DOCKER_BUILDKIT=1 docker build \
        $NO_CACHE \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        -t "$full_image" \
        .
    print_ok "镜像构建完成: $full_image"
    docker images "$full_image" --format "  大小: {{.Size}}"
}

# ------------------------------------------------------------------------------
# 停止并清理已存在的同名容器
# ------------------------------------------------------------------------------
stop_existing_container() {
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_step "停止并删除已有容器 ${CONTAINER_NAME}..."
        docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true
        print_ok "旧容器已清理"
    fi
}

# ------------------------------------------------------------------------------
# 启动容器（docker run 模式）
# ------------------------------------------------------------------------------
run_container_docker() {
    local full_image="${IMAGE_NAME}:${IMAGE_TAG}"

    if ! $SKIP_BUILD; then
        build_image
    fi

    if ! docker image inspect "$full_image" &>/dev/null; then
        print_error "镜像 ${full_image} 不存在，请先构建: ./run.sh build"
        exit 1
    fi

    stop_existing_container

    local abs_workdir="${MOUNT_WORKDIR:-${PROJECT_DIR}/workspace}"
    mkdir -p "$abs_workdir"

    print_step "启动容器 ${CONTAINER_NAME}（后台运行）..."

    local docker_args=(run -d)
    docker_args+=(--name "${CONTAINER_NAME}")
    docker_args+=(-p "${SSH_PORT}:22")
    docker_args+=(-p "${JUPYTER_PORT}:8888")
    docker_args+=(-v "${abs_workdir}:/workspace")
    docker_args+=(-e "USER_PASSWORD=${USER_PASSWORD}")
    docker_args+=(-e "JUPYTER_TOKEN=${JUPYTER_TOKEN}")
    docker_args+=(-e "TZ=Asia/Shanghai")
    docker_args+=(--restart unless-stopped)
    docker_args+=(--health-cmd "curl -f http://localhost:8888/api || exit 1")
    docker_args+=(--health-interval 30s)
    docker_args+=(--health-timeout 10s)
    docker_args+=(--health-retries 3)
    docker_args+=(--health-start-period 45s)
    docker_args+=(-t)

    # SSH 公钥自动检测与注入
    if detect_ssh_key; then
        local pubkey_content
        pubkey_content=$(cat "$SSH_KEY_PATH")
        docker_args+=(-e "SSH_PUBLIC_KEY=${pubkey_content}")
        print_ok "SSH 公钥已注入: $(basename "$SSH_KEY_PATH")"
    else
        print_warn "未找到 SSH 公钥，仅支持密码登录（使用 --ssh-key 指定或 --no-ssh-key 静默）"
    fi

    docker_args+=("$full_image")

    docker "${docker_args[@]}"

    print_ok "容器已启动"
    print_ok "SSH 端口: ${SSH_PORT} -> 22"
    print_ok "Jupyter 端口: ${JUPYTER_PORT} -> 8888"
    print_ok "工作目录: ${abs_workdir} -> /workspace"

    sleep 3
    echo ""
    show_access_info
}

# ------------------------------------------------------------------------------
# 启动容器（docker compose 模式）
# ------------------------------------------------------------------------------
run_container_compose() {
    if ! $SKIP_BUILD; then
        build_image
    fi

    stop_existing_container

    print_step "使用 docker compose 启动..."
    docker compose up -d

    print_ok "容器已启动（Compose 模式）"
    sleep 3
    echo ""
    show_access_info
}

# ------------------------------------------------------------------------------
# 停止容器
# ------------------------------------------------------------------------------
stop_container() {
    if $USE_COMPOSE; then
        docker compose down
        print_ok "容器已停止（Compose 模式）"
        return
    fi

    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_step "停止容器 ${CONTAINER_NAME}..."
        docker stop "${CONTAINER_NAME}"
        print_ok "容器已停止"
    elif docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_warn "容器 ${CONTAINER_NAME} 已经是停止状态"
    else
        print_warn "容器 ${CONTAINER_NAME} 不存在"
    fi
}

# ------------------------------------------------------------------------------
# 进入容器 shell
# ------------------------------------------------------------------------------
shell_into_container() {
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_step "进入容器 ${CONTAINER_NAME}..."
        exec docker exec -it "${CONTAINER_NAME}" /bin/bash
    elif docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_step "容器已停止，先启动再进入..."
        docker start "${CONTAINER_NAME}"
        sleep 2
        exec docker exec -it "${CONTAINER_NAME}" /bin/bash
    else
        print_error "容器 ${CONTAINER_NAME} 不存在，请先运行: ./run.sh run"
        exit 1
    fi
}

# ------------------------------------------------------------------------------
# SSH 连接
# ------------------------------------------------------------------------------
ssh_connect() {
    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_error "容器 ${CONTAINER_NAME} 未运行，请先启动: ./run.sh run"
        exit 1
    fi

    echo ""
    echo -e "${CYAN}SSH 连接信息${NC}"
    echo ""
    echo -e "  命令:     ${GREEN}ssh -p ${SSH_PORT} jupyteruser@localhost${NC}"
    echo -e "  密码:     ${GREEN}${USER_PASSWORD}${NC}"
    echo ""

    if command -v ssh &>/dev/null; then
        print_step "尝试建立 SSH 连接..."
        ssh -o StrictHostKeyChecking=no -p "${SSH_PORT}" jupyteruser@localhost || true
    else
        print_warn "未找到 ssh 命令，请手动执行上述连接命令"
    fi
}

# ------------------------------------------------------------------------------
# 查看日志
# ------------------------------------------------------------------------------
show_logs() {
    if $USE_COMPOSE; then
        docker compose logs -f
        return
    fi

    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_step "容器 ${CONTAINER_NAME} 日志（按 Ctrl+C 退出）:"
        echo ""
        docker logs -f "${CONTAINER_NAME}"
    else
        print_error "容器 ${CONTAINER_NAME} 不存在"
        exit 1
    fi
}

# ------------------------------------------------------------------------------
# 运行验证
# ------------------------------------------------------------------------------
verify_container() {
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_step "在运行中的容器上执行验证..."
        echo ""
        docker exec "${CONTAINER_NAME}" /usr/local/bin/healthcheck.sh
        echo ""
        print_step "SSH 非交互路径验证..."
        docker exec "${CONTAINER_NAME}" /bin/bash -c 'ssh -o StrictHostKeyChecking=no -p 22 jupyteruser@localhost "which jupyter"' 2>/dev/null || \
            print_warn "SSH 非交互路径验证失败（容器内自环测试）"
    else
        print_error "容器 ${CONTAINER_NAME} 未运行，请先启动"
        exit 1
    fi
}

# ------------------------------------------------------------------------------
# 清理
# ------------------------------------------------------------------------------
clean_all() {
    local full_image="${IMAGE_NAME}:${IMAGE_TAG}"

    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true
        print_ok "容器已删除"
    fi

    if docker image inspect "$full_image" &>/dev/null; then
        docker rmi "$full_image" 2>/dev/null || true
        print_ok "镜像已删除: $full_image"
    else
        print_warn "镜像不存在，无需删除"
    fi

    print_ok "清理完成"
}

# ------------------------------------------------------------------------------
# 显示访问信息
# ------------------------------------------------------------------------------
show_access_info() {
    echo -e "${CYAN}Jupyter SSH Base 访问信息${NC}"
    echo ""

    echo -e "${GREEN}Jupyter Notebook:${NC}"
    echo -e "  URL:      ${MAGENTA}http://localhost:${JUPYTER_PORT}/?token=${JUPYTER_TOKEN}${NC}"
    echo ""

    echo -e "${MAGENTA}SSH 连接:${NC}"
    echo -e "  命令:     ${GREEN}ssh -p ${SSH_PORT} jupyteruser@localhost${NC}"
    echo -e "  密码:     ${GREEN}${USER_PASSWORD}${NC}"
    echo ""

    echo -e "${YELLOW}容器信息:${NC}"
    echo -e "  名称:     ${CONTAINER_NAME}"
    echo -e "  镜像:     ${IMAGE_NAME}:${IMAGE_TAG}"
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "  状态:     ${GREEN}运行中${NC}"
    elif docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "  状态:     ${YELLOW}已停止${NC}"
    else
        echo -e "  状态:     ${RED}不存在${NC}"
    fi
    echo ""

    echo -e "${YELLOW}快速命令:${NC}"
    echo "  查看日志:   ./run.sh logs"
    echo "  进入Shell:  ./run.sh shell"
    echo "  SSH连接:    ./run.sh ssh"
    echo "  停止容器:   ./run.sh stop"
    echo "  重新启动:   ./run.sh run --no-build"
    echo ""
}

# ------------------------------------------------------------------------------
# 显示完整信息
# ------------------------------------------------------------------------------
show_info() {
    echo ""
    echo -e "${CYAN}Jupyter SSH Base 完整信息${NC}"
    echo ""

    local full_image="${IMAGE_NAME}:${IMAGE_TAG}"
    echo -e "${YELLOW}镜像信息:${NC}"
    if docker image inspect "$full_image" &>/dev/null; then
        docker images "$full_image" --format "  名称: {{.Repository}}:{{.Tag}}"
        docker images "$full_image" --format "  大小: {{.Size}}"
        docker images "$full_image" --format "  创建: {{.CreatedSince}}"
    else
        echo "  (镜像不存在，请运行 ./run.sh build)"
    fi
    echo ""

    show_access_info
}

# ------------------------------------------------------------------------------
# 命令行参数解析
# ------------------------------------------------------------------------------
parse_args() {
    COMMAND="run"

    while [ $# -gt 0 ]; do
        case "$1" in
            build|run|stop|shell|ssh|logs|verify|clean|rebuild|info)
                COMMAND="$1"
                shift
                ;;
            --no-cache)
                NO_CACHE="--no-cache"
                shift
                ;;
            --no-build)
                SKIP_BUILD=true
                shift
                ;;
            --workdir)
                MOUNT_WORKDIR="$2"
                shift 2
                ;;
            --ssh-port)
                SSH_PORT="$2"
                shift 2
                ;;
            --jupyter-port)
                JUPYTER_PORT="$2"
                shift 2
                ;;
            --password)
                USER_PASSWORD="$2"
                shift 2
                ;;
            --token)
                JUPYTER_TOKEN="$2"
                shift 2
                ;;
            --ssh-key)
                SSH_KEY_PATH="$2"
                shift 2
                ;;
            --no-ssh-key)
                SSH_KEY_PATH=""
                shift
                ;;
            --name)
                CONTAINER_NAME="$2"
                shift 2
                ;;
            --compose)
                USE_COMPOSE=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                print_error "未知参数: $1"
                echo ""
                usage
                exit 1
                ;;
        esac
    done

    # 默认命令是 run
    if [ -z "${COMMAND:-}" ]; then
        COMMAND="run"
    fi
}

# ------------------------------------------------------------------------------
# 主函数
# ------------------------------------------------------------------------------
main() {
    parse_args "$@"

    case "${COMMAND}" in
        build)
            build_image
            echo ""
            print_ok "构建完成！运行 './run.sh run' 启动服务"
            ;;
        run)
            if $USE_COMPOSE; then
                run_container_compose
            else
                run_container_docker
            fi
            ;;
        stop)
            stop_container
            ;;
        shell)
            shell_into_container
            ;;
        ssh)
            ssh_connect
            ;;
        logs)
            show_logs
            ;;
        verify)
            verify_container
            ;;
        clean)
            clean_all
            ;;
        rebuild)
            NO_CACHE="--no-cache"
            clean_all
            build_image
            echo ""
            print_ok "重新构建完成！运行 './run.sh run' 启动服务"
            ;;
        info)
            show_info
            ;;
    esac
}

main "$@"