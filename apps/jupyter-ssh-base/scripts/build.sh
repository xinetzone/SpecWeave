#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

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
  -t, --tag TAG          Image tag (default: 1.0)
  -n, --name NAME        Image name (default: jupyter-ssh-base)
  -r, --registry REG     Registry prefix (e.g., your-registry.com)
  --no-cache             Disable Docker build cache
  --cn                   Use China mirrors (aliyun apt + aliyun pip)
  --apt-mirror MIRROR    APT mirror: official|aliyun|tuna (default: official)
  --pip-mirror MIRROR    PyPI mirror: official|aliyun|tuna (default: official)
  --verify               Run embedded verification after build
  --verify-only           Only verify existing image (skip build)
  -h, --help              Show this help message

Environment variables (overridden by CLI args):
  IMAGE_NAME, IMAGE_TAG, REGISTRY, APT_MIRROR, PIP_MIRROR

Examples:
  $0                                    # Build with default settings
  $0 --tag latest --cn                  # Build :latest with China mirrors
  $0 --no-cache -t dev                  # Build without cache, tag as dev
  $0 --verify                           # Build and verify
  $0 --verify-only --tag 1.0            # Verify existing image only
EOF
}

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

# ------------------------------------------------------------------------------
# 嵌入式验证：启动临时容器运行验证脚本，失败则退出
# ------------------------------------------------------------------------------
verify_image() {
    echo ""
    echo "========================================"
    echo "Verifying ${FULL_IMAGE}..."
    echo "========================================"
    echo ""

    local verify_container="verify-${IMAGE_NAME}-$(date +%s)"
    local verify_result=0

    # 启动临时验证容器
    docker run -d --name "$verify_container" \
        -e USER_PASSWORD=verifypass \
        -e JUPYTER_TOKEN=verifytoken \
        -p 0:22 -p 0:8888 \
        "$FULL_IMAGE" || {
        echo "[FAIL] Failed to start verification container"
        return 1
    }

    # 等待服务启动
    echo "[INFO] Waiting for services to start..."
    sleep 10

    # 运行健康检查
    echo "[INFO] Running healthcheck..."
    docker exec "$verify_container" /usr/local/bin/healthcheck.sh || verify_result=1

    # SSH 非交互路径验证
    echo "[INFO] Verifying SSH non-interactive PATH..."
    docker exec "$verify_container" /bin/bash -c \
        'ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no -p 22 jupyteruser@localhost "which jupyter"' 2>/dev/null || {
        echo "[WARN] SSH non-interactive PATH check failed (may be expected if no SSH key)"
    }

    # Jupyter API 验证
    echo "[INFO] Verifying Jupyter API..."
    docker exec "$verify_container" curl -sf http://localhost:8888/api >/dev/null || {
        echo "[FAIL] Jupyter API not responding"
        verify_result=1
    }

    # 清理
    docker rm -f "$verify_container" >/dev/null 2>&1

    if [ "$verify_result" -eq 0 ]; then
        echo ""
        echo "[PASS] All verification checks passed"
        echo ""
    else
        echo ""
        echo "[FAIL] Verification failed!"
        exit 1
    fi
}

if $VERIFY_ONLY; then
    verify_image
    exit 0
fi

echo "========================================"
echo "Building ${FULL_IMAGE}"
echo "Project dir: ${PROJECT_DIR}"
echo "APT mirror:  ${APT_MIRROR}"
echo "PyPI mirror: ${PIP_MIRROR}"
if [ -n "$NO_CACHE" ]; then echo "Cache:       disabled"; fi
echo "========================================"
echo ""

DOCKER_BUILDKIT=1 docker build \
    ${NO_CACHE} \
    --build-arg APT_MIRROR="${APT_MIRROR}" \
    --build-arg PIP_MIRROR="${PIP_MIRROR}" \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -t "${FULL_IMAGE}" \
    .

echo ""
echo "========================================"
echo "Build complete: ${FULL_IMAGE}"
IMAGE_SIZE=$(docker images --format '{{.Size}}' "${FULL_IMAGE}" | head -1)
echo "Image size: ${IMAGE_SIZE}"
echo "========================================"
echo ""
echo "Quick start:"
echo "  docker run -d -p 2222:22 -p 8888:8888 -v \$(pwd)/workspace:/workspace \\"
echo "    -e USER_PASSWORD=mypassword -e JUPYTER_TOKEN=mysecret ${FULL_IMAGE}"
echo ""
echo "SSH access:"
echo "  ssh -p 2222 jupyteruser@localhost"
echo ""
echo "Jupyter access:"
echo "  http://localhost:8888/?token=mysecret"
echo ""
if [ -n "$REGISTRY" ]; then
    echo "To push:"
    echo "  docker push ${FULL_IMAGE}"
fi

if $VERIFY; then
    verify_image
fi
