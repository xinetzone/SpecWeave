#!/usr/bin/env python3
"""Conv Layer v2 (output-channel parallelism) comprehensive benchmark.
Fixed: OMP=1 path now uses serial forward_cpu_gemm() outside parallel region
       so OpenBLAS can multi-thread GEMM calls.
"""
import os, sys, time, subprocess
import numpy as np

MODELS = {
    "InceptionV1": ("/root/.caffe_test_data/models/inceptionv1.prototxt",
                    "/root/.caffe_test_data/models/inceptionv1.caffemodel",
                    [104., 117., 123.]),
    "ResNet-50":   ("/root/.caffe_test_data/models/resnet50.prototxt",
                    "/root/.caffe_test_data/models/resnet50.caffemodel",
                    [103.939, 116.779, 123.68]),
}

# Configs: (omp_threads, blas_threads, batch)
configs = []
for batch in [1, 4]:
    for omp in [1, 2, 4]:
        for blas in [1, 4]:
            if omp > 1 and blas > 1:
                continue  # avoid double oversubscription
            configs.append((omp, blas, batch))

def run_one(proto, model, mean_vals, omp_t, blas_t, batch, warmup=5, iters=15):
    code = f'''
import os, time
os.environ["OMP_NUM_THREADS"] = "{omp_t}"
os.environ["OPENBLAS_NUM_THREADS"] = "{blas_t}"
os.environ["OMP_PROC_BIND"] = "close"
os.environ["OMP_PLACES"] = "cores"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["GLOG_minloglevel"] = "3"
import numpy as np, caffe_ffi
proto = "{proto}"
model = "{model}"
mean_vals = {mean_vals}
batch = {batch}
np.random.seed(42)
net = caffe_ffi.read_net(proto, model)
# Find input blob
input_blob = None
for bn in ["data"]:
    try:
        input_blob = net.blob_by_name(bn)
        break
    except: pass
data = np.random.rand(batch,3,224,224).astype(np.float32)
data -= np.array(mean_vals,dtype=np.float32).reshape(1,3,1,1)
input_blob.data = data
for _ in range({warmup}): net.forward()
lats = []
for _ in range({iters}):
    t0=time.perf_counter(); net.forward(); lats.append((time.perf_counter()-t0)*1000)
avg=np.mean(lats); med=np.median(lats); p95=np.percentile(lats,95)
ps=avg/batch; fps=1000.*batch/avg
print(f"RESULT avg={{avg:.1f}} med={{med:.1f}} p95={{p95:.1f}} ps={{ps:.1f}} fps={{fps:.2f}}")
'''
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=180, cwd="/root")
    for line in r.stdout.split("\n"):
        if line.startswith("RESULT "):
            parts = {}
            for tok in line[7:].split():
                k, v = tok.split("=")
                try:
                    parts[k] = float(v)
                except ValueError:
                    parts[k] = v
            return parts
    err = [l for l in r.stderr.split("\n") if "Error" in l or "Traceback" in l]
    if err:
        print(f"    ERROR: {err[-1][:150]}", file=sys.stderr)
    return None

for model_name, (proto, model, mean_vals) in MODELS.items():
    print(f"\n{'='*78}")
    print(f"  {model_name} (v2: output-channel parallelism + OMP=1 BLAS fix)")
    print(f"{'='*78}")
    print(f"{'Mode':>20} {'OMP':>4} {'BLAS':>4} {'Batch':>5} {'Avg(ms)':>8} {'P50(ms)':>8} {'P95(ms)':>8} {'Per-sample':>11} {'FPS':>8} {'Spd':>6}")
    print("-"*78)
    baseline_fps = None
    best_fps_b1 = 0
    best_cfg_b1 = None
    best_fps_b4 = 0
    best_cfg_b4 = None
    for omp_t, blas_t, batch in configs:
        mode = "Outer-OpenMP" if omp_t > 1 else ("BLAS-parallel" if blas_t > 1 else "Serial")
        r = run_one(proto, model, mean_vals, omp_t, blas_t, batch)
        if r:
            if baseline_fps is None and batch == 1 and omp_t == 1 and blas_t == 1:
                baseline_fps = r["fps"]
            spd = r["fps"] / baseline_fps if baseline_fps else 0
            print(f"{mode:>20} {omp_t:4d} {blas_t:4d} {batch:5d} {r['avg']:8.1f} {r['med']:8.1f} {r['p95']:8.1f} {r['ps']:10.1f}ms {r['fps']:8.2f} {spd:5.2f}x")
            if batch == 1 and r["fps"] > best_fps_b1:
                best_fps_b1 = r["fps"]; best_cfg_b1 = (mode, omp_t, blas_t)
            if batch == 4 and r["fps"] > best_fps_b4:
                best_fps_b4 = r["fps"]; best_cfg_b4 = (mode, omp_t, blas_t)
        else:
            print(f"{mode:>20} {omp_t:4d} {blas_t:4d} {batch:5d}    FAILED")
    print(f"\n  >>> Best batch=1: {best_cfg_b1[0]} OMP={best_cfg_b1[1]} BLAS={best_cfg_b1[2]} -> {best_fps_b1:.2f} FPS")
    print(f"  >>> Best batch=4: {best_cfg_b4[0]} OMP={best_cfg_b4[1]} BLAS={best_cfg_b4[2]} -> {best_fps_b4:.2f} FPS")
