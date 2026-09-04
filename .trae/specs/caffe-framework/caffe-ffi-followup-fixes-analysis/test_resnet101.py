import os
os.environ["GLOG_minloglevel"] = "3"
import numpy as np, time, caffe_ffi

# Test ResNet-101 with random weights
proto = "/root/.caffe_test_data/models/resnet101.prototxt"
net = caffe_ffi.read_net(proto, None)
print("ResNet-101 loaded with random weights")

inp = net.blob_by_name("data")
print(f"Input blob shape after load: {inp.data.shape}")

data = np.random.rand(1,3,224,224).astype(np.float32)
data -= np.array([103.939,116.779,123.68], dtype=np.float32).reshape(1,3,1,1)
inp.data = data

# Warmup
for _ in range(3):
    net.forward()

# Timing
t0 = time.perf_counter()
for _ in range(5):
    net.forward()
t1 = time.perf_counter()
avg_ms = (t1-t0)/5*1000
print(f"ResNet-101 batch=1: {avg_ms:.1f} ms/iter, {1000/avg_ms:.2f} FPS")

# Find output blob
for name in ["prob", "fc1000", "loss3/classifier"]:
    try:
        out = net.blob_by_name(name)
        print(f"Output blob '{name}' shape: {out.data.shape}")
        break
    except:
        pass
