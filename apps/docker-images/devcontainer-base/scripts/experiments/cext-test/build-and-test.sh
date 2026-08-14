#!/usr/bin/env bash
# =============================================================================
# build-and-test.sh — C扩展构建+测试入口脚本（宿主机执行）
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
TEST_DIR="${SCRIPT_DIR}"
IMAGE="${IMAGE:-devcontainer-base:v2.2-fasttest}"
CONTAINER_NAME="cext-build-$(date +%s)"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  C Extension Free-Threading Build & Test (cmake+ninja)     ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  Image:  %-51s║\n" "$IMAGE"
printf "║  Source: %-51s║\n" "$TEST_DIR"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ── 清理旧容器 ──
docker rm -f $(docker ps -aq --filter name=cext-build-) 2>/dev/null || true

# ── Step 1: 启动容器 ──
echo ">>> Step 1/3: Starting container..."
docker run -d \
    --name "$CONTAINER_NAME" \
    -v "${TEST_DIR}:/cext-test:ro" \
    "$IMAGE" \
    tail -f /dev/null >/dev/null
sleep 2
echo "[OK] Container $CONTAINER_NAME started"

# ── Step 2: 安装构建工具 ──
echo ""
echo ">>> Step 2/3: Installing build toolchain (cmake/ninja/gcc)..."
TOOL_START=$(date +%s)
docker exec "$CONTAINER_NAME" bash -c '
    export PATH="/opt/conda/envs/main/bin:/opt/conda/bin:$PATH"
    conda install -y -n main -c conda-forge \
        "cmake>=3.30" \
        "ninja>=1.12" \
        "make" \
        "c-compiler" \
        "cxx-compiler" \
        "pkg-config" \
        2>&1 | tail -15
    echo "---"
    cmake --version | head -1
    ninja --version
    gcc --version | head -1
'
TOOL_END=$(date +%s)
echo "[OK] Build tools installed in $((TOOL_END - TOOL_START))s"

# ── Step 3: 运行构建+测试 ──
echo ""
echo ">>> Step 3/3: Building C extension and running tests..."
# Copy the inside-container script and run it
docker cp "${TEST_DIR}/run-inside-container.sh" "$CONTAINER_NAME:/tmp/run-test.sh"
docker exec "$CONTAINER_NAME" bash /tmp/run-test.sh
BUILD_STATUS=$?

# ── 拷贝结果 ──
echo ""
echo ">>> Copying build artifacts..."
docker cp "$CONTAINER_NAME:/build/ft_test_ext.so" "${TEST_DIR}/ft_test_ext.cpython-314t-x86_64-linux-gnu.so" 2>/dev/null && {
    echo "[OK] Compiled .so saved to: ${TEST_DIR}/ft_test_ext.cpython-314t-x86_64-linux-gnu.so"
    ls -lh "${TEST_DIR}/ft_test_ext.cpython-314t-x86_64-linux-gnu.so"
} || echo "[WARN] Could not copy .so file"

# ── 清理 ──
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

echo ""
if [ $BUILD_STATUS -eq 0 ]; then
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  SUCCESS: cmake+ninja C extension verified on Python 3.14t ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
else
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  FAILED (exit code: $BUILD_STATUS)"
    echo "╚══════════════════════════════════════════════════════════════╝"
    exit $BUILD_STATUS
fi
