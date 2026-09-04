#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""算子性能基准：多迭代延迟统计（自动适配 caffe_ffi / caffe pycaffe）
用法: python benchmark_ops.py <out.json> <iterations>
"""
import json, os, sys, time
import numpy as np

try:
    from google.protobuf import text_format
    import caffe  # noqa
    HAS_PYCAFFE = True
except Exception:
    HAS_PYCAFFE = False

try:
    import caffe_ffi
    from caffe_ffi import caffe_pb2
    HAS_CAFFE_FFI = True
except Exception:
    HAS_CAFFE_FFI = False

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/bench.json"
ITERS = int(sys.argv[2]) if len(sys.argv) > 2 else 20

def make_input(shape, seed):
    rng = np.random.RandomState(seed)
    return rng.randn(*shape).astype(np.float32)

OPERATORS = {
    "convolution": (
        "layer { name: \"conv\" type: \"Convolution\" bottom: \"data\" top: \"conv\" "
        "convolution_param { num_output: 16 kernel_size: 3 pad: 1 } }",
        (2, 8, 32, 32)),
    "pooling": (
        "layer { name: \"pool\" type: \"Pooling\" bottom: \"data\" top: \"pool\" "
        "pooling_param { pool: MAX kernel_size: 2 stride: 2 } }",
        (2, 8, 32, 32)),
    "relu": (
        "layer { name: \"re\" type: \"ReLU\" bottom: \"data\" top: \"re\" }",
        (2, 8, 32, 32)),
    "sigmoid": (
        "layer { name: \"s\" type: \"Sigmoid\" bottom: \"data\" top: \"s\" }",
        (2, 8, 32, 32)),
    "tanh": (
        "layer { name: \"t\" type: \"TanH\" bottom: \"data\" top: \"t\" }",
        (2, 8, 32, 32)),
    "softmax": (
        "layer { name: \"sm\" type: \"Softmax\" bottom: \"data\" top: \"sm\" }",
        (2, 8, 32, 32)),
    "inner_product": (
        "layer { name: \"ip\" type: \"InnerProduct\" bottom: \"data\" top: \"ip\" "
        "inner_product_param { num_output: 128 } }",
        (2, 8, 32, 32)),
    "batchnorm": (
        "layer { name: \"bn\" type: \"BatchNorm\" bottom: \"data\" top: \"bn\" "
        "batch_norm_param { use_global_stats: true } }",
        (2, 8, 32, 32)),
    "lrn": (
        "layer { name: \"lr\" type: \"LRN\" bottom: \"data\" top: \"lr\" "
        "lrn_param { local_size: 5 alpha: 0.0001 beta: 0.75 } }",
        (2, 8, 32, 32)),
    "eltwise_sum": (
        "layer { name: \"e\" type: \"Eltwise\" bottom: \"data\" bottom: \"data2\" top: \"e\" "
        "eltwise_param { operation: SUM } }",
        (2, 8, 32, 32)),
    "concat": (
        "layer { name: \"c\" type: \"Concat\" bottom: \"data\" bottom: \"data2\" top: \"c\" }",
        (2, 8, 32, 32)),
}

def build_proto(op):
    body, shape = OPERATORS[op]
    dim = " ".join(f"dim: {d}" for d in shape)
    proto = f"name: \"t\"\ninput: \"data\"\ninput_shape {{ {dim} }}\n"
    if op in ("eltwise_sum", "concat"):
        proto += f"input: \"data2\"\ninput_shape {{ {dim} }}\n"
    proto += body
    return proto

def bench_ffi(op):
    param = caffe_pb2.NetParameter()
    text_format.Parse(build_proto(op), param)
    net = caffe_ffi.net_from_param(param)
    seed = sum(ord(c) for c in op) + 1000
    data = make_input(OPERATORS[op][1], seed)
    feed = {"data": data}
    if op in ("eltwise_sum", "concat"):
        feed["data2"] = make_input(OPERATORS[op][1], seed + 1)
    out = net.forward(feed)
    return out

def bench_pycaffe(op):
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".prototxt")
    os.write(fd, build_proto(op).encode()); os.close(fd)
    net = caffe.Net(path, caffe.TEST)
    seed = sum(ord(c) for c in op) + 1000
    shape = OPERATORS[op][1]
    data = make_input(shape, seed)
    net.blobs["data"].data[...] = data
    if op in ("eltwise_sum", "concat"):
        net.blobs["data2"].data[...] = make_input(shape, seed + 1)
    out = net.forward()
    return out

results = {}
for op in OPERATORS:
    try:
        if HAS_CAFFE_FFI:
            fn = bench_ffi
        else:
            fn = bench_pycaffe
        # warmup
        fn(op)
        times = []
        for _ in range(ITERS):
            t0 = time.perf_counter()
            fn(op)
            times.append((time.perf_counter() - t0) * 1000)
        times = np.array(times)
        results[op] = {
            "ok": True,
            "env": "caffe_ffi" if HAS_CAFFE_FFI else "pycaffe",
            "mean_ms": round(float(times.mean()), 4),
            "std_ms": round(float(times.std()), 4),
            "min_ms": round(float(times.min()), 4),
            "max_ms": round(float(times.max()), 4),
            "fps": round(1000.0 / float(times.mean()), 2),
            "iters": ITERS,
        }
    except Exception as e:
        results[op] = {"ok": False, "error": f"{type(e).__name__}: {e}"}

with open(OUT, "w") as f:
    json.dump({"env": "caffe_ffi" if HAS_CAFFE_FFI else "pycaffe",
               "iters": ITERS, "ops": results}, f, indent=2, ensure_ascii=False)
for op, r in results.items():
    if r.get("ok"):
        print(f"  {op:16s} mean={r['mean_ms']:.3f}ms std={r['std_ms']:.3f} min={r['min_ms']:.3f} max={r['max_ms']:.3f} fps={r['fps']}")
    else:
        print(f"  {op:16s} FAIL {r['error']}")
print("saved:", OUT)