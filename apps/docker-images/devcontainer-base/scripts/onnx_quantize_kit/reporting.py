"""
onnx_quantize_kit.reporting — 量化报告构建、解析与格式化

提供统一的量化报告构建/解析/格式化能力，供 CLI、CI 门禁、批量脚本复用：
- build_report(): 将 QuantizationResult 转为标准 dict
- parse_report(): 从 JSON 文件或 dict 加载并校验报告
- format_summary(): 生成人类可读的摘要文本
- format_batch_summary(): 批量量化汇总表格
"""
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from .accuracy import AccuracyThresholds


# ──── ANSI Colors ────
class _C:
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
    import sys
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(text: str, color: str) -> str:
    if not _supports_color():
        return text
    return f"{color}{text}{_C.RESET}"


_STRATEGY_LABELS = {
    "static_qdq": "Static QDQ (INT8)",
    "static_qoperator": "Static QOp (INT8)",
    "static_qoperator_quint8": "Static QOp/U8 (INT8)",
    "dynamic": "Dynamic (INT8)",
    "fp16": "FP16",
}

_LEVEL_EMOJI = {"excellent": "🟢", "acceptable": "🟡", "unacceptable": "🔴"}


def build_report(
    result,
    thresholds: Optional[AccuracyThresholds] = None,
    elapsed: Optional[float] = None,
    model_path: str = "",
) -> Dict[str, Any]:
    """将 QuantizationResult 转换为标准化报告 dict。

    Args:
        result: QuantizationResult 对象
        thresholds: 使用的精度阈值（可选，记录到报告中）
        elapsed: 量化耗时秒数（可选）
        model_path: 原始 FP32 模型路径（可选）

    Returns:
        标准化报告 dict，字段稳定可被 CI 解析
    """
    report: Dict[str, Any] = {
        "status": "PASS" if result.success else "FAIL",
        "model": os.path.basename(model_path) if model_path else "",
        "model_path": model_path,
        "output": result.output_path,
        "model_type": result.model_type,
        "strategy_used": result.strategy_used,
        "fallback_triggered": result.fallback_triggered,
        "fallback_reason": result.fallback_reason,
        "speedup": round(result.speedup, 2) if result.speedup else 0,
        "size_ratio": round(result.size_ratio, 3) if result.size_ratio else 0,
        "all_attempts": result.all_attempts,
    }

    if elapsed is not None:
        report["elapsed_seconds"] = round(elapsed, 2)

    if thresholds:
        report["thresholds"] = {
            "acceptable_max_diff": thresholds.acceptable_max_diff,
            "excellent_max_diff": thresholds.excellent_max_diff,
            "min_cosine_sim": thresholds.min_cosine_sim,
            "min_speedup": thresholds.min_speedup,
        }

    if result.fp32_performance and result.fp32_performance.success:
        report["fp32"] = {
            "avg_ms": round(result.fp32_performance.avg_ms, 4),
            "size_kb": round(result.fp32_performance.size_kb, 1),
        }

    if result.performance and result.performance.success:
        report["quantized"] = {
            "avg_ms": round(result.performance.avg_ms, 4),
            "p50_ms": round(result.performance.p50_ms, 4),
            "p95_ms": round(result.performance.p95_ms, 4),
            "p99_ms": round(result.performance.p99_ms, 4),
            "throughput_fps": round(result.performance.throughput_fps, 1),
            "size_kb": round(result.performance.size_kb, 1),
        }

    if result.accuracy:
        report["accuracy"] = {
            "level": result.accuracy.level,
            "max_diff": round(result.accuracy.max_diff, 6),
            "mean_diff": round(result.accuracy.mean_diff, 6),
            "cosine_sim_min": round(result.accuracy.cosine_sim_min, 6),
            "passed": result.accuracy.passed,
        }
        if result.accuracy.fail_reason:
            report["accuracy"]["fail_reason"] = result.accuracy.fail_reason

    if result.error:
        report["error"] = result.error

    return report


def parse_report(source: Union[str, dict, "os.PathLike"]) -> Dict[str, Any]:
    """从 JSON 文件路径或 dict 加载并校验量化报告。

    Args:
        source: JSON 文件路径(str/PathLike) 或已经是 dict 的报告

    Returns:
        校验后的报告 dict

    Raises:
        FileNotFoundError: 文件不存在
        ValueError: JSON 格式错误或缺少必要字段
    """
    if isinstance(source, dict):
        data = source
    else:
        path = str(source)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Report file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

    # 校验必要字段
    required = ["status", "strategy_used"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Invalid report: missing required fields: {missing}")

    if data["status"] not in ("PASS", "FAIL"):
        raise ValueError(f"Invalid report: status must be PASS/FAIL, got '{data['status']}'")

    return data


def format_summary(report: Dict[str, Any], color: bool = True) -> str:
    """生成人类可读的量化摘要文本。

    Args:
        report: parse_report() 返回的报告 dict
        color: 是否使用 ANSI 彩色输出

    Returns:
        格式化的多行字符串
    """
    lines: List[str] = []

    def _w(text, c=""):
        return _c(text, c) if color else text

    status = report["status"]
    if status == "PASS":
        mark = _w("✅ PASS", _C.BOLD + _C.GREEN)
    else:
        mark = _w("❌ FAIL", _C.BOLD + _C.RED)

    strategy = _STRATEGY_LABELS.get(report.get("strategy_used", ""), report.get("strategy_used", "unknown"))
    lines.append(f"  {mark}  {_w(strategy, _C.CYAN)}")

    model_name = report.get("model", "")
    if model_name:
        lines.append(f"  Model:     {model_name}")

    # 性能
    speedup = report.get("speedup", 0)
    size_ratio = report.get("size_ratio", 0)
    if speedup:
        sp_note = (_w("faster", _C.GREEN) if speedup > 1.05 else
                   _w("slower", _C.RED) if speedup < 0.95 else
                   _w("same", _C.DIM))
        lines.append(f"  Speedup:   {speedup:.2f}x  {sp_note}")
    if size_ratio:
        lines.append(f"  Size:      {size_ratio:.1%} of FP32")

    # 精度
    acc = report.get("accuracy")
    if acc:
        level = acc.get("level", "unknown")
        emoji = _LEVEL_EMOJI.get(level, "❓")
        md = acc.get("max_diff", -1)
        cs = acc.get("cosine_sim_min", -1)
        cs_note = (_w("good", _C.GREEN) if cs > 0.99 else
                   _w("ok", _C.YELLOW) if cs > 0.9 else
                   _w("poor", _C.RED) if cs >= 0 else "")
        lines.append(f"  Accuracy:  {emoji} max_diff={md:.6f}  cos_sim={cs:.6f} {cs_note}")

    # 回滚
    if report.get("fallback_triggered"):
        lines.append(f"  {_w('⚠️  Fallback:', _C.YELLOW)} {report.get('fallback_reason', '')}")

    # 错误
    if report.get("error"):
        lines.append(f"  {_w('Error:', _C.RED)} {report['error']}")

    elapsed = report.get("elapsed_seconds")
    if elapsed:
        lines.append(f"  Elapsed:   {elapsed:.1f}s")

    return "\n".join(lines)


def format_strategy_chain(attempts: list, color: bool = True) -> str:
    """格式化策略尝试链为可读文本。"""
    def _w(text, c=""):
        return _c(text, c) if color else text

    lines = []
    for i, a in enumerate(attempts):
        tag = "PRIMARY" if i == 0 else f"FALLBACK-{i}"
        ok = a.get("success", False)
        mark = _w("✅", _C.GREEN) if ok else _w("❌", _C.RED)
        sname = _STRATEGY_LABELS.get(a.get("strategy", ""), a.get("strategy", "?"))
        md = a.get("max_diff", -1)
        sp = a.get("speedup", 0)
        err = a.get("error", "")

        parts = []
        if md >= 0:
            parts.append(f"max_diff={md:.4f}")
        if sp > 0:
            parts.append(f"speedup={sp:.2f}x")
        if err and not ok:
            parts.append(f"({err[:60]})")

        detail = "  ".join(parts)
        lines.append(f"  {mark} [{_w(f'{tag:10s}', _C.BOLD)}] {sname:30s} {detail}")

    return "\n".join(lines)


def format_batch_summary(reports: List[Dict[str, Any]], color: bool = True) -> str:
    """生成批量量化汇总表格。

    Args:
        reports: 多个 parse_report() 返回的报告 dict 列表
        color: 是否使用 ANSI 彩色输出

    Returns:
        格式化的汇总表格字符串
    """
    def _w(text, c=""):
        return _c(text, c) if color else text

    passed = sum(1 for r in reports if r["status"] == "PASS")
    failed = len(reports) - passed

    lines = []
    lines.append(_w("=" * 82, _C.DIM))
    lines.append(_w("Batch Quantization Summary", _C.BOLD))
    lines.append(_w("=" * 82, _C.DIM))

    # 表头
    header = f"  {'Model':<30s} {'Type':<13s} {'Strategy':<22s} {'Speedup':>8s} {'MaxDiff':>10s}  Status"
    lines.append(header)
    lines.append(_w("  " + "-" * 80, _C.DIM))

    for r in reports:
        model = r.get("model", "?")[:28]
        mtype = r.get("model_type", "?")[:11]
        strat = _STRATEGY_LABELS.get(r.get("strategy_used", ""), r.get("strategy_used", "?"))[:20]
        sp = r.get("speedup", 0)
        sp_str = f"{sp:.2f}x" if sp else "N/A"
        acc = r.get("accuracy", {})
        md = acc.get("max_diff", -1)
        md_str = f"{md:.4f}" if md >= 0 else "N/A"

        if r["status"] == "PASS":
            status = _w("✅ PASS", _C.GREEN)
        else:
            status = _w("❌ FAIL", _C.RED)

        lines.append(f"  {model:<30s} {mtype:<13s} {strat:<22s} {sp_str:>8s} {md_str:>10s}  {status}")

    lines.append(_w("  " + "-" * 80, _C.DIM))
    total = len(reports)
    lines.append(f"  Total: {total}  |  "
                 f"{_w(f'Passed: {passed}', _C.GREEN)}  |  "
                 f"{_w(f'Failed: {failed}', _C.RED if failed else _C.DIM)}")
    lines.append(_w("=" * 82, _C.DIM))

    return "\n".join(lines)
