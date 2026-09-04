#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速验证 caffex/pycaffe 多输入算子行为"""
import os
import tempfile
import numpy as np
import caffe

proto = '''name: "t"
input: "data"
input_shape { dim: 1 dim: 2 dim: 2 dim: 2 }
input: "data2"
input_shape { dim: 1 dim: 2 dim: 2 dim: 2 }
layer { name: "e" type: "Eltwise" bottom: "data" bottom: "data2" top: "e" eltwise_param { operation: SUM } }
'''
fd, path = tempfile.mkstemp(suffix=".prototxt")
os.write(fd, proto.encode())
os.close(fd)
net = caffe.Net(path, caffe.TEST)
print("blob names:", list(net.blobs.keys()))
data = np.arange(8, dtype=np.float32).reshape(1,2,2,2)
data2 = np.full((1,2,2,2), 100.0, dtype=np.float32)
net.blobs['data'].data[...] = data
net.blobs['data2'].data[...] = data2
print("data  readback:", net.blobs['data'].data.ravel()[:4])
print("data2 readback:", net.blobs['data2'].data.ravel()[:4])
out = net.forward()
print("e output:", out['e'].ravel()[:4], " (期望 100,101,102,103)")
os.remove(path)