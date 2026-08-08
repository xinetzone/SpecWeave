#!/usr/bin/env python3
"""
CI门禁：ONNX模型量化精度自动检测与回滚

在CI流水线中对FP32 ONNX模型自动执行量化→精度验证→自动回滚：
1. 自动检测模型类型（MLP/CNN/Transformer/RNN）
2. 按推荐策略量化（静态QDQ/QOperator/动态/FP16）
3. 精度验证（max_diff/cosine_sim/加速比三重门禁）
4. 精度不达标时自动回滚到安全策略
5. 所有策略均失败时返回非零退出码，阻断CI

用法:
  # 基本用法（自动检测+自动量化+自动回滚）
  python ci_quantization_gate.py --model model.onnx --output model_int8.onnx

  # 指定校准数据目录
  python ci_quantization_gate.py -m model.onnx -o model_int8.onnx -d ./calib_data/

  # 严格精度阈值（适用于分类/回归任务）
  python ci_quantization_gate.py -m model.onnx -o model_int8.onnx --strict

  # CI模式（输出JSON报告，非零退出码阻断流水线）
  python ci_quantization_gate.py -m model.onnx -o model_int8.onnx --report report.json --ci

  # 指定输入形状和名称（多输入模型需手动指定）
  python ci_quantization_gate.py -m model.onnx -o model_int8.onnx -s 1,3,224,224 -n input

退出码:
  0: 量化成功（含回退后成功）
  1: 所有量化策略均失败
  2: 参数错误
  3: 输入文件不存在

CI集成示例（GitHub Actions）:
  - name: Quantize ONNX Model
    run: |
      python scripts/ci_quantization_gate.py \
        --model artifacts/model.onnx \
        --output artifacts/model_int8.onnx \
        --calib-dir calib_data/ \
        --report artifacts/quant-report.json \
        --ci
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

# 将scripts目录加入sys.path，方便导入工具包
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from onnx_quantize_kit import (
    auto_quantize, QuantizationConfig, AccuracyThresholds,
    FileCalibrationReader, RandomCalibrationReader,
    detect_model_type, ModelType,
    build_report,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="CI门禁：ONNX模型量化精度自动检测与回滚",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("-m", "--model", required=True, help="FP32 ONNX模型路径")
    parser.add_argument("-o", "--output", required=True, help="量化输出模型路径")
    parser.add_argument("-s", "--input-shape", default=None,
                        help="输入形状，逗号分隔 (如 1,3,224,224)，默认自动检测")
    parser.add_argument("-n", "--input-name", default=None,
                        help="输入节点名，默认自动检测")
    parser.add_argument("-d", "--calib-dir", default=None,
                        help="校准数据目录(.npy文件)，不指定则用随机数据（仅流程验证）")
    parser.add_argument("-c", "--calib-samples", type=int, default=100,
                        help="校准样本数 (默认100)")
    parser.add_argument("--strategy", default="auto",
                        choices=["auto", "static_qdq", "static_qoperator",
                                 "dynamic", "fp16"],
                        help="量化策略 (默认auto自动选择)")
    parser.add_argument("--strict", action="store_true",
                        help="使用严格精度阈值（max_diff<0.02, cosine>0.999）")
    parser.add_argument("--relaxed", action="store_true",
                        help="使用宽松精度阈值（max_diff<0.1, cosine>0.95）")
    parser.add_argument("--max-diff", type=float, default=None,
                        help="自定义max_diff阈值（覆盖默认/严格/宽松）")
    parser.add_argument("--min-speedup", type=float, default=None,
                        help="最低加速比要求（默认1.0x，低于则拒绝量化）")
    parser.add_argument("-t", "--threads", type=int, default=4,
                        help="intra_op线程数 (默认4)")
    parser.add_argument("-w", "--warmup", type=int, default=50,
                        help="预热次数 (默认50)")
    parser.add_argument("-r", "--runs", type=int, default=200,
                        help="性能测量次数 (默认200)")
    parser.add_argument("--exclude-nodes", nargs="*", default=None,
                        help="排除量化的节点名称列表")
    parser.add_argument("--report", default=None,
                        help="JSON报告输出路径")
    parser.add_argument("--ci", action="store_true",
                        help="CI模式：精简输出，非零退出码阻断流水线")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="详细输出")

    return parser.parse_args()


def main():
    args = parse_args()

    # 检查输入文件
    if not os.path.isfile(args.model):
        print(f"[CI-GATE] ❌ Model not found: {args.model}", file=sys.stderr)
        return 3

    # 解析输入形状
    input_shape = None
    if args.input_shape:
        input_shape = tuple(int(x) for x in args.input_shape.split(","))

    # 精度阈值
    if args.max_diff is not None:
        thresholds = AccuracyThresholds(
            acceptable_max_diff=args.max_diff,
            excellent_max_diff=args.max_diff / 5,
            min_cosine_sim=0.99,
            min_speedup=args.min_speedup or 1.0,
        )
    elif args.strict:
        thresholds = AccuracyThresholds.strict()
        if args.min_speedup:
            thresholds.min_speedup = args.min_speedup
    elif args.relaxed:
        thresholds = AccuracyThresholds.relaxed()
        if args.min_speedup:
            thresholds.min_speedup = args.min_speedup
    else:
        thresholds = AccuracyThresholds()
        if args.min_speedup:
            thresholds.min_speedup = args.min_speedup

    # 校准数据Reader
    input_name_for_calib = args.input_name or "input"
    shape_for_calib = input_shape or (1, 3, 224, 224)
    if args.calib_dir and os.path.isdir(args.calib_dir):
        calib_reader = FileCalibrationReader(
            input_name=input_name_for_calib,
            input_shape=shape_for_calib,
            calib_dir=args.calib_dir,
            num_samples=args.calib_samples,
        )
    else:
        if not args.ci:
            print("[CI-GATE] ⚠️  No calibration data provided, using random data. "
                  "This is for pipeline validation only; use --calib-dir for production.")
        calib_reader = RandomCalibrationReader(
            input_name=input_name_for_calib,
            input_shape=shape_for_calib,
            num_samples=args.calib_samples,
        )

    # 量化配置
    config = QuantizationConfig(
        strategy=args.strategy,
        intra_threads=args.threads,
        warmup=args.warmup,
        runs=args.runs,
        auto_fallback=True,
        exclude_nodes=args.exclude_nodes,
        thresholds=thresholds,
        num_calib_samples=args.calib_samples,
    )

    # 执行自动量化（含回滚）
    t0 = time.perf_counter()
    if not args.ci or args.verbose:
        print("=" * 70)
        print("CI Quantization Gate")
        print("=" * 70)
        print(f"  Model:     {args.model}")
        print(f"  Output:    {args.output}")
        print(f"  Strategy:  {args.strategy}")
        print(f"  Thresholds: max_diff<{thresholds.acceptable_max_diff}, "
              f"cos_sim>{thresholds.min_cosine_sim}, "
              f"speedup>{thresholds.min_speedup}x")
        print("=" * 70)

    result = auto_quantize(
        model_path=args.model,
        output_path=args.output,
        calib_reader=calib_reader,
        input_shape=input_shape,
        input_name=args.input_name,
        config=config,
        verbose=not args.ci or args.verbose,
    )

    elapsed = time.perf_counter() - t0

    # 构建CI报告（使用统一的reporting模块）
    report = build_report(result, thresholds, elapsed, args.model)

    # 输出报告
    if args.report:
        os.makedirs(os.path.dirname(os.path.abspath(args.report)) or ".", exist_ok=True)
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        if not args.ci or args.verbose:
            print(f"\n[CI-GATE] Report saved to: {args.report}")

    # CI模式输出
    if args.ci:
        print(json.dumps(report, ensure_ascii=False))
    else:
        print("\n" + "=" * 70)
        if result.success:
            print(f"[CI-GATE] ✅ PASS - {result.strategy_used}")
            print(f"  Speedup:   {result.speedup:.2f}x")
            print(f"  Size:      {result.size_ratio:.1%} of FP32")
            if result.accuracy:
                level_emoji = {"excellent": "🟢", "acceptable": "🟡", "unacceptable": "🔴"}
                emoji = level_emoji.get(result.accuracy.level, "❓")
                print(f"  Accuracy:  {emoji} max_diff={result.accuracy.max_diff:.6f} "
                      f"cos_sim={result.accuracy.cosine_sim_min:.6f}")
            if result.fallback_triggered:
                print(f"  ⚠️  Fallback triggered: {result.fallback_reason}")
        else:
            print(f"[CI-GATE] ❌ FAIL - All strategies exhausted")
            if result.error:
                print(f"  Error: {result.error}")
        print(f"  Elapsed: {elapsed:.1f}s")
        print("=" * 70)

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
