#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Top-K 分类一致性分析（跨实现）。

在真实预训练网络（InceptionV1 / ResNet50）上，对同一固定输入，
分别用 caffe-ffi 与 caffex 推理，计算 Top-1/Top-5 类别索引及其跨实现一致性。

用法（在对应环境内执行）:
    python topk_analysis.py <model_dir> <input_npy> <out.json> <impl>
    impl: caffe_ffi | caffex
"""
import json, os, sys
import numpy as np

model_dir = sys.argv[1]
input_npy = sys.argv[2]
out_json = sys.argv[3]
impl = sys.argv[4]

try:
    import caffe_ffi
    HAS_FFI = True
except Exception:
    HAS_FFI = False
try:
    import caffe
    HAS_PYCAFFE = True
except Exception:
    HAS_PYCAFFE = False

MODEL = os.environ.get("NET_NAME", "inceptionv1")
PROTO = os.path.join(model_dir, f"{MODEL}.prototxt")
BLOB = os.path.join(model_dir, f"{MODEL}.caffemodel")

raw = np.load(input_npy)  # (1,3,224,224) 0-255 uint8
ref_mean = np.array([103.939, 116.779, 123.68], dtype=np.float32).reshape(1, 3, 1, 1)
data = (raw.astype(np.float32) - ref_mean).astype(np.float32)  # 预处理后

def softmax_topk(score):
    # 若为 (batch, classes)，取第一个样本做 Top-K（batch 维度不影响分类一致性比较）
    if score.ndim == 2:
        score = score[0]
    score = score.ravel().astype(np.float64)
    # 稳定 softmax
    e = np.exp(score - score.max())
    p = e / e.sum()
    topk = np.argsort(-p)[:5]  # 若含 NaN，argsort 结果不确定，但诚实记录
    return {
        "top1": int(topk[0]),
        "top5": [int(x) for x in topk],
        "probs_top5": [float(round(p[x], 4)) for x in topk],
        "has_nan": bool(np.isnan(score).any()),
        "has_inf": bool(np.isinf(score).any()),
        "score_max": float(np.nanmax(score)) if not np.all(np.isnan(score)) else None,
    }

result = {"impl": impl, "model": MODEL, "shapes_ok": True}
try:
    if impl == "caffe_ffi":
        if not HAS_FFI:
            raise RuntimeError("caffe_ffi not importable")
        net = caffe_ffi.read_net(PROTO, BLOB)
        net.blob_by_name("data").data = data
        out = net.forward()
        # 取第一个输出 blob
        key = list(out.keys())[0]
        score = np.asarray(out[key], dtype=np.float64)
        result["output_blob"] = key
        result["output_shape"] = list(score.shape)
    elif impl == "caffex":
        if not HAS_PYCAFFE:
            raise RuntimeError("caffe not importable")
        net = caffe.Net(PROTO, caffe.TEST)
        net.copy_from(BLOB)
        # 输入 blob 名
        in_blob = net.blobs.keys()[0] if hasattr(net.blobs.keys(), "__getitem__") else list(net.blobs.keys())[0]
        if in_blob != "data":
            in_blob = "data"
        net.blobs[in_blob].data[...] = data
        out = net.forward()
        key = list(out.keys())[0]
        score = np.asarray(out[key].data, dtype=np.float64) if hasattr(out[key], "data") else np.asarray(out[key], dtype=np.float64)
        result["output_blob"] = key
        result["output_shape"] = list(score.shape)
    else:
        raise ValueError("unknown impl")
    result.update(softmax_topk(score))
    result["ok"] = True
except Exception as e:
    result["ok"] = False
    result["error"] = f"{type(e).__name__}: {e}"

with open(out_json, "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print(json.dumps(result, indent=2, ensure_ascii=False))