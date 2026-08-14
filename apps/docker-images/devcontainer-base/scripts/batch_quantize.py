#!/usr/bin/env python3
"""
batch_quantize.py — 批量模型量化工具

对目录中的多个 ONNX 模型执行自动量化（含自动回滚），生成汇总报告。

用法:
  # 量化目录中所有 .onnx 文件
  python batch_quantize.py ./models/ -o ./quantized/

  # 使用 glob 模式
  python batch_quantize.py "./models/*.onnx" -o ./quantized/

  # 指定多个模型
  python batch_quantize.py model1.onnx model2.onnx model3.onnx -o ./out/

  # 严格模式 + 指定校准数据目录
  python batch_quantize.py ./models/ -o ./out/ --strict --calib-dir ./calib/

  # 宽松模式 + 并发处理
  python batch_quantize.py ./models/ -o ./out/ --relaxed -j 4

  # 仅列出将处理的模型（dry-run）
  python batch_quantize.py ./models/ -o ./out/ --dry-run

  # 生成 JSON 批量报告
  python batch_quantize.py ./models/ -o ./out/ --report batch_report.json
"""
import argparse
import glob
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from onnx_quantize_kit import (
    auto_quantize, QuantizationConfig, AccuracyThresholds,
    FileCalibrationReader, RandomCalibrationReader,
    detect_model_type,
)
from onnx_quantize_kit.quantize import _safe_get_input_shape
from onnx_quantize_kit.benchmark import create_session
from onnx_quantize_kit.reporting import (
    build_report, parse_report, format_summary,
    format_strategy_chain, format_batch_summary,
)


def find_models(paths: List[str], recursive: bool = False) -> List[str]:
    """从路径列表中发现 .onnx 模型文件。

    支持：
    - 具体文件路径
    - 目录路径（扫描目录下 .onnx 文件）
    - glob 通配符模式
    """
    models = []
    for p in paths:
        if os.path.isfile(p) and p.endswith(".onnx"):
            models.append(os.path.abspath(p))
        elif os.path.isdir(p):
            pattern = os.path.join(p, "**/*.onnx" if recursive else "*.onnx")
            models.extend(sorted(glob.glob(pattern, recursive=recursive)))
        elif any(c in p for c in "*?[]"):
            models.extend(sorted(glob.glob(p, recursive=recursive)))
        else:
            print(f"[WARN] Skipping invalid path: {p}", file=sys.stderr)
    # 去重
    seen = set()
    unique = []
    for m in models:
        ap = os.path.abspath(m)
        if ap not in seen:
            seen.add(ap)
            unique.append(ap)
    return unique


def quantize_single(
    model_path: str,
    output_dir: str,
    suffix: str,
    config: QuantizationConfig,
    thresholds: AccuracyThresholds,
    calib_dir: Optional[str] = None,
    input_shape: Optional[tuple] = None,
    input_name: Optional[str] = None,
    verbose: bool = False,
) -> dict:
    """量化单个模型，返回报告 dict（失败也返回不抛异常）。"""
    model_name = os.path.basename(model_path)
    base = os.path.splitext(model_name)[0]
    output_path = os.path.join(output_dir, f"{base}{suffix}.onnx")

    # 自动检测输入形状/名称
    shape_for_calib = input_shape
    name_for_calib = input_name
    if shape_for_calib is None or name_for_calib is None:
        try:
            sess = create_session(model_path, config.intra_threads)
            inp = sess.get_inputs()[0]
            name_for_calib = name_for_calib or inp.name
            if shape_for_calib is None:
                shape_for_calib = _safe_get_input_shape(inp)
            del sess
        except Exception as e:
            if verbose:
                print(f"  [WARN] Auto-detect input failed for {model_name}: {e}")
            shape_for_calib = shape_for_calib or (1, 3, 224, 224)
            name_for_calib = name_for_calib or "input"

    # 校准数据
    if calib_dir and os.path.isdir(calib_dir):
        # 尝试模型专用校准目录（calib_dir/model_name/）
        model_calib = os.path.join(calib_dir, base)
        actual_calib = model_calib if os.path.isdir(model_calib) else calib_dir
        calib_reader = FileCalibrationReader(
            input_name=name_for_calib,
            input_shape=shape_for_calib,
            calib_dir=actual_calib,
            num_samples=config.num_calib_samples,
        )
    else:
        calib_reader = RandomCalibrationReader(
            input_name=name_for_calib,
            input_shape=shape_for_calib,
            num_samples=config.num_calib_samples,
        )

    t0 = time.perf_counter()
    try:
        result = auto_quantize(
            model_path=model_path,
            output_path=output_path,
            calib_reader=calib_reader,
            input_shape=input_shape,
            input_name=input_name,
            config=config,
            verbose=verbose,
        )
        elapsed = time.perf_counter() - t0
        report = build_report(result, thresholds, elapsed, model_path)
        return report
    except Exception as e:
        elapsed = time.perf_counter() - t0
        return {
            "status": "FAIL",
            "model": model_name,
            "model_path": model_path,
            "output": output_path,
            "strategy_used": "",
            "error": str(e),
            "elapsed_seconds": round(elapsed, 2),
            "all_attempts": [],
            "speedup": 0,
            "size_ratio": 0,
            "fallback_triggered": False,
            "fallback_reason": "",
        }


def main():
    parser = argparse.ArgumentParser(
        description="批量ONNX模型量化工具（自动检测+自动回滚+汇总报告）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("inputs", nargs="+",
                        help="模型文件路径、目录或glob模式（支持多个）")
    parser.add_argument("-o", "--output-dir", required=True,
                        help="量化输出目录")
    parser.add_argument("--suffix", default="_quantized",
                        help="输出文件后缀（默认: _quantized）")
    parser.add_argument("-R", "--recursive", action="store_true",
                        help="递归扫描子目录中的 .onnx 文件")
    parser.add_argument("--strategy", default="auto",
                        choices=["auto", "static_qdq", "static_qoperator", "dynamic", "fp16"],
                        help="量化策略 (默认auto)")
    parser.add_argument("-d", "--calib-dir", default=None,
                        help="校准数据根目录（支持模型专用子目录: <calib_dir>/<model_basename>/）")
    parser.add_argument("-c", "--calib-samples", type=int, default=100,
                        help="校准样本数 (默认100)")
    parser.add_argument("-s", "--input-shape", default=None,
                        help="输入形状，逗号分隔 (默认自动检测)")
    parser.add_argument("-n", "--input-name", default=None,
                        help="输入节点名 (默认自动检测)")
    parser.add_argument("--strict", action="store_true",
                        help="严格精度阈值")
    parser.add_argument("--relaxed", action="store_true",
                        help="宽松精度阈值")
    parser.add_argument("--max-diff", type=float, default=None,
                        help="自定义max_diff阈值")
    parser.add_argument("-t", "--threads", type=int, default=4,
                        help="推理线程数 (默认4)")
    parser.add_argument("-w", "--warmup", type=int, default=20,
                        help="预热次数 (默认20)")
    parser.add_argument("--runs", type=int, default=100,
                        help="性能测量次数 (默认100)")
    parser.add_argument("-j", "--jobs", type=int, default=1,
                        help="并发量化线程数 (默认1，设为0使用CPU核心数)")
    parser.add_argument("--report", default=None,
                        help="批量JSON报告输出路径")
    parser.add_argument("--per-model-reports", action="store_true",
                        help="为每个模型生成单独的 JSON 报告（输出到输出目录）")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅列出待处理模型，不执行量化")
    parser.add_argument("--no-color", action="store_true",
                        help="禁用彩色输出")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="详细输出")

    args = parser.parse_args()

    if args.no_color:
        os.environ["NO_COLOR"] = "1"

    # 发现模型
    models = find_models(args.inputs, recursive=args.recursive)
    if not models:
        print("[BATCH] ❌ No .onnx models found.", file=sys.stderr)
        return 2

    print(f"[BATCH] Found {len(models)} model(s) to process:")
    for m in models:
        print(f"  - {os.path.relpath(m)}")
    print()

    if args.dry_run:
        print("[BATCH] 🔍 Dry run mode - no quantization performed.")
        return 0

    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)

    # 精度阈值
    if args.max_diff is not None:
        thresholds = AccuracyThresholds(
            acceptable_max_diff=args.max_diff,
            excellent_max_diff=args.max_diff / 5,
            min_cosine_sim=0.99,
            min_speedup=0.0,
        )
    elif args.strict:
        thresholds = AccuracyThresholds.strict()
    elif args.relaxed:
        thresholds = AccuracyThresholds.relaxed()
    else:
        thresholds = AccuracyThresholds()
        thresholds.min_speedup = 0.0  # 批量模式默认不拒绝小模型

    # 输入形状
    input_shape = None
    if args.input_shape:
        input_shape = tuple(int(x) for x in args.input_shape.split(","))

    # 量化配置
    config = QuantizationConfig(
        strategy=args.strategy,
        intra_threads=args.threads,
        warmup=args.warmup,
        runs=args.runs,
        auto_fallback=True,
        thresholds=thresholds,
        num_calib_samples=args.calib_samples,
    )

    # 并发数
    jobs = args.jobs
    if jobs == 0:
        jobs = os.cpu_count() or 1
    jobs = min(jobs, len(models))

    # 执行量化
    reports = []
    t_start = time.perf_counter()

    if jobs == 1:
        # 串行执行
        for i, model_path in enumerate(models, 1):
            name = os.path.basename(model_path)
            print(f"[{i}/{len(models)}] Processing: {name} ...", flush=True)
            r = quantize_single(
                model_path, args.output_dir, args.suffix,
                config, thresholds, args.calib_dir,
                input_shape, args.input_name, args.verbose,
            )
            reports.append(r)
            status_icon = "✅" if r["status"] == "PASS" else "❌"
            print(f"  {status_icon} {r.get('strategy_used', 'N/A')}  "
                  f"speedup={r.get('speedup', 0):.2f}x  "
                  f"max_diff={r.get('accuracy', {}).get('max_diff', 'N/A')}")
            if args.per_model_reports:
                per_path = os.path.join(args.output_dir,
                                        f"{os.path.splitext(name)[0]}_report.json")
                with open(per_path, "w", encoding="utf-8") as f:
                    json.dump(r, f, indent=2, ensure_ascii=False)
    else:
        # 并发执行
        print(f"[BATCH] Running with {jobs} concurrent workers ...")
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            futures = {}
            for i, model_path in enumerate(models, 1):
                fut = pool.submit(
                    quantize_single,
                    model_path, args.output_dir, args.suffix,
                    config, thresholds, args.calib_dir,
                    input_shape, args.input_name, False,  # 并发时不verbose
                )
                futures[fut] = (i, model_path)

            for fut in as_completed(futures):
                i, model_path = futures[fut]
                name = os.path.basename(model_path)
                try:
                    r = fut.result()
                except Exception as e:
                    r = {"status": "FAIL", "model": name, "error": str(e),
                         "all_attempts": [], "speedup": 0}
                reports.append(r)
                status_icon = "✅" if r["status"] == "PASS" else "❌"
                print(f"  [{i}/{len(models)}] {status_icon} {name}: "
                      f"{r.get('strategy_used', 'N/A')} "
                      f"({r.get('speedup', 0):.2f}x)")
                if args.per_model_reports:
                    per_path = os.path.join(args.output_dir,
                                            f"{os.path.splitext(name)[0]}_report.json")
                    with open(per_path, "w", encoding="utf-8") as f:
                        json.dump(r, f, indent=2, ensure_ascii=False)

    total_elapsed = time.perf_counter() - t_start

    # 按原始顺序排序（并发模式可能乱序）
    path_order = {m: i for i, m in enumerate(models)}
    reports.sort(key=lambda r: path_order.get(r.get("model_path", ""), 999))

    # 输出汇总
    print()
    print(format_batch_summary(reports, color=not args.no_color))
    print(f"  Total elapsed: {total_elapsed:.1f}s")
    print()

    # 输出失败详情
    failed = [r for r in reports if r["status"] == "FAIL"]
    if failed:
        print("Failed models:")
        for r in failed:
            print(f"  ❌ {r['model']}: {r.get('error', 'unknown error')}")
        print()

    # 批量报告
    if args.report:
        batch_report = {
            "batch_summary": {
                "total": len(reports),
                "passed": sum(1 for r in reports if r["status"] == "PASS"),
                "failed": len(failed),
                "elapsed_seconds": round(total_elapsed, 2),
                "config": {
                    "strategy": args.strategy,
                    "thresholds": {
                        "acceptable_max_diff": thresholds.acceptable_max_diff,
                        "min_cosine_sim": thresholds.min_cosine_sim,
                    },
                },
            },
            "models": reports,
        }
        os.makedirs(os.path.dirname(os.path.abspath(args.report)) or ".", exist_ok=True)
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(batch_report, f, indent=2, ensure_ascii=False)
        print(f"[BATCH] Report saved to: {args.report}")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
