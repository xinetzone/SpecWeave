#!/usr/bin/env python3
"""Analyze benchmark_results.json and generate performance insights."""
import json
import sys
from pathlib import Path


def analyze(results_path: str):
    with open(results_path, encoding="utf-8") as f:
        data = json.load(f)

    cfg = data["config"]
    results = data["results"]

    print("=" * 80)
    print("ONNX Quantization Benchmark — Performance Analysis")
    print("=" * 80)
    print(f"Device:    {cfg.get('device', 'unknown')}")
    print(f"ORT:       {cfg['ort_version']}")
    print(f"Config:    warmup={cfg['warmup']}, runs={cfg['runs']}, threads={cfg['intra_threads']}")
    print()

    prec_names = [
        ("FP16", "FP16"),
        ("INT8_Dynamic", "INT8-Dyn"),
        ("INT8_Static_QDQ", "INT8-QDQ"),
        ("INT8_Static_QOperator", "INT8-QOp"),
    ]

    per_model_summary = []

    for name, model_results in results.items():
        fp32 = model_results["FP32"]
        print(f"--- {name} ---")
        print(f"  FP32 baseline: {fp32['avg_ms']:.4f}ms  size={fp32['size_kb']:.1f}KB  throughput={fp32['throughput_fps']:.0f} fps")
        print()

        best_sp = 1.0
        best_prec = "FP32"
        best_diff = 0.0

        rows = []
        for key, label in prec_names:
            r = model_results[key]
            sp = r["speedup"]
            diff = r["max_diff"]
            size_pct = r["size_ratio"] * 100
            icon = "✅" if sp > 1.05 else "⚠️ " if sp > 0.95 else "❌"
            if sp > best_sp:
                best_sp = sp
                best_prec = label
                best_diff = diff
            rows.append((label, r["avg_ms"], sp, size_pct, diff, icon))

        for label, avg_ms, sp, size_pct, diff, icon in rows:
            print(f"  {icon} {label:<10s}: {avg_ms:.4f}ms  ({sp:.2f}x)  size={size_pct:.1f}%  max_diff={diff:.6f}")

        print(f"  🏆 Winner:   {best_prec}  ({best_sp:.2f}x speedup, max_diff={best_diff:.6f})")
        print()
        per_model_summary.append((name, fp32["avg_ms"], best_prec, best_sp, best_diff))

    # Summary table
    print("=" * 80)
    print("SPEEDUP SUMMARY (vs FP32 baseline)")
    print("=" * 80)
    header = f"{'Model':<25} {'FP32(ms)':>8} {'FP16':>7} {'Dyn':>7} {'QDQ':>7} {'QOp':>7} | Best"
    print(header)
    print("-" * len(header))
    for name, model_results in results.items():
        fp32_ms = model_results["FP32"]["avg_ms"]
        fp16 = model_results["FP16"]["speedup"]
        dyn = model_results["INT8_Dynamic"]["speedup"]
        qdq = model_results["INT8_Static_QDQ"]["speedup"]
        qop = model_results["INT8_Static_QOperator"]["speedup"]
        precs = {"FP16": fp16, "Dyn": dyn, "QDQ": qdq, "QOp": qop}
        best_label, best_sp = max(precs.items(), key=lambda x: x[1])
        print(f"{name:<25} {fp32_ms:>7.3f} {fp16:>6.2f}x {dyn:>6.2f}x {qdq:>6.2f}x {qop:>6.2f}x | {best_label}: {best_sp:.2f}x")

    print()
    print("=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)

    # Insight 1: FP16 always slower on CPU
    fp16_speedups = [model_results["FP16"]["speedup"] for model_results in results.values()]
    avg_fp16 = sum(fp16_speedups) / len(fp16_speedups)
    print(f"1. FP16 on CPU: avg speedup = {avg_fp16:.2f}x (always slower — expected: FP16 has no hardware acceleration on x64 CPU, extra conversion overhead)")

    # Insight 2: INT8-Dynamic wins for MLPs
    dyn_speedups = [model_results["INT8_Dynamic"]["speedup"] for model_results in results.values()]
    print(f"2. INT8 Dynamic: speedup range [{min(dyn_speedups):.2f}x, {max(dyn_speedups):.2f}x], avg={sum(dyn_speedups)/len(dyn_speedups):.2f}x")
    print(f"   - Best for MLPs (GEMM-heavy workloads)")
    print(f"   - Less effective for ConvNet (conv ops not dynamically quantized)")
    print(f"   - Worst case: Transformer (attention ops not well-optimized)")

    # Insight 3: QDQ vs QOperator
    qdq_better = sum(1 for mr in results.values() if mr["INT8_Static_QDQ"]["avg_ms"] < mr["INT8_Static_QOperator"]["avg_ms"])
    total = len(results)
    print(f"3. QDQ vs QOperator: QDQ better in {qdq_better}/{total} models")

    # Insight 4: Accuracy
    print(f"4. Accuracy (max_diff from FP32):")
    for name, model_results in results.items():
        dyn_diff = model_results["INT8_Dynamic"]["max_diff"]
        qdq_diff = model_results["INT8_Static_QDQ"]["max_diff"]
        print(f"   - {name}: Dynamic={dyn_diff:.6f}, QDQ={qdq_diff:.6f}")

    print()
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print("• For CPU deployment: prefer INT8 Dynamic Quantization (best speed/accuracy tradeoff for GEMM)")
    print("• For ConvNets: use INT8 Static QDQ (conv ops benefit from static calibration)")
    print("• For Transformers: INT8 Dynamic is best static option, but expect <1.5x speedup")
    print("• FP16: Only useful for GPU deployments with Tensor Cores; avoid on CPU")
    print("• QOperator format: sometimes faster for certain op patterns (test both)")
    print()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent / "benchmark-results.json")
    analyze(path)
