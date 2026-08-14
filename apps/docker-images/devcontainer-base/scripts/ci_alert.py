#!/usr/bin/env python3
"""
ci_alert.py — CI 流水线量化报告解析与报警工具

解析单模型或批量量化 JSON 报告，输出失败摘要，失败时以非零退出码退出。
可集成到 CI/CD 流水线中作为量化门禁的后置报警步骤。

用法:
  # 检查单个报告
  python ci_alert.py quant_report.json

  # 检查批量报告
  python ci_alert.py batch_report.json

  # 多个报告文件
  python ci_alert.py report1.json report2.json report3.json

  # 严格模式：将 WARNING 级别(acceptable)精度视为失败
  python ci_alert.py report.json --fail-on-warning

  # JSON 格式输出（供 CI 系统解析）
  python ci_alert.py report.json --json

  # 指定最低加速比阈值
  python ci_alert.py report.json --min-speedup 1.0

退出码:
  0: 全部通过
  1: 存在失败模型
  2: 报告文件解析错误
  3: 命令行参数错误
"""
import argparse
import json
import os
import sys
from typing import Any, Dict, List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from onnx_quantize_kit import parse_report
from onnx_quantize_kit.reporting import format_summary, format_batch_summary

_STRATEGY_LABELS = {
    "static_qdq": "Static QDQ (INT8)",
    "static_qoperator": "Static QOp (INT8)",
    "static_qoperator_quint8": "Static QOp/U8 (INT8)",
    "dynamic": "Dynamic (INT8)",
    "fp16": "FP16",
}


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"


def _supports_color() -> bool:
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(text: str, color: str) -> str:
    if not _supports_color():
        return text
    return f"{color}{text}{Colors.RESET}"


def _load_reports(path: str) -> List[Dict[str, Any]]:
    """加载报告文件，自动识别单模型/批量格式，返回模型报告列表。"""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Report not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 批量报告格式: {"batch_summary": {...}, "models": [...]}
    if isinstance(data, dict) and "models" in data:
        models = []
        for m in data["models"]:
            try:
                models.append(parse_report(m))
            except ValueError:
                models.append(m)
        return models

    # 单模型报告
    return [parse_report(data)]


def _evaluate_report(
    report: Dict[str, Any],
    fail_on_warning: bool = False,
    min_speedup: float = 0.0,
) -> Dict[str, Any]:
    """评估单个报告，返回评估结果。"""
    issues = []
    warnings = []
    status = report.get("status", "FAIL")

    # 检查状态
    if status == "FAIL":
        issues.append(f"Quantization failed: {report.get('error', 'unknown error')}")

    # 检查精度级别
    acc = report.get("accuracy", {})
    level = acc.get("level", "unknown")
    if level == "unacceptable":
        issues.append(f"Accuracy unacceptable: max_diff={acc.get('max_diff', 'N/A')}, "
                      f"cos_sim={acc.get('cosine_sim_min', 'N/A')}")
    elif level == "acceptable" and fail_on_warning:
        issues.append(f"Accuracy warning (treated as failure): max_diff={acc.get('max_diff', 'N/A')}")
    elif level == "acceptable":
        warnings.append(f"Accuracy at acceptable level: max_diff={acc.get('max_diff', 'N/A')}")

    # 检查加速比
    speedup = report.get("speedup", 0)
    if speedup > 0 and speedup < min_speedup:
        issues.append(f"Speedup {speedup:.2f}x below threshold {min_speedup:.2f}x")

    # 检查回滚
    if report.get("fallback_triggered"):
        warnings.append(f"Fallback triggered: {report.get('fallback_reason', '')}")

    is_failure = len(issues) > 0
    return {
        "report": report,
        "is_failure": is_failure,
        "issues": issues,
        "warnings": warnings,
    }


def format_alert_text(
    evaluations: List[Dict[str, Any]],
    source_files: List[str],
    color: bool = True,
) -> str:
    """格式化报警文本输出。"""
    def _w(text, c=""):
        return _c(text, c) if color else text

    lines = []
    total = len(evaluations)
    failures = [e for e in evaluations if e["is_failure"]]
    passed = total - len(failures)
    has_warnings = any(e["warnings"] for e in evaluations)

    lines.append(_w("=" * 72, Colors.DIM))
    lines.append(_w("CI Quantization Report Alert", Colors.BOLD))
    lines.append(_w("=" * 72, Colors.DIM))
    lines.append(f"  Sources: {', '.join(source_files)}")
    lines.append(f"  Total: {total}  |  "
                 f"{_w(f'Passed: {passed}', Colors.GREEN)}  |  "
                 f"{_w(f'Failed: {len(failures)}', Colors.RED if failures else Colors.DIM)}"
                 f"  |  Warnings: {sum(len(e['warnings']) for e in evaluations)}")
    lines.append("")

    # 失败详情
    if failures:
        lines.append(_w("── Failures ──────────────────────────────────────────────", Colors.RED))
        for e in failures:
            r = e["report"]
            name = r.get("model", r.get("model_path", "unknown"))
            strategy = _STRATEGY_LABELS.get(r.get("strategy_used", ""), r.get("strategy_used", "N/A"))
            lines.append(f"  {_w('❌', Colors.RED)} {_w(name, Colors.BOLD)}  [{strategy}]")
            for issue in e["issues"]:
                lines.append(f"     {_w('•', Colors.RED)} {issue}")
            for w in e["warnings"]:
                lines.append(f"     {_w('⚠', Colors.YELLOW)} {w}")
            lines.append("")

    # 警告（非失败类）
    all_warnings = [(e, w) for e in evaluations for w in e["warnings"]
                    if not e["is_failure"]]
    if all_warnings:
        lines.append(_w("── Warnings ──────────────────────────────────────────────", Colors.YELLOW))
        for e, w in all_warnings:
            name = e["report"].get("model", "?")
            lines.append(f"  {_w('⚠', Colors.YELLOW)} {name}: {w}")
        lines.append("")

    # 通过的模型概要
    passed_evals = [e for e in evaluations if not e["is_failure"]]
    if passed_evals:
        lines.append(_w("── Passed ────────────────────────────────────────────────", Colors.GREEN))
        reports = [e["report"] for e in passed_evals]
        # 复用批量汇总表格
        lines.append(format_batch_summary(reports, color=color))
        lines.append("")

    # 总结
    if failures:
        lines.append(_w(f"❌ {len(failures)} model(s) FAILED quantization checks.", Colors.BOLD + Colors.RED))
    elif has_warnings:
        lines.append(_w(f"⚠️  All {total} model(s) passed with warnings.", Colors.BOLD + Colors.YELLOW))
    else:
        lines.append(_w(f"✅ All {total} model(s) passed quantization checks.", Colors.BOLD + Colors.GREEN))

    lines.append(_w("=" * 72, Colors.DIM))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="CI量化报告解析与报警工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("reports", nargs="+",
                        help="一个或多个量化报告 JSON 文件（支持单模型和批量格式）")
    parser.add_argument("--fail-on-warning", action="store_true",
                        help="将 acceptable 精度级别视为失败")
    parser.add_argument("--min-speedup", type=float, default=0.0,
                        help="最低加速比阈值，低于此值视为失败 (默认0.0=不检查)")
    parser.add_argument("--json", action="store_true",
                        help="JSON 格式输出（供 CI 系统解析）")
    parser.add_argument("--no-color", action="store_true",
                        help="禁用彩色输出")

    args = parser.parse_args()

    if args.no_color:
        os.environ["NO_COLOR"] = "1"

    # 加载所有报告
    all_evaluations = []
    source_files = []
    parse_errors = []

    for path in args.reports:
        try:
            reports = _load_reports(path)
            source_files.append(path)
            for r in reports:
                ev = _evaluate_report(r, args.fail_on_warning, args.min_speedup)
                all_evaluations.append(ev)
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
            parse_errors.append(f"{path}: {e}")

    if parse_errors:
        for err in parse_errors:
            print(_c(f"[ERROR] {err}", Colors.RED), file=sys.stderr)
        return 2

    if not all_evaluations:
        print(_c("[ERROR] No reports found.", Colors.RED), file=sys.stderr)
        return 2

    if args.json:
        # JSON 输出
        failures = [e for e in all_evaluations if e["is_failure"]]
        result = {
            "total": len(all_evaluations),
            "passed": len(all_evaluations) - len(failures),
            "failed": len(failures),
            "fail_on_warning": args.fail_on_warning,
            "min_speedup": args.min_speedup,
            "failures": [
                {
                    "model": e["report"].get("model", ""),
                    "model_path": e["report"].get("model_path", ""),
                    "strategy_used": e["report"].get("strategy_used", ""),
                    "issues": e["issues"],
                    "warnings": e["warnings"],
                }
                for e in failures
            ],
            "warnings": [
                {
                    "model": e["report"].get("model", ""),
                    "warnings": e["warnings"],
                }
                for e in all_evaluations
                if e["warnings"] and not e["is_failure"]
            ],
            "reports": [e["report"] for e in all_evaluations],
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1 if failures else 0

    # 文本输出
    print(format_alert_text(all_evaluations, source_files, color=not args.no_color))

    failures = [e for e in all_evaluations if e["is_failure"]]
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
