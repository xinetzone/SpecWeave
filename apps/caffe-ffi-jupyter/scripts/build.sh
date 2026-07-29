#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
# Build context is SpecWeave root (3 levels up from scripts/: scripts -> app -> apps -> root)
CONTEXT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DOCKERFILE="${APP_DIR}/Dockerfile"

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

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Build the caffe-ffi-jupyter Docker image.

Prerequisites:
  - jupyter-ssh-base:1.1 must be built first (run ../jupyter-ssh-base/scripts/build.sh)

Options:
  -t, --tag TAG          Image tag (default: latest)
  -n, --name NAME        Image name (default: caffe-ffi-jupyter)
  -r, --registry REG     Registry prefix (e.g., your-registry.com)
  --base-image IMAGE     Base image name (default: jupyter-ssh-base:1.1)
  --python-version VER   Python version for conda env (default: 3.14)
  --no-cache             Disable Docker build cache
  --cn                   Use China mirrors (aliyun apt/pip + tuna conda)
  --apt-mirror MIRROR    APT mirror: official|aliyun|tuna (default: official)
  --pip-mirror MIRROR    PyPI mirror: official|aliyun|tuna (default: official)
  --conda-mirror MIRROR  Conda mirror: official|tuna (default: official)
  --verify               Run verification after build
  -h, --help             Show this help message

Environment variables (overridden by CLI args):
  IMAGE_NAME, IMAGE_TAG, REGISTRY, APT_MIRROR, PIP_MIRROR, CONDA_MIRROR,
  PYTHON_VERSION, BASE_IMAGE

Examples:
  $0                                    # Build with default settings
  $0 --cn                               # Build with China mirrors (recommended in CN)
  $0 --tag dev --no-cache               # Build without cache, tag as dev
  $0 --verify                           # Build and run verification
EOF
}

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
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

if [ -n "$REGISTRY" ]; then
    FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
else
    FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"
fi

echo "========================================"
echo "Building ${FULL_IMAGE}"
echo "Context dir:  ${CONTEXT_DIR}"
echo "Dockerfile:   ${DOCKERFILE}"
echo "Base image:   ${BASE_IMAGE}"
echo "Python:       ${PYTHON_VERSION}"
echo "APT mirror:   ${APT_MIRROR}"
echo "PyPI mirror:  ${PIP_MIRROR}"
echo "Conda mirror: ${CONDA_MIRROR}"
if [ -n "$NO_CACHE" ]; then echo "Cache:        disabled"; fi
echo "========================================"
echo ""

# Check that base image exists
echo "[CHECK] Verifying base image '${BASE_IMAGE}' exists..."
if ! docker image inspect "${BASE_IMAGE}" >/dev/null 2>&1; then
    echo ""
    echo "[ERROR] Base image '${BASE_IMAGE}' not found!"
    echo ""
    echo "Please build jupyter-ssh-base first:"
    echo "  cd ${APP_DIR}/../jupyter-ssh-base"
    echo "  bash scripts/build.sh${APT_MIRROR:+ --apt-mirror ${APT_MIRROR}}${PIP_MIRROR:+ --pip-mirror ${PIP_MIRROR}}"
    echo ""
    exit 1
fi
echo "[OK] Base image '${BASE_IMAGE}' found"
echo ""

# Check that caffe-ffi source exists
CAFFE_FFI_SRC="${CONTEXT_DIR}/projects/xuanspace/libs/caffe-ffi"
if [ ! -f "${CAFFE_FFI_SRC}/CMakeLists.txt" ]; then
    echo "[ERROR] caffe-ffi source not found at: ${CAFFE_FFI_SRC}"
    echo "Make sure the xuanspace submodule is initialized and updated:"
    echo "  cd ${CONTEXT_DIR} && git submodule update --init projects/xuanspace"
    exit 1
fi
echo "[OK] caffe-ffi source found at: ${CAFFE_FFI_SRC}"
echo ""

# Build from SpecWeave root context
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

echo ""
echo "========================================"
echo "Build complete: ${FULL_IMAGE}"
IMAGE_SIZE=$(docker images --format '{{.Size}}' "${FULL_IMAGE}" | head -1)
echo "Image size: ${IMAGE_SIZE}"
echo "========================================"
echo ""
echo "Quick start:"
echo "  docker run -d -p 2222:22 -p 8888:8888 \\"
echo "    -e USER_PASSWORD=changeme -e JUPYTER_TOKEN=mysecret \\"
echo "    -v \$(pwd)/workspace:/workspace \\"
echo "    --name caffe-ffi ${FULL_IMAGE}"
echo ""
echo "SSH access:"
echo "  ssh -p 2222 jupyteruser@localhost"
echo ""
echo "Jupyter access:"
echo "  http://localhost:8888/?token=mysecret"
echo "  Kernel: Python 3.14 (caffe-ffi)"
echo ""
echo "Verify caffe-ffi:"
echo "  docker exec caffe-ffi bash -lc \\"
echo "    'source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && \\"
echo "     python -c \"import caffe_ffi; print(caffe_ffi.__version__)\"'"
echo ""

if $VERIFY; then
    echo "[VERIFY] Running verification..."
    echo ""

    VERIFY_CONTAINER="verify-caffe-ffi-$(date +%s)"

    docker run -d --name "$VERIFY_CONTAINER" \
        -e USER_PASSWORD=verifypass \
        -e JUPYTER_TOKEN=verifytoken \
        -p 0:22 -p 0:8888 \
        "$FULL_IMAGE" || {
        echo "[FAIL] Failed to start verification container"
        exit 1
    }

    echo "[VERIFY] Waiting for services to start (15s)..."
    sleep 15

    VERIFY_RESULT=0

    echo "[VERIFY] Checking SSH + Jupyter services..."
    docker exec "$VERIFY_CONTAINER" supervisorctl status || VERIFY_RESULT=1

    echo "[VERIFY] Checking caffe_ffi import..."
    docker exec "$VERIFY_CONTAINER" bash -lc \
        "source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && python -c 'import caffe_ffi; print(\"caffe_ffi OK\")'" || {
        echo "[FAIL] caffe_ffi import failed"
        VERIFY_RESULT=1
    }

    echo "[VERIFY] Checking Jupyter kernelspec..."
    docker exec "$VERIFY_CONTAINER" bash -lc \
        "source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && jupyter kernelspec list" || {
        echo "[FAIL] Jupyter kernelspec check failed"
        VERIFY_RESULT=1
    }

    echo "[VERIFY] Checking numpy..."
    docker exec "$VERIFY_CONTAINER" bash -lc \
        "source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && python -c 'import numpy; print(\"numpy\", numpy.__version__)'" || VERIFY_RESULT=1

    echo "[VERIFY] Checking protobuf..."
    docker exec "$VERIFY_CONTAINER" bash -lc \
        "source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && python -c 'import google.protobuf; print(\"protobuf OK\")'" || VERIFY_RESULT=1

    docker rm -f "$VERIFY_CONTAINER" >/dev/null 2>&1

    if [ "$VERIFY_RESULT" -eq 0 ]; then
        echo ""
        echo "[PASS] All verification checks passed"
        echo ""
    else
        echo ""
        echo "[FAIL] Verification failed!"
        exit 1
    fi
fi
