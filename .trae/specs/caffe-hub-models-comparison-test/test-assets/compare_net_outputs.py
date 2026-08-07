"""跨实现网络级精度对比（Task 6 / FR-4 + FR-5）。

加载 caffe_ffi 与 caffex 两实现的 raw_outputs/<impl>/ 原始输出 .npy，
对每个两实现均成功的模型计算逐输出 blob 的精度指标，并生成逐模型判定与 A-001 证据。

用法: python compare_net_outputs.py <results_dir> [--out net_comparison.json]
- <results_dir> 为含 caffe_ffi_net_results.json / caffex_net_results.json 及 raw_outputs/ 的目录。
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

import numpy as np

RAW_SUBDIR = "raw_outputs"
TOP_K = 5


def _bn(name: str) -> str:
    """Normalize a blob-name for cross-impl matching (strip unsafe chars)."""
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(name))


def load_results(results_dir: Path) -> dict[str, dict]:
    """Load impl -> model-name -> result record."""
    out = {}
    for impl, fname in (("caffe_ffi", "caffe_ffi_net_results.json"), ("caffex", "caffex_net_results.json")):
        p = results_dir / fname
        if not p.exists():
            out[impl] = {}
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        out[impl] = {r["name"]: r for r in data["results"]}
    return out


def load_raw(impl: str, results_dir: Path, model_name: str) -> dict[str, np.ndarray]:
    """Load all raw output .npy for a model+impl. Returns {blob_name: array}."""
    d = results_dir / RAW_SUBDIR / impl
    if not d.exists():
        return {}
    out = {}
    for f in d.glob(f"{_bn(model_name)}__*.npy"):
        parts = f.stem.split("__", 1)
        if len(parts) != 2:
            continue
        blob = parts[1]
        try:
            out[blob] = np.load(f, allow_pickle=False)
        except Exception as e:  # noqa: BLE001
            out[blob + "!!ERR"] = np.zeros(0, dtype=np.float32)
    return out


def compare_blob(a: np.ndarray, b: np.ndarray) -> dict:
    """Compare two arrays; returns error metrics or shape-mismatch flag."""
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    if a.shape != b.shape:
        return {
            "shape_match": False,
            "shape_a": list(a.shape),
            "shape_b": list(b.shape),
            "max_abs_error": None,
            "mean_abs_error": None,
            "max_rel_error": None,
            "topk_agree": None,
        }
    diff = a - b
    abs_diff = np.abs(diff)
    # relative error denominator: max(|a|, 1e-8)
    denom = np.maximum(np.abs(a), 1e-8)
    rel = abs_diff / denom
    # Top-K agreement (only meaningful for 1-D / 2-D class-like outputs)
    topk_agree = None
    if a.ndim == 1 or (a.ndim == 2 and a.shape[0] == 1):
        k = min(TOP_K, a.shape[-1])
        if k > 0:
            ai = np.argsort(a)[-k:]
            bi = np.argsort(b)[-k:]
            topk_agree = int(np.intersect1d(ai, bi).size)
    return {
        "shape_match": True,
        "shape": list(a.shape),
        "max_abs_error": float(abs_diff.max()) if abs_diff.size else None,
        "mean_abs_error": float(abs_diff.mean()) if abs_diff.size else None,
        "max_rel_error": float(rel.max()) if rel.size else None,
        "topk_agree": topk_agree,
    }


VERDICT_RULES = {
    "shape_mismatch": lambda r: r.get("shape_match") is False,
    "nan_or_inf": lambda r: (r.get("has_nan") or r.get("has_inf")),
    "consistent": lambda r: r.get("max_abs_error") is not None and r["max_abs_error"] < 1e-3,
    "near": lambda r: r.get("max_abs_error") is not None and r["max_abs_error"] < 1e-1,
    "divergent": lambda r: r.get("max_abs_error") is not None,
}


def verdict_for(blob_metrics: list[dict]) -> str:
    """Derive a per-model verdict from the worst blob."""
    if not blob_metrics:
        return "no_outputs"
    worst = max(blob_metrics, key=lambda r: r.get("max_abs_error") or 0)
    if worst.get("shape_match") is False:
        return "shape_mismatch"
    if worst.get("has_nan") or worst.get("has_inf"):
        return "nan_or_inf"
    err = worst.get("max_abs_error")
    if err is None:
        return "unknown"
    if err < 1e-3:
        return "consistent"  # 同一输入/权重下浮点级一致
    if err < 1e-1:
        return "near"  # 量级接近但非精确一致
    return "divergent"  # 明显不一致（可能输入/权重/拓扑差异）


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("results_dir", help="目录含两实现 results JSON 与 raw_outputs/")
    ap.add_argument("--out", default="net_comparison.json")
    args = ap.parse_args()

    results_dir = Path(args.results_dir)
    res = load_results(results_dir)

    ffi = res["caffe_ffi"]
    caffex = res["caffex"]
    all_names = sorted(set(ffi) | set(caffex))

    comparison = {
        "impl_ffi": "caffe_ffi",
        "impl_caffex": "caffex",
        "models": [],
        "summary": {},
    }
    model_records = []
    stats = {"both_ok": 0, "ffi_ok_caffex_fail": 0, "caffex_ok_ffi_fail": 0, "both_fail": 0}
    verdict_counts: dict[str, int] = {}

    for name in all_names:
        r_ffi = ffi.get(name)
        r_caffex = caffex.get(name)
        s_ffi = r_ffi["status"] if r_ffi else "missing"
        s_caffex = r_caffex["status"] if r_caffex else "missing"

        rec = {
            "name": name,
            "status_ffi": s_ffi,
            "status_caffex": s_caffex,
            "verdict": None,
            "blob_errors": {},
        }

        if s_ffi == "ok" and s_caffex == "ok":
            stats["both_ok"] += 1
            raw_ffi = load_raw("caffe_ffi", results_dir, name)
            raw_cx = load_raw("caffex", results_dir, name)
            common = sorted(set(raw_ffi) & set(raw_cx))
            blob_metrics = []
            for blob in common:
                if blob.endswith("!!ERR"):
                    continue
                m = compare_blob(raw_ffi[blob], raw_cx[blob])
                # fold in finite checks
                fa = np.asarray(raw_ffi[blob], dtype=np.float32)
                fb = np.asarray(raw_cx[blob], dtype=np.float32)
                m["has_nan"] = bool(np.isnan(fa).any() or np.isnan(fb).any())
                m["has_inf"] = bool(np.isinf(fa).any() or np.isinf(fb).any())
                # only keep blobs actually present in both (avoid !!ERR keys)
                rec["blob_errors"][blob] = m
                blob_metrics.append(m)
            rec["verdict"] = verdict_for(blob_metrics)
            verdict_counts[rec["verdict"]] = verdict_counts.get(rec["verdict"], 0) + 1
        elif s_ffi == "ok" and s_caffex != "ok":
            stats["ffi_ok_caffex_fail"] += 1
            rec["verdict"] = "ffi_ok_caffex_fail"
        elif s_ffi != "ok" and s_caffex == "ok":
            stats["caffex_ok_ffi_fail"] += 1
            rec["verdict"] = "caffex_ok_ffi_fail"
        else:
            stats["both_fail"] += 1
            rec["verdict"] = "both_fail"

        model_records.append(rec)

    comparison["models"] = model_records
    comparison["summary"] = {
        "total": len(all_names),
        **stats,
        "verdict_counts": verdict_counts,
        "a001_evidence": a001_evidence(ffi, caffex),
    }

    with open(results_dir / args.out, "w", encoding="utf-8") as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)

    print(f"total={comparison['summary']['total']} both_ok={stats['both_ok']}")
    print(f"verdicts={verdict_counts}")
    print(f"a001={comparison['summary']['a001_evidence']}")
    print(f"written: {results_dir / args.out}")


def a001_evidence(ffi: dict, caffex: dict) -> dict:
    """A-001 权重加载缺陷在真实模型上的判定证据。

    A-001 指 read_net 未加载真实权重导致输出 NaN/占位。判定：
    - 若正常加载模型权重，conv1 权重 std 应非零、输出有限；
    - 若 A-001 仍存在，则 conv1 权重为占位（std≈0 或偏离真实值）且输出 NaN。
    """
    r = ffi.get("resnet50_caffe")
    if not r or r.get("status") != "ok":
        return {"status": "unknown", "reason": "resnet50_caffe not ok in ffi"}
    d = r.get("detail", {})
    w = d.get("first_conv_weight") or {}
    outs = d.get("outputs", {}) or {}
    any_nan = any(o.get("has_nan") or o.get("has_inf") for o in outs.values())
    std = w.get("std")
    size = w.get("size")
    # 真实权重 std 应远离 0；输出应有限
    fixed = (std is not None and std > 1e-4 and size and size > 0) and not any_nan
    return {
        "status": "fixed" if fixed else "still_present",
        "conv1_std": std,
        "conv1_size": size,
        "output_nan_or_inf": any_nan,
        "evidence": "conv1 权重非占位(std>1e-4)且输出有限 => A-001 已修复" if fixed
        else "conv1 权重缺失或输出含 NaN/Inf => A-001 仍存在",
        "model": "resnet50_caffe",
    }


if __name__ == "__main__":
    main()