#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""InceptionV1 逐层 max-abs 追踪：定位 Inf 放大路径"""
import os, sys, numpy as np
sys.path.insert(0, "/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python/networks")
from utils import _preprocess_imagenet, _CAFFE_FFI_AVAILABLE
import caffe_ffi

MODEL_DIR = "/root/.caffe_test_data/models"
np.random.seed(42)
data = np.random.randint(0, 256, size=(1, 3, 224, 224)).astype(np.float32)
data_process = _preprocess_imagenet(data, scale=58.8)
# 保存输入供 caffex 复用
np.save("/tmp/inception_input.npy", data_process)

net = caffe_ffi.read_net(os.path.join(MODEL_DIR, "inceptionv1.prototxt"),
                         os.path.join(MODEL_DIR, "inceptionv1.caffemodel"))
net.blob_by_name("data").data = data_process
out = net.forward()
print("input done, output keys:", list(out.keys()))

# 追踪 conv4/inception_5 区域每个 blob 的 max-abs、Inf、NaN
def fmt(v):
    a = np.asarray(v, dtype=np.float64)
    mx = np.abs(a).max() if a.size else 0.0
    return f"max={mx:12.4e} inf={int(np.isinf(a).sum()):8d} nan={int(np.isnan(a).sum()):8d}"

# 打印所有 blob 的 max-abs，找出放大点
prev = None
for bname in net.blob_names():
    if not any(k in bname for k in ["inception_4c", "inception_4d", "inception_4e", "inception_5a", "pool2", "pool3", "inception_3"]):
        continue
    try:
        bdata = net.blob_by_name(bname).data
        print(f"  {bname:28s} {fmt(bdata)}")
    except Exception as e:
        print(f"  {bname:28s} ERR {e}")