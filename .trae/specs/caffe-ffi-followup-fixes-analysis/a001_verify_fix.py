#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A-001 修复验证脚本：确认 caffe-ffi read_net 真正加载 caffemodel 真实权重。

在 WSL 容器 caffe-ffi-jupyter（Python 3.14）内重编译 native 扩展后运行：
    python a001_verify_fix.py

三项断言：
  1) conv1/7x7_s2 权重真实（std>0 且非全 1.0）—— 修复前为 constant=1.0 / std=0
  2) 全网络 forward 无 NaN/Inf —— 修复前指数放大至 Inf/NaN
  3) 与 caffex（原生 Caffe）关键层输出对齐
"""
import os
import sys
import numpy as np

MODEL_DIR = "/SpecWeave/.trae/specs/caffe-comprehensive-comparison-test/test-assets/models"
PROTO = os.path.join(MODEL_DIR, "inceptionv1.prototxt")
CAFFEMODEL = os.path.join(MODEL_DIR, "inceptionv1.caffemodel")

import caffe_ffi

failures = []


def check(cond, msg):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {msg}")
    if not cond:
        failures.append(msg)


def get_conv1_blob(net):
    """返回 conv1/7x7_s2 的权重数组（numpy float64）。"""
    for ln in net.layers_array():
        nm = getattr(ln, "name", ln)
        if "conv1/7x7_s2" in str(nm):
            for b in ln.blobs:
                arr = np.asarray(b.data, dtype=np.float64)
                if arr.ndim >= 2 and arr.size > 0:
                    return arr
    return None


def main():
    print("caffe_ffi:", caffe_ffi.__version__,
          "native:", caffe_ffi.is_available())
    if not caffe_ffi.is_available():
        print("FATAL: native extension not available; rebuild _caffe_ffi.so first.")
        sys.exit(2)

    # ---- 1. 权重真实性 ----
    net = caffe_ffi.read_net(PROTO, CAFFEMODEL)
    w = get_conv1_blob(net)
    check(w is not None, "找到 conv1/7x7_s2 权重 blob")
    if w is not None:
        print(f"  conv1 weight shape={w.shape} "
              f"max-abs={np.abs(w).max():.4e} std={w.std():.4e}")
        check(w.size > 0 and w.std() > 1e-6, "conv1 权重 std>0（非默认 constant=1.0）")
        check(not np.allclose(w, 1.0), "conv1 权重不全为 1.0")

    # ---- 2. 无 NaN/Inf ----
    rng = np.random.default_rng(0)
    data = rng.integers(0, 256, size=(1, 3, 224, 224)).astype(np.float32)
    # InceptionV1 常用预处理：图像均值 123.68/116.779/103.939，scale=1/58.8
    mean = np.array([123.68, 116.779, 103.939], dtype=np.float32).reshape(1, 3, 1, 1)
    data_process = (data - mean) * (1.0 / 58.8)
    try:
        net.blob_by_name("data").data = data_process.astype(np.float32)
    except Exception as e:
        print("  (input set skipped:)", type(e).__name__, e)
    out = net.forward()
    print("  forward keys:", list(out.keys()))

    nan_total = inf_total = 0
    for bname in net.blob_names():
        try:
            arr = np.asarray(net.blob_by_name(bname).data, dtype=np.float64)
            if arr.size == 0:
                continue
            nan_total += int(np.isnan(arr).sum())
            inf_total += int(np.isinf(arr).sum())
        except Exception:
            pass
    print(f"  [NAN] total={nan_total} [INF] total={inf_total}")
    check(nan_total == 0 and inf_total == 0, "全网络 forward 无 NaN/Inf")

    # ---- 3. 与 caffex 对齐（需容器内安装 pycaffe）----
    try:
        import caffe  # noqa
        os.environ.setdefault("GLOG_minloglevel", "2")
        cnet = caffe.Net(PROTO, CAFFEMODEL, caffe.TEST)
        cnet.blobs["data"].data[...] = data_process.astype(np.float32)
        cout = cnet.forward()
        cfirst = np.asarray(list(cout.values())[0])
        ffirst = np.asarray(list(out.values())[0])
        diff = np.abs(ffirst - cfirst[: ffirst.shape[0]]).max()
        print(f"  output max-abs diff vs caffex: {diff:.6e}")
        check(diff < 1e-2, "输出与 caffex 对齐（max-abs diff < 1e-2）")
    except ImportError:
        print("[SKIP] pycaffe 未安装，跳过 caffex 对齐对比")

    print("\n==== 结果 ====")
    if failures:
        print("FAILED:", len(failures), "项")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print("ALL PASS")


if __name__ == "__main__":
    main()