#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

IMAGE_NAME="${IMAGE_NAME:-jupyter-ssh-base}"
IMAGE_TAG="${IMAGE_TAG:-1.0}"
REGISTRY="${REGISTRY:-}"
NO_CACHE=""
APT_MIRROR="${APT_MIRROR:-official}"
PIP_MIRROR="${PIP_MIRROR:-official}"

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
  -h, --help             Show this help message

Environment variables (overridden by CLI args):
  IMAGE_NAME, IMAGE_TAG, REGISTRY, APT_MIRROR, PIP_MIRROR

Examples:
  $0                                    # Build with default settings
  $0 --tag latest --cn                  # Build :latest with China mirrors
  $0 --no-cache -t dev                  # Build without cache, tag as dev
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
