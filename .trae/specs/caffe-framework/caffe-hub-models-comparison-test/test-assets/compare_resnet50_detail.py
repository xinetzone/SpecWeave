"""ResNet50 输出张量详细数值对比。

加载 raw_outputs/caffe_ffi 与 raw_outputs/caffex 的 .npy，
对每个共有 blob 输出详细数值分布统计与 Top-K 预测对比。
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


def load_raw(impl: str, results_dir: Path, model_name: str) -> dict[str, np.ndarray]:
    d = results_dir / "raw_outputs" / impl
    import re

    def _bn(n: str) -> str:
        return re.sub(r"[^A-Za-z0-9_.-]", "_", n)

    out = {}
    for f in d.glob(f"{_bn(model_name)}__*.npy"):
        blob = f.stem.split("__", 1)[1]
        out[blob] = np.load(f, allow_pickle=False).astype(np.float32)
    return out


def summarize(arr: np.ndarray, label: str) -> str:
    a = arr.flatten()
    finite = np.isfinite(a)
    n_nan = int(np.isnan(a).sum())
    n_inf = int(np.isinf(a).sum())
    af = a[finite] if finite.any() else a
    lines = [f"  {label}: shape={arr.shape} size={a.size} dtype={arr.dtype}"]
    lines.append(
        f"    mean={af.mean():.8f}  std={af.std():.8f}  min={af.min():.8f}  max={af.max():.8f}"
    )
    lines.append(f"    nan={n_nan}  inf={n_inf}  finite_ratio={finite.mean():.4f}")
    # distribution
    if af.size > 0:
        for q in [0.0, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 1.0]:
            pass  # keep output concise
        abs_a = np.abs(af)
        lines.append(
            f"    |x| quantiles: 50%={np.quantile(abs_a,0.5):.2e}  90%={np.quantile(abs_a,0.9):.2e}  99%={np.quantile(abs_a,0.99):.2e}  max={abs_a.max():.2e}"
        )
    return "\n".join(lines)


def compare_detail(a: np.ndarray, b: np.ndarray) -> dict:
    a = a.flatten().astype(np.float32)
    b = b.flatten().astype(np.float32)
    diff = a - b
    abs_diff = np.abs(diff)
    denom = np.maximum(np.abs(b), 1e-8)
    rel = abs_diff / denom
    # Worst elements (by abs diff)
    idx = np.argsort(-abs_diff)[:10]
    worst = [(int(i), float(a[i]), float(b[i]), float(diff[i]), float(rel[i])) for i in idx]
    return {
        "max_abs": float(abs_diff.max()),
        "mean_abs": float(abs_diff.mean()),
        "max_rel": float(rel.max()),
        "mean_rel": float(rel.mean()),
        "cos_sim": float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-20)),
        "l2_ratio": float(np.linalg.norm(diff) / (np.linalg.norm(b) + 1e-20)),
        "exact_match_ratio": float((abs_diff < 1e-7).mean()),
        "sign_match_ratio": float((np.sign(a) == np.sign(b)).mean()),
        "worst_10": worst,
    }


def topk(arr: np.ndarray, k: int = 5) -> list[tuple[int, float]]:
    a = arr.flatten()
    idx = np.argsort(-a)[:k]
    return [(int(i), float(a[i])) for i in idx]


def main(results_dir: str, model_name: str = "resnet50_caffe") -> None:
    d = Path(results_dir)
    ffi = load_raw("caffe_ffi", d, model_name)
    cx = load_raw("caffex", d, model_name)

    print("=" * 80)
    print(f"ResNet50 原始输出张量对比（{model_name}）")
    print("=" * 80)
    print(f"\ncaffe-ffi blobs ({len(ffi)}): {sorted(ffi)}")
    print(f"caffex   blobs ({len(cx)}): {sorted(cx)}")

    common = sorted(set(ffi) & set(cx))
    only_ffi = sorted(set(ffi) - set(cx))
    only_cx = sorted(set(cx) - set(ffi))
    if only_ffi:
        print(f"\n⚠️  仅 caffe-ffi 输出: {only_ffi}")
    if only_cx:
        print(f"\n⚠️  仅 caffex 输出: {only_cx}")

    for blob in common:
        print(f"\n{'─'*80}")
        print(f"BLOB: {blob}")
        print(summarize(ffi[blob], "caffe-ffi"))
        print(summarize(cx[blob], "caffex  "))

        if ffi[blob].shape != cx[blob].shape:
            print(f"  ❌ 形状不匹配: {ffi[blob].shape} vs {cx[blob].shape}")
            continue

        cmp = compare_detail(ffi[blob], cx[blob])
        print(f"\n  差异统计:")
        print(f"    max_abs_error  = {cmp['max_abs']:.6e}")
        print(f"    mean_abs_error = {cmp['mean_abs']:.6e}")
        print(f"    max_rel_error  = {cmp['max_rel']:.6e}")
        print(f"    mean_rel_error = {cmp['mean_rel']:.6e}")
        print(f"    cos_similarity = {cmp['cos_sim']:.10f}")
        print(f"    relative L2    = {cmp['l2_ratio']:.6e}")
        print(f"    exact_match(<1e-7) ratio = {cmp['exact_match_ratio']:.4%}")
        print(f"    sign_match_ratio        = {cmp['sign_match_ratio']:.4%}")

        # Top-K for class-probability outputs
        if blob in ("prob",) or ffi[blob].shape[-1] >= 100:
            print(f"\n  Top-5 预测（caffe-ffi）:")
            for rank, (idx, val) in enumerate(topk(ffi[blob], 5), 1):
                print(f"    #{rank}: class={idx:4d}  prob={val:.6f}")
            print(f"  Top-5 预测（caffex）:")
            for rank, (idx, val) in enumerate(topk(cx[blob], 5), 1):
                print(f"    #{rank}: class={idx:4d}  prob={val:.6f}")

            # Top-K agreement
            tk = 5
            ffi_topk = {i for i, _ in topk(ffi[blob], tk)}
            cx_topk = {i for i, _ in topk(cx[blob], tk)}
            agree = len(ffi_topk & cx_topk)
            print(f"\n  Top-{tk} 一致: {agree}/{tk}")

        print(f"\n  差异最大的 10 个元素 (index, ffi, caffex, diff, rel_err):")
        for i, fa, ca, df, rl in cmp["worst_10"]:
            print(f"    [{i:>6d}] ffi={fa: .8f}  cx={ca: .8f}  Δ={df:+.2e}  rel={rl:.2e}")


if __name__ == "__main__":
    rd = sys.argv[1] if len(sys.argv) > 1 else "results"
    mn = sys.argv[2] if len(sys.argv) > 2 else "resnet50_caffe"
    main(rd, mn)
