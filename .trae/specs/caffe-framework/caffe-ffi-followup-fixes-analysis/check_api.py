import os
os.environ["GLOG_minloglevel"] = "3"
import caffe_ffi
# Check Net methods
net = caffe_ffi.read_net("/root/.caffe_test_data/models/resnet50.prototxt",
                         "/root/.caffe_test_data/models/resnet50.caffemodel")
methods = [m for m in dir(net) if not m.startswith('_')]
print("Net methods:", methods)
# Check Blob methods
inp = net.blob_by_name("data")
print("Blob methods:", [m for m in dir(inp) if not m.startswith('_')])
print("Input shape:", inp.data.shape)
