#!/usr/bin/env python3
"""Quick smoke test for batch=16 functionality."""
import os, sys, tempfile, re
sys.path.insert(0, os.path.dirname(__file__))

# Copy the _make_batch_prototxt function
def make_proto(proto_path, batch):
    if batch == 1:
        return proto_path
    with open(proto_path, "r") as f:
        content = f.read()
    lines = content.split("\n")
    found_data = False
    dim_count = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("input:") and "data" in stripped:
            found_data = True
            continue
        if found_data and stripped.startswith("input_dim:"):
            dim_count += 1
            if dim_count == 1:
                lines[i] = re.sub(r"input_dim:\s*\d+", f"input_dim: {batch}", line)
                break
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".prototxt", delete=False, dir="/tmp")
    tmp.write("\n".join(lines))
    tmp.close()
    return tmp.name

os.environ["OMP_NUM_THREADS"] = "4"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_WAIT_POLICY"] = "PASSIVE"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["GLOG_minloglevel"] = "3"
import numpy as np, caffe_ffi, time

# Test ResNet-50 batch=16
proto16 = make_proto("/root/.caffe_test_data/models/resnet50.prototxt", 16)
print(f"Using proto: {proto16}")
print("Loading ResNet-50 batch=16...")
net = caffe_ffi.read_net(proto16, "/root/.caffe_test_data/models/resnet50.caffemodel")
inp = net.blob_by_name("data")
print(f"Input shape after load: {inp.data.shape}")

data = np.random.rand(16, 3, 224, 224).astype(np.float32)
data -= np.array([103.939, 116.779, 123.68], dtype=np.float32).reshape(1,3,1,1)
inp.data = data
print("Running forward...")
for _ in range(3):
    net.forward()
t0 = time.perf_counter()
for _ in range(5):
    net.forward()
t1 = time.perf_counter()
avg = (t1-t0)/5*1000
print(f"batch=16 avg={avg:.1f}ms  per-img={avg/16:.1f}ms  FPS={1000*16/avg:.2f}")

# Get output shape
for name in ["prob", "fc1000"]:
    try:
        out = net.blob_by_name(name)
        print(f"Output '{name}' shape: {out.data.shape}")
        break
    except:
        pass

os.unlink(proto16)
print("\nBatch=16 works!")
