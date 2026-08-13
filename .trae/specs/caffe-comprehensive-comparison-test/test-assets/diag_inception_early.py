#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""caffe-ffi 早期层（conv1~pool2）max-abs 追踪"""
import os, sys, numpy as np
sys.path.insert(0, "/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python/networks")
from utils import _preprocess_imagenet, _CAFFE_FFI_AVAILABLE
import caffe_ffi

MODEL_DIR = "/root/.caffe_test_data/models"
np.random.seed(42)
data = np.random.randint(0, 256, size=(1, 3, 224, 224)).astype(np.float32)
data_process = _preprocess_imagenet(data, scale=58.8)
np.save("/tmp/inc.npy", data_process)

net = caffe_ffi.read_net(os.path.join(MODEL_DIR, "inceptionv1.prototxt"),
                         os.path.join(MODEL_DIR, "inceptionv1.caffemodel"))
print("data blob shape:", net.blob_by_name("data").shape)
net.blob_by_name("data").data = data_process
out = net.forward()
print("output keys:", list(out.keys()), "prob shape:", np.asarray(out['prob']).shape)

def fmt(v):
    a = np.asarray(v, dtype=np.float64)
    return f"max={np.abs(a).max():12.4e} inf={int(np.isinf(a).sum()):6d} nan={int(np.isnan(a).sum()):6d}"

for bname in net.blob_names():
    if not any(k in bname for k in ["data", "conv1", "pool1", "norm1", "conv2", "norm2", "pool2"]):
        continue
    if "split" in bname:
        continue
    try:
        print(f"  {bname:22s} {fmt(net.blob_by_name(bname).data)}")
    except Exception as e:
        print(f"  {bname:22s} ERR {e}")