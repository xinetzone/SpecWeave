import os
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_WAIT_POLICY"] = "PASSIVE"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["GLOG_minloglevel"] = "3"
import numpy as np, caffe_ffi, time

models = [
    ('ResNet-50', '/root/.caffe_test_data/models/resnet50.prototxt',
     '/root/.caffe_test_data/models/resnet50.caffemodel', [103.939,116.779,123.68]),
]

for name, proto, model, mean in models:
    net = caffe_ffi.read_net(proto, model)
    inp = net.blob_by_name("data")
    data = np.random.rand(1,3,224,224).astype(np.float32)
    data -= np.array(mean,dtype=np.float32).reshape(1,3,1,1)
    inp.data = data
    # Warmup
    for _ in range(10):
        net.forward()
    # Benchmark
    times = []
    for _ in range(30):
        t0 = time.perf_counter()
        net.forward()
        times.append((time.perf_counter()-t0)*1000)
    times = np.array(times)
    print(f"{name} batch=1 OMP=4: avg={np.mean(times):.1f}ms  med={np.median(times):.1f}ms  "
          f"min={np.min(times):.1f}ms  p99={np.percentile(times,99):.1f}ms  cv={np.std(times)/np.mean(times)*100:.1f}%")
