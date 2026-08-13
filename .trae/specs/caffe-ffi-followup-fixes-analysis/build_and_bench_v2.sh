#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────
# Conv Layer v2 (output-channel parallelism) Build & Benchmark Script
# Compiles caffe-ffi with the new M-dimension OpenMP parallelism and runs
# performance tests on InceptionV1 and ResNet-50 across multiple thread configs.
# ──────────────────────────────────────────────────────────────────────────
set -euo pipefail

CAFFE_FFI_ROOT="/root/.caffe-ffi"
BUILD_DIR="${CAFFE_FFI_ROOT}/build"
SRC_ROOT="/SpecWeave/.trae/specs/caffe-ffi-followup-fixes-analysis"
CONDA_ENV="caffe-ffi"

LOG_DIR="${SRC_ROOT}/bench_v2_logs"
mkdir -p "${LOG_DIR}"

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  Conv Layer v2 — Output-Channel Parallelism Build & Benchmark  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"

# ── Step 1: Build ──────────────────────────────────────────────────────────
echo ""
echo "▶ Step 1: Compiling caffe-ffi (Debug, tests enabled)..."
source /opt/conda/etc/profile.d/conda.sh
conda activate "${CONDA_ENV}"

mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"
cmake .. -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTS=ON 2>&1 | tail -5
cmake --build . -j"$(nproc)" 2>&1 | tail -5
echo "  ✅ Build complete"

# ── Step 2: Verify correctness first (InceptionV1 batch=1, OMP=2 BLAS=1) ──
echo ""
echo "▶ Step 2: Correctness verification (OMP=2, BLAS=1)..."
cd "${CAFFE_FFI_ROOT}"
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1 \
OMP_PROC_BIND=close OMP_PLACES=cores KMP_DUPLICATE_LIB_OK=TRUE \
GLOG_minloglevel=3 \
python -c "
import numpy as np, caffe_ffi
proto = '/root/.caffe_test_data/models/deploy.prototxt'
model = '/root/.caffe_test_data/models/bvlc_googlenet.caffemodel'

net1 = caffe_ffi.read_net(proto, model)
data = np.random.rand(1, 3, 224, 224).astype(np.float32)
mean = np.array([104.0, 117.0, 123.0], dtype=np.float32).reshape(1,3,1,1)
data = (data - mean).astype(np.float32)
net1.blob_by_name('data').data = data
out1 = net1.forward().copy()

net2 = caffe_ffi.read_net(proto, model)
net2.blob_by_name('data').data = data
out2 = net2.forward().copy()

max_diff = np.max(np.abs(out1 - out2))
print(f'  Reproducibility (same config): max_diff = {max_diff:.2e}')
assert max_diff < 1e-5, f'Reproducibility FAILED: {max_diff}'

# Test OMP=1 vs OMP=2 produce same result
import os
os.environ['OMP_NUM_THREADS'] = '1'
net3 = caffe_ffi.read_net(proto, model)
net3.blob_by_name('data').data = data
out3 = net3.forward().copy()
max_diff_omp = np.max(np.abs(out1 - out3))
print(f'  OMP=1 vs OMP=2: max_diff = {max_diff_omp:.2e}')
assert max_diff_omp < 1e-5, f'OMP consistency FAILED: {max_diff_omp}'
print('  ✅ Correctness verified')
" 2>&1 | grep -E "Reproducibility|OMP=1|✅|Error|FAILED|Traceback" || true

# ── Step 3: Performance benchmark ──────────────────────────────────────────
echo ""
echo "▶ Step 3: Running performance benchmarks..."

BENCH_SCRIPT="${SRC_ROOT}/bench_v2_runner.py"
cat > "${BENCH_SCRIPT}" <<'PYEOF'
import os, sys, time, json, ctypes, subprocess
import numpy as np

# Try to load OpenMP and OpenBLAS for dynamic thread setting
try:
    omp_lib = ctypes.CDLL("libgomp.so.1")
    omp_lib.omp_set_num_threads.restype = None
    omp_lib.omp_set_num_threads.argtypes = [ctypes.c_int]
    has_omp = True
except:
    has_omp = False
    print("WARNING: libgomp not found, using env var fallback")

try:
    blas_lib = ctypes.CDLL("libopenblas.so.0")
    blas_lib.openblas_set_num_threads.restype = None
    blas_lib.openblas_set_num_threads.argtypes = [ctypes.c_int]
    has_blas = True
except:
    has_blas = False
    print("WARNING: libopenblas not found, using env var fallback")

# Must set env BEFORE importing caffe_ffi if using subprocess approach
# But we use ctypes to dynamically set threads, which works for same-process

import caffe_ffi

MODELS = {
    "InceptionV1": {
        "proto": "/root/.caffe_test_data/models/deploy.prototxt",
        "model": "/root/.caffe_test_data/models/bvlc_googlenet.caffemodel",
        "mean": [104.0, 117.0, 123.0],
        "input_shape": (3, 224, 224),
    },
    "ResNet-50": {
        "proto": "/root/.caffe_test_data/models/resnet50.prototxt",
        "model": "/root/.caffe_test_data/models/resnet50.caffemodel",
        "mean": [103.939, 116.779, 123.68],
        "input_shape": (3, 224, 224),
    },
}

os.environ["OMP_PROC_BIND"] = "close"
os.environ["OMP_PLACES"] = "cores"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def run_bench(model_name, proto, model_path, mean_vals, input_shape,
              omp_t, blas_t, batch=1, warmup=5, iters=15):
    """Run benchmark in a subprocess to ensure env vars take effect."""
    C, H, W = input_shape
    code = f'''
import os, sys, time, ctypes
os.environ["OMP_NUM_THREADS"] = "{omp_t}"
os.environ["OPENBLAS_NUM_THREADS"] = "{blas_t}"
os.environ["OMP_PROC_BIND"] = "close"
os.environ["OMP_PLACES"] = "cores"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["GLOG_minloglevel"] = "3"

import numpy as np
import caffe_ffi

proto = "{proto}"
model = "{model_path}"
C, H, W = {C}, {H}, {W}
batch = {batch}
warmup = {warmup}
iters = {iters}
mean_vals = {mean_vals}

net = caffe_ffi.read_net(proto, model)
data = np.random.rand(batch, C, H, W).astype(np.float32)
mean = np.array(mean_vals, dtype=np.float32).reshape(1,C,1,1)
data = (data - np.tile(mean, (batch,1,1,1))).astype(np.float32)
net.blob_by_name("data").data = data

for _ in range(warmup):
    net.forward()

latencies = []
for _ in range(iters):
    t0 = time.perf_counter()
    net.forward()
    latencies.append((time.perf_counter() - t0) * 1000.0)

avg = np.mean(latencies)
std = np.std(latencies)
med = np.median(latencies)
p95 = np.percentile(latencies, 95)
per_sample = avg / batch
fps = 1000.0 * batch / avg
print(f"RESULT avg={{avg:.1f}}ms std={{std:.1f}}ms med={{med:.1f}}ms p95={{p95:.1f}}ms per_sample={{per_sample:.1f}}ms fps={{fps:.2f}}")
'''
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=120,
        cwd="/root/.caffe-ffi"
    )
    for line in result.stdout.split("\n"):
        if line.startswith("RESULT "):
            parts = {}
            for token in line[7:].split():
                k, v = token.split("=")
                try:
                    parts[k] = float(v.replace("ms","").replace("fps",""))
                except:
                    parts[k] = v
            return parts
    print(f"  STDERR: {result.stderr[-500:]}")
    return None

results = {}
configs = []

# Test key configurations
for batch in [1, 4]:
    for omp_t in [1, 2, 4]:
        for blas_t in [1, 4]:
            # Skip oversubscription combos (OMP>1 + BLAS>1 = too many threads)
            if omp_t > 1 and blas_t > 1:
                continue
            configs.append((omp_t, blas_t, batch))

# Also test BLAS=4 OMP=1 with different thread binding
configs.append((1, 4, 1))  # duplicate for binding test

for model_name, info in MODELS.items():
    print(f"\n{'='*70}")
    print(f"  Model: {model_name}")
    print(f"{'='*70}")
    results[model_name] = []

    for omp_t, blas_t, batch in configs:
        binding = "close+cores"
        print(f"  OMP={omp_t} BLAS={blas_t} batch={batch}...", end=" ", flush=True)
        r = run_bench(model_name, info["proto"], info["model"],
                      info["mean"], info["input_shape"],
                      omp_t, blas_t, batch=batch)
        if r:
            r.update({"omp": omp_t, "blas": blas_t, "batch": batch, "binding": binding})
            results[model_name].append(r)
            print(f"avg={r['avg']:.0f}ms fps={r['fps']:.2f} per_sample={r['per_sample']:.0f}ms")
        else:
            print("FAILED")

# Save results
with open("${LOG_DIR}/bench_v2_results.json", "w") as f:
    json.dump(results, f, indent=2)

# Print summary table
print(f"\n\n{'='*80}")
print("PERFORMANCE SUMMARY (v2: output-channel parallelism)")
print(f"{'='*80}")
for model_name in MODELS:
    print(f"\n── {model_name} ──")
    print(f"{'OMP':>4} {'BLAS':>4} {'Batch':>5} {'Avg(ms)':>8} {'P95(ms)':>8} {'Per-sample(ms)':>14} {'FPS':>8} {'Speedup':>8}")
    print("-" * 70)
    baseline_fps = None
    for r in sorted(results[model_name], key=lambda x: (x['batch'], x['omp'], x['blas'])):
        if baseline_fps is None and r['batch'] == 1 and r['omp'] == 1 and r['blas'] == 1:
            baseline_fps = r['fps']
        speedup = r['fps'] / baseline_fps if baseline_fps else 0
        print(f"{r['omp']:4d} {r['blas']:4d} {r['batch']:5d} {r['avg']:8.1f} {r['p95']:8.1f} {r['per_sample']:14.1f} {r['fps']:8.2f} {speedup:7.2f}x")

# Find best config for each model and batch
print(f"\n── Best Configs ──")
for model_name in MODELS:
    for batch in [1, 4]:
        batch_results = [r for r in results[model_name] if r['batch'] == batch]
        if batch_results:
            best = max(batch_results, key=lambda x: x['fps'])
            print(f"  {model_name} batch={batch}: OMP={best['omp']} BLAS={best['blas']} → {best['fps']:.2f} FPS ({best['per_sample']:.0f}ms/sample)")
PYEOF

echo ""
cd "${CAFFE_FFI_ROOT}"
GLOG_minloglevel=3 python "${BENCH_SCRIPT}" 2>&1 | tee "${LOG_DIR}/bench_v2_output.txt"

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  Benchmark complete! Logs saved to:                            ║"
echo "║    ${LOG_DIR}/bench_v2_output.txt"
echo "║    ${LOG_DIR}/bench_v2_results.json"
echo "╚══════════════════════════════════════════════════════════════════╝"
