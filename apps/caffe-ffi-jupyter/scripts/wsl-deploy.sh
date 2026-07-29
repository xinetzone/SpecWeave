#!/bin/bash
# =============================================================================
# wsl-deploy.sh — Caffe-FFI WSL 一键部署脚本
# 功能：从基础镜像构建到最终 Python 导入验证的全流程自动化
# 使用：bash scripts/wsl-deploy.sh [OPTIONS]
# 必须在 WSL2/Linux 环境中执行（从 SpecWeave 根目录或任意位置均可）
# =============================================================================
set -euo pipefail

# ── 颜色定义 ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ── 默认参数 ──
USE_CN_MIRRORS=false
NO_CACHE=""
SKIP_BASE_BUILD=false
SKIP_RUN=false
VERBOSE=false
IMAGE_TAG="latest"
CONTAINER_NAME="caffe-ffi-jupyter"
SSH_PORT=2222
JUPYTER_PORT=8888
USER_PASSWORD="deploy-test"
JUPYTER_TOKEN="deploy-token"
REBUILD=false
CLEANUP=false

# ── 日志函数 ──
log_info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }
log_step()  { echo -e "\n${BOLD}${BLUE}━━━ $* ━━━${NC}\n"; }
log_ok()    { echo -e "${GREEN}  ✔ $*${NC}"; }
log_fail()  { echo -e "${RED}  ✘ $*${NC}"; }

# ── 用法 ──
usage() {
    cat << EOF
${BOLD}Caffe-FFI WSL 一键部署脚本${NC}

用法: bash scripts/wsl-deploy.sh [选项]

${BOLD}选项:${NC}
  --cn                 使用国内镜像源（apt: aliyun, pip: aliyun, conda: tuna）
  --no-cache           构建时禁用 Docker 缓存
  --skip-base          跳过基础镜像(jupyter-ssh-base)检查/构建
  --skip-run           构建完成后不启动容器、不做运行时验证
  --rebuild            先清理旧容器和镜像再重建
  --cleanup            验证完成后自动清理容器
  --tag TAG            镜像标签（默认: latest）
  --ssh-port PORT      SSH 端口映射（默认: 2222）
  --jupyter-port PORT  Jupyter 端口映射（默认: 8888）
  --password PASS      SSH 密码（默认: deploy-test）
  --token TOKEN        Jupyter Token（默认: deploy-token）
  -v, --verbose        详细输出
  -h, --help           显示帮助信息

${BOLD}示例:${NC}
  bash scripts/wsl-deploy.sh --cn                 # 国内用户一键部署
  bash scripts/wsl-deploy.sh --cn --cleanup       # 国内用户部署+验证后自动清理
  bash scripts/wsl-deploy.sh --rebuild --no-cache # 强制重建
  bash scripts/wsl-deploy.sh --skip-run           # 仅构建不运行

${BOLD}前置条件:${NC}
  - WSL2 (Ubuntu 24.04/26.04 推荐) 或原生 Linux
  - Docker Engine 已安装且运行中
  - Docker BuildKit 支持（Docker 18.09+）
  - SpecWeave 仓库已克隆，xuanspace 子模块已初始化
EOF
}

# ── 解析命令行参数 ──
while [[ $# -gt 0 ]]; do
    case "$1" in
        --cn)              USE_CN_MIRRORS=true; shift ;;
        --no-cache)        NO_CACHE="--no-cache"; shift ;;
        --skip-base)       SKIP_BASE_BUILD=true; shift ;;
        --skip-run)        SKIP_RUN=true; shift ;;
        --rebuild)         REBUILD=true; shift ;;
        --cleanup)         CLEANUP=true; shift ;;
        --tag)             IMAGE_TAG="$2"; shift 2 ;;
        --ssh-port)        SSH_PORT="$2"; shift 2 ;;
        --jupyter-port)    JUPYTER_PORT="$2"; shift 2 ;;
        --password)        USER_PASSWORD="$2"; shift 2 ;;
        --token)           JUPYTER_TOKEN="$2"; shift 2 ;;
        -v|--verbose)      VERBOSE=true; shift ;;
        -h|--help)         usage; exit 0 ;;
        *) echo "未知选项: $1"; usage; exit 1 ;;
    esac
done

# ── 确定脚本和项目根目录 ──
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# ── 镜像源参数 ──
MIRROR_ARGS=""
if $USE_CN_MIRRORS; then
    MIRROR_ARGS="--apt-mirror aliyun --pip-mirror aliyun --conda-mirror tuna"
fi

BUILD_SCRIPT="$APP_DIR/scripts/build.sh"
BASE_BUILD_SCRIPT="$PROJECT_ROOT/apps/jupyter-ssh-base/scripts/build.sh"

# =============================================================================
# 阶段 0: 环境预检（Environment Pre-flight Check）
# =============================================================================
log_step "阶段 0/7: 环境预检"

ERRORS=0

# 0.1 WSL/Linux 检测
log_info "检测操作系统环境..."
if grep -qiE '(microsoft|wsl)' /proc/version 2>/dev/null; then
    log_ok "运行在 WSL2 环境中"
elif [ "$(uname -s)" = "Linux" ]; then
    log_ok "运行在原生 Linux 环境中"
else
    log_error "当前操作系统不是 Linux/WSL2！"
    log_error "本脚本必须在 WSL2 或 Linux 环境中运行。"
    log_error "在 Windows PowerShell 中执行: wsl 进入 WSL 环境"
    exit 1
fi

# 0.2 Docker 引擎可用性
log_info "检测 Docker 引擎..."
if ! command -v docker &>/dev/null; then
    log_error "Docker 未安装！请先安装 Docker Engine 或 Docker Desktop（启用 WSL2 后端）"
    ERRORS=$((ERRORS + 1))
elif ! docker info &>/dev/null 2>&1; then
    log_error "Docker 守护进程未运行！请启动 Docker 服务："
    log_error "  - WSL2 + Docker Desktop: 启动 Docker Desktop 应用"
    log_error "  - 原生 Linux: sudo service docker start"
    ERRORS=$((ERRORS + 1))
else
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
    log_ok "Docker 可用，版本: $DOCKER_VERSION"
fi

# 0.3 Docker Compose 命令形态检测
log_info "检测 Docker Compose..."
if docker compose version &>/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
    COMPOSE_VERSION=$(docker compose version --short 2>/dev/null || echo "plugin")
    log_ok "Docker Compose 插件可用: $COMPOSE_VERSION"
elif command -v docker-compose &>/dev/null; then
    COMPOSE_CMD="docker-compose"
    COMPOSE_VERSION=$(docker-compose --version --short 2>/dev/null || echo "standalone")
    log_ok "docker-compose 独立命令可用: $COMPOSE_VERSION"
else
    log_error "Docker Compose 不可用！请安装 docker-compose-plugin 或 docker-compose"
    ERRORS=$((ERRORS + 1))
fi

# 0.4 BuildKit 检测
log_info "检测 Docker BuildKit..."
if docker buildx version &>/dev/null 2>&1; then
    log_ok "BuildKit 可用"
else
    log_warn "BuildKit 未检测到，尝试启用 DOCKER_BUILDKIT=1"
fi

# 0.5 Git 子模块检测
log_info "检测 Git 子模块状态..."
cd "$PROJECT_ROOT"
if [ -f ".gitmodules" ]; then
    SUBMODULE_STATUS=$(git submodule status --recursive 2>/dev/null | head -5 || true)
    if echo "$SUBMODULE_STATUS" | grep -qE '^-'; then
        log_warn "部分子模块未初始化，尝试自动初始化..."
        git submodule update --init --recursive projects/xuanspace || {
            log_error "子模块初始化失败！请手动执行：git submodule update --init --recursive"
            ERRORS=$((ERRORS + 1))
        }
    else
        log_ok "Git 子模块已初始化"
    fi
else
    log_warn "未检测到 .gitmodules 文件（可能不在 git 仓库中）"
fi

# 0.6 源码目录检测
CAFFE_FFI_SRC="$PROJECT_ROOT/projects/xuanspace/libs/caffe-ffi"
if [ ! -f "$CAFFE_FFI_SRC/CMakeLists.txt" ]; then
    log_error "caffe-ffi 源码未找到: $CAFFE_FFI_SRC"
    log_error "请确认 projects/xuanspace 子模块已正确初始化"
    ERRORS=$((ERRORS + 1))
else
    log_ok "caffe-ffi 源码目录存在: $CAFFE_FFI_SRC"
fi

# 0.7 端口占用检测
log_info "检测端口占用..."
for PORT in $SSH_PORT $JUPYTER_PORT; do
    if ss -tlnp 2>/dev/null | grep -q ":$PORT " || netstat -tlnp 2>/dev/null | grep -q ":$PORT "; then
        log_warn "端口 $PORT 已被占用，可能导致容器启动失败"
    else
        log_ok "端口 $PORT 可用"
    fi
done

if [ $ERRORS -gt 0 ]; then
    log_error "环境预检发现 $ERRORS 个错误，请修复后重试"
    exit 1
fi

log_ok "环境预检全部通过！"

# =============================================================================
# 阶段 1: 清理旧资源（如启用 --rebuild）
# =============================================================================
if $REBUILD; then
    log_step "阶段 1/7: 清理旧容器和镜像"

    if docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^${CONTAINER_NAME}$"; then
        log_info "停止并删除旧容器 $CONTAINER_NAME..."
        docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
        log_ok "旧容器已删除"
    fi
fi

# =============================================================================
# 阶段 2: 构建基础镜像 jupyter-ssh-base
# =============================================================================
if ! $SKIP_BASE_BUILD; then
    log_step "阶段 2/7: 构建基础镜像 jupyter-ssh-base:1.1"

    if docker image inspect jupyter-ssh-base:1.1 &>/dev/null 2>&1; then
        log_ok "基础镜像 jupyter-ssh-base:1.1 已存在，跳过构建"
        log_info "如需强制重建，使用 --rebuild 参数"
    else
        log_info "基础镜像不存在，开始构建..."
        if [ ! -f "$BASE_BUILD_SCRIPT" ]; then
            log_error "基础镜像构建脚本未找到: $BASE_BUILD_SCRIPT"
            exit 1
        fi
        cd "$PROJECT_ROOT/apps/jupyter-ssh-base"
        if $USE_CN_MIRRORS; then
            bash scripts/build.sh --cn
        else
            bash scripts/build.sh
        fi
        log_ok "基础镜像构建完成"
    fi
else
    log_step "阶段 2/7: 跳过基础镜像构建（--skip-base）"
fi

# =============================================================================
# 阶段 3: 构建 caffe-ffi-jupyter 镜像
# =============================================================================
log_step "阶段 3/7: 构建 caffe-ffi-jupyter:${IMAGE_TAG} 镜像"

cd "$APP_DIR"

BUILD_CMD="bash $BUILD_SCRIPT --tag $IMAGE_TAG $MIRROR_ARGS $NO_CACHE"

log_info "执行构建命令: $BUILD_CMD"
echo ""

START_TIME=$(date +%s)

if $VERBOSE; then
    $BUILD_CMD
else
    $BUILD_CMD 2>&1 | tee /tmp/caffe-ffi-build.log | tail -50
    BUILD_EXIT_CODE=${PIPESTATUS[0]:-${PIPESTATUS[1]}}
    if [ "$BUILD_EXIT_CODE" != "0" ]; then
        log_error "构建失败！完整日志: /tmp/caffe-ffi-build.log"
        log_error "日志末尾："
        tail -30 /tmp/caffe-ffi-build.log
        exit 1
    fi
fi

END_TIME=$(date +%s)
BUILD_DURATION=$((END_TIME - START_TIME))
IMAGE_SIZE=$(docker images --format '{{.Size}}' "caffe-ffi-jupyter:${IMAGE_TAG}" | head -1)

log_ok "镜像构建完成！耗时: ${BUILD_DURATION}s, 大小: $IMAGE_SIZE"

# =============================================================================
# 阶段 4: 启动容器
# =============================================================================
if $SKIP_RUN; then
    log_step "阶段 4/7: 跳过容器启动（--skip-run）"
    log_info "镜像已构建完成，可以手动启动："
    echo ""
    echo "  docker run -d -p ${SSH_PORT}:22 -p ${JUPYTER_PORT}:8888 \\"
    echo "    -e USER_PASSWORD=${USER_PASSWORD} -e JUPYTER_TOKEN=${JUPYTER_TOKEN} \\"
    echo "    -v \$(pwd)/workspace:/workspace --name ${CONTAINER_NAME} caffe-ffi-jupyter:${IMAGE_TAG}"
    echo ""
    log_info "部署完成！"
    exit 0
fi

log_step "阶段 4/7: 启动验证容器"

# 清理同名容器
if docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^${CONTAINER_NAME}$"; then
    log_info "删除已存在的同名容器..."
    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
fi

log_info "启动容器: $CONTAINER_NAME"
docker run -d \
    -p "${SSH_PORT}:22" \
    -p "${JUPYTER_PORT}:8888" \
    -e "USER_PASSWORD=${USER_PASSWORD}" \
    -e "JUPYTER_TOKEN=${JUPYTER_TOKEN}" \
    --name "$CONTAINER_NAME" \
    "caffe-ffi-jupyter:${IMAGE_TAG}"

log_info "等待服务启动（20秒）..."
sleep 20

# 检查容器是否仍在运行
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    log_error "容器启动后立即退出！查看日志："
    docker logs "$CONTAINER_NAME" 2>&1 | tail -40
    exit 1
fi
log_ok "容器运行中（ID: $(docker ps -qf name=$CONTAINER_NAME | cut -c1-12)）"

# =============================================================================
# 阶段 5: 服务级验证（SSH + Jupyter + supervisord）
# =============================================================================
log_step "阶段 5/7: 服务级验证"

VERIFY_PASS=0
VERIFY_FAIL=0

# 5.1 supervisord 状态
log_info "检查 supervisord 服务状态..."
if docker exec "$CONTAINER_NAME" supervisorctl status 2>/dev/null; then
    log_ok "supervisord 服务状态正常"
    VERIFY_PASS=$((VERIFY_PASS + 1))
else
    log_fail "supervisord 状态异常"
    VERIFY_FAIL=$((VERIFY_FAIL + 1))
fi

# 5.2 SSH 服务
log_info "检查 SSH 服务..."
if docker exec "$CONTAINER_NAME" supervisorctl status sshd 2>/dev/null | grep -q RUNNING; then
    log_ok "SSH 服务运行中"
    VERIFY_PASS=$((VERIFY_PASS + 1))
else
    log_fail "SSH 服务未运行"
    VERIFY_FAIL=$((VERIFY_FAIL + 1))
fi

# 5.3 Jupyter 服务
log_info "检查 Jupyter 服务..."
if docker exec "$CONTAINER_NAME" supervisorctl status jupyter 2>/dev/null | grep -q RUNNING; then
    log_ok "Jupyter 服务运行中"
    VERIFY_PASS=$((VERIFY_PASS + 1))
else
    log_fail "Jupyter 服务未运行"
    VERIFY_FAIL=$((VERIFY_FAIL + 1))
fi

# 5.4 Jupyter HTTP API
log_info "检查 Jupyter HTTP API（端口 ${JUPYTER_PORT}）..."
sleep 5  # 额外等待 Jupyter 完全启动
HEALTHCHECK_RETRIES=5
for i in $(seq 1 $HEALTHCHECK_RETRIES); do
    if curl -sf "http://localhost:${JUPYTER_PORT}/api?token=${JUPYTER_TOKEN}" &>/dev/null; then
        log_ok "Jupyter HTTP API 响应正常"
        VERIFY_PASS=$((VERIFY_PASS + 1))
        break
    fi
    if [ $i -eq $HEALTHCHECK_RETRIES ]; then
        log_fail "Jupyter HTTP API 无响应（已重试 ${HEALTHCHECK_RETRIES} 次）"
        VERIFY_FAIL=$((VERIFY_FAIL + 1))
    else
        log_info "等待 Jupyter API... (${i}/${HEALTHCHECK_RETRIES})"
        sleep 5
    fi
done

# =============================================================================
# 阶段 6: Python/caffe-ffi 运行时验证
# =============================================================================
log_step "阶段 6/7: Python 运行时验证"

DOCKER_EXEC="docker exec $CONTAINER_NAME bash -lc"
CONDA_INIT="source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi &&"

# 6.1 Python 版本
log_info "检查 Python 版本..."
PY_VER=$($DOCKER_EXEC "$CONDA_INIT python --version" 2>&1)
if echo "$PY_VER" | grep -q "Python 3.14"; then
    log_ok "$PY_VER"
    VERIFY_PASS=$((VERIFY_PASS + 1))
else
    log_fail "Python 版本不符: $PY_VER（期望 3.14.x）"
    VERIFY_FAIL=$((VERIFY_FAIL + 1))
fi

# 6.2 caffe_ffi 基础导入
log_info "检查 caffe_ffi 导入..."
CAFFE_IMPORT=$($DOCKER_EXEC "$CONDA_INIT python -c \"import caffe_ffi; print(caffe_ffi.__version__)\"" 2>&1)
if [ $? -eq 0 ] && echo "$CAFFE_IMPORT" | grep -qE '[0-9]+\.[0-9]+\.[0-9]+'; then
    log_ok "caffe_ffi 导入成功，版本: $CAFFE_IMPORT"
    VERIFY_PASS=$((VERIFY_PASS + 1))
else
    log_fail "caffe_ffi 导入失败: $CAFFE_IMPORT"
    VERIFY_FAIL=$((VERIFY_FAIL + 1))
    log_info "尝试运行诊断脚本..."
    $DOCKER_EXEC "$CONDA_INIT python -c \"
import sys
print('Python:', sys.version)
print('sys.path:', sys.path[:5])
try:
    import tvm_ffi
    print('tvm_ffi:', tvm_ffi.__file__)
except Exception as e:
    print('tvm_ffi import error:', e)
try:
    import caffe_ffi
    print('caffe_ffi:', caffe_ffi.__file__)
except Exception as e:
    print('caffe_ffi import error:', e)
" 2>&1 || true
fi

# 6.3 _caffe_ffi.so 共享库依赖检查
log_info "检查 _caffe_ffi.so 共享库依赖..."
LDD_OUTPUT=$($DOCKER_EXEC "$CONDA_INIT _SO=\$(python -c 'import caffe_ffi,os; print(os.path.join(os.path.dirname(caffe_ffi.__file__), \"_caffe_ffi.so\"))'); ldd \"\$_SO\"" 2>&1)
if echo "$LDD_OUTPUT" | grep -q 'not found'; then
    log_fail "共享库存在未解析依赖！"
    echo "$LDD_OUTPUT" | grep 'not found'
    VERIFY_FAIL=$((VERIFY_FAIL + 1))
    log_info "=== 完整 ldd 输出 ==="
    echo "$LDD_OUTPUT"
else
    log_ok "_caffe_ffi.so 所有共享库依赖已解析"
    VERIFY_PASS=$((VERIFY_PASS + 1))
fi

# 6.4 numpy 导入
log_info "检查 numpy..."
NUMPY_VER=$($DOCKER_EXEC "$CONDA_INIT python -c \"import numpy; print(numpy.__version__)\"" 2>&1)
if echo "$NUMPY_VER" | grep -qE '[0-9]+\.[0-9]+'; then
    log_ok "numpy $NUMPY_VER"
    VERIFY_PASS=$((VERIFY_PASS + 1))
else
    log_fail "numpy 导入失败: $NUMPY_VER"
    VERIFY_FAIL=$((VERIFY_FAIL + 1))
fi

# 6.5 protobuf 版本检查
log_info "检查 protobuf 版本（要求 >= 7.0.0）..."
PROTF_VER=$($DOCKER_EXEC "$CONDA_INIT python -c \"import google.protobuf; print(google.protobuf.__version__)\"" 2>&1)
if echo "$PROTF_VER" | grep -qE '^[7-9]\.'; then
    log_ok "protobuf $PROTF_VER (>= 7.0.0)"
    VERIFY_PASS=$((VERIFY_PASS + 1))
elif echo "$PROTF_VER" | grep -qE '^[1-9][0-9]\.'; then
    log_ok "protobuf $PROTF_VER (>= 7.0.0)"
    VERIFY_PASS=$((VERIFY_PASS + 1))
else
    log_fail "protobuf 版本不符合: $PROTF_VER（要求 >= 7.0.0）"
    VERIFY_FAIL=$((VERIFY_FAIL + 1))
    log_info "运行诊断: bash scripts/diagnose.sh --container $CONTAINER_NAME"
fi

# 6.6 protoc 版本
log_info "检查 protoc 版本..."
PROTOC_VER=$($DOCKER_EXEC "$CONDA_INIT protoc --version" 2>&1)
if echo "$PROTOC_VER" | grep -qE '[0-9]+\.[0-9]+'; then
    log_ok "$PROTOC_VER"
    VERIFY_PASS=$((VERIFY_PASS + 1))
else
    log_fail "protoc 不可用: $PROTOC_VER"
    VERIFY_FAIL=$((VERIFY_FAIL + 1))
fi

# 6.7 Jupyter Kernel 注册
log_info "检查 Jupyter Kernel 注册..."
KERNELS=$($DOCKER_EXEC "$CONDA_INIT jupyter kernelspec list" 2>&1)
if echo "$KERNELS" | grep -q caffe-ffi; then
    log_ok "caffe-ffi Jupyter Kernel 已注册"
    VERIFY_PASS=$((VERIFY_PASS + 1))
else
    log_fail "caffe-ffi Jupyter Kernel 未注册"
    VERIFY_FAIL=$((VERIFY_FAIL + 1))
fi

# 6.8 caffe_ffi 核心功能测试（Blob 创建和基本操作）
log_info "运行 caffe_ffi 核心功能测试（Blob 创建）..."
BLOB_TEST=$($DOCKER_EXEC "$CONDA_INIT python -c \"
import caffe_ffi
from caffe_ffi import Blob
import numpy as np
b = Blob()
b.reshape(1, 3, 224, 224)
data = b.data
assert data.shape == (1, 3, 224, 224), f'Shape mismatch: {data.shape}'
assert data.dtype == np.float32, f'Dtype mismatch: {data.dtype}'
print(f'Blob OK: shape={data.shape}, dtype={data.dtype}')
\"" 2>&1)
if [ $? -eq 0 ]; then
    log_ok "$BLOB_TEST"
    VERIFY_PASS=$((VERIFY_PASS + 1))
else
    log_fail "Blob 功能测试失败: $BLOB_TEST"
    VERIFY_FAIL=$((VERIFY_FAIL + 1))
fi

# 6.9 内存诊断 API
log_info "检查内存诊断 API..."
MEM_TEST=$($DOCKER_EXEC "$CONDA_INIT python -c \"
import caffe_ffi
info = caffe_ffi.memory_info()
print(f'Memory info: {info}')
assert 'total_allocated_bytes' in info
assert 'live_blob_count' in info
print('Memory API OK')
\"" 2>&1)
if [ $? -eq 0 ]; then
    log_ok "$MEM_TEST"
    VERIFY_PASS=$((VERIFY_PASS + 1))
else
    log_fail "内存 API 测试失败: $MEM_TEST"
    VERIFY_FAIL=$((VERIFY_FAIL + 1))
fi

# =============================================================================
# 阶段 7: 结果汇总与清理
# =============================================================================
log_step "阶段 7/7: 验证结果汇总"

echo ""
echo -e "${BOLD}┌─────────────────────────────────────────┐${NC}"
echo -e "${BOLD}│       部署验证结果汇总                   │${NC}"
echo -e "${BOLD}├─────────────────────────────────────────┤${NC}"
echo -e "${BOLD}│${NC}  通过: ${GREEN}${VERIFY_PASS}${NC} 项"
echo -e "${BOLD}│${NC}  失败: ${RED}${VERIFY_FAIL}${NC} 项"
echo -e "${BOLD}│${NC}  总计: $((VERIFY_PASS + VERIFY_FAIL)) 项"
echo -e "${BOLD}└─────────────────────────────────────────┘${NC}"
echo ""

if [ $VERIFY_FAIL -eq 0 ]; then
    echo -e "${GREEN}${BOLD}🎉 所有验证通过！Caffe-FFI 环境部署成功！${NC}"
    echo ""
    echo -e "${CYAN}连接信息：${NC}"
    echo "  SSH 访问:     ssh -p ${SSH_PORT} jupyteruser@localhost  (密码: ${USER_PASSWORD})"
    echo "  Jupyter 访问: http://localhost:${JUPYTER_PORT}/?token=${JUPYTER_TOKEN}"
    echo "  容器名称:     ${CONTAINER_NAME}"
    echo "  快速验证:     docker exec ${CONTAINER_NAME} bash -lc 'source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && python -c \"import caffe_ffi; print(caffe_ffi.version())\"'"
    echo ""
    echo -e "${CYAN}进入容器:${NC}"
    echo "  docker exec -it ${CONTAINER_NAME} bash"
    echo ""

    if $CLEANUP; then
        log_info "自动清理容器（--cleanup）..."
        docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1
        log_ok "容器已清理"
    fi

    exit 0
else
    echo -e "${RED}${BOLD}❌ ${VERIFY_FAIL} 项验证失败！${NC}"
    echo ""
    echo -e "${YELLOW}故障排查命令：${NC}"
    echo "  1. 查看容器日志:     docker logs ${CONTAINER_NAME} 2>&1 | tail -50"
    echo "  2. 运行诊断脚本:     bash scripts/diagnose.sh --container ${CONTAINER_NAME}"
    echo "  3. 进入容器调试:     docker exec -it ${CONTAINER_NAME} bash"
    echo "  4. 检查 supervisord: docker exec ${CONTAINER_NAME} supervisorctl status"
    echo ""
    echo -e "${YELLOW}常见问题：${NC}"
    echo "  - protobuf 版本冲突:   bash scripts/diagnose.sh --container ${CONTAINER_NAME} --fix-protobuf"
    echo "  - 共享库未解析:        bash scripts/diagnose.sh --container ${CONTAINER_NAME} --fix-ldpath"
    echo "  - 详细部署指南参见:    apps/caffe-ffi-jupyter/WSL-DEPLOY-GUIDE.md"
    echo ""
    exit 1
fi
