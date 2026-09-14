#!/bin/bash
# ==============================================================================
# build-wheel.sh — agent-monetize 纯 Python wheel 打包（运行时调用）
#
# 调用：invoke monetize.wheel
#       podman-compose exec monetize bash /opt/monetize-builder/scripts/build-wheel.sh
#
# 产物：$DIST_DIR/agent_monetize-*.whl（setuptools src 布局，py3-none-any）。
# 注意：原生 score_opportunity.so **不**入 wheel（pyproject 现状不含
# ext_modules/package_data）；.so 是挂载源码树 native/build 的运行时产物，
# ffi_bridge 从文件路径加载。本脚本不要求 .so 已编译。
# ==============================================================================
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/logging.sh"
LOG_FILE=/dev/null
log_enable_trap

SRC_ROOT="${SRC_ROOT:-/workspace/agent-monetize}"
DIST_DIR="${DIST_DIR:-/workspace/dist}"
BASE_PYTHON=/opt/conda/bin/python

if [ ! -f "$SRC_ROOT/pyproject.toml" ]; then
    log_error "未找到 $SRC_ROOT/pyproject.toml（SRC_ROOT 挂载是否正确？）"
    exit 2
fi
if [ "$("$BASE_PYTHON" -c 'import build' 2>/dev/null && echo ok)" != "ok" ]; then
    log_error "base env 缺少 build 模块（镜像应已 pip 装 build）"
    exit 2
fi

mkdir -p "$DIST_DIR"
cd "$SRC_ROOT"

echo ""
log_step "Building agent-monetize wheel (pure Python, setuptools)"
set +e
"$BASE_PYTHON" -m build --wheel --no-isolation --outdir "$DIST_DIR" 2>&1
BUILD_EXIT=$?
set -e
if [ "$BUILD_EXIT" -ne 0 ]; then
    log_error "Wheel build failed with exit code $BUILD_EXIT"
    exit "$BUILD_EXIT"
fi

echo ""
log_section "List dist contents"
ls -la "$DIST_DIR"/agent_monetize-*.whl
WHL_FILE="$(ls "$DIST_DIR"/agent_monetize-*.whl 2>/dev/null | head -1 || true)"
if [ -n "$WHL_FILE" ]; then
    log_ok "Wheel: $WHL_FILE ($(du -h "$WHL_FILE" | cut -f1))（宿主可见于 workspace/dist）"
else
    log_error "No agent_monetize wheel found in $DIST_DIR"
    exit 1
fi
