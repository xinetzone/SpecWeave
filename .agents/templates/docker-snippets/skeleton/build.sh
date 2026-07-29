#!/bin/bash
# 一键构建Docker运行时镜像
# 用法: bash build.sh -t <image:tag> [context_dir]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_TAG=""
CONTEXT_DIR="."
PULL=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        -t|--tag) IMAGE_TAG="$2"; shift 2 ;;
        --pull) PULL=1; shift ;;
        -h|--help)
            echo "Usage: $0 -t <image:tag> [--pull] [context_dir]"
            echo "  -t, --tag    Image tag (required)"
            echo "  --pull       Pull latest base image"
            echo "  context_dir  Docker build context (default: .)"
            exit 0
            ;;
        *) CONTEXT_DIR="$1"; shift ;;
    esac
done

if [ -z "$IMAGE_TAG" ]; then
    echo "Error: -t <image:tag> is required"
    exit 1
fi

DOCKERFILE="$SCRIPT_DIR/Dockerfile"

echo "=== Building Docker image: $IMAGE_TAG ==="
echo "    Dockerfile: $DOCKERFILE"
echo "    Context:    $CONTEXT_DIR"
echo ""

BUILD_ARGS=()
if [ $PULL -eq 1 ]; then
    BUILD_ARGS+=(--pull)
fi

docker build \
    "${BUILD_ARGS[@]}" \
    -f "$DOCKERFILE" \
    -t "$IMAGE_TAG" \
    "$CONTEXT_DIR"

echo ""
echo "=== Build complete ==="
echo "Image: $IMAGE_TAG"
echo "Size:"
docker images "$IMAGE_TAG" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
echo ""
echo "Quick test:"
echo "  docker run --rm $IMAGE_TAG python -c 'print(\"OK\")'"
