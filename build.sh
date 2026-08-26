#!/bin/bash
# ==============================================================================
# vta-dev — 宿主侧一键构建 & 验证脚本
#   基于 devcontainer-base:onnx-quantized-latest 构建 Nuitka 编译的 xmnn wheel 并生成运行时镜像。
#
# 用法:
#   ./build.sh                                # 构建 vta-dev:latest 镜像
#   ./build.sh --verify-only, -V              # 仅验证已存在的 vta-dev 镜像
#   ./build.sh --no-cache, -F                 # 强制 --no-cache 全量重建
#   ./build.sh --debug, -d                    # 仅构建到 builder 阶段（调试Nuitka编译）
#   ./build.sh --extract, -e                  # 构建后提取 wheel 到本地 dist/
#   ./build.sh --verbose, -v                  # 详细模式：打印每条执行命令
#   ./build.sh -h, --help                     # 显示帮助
#
# 日志:
#   所有输出自动 tee 到 logs/build-<timestamp>.log
#   构建失败时打印排查建议并提示日志文件路径
#
# 构建上下文必须为 SpecWeave 根目录（确保 Dockerfile COPY/bind mount 路径正确解析）。
# ==============================================================================

set -euo pipefail

# ── ANSI 颜色定义 ────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# ── 路径常量 ──────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

find_specweave_root() {
    local current="$SCRIPT_DIR"
    while [ "$current" != "/" ]; do
        if [ -d "$current/.agents" ] && [ -d "$current/external/chaos/npuusertools" ]; then
            echo "$current"
            return 0
        fi
        current="$(dirname "$current")"
    done
    echo ""
    return 1
}

SPECWEAVE_ROOT="$(find_specweave_root)"
if [ -z "$SPECWEAVE_ROOT" ]; then
    SPECWEAVE_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
fi

DOCKERFILE="${SCRIPT_DIR}/Dockerfile"
LOG_DIR="${SCRIPT_DIR}/logs"
DIST_DIR="${SCRIPT_DIR}/dist"

BASE_IMAGE="devcontainer-base:onnx-quantized-latest"
IMAGE_NAME="vta-dev:latest"
BUILDER_IMAGE_NAME="vta-dev-builder:latest"

# ── 参数变量 ──────────────────────────────────────────────────────────
VERIFY_ONLY=0
NO_CACHE=0
DEBUG_MODE=0
EXTRACT_WHEEL=0
VERBOSE=0

# ── 日志函数（内置，不依赖外部logging.sh）────────────────────────────
log_info() {
    echo -e "[$(date '+%H:%M:%S')] ${CYAN}[INFO]${RESET} $*"
}

log_ok() {
    echo -e "[$(date '+%H:%M:%S')] ${GREEN}[OK]${RESET} ✅ $*"
}

log_warn() {
    echo -e "[$(date '+%H:%M:%S')] ${YELLOW}[WARN]${RESET} ⚠️  $*"
}

log_error() {
    echo -e "[$(date '+%H:%M:%S')] ${RED}[ERROR]${RESET} ❌ $*"
}

log_section() {
    echo ""
    echo -e "${BOLD}--- $* ---${RESET}"
}

log_header() {
    echo ""
    echo "============================================================"
}

# ── 参数解析 ──────────────────────────────────────────────────────────
usage() {
    cat <<EOF
vta-dev — 一键构建 & 验证脚本

用法: $0 [选项]

选项:
  --verify-only, -V      仅验证已存在的 ${IMAGE_NAME} 镜像（跳过构建）
  --no-cache, -F         强制 docker build --no-cache 全量重建（忽略层缓存）
  --debug, -d            仅构建到 builder 阶段（用于调试 Nuitka 编译）
                         镜像标签为 ${BUILDER_IMAGE_NAME}
  --extract, -e          构建成功后提取 wheel 文件到本地 ${DIST_DIR}/
  --verbose, -v          详细模式：打印每条执行命令 (set -x)，排查问题时使用
  -h, --help             显示帮助

镜像配置:
  基础镜像:     ${BASE_IMAGE}
  最终镜像:     ${IMAGE_NAME}
  Builder镜像:  ${BUILDER_IMAGE_NAME}（--debug模式）
  Dockerfile:   ${DOCKERFILE}
  构建上下文:   ${SPECWEAVE_ROOT}
  日志目录:     ${LOG_DIR}
  输出目录:     ${DIST_DIR}

示例:
  $0                              # 构建 ${IMAGE_NAME}
  $0 --verify-only                # 验证已有镜像
  $0 -F -e                        # 强制全量重建并提取 wheel
  $0 -d -v                        # 调试模式构建 builder，详细日志
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --verify-only|-V)
            VERIFY_ONLY=1
            shift
            ;;
        --no-cache|-F)
            NO_CACHE=1
            shift
            ;;
        --debug|-d)
            DEBUG_MODE=1
            shift
            ;;
        --extract|-e)
            EXTRACT_WHEEL=1
            shift
            ;;
        --verbose|-v)
            VERBOSE=1
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            log_error "未知选项: $1"
            usage
            ;;
    esac
done

if [ "$VERBOSE" -eq 1 ]; then
    set -x
    log_info "详细模式已启用 (set -x)"
fi

# ── 创建目录 ──────────────────────────────────────────────────────────
mkdir -p "$LOG_DIR" "$DIST_DIR"

# ── 日志文件 ──────────────────────────────────────────────────────────
TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"
LOG_FILE="${LOG_DIR}/build-${TIMESTAMP}.log"

# 重定向所有输出到日志文件同时显示在终端
exec > >(tee -a "$LOG_FILE") 2>&1

# ── 启动 Banner ───────────────────────────────────────────────────────
{
    echo "============================================================"
    echo "  vta-dev — Build & Test"
    echo "  Started at: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "  Log file:   ${LOG_FILE}"
    echo "============================================================"
}

log_section "构建配置"
log_info "基础镜像:     ${BASE_IMAGE}"
log_info "目标镜像:     $([ "$DEBUG_MODE" -eq 1 ] && echo "${BUILDER_IMAGE_NAME} (debug模式)" || echo "${IMAGE_NAME}")"
log_info "Dockerfile:   ${DOCKERFILE}"
log_info "构建上下文:   ${SPECWEAVE_ROOT}"
log_info "仅验证模式:   $([ "$VERIFY_ONLY" -eq 1 ] && echo '是 (--verify-only)' || echo '否')"
log_info "强制重建:     $([ "$NO_CACHE" -eq 1 ] && echo '是 (--no-cache)' || echo '否')"
log_info "调试模式:     $([ "$DEBUG_MODE" -eq 1 ] && echo '是 (--debug, 仅builder阶段)' || echo '否')"
log_info "提取wheel:    $([ "$EXTRACT_WHEEL" -eq 1 ] && echo '是 (--extract)' || echo '否')"
log_info "日志文件:     ${LOG_FILE}"

# ── 前置检查 ──────────────────────────────────────────────────────────
log_section "前置环境检查"

if ! command -v docker &> /dev/null; then
    log_error "未找到 docker 命令，请先安装 Docker Desktop 或 Docker Engine"
    exit 1
fi
DOCKER_VER=$(docker --version 2>&1 | head -1)
log_ok "Docker 已安装: ${DOCKER_VER}"

if ! docker info &>/dev/null; then
    log_error "Docker daemon 未运行或无权限访问"
    log_warn "  → Windows/Mac: 请启动 Docker Desktop"
    log_warn "  → Linux: sudo systemctl start docker"
    exit 1
fi
log_ok "Docker daemon 可访问"

export DOCKER_BUILDKIT=1
log_info "DOCKER_BUILDKIT=1 已启用（BuildKit 支持 bind mount）"

if [ ! -f "$DOCKERFILE" ]; then
    log_error "Dockerfile 不存在: ${DOCKERFILE}"
    exit 1
fi
log_ok "Dockerfile 存在: ${DOCKERFILE}"

log_section "构建上下文关键路径检查"
check_file() {
    local rel_path="$1"
    local full_path="${SPECWEAVE_ROOT}/${rel_path}"
    if [ -f "$full_path" ]; then
        log_ok "存在: ${rel_path}"
    else
        log_error "缺失: ${rel_path}（构建将失败）"
        exit 1
    fi
}

check_file "external/dao/runtime/vta-dev/pyproject.toml"
check_file "external/dao/runtime/vta-dev/CMakeLists.txt"
check_file "external/dao/runtime/vta-dev/scripts/build-wheel.sh"
check_file "external/dao/runtime/vta-dev/scripts/verify-wheel.sh"

SOURCE_DIR="${SPECWEAVE_ROOT}/external/chaos/npuusertools"
if [ -d "$SOURCE_DIR" ]; then
    log_ok "源码目录存在: external/chaos/npuusertools"
else
    log_error "源码目录不存在: external/chaos/npuusertools（bind mount 将失败）"
    exit 1
fi

# ── 验证函数 ──────────────────────────────────────────────────────────
verify_image() {
    local verify_image_name="$1"
    local is_builder="$2"
    
    log_section "镜像验证"
    
    if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${verify_image_name}$"; then
        log_error "镜像不存在: ${verify_image_name}，请先构建"
        exit 1
    fi

    local img_info
    img_info=$(docker image inspect "$verify_image_name" --format 'ID={{.Id|truncate 20}} | Created={{.Created}} | Size={{.Size}}' 2>/dev/null || echo "inspect failed")
    log_ok "镜像存在: ${verify_image_name}"
    log_info "         ${img_info}"
    echo ""

    if [ "$is_builder" -eq 1 ]; then
        log_info "Builder 镜像验证：仅检查构建产物目录"
        
        log_info "[Verify 1/2] 检查 wheel 文件 (/opt/vta-dist/)..."
        if docker run --rm --entrypoint ls "$verify_image_name" /opt/vta-dist/*.whl >/dev/null 2>&1; then
            whl_count=$(docker run --rm --entrypoint sh "$verify_image_name" -c "ls /opt/vta-dist/*.whl 2>/dev/null | wc -l")
            log_ok "/opt/vta-dist/ 存在，包含 ${whl_count} 个 whl 文件"
            docker run --rm --entrypoint ls "$verify_image_name" -la /opt/vta-dist/ 2>&1
        else
            log_warn "/opt/vta-dist/ 不存在或为空"
        fi
        echo ""
        
        log_info "[Verify 2/2] 检查构建工具..."
        if docker run --rm --entrypoint sh "$verify_image_name" -c "command -v nuitka && command -v cmake" >/dev/null 2>&1; then
            log_ok "构建工具存在 (nuitka, cmake)"
        else
            log_warn "部分构建工具缺失"
        fi
    else
        log_info "[Verify 1/3] 基础 import 测试 (xmnn)..."
        set +e
        VERIFY_OUTPUT=$(docker run --rm "$verify_image_name" python -c \
            "import xmnn; from importlib.metadata import version; print('  xmnn =', version('xmnn')); print('  [OK] Core import passed')" 2>&1)
        verify_exit=$?
        set -e

        if [ $verify_exit -eq 0 ]; then
            echo "$VERIFY_OUTPUT"
            log_ok "基础 import 验证通过"
        else
            echo "$VERIFY_OUTPUT"
            log_error "基础 import 验证失败！"
            exit $verify_exit
        fi
        echo ""

        log_info "[Verify 2/3] 检查 wheel 文件 (/opt/vta-dist/)..."
        if docker run --rm --entrypoint ls "$verify_image_name" /opt/vta-dist/*.whl >/dev/null 2>&1; then
            whl_count=$(docker run --rm --entrypoint sh "$verify_image_name" -c "ls /opt/vta-dist/*.whl 2>/dev/null | wc -l")
            log_ok "/opt/vta-dist/ 存在，包含 ${whl_count} 个 whl 文件"
            docker run --rm --entrypoint ls "$verify_image_name" -la /opt/vta-dist/ 2>&1
        else
            log_warn "/opt/vta-dist/ 不存在或为空"
        fi
        echo ""

        log_info "[Verify 3/3] 运行 verify-wheel.sh 完整验证..."
        echo ""
        set +e
        docker run --rm "$verify_image_name" verify-wheel.sh 2>&1
        vw_exit=${PIPESTATUS[0]}
        set -e

        if [ $vw_exit -eq 0 ]; then
            log_ok "verify-wheel.sh 全部验证通过"
        else
            log_error "verify-wheel.sh 验证失败（退出码: ${vw_exit}）"
            exit $vw_exit
        fi
    fi
    echo ""
}

# --verify-only：仅验证已有镜像
if [ "$VERIFY_ONLY" -eq 1 ]; then
    log_info "仅验证模式，跳过镜像构建"
    if [ "$DEBUG_MODE" -eq 1 ]; then
        verify_image "$BUILDER_IMAGE_NAME" 1
    else
        verify_image "$IMAGE_NAME" 0
    fi
    log_header
    echo -e "${BOLD}${GREEN}  验 证 通 过！ 🎉${RESET}"
    log_header
    log_ok "日志已保存: ${LOG_FILE}"
    exit 0
fi

# ── 基础镜像检查 ──────────────────────────────────────────────────────
log_section "基础镜像检查"

if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${BASE_IMAGE}$"; then
    log_error "基础镜像不存在: ${BASE_IMAGE}"
    echo ""
    echo -e "${YELLOW}  请先构建基础镜像（不自动构建，避免依赖链问题）：${RESET}"
    echo -e "${CYAN}    cd apps/docker-images/devcontainer-base/variants/onnx-quantized${RESET}"
    echo -e "${CYAN}    bash build.sh${RESET}"
    echo ""
    exit 1
fi

img_info=$(docker image inspect "$BASE_IMAGE" --format 'ID={{.Id|truncate 20}} | Created={{.Created}}' 2>/dev/null || echo "inspect failed")
log_ok "基础镜像存在: ${BASE_IMAGE}"
log_info "         ${img_info}"

# ── 磁盘空间与资源建议 ────────────────────────────────────────────────
log_section "系统资源"
df -h . 2>/dev/null | head -2 || true
echo ""
log_warn "Nuitka 编译 xmnn 资源消耗较大，建议 Docker 分配："
log_info "  - 内存: ≥ 4GB"
log_info "  - CPU: ≥ 2 cores"
log_info "  - 磁盘: ≥ 10GB 可用空间"
echo ""

# ── 构建命令组装 ──────────────────────────────────────────────────────
BUILD_TARGET_IMAGE="$IMAGE_NAME"
BUILD_ARGS=()

DOCKERFILE_REL="${DOCKERFILE#$SPECWEAVE_ROOT/}"

if [ "$DEBUG_MODE" -eq 1 ]; then
    BUILD_TARGET_IMAGE="$BUILDER_IMAGE_NAME"
    BUILD_ARGS+=(--target builder)
    log_info "调试模式：仅构建到 builder 阶段"
fi

if [ "$NO_CACHE" -eq 1 ]; then
    BUILD_ARGS+=(--no-cache)
    log_info "已禁用构建缓存 (--no-cache)"
fi

log_section "开始 Docker 构建"
log_info "构建目标镜像: ${BUILD_TARGET_IMAGE}"
log_info "执行命令: docker build ${BUILD_ARGS[*]} --progress=plain -t ${BUILD_TARGET_IMAGE} -f ${DOCKERFILE_REL} ${SPECWEAVE_ROOT}"
log_info "构建开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
log_info ">>> DOCKER BUILD OUTPUT START >>>"
echo ""

BUILD_START=$(date +%s)

set +e
docker build \
    "${BUILD_ARGS[@]}" \
    --progress=plain \
    -t "${BUILD_TARGET_IMAGE}" \
    -f "${DOCKERFILE_REL}" \
    "${SPECWEAVE_ROOT}"
build_exit_code=$?
set -e

echo ""
log_info "<<< DOCKER BUILD OUTPUT END <<<"
echo ""

BUILD_END=$(date +%s)
BUILD_DURATION=$((BUILD_END - BUILD_START))
BUILD_MIN=$((BUILD_DURATION / 60))
BUILD_SEC=$((BUILD_DURATION % 60))

if [ $build_exit_code -ne 0 ]; then
    log_error "docker build 退出码: ${build_exit_code}（非零 = 失败）"
    log_error "构建耗时: ${BUILD_DURATION}s (${BUILD_MIN}m${BUILD_SEC}s)"
    echo ""
    
    log_section "排查建议"
    log_error "1. 查看完整日志: ${LOG_FILE}"
    log_error "2. Nuitka 编译常见问题："
    log_info "   - 内存不足 → 增加 Docker 内存限制"
    log_info "   - 编译错误 → 检查 C/C++ 依赖"
    log_error "3. Dockerfile/路径问题："
    log_info "   - 确认构建上下文是 SpecWeave 根目录"
    log_info "   - 确认所有 COPY 源文件存在"
    log_error "4. 重试命令（详细模式）："
    log_info "   bash build.sh --debug --verbose"
    echo ""
    exit 1
fi

log_ok "docker build 退出码: 0（成功）"
log_ok "构建耗时: ${BUILD_DURATION}s (${BUILD_MIN}m${BUILD_SEC}s)"

# ── 构建结果 ──────────────────────────────────────────────────────────
log_section "构建结果与镜像详情"

IMAGE_ID=$(docker image inspect "${BUILD_TARGET_IMAGE}" --format='{{.Id}}' 2>/dev/null || echo "unknown")
IMAGE_SIZE=$(docker image inspect "${BUILD_TARGET_IMAGE}" --format='{{.Size}}' 2>/dev/null || echo "0")
IMAGE_LAYERS=$(docker image inspect "${BUILD_TARGET_IMAGE}" --format='{{len .RootFS.Layers}}' 2>/dev/null || echo "?")
IMAGE_CREATED=$(docker image inspect "${BUILD_TARGET_IMAGE}" --format='{{.Created}}' 2>/dev/null || echo "unknown")

IMAGE_SIZE_MB=$((IMAGE_SIZE / 1024 / 1024))
if [ "$IMAGE_SIZE_MB" -ge 1024 ]; then
    IMAGE_SIZE_GB=$((IMAGE_SIZE_MB / 1024))
    IMAGE_SIZE_GB_DEC=$(((IMAGE_SIZE_MB % 1024) * 10 / 1024))
    IMAGE_SIZE_HUMAN="${IMAGE_SIZE_GB}.${IMAGE_SIZE_GB_DEC} GB"
else
    IMAGE_SIZE_HUMAN="${IMAGE_SIZE_MB} MB"
fi

log_info "镜像名称:     ${BUILD_TARGET_IMAGE}"
log_info "镜像ID:       ${IMAGE_ID}"
log_info "创建时间:     ${IMAGE_CREATED}"
log_info "镜像大小:     ~${IMAGE_SIZE_HUMAN} (${IMAGE_LAYERS} 层)"
log_info "构建耗时:     ${BUILD_DURATION}s (${BUILD_MIN}m${BUILD_SEC}s)"
echo ""

# ── 验证镜像 ──────────────────────────────────────────────────────────
verify_image "$BUILD_TARGET_IMAGE" "$DEBUG_MODE"

# ── 提取 wheel（如果需要）────────────────────────────────────────────
if [ "$EXTRACT_WHEEL" -eq 1 ] && [ "$DEBUG_MODE" -ne 1 ]; then
    log_section "提取 wheel 到本地 dist/"
    
    log_info "创建临时容器提取 wheel..."
    CONTAINER_ID=$(docker create "$BUILD_TARGET_IMAGE" 2>/dev/null)
    if [ -n "$CONTAINER_ID" ]; then
        docker cp "${CONTAINER_ID}:/opt/vta-dist/." "$DIST_DIR/" 2>&1
        docker rm -f "$CONTAINER_ID" >/dev/null 2>&1
        log_ok "wheel 已提取到: ${DIST_DIR}/"
        ls -la "$DIST_DIR/"*.whl 2>/dev/null || true
    else
        log_error "创建临时容器失败，无法提取 wheel"
    fi
    echo ""
elif [ "$EXTRACT_WHEEL" -eq 1 ] && [ "$DEBUG_MODE" -eq 1 ]; then
    log_section "提取 wheel (debug模式从builder镜像)"
    
    log_info "从 builder 镜像提取 wheel..."
    CONTAINER_ID=$(docker create "$BUILD_TARGET_IMAGE" 2>/dev/null)
    if [ -n "$CONTAINER_ID" ]; then
        docker cp "${CONTAINER_ID}:/opt/vta-dist/." "$DIST_DIR/" 2>&1
        docker rm -f "$CONTAINER_ID" >/dev/null 2>&1
        log_ok "wheel 已提取到: ${DIST_DIR}/"
        ls -la "$DIST_DIR/"*.whl 2>/dev/null || true
    else
        log_error "创建临时容器失败，无法提取 wheel"
    fi
    echo ""
fi

# ── 快速参考命令 ─────────────────────────────────────────────────────
log_header
echo -e "${BOLD}${GREEN}  构 建 成 功！ 🎉${RESET}"
log_header
echo ""

log_info "📌 快速参考命令："
echo ""
echo -e "${CYAN}  # 验证镜像${RESET}"
echo -e "  $0 --verify-only"
echo ""
echo -e "${CYAN}  # 测试 import${RESET}"
if [ "$DEBUG_MODE" -eq 1 ]; then
    echo -e "  docker run --rm ${BUILDER_IMAGE_NAME} python -c \"import sys; sys.path.insert(0,'/builder'); print('builder ready')\""
else
    echo -e "  docker run --rm ${IMAGE_NAME} python -c \"import xmnn; from importlib.metadata import version; print(version('xmnn'))\""
fi
echo ""
echo -e "${CYAN}  # 进入容器交互模式${RESET}"
if [ "$DEBUG_MODE" -eq 1 ]; then
    echo -e "  docker run --rm -it ${BUILDER_IMAGE_NAME} bash"
else
    echo -e "  docker run --rm -it ${IMAGE_NAME} bash"
fi
echo ""

if [ "$EXTRACT_WHEEL" -eq 1 ]; then
    echo -e "${CYAN}  # wheel 文件位置${RESET}"
    echo -e "  ls -la ${DIST_DIR}/"
    echo ""
fi

log_ok "日志已保存: ${LOG_FILE}"
log_info "BUILD SCRIPT COMPLETED SUCCESSFULLY"
