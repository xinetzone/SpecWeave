#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path

from lib.project import resolve_project_root
from lib.cli import print_error, print_header, print_warn, add_common_args, setup_safe_output
from lib.quality_report import (
    build_json_output,
    common_report_fields,
    safe_relative_to,
    print_aggregate_summary,
)

from .checker import check_pattern
from .constants import PATTERNS_DIR
from .discovery import find_pattern_files
from .reporter import print_pattern_report


def main():
    setup_safe_output()
    parser = argparse.ArgumentParser(
        description="方法论模式质量检查：验证docs/retrospective/patterns/下的模式文档符合规范"
    )
    add_common_args(parser)
    parser.add_argument("--score", action="store_true", help="仅输出质量评分")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示通过项详情")
    parser.add_argument("--threshold", type=int, default=60, help="评分阈值（低于则退出码1，默认60）")
    args = parser.parse_args()

    root_dir = resolve_project_root(__file__)
    patterns_dir = root_dir / PATTERNS_DIR

    target_path = Path(args.path).resolve() if args.path else None
    pattern_files = find_pattern_files(root_dir, patterns_dir, target_path)

    if not pattern_files:
        msg = f"未找到模式文件（目录: {patterns_dir}）"
        if args.json:
            print(json.dumps({"error": msg, "patterns": []}, ensure_ascii=False, indent=2))
        else:
            print_error(msg)
        sys.exit(1)

    reports = [check_pattern(f, root_dir) for f in pattern_files]

    if args.json:
        output = build_json_output(
            reports,
            root_dir,
            base_dir_key="patterns_dir",
            base_dir_value=patterns_dir,
            count_key="pattern_count",
            items_key="patterns",
            item_builder=lambda r: {
                "id": r.pattern_id,
                "title": r.pattern_title,
                "path": str(safe_relative_to(r.pattern_path, root_dir)),
                **common_report_fields(r),
            },
        )
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    if args.score:
        for r in sorted(reports, key=lambda x: x.score):
            print(f"{r.pattern_id}: {r.score}  {r.pattern_title[:50]}")
        avg = sum(r.score for r in reports) // len(reports) if reports else 0
        print(f"\n平均: {avg}/100")
        failed = [r for r in reports if r.score < args.threshold]
        sys.exit(1 if failed else 0)

    print_header("方法论模式质量检查")
    print(f"  扫描目录: {patterns_dir}")
    print(f"  检查项: Frontmatter/必要章节/检查清单/Why解释/可视化/路径规范/交叉引用")
    print(f"  发现 {len(reports)} 个模式文件")

    for report in sorted(reports, key=lambda x: x.score):
        print_pattern_report(report, root_dir, verbose=args.verbose)

    stats = print_aggregate_summary(reports)
    avg_score = stats["avg_score"]

    if avg_score < args.threshold:
        print()
        print_warn(f"平均评分{avg_score}低于阈值{args.threshold}，建议根据上述改进项优化")
        print()
        print("改进指引：")
        print("  1. Frontmatter：补齐必需字段id/domain/layer/maturity/source")
        print("  2. 必要章节：模式类型/成熟度/适用场景/问题背景/核心内容缺一不可")
        print("  3. 检查清单：添加至少3个- [ ]格式的可执行检查项，方便落地验证")
        print("  4. Why解释：关键规则后添加'> **为什么？**'解释设计意图")
        print("  5. 正例/反例：补充正反案例对比，帮助理解模式边界")
        print("  6. 交叉引用：在「与现有模式的关系」章节链接2+个相关模式，构建知识网络")
        print("  7. Mermaid：复杂流程建议添加Mermaid可视化降低理解门槛")

    failed = [r for r in reports if r.errors]
    sys.exit(1 if failed and avg_score < args.threshold else 0)
