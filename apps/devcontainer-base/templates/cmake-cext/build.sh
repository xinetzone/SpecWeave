#!/usr/bin/env bash
# =============================================================================
# build.sh — Build and test the free-threading C extension template
# =============================================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BUILD_DIR="${BUILD_DIR:-build}"
BUILD_TYPE="${BUILD_TYPE:-Release}"
MODULE_NAME="${MODULE_NAME:-ft_extension}"

echo "=== Building ${MODULE_NAME} (${BUILD_TYPE}) ==="

# ── Configure with CMake + Ninja ──
cmake -G Ninja \
    -B "$BUILD_DIR" \
    -DCMAKE_BUILD_TYPE="$BUILD_TYPE" \
    -DMODULE_NAME="$MODULE_NAME" \
    -DPYTHON_TARGET_VER=3.13 \
    -DREQUIRE_FT=ON

# ── Build ──
cmake --build "$BUILD_DIR" -j"$(nproc 2>/dev/null || echo 4)"

echo ""
echo "=== Build complete ==="
echo "Output: ${SCRIPT_DIR}/${MODULE_NAME}.so"
ls -la "${SCRIPT_DIR}/${MODULE_NAME}.so"

# ── Quick self-test ──
echo ""
echo "=== Running self-test ==="
python -c "import ${MODULE_NAME}; assert ${MODULE_NAME}.run_self_test(), 'Self-test failed'"

# ── Multi-thread stress test (8 threads × 100K iterations) ──
echo ""
echo "=== Running multi-thread stress test ==="
python -c "
import ${MODULE_NAME}
result = ${MODULE_NAME}.thread_stress(8, 100000)
print(f'Threads: {result[\"threads\"]}')
print(f'Iterations per thread: {result[\"iterations_per_thread\"]}')
print(f'Expected: {result[\"expected_total\"]}')
print(f'Actual:   {result[\"actual_total\"]}')
print(f'Correct:  {result[\"correct\"]}')
assert result['correct'], f'Race condition detected! Expected {result[\"expected_total\"]}, got {result[\"actual_total\"]}'
print('Stress test PASSED')
"

echo ""
echo "=== All tests passed ==="
