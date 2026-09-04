#!/usr/bin/env python3
"""Diagnostic: Verify thread counts are correctly set and find optimal config."""
import os, sys, time, subprocess
import numpy as np

proto = "/root/.caffe_test_data/models/resnet50.prototxt"
model = "/root/.caffe_test_data/models/resnet50.caffemodel"

# First: verify BLAS thread count is actually being controlled
diag_code = '''
import os
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["GLOG_minloglevel"] = "3"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import ctypes, numpy as np, caffe_ffi
# Check OpenBLAS thread count after import
lib = ctypes.CDLL("libopenblas.so.0")
try:
    fn = lib.openblas_get_num_threads
    fn.restype = ctypes.c_int
    print("OpenBLAS threads after caffe_ffi import:", fn())
except Exception as e:
    print("Cannot get openblas threads:", e)
try:
    fn = lib.openblas_get_parallel
    fn.restype = ctypes.c_int
    print("OpenBLAS parallel mode (0=SEQ,1=THREADED,2=OPENMP):", fn())
except Exception as e:
    print("Cannot get parallel mode:", e)
'''
r = subprocess.run([sys.executable, "-c", diag_code], capture_output=True, text=True, timeout=30)
print("=== Diagnostic ===")
print(r.stdout)
if r.stderr: print("STDERR:", r.stderr[:300])

# Now run benchmark with explicit openblas_set_num_threads() call
print("\n=== ResNet-50 batch=1, with explicit BLAS thread control ===")
for omp_t in [1, 2, 4]:
    for blas_t in [1, 2, 4]:
        code = f'''
import os, time, ctypes
os.environ["OMP_NUM_THREADS"] = "{omp_t}"
os.environ["OPENBLAS_NUM_THREADS"] = "{blas_t}"
os.environ["OMP_PROC_BIND"] = "close"
os.environ["OMP_PLACES"] = "cores"
os.environ["GLOG_minloglevel"] = "3"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import numpy as np, caffe_ffi
# Explicitly set BLAS threads via C API in case env var not picked up
_lib = ctypes.CDLL("libopenblas.so.0")
try:
    _lib.openblas_set_num_threads(int({blas_t}))
except: pass
np.random.seed(42)
net = caffe_ffi.read_net("{proto}", "{model}")
data = np.random.rand(1,3,224,224).astype(np.float32)
data -= np.array([103.939,116.779,123.68],dtype=np.float32).reshape(1,3,1,1)
net.blob_by_name("data").data = data
for _ in range(5): net.forward()
t0=time.perf_counter()
for _ in range(15): net.forward()
dt=(time.perf_counter()-t0)*1000/15
print(f"RESULT dt={{dt:.1f}}")
'''
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
        for line in r.stdout.split("\n"):
            if line.startswith("RESULT "):
                dt = float(line.split("dt=")[1])
                print(f"  OMP={omp_t} BLAS={blas_t}: {dt:.1f} ms  ({1000/dt:.2f} FPS)")
                break
        else:
            err = [l for l in r.stderr.split("\n") if "Error" in l or "Traceback" in l]
            if err: print(f"  OMP={omp_t} BLAS={blas_t}: FAILED - {err[-1][:100]}")
