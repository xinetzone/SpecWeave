#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 caffe-ffi read_net 是否真正加载 caffemodel 权重"""
import numpy as np
import caffe_ffi

net = caffe_ffi.read_net("/root/.caffe_test_data/models/inceptionv1.prototxt",
                         "/root/.caffe_test_data/models/inceptionv1.caffemodel")
print("num layers:", len(net.layers_array()))
print("num blobs:", len(net.blobs_array()))

# 定位 conv1/7x7_s2 层
for i, ln in enumerate(net.layers_array()):
    nm = getattr(ln, "name", ln)
    if "conv1/7x7_s2" in str(nm):
        print(f"layer[{i}]: {nm} type={getattr(ln, 'type', ln)} nblobs={len(getattr(ln,'blobs',[]))}")
        blobs = ln.blobs
        for bi, b in enumerate(blobs):
            try:
                arr = np.asarray(b.data, dtype=np.float64)
                print(f"  blob[{bi}] shape={arr.shape} max={np.abs(arr).max():.4e} min={arr.min():.4e} mean={arr.mean():.4e} std={arr.std():.4e}")
            except Exception as e:
                print(f"  blob[{bi}] ERR {e}")
        break