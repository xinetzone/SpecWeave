"""
onnx_quantize_kit.cli — 本地开发一键量化 CLI

专为本地开发场景设计的 ONNX 模型量化工具，特点：
- 彩色输出，直观展示量化过程和回滚链
- 自动检测模型类型，推荐最优策略
- 精度不达标自动回滚，输出完整策略尝试链
- 内置对比视图（FP32 vs 量化后）
- 支持快速预览（--dry-run 不写文件，仅检测+推荐）
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

from . import (
    auto_quantize, QuantizationConfig, AccuracyThresholds,
    FileCalibrationReader, RandomCalibrationReader,
    detect_model_type, ModelType, benchmark_model, analyze_model,
)
from .quantize import _safe_get_input_shape, _build_fallback_chain
from .model_detect import get_recommended_quant_config
from .benchmark import create_session
from .reporting import build_report


# ──── ANSI Colors ────
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


def _supports_color() -> bool:
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(text: str, color: str) -> str:
    if not _supports_color():
        return text
    return f"{color}{text}{C.RESET}"


def _strategy_label(s: str) -> str:
    labels = {
        "static_qdq": _c("Static QDQ (INT8)", C.CYAN),
        "static_qoperator": _c("Static QOp (INT8)", C.CYAN),
        "static_qoperator_quint8": _c("Static QOp/U8 (INT8)", C.CYAN),
        "dynamic": _c("Dynamic (INT8)", C.BLUE),
        "fp16": _c("FP16", C.MAGENTA),
    }
    return labels.get(s, s)


def _model_type_label(t: str) -> str:
    labels = {
        "mlp": _c("MLP (全连接网络)", C.CYAN),
        "cnn": _c("CNN (卷积网络)", C.BLUE),
        "transformer": _c("Transformer (注意力网络)", C.MAGENTA),
        "rnn": _c("RNN/LSTM", C.YELLOW),
        "unknown": _c("Unknown", C.DIM),
    }
    return labels.get(t, t)


def _level_emoji(level: str) -> str:
    return {"excellent": _c("🟢", C.GREEN), "acceptable": _c("🟡", C.YELLOW),
            "unacceptable": _c("🔴", C.RED)}.get(level, "❓")


def _print_banner():
    print()
    print(_c("╔══════════════════════════════════════════════════════════════╗", C.CYAN))
    print(_c("║", C.CYAN) + _c("           ONNX Quantize  —  本地开发一键量化工具            ", C.BOLD) + _c("║", C.CYAN))
    print(_c("╚══════════════════════════════════════════════════════════════╝", C.CYAN))
    print()


def _print_model_info(model_path: str):
    """打印模型基本信息，返回检测到的模型类型"""
    import onnx

    print(_c("── Model Info ──────────────────────────────────────────────", C.DIM))
    model = onnx.load(model_path)
    file_size = os.path.getsize(model_path) / 1024

    print(f"  Path:      {_c(model_path, C.WHITE)}")
    print(f"  Size:      {file_size:.1f} KB")
    print(f"  Opset:     {model.opset_import[0].version}")
    print(f"  IR Ver:    {model.ir_version}")

    mtype = None
    try:
        mtype = detect_model_type(model_path, verbose=False)
        print(f"  Type:      {_model_type_label(mtype.value)}")
    except Exception:
        print(f"  Type:      detection failed")

    try:
        sess = create_session(model_path, intra_threads=4)
        inp = sess.get_inputs()[0]
        out = sess.get_outputs()[0]
        shape = _safe_get_input_shape(inp)
        print(f"  Input:     {_c(inp.name, C.WHITE)}  shape={shape}")
        print(f"  Output:    {_c(out.name, C.WHITE)}")
        del sess
    except Exception as e:
        print(f"  I/O:       {_c(f'error: {e}', C.RED)}")

    print()
    return mtype


def _print_strategy_chain(attempts: list):
    """打印策略尝试链"""
    print(_c("── Strategy Chain ───────────────────────────────────────────", C.DIM))
    for i, a in enumerate(attempts):
        tag = "PRIMARY" if i == 0 else f"FALLBACK-{i}"
        ok = a.get("success", False)
        mark = _c("✅", C.GREEN) if ok else _c("❌", C.RED)
        strat = _strategy_label(a["strategy"])
        md = a.get("max_diff", -1)
        sp = a.get("speedup", 0)
        err = a.get("error", "")

        md_str = f"max_diff={md:.4f}" if md >= 0 else ""
        sp_str = f"speedup={sp:.2f}x" if sp > 0 else ""
        err_str = f"  ({err[:60]})" if err and not ok else ""

        details = "  ".join(filter(None, [md_str, sp_str]))
        print(f"  {mark} [{_c(f'{tag:10s}', C.BOLD)}] {strat:30s} {details}{err_str}")
    print()


def _print_comparison(result):
    """打印 FP32 vs 量化后对比"""
    print(_c("── Comparison (FP32 → Quantized) ──────────────────────────", C.DIM))

    fp32 = result.fp32_performance
    q = result.performance

    if fp32 and fp32.success:
        print(f"  {'FP32 latency':20s} {_c(f'{fp32.avg_ms:.4f} ms', C.DIM):>20s}  baseline")
        print(f"  {'FP32 size':20s} {_c(f'{fp32.size_kb:.1f} KB', C.DIM):>20s}  baseline")
    if q and q.success:
        print(f"  {'Quantized latency':20s} {_c(f'{q.avg_ms:.4f} ms', C.BOLD):>20s}")
        print(f"  {'Quantized size':20s} {_c(f'{q.size_kb:.1f} KB', C.BOLD):>20s}  {result.size_ratio:.1%}")
        speed_note = (_c("faster", C.GREEN) if result.speedup > 1.05 else
                      _c("slower", C.RED) if result.speedup < 0.95 else
                      _c("same", C.DIM))
        print(f"  {'Speedup':20s} {_c(f'{result.speedup:.2f}x', C.BOLD):>20s}  {speed_note}")

    if result.accuracy:
        acc = result.accuracy
        print(f"  {'Max diff':20s} {_c(f'{acc.max_diff:.6f}', C.BOLD):>20s}  {_level_emoji(acc.level)}")
        cos_note = (_c("good", C.GREEN) if acc.cosine_sim_min > 0.99 else
                    _c("ok", C.YELLOW) if acc.cosine_sim_min > 0.9 else
                    _c("poor", C.RED))
        print(f"  {'Cosine sim':20s} {_c(f'{acc.cosine_sim_min:.6f}', C.BOLD):>20s}  {cos_note}")
    print()


def main(argv=None):
    """CLI 入口函数"""
    parser = argparse.ArgumentParser(
        description="ONNX模型本地开发一键量化工具（自动检测+自动回滚+彩色输出）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("model", nargs="?", help="FP32 ONNX模型路径")
    parser.add_argument("-o", "--output", default=None,
                        help="输出路径（默认: <model>_quantized.onnx）")
    parser.add_argument("--strategy", default="auto",
                        choices=["auto", "static_qdq", "static_qoperator",
                                 "dynamic", "fp16"],
                        help="量化策略 (默认auto自动选择)")
    parser.add_argument("-d", "--calib-dir", default=None,
                        help="校准数据目录(.npy文件)，不指定则用随机数据")
    parser.add_argument("-c", "--calib-samples", type=int, default=100,
                        help="校准样本数 (默认100)")
    parser.add_argument("-s", "--input-shape", default=None,
                        help="输入形状，逗号分隔 (如 1,3,224,224)，默认自动检测")
    parser.add_argument("-n", "--input-name", default=None,
                        help="输入节点名，默认自动检测")
    parser.add_argument("--strict", action="store_true",
                        help="严格精度阈值（max_diff<0.02, cosine>0.999）")
    parser.add_argument("--relaxed", action="store_true",
                        help="宽松精度阈值（max_diff<0.1, cosine>0.95）")
    parser.add_argument("--max-diff", type=float, default=None,
                        help="自定义max_diff阈值")
    parser.add_argument("-t", "--threads", type=int, default=4,
                        help="推理线程数 (默认4)")
    parser.add_argument("-w", "--warmup", type=int, default=20,
                        help="预热次数 (默认20)")
    parser.add_argument("-r", "--runs", type=int, default=100,
                        help="性能测量次数 (默认100)")
    parser.add_argument("--info", action="store_true",
                        help="仅显示模型信息，不执行量化")
    parser.add_argument("--dry-run", action="store_true",
                        help="预览模式：检测模型+推荐策略，不实际执行量化")
    parser.add_argument("--json", action="store_true",
                        help="JSON格式输出（用于脚本调用）")
    parser.add_argument("--no-color", action="store_true",
                        help="禁用彩色输出")
    parser.add_argument("--exclude-nodes", nargs="*", default=None,
                        help="排除量化的节点名称列表")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="详细输出")

    args = parser.parse_args(argv)

    if args.no_color:
        os.environ["NO_COLOR"] = "1"

    if args.json:
        import warnings, logging
        warnings.filterwarnings("ignore")
        logging.disable(logging.WARNING)
        os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

    if not args.model:
        parser.print_help()
        return 0

    if not os.path.isfile(args.model):
        print(_c(f"Error: Model not found: {args.model}", C.RED), file=sys.stderr)
        return 3

    model_path = os.path.abspath(args.model)

    # 使用 analyze_model() 统一获取模型信息（模型类型、推荐策略、输入形状等）
    analysis = None
    mtype = None
    try:
        analysis = analyze_model(model_path, intra_threads=args.threads)
        mtype = ModelType(analysis["model_type"])
    except Exception as e:
        if not args.json:
            print(_c(f"Warning: model analysis failed: {e}", C.YELLOW), file=sys.stderr)

    if not args.json:
        _print_banner()
        _print_model_info(model_path)

    # --info: 只显示信息
    if args.info:
        return 0

    # 输出路径
    output_path = args.output
    if not output_path:
        p = Path(model_path)
        output_path = str(p.with_name(f"{p.stem}_quantized{p.suffix}"))

    # 输入形状（CLI 参数优先于自动检测）
    input_shape = None
    if args.input_shape:
        input_shape = tuple(int(x) for x in args.input_shape.split(","))

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

    if not args.json:
        if analysis:
            print(_c("── Quantization Plan ───────────────────────────────────────", C.DIM))
            chosen = args.strategy if args.strategy != "auto" else analysis["recommended_strategy"]
            print(f"  Strategy:     {_strategy_label(chosen)}")
            if args.strategy == "auto":
                print(f"  Detected:     {_model_type_label(analysis['model_type'])}")
                print(f"  Fallback:     {analysis['strategy_chain']}")
            print(f"  Thresholds:   max_diff<{thresholds.acceptable_max_diff}, cos_sim>{thresholds.min_cosine_sim}")
            print(f"  Output:       {_c(output_path, C.WHITE)}")
            print()

    # --dry-run: 预览模式退出
    if args.dry_run:
        if args.json and analysis:
            import warnings, logging as _log
            warnings.filterwarnings("ignore")
            _log.disable(_log.WARNING)
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
        elif not args.json:
            print(_c("🔍 Dry run mode - no quantization performed.", C.YELLOW))
            print()
        return 0

    # 自动检测输入信息用于校准Reader（优先顺序：用户指定 > analyze_model结果 > Session检测 > 安全fallback）
    # Bug #3修复：不再硬编码(1,3,224,224)图像形状，避免非CNN模型错误
    shape_for_calib = input_shape
    name_for_calib = args.input_name
    detect_failed = False

    if input_shape is None or args.input_name is None:
        # 尝试1：使用analyze_model结果
        if analysis and analysis.get("input_shape") and analysis.get("input_name"):
            if input_shape is None:
                shape_for_calib = analysis["input_shape"]
            if args.input_name is None:
                name_for_calib = analysis["input_name"]
        else:
            # 尝试2：直接创建Session检测
            try:
                sess = create_session(model_path, args.threads)
                if len(sess.get_inputs()) > 0:
                    inp = sess.get_inputs()[0]
                    name_for_calib = args.input_name or inp.name
                    if input_shape is None:
                        shape_for_calib = _safe_get_input_shape(inp)
                del sess
            except Exception:
                detect_failed = True

    # 最终fallback：如果所有检测都失败，使用基于模型秩的通用默认值而非图像专用形状
    # 注意：这是一个安全的兜底，但用户应优先通过--input-shape显式指定
    if shape_for_calib is None:
        detect_failed = True
        # 使用(1, 10)作为通用fallback（适合大多数MLP/简单RNN；CNN需要用户显式指定）
        # 不使用(1,3,224,224)因为那只适用于图像模型，会让其他类型模型静默失败
        shape_for_calib = (1, 10)
        if not args.json:
            print(_c("⚠️  Warning: Could not auto-detect input shape, using fallback (1,10). "
                     "Please specify --input-shape for non-trivial models.", C.YELLOW))
    if name_for_calib is None:
        name_for_calib = "input"

    # 校准数据Reader
    if args.calib_dir and os.path.isdir(args.calib_dir):
        calib_reader = FileCalibrationReader(
            input_name=name_for_calib,
            input_shape=shape_for_calib,
            calib_dir=args.calib_dir,
            num_samples=args.calib_samples,
        )
    else:
        calib_reader = RandomCalibrationReader(
            input_name=name_for_calib,
            input_shape=shape_for_calib,
            num_samples=args.calib_samples,
        )

    # 执行量化
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

    t0 = time.perf_counter()

    if not args.json:
        print(_c("── Running Quantization ────────────────────────────────────", C.DIM))

    result = auto_quantize(
        model_path=model_path,
        output_path=output_path,
        calib_reader=calib_reader,
        input_shape=input_shape,
        input_name=args.input_name,
        config=config,
        verbose=args.verbose and not args.json,
    )

    elapsed = time.perf_counter() - t0

    if args.json:
        report = build_report(result, thresholds, elapsed, model_path)
        report["success"] = result.success  # backward compatibility
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if result.success else 1

    # 输出结果
    print()
    _print_strategy_chain(result.all_attempts)
    _print_comparison(result)

    print(_c("── Result ──────────────────────────────────────────────────", C.DIM))
    if result.success:
        print(f"  {_c('✅ QUANTIZATION SUCCESSFUL', C.BOLD + C.GREEN)}")
        print(f"  Strategy:   {_strategy_label(result.strategy_used)}")
        print(f"  Output:     {_c(output_path, C.WHITE)}")
        if result.fallback_triggered:
            print(f"  {_c('⚠️  Fallback triggered:', C.YELLOW)} {result.fallback_reason}")
    else:
        print(f"  {_c('❌ ALL STRATEGIES FAILED', C.BOLD + C.RED)}")
        if result.error:
            print(f"  Error: {result.error}")
    print(f"  Elapsed:    {elapsed:.1f}s")
    print()

    return 0 if result.success else 1
