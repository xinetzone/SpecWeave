#!/usr/bin/env python3
"""v3 Conv scaling test with min_chunk=16 fix."""
import os, sys, time, subprocess
import numpy as np

MODELS = {
    "ResNet-50":  ("/root/.caffe_test_data/models/resnet50.prototxt",
                   "/root/.caffe_test_data/models/resnet50.caffemodel",
                   [103.939, 116.779, 123.68]),
    "InceptionV1":("/root/.caffe_test_data/models/inceptionv1.prototxt",
                   "/root/.caffe_test_data/models/inceptionv1.caffemodel",
                   [104., 117., 123.]),
}

def run_one(proto, model, mean_vals, omp_t, blas_t=1, batch=1, warmup=8, iters=20):
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
input_blob = net.blob_by_name("data")
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
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=300, cwd="/root")
    for line in r.stdout.split("\n"):
        if line.startswith("RESULT "):
            parts = {}
            for tok in line[7:].split():
                k, v = tok.split("=")
                try: parts[k] = float(v)
                except: parts[k] = v
            return parts
    err = [l for l in r.stderr.split("\n") if "Error" in l or "Traceback" in l]
    if err:
        print(f"  ERR({omp_t}t): {err[-1][:200]}", file=sys.stderr)
    return None

for model_name, (proto, model, mean_vals) in MODELS.items():
    print(f"\n{'='*80}")
    print(f"  {model_name} v3 (min_chunk=16) batch=1 — BLAS=1, OMP_PROC_BIND=close")
    print(f"{'='*80}")
    print(f"{'Threads':>8} {'Avg(ms)':>8} {'P50(ms)':>8} {'P95(ms)':>8} {'Per-sample':>11} {'FPS':>8} {'Spdup':>7} {'Eff':>6}")
    print("-"*80)
    base_dt = None
    for threads in [1, 2, 4, 8, 16]:
        r = run_one(proto, model, mean_vals, threads, 1, batch=1)
        if r:
            if base_dt is None: base_dt = r["avg"]
            spd = base_dt / r["avg"]
            eff = spd / threads * 100
            print(f"{threads:8d} {r['avg']:8.1f} {r['med']:8.1f} {r['p95']:8.1f} {r['ps']:10.1f}ms {r['fps']:8.2f} {spd:6.2f}x {eff:5.1f}%")
        else:
            print(f"{threads:8d}    FAILED")

    print(f"\n  {model_name} v3 batch=4 — BLAS=1, OMP_PROC_BIND=close")
    print(f"{'Threads':>8} {'Total(ms)':>10} {'Per-sample':>11} {'FPS(total)':>11} {'Spdup':>7}")
    print("-"*80)
    base_ps = None
    for threads in [1, 2, 4, 8, 16]:
        r = run_one(proto, model, mean_vals, threads, 1, batch=4)
        if r:
            if base_ps is None: base_ps = r["ps"]
            spd = base_ps / r["ps"]
            fps_total = 1000.0*4/r["avg"]
            print(f"{threads:8d} {r['avg']:10.1f} {r['ps']:10.1f}ms {fps_total:11.2f} {spd:6.2f}x")
        else:
            print(f"{threads:8d}    FAILED")
