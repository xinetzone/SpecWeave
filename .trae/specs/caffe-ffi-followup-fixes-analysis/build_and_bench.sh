#!/bin/bash
# =============================================================================
# Conv Layer OpenMP Parallelization — One-Click Build & Benchmark Script
# =============================================================================
# This script:
#   1. Sets optimal OpenMP/OpenBLAS environment variables
#   2. Cleans old build artifacts and recompiles caffe-ffi with OpenMP enabled
#   3. Runs InceptionV1 forward benchmarks at multiple thread counts
#   4. Compares results against baseline (1-thread serial BLAS)
#   5. Saves results to a JSON + Markdown report
#
# Usage:
#   docker exec -it caffe-ffi-jupyter bash /SpecWeave/.trae/specs/caffe-ffi-followup-fixes-analysis/build_and_bench.sh
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_ROOT="${SCRIPT_DIR}/../../.."
CAFFE_FFI_SRC="${SRC_ROOT}/projects/xuanspace/libs/caffe-ffi"
CAFFE_FFI_CMAKE_ARGS="-DCAFFE_USE_OPENMP=ON"
CONDA_ENV="caffe-ffi"
BENCH_SCRIPT="${SCRIPT_DIR}/bench_inceptionv1.py"
REPORT_DIR="${SCRIPT_DIR}/benchmark_results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Model paths (pre-cached in container)
PROTO_FILE="/root/.caffe_test_data/models/inceptionv1.prototxt"
MODEL_FILE="/root/.caffe_test_data/models/inceptionv1.caffemodel"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
log_info()  { echo -e "${GREEN}[BUILD&BENCH]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[BUILD&BENCH]${NC} $*"; }
log_error() { echo -e "${RED}[BUILD&BENCH]${NC} $*" >&2; }
log_step()  { echo -e "${CYAN}[BUILD&BENCH]${NC} $*"; }
log_hdr()   { echo -e "\n${BOLD}${CYAN}━━━ $* ━━━${NC}\n"; }

# ── Activate conda ──
log_step "Activating conda environment: ${CONDA_ENV}"
source /opt/conda/etc/profile.d/conda.sh
conda activate "${CONDA_ENV}"
log_info "Python: $(python --version)"

# ── Fix OpenBLAS symlink ──
if [ -d "$CONDA_PREFIX/lib" ] && [ ! -f "$CONDA_PREFIX/lib/libopenblas.so" ] && [ -f "$CONDA_PREFIX/lib/libopenblas.so.0" ]; then
    ln -sf libopenblas.so.0 "$CONDA_PREFIX/lib/libopenblas.so"
    log_info "Created libopenblas.so symlink"
fi

# ── Set environment variables for build & runtime ──
export KMP_DUPLICATE_LIB_OK=TRUE
export OMP_PROC_BIND=close
export OMP_PLACES=cores

log_hdr "Step 1: Clean build directory"
cd "${CAFFE_FFI_SRC}"
rm -rf build/
log_info "Build directory cleaned"

log_hdr "Step 2: Rebuild caffe-ffi with OpenMP + BLAS single-threaded"
log_info "CMake args: ${CAFFE_FFI_CMAKE_ARGS}"
log_info "OPENBLAS_NUM_THREADS=1 (prevent nested parallelism)"

# Force rebuild by removing old .so
find python/caffe_ffi -name "_caffe_ffi*.so" -delete 2>/dev/null || true

SKBUILD_CMAKE_ARGS="${CAFFE_FFI_CMAKE_ARGS}" pip install --no-cache-dir --no-build-isolation -e . 2>&1 | tail -20
PIP_STATUS=$?

if [ $PIP_STATUS -ne 0 ]; then
    log_warn "First build attempt failed, retrying after deeper clean..."
    rm -rf build/ _skbuild/
    SKBUILD_CMAKE_ARGS="${CAFFE_FFI_CMAKE_ARGS}" pip install --no-cache-dir --no-build-isolation -e . 2>&1 | tail -20
    PIP_STATUS=$?
fi

if [ $PIP_STATUS -ne 0 ]; then
    log_error "Build failed after retry. Check compiler output above."
    exit 1
fi

# ── Verify build ──
log_hdr "Step 3: Verify build"
python -c "
import caffe_ffi
import os
so = os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi.so')
print(f'  caffe_ffi version: {caffe_ffi.__version__}')
print(f'  .so location: {so}')
print(f'  .so exists: {os.path.exists(so)}')
print(f'  caffe_ffi available: {caffe_ffi.is_available()}')
"
# Verify OpenMP symbols in the .so
_SO=$(python -c "import caffe_ffi, os; print(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi.so'))")
if ldd "$_SO" | grep -q libgomp; then
    log_info "✅ OpenMP runtime (libgomp) linked: $(ldd $_SO | grep libgomp | awk '{print $3}')"
else
    log_warn "⚠️  libgomp not found in ldd output (may be statically linked or via another lib)"
fi
if ldd "$_SO" | grep -q libopenblas; then
    log_info "✅ OpenBLAS linked: $(ldd $_SO | grep libopenblas | awk '{print $3}')"
else
    log_warn "⚠️  OpenBLAS not found in direct ldd output (may be loaded dynamically)"
fi

# ── Check model files ──
log_hdr "Step 4: Check model files"
if [ ! -f "$PROTO_FILE" ]; then
    log_error "Prototxt not found: $PROTO_FILE"
    exit 1
fi
if [ ! -f "$MODEL_FILE" ]; then
    log_error "Caffemodel not found: $MODEL_FILE"
    exit 1
fi
MODEL_SIZE=$(du -h "$MODEL_FILE" | cut -f1)
log_info "Proto: $PROTO_FILE"
log_info "Model: $MODEL_FILE ($MODEL_SIZE)"

# ── Ensure OpenBLAS is single-threaded for benchmarks ──
export OPENBLAS_NUM_THREADS=1

# ── Run benchmarks ──
log_hdr "Step 5: Run InceptionV1 Forward Benchmarks"
mkdir -p "${REPORT_DIR}"

# Phase A: BLAS=1 (single-threaded BLAS) — optimal for Conv-OpenMP parallelism
log_step "Phase A: OPENBLAS_NUM_THREADS=1, varying OMP_NUM_THREADS"
RESULT_A="${REPORT_DIR}/bench_phaseA_${TIMESTAMP}.json"
python "${BENCH_SCRIPT}" \
    --proto "$PROTO_FILE" \
    --model "$MODEL_FILE" \
    --warmup 3 \
    --iters 10 \
    --threads "1,2,4,8" \
    --blas-threads 1 \
    --output "$RESULT_A" 2>&1 | tee "${REPORT_DIR}/bench_phaseA_${TIMESTAMP}.log"
RESULT_A_EXIT=$?

# Phase B: BLAS multi-threaded (traditional) for comparison
log_step "Phase B: OPENBLAS_NUM_THREADS=4 (multi-threaded BLAS), no Conv-OpenMP benefit expected"
RESULT_B="${REPORT_DIR}/bench_phaseB_${TIMESTAMP}.json"
python "${BENCH_SCRIPT}" \
    --proto "$PROTO_FILE" \
    --model "$MODEL_FILE" \
    --warmup 3 \
    --iters 10 \
    --threads "1,2" \
    --blas-threads 4 \
    --output "$RESULT_B" 2>&1 | tee "${REPORT_DIR}/bench_phaseB_${TIMESTAMP}.log"
RESULT_B_EXIT=$?

# ── Generate Markdown report ──
log_hdr "Step 6: Generate Markdown Report"
REPORT_MD="${REPORT_DIR}/benchmark_report_${TIMESTAMP}.md"

python - <<PYEOF
import json, os, glob
from datetime import datetime

report_dir = "${REPORT_DIR}"
ts = "${TIMESTAMP}"

# Load results
results = {}
for phase in ["A", "B"]:
    pattern = os.path.join(report_dir, f"bench_phase{phase}_{ts}.json")
    files = glob.glob(pattern)
    if files:
        with open(files[0]) as f:
            results[phase] = json.load(f)

blas_desc = {"A": "BLAS=1 (single-threaded, Conv-OpenMP parallel)", "B": "BLAS=4 (multi-threaded BLAS)"}

md = []
md.append(f"# InceptionV1 Forward Performance Report")
md.append(f"")
md.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
md.append(f"**Build**: Conv layer OpenMP batch-parallelization (`forward_cpu_gemm_ext`)")
md.append(f"**Model**: InceptionV1 (GoogLeNet), input 1×3×224×224")
md.append(f"")

for phase, data in results.items():
    md.append(f"## Phase {phase}: {blas_desc.get(phase, phase)}")
    md.append(f"")
    md.append(f"| OMP_THREADS | BLAS_THREADS | AVG_LAT(ms) | MEDIAN(ms) | MIN(ms) | MAX(ms) | FPS | Speedup |")
    md.append(f"|-------------|--------------|-------------|------------|---------|---------|-----|---------|")
    baseline_fps = None
    for r in data:
        if "error" in r:
            md.append(f"| {r['omp_threads']} | {r['openblas_threads']} | ERROR: {r['error']} | | | | | |")
            continue
        if baseline_fps is None:
            baseline_fps = r["fps"]
        speedup = r["fps"] / baseline_fps if baseline_fps else 0
        md.append(f"| {r['omp_threads']} | {r['openblas_threads']} | {r['avg_latency_ms']} | "
                  f"{r['median_latency_ms']} | {r['min_latency_ms']} | {r['max_latency_ms']} | "
                  f"{r['fps']} | {speedup:.2f}x |")
    md.append(f"")

# Cross-phase comparison
if "A" in results and "B" in results and results["A"] and results["B"]:
    best_a = max((r for r in results["A"] if "error" not in r), key=lambda x: x["fps"], default=None)
    best_b = max((r for r in results["B"] if "error" not in r), key=lambda x: x["fps"], default=None)
    baseline_1t = next((r for r in results["A"] if r.get("omp_threads") == 1 and "error" not in r), None)
    if best_a and best_b and baseline_1t:
        md.append(f"## Cross-Phase Comparison")
        md.append(f"")
        md.append(f"| Configuration | Threads | Avg Latency | FPS | vs 1-thread |")
        md.append(f"|---------------|---------|-------------|-----|-------------|")
        md.append(f"| Baseline (OMP=1, BLAS=1) | 1 | {baseline_1t['avg_latency_ms']} ms | {baseline_1t['fps']} | 1.00x |")
        if best_b:
            md.append(f"| Multi-threaded BLAS=4 | 1+4 | {best_b['avg_latency_ms']} ms | {best_b['fps']} | {best_b['fps']/baseline_1t['fps']:.2f}x |")
        if best_a:
            md.append(f"| **Conv-OpenMP (OMP={best_a['omp_threads']}, BLAS=1)** | **{best_a['omp_threads']}** | **{best_a['avg_latency_ms']} ms** | **{best_a['fps']}** | **{best_a['fps']/baseline_1t['fps']:.2f}x** |")
        md.append(f"")
        if best_a and best_b:
            if best_a["fps"] > best_b["fps"]:
                md.append(f"✅ **Conv-OpenMP is faster**: {best_a['fps']/best_b['fps']:.2f}x vs multi-threaded BLAS")
            else:
                md.append(f"⚠️ Multi-threaded BLAS is currently faster: {best_b['fps']/best_a['fps']:.2f}x vs Conv-OpenMP")
        md.append(f"")

md.append(f"## Environment")
md.append(f"")
md.append(f"- CPU: Intel Core Ultra 9 285H (Arrow Lake-H)")
md.append(f"- Container: caffe-ffi-jupyter")
md.append(f"- OMP_PROC_BIND=close, OMP_PLACES=cores")
md.append(f"- OpenBLAS: single-threaded (Phase A) vs 4-threaded (Phase B)")
md.append(f"")

with open("${REPORT_MD}", "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print(f"Report saved to: ${REPORT_MD}")
PYEOF

log_hdr "Build & Benchmark Complete!"
log_info "Results directory: ${REPORT_DIR}"
log_info "JSON results: ${RESULT_A}"
log_info "Markdown report: ${REPORT_MD}"
echo ""
echo "To view the report:"
echo "  cat ${REPORT_MD}"
echo ""
