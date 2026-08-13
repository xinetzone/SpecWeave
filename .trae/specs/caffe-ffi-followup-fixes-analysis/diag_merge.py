#!/usr/bin/env python3
"""Diagnostic: check if _merge_weights correctly puts caffemodel blobs into param.
Uses standalone caffe_pb2 import without importing full caffe_ffi."""
import sys, os
sys.path.insert(0, "/SpecWeave/projects/xuanspace/libs/caffe-ffi/python")
# Directly import caffe_pb2 generated file
import importlib.util
pb2_path = "/SpecWeave/projects/xuanspace/libs/caffe-ffi/python/caffe_ffi/caffe_pb2.py"
spec = importlib.util.spec_from_file_location("caffe_pb2", pb2_path)
caffe_pb2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(caffe_pb2)

from google.protobuf import text_format
import numpy as np

MODEL_DIR = "/SpecWeave/.trae/specs/caffe-comprehensive-comparison-test/test-assets/models"
PROTO = MODEL_DIR + "/inceptionv1.prototxt"
CAFFEMODEL = MODEL_DIR + "/inceptionv1.caffemodel"

param = caffe_pb2.NetParameter()
with open(PROTO, "r", encoding="utf-8") as f:
    text_format.Parse(f.read(), param)

weights = caffe_pb2.NetParameter()
with open(CAFFEMODEL, "rb") as f:
    weights.ParseFromString(f.read())

print(f"Prototxt layers: {len(param.layer)}")
print(f"Caffemodel layers: {len(weights.layer)}")

# Check a few weight layers
n_with_blobs = 0
for wl in weights.layer:
    if len(wl.blobs) > 0:
        n_with_blobs += 1
        if n_with_blobs <= 5:
            b0 = wl.blobs[0]
            dcount = max(len(b0.data), len(b0.double_data))
            if dcount > 0:
                arr = list(b0.data) if len(b0.data) > 0 else [float(v) for v in b0.double_data]
                arr = np.array(arr, dtype=np.float64)
                print(f"  W '{wl.name}': blobs={len(wl.blobs)}, b0.elems={dcount}, std={arr.std():.4e}, max={np.abs(arr).max():.4e}")
            else:
                print(f"  W '{wl.name}': blobs={len(wl.blobs)}, b0 HAS NO DATA/DOUBLE_DATA!")
print(f"Total layers with blobs in caffemodel: {n_with_blobs}")

# Merge
layer_map = {layer.name: layer for layer in param.layer}
merged = 0
for w_layer in weights.layer:
    if w_layer.name in layer_map and len(w_layer.blobs) > 0:
        layer_map[w_layer.name].blobs.extend(w_layer.blobs)
        merged += 1
print(f"Merged: {merged} layers")

# Check conv1
target = None
for l in param.layer:
    if 'conv1/7x7_s2' in l.name:
        target = l
        break

if target:
    print(f"\nAfter merge: '{target.name}' blobs={len(target.blobs)}")
    for i, b in enumerate(target.blobs):
        dcount = max(len(b.data), len(b.double_data))
        print(f"  blob[{i}]: data={len(b.data)}, double_data={len(b.double_data)}, shape=({b.num},{b.channels},{b.height},{b.width})")
        if dcount > 0:
            arr = list(b.data) if len(b.data) > 0 else [float(v) for v in b.double_data]
            arr = np.array(arr, dtype=np.float64)
            print(f"    -> std={arr.std():.4e}, max_abs={np.abs(arr).max():.4e}, first5={arr[:5]}")
else:
    print("conv1/7x7_s2 NOT FOUND!")

# Serialize to text and re-parse
proto_text = text_format.MessageToString(param)
print(f"\nSerialized text length: {len(proto_text)} chars")

param2 = caffe_pb2.NetParameter()
text_format.Parse(proto_text, param2)
for l in param2.layer:
    if 'conv1/7x7_s2' in l.name:
        print(f"After text round-trip: '{l.name}' blobs={len(l.blobs)}")
        for i, b in enumerate(l.blobs):
            dcount = max(len(b.data), len(b.double_data))
            print(f"  blob[{i}]: data={len(b.data)}, double_data={len(b.double_data)}")
            if dcount > 0:
                arr = list(b.data) if len(b.data) > 0 else [float(v) for v in b.double_data]
                arr = np.array(arr, dtype=np.float64)
                print(f"    -> std={arr.std():.4e}, max_abs={np.abs(arr).max():.4e}")
        break
