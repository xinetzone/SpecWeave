#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""caffex 早期层对比：conv1~pool2 max-abs"""
import os, numpy as np
import caffe
os.environ["GLOG_minloglevel"]="2"
data_process = np.load("/tmp/inc.npy")
net = caffe.Net("/tmp/inc.prototxt", "/tmp/inc.caffemodel", caffe.TEST)
net.blobs["data"].data[...] = data_process
out = net.forward()

def fmt(b):
    a=np.asarray(b,dtype=np.float64)
    return f"shape=({a.shape[0] if a.ndim else ''},{a.shape[1] if a.ndim>1 else ''}) max={np.abs(a).max():12.4e} inf={int(np.isinf(a).sum()):6d} nan={int(np.isnan(a).sum()):6d}"

for bname in ["data","conv1/7x7_s2","pool1/3x3_s2","pool1/norm1","conv2/3x3_reduce","conv2/3x3","conv2/norm2","pool2/3x3_s2","inception_3a/1x1","inception_3a/output"]:
    try:
        print(f"  {bname:20s} {fmt(net.blobs[bname].data)}")
    except Exception as e:
        print(f"  {bname}: ERR {type(e).__name__}: {e}")

prob = np.asarray(list(out.values())[0])
print("output prob shape:", prob.shape, "max-abs:", np.abs(prob).max())