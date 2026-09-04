import os
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_WAIT_POLICY"] = "PASSIVE"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["GLOG_minloglevel"] = "3"
import caffe_ffi, numpy as np, time
print(f"caffe_ffi file: {caffe_ffi.__file__}")
print(f"caffe_ffi dir: {dir(caffe_ffi)[:10]}")
# Check if conv layer code has v4 features (parallel for M-dimension chunking)
net = caffe_ffi.read_net("/root/.caffe_test_data/models/resnet50.prototxt",
                         "/root/.caffe_test_data/models/resnet50.caffemodel")
# Get a conv layer
for lname in net.layer_names:
    layer = net.layer_by_name(lname)
    if hasattr(layer, 'type') or 'conv' in lname.lower():
        print(f"Layer: {lname}, type check...")
        break
