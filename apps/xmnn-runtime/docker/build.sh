#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

IMAGE_TAG="${1:-xmnn-runtime-skeleton:test}"

echo "=== Building XMNN Runtime Image (Skeleton Template) ==="
echo "    Dockerfile: ${SCRIPT_DIR}/Dockerfile"
echo "    Context:    ${PROJECT_DIR}"
echo "    Image Tag:  ${IMAGE_TAG}"
echo ""

cd "${PROJECT_DIR}"
docker build -f docker/Dockerfile -t "${IMAGE_TAG}" .

echo ""
echo "=== Build Complete ==="
docker images "${IMAGE_TAG}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
