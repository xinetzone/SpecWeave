#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ── 加载统一日志库 ──
source "${SCRIPT_DIR}/lib/logging.sh"
LOG_SERVICE="xmnn-runtime-build"
LOG_JSON_OUTPUT="/tmp/xmnn-runtime-events.jsonl"

IMAGE_TAG="${1:-xmnn-runtime-skeleton:test}"

# ── 解析日志参数（若通过 $2 传入） ──
if [ $# -gt 1 ]; then
    eval "$(log_parse_args "$@")"
fi

log_set_field "image" "$IMAGE_TAG"
log_step "Building XMNN Runtime Image"
log_info "Dockerfile: ${SCRIPT_DIR}/Dockerfile"
log_info "Context:    ${PROJECT_DIR}"
log_info "Image Tag:  ${IMAGE_TAG}"
echo ""

BUILD_START=$(date +%s)
log_event "build_start" "image=$IMAGE_TAG"

cd "${PROJECT_DIR}"
docker build -f docker/Dockerfile -t "${IMAGE_TAG}" .

BUILD_END=$(date +%s)
BUILD_DURATION=$((BUILD_END - BUILD_START))
log_metric "build_duration_seconds" "$BUILD_DURATION" "seconds"

echo ""
log_ok "Build Complete"
IMAGE_SIZE=$(docker images --format '{{.Size}}' "${IMAGE_TAG}" | head -1)
log_info "Image size: ${IMAGE_SIZE}"
log_metric "image_size_mb" "$(echo "$IMAGE_SIZE" | grep -oE '[0-9.]+' | head -1)" "mb"
log_event "build_complete" "image=$IMAGE_TAG" "duration=$BUILD_DURATION" "status=success"
echo ""
docker images "${IMAGE_TAG}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
