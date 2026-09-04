#!/usr/bin/env python3
"""ResNet-50 & InceptionV1 Forward Benchmark — runs each config in a fresh subprocess
to ensure OMP/BLAS environment variables take effect correctly.
"""
import subprocess, sys, json, os, argparse, time
import numpy as np
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SRC_ROOT = SCRIPT_DIR.parent.parent.parent

def run_one(proto, model, omp_threads, blas_threads, warmup=3, iters=10, batch=1):
    """Run benchmark in a fresh subprocess to ensure env vars take effect."""
    code = f'''
import numpy as np, os, time, sys
os.environ["OMP_NUM_THREADS"] = "{omp_threads}"
os.environ["OPENBLAS_NUM_THREADS"] = "{blas_threads}"
os.environ["OMP_PROC_BIND"] = "close"
os.environ["OMP_PLACES"] = "cores"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["GLOG_minloglevel"] = "3"

import caffe_ffi

proto = "{proto}"
model = "{model}"
batch = {batch}

data = np.random.rand(batch, 3, 224, 224).astype(np.float32)
mean = np.array([103.939, 116.779, 123.68], dtype=np.float32).reshape(1,3,1,1)
mean = np.tile(mean, (batch,1,1,1))
data = (data - mean).astype(np.float32)

net = caffe_ffi.read_net(proto, model)
net.blob_by_name("data").reshape(batch, 3, 224, 224)
net.blob_by_name("data").data = data

# Warmup
for _ in range({warmup}):
    net.forward()

# Benchmark
latencies = []
for _ in range({iters}):
    t0 = time.perf_counter()
    out = net.forward()
    latencies.append((time.perf_counter() - t0) * 1000)

import json
result = {{
    "omp_threads": {omp_threads},
    "openblas_threads": {blas_threads},
    "batch": batch,
    "avg_latency_ms": float(np.mean(latencies)),
    "median_latency_ms": float(np.median(latencies)),
    "min_latency_ms": float(np.min(latencies)),
    "max_latency_ms": float(np.max(latencies)),
    "std_latency_ms": float(np.std(latencies)),
    "fps": float(1000.0 / np.mean(latencies)),
    "per_sample_ms": float(np.mean(latencies) / batch),
    "samples_per_sec": float(1000.0 * batch / np.mean(latencies)),
}}
print("RESULT_JSON:" + json.dumps(result))
'''
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=300,
        cwd=str(SRC_ROOT),
        env={**os.environ}
    )
    if result.returncode != 0:
        return {"omp_threads": omp_threads, "openblas_threads": blas_threads, "batch": batch,
                "error": result.stderr[-500:]}
    for line in result.stdout.split("\n"):
        if line.startswith("RESULT_JSON:"):
            return json.loads(line[len("RESULT_JSON:"):])
    return {"omp_threads": omp_threads, "openblas_threads": blas_threads, "batch": batch,
            "error": "No RESULT_JSON found", "stdout_tail": result.stdout[-500:]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proto", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--model-name", default="unknown")
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--iters", type=int, default=10)
    parser.add_argument("--threads", default="1,2,4,8")
    parser.add_argument("--blas-threads", default="1,4")
    parser.add_argument("--batches", default="1")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    threads = [int(x) for x in args.threads.split(",")]
    blas_threads_list = [int(x) for x in args.blas_threads.split(",")]
    batches = [int(x) for x in args.batches.split(",")]

    all_results = []
    print(f"\n{'='*70}")
    print(f"Model: {args.model_name}")
    print(f"Proto: {args.proto}")
    print(f"Model: {args.model}")
    print(f"Configs: OMP={threads}, BLAS={blas_threads_list}, batch={batches}")
    print(f"{'='*70}\n")

    for batch in batches:
        print(f"\n--- Batch size: {batch} ---")
        print(f"{'OMP':>4} {'BLAS':>4} {'Avg(ms)':>10} {'P50(ms)':>10} {'Min(ms)':>10} {'FPS':>8} {'Sample/s':>10} {'Speedup':>8}")
        print("-" * 70)
        baseline_fps = None
        for blas in blas_threads_list:
            for omp in threads:
                r = run_one(args.proto, args.model, omp, blas, args.warmup, args.iters, batch)
                all_results.append(r)
                if "error" in r:
                    print(f"{omp:>4} {blas:>4} ERROR: {r['error'][:80]}")
                    continue
                if baseline_fps is None:
                    baseline_fps = r["samples_per_sec"]
                speedup = r["samples_per_sec"] / baseline_fps
                print(f"{omp:>4} {blas:>4} {r['avg_latency_ms']:>10.1f} {r['median_latency_ms']:>10.1f} "
                      f"{r['min_latency_ms']:>10.1f} {r['fps']:>8.2f} {r['samples_per_sec']:>10.2f} {speedup:>7.2f}x")

    if args.output:
        os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"\nResults saved to: {args.output}")

    # Print best config
    valid = [r for r in all_results if "error" not in r]
    if valid:
        best = max(valid, key=lambda x: x["samples_per_sec"])
        worst = min(valid, key=lambda x: x["samples_per_sec"])
        print(f"\n{'='*70}")
        print(f"Best config: OMP={best['omp_threads']}, BLAS={best['openblas_threads']}, "
              f"batch={best['batch']}: {best['samples_per_sec']:.2f} samples/s "
              f"({best['per_sample_ms']:.1f}ms/sample)")
        print(f"Worst config: OMP={worst['omp_threads']}, BLAS={worst['openblas_threads']}, "
              f"batch={worst['batch']}: {worst['samples_per_sec']:.2f} samples/s "
              f"({worst['per_sample_ms']:.1f}ms/sample)")

if __name__ == "__main__":
    main()
