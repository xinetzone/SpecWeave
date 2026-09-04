#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""caffe-ffi 网络级 NaN 逐层诊断：找出首个产生 NaN 的 blob/层"""
import os
import sys
import numpy as np

sys.path.insert(0, "/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python/networks")
from utils import _preprocess_imagenet, _CAFFE_FFI_AVAILABLE

import caffe_ffi

MODEL_DIR = "/root/.caffe_test_data/models"

def preprocess(data, scale):
    return _preprocess_imagenet(data, scale=scale)

def diag(name, proto, blob, scale):
    print(f"\n{'='*60}\n=== {name} ===\n{'='*60}")
    if not _CAFFE_FFI_AVAILABLE:
        print("  caffe_ffi C++ extension NOT available")
        return
    print(f"  caffe_ffi version: {caffe_ffi.__version__}, native: {caffe_ffi.is_available()}")
    data = np.random.randint(0, 256, size=(1, 3, 224, 224)).astype(np.float32)
    data_process = preprocess(data, scale)
    proto_file = os.path.join(MODEL_DIR, proto)
    blob_file = os.path.join(MODEL_DIR, blob)
    net = caffe_ffi.read_net(proto_file, blob_file)
    print(f"  input blobs: {net.input_blob_names()}")
    print(f"  output blobs: {net.output_blob_names()}")
    print(f"  num layers: {len(net.layers_array())}")
    net.blob_by_name("data").data = data_process
    out = net.forward()
    print(f"  forward keys: {list(out.keys())}")
    # 检查所有 blob 是否 NaN/Inf
    for bname in net.blob_names():
        try:
            bdata = net.blob_by_name(bname).data
            arr = np.asarray(bdata, dtype=np.float64)
            if arr.size == 0:
                continue
            nan_n = int(np.isnan(arr).sum())
            inf_n = int(np.isinf(arr).sum())
            if nan_n or inf_n:
                print(f"  [NAN] blob={bname:20s} shape={arr.shape} nan={nan_n} inf={inf_n}")
        except Exception as e:
            print(f"  [err] blob={bname}: {type(e).__name__}: {e}")
    # 输出层首值
    for k, v in out.items():
        print(f"  output {k}: shape={np.asarray(v).shape} first8={np.round(np.asarray(v).ravel()[:8],4)}")

diag("InceptionV1", "inceptionv1.prototxt", "inceptionv1.caffemodel", 58.8)
diag("MobileNetV2", "mobilenetv2.prototxt", "mobilenetv2.caffemodel", 1.0)
diag("ResNet50", "resnet50.prototxt", "resnet50.caffemodel", 1.0)