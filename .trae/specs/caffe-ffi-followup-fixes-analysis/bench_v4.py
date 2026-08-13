#!/usr/bin/env python3
"""v4 correctness + scaling benchmark."""
import os, sys, time, subprocess
import numpy as np

MODELS = {
    "ResNet-50":  ("/root/.caffe_test_data/models/resnet50.prototxt",
                   "/root/.caffe_test_data/models/resnet50.caffemodel",
                   [103.939, 116.779, 123.68], "prob"),
    "InceptionV1":("/root/.caffe_test_data/models/inceptionv1.prototxt",
                   "/root/.caffe_test_data/models/inceptionv1.caffemodel",
                   [104., 117., 123.], "prob"),
}

def run_bench(proto, model, mean_vals, out_name, omp_t, blas_t=1, batch=1, warmup=8, iters=20):
    env_vars = f"""
os.environ["OMP_NUM_THREADS"] = "{omp_t}"
os.environ["OPENBLAS_NUM_THREADS"] = "{blas_t}"
os.environ["OMP_WAIT_POLICY"] = "PASSIVE"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["GLOG_minloglevel"] = "3"
"""
    code = f'''
import os, time
{env_vars}
import numpy as np, caffe_ffi
proto = "{proto}"
model = "{model}"
mean_vals = {mean_vals}
out_name = "{out_name}"
batch = {batch}
np.random.seed(42)
net = caffe_ffi.read_net(proto, model)
input_blob = net.blob_by_name("data")
data = np.random.rand(batch,3,224,224).astype(np.float32)
data -= np.array(mean_vals,dtype=np.float32).reshape(1,3,1,1)
input_blob.data = data
for _ in range({warmup}): net.forward()
# Determine output blob
out = None
for name in ["prob", "fc1000", "loss3/classifier"]:
    try:
        out = net.blob_by_name(name); break
    except: pass
if out is None:
    # Use last blob
    blob_names = []
    for i in range(1000):
        try:
            b = net.blob_by_name(f"__blob_{{i}}")
            blob_names.append(b)
        except: break
    out = blob_names[-1] if blob_names else None
lats = []
for _ in range({iters}):
    t0=time.perf_counter(); net.forward(); lats.append((time.perf_counter()-t0)*1000)
avg=np.mean(lats); med=np.median(lats); p95=np.percentile(lats,95)
ps=avg/batch; fps=1000.*batch/avg
result = out.data.copy()
print(f"RESULT avg={{avg:.1f}} med={{med:.1f}} p95={{p95:.1f}} ps={{ps:.1f}} fps={{fps:.2f}}")
# Save output to temp for correctness check
np.save("/tmp/_bench_out.npy", result)
'''
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=300, cwd="/root")
    result_arr = None
    try:
        result_arr = np.load("/tmp/_bench_out.npy")
    except: pass
    for line in r.stdout.split("\n"):
        if line.startswith("RESULT "):
            parts = {}
            for tok in line[7:].split():
                k, v = tok.split("=")
                try: parts[k] = float(v)
                except: parts[k] = v
            return parts, result_arr
    err = [l for l in r.stderr.split("\n") if "Error" in l or "Traceback" in l]
    if err:
        return {"error": err[-1][:200]}, None
    return None, None

# ── Correctness check ──
print("=== Correctness Check: OMP=1 vs OMP=4 ===")
for mn, (proto, model, mv, on) in MODELS.items():
    r1, a1 = run_bench(proto, model, mv, on, 1, 1, batch=1, warmup=3, iters=5)
    r4, a4 = run_bench(proto, model, mv, on, 4, 1, batch=1, warmup=3, iters=5)
    if a1 is not None and a4 is not None:
        diff = np.max(np.abs(a1 - a4))
        rel = np.max(np.abs(a1 - a4) / (np.abs(a1) + 1e-10))
        print(f"  {mn}: max_abs_diff={diff:.2e} max_rel_diff={rel:.2e} {'✓' if diff < 1e-5 else '✗'}")
    else:
        print(f"  {mn}: FAILED to collect outputs")

# ── Scaling test ──
for batch in [1, 4]:
    for model_name, (proto, model, mean_vals, on) in MODELS.items():
        print(f"\n{'='*80}")
        print(f"  {model_name} v4 batch={batch} — BLAS=1, OMP_WAIT_POLICY=PASSIVE, no bind")
        print(f"{'='*80}")
        print(f"{'Threads':>8} {'Avg(ms)':>8} {'P50(ms)':>8} {'P95(ms)':>8} {'Per-sample':>11} {'FPS':>8} {'Spdup':>7} {'Eff':>6}")
        print("-"*80)
        base_ps = None
        for threads in [1, 2, 4, 8, 16]:
            r, _ = run_bench(proto, model, mean_vals, on, threads, 1, batch=batch)
            if r and "error" not in r:
                if base_ps is None: base_ps = r["ps"]
                spd = base_ps / r["ps"]
                eff = spd / threads * 100
                print(f"{threads:8d} {r['avg']:8.1f} {r['med']:8.1f} {r['p95']:8.1f} {r['ps']:10.1f}ms {r['fps']:8.2f} {spd:6.2f}x {eff:5.1f}%")
            else:
                err = r.get("error", "unknown") if r else "no result"
                print(f"{threads:8d}    FAIL: {err[:60]}")
