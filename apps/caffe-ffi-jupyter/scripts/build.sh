#!/bin/bash
# =============================================================================
# build.sh — caffe-ffi-jupyter Docker 镜像构建脚本
# 功能：基于 jupyter-ssh-base 基础镜像构建 caffe-ffi-jupyter 镜像
# 使用：bash scripts/build.sh [OPTIONS]
# 可独立执行，也可被 wsl-deploy.sh 调用
# 日志格式：默认 text（人类可读），使用 --log-format=json 输出 JSON Lines
# =============================================================================
set -euo pipefail

# ── 确定脚本目录并加载统一日志库 ──
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/logging.sh
source "${SCRIPT_DIR}/lib/logging.sh"
LOG_SERVICE="caffe-ffi-build"

APP_DIR="$(dirname "$SCRIPT_DIR")"
# Build context is SpecWeave root (3 levels up from scripts/: scripts -> app -> apps -> root)
CONTEXT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DOCKERFILE="${APP_DIR}/Dockerfile"

# ── 默认参数 ──
IMAGE_NAME="${IMAGE_NAME:-caffe-ffi-jupyter}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-}"
NO_CACHE=""
APT_MIRROR="${APT_MIRROR:-official}"
PIP_MIRROR="${PIP_MIRROR:-official}"
CONDA_MIRROR="${CONDA_MIRROR:-official}"
PYTHON_VERSION="${PYTHON_VERSION:-3.14}"
VERIFY=false
BASE_IMAGE="${BASE_IMAGE:-jupyter-ssh-base:1.1}"

# ── 用法 ──
usage() {
    cat << EOF
${_CLR_BOLD}caffe-ffi-jupyter 镜像构建脚本${_CLR_RESET}

用法: bash scripts/build.sh [选项]

前置条件:
  - jupyter-ssh-base:1.1 须先构建（运行 ../jupyter-ssh-base/scripts/build.sh）

${_CLR_BOLD}选项:${_CLR_RESET}
  -t, --tag TAG          镜像标签（默认: latest）
  -n, --name NAME        镜像名称（默认: caffe-ffi-jupyter）
  -r, --registry REG     Registry 前缀（如 your-registry.com）
  --base-image IMAGE     基础镜像名（默认: jupyter-ssh-base:1.1）
  --python-version VER   Conda 环境 Python 版本（默认: 3.14）
  --no-cache             禁用 Docker 构建缓存
  --cn                   使用国内镜像（apt:aliyun, pip:aliyun, conda:tuna）
  --apt-mirror MIRROR    APT 镜像源: official|aliyun|tuna（默认: official）
  --pip-mirror MIRROR    PyPI 镜像源: official|aliyun|tuna（默认: official）
  --conda-mirror MIRROR  Conda 镜像源: official|tuna（默认: official）
  --verify               构建后运行验证
  --log-format FMT       日志格式: text|json（默认: text）
  --log-level LVL        日志级别: DEBUG|INFO|WARN|ERROR（默认: INFO）
  --log-json             JSON 日志同时输出到 stdout
  -h, --help             显示帮助

${_CLR_BOLD}示例:${_CLR_RESET}
  bash scripts/build.sh                          # 默认构建
  bash scripts/build.sh --cn                     # 国内镜像构建
  bash scripts/build.sh --tag dev --no-cache     # 无缓存构建，标签 dev
  bash scripts/build.sh --verify                 # 构建并验证
EOF
}

# ── 参数解析 ──
while [[ $# -gt 0 ]]; do
    case "$1" in
        -t|--tag) IMAGE_TAG="$2"; shift 2 ;;
        -n|--name) IMAGE_NAME="$2"; shift 2 ;;
        -r|--registry) REGISTRY="$2"; shift 2 ;;
        --base-image) BASE_IMAGE="$2"; shift 2 ;;
        --python-version) PYTHON_VERSION="$2"; shift 2 ;;
        --no-cache) NO_CACHE="--no-cache"; shift ;;
        --cn) APT_MIRROR="aliyun"; PIP_MIRROR="aliyun"; CONDA_MIRROR="tuna"; shift ;;
        --apt-mirror) APT_MIRROR="$2"; shift 2 ;;
        --pip-mirror) PIP_MIRROR="$2"; shift 2 ;;
        --conda-mirror) CONDA_MIRROR="$2"; shift 2 ;;
        --verify) VERIFY=true; shift ;;
        --log-format=*) LOG_FORMAT="${1#*=}"; shift ;;
        --log-level=*) LOG_LEVEL="${1#*=}"; shift ;;
        --log-json) LOG_JSON_STDOUT=1; shift ;;
        --log-json-output=*) LOG_JSON_OUTPUT="${1#*=}"; shift ;;
        -h|--help) usage; exit 0 ;;
        *) log_error "未知选项: $1"; usage; exit 1 ;;
    esac
done

# ── WSL/Linux 环境检测 ──
if ! grep -qiE '(microsoft|wsl)' /proc/version 2>/dev/null && [ "$(uname -s)" != "Linux" ]; then
    log_warn "此构建脚本设计用于 WSL2/Linux 环境，当前 OS: $(uname -s)"
    log_warn "建议在 WSL 内执行以获得可靠构建结果"
fi

if [ -n "$REGISTRY" ]; then
    FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
else
    FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"
fi

# ── 构建开始 ──
log_set_field "image" "$FULL_IMAGE"
log_set_field "base_image" "$BASE_IMAGE"
log_set_field "python_version" "$PYTHON_VERSION"
log_event "build_start" "image=$FULL_IMAGE" "base=$BASE_IMAGE" "python=$PYTHON_VERSION" "cn_mirrors=$([ "$APT_MIRROR" = "aliyun" ] && echo true || echo false)"

log_step "构建配置"
log_info "镜像:       $FULL_IMAGE"
log_info "构建上下文: $CONTEXT_DIR"
log_info "Dockerfile: $DOCKERFILE"
log_info "基础镜像:   $BASE_IMAGE"
log_info "Python:     $PYTHON_VERSION"
log_info "APT 镜像:   $APT_MIRROR"
log_info "PyPI 镜像:  $PIP_MIRROR"
log_info "Conda 镜像: $CONDA_MIRROR"
[ -n "$NO_CACHE" ] && log_info "缓存:       已禁用"

# ── 检查基础镜像 ──
log_step "阶段 1/3: 前置检查"

log_info "验证基础镜像 '${BASE_IMAGE}' 是否存在..."
if ! docker image inspect "${BASE_IMAGE}" >/dev/null 2>&1; then
    log_fail "基础镜像 '${BASE_IMAGE}' 未找到"
    log_info "请先构建 jupyter-ssh-base:"
    log_info "  cd ${APP_DIR}/../jupyter-ssh-base"
    log_info "  bash scripts/build.sh${APT_MIRROR:+ --apt-mirror ${APT_MIRROR}}${PIP_MIRROR:+ --pip-mirror ${PIP_MIRROR}}"
    log_event "build_error" "phase=precheck" "error=base_image_not_found" "base=$BASE_IMAGE"
    exit 1
fi
log_ok "基础镜像 '${BASE_IMAGE}' 存在"

# ── 检查 caffe-ffi 源码 ──
CAFFE_FFI_SRC="${CONTEXT_DIR}/projects/xuanspace/libs/caffe-ffi"
if [ ! -f "${CAFFE_FFI_SRC}/CMakeLists.txt" ]; then
    log_fail "caffe-ffi 源码未找到: ${CAFFE_FFI_SRC}"
    log_info "请初始化 xuanspace 子模块:"
    log_info "  cd ${CONTEXT_DIR} && git submodule update --init projects/xuanspace"
    log_event "build_error" "phase=precheck" "error=source_not_found" "path=$CAFFE_FFI_SRC"
    exit 1
fi
log_ok "caffe-ffi 源码存在: ${CAFFE_FFI_SRC}"

# ── 执行构建 ──
log_step "阶段 2/3: 构建镜像"
log_info "开始 Docker 构建（BuildKit）..."

BUILD_START=$(date +%s)
cd "$CONTEXT_DIR"

DOCKER_BUILDKIT=1 docker build \
    ${NO_CACHE} \
    -f "${DOCKERFILE}" \
    --build-arg BASE_IMAGE="${BASE_IMAGE}" \
    --build-arg APT_MIRROR="${APT_MIRROR}" \
    --build-arg PIP_MIRROR="${PIP_MIRROR}" \
    --build-arg CONDA_MIRROR="${CONDA_MIRROR}" \
    --build-arg PYTHON_VERSION="${PYTHON_VERSION}" \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -t "${FULL_IMAGE}" \
    .

BUILD_DURATION=$(($(date +%s) - BUILD_START))
IMAGE_SIZE=$(docker images --format '{{.Size}}' "${FULL_IMAGE}" | head -1)

log_metric "build_duration_seconds" "$BUILD_DURATION" "seconds"
log_metric "image_size_mb" "$(echo "$IMAGE_SIZE" | grep -oE '[0-9.]+' | head -1)" "mb"
log_event "image_build_complete" "image=$FULL_IMAGE" "duration=${BUILD_DURATION}s" "size=$IMAGE_SIZE"

log_ok "构建完成: ${FULL_IMAGE}"
log_info "镜像大小: ${IMAGE_SIZE}"
log_info "构建耗时: ${BUILD_DURATION}s"

# ── 使用提示 ──
if [ "$LOG_FORMAT" != "json" ] || [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then
    echo ""
    echo -e "${_CLR_CYAN}快速启动:${_CLR_RESET}"
    echo "  docker run -d -p 2222:22 -p 8888:8888 \\"
    echo "    -e USER_PASSWORD=changeme -e JUPYTER_TOKEN=mysecret \\"
    echo "    -v \$(pwd)/workspace:/workspace \\"
    echo "    --name caffe-ffi ${FULL_IMAGE}"
    echo ""
    echo -e "${_CLR_CYAN}SSH 访问:${_CLR_RESET}"
    echo "  ssh -p 2222 jupyteruser@localhost"
    echo ""
    echo -e "${_CLR_CYAN}Jupyter 访问:${_CLR_RESET}"
    echo "  http://localhost:8888/?token=mysecret"
    echo "  Kernel: Python ${PYTHON_VERSION} (caffe-ffi)"
    echo ""
    echo -e "${_CLR_CYAN}验证 caffe-ffi:${_CLR_RESET}"
    echo "  docker exec caffe-ffi bash -lc \\"
    echo "    'source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && \\"
    echo "     python -c \"import caffe_ffi; print(caffe_ffi.__version__)\"'"
    echo ""
fi

# ── 验证 ──
if $VERIFY; then
    log_step "阶段 3/3: 构建后验证"
    log_info "启动验证容器..."

    VERIFY_CONTAINER="verify-caffe-ffi-$(date +%s)"
    VERIFY_PASS=0
    VERIFY_FAIL=0
    VERIFY_TOTAL=0
    VERIFY_START=$(date +%s)

    if ! docker run -d --name "$VERIFY_CONTAINER" \
        -e USER_PASSWORD=verifypass \
        -e JUPYTER_TOKEN=verifytoken \
        -p 0:22 -p 0:8888 \
        "$FULL_IMAGE"; then
        log_fail "验证容器启动失败"
        log_event "build_error" "phase=verify" "error=container_start_failed"
        exit 1
    fi
    log_set_field "verify_container" "$VERIFY_CONTAINER"

    log_info "等待服务启动（15秒）..."
    sleep 15

    # ── 验证项 ──
    verify() {
        local desc="$1"; shift
        VERIFY_TOTAL=$((VERIFY_TOTAL + 1))
        log_info "检查: $desc"
        if "$@"; then
            log_ok "$desc: 通过"
            VERIFY_PASS=$((VERIFY_PASS + 1))
        else
            log_fail "$desc: 失败"
            VERIFY_FAIL=$((VERIFY_FAIL + 1))
        fi
    }

    verify "SSH + Jupyter 服务状态" \
        docker exec "$VERIFY_CONTAINER" supervisorctl status

    verify "caffe_ffi Python 导入" \
        docker exec "$VERIFY_CONTAINER" bash -lc \
        "source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && python -c 'import caffe_ffi; print(\"caffe_ffi OK\")'"

    verify "_caffe_ffi.so 共享库解析" \
        docker exec "$VERIFY_CONTAINER" bash -lc \
        "source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && \
         _SO=\$(python -c 'import caffe_ffi,os; print(os.path.join(os.path.dirname(caffe_ffi.__file__), \"_caffe_ffi.so\"))') && \
         echo \"_caffe_ffi.so: \$_SO\" && \
         if ldd \"\$_SO\" 2>&1 | grep -q 'not found'; then echo '[FAIL] Unresolved shared libraries:'; ldd \"\$_SO\" | grep 'not found'; exit 1; \
         else echo '[OK] All shared libraries resolved'; fi"

    verify "Jupyter kernelspec" \
        docker exec "$VERIFY_CONTAINER" bash -lc \
        "source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && jupyter kernelspec list"

    verify "numpy 导入" \
        docker exec "$VERIFY_CONTAINER" bash -lc \
        "source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && python -c 'import numpy; print(\"numpy\", numpy.__version__)'"

    verify "protobuf 导入" \
        docker exec "$VERIFY_CONTAINER" bash -lc \
        "source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && python -c 'import google.protobuf; print(\"protobuf OK\")'"

    # ── 清理验证容器 ──
    docker rm -f "$VERIFY_CONTAINER" >/dev/null 2>&1
    log_info "验证容器已清理"

    VERIFY_DURATION=$(($(date +%s) - VERIFY_START))
    BUILD_TOTAL_DURATION=$(($(date +%s) - BUILD_START))

    log_metric "verify_passed" "$VERIFY_PASS" "count"
    log_metric "verify_failed" "$VERIFY_FAIL" "count"
    log_metric "verify_duration_seconds" "$VERIFY_DURATION" "seconds"

    if [ "$VERIFY_FAIL" -eq 0 ]; then
        log_event "build_complete" "status=success" "pass=$VERIFY_PASS" "fail=0" "total_duration=${BUILD_TOTAL_DURATION}s"
        log_summary "$VERIFY_PASS" "$VERIFY_FAIL" "$VERIFY_TOTAL" "$BUILD_TOTAL_DURATION" "success"
    else
        log_event "build_complete" "status=failed" "pass=$VERIFY_PASS" "fail=$VERIFY_FAIL" "total_duration=${BUILD_TOTAL_DURATION}s"
        log_summary "$VERIFY_PASS" "$VERIFY_FAIL" "$VERIFY_TOTAL" "$BUILD_TOTAL_DURATION" "failed"
        exit 1
    fi
else
    BUILD_TOTAL_DURATION="$BUILD_DURATION"
    log_event "build_complete" "status=success" "verify=skipped" "duration=${BUILD_TOTAL_DURATION}s"
    log_step "构建完成"
    log_ok "镜像构建成功（跳过验证，使用 --verify 参数启用验证）"
fi
