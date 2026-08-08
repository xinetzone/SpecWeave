#!/usr/bin/env bash
# run-benchmark-docker.sh — Run ONNX quantization benchmark in isolated Docker container
#
# Usage:
#   bash scripts/run-benchmark-docker.sh [--cn] [--quick] [--threads N] [--output DIR]
#
# Options:
#   --cn         Use domestic (China) mirror for faster dependency resolution
#   --quick      Quick mode: warmup=10, runs=50, calib=20 (for fast validation)
#   --threads N  ORT intra-op threads (default: 4)
#   --output DIR Host directory to mount for results (default: ./benchmark-results)
#   --image TAG  Override Docker image (default: devcontainer-onnx-pytorch:latest)
#   --help       Show this help

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Defaults
USE_CN=0
QUICK_MODE=0
THREADS=4
OUTPUT_DIR="${SCRIPT_DIR}/../benchmark-results"
IMAGE_TAG="devcontainer-onnx-pytorch:latest"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --cn) USE_CN=1; shift ;;
        --quick) QUICK_MODE=1; shift ;;
        --threads) THREADS="$2"; shift 2 ;;
        --output) OUTPUT_DIR="$2"; shift 2 ;;
        --image) IMAGE_TAG="$2"; shift 2 ;;
        --help|-h)
            head -20 "$0" | grep '^#' | sed 's/^# \?//'
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo "============================================================"
echo "  ONNX Quantization Benchmark — Docker Runner"
echo "============================================================"
echo "  Image:     ${IMAGE_TAG}"
echo "  Threads:   ${THREADS}"
echo "  Quick mode: $([[ ${QUICK_MODE} -eq 1 ]] && echo 'YES' || echo 'NO')"
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
    echo "[INFO] Building onnx-pytorch variant..."

    BUILD_SCRIPT="${SCRIPT_DIR}/../variants/build.sh"
    if [[ ! -f "${BUILD_SCRIPT}" ]]; then
        echo "[ERROR] variants/build.sh not found. Please build the image first:"
        echo "  cd apps/devcontainer-base/variants && bash build.sh --variant onnx-pytorch $([[ ${USE_CN} -eq 1 ]] && echo '--cn')"
        exit 1
    fi

    BUILD_FLAGS="--variant onnx-pytorch"
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
fi
BENCH_ARGS="${BENCH_ARGS} --output /results/benchmark_results.json"

# Environment variables for OpenMP
ENV_VARS=(
    -e OMP_NUM_THREADS="${THREADS}"
    -e OPENBLAS_NUM_THREADS=1
    -e OMP_WAIT_POLICY=PASSIVE
    -e KMP_DUPLICATE_LIB_OK=TRUE
)

echo ""
echo "[INFO] Starting benchmark container..."
echo "[INFO] Benchmark args: ${BENCH_ARGS}"
echo ""

# Run the container
# Mount: scripts dir -> /benchmark, output dir -> /results
CONTAINER_NAME="onnx-bench-$(date +%Y%m%d-%H%M%S)"

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
        python /benchmark/benchmark_quantization.py -v ${BENCH_ARGS}
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
