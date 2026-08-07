#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨实现算子精度对比分析：读取 caffe-ffi 与 caffex 输出，计算精度指标"""
import json
import os
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
RESULT_DIR = os.path.join(BASE, "results")

with open(os.path.join(RESULT_DIR, "cross_ops_caffe_ffi.json")) as f:
    ffi = json.load(f)
with open(os.path.join(RESULT_DIR, "cross_ops_caffex.json")) as f:
    caffex = json.load(f)

# 多输出算子取第一个输出对比（slice 有两个输出）
def first_output(entry):
    for k, v in entry["outputs"].items():
        data, shape = v
        return np.asarray(data, dtype=np.float64).reshape(shape)
    return None

rows = []
for op in ffi:
    e_ffi = ffi[op]
    e_cx = caffex.get(op)
    row = {
        "op": op,
        "caffe_ffi_ok": e_ffi.get("ok", False),
        "caffex_ok": bool(e_cx and e_cx.get("ok", False)),
        "caffe_ffi_ms": e_ffi.get("elapsed_ms", 0),
        "caffex_ms": e_cx.get("elapsed_ms", 0) if e_cx else 0,
        "caffe_ffi_nan": e_ffi.get("has_nan", False),
        "caffex_nan": (e_cx or {}).get("has_nan", False),
    }
    if e_ffi.get("ok") and e_cx and e_cx.get("ok"):
        a = first_output(e_ffi)
        b = first_output(e_cx)
        if a is not None and b is not None and a.shape == b.shape:
            diff = np.abs(a - b)
            abs_err = float(diff.max())
            mean_abs_err = float(diff.mean())
            denom = np.maximum(np.abs(b), 1e-12)
            rel_err = float((diff / denom).max())
            row["max_abs_err"] = abs_err
            row["mean_abs_err"] = mean_abs_err
            row["max_rel_err"] = rel_err
            row["exact_match"] = bool(abs_err == 0.0)
            row["shape_match"] = True
            row["shape_ffi"] = list(a.shape)
            row["shape_caffex"] = list(b.shape)
        else:
            row["max_abs_err"] = None
            row["mean_abs_err"] = None
            row["max_rel_err"] = None
            row["exact_match"] = False
            row["shape_match"] = False
            row["shape_ffi"] = list(a.shape) if a is not None else None
            row["shape_caffex"] = list(b.shape) if b is not None else None
    else:
        row["max_abs_err"] = None
        row["mean_abs_err"] = None
        row["max_rel_err"] = None
        row["exact_match"] = False
        row["shape_match"] = None
        row["error_ffi"] = e_ffi.get("error", "")
        row["error_caffex"] = (e_cx or {}).get("error", "")
    rows.append(row)

# 输出 markdown 表格
print("| 算子 | caffe-ffi | caffex | 最大绝对误差 | 平均绝对误差 | 最大相对误差 | 精确一致 | 形状一致 | FFI耗时(ms) | Caffex耗时(ms) |")
print("|------|-----------|--------|-------------|-------------|-------------|---------|---------|-------------|----------------|")
for r in rows:
    def fmt(v, nd=3):
        return "n/a" if v is None else f"{v:.{nd}e}" if isinstance(v, float) else str(v)
    print(f"| {r['op']} | {'OK' if r['caffe_ffi_ok'] else 'FAIL'} | "
          f"{'OK' if r['caffex_ok'] else 'FAIL'} | "
          f"{fmt(r['max_abs_err'])} | {fmt(r['mean_abs_err'])} | "
          f"{fmt(r['max_rel_err'])} | {'Y' if r['exact_match'] else 'N'} | "
          f"{('Y' if r['shape_match'] else 'N') if r['shape_match'] is not None else 'n/a'} | "
          f"{r['caffe_ffi_ms']:.3f} | {r['caffex_ms']:.3f} |")

# 汇总
ok_cnt = sum(1 for r in rows if r["caffe_ffi_ok"] and r["caffex_ok"])
exact_cnt = sum(1 for r in rows if r.get("exact_match"))
print(f"\n=== 汇总: {len(rows)} 算子, 双实现均通过 {ok_cnt}, 精确一致 {exact_cnt} ===")

# 保存结构化结果
out = os.path.join(RESULT_DIR, "cross_ops_comparison.json")
with open(out, "w") as f:
    json.dump(rows, f, indent=2, ensure_ascii=False)
print(f"对比结果已保存: {out}")