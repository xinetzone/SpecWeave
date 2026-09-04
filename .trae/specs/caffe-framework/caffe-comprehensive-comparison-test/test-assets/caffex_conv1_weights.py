#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""caffex conv1 权重统计（对比 caffe-ffi 权重加载）"""
import os, numpy as np
import caffe
os.environ["GLOG_minloglevel"]="2"
net = caffe.Net("/tmp/inc.prototxt", "/tmp/inc.caffemodel", caffe.TEST)
conv1 = net.layer_dict["conv1/7x7_s2"]
print("layer found:", "conv1/7x7_s2", "type:", conv1.type, "nblobs:", len(conv1.blobs))
for bi, b in enumerate(conv1.blobs):
    w = np.array(b.data, dtype=np.float64)
    print(f"  blob[{bi}] shape={w.shape} max={np.abs(w).max():.4e} min={w.min():.4e} mean={w.mean():.4e} std={w.std():.4e}")