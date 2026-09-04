#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""caffex 相同输入 InceptionV1 对比：确认是否同样 float32 溢出"""
import os, numpy as np
import caffe
os.environ["GLOG_minloglevel"]="2"

data_process = np.load("/tmp/inc.npy")
print("input shape:", data_process.shape, "max:", np.abs(data_process).max())

net = caffe.Net("/tmp/inc.prototxt", "/tmp/inc.caffemodel", caffe.TEST)
net.blobs["data"].data[...] = data_process
out = net.forward()
first = list(out.values())[0]
arr = np.asarray(first)
print("output prob shape:", arr.shape)
print("  max-abs:", np.abs(arr).max(), "inf:", int(np.isinf(arr).sum()), "nan:", int(np.isnan(arr).sum()))
print("  first8:", np.round(arr.ravel()[:8],6))

# 检查关键中间层
for bname in ["inception_3a/output","inception_3b/output","inception_4c/output","inception_4d/output","inception_4e/output","inception_5a/output"]:
    try:
        b = net.blobs[bname].data
        b = np.asarray(b)
        print(f"  {bname:24s} max={np.abs(b).max():12.4e} inf={int(np.isinf(b).sum()):7d} nan={int(np.isnan(b).sum()):7d}")
    except Exception as e:
        print(f"  {bname}: ERR {type(e).__name__}: {e}")