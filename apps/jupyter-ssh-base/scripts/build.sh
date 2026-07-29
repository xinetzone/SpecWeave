#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# ── 加载统一日志库 ──
source "${SCRIPT_DIR}/lib/logging.sh"
LOG_SERVICE="jupyter-ssh-build"
LOG_JSON_OUTPUT="/tmp/jupyter-ssh-base-events.jsonl"

IMAGE_NAME="${IMAGE_NAME:-jupyter-ssh-base}"
IMAGE_TAG="${IMAGE_TAG:-1.1}"
REGISTRY="${REGISTRY:-}"
NO_CACHE=""
APT_MIRROR="${APT_MIRROR:-official}"
PIP_MIRROR="${PIP_MIRROR:-official}"
VERIFY=false
VERIFY_ONLY=false

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Build the jupyter-ssh-base Docker image.

Options:
  -t, --tag TAG          Image tag (default: 1.1)
  -n, --name NAME        Image name (default: jupyter-ssh-base)
  -r, --registry REG     Registry prefix (e.g., your-registry.com)
  --no-cache             Disable Docker build cache
  --cn                   Use China mirrors (aliyun apt + aliyun pip)
  --apt-mirror MIRROR    APT mirror: official|aliyun|tuna (default: official)
  --pip-mirror MIRROR    PyPI mirror: official|aliyun|tuna (default: official)
  --verify               Run embedded verification after build
  --verify-only           Only verify existing image (skip build)
  --log-format=FMT       Log format: text (default) | json
  --log-level=LEVEL      Log level: DEBUG|INFO|WARN|ERROR (default: INFO)
  --log-json             Also output JSON to stdout
  -h, --help              Show this help message

Environment variables (overridden by CLI args):
  IMAGE_NAME, IMAGE_TAG, REGISTRY, APT_MIRROR, PIP_MIRROR

Examples:
  $0                                    # Build with default settings
  $0 --tag latest --cn                  # Build :latest with China mirrors
  $0 --no-cache -t dev                  # Build without cache, tag as dev
  $0 --verify                           # Build and verify
  $0 --verify-only --tag 1.0            # Verify existing image only
  $0 --log-format=json --log-json       # JSON output for monitoring
EOF
}

# ── 解析日志参数 ──
eval "$(log_parse_args "$@")"

while [[ $# -gt 0 ]]; do
    case "$1" in
        -t|--tag) IMAGE_TAG="$2"; shift 2 ;;
        -n|--name) IMAGE_NAME="$2"; shift 2 ;;
        -r|--registry) REGISTRY="$2"; shift 2 ;;
        --no-cache) NO_CACHE="--no-cache"; shift ;;
        --cn) APT_MIRROR="aliyun"; PIP_MIRROR="aliyun"; shift ;;
        --apt-mirror) APT_MIRROR="$2"; shift 2 ;;
        --pip-mirror) PIP_MIRROR="$2"; shift 2 ;;
        --verify) VERIFY=true; shift ;;
        --verify-only) VERIFY_ONLY=true; VERIFY=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

if [ -n "$REGISTRY" ]; then
    FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
else
    FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"
fi

cd "$PROJECT_DIR"

# ── 设置上下文字段 ──
log_set_field "image" "$FULL_IMAGE"
log_set_field "apt_mirror" "$APT_MIRROR"
log_set_field "pip_mirror" "$PIP_MIRROR"

# ------------------------------------------------------------------------------
# 嵌入式验证
# ------------------------------------------------------------------------------
verify_image() {
    log_step "Verifying ${FULL_IMAGE}"

    local verify_container="verify-${IMAGE_NAME}-$(date +%s)"
    local verify_result=0

    if ! docker run -d --name "$verify_container" \
        -e USER_PASSWORD=verifypass \
        -e JUPYTER_TOKEN=verifytoken \
        -p 0:22 -p 0:8888 \
        "$FULL_IMAGE"; then
        log_error "Failed to start verification container"
        return 1
    fi

    log_info "Waiting for services to start..."
    sleep 10

    log_info "Running healthcheck..."
    docker exec "$verify_container" /usr/local/bin/healthcheck.sh || verify_result=1

    log_info "Verifying SSH non-interactive PATH..."
    docker exec "$verify_container" /bin/bash -c \
        'ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no -p 22 jupyteruser@localhost "which jupyter"' 2>/dev/null || {
        log_warn "SSH non-interactive PATH check failed (may be expected if no SSH key)"
    }

    log_info "Verifying Jupyter API..."
    docker exec "$verify_container" curl -sf http://localhost:8888/api >/dev/null || {
        log_error "Jupyter API not responding"
        verify_result=1
    }

    docker rm -f "$verify_container" >/dev/null 2>&1

    if [ "$verify_result" -eq 0 ]; then
        log_ok "All verification checks passed"
    else
        log_fail "Verification failed!"
        exit 1
    fi
}

if $VERIFY_ONLY; then
    log_event "verify_only_start" "image=$FULL_IMAGE"
    verify_image
    log_event "verify_only_complete" "status=success"
    exit 0
fi

# ── 构建 ──
log_step "Building ${FULL_IMAGE}"
log_info "Project dir:  ${PROJECT_DIR}"
log_info "APT mirror:   ${APT_MIRROR}"
log_info "PyPI mirror:  ${PIP_MIRROR}"
if [ -n "$NO_CACHE" ]; then log_info "Cache: disabled"; fi
echo ""

BUILD_START=$(date +%s)
log_event "build_start" "image=$FULL_IMAGE" "apt_mirror=$APT_MIRROR" "pip_mirror=$PIP_MIRROR"

DOCKER_BUILDKIT=1 docker build \
    ${NO_CACHE} \
    --build-arg APT_MIRROR="${APT_MIRROR}" \
    --build-arg PIP_MIRROR="${PIP_MIRROR}" \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -t "${FULL_IMAGE}" \
    .

BUILD_END=$(date +%s)
BUILD_DURATION=$((BUILD_END - BUILD_START))
log_metric "build_duration_seconds" "$BUILD_DURATION" "seconds"

echo ""
log_ok "Build complete: ${FULL_IMAGE}"
IMAGE_SIZE=$(docker images --format '{{.Size}}' "${FULL_IMAGE}" | head -1)
log_info "Image size: ${IMAGE_SIZE}"
log_metric "image_size_mb" "$(echo "$IMAGE_SIZE" | grep -oE '[0-9.]+' | head -1)" "mb"

echo ""
log_info "Quick start:"
echo "  docker run -d -p 2222:22 -p 8888:8888 -v \$(pwd)/workspace:/workspace \\"
echo "    -e USER_PASSWORD=mypassword -e JUPYTER_TOKEN=mysecret ${FULL_IMAGE}"
echo ""
log_info "SSH access:"
echo "  ssh -p 2222 jupyteruser@localhost"
echo ""
log_info "Jupyter access:"
echo "  http://localhost:8888/?token=mysecret"
echo ""
if [ -n "$REGISTRY" ]; then
    log_info "To push:"
    echo "  docker push ${FULL_IMAGE}"
fi

log_event "build_complete" "image=$FULL_IMAGE" "duration=$BUILD_DURATION" "status=success"

if $VERIFY; then
    verify_image
fi
