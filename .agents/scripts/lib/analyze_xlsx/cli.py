from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .constants import DEFAULT_SUMMARY_TEMPLATE, DEFAULT_TEMPLATE
from .context import extract_report_context
from .renderer import render_release_summary, render_report
from .utils import configure_stdio


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="解析 .xlsx 测试报告并导出 Markdown")
    parser.add_argument("--input", required=True, help="输入 .xlsx 文件路径")
    parser.add_argument("--output", required=True, help="输出 Markdown 文件路径")
    parser.add_argument(
        "--template",
        default=str(DEFAULT_TEMPLATE),
        help="Markdown 模板路径",
    )
    parser.add_argument("--summary-output", default=None, help="输出发布判断摘要 Markdown 文件路径")
    parser.add_argument(
        "--summary-template",
        default=str(DEFAULT_SUMMARY_TEMPLATE),
        help="发布判断摘要模板路径",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="仅生成摘要，不生成全量报告",
    )
    return parser.parse_args()


def main() -> int:
    configure_stdio()
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    template_path = Path(args.template)
    summary_output = Path(args.summary_output) if args.summary_output else None
    summary_template = Path(args.summary_template) if args.summary_template else None

    try:
        if args.summary_only and summary_output is None:
            raise ValueError("--summary-only 需要与 --summary-output 一起使用")

        context = extract_report_context(input_path)

        if not args.summary_only:
            markdown = render_report(context, template_path=template_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(markdown, encoding="utf-8")
            print(f"已生成报告: {output_path}")

        if summary_output is not None:
            summary_md = render_release_summary(context, template_path=summary_template)
            summary_output.parent.mkdir(parents=True, exist_ok=True)
            summary_output.write_text(summary_md, encoding="utf-8")
            print(f"已生成摘要: {summary_output}")

        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
