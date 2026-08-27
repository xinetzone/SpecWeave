#!/bin/bash
set -euo pipefail

export PATH="/usr/bin:/usr/local/bin:/usr/sbin:/usr/local/sbin:/sbin:/bin:$PATH"
VARIANTS_DIR="/mnt/d/spaces/SpecWeave/apps/docker-images/devcontainer-base/variants"
LOG_DIR="/mnt/d/spaces/SpecWeave/apps/docker-images/devcontainer-base/logs"
mkdir -p "$LOG_DIR"

# Start dockerd if not running
if ! docker info >/dev/null 2>&1; then
    echo "Starting dockerd..."
    pkill dockerd 2>/dev/null || true
    sleep 1
    rm -f /var/run/docker.sock
    dockerd >/tmp/dockerd-root.log 2>&1 &
    for i in $(seq 1 30); do
        if docker info >/dev/null 2>&1; then
            echo "Docker ready after ${i}s"
            break
        fi
        sleep 1
    done
fi

echo "=== Docker Server Version ==="
docker version --format '{{.Server.Version}}'

echo ""
echo "=== Disk space ==="
df -h / | tail -1

echo ""
echo "=== Existing images (baseline) ==="
docker images | grep -E "REPOSITORY|devcontainer-base|conda-llvm|onnx-dev|onnx-quantized" || true

echo ""
echo "=== Pruning builder cache ==="
docker builder prune -af 2>&1 | tail -3

# Build function
build_variant() {
    local name=$1
    local dockerfile=$2
    local tag=$3
    local base_arg=$4
    
    echo ""
    echo "=========================================="
    echo "=== Building: ${name} ==="
    echo "=== Tag: ${tag} ==="
    echo "=========================================="
    
    cd "$VARIANTS_DIR"
    
    local build_args=(
        --progress=plain
        -f "$dockerfile"
        --build-arg APT_MIRROR=aliyun
        --build-arg CONDA_MIRROR=bfsu
        --build-arg PIP_MIRROR=aliyun
        -t "$tag"
    )
    
    if [ -n "$base_arg" ]; then
        build_args+=(--build-arg "$base_arg")
    fi
    
    build_args+=(.)
    
    DOCKER_BUILDKIT=1 docker build "${build_args[@]}" 2>&1 | tee "$LOG_DIR/build-${name}.log"
    
    echo ""
    echo "=== ${name} build complete ==="
    docker images | grep -E "REPOSITORY|${tag}"
}

# Step 1: Build conda-llvm (base toolchain) - NO_CACHE to get clean slim build
build_variant "conda-llvm-slim" "conda-llvm/Dockerfile" "devcontainer-base:conda-llvm-slim" ""

# Step 2: Build onnx-dev (depends on conda-llvm-slim)
build_variant "onnx-dev-slim" "onnx-dev/Dockerfile" "devcontainer-base:onnx-dev-slim" "BASE_IMAGE=devcontainer-base:conda-llvm-slim"

# Step 3: Build onnx-quantized (depends on onnx-dev-slim)
build_variant "onnx-quantized-slim" "onnx-quantized/Dockerfile" "devcontainer-base:onnx-quantized-slim" "BASE_IMAGE=devcontainer-base:onnx-dev-slim"

echo ""
echo "=========================================="
echo "=== ALL BUILDS COMPLETE ==="
echo "=========================================="
echo ""
echo "=== Final image sizes ==="
docker images | grep -E "REPOSITORY|devcontainer-base"
echo ""
echo "Build logs saved to: $LOG_DIR/"
ls -lh "$LOG_DIR"/build-*.log
