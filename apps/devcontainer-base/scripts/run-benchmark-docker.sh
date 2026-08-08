#!/usr/bin/env bash
# run-benchmark-docker.sh — Run ONNX quantization benchmark in isolated Docker container
#
# Usage:
#   bash scripts/run-benchmark-docker.sh [--cn] [--quick] [--threads N] [--output DIR] [--variant VARIANT]
#
# Options:
#   --cn         Use domestic (China) mirror for faster dependency resolution
#   --quick      Quick mode: warmup=10, runs=50, calib=20 (for fast validation)
#   --full       Full mode: all models, warmup=20, runs=100, calib=100 (for thorough testing)
#   --threads N  ORT intra-op threads (default: 4)
#   --output DIR Host directory to mount for results (default: ./benchmark-results)
#   --variant V  Variant to use: onnx-pytorch (default) or onnx-quantized (includes FP16 support)
#   --image TAG  Override Docker image (default depends on --variant)
#   --verbose    Verbose mode: pass -v to benchmark script, show docker commands
#   --help       Show this help
#
# Examples:
#   bash scripts/run-benchmark-docker.sh --quick                  # Quick test on onnx-pytorch (INT8 only)
#   bash scripts/run-benchmark-docker.sh --quick --variant onnx-quantized  # Quick test with FP16 support
#   bash scripts/run-benchmark-docker.sh --full --variant onnx-quantized --cn  # Full test with CN mirrors

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Defaults
USE_CN=0
QUICK_MODE=0
FULL_MODE=0
VERBOSE=0
THREADS=4
OUTPUT_DIR="${SCRIPT_DIR}/../benchmark-results"
VARIANT="onnx-pytorch"
IMAGE_TAG=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --cn) USE_CN=1; shift ;;
        --quick) QUICK_MODE=1; shift ;;
        --full) FULL_MODE=1; shift ;;
        --verbose) VERBOSE=1; shift ;;
        --threads) THREADS="$2"; shift 2 ;;
        --output) OUTPUT_DIR="$2"; shift 2 ;;
        --variant) VARIANT="$2"; shift 2 ;;
        --image) IMAGE_TAG="$2"; shift 2 ;;
        --help|-h)
            head -27 "$0" | grep '^#' | sed 's/^# \?//'
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Validate variant
case "$VARIANT" in
    onnx-pytorch|onnx-quantized) ;;
    *) echo "[ERROR] Unknown variant: $VARIANT (supported: onnx-pytorch, onnx-quantized)"; exit 1 ;;
esac

# Set default image based on variant if not overridden
if [ -z "$IMAGE_TAG" ]; then
    IMAGE_TAG="devcontainer-base:${VARIANT}-latest"
fi

# Output directory includes variant name for clarity
if [[ "$OUTPUT_DIR" == "${SCRIPT_DIR}/../benchmark-results" ]]; then
    OUTPUT_DIR="${SCRIPT_DIR}/../benchmark-results-${VARIANT}"
fi

echo "============================================================"
echo "  ONNX Quantization Benchmark — Docker Runner"
echo "============================================================"
echo "  Variant:   ${VARIANT}"
echo "  Image:     ${IMAGE_TAG}"
echo "  Threads:   ${THREADS}"
echo "  Quick mode: $([[ ${QUICK_MODE} -eq 1 ]] && echo 'YES' || echo 'NO')"
echo "  Full mode:  $([[ ${FULL_MODE} -eq 1 ]] && echo 'YES' || echo 'NO')"
echo "  Verbose:    $([[ ${VERBOSE} -eq 1 ]] && echo 'YES' || echo 'NO')"
echo "  CN mirror:  $([[ ${USE_CN} -eq 1 ]] && echo 'YES' || echo 'NO')"
echo "  Output:    ${OUTPUT_DIR}"
echo "============================================================"

# Check Docker availability
if ! command -v docker &>/dev/null; then
    echo "[ERROR] Docker not found. Please install Docker first."
    exit 1
fi

# Check if image exists, build if needed
if ! docker image inspect "${IMAGE_TAG}" &>/dev/null; then
    echo "[INFO] Image '${IMAGE_TAG}' not found locally."
    echo "[INFO] Building ${VARIANT} variant..."

    BUILD_SCRIPT="${SCRIPT_DIR}/../variants/build.sh"
    if [[ ! -f "${BUILD_SCRIPT}" ]]; then
        echo "[ERROR] variants/build.sh not found. Please build the image first:"
        echo "  cd apps/devcontainer-base/variants && bash build.sh --variant ${VARIANT} $([[ ${USE_CN} -eq 1 ]] && echo '--cn')"
        exit 1
    fi

    BUILD_FLAGS="--variant ${VARIANT}"
    [[ ${USE_CN} -eq 1 ]] && BUILD_FLAGS="${BUILD_FLAGS} --cn"
    bash "${BUILD_SCRIPT}" ${BUILD_FLAGS}
fi

# Prepare output directory
mkdir -p "${OUTPUT_DIR}"
OUTPUT_DIR="$(cd "${OUTPUT_DIR}" && pwd)"

# Build benchmark arguments
BENCH_ARGS="--threads ${THREADS}"
if [[ ${QUICK_MODE} -eq 1 ]]; then
    BENCH_ARGS="${BENCH_ARGS} --warmup 10 --runs 50 --calib 20"
elif [[ ${FULL_MODE} -eq 1 ]]; then
    BENCH_ARGS="${BENCH_ARGS} --warmup 20 --runs 100 --calib 100"
else
    BENCH_ARGS="${BENCH_ARGS} --warmup 5 --runs 20 --calib 10"
fi
[[ ${VERBOSE} -eq 1 ]] && BENCH_ARGS="${BENCH_ARGS} -v"
BENCH_ARGS="${BENCH_ARGS} --output /results/benchmark_results.json"

# Environment variables for OpenMP
ENV_VARS=(
    -e OMP_NUM_THREADS="${THREADS}"
    -e OPENBLAS_NUM_THREADS=1
    -e OMP_WAIT_POLICY=PASSIVE
    -e KMP_DUPLICATE_LIB_OK=TRUE
)

# Run the container
# Mount: scripts dir -> /benchmark, output dir -> /results
CONTAINER_NAME="onnx-bench-$(date +%Y%m%d-%H%M%S)"

echo ""
echo "[INFO] Starting benchmark container..."
echo "[INFO] Benchmark args: ${BENCH_ARGS}"
if [[ ${VERBOSE} -eq 1 ]]; then
    echo "[INFO] Docker command:"
    echo "  docker run --rm --name ${CONTAINER_NAME} \\"
    for ev in "${ENV_VARS[@]}"; do
        echo "    ${ev} \\"
    done
    echo "    -v ${SCRIPT_DIR}:/benchmark:ro \\"
    echo "    -v ${OUTPUT_DIR}:/results \\"
    echo "    ${IMAGE_TAG} bash -lc '...'"
    echo ""
fi

docker run --rm \
    --name "${CONTAINER_NAME}" \
    "${ENV_VARS[@]}" \
    -v "${SCRIPT_DIR}:/benchmark:ro" \
    -v "${OUTPUT_DIR}:/results" \
    "${IMAGE_TAG}" \
    bash -lc "
        set -e
        echo '[CONTAINER] Environment info:'
        echo '  Python:' \$(python --version)
        echo '  PyTorch:' \$(python -c 'import torch; print(torch.__version__)')
        echo '  ONNX Runtime:' \$(python -c 'import onnxruntime; print(onnxruntime.__version__)')
        echo '  CPU count:' \$(nproc)
        echo ''
        echo '[CONTAINER] Running benchmark...'
        python /benchmark/benchmark_quantization.py ${BENCH_ARGS}
        echo ''
        echo '[CONTAINER] Benchmark complete! Results saved to /results/benchmark_results.json'
        echo '[CONTAINER] Result summary:'
        python -c \"
import json
with open('/results/benchmark_results.json') as f:
    data = json.load(f)
print(f'  Models tested: {len(data[\"results\"])}')
for name, r in data['results'].items():
    fp32 = r['FP32']['avg_ms']
    best_prec = max(
        [(p, r[p]['speedup']) for p in ['FP16','INT8-Dyn','INT8_Static_QDQ','INT8_Static_QOperator'] if p in r],
        key=lambda x: x[1]
    )
    print(f'  {name}: FP32={fp32:.3f}ms, best={best_prec[0]} ({best_prec[1]:.2f}x)')
\"
    "

echo ""
echo "============================================================"
echo "  Benchmark finished!"
echo "  Results: ${OUTPUT_DIR}/benchmark_results.json"
echo "============================================================"
