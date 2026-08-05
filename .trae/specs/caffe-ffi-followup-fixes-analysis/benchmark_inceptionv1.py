#!/usr/bin/env python3
"""InceptionV1 Forward performance benchmark for caffe-ffi with OpenMP.

Measures latency and FPS across different OMP_NUM_THREADS configurations
to demonstrate OpenMP parallelization speedup on Pooling/Eltwise layers.
"""
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['CAFFE_FFI_CPP_LOG_LEVEL'] = '3'  # ERROR only, suppress WARN/INFO

import sys
import time
import json
import numpy as np

import caffe_ffi

MODEL_DIR = "/SpecWeave/.trae/specs/caffe-comprehensive-comparison-test/test-assets/models"
PROTO = f"{MODEL_DIR}/inceptionv1.prototxt"
CAFFEMODEL = f"{MODEL_DIR}/inceptionv1.caffemodel"

WARMUP_ITERS = 5
BENCH_ITERS = 20
BATCH_SIZES = [1]
THREAD_CONFIGS = [1, 2, 4, 8, 16]

def bench_forward(net, data, n_iters):
    """Run forward n_iters times, return list of per-iter latencies in ms."""
    latencies = []
    for _ in range(n_iters):
        t0 = time.perf_counter()
        net.forward()
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000)
    return latencies

def main():
    print(f"caffe-ffi: {caffe_ffi.__version__}, native: {caffe_ffi.is_available()}")
    print(f"Model: InceptionV1 (GoogleNet)")
    print(f"Warmup: {WARMUP_ITERS} iters, Bench: {BENCH_ITERS} iters")
    print("=" * 70)

    results = []

    rng = np.random.default_rng(42)
    mean = np.array([123.68, 116.779, 103.939], dtype=np.float32).reshape(1, 3, 1, 1)

    for batch_size in BATCH_SIZES:
        for n_threads in THREAD_CONFIGS:
            os.environ['OMP_NUM_THREADS'] = str(n_threads)
            os.environ['MKL_NUM_THREADS'] = str(n_threads)
            
            # Reload net for each thread config to ensure thread count takes effect
            net = caffe_ffi.read_net(PROTO, CAFFEMODEL)
            
            data = rng.integers(0, 256, size=(batch_size, 3, 224, 224)).astype(np.float32)
            data_process = (data - mean) * (1.0 / 58.8)
            net.blob_by_name("data").data = data_process
            
            # Warmup
            for _ in range(WARMUP_ITERS):
                net.forward()
            
            # Benchmark
            latencies = bench_forward(net, data_process, BENCH_ITERS)
            
            lat_arr = np.array(latencies)
            avg_ms = lat_arr.mean()
            p50_ms = np.percentile(lat_arr, 50)
            p95_ms = np.percentile(lat_arr, 95)
            p99_ms = np.percentile(lat_arr, 99)
            min_ms = lat_arr.min()
            fps = (1000.0 / avg_ms) * batch_size
            
            result = {
                "batch_size": batch_size,
                "omp_threads": n_threads,
                "avg_ms": round(avg_ms, 2),
                "p50_ms": round(p50_ms, 2),
                "p95_ms": round(p95_ms, 2),
                "p99_ms": round(p99_ms, 2),
                "min_ms": round(min_ms, 2),
                "fps": round(fps, 2),
            }
            results.append(result)
            
            print(f"  batch={batch_size}  threads={n_threads:2d}  "
                  f"avg={avg_ms:7.2f}ms  p50={p50_ms:7.2f}ms  "
                  f"p95={p95_ms:7.2f}ms  FPS={fps:6.2f}")
    
    print("=" * 70)
    print("\n📊 Speedup Summary (relative to single-thread):")
    baseline_fps = results[0]["fps"]
    for r in results:
        speedup = r["fps"] / baseline_fps
        print(f"  threads={r['omp_threads']:2d}:  FPS={r['fps']:6.2f}  "
              f"speedup={speedup:.2f}x  avg_latency={r['avg_ms']:.2f}ms")
    
    # Save JSON report
    report = {
        "model": "InceptionV1 (GoogleNet)",
        "framework": "caffe-ffi",
        "native_ext": caffe_ffi.is_available(),
        "version": caffe_ffi.__version__,
        "warmup_iters": WARMUP_ITERS,
        "bench_iters": BENCH_ITERS,
        "input_shape": [1, 3, 224, 224],
        "results": results,
    }
    report_path = "/SpecWeave/.trae/specs/caffe-ffi-followup-fixes-analysis/benchmark_results.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Full report saved to: {report_path}")

if __name__ == "__main__":
    main()
