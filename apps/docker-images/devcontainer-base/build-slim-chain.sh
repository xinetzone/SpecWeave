#!/bin/bash
set -euo pipefail

export PATH="/usr/bin:/usr/local/bin:/usr/sbin:/usr/local/sbin:/sbin:/bin:$PATH"

SRC_DIR="/mnt/d/spaces/SpecWeave/apps/docker-images/devcontainer-base"
VARIANTS_DIR="$SRC_DIR/variants"
LOG_DIR="$SRC_DIR/logs"
SLIM_TAG="slim"
mkdir -p "$LOG_DIR"

echo "=== [1/8] Restarting dockerd with updated mirrors ==="
pkill dockerd 2>/dev/null || true
sleep 2
rm -f /var/run/docker.sock
mkdir -p /etc/docker
cp "$SRC_DIR/daemon.json" /etc/docker/daemon.json
nohup dockerd >/tmp/dockerd-root.log 2>&1 &
for i in $(seq 1 30); do
    if docker info >/dev/null 2>&1; then
        echo "Docker ready after ${i}s"
        break
    fi
    sleep 1
done
docker version --format 'Server: {{.Server.Version}}'

echo ""
echo "=== [2/8] Disk space ==="
df -h / | tail -1
AVAIL_GB=$(df -k / | tail -1 | awk '{print int($4/1024/1024)}')
echo "Available: ${AVAIL_GB}GB"

echo ""
echo "=== [3/8] Clean up failed build cache ==="
docker builder prune -af 2>&1 | tail -3

echo ""
echo "=== [4/8] Building root image devcontainer-base:${SLIM_TAG} ==="
cd "$SRC_DIR"
DOCKER_BUILDKIT=1 docker build \
    --progress=plain \
    --build-arg APT_MIRROR=aliyun \
    --build-arg DOCKER_MIRROR=aliyun \
    --build-arg CONDA_MIRROR=bfsu \
    --build-arg PIP_MIRROR=aliyun \
    -t "devcontainer-base:${SLIM_TAG}" \
    . 2>&1 | tee "$LOG_DIR/build-root-${SLIM_TAG}.log"
echo "Root image built."
docker images "devcontainer-base:${SLIM_TAG}"

build_variant() {
    local variant_name=$1
    local dockerfile=$2
    
    echo ""
    echo "=========================================="
    echo "=== Building: ${variant_name} (BASE_TAG=${SLIM_TAG}) ==="
    echo "=========================================="
    
    cd "$VARIANTS_DIR"
    local target_tag="devcontainer-base:${variant_name}-${SLIM_TAG}"
    
    DOCKER_BUILDKIT=1 docker build \
        --progress=plain \
        -f "$dockerfile" \
        --build-arg BASE_TAG="$SLIM_TAG" \
        --build-arg APT_MIRROR=aliyun \
        --build-arg CONDA_MIRROR=bfsu \
        --build-arg PIP_MIRROR=aliyun \
        -t "$target_tag" \
        . 2>&1 | tee "$LOG_DIR/build-${variant_name}-${SLIM_TAG}.log"
    
    echo ""
    echo "=== ${variant_name} build complete ==="
    docker images "$target_tag"
}

echo ""
echo "=== [5/8] Building conda-llvm ==="
build_variant "conda-llvm" "conda-llvm/Dockerfile"

echo ""
echo "=== [6/8] Building onnx-dev ==="
build_variant "onnx-dev" "onnx-dev/Dockerfile"

echo ""
echo "=== [7/8] Building onnx-quantized ==="
build_variant "onnx-quantized" "onnx-quantized/Dockerfile"

echo ""
echo "=== [8/8] ALL BUILDS COMPLETE ==="
echo "=========================================="
echo ""
echo "=== Final image sizes ==="
docker images | grep -E "REPOSITORY|devcontainer-base"
echo ""
echo "=== Build logs ==="
ls -lh "$LOG_DIR"/build-*-${SLIM_TAG}.log 2>/dev/null
