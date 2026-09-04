#!/usr/bin/env python3
"""Quick correctness + perf test for v2 Conv with OMP=1/BLAS fix."""
import os, sys, time, subprocess
import numpy as np

# Generate deterministic test data once (run inside container, so /tmp is container's /tmp)
np.random.seed(42)
data = np.random.rand(1,3,224,224).astype(np.float32)
data -= np.array([103.939,116.779,123.68],dtype=np.float32).reshape(1,3,1,1)
np.save("/tmp/_test_data.npy", data)

proto_rn50 = "/root/.caffe_test_data/models/resnet50.prototxt"
model_rn50 = "/root/.caffe_test_data/models/resnet50.caffemodel"
proto_inc  = "/root/.caffe_test_data/models/inceptionv1.prototxt"
model_inc  = "/root/.caffe_test_data/models/inceptionv1.caffemodel"
mean_rn50  = [103.939,116.779,123.68]
mean_inc   = [104.,117.,123.]

def run_cfg(proto, model, mean_vals, batch, omp_t, blas_t, warmup=5, iters=10):
    code = '''
import os, time
os.environ["OMP_NUM_THREADS"] = "%d"
os.environ["OPENBLAS_NUM_THREADS"] = "%d"
os.environ["OMP_PROC_BIND"] = "close"
os.environ["OMP_PLACES"] = "cores"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["GLOG_minloglevel"] = "3"
import numpy as np, caffe_ffi
proto = "%s"
model = "%s"
batch = %d
mean_vals = %s
np.random.seed(42)
data = np.random.rand(batch,3,224,224).astype(np.float32)
data -= np.array(mean_vals,dtype=np.float32).reshape(1,3,1,1)
net = caffe_ffi.read_net(proto, model)
input_blob = None
for bname in ["data", "data1", "input"]:
    try:
        input_blob = net.blob_by_name(bname)
        break
    except: pass
input_blob.data = data
# Find output blob name (last blob after forward)
for _ in range(%d): net.forward()
out_blob = None
for bname in ["prob", "fc1000", "loss3/classifier", "output"]:
    try:
        out_blob = net.blob_by_name(bname)
        break
    except: pass
if out_blob is None:
    # Get any blob after forward by iterating
    import ctypes
    # fallback: forward returns a dict
    res = net.forward()
    out_key = list(res.keys())[-1]
    out_blob = net.blob_by_name(out_key)
t0=time.perf_counter()
for _ in range(%d): net.forward()
dt=(time.perf_counter()-t0)*1000.0/%d
out = out_blob.data.copy()
np.save("/tmp/_test_out.npy", out)
print(f"RESULT dt={dt:.1f} outsum={np.sum(out):.6f}")
''' % (omp_t, blas_t, proto, model, batch, mean_vals, warmup, iters, iters)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
    for line in r.stdout.split("\n"):
        if line.startswith("RESULT "):
            parts = {}
            for tok in line[7:].split():
                k,v = tok.split("=")
                try: parts[k] = float(v)
                except: parts[k] = v
            out = np.load("/tmp/_test_out.npy")
            return parts["dt"], out
    # Print error
    for line in r.stderr.split("\n"):
        if "Error" in line or "Traceback" in line or "KeyError" in line:
            print(f"  ERR: {line.strip()[:200]}", file=sys.stderr)
    return None, None

for model_name, proto, model in [("ResNet-50", proto_rn50, model_rn50), ("InceptionV1", proto_inc, model_inc)]:
    mean_vals = mean_rn50 if "ResNet" in model_name else mean_inc
    print(f"\n=== {model_name} batch=1, v2 channel-parallel with OMP=1 BLAS fix ===\n")
    results = {}
    for label, omp, blas in [("OMP=1 BLAS=1", 1,1), ("OMP=1 BLAS=4", 1,4),
                              ("OMP=2 BLAS=1", 2,1), ("OMP=4 BLAS=1", 4,1)]:
        dt, out = run_cfg(proto, model, mean_vals, 1, omp, blas)
        if dt:
            results[label] = (dt, out)
            base_dt = results["OMP=1 BLAS=1"][0] if "OMP=1 BLAS=1" in results else dt
            print(f"  {label}: {dt:.1f} ms  ({base_dt/dt:.2f}x)")
        else:
            print(f"  {label}: FAILED")
    # Correctness check
    if "OMP=1 BLAS=1" in results:
        base_out = results["OMP=1 BLAS=1"][1]
        for label,(dt,out) in results.items():
            if label != "OMP=1 BLAS=1":
                d = np.max(np.abs(base_out - out))
                print(f"  diff({label} vs base): {d:.2e} {'PASS' if d<1e-4 else 'FAIL'}")
