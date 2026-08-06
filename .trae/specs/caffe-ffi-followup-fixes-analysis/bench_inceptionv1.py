#!/usr/bin/env python3
"""InceptionV1 Forward Performance Benchmark for caffe-ffi.

Runs InceptionV1 (GoogLeNet) forward pass multiple times with configurable
OpenMP/OpenBLAS thread counts and reports latency/FPS.

Usage:
  python bench_inceptionv1.py [--warmup N] [--iters N] [--proto FILE] [--model FILE]
                              [--output FILE] [--threads LIST]
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np


def _add_project_paths():
    """Ensure caffe_ffi can be imported from the editable install location."""
    # bench_inceptionv1.py is at: <repo>/.trae/specs/caffe-ffi-followup-fixes-analysis/bench_inceptionv1.py
    # So 4 parents up from this file = repo root.
    _src_root = Path(__file__).resolve().parent.parent.parent.parent
    _py_dir = _src_root / "projects" / "xuanspace" / "libs" / "caffe-ffi" / "python"
    if _py_dir.is_dir() and str(_py_dir) not in sys.path:
        sys.path.insert(0, str(_py_dir))


def run_benchmark(proto_file, blob_file, num_warmup=3, num_iters=10,
                  omp_threads=1, openblas_threads=1):
    """Run InceptionV1 forward benchmark.

    Returns dict with latency stats and FPS.
    """
    os.environ["OMP_NUM_THREADS"] = str(omp_threads)
    os.environ["OPENBLAS_NUM_THREADS"] = str(openblas_threads)
    os.environ["OMP_PROC_BIND"] = "close"
    os.environ["OMP_PLACES"] = "cores"
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    os.environ["GLOG_minloglevel"] = "2"

    import caffe_ffi
    if not caffe_ffi.is_available():
        return {"error": "caffe_ffi C++ extension not available"}

    # Create random input (1, 3, 224, 224)
    data = np.random.randint(0, 256, size=(1, 3, 224, 224)).astype(np.float32)
    # ImageNet mean subtraction (BGR)
    mean = np.array([103.939, 116.779, 123.68], dtype=np.float32).reshape(1, 3, 1, 1)
    mean = np.tile(mean, (1, 1, 224, 224))
    data_process = (data - mean) / 58.8
    data_process = data_process.astype(np.float32)

    # Load network
    net = caffe_ffi.read_net(str(proto_file), str(blob_file))
    net.blob_by_name("data").data = data_process

    # Warmup
    for _ in range(num_warmup):
        out = net.forward()

    # Timed iterations
    latencies = []
    for _ in range(num_iters):
        t0 = time.perf_counter()
        out = net.forward()
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000.0)  # ms

    latencies = np.array(latencies)
    avg_lat = np.mean(latencies)
    std_lat = np.std(latencies)
    min_lat = np.min(latencies)
    max_lat = np.max(latencies)
    median_lat = np.median(latencies)
    fps = 1000.0 / avg_lat

    # Get output stats
    out_vals = list(out.values())
    out_min = float(np.min([np.min(v) for v in out_vals]))
    out_max = float(np.max([np.max(v) for v in out_vals]))

    return {
        "omp_threads": omp_threads,
        "openblas_threads": openblas_threads,
        "num_iters": num_iters,
        "num_warmup": num_warmup,
        "avg_latency_ms": round(avg_lat, 2),
        "std_latency_ms": round(std_lat, 2),
        "min_latency_ms": round(min_lat, 2),
        "max_latency_ms": round(max_lat, 2),
        "median_latency_ms": round(median_lat, 2),
        "fps": round(fps, 4),
        "out_min": round(out_min, 6),
        "out_max": round(out_max, 6),
        "latencies_ms": [round(x, 2) for x in latencies.tolist()],
    }


def main():
    parser = argparse.ArgumentParser(description="InceptionV1 Forward Benchmark")
    parser.add_argument("--proto", type=str, default=None,
                        help="Path to deploy.prototxt")
    parser.add_argument("--model", type=str, default=None,
                        help="Path to .caffemodel")
    parser.add_argument("--warmup", type=int, default=3,
                        help="Number of warmup iterations")
    parser.add_argument("--iters", type=int, default=10,
                        help="Number of timed iterations")
    parser.add_argument("--threads", type=str, default="1,2,4,8",
                        help="Comma-separated OMP thread counts to test")
    parser.add_argument("--blas-threads", type=int, default=1,
                        help="OpenBLAS thread count (1=single-threaded BLAS)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output JSON file for results")
    args = parser.parse_args()

    _add_project_paths()

    # Find model files if not specified
    if args.proto is None or args.model is None:
        # Search common locations
        search_dirs = [
            Path("/workspace"),
            Path("/root/.cache"),
            Path("/SpecWeave/playground/caffemodel-conversion/output"),
            Path("/SpecWeave/.trae/specs/caffe-ffi-followup-fixes-analysis/converted_models"),
            Path.home() / ".cache" / "caffe_ffi",
        ]
        for d in search_dirs:
            if d.is_dir():
                if args.proto is None:
                    proto_candidates = list(d.rglob("*deploy.prototxt")) + list(d.rglob("inceptionv1.prototxt"))
                    if proto_candidates:
                        args.proto = str(proto_candidates[0])
                if args.model is None:
                    model_candidates = (list(d.rglob("*googlenet*.caffemodel")) +
                                       list(d.rglob("*inceptionv1*.caffemodel")))
                    if model_candidates:
                        args.model = str(model_candidates[0])

    if args.proto is None or args.model is None:
        print("ERROR: Could not find prototxt or caffemodel. "
              "Please specify --proto and --model.")
        print(f"  proto: {args.proto}")
        print(f"  model: {args.model}")
        sys.exit(1)

    print(f"Proto: {args.proto}")
    print(f"Model: {args.model}")
    print(f"Warmup: {args.warmup}, Iters: {args.iters}")
    print(f"BLAS threads: {args.blas_threads}")
    print()

    thread_list = [int(t.strip()) for t in args.threads.split(",")]
    results = []

    for nthreads in thread_list:
        print(f"--- Testing with OMP_NUM_THREADS={nthreads}, "
              f"OPENBLAS_NUM_THREADS={args.blas_threads} ---")
        result = run_benchmark(
            args.proto, args.model,
            num_warmup=args.warmup, num_iters=args.iters,
            omp_threads=nthreads, openblas_threads=args.blas_threads,
        )
        if "error" in result:
            print(f"  ERROR: {result['error']}")
            results.append(result)
            continue
        print(f"  Avg latency: {result['avg_latency_ms']} ms (±{result['std_latency_ms']} ms)")
        print(f"  Median:      {result['median_latency_ms']} ms")
        print(f"  Min/Max:     {result['min_latency_ms']} / {result['max_latency_ms']} ms")
        print(f"  FPS:         {result['fps']}")
        print(f"  Output range:[{result['out_min']}, {result['out_max']}]")
        print()
        results.append(result)

    # Print comparison table
    print("=" * 80)
    print("SUMMARY: InceptionV1 Forward Performance")
    print("=" * 80)
    print(f"{'OMP_THREADS':<12} {'BLAS_THREADS':<13} {'AVG_LAT(ms)':<12} "
          f"{'MEDIAN(ms)':<12} {'MIN(ms)':<10} {'FPS':<10} {'SPEEDUP':<10}")
    print("-" * 80)

    baseline_fps = None
    for r in results:
        if "error" in r:
            continue
        if baseline_fps is None:
            baseline_fps = r["fps"]
        speedup = r["fps"] / baseline_fps if baseline_fps else 0
        print(f"{r['omp_threads']:<12} {r['openblas_threads']:<13} "
              f"{r['avg_latency_ms']:<12} {r['median_latency_ms']:<12} "
              f"{r['min_latency_ms']:<10} {r['fps']:<10} {speedup:<10.2f}x")
    print("=" * 80)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()
