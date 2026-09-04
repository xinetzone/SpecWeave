#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨实现算子精度对比脚本（caffe-ffi <-> caffex/pycaffe 通用）
- 环境自适应：检测 caffe_ffi 或 pycaffe，分别使用对应 API
- 使用 constant filler 保证权重确定性，输入使用固定种子，确保两实现可复现对比
- 输出：dump JSON 到指定目录，供后续对比
用法: python cross_ops.py <out_dir> <op_filter>
"""
import os
import sys
import json
import time

import numpy as np
from google.protobuf import text_format

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "/tmp/cross_ops"
OP_FILTER = sys.argv[2] if len(sys.argv) > 2 else "all"

# 环境检测
HAS_CAFFE_FFI = False
HAS_PYCAFFE = False
try:
    import caffe_ffi
    from caffe_ffi import caffe_pb2
    HAS_CAFFE_FFI = True
except Exception:
    pass
try:
    import caffe
    HAS_PYCAFFE = True
except Exception:
    pass

os.makedirs(OUT_DIR, exist_ok=True)
os.environ["GLOG_minloglevel"] = "2"

def make_input(shape, seed):
    # 每算子独立固定种子，保证两环境 RNG 序列一致、可复现
    return np.random.RandomState(seed).randn(*shape).astype(np.float32)


def run_net_pycaffe(proto_text, feed):
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".prototxt")
    with os.fdopen(fd, "w") as f:
        f.write(proto_text)
    net = caffe.Net(path, caffe.TEST)
    for name, arr in feed.items():
        net.blobs[name].data[...] = arr
    out = net.forward()
    os.remove(path)
    return out


def outputs_to_dict(out):
    return {k: (np.asarray(v).ravel().tolist(), list(np.asarray(v).shape)) for k, v in out.items()}


# ---------------- 算子配置 ----------------
OPERATORS = {
    "convolution": (
        """layer { name: "conv" type: "Convolution" bottom: "data" top: "conv"
  convolution_param {
    num_output: 8 kernel_size: 3 pad: 1 stride: 1
    weight_filler { type: "constant" value: 0.35 }
    bias_filler { type: "constant" value: 0.1 }
  }
}""",
        (1, 3, 16, 16),
    ),
    "pooling": (
        """layer { name: "pool" type: "Pooling" bottom: "data" top: "pool"
  pooling_param { pool: MAX kernel_size: 2 stride: 2 }
}""",
        (1, 4, 16, 16),
    ),
    "pooling_ave": (
        """layer { name: "pool" type: "Pooling" bottom: "data" top: "pool"
  pooling_param { pool: AVE kernel_size: 2 stride: 2 }
}""",
        (1, 4, 16, 16),
    ),
    "relu": ("""layer { name: "relu" type: "ReLU" bottom: "data" top: "relu" }""", (2, 8, 8, 8)),
    "sigmoid": ("""layer { name: "s" type: "Sigmoid" bottom: "data" top: "s" }""", (2, 8, 8, 8)),
    "tanh": ("""layer { name: "t" type: "TanH" bottom: "data" top: "t" }""", (2, 8, 8, 8)),
    "softmax": ("""layer { name: "sm" type: "Softmax" bottom: "data" top: "sm" }""", (2, 5, 4, 4)),
    "eltwise_sum": (
        """layer { name: "e" type: "Eltwise" bottom: "data" bottom: "data2" top: "e"
  eltwise_param { operation: SUM }
}""",
        (2, 4, 8, 8),
    ),
    "eltwise_max": (
        """layer { name: "e" type: "Eltwise" bottom: "data" bottom: "data2" top: "e"
  eltwise_param { operation: MAX }
}""",
        (2, 4, 8, 8),
    ),
    "inner_product": (
        """layer { name: "ip" type: "InnerProduct" bottom: "data" top: "ip"
  inner_product_param {
    num_output: 32
    weight_filler { type: "constant" value: 0.2 }
    bias_filler { type: "constant" value: 0.05 }
  }
}""",
        (2, 4, 4, 4),
    ),
    "batchnorm": (
        """layer { name: "bn" type: "BatchNorm" bottom: "data" top: "bn"
  batch_norm_param { use_global_stats: true }
}
layer { name: "scale" type: "Scale" bottom: "bn" top: "bn_out"
  scale_param { bias_term: true
    filler { type: "constant" value: 0.9 }
    bias_filler { type: "constant" value: 0.1 }
  }
}""",
        (2, 4, 8, 8),
    ),
    "lrn": (
        """layer { name: "lrn" type: "LRN" bottom: "data" top: "lrn"
  lrn_param { local_size: 5 alpha: 0.0001 beta: 0.75 }
}""",
        (1, 8, 8, 8),
    ),
    "prelu": (
        """layer { name: "p" type: "PReLU" bottom: "data" top: "p"
  prelu_param { filler { type: "constant" value: 0.25 } }
}""",
        (2, 4, 8, 8),
    ),
    "elu": ("""layer { name: "e" type: "ELU" bottom: "data" top: "e" }""", (2, 4, 8, 8)),
    "swish": ("""layer { name: "sw" type: "Swish" bottom: "data" top: "sw" }""", (2, 4, 8, 8)),
    "dropout": (
        """layer { name: "d" type: "Dropout" bottom: "data" top: "d"
  dropout_param { dropout_ratio: 0.5 }
}""",
        (2, 4, 8, 8),
    ),
    "flatten": ("""layer { name: "f" type: "Flatten" bottom: "data" top: "f" }""", (2, 4, 4, 4)),
    "concat": (
        """layer { name: "c1" type: "Concat" bottom: "data" bottom: "data2" top: "c"
  concat_param { axis: 1 }
}""",
        (2, 3, 6, 6),
    ),
    "slice": (
        """layer { name: "s" type: "Slice" bottom: "data" top: "s0" top: "s1"
  slice_param { axis: 1 slice_point: 3 }
}""",
        (2, 6, 6, 6),
    ),
}


def build_proto(op_name):
    body, shape = OPERATORS[op_name]
    dim_str = " ".join(f"dim: {d}" for d in shape)
    proto = f"""name: "cross_{op_name}"
input: "data"
input_shape {{ {dim_str} }}
"""
    if op_name in ("eltwise_sum", "eltwise_max", "concat"):
        proto += f'\ninput: "data2"\ninput_shape {{ {dim_str} }}\n'
    proto += body
    return proto


def main():
    results = {}
    for op_name in OPERATORS:
        if OP_FILTER != "all" and OP_FILTER not in op_name:
            continue
        body, shape = OPERATORS[op_name]
        proto = build_proto(op_name)
        seed = sum(ord(c) for c in op_name) + 1000  # 每算子确定性种子
        input_data = make_input(shape, seed)
        input_data2 = make_input(shape, seed + 1)
        entry = {
            "op": op_name,
            "input_shape": list(shape),
            "env": "caffe_ffi" if HAS_CAFFE_FFI else ("pycaffe" if HAS_PYCAFFE else "unknown"),
        }
        t0 = time.time()
        try:
            if HAS_CAFFE_FFI:
                net = caffe_ffi.net_from_param(text_format.Parse(proto, caffe_pb2.NetParameter()))
                feed = {"data": input_data}
                if op_name in ("eltwise_sum", "eltwise_max", "concat"):
                    feed["data2"] = input_data2
                out = net.forward(feed)
                entry["outputs"] = outputs_to_dict(out)
            else:
                feed = {"data": input_data}
                if op_name in ("eltwise_sum", "eltwise_max", "concat"):
                    feed["data2"] = input_data2
                out = run_net_pycaffe(proto, feed)
                entry["outputs"] = outputs_to_dict(out)
            entry["ok"] = True
            entry["elapsed_ms"] = round((time.time() - t0) * 1000, 3)
            entry["has_nan"] = any(np.isnan(np.asarray(v[0])).any() for v in entry["outputs"].values())
            entry["has_inf"] = any(np.isinf(np.asarray(v[0])).any() for v in entry["outputs"].values())
        except Exception as e:
            entry["ok"] = False
            entry["error"] = f"{type(e).__name__}: {e}"
            entry["elapsed_ms"] = round((time.time() - t0) * 1000, 3)
        results[op_name] = entry
        print(f"[{entry['env']}] {op_name}: {'OK' if entry.get('ok') else 'FAIL'} "
              f"({entry.get('elapsed_ms', '-')}ms) {entry.get('error', '')}")

    out_path = os.path.join(OUT_DIR, f"cross_ops_{'caffe_ffi' if HAS_CAFFE_FFI else 'caffex'}.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n结果已保存: {out_path}")


if __name__ == "__main__":
    main()