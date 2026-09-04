#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核验 eltwise_sum / concat 的参考值，判定哪实现正确"""
import json
import numpy as np

def make_input(shape, seed):
    return np.random.RandomState(seed).randn(*shape).astype(np.float32)

RES = "/tmp/results"
ffi = json.load(open(f"{RES}/cross_ops_caffe_ffi.json"))
cx = json.load(open(f"{RES}/cross_ops_caffex.json"))

for op, shape in [("eltwise_sum", (2,4,8,8)), ("eltwise_max",(2,4,8,8)), ("concat",(2,3,6,6))]:
    seed = sum(ord(c) for c in op) + 1000
    data = make_input(shape, seed)
    data2 = make_input(shape, seed + 1)
    if op == "eltwise_sum":
        ref = data + data2
    elif op == "eltwise_max":
        ref = np.maximum(data, data2)
    else:
        ref = np.concatenate([data, data2], axis=1)
    ref = ref.ravel()

    def get(entry):
        d, shp = next(iter(entry["outputs"].values()))
        return np.asarray(d, dtype=np.float64).ravel()

    a = get(ffi[op])
    b = get(cx[op])
    print(f"=== {op} | shape={shape} | ref_len={ref.shape[0]} ffi_len={a.shape[0]} cx_len={b.shape[0]} ===")
    print(f"  ref  first8: {np.round(ref[:8],4)}")
    print(f"  ffi  first8: {np.round(a[:8],4)}   max|ffi-ref|={np.abs(a-ref).max():.3e}")
    print(f"  cx   first8: {np.round(b[:8],4)}   max|cx-ref|={np.abs(b-ref).max():.3e}")
    print(f"  max|ffi-cx|={np.abs(a-b).max():.3e}")
    print()