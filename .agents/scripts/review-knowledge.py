#!/usr/bin/env python3
"""对抗式审查 CLI 工具。

执行多Agent对抗式审查，生成结构化漏洞报告。

用法：
  python review-knowledge.py run                    # 执行完整审查
  python review-knowledge.py run --profile security # 仅安全攻击者
  python review-knowledge.py run --category encryption_boundary  # 仅加密场景
  python review-knowledge.py run --verbose          # 详细输出
  python review-knowledge.py run --json             # JSON 输出
  python review-knowledge.py profiles              # 列出攻击者
  python review-knowledge.py scenarios             # 列出场景
  python review-knowledge.py report <path>         # 查看审查报告
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.knowledge_adversarial import (
    run_adversarial_review,
    generate_attack_scenarios,
    ATTACKER_PROFILES,
    REPORT_DIR,
)


def cmd_run(args):
    """执行审查。"""
    result = run_adversarial_review(
        profiles=args.profile,
        categories=args.category,
        verbose=args.verbose,
    )

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if not args.verbose:
        meta = result["metadata"]
        stats = result["stats"]
        print(f"审查完成: {meta['total_scenarios']} 场景, {meta['elapsed_seconds']}s")
        print(f"漏洞: P0={stats['P0']} P1={stats['P1']} P2={stats['P2']} 总计={stats['total']}")
        print(f"报告: {result.get('report_path', 'N/A')}")

    return 0


def cmd_profiles(args):
    """列出攻击者Profile。"""
    print("攻击者Profile:")
    print()
    for pid, p in ATTACKER_PROFILES.items():
        print(f"  [{pid}] {p.name}")
        print(f"    关注: {p.focus}")
        print(f"    描述: {p.description}")
        print(f"    攻击向量: {', '.join(p.attack_vectors)}")
        print()


def cmd_scenarios(args):
    """列出攻击场景。"""
    scenarios = generate_attack_scenarios()

    if args.category:
        scenarios = [s for s in scenarios if s["category"] == args.category]
    if args.profile:
        scenarios = [s for s in scenarios if s["attacker"] == args.profile]

    # 按类别分组
    categories = {}
    for s in scenarios:
        cat = s["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(s)

    for cat, sc_list in categories.items():
        print(f"\n[{cat}] ({len(sc_list)} 场景)")
        for s in sc_list:
            print(f"  {s['id']} [{s['attacker']}] {s['name']}")
            print(f"    {s['description']}")


def cmd_report(args):
    """查看报告。"""
    report_path = Path(args.path)
    if not report_path.exists():
        print(f"报告不存在: {report_path}")
        return 1

    content = report_path.read_text(encoding="utf-8")
    print(content)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="对抗式审查 CLI 工具",
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # run
    p_run = subparsers.add_parser("run", help="执行对抗式审查")
    p_run.add_argument(
        "--profile", action="append",
        choices=list(ATTACKER_PROFILES.keys()),
        help="限制攻击者（可多次指定）",
    )
    p_run.add_argument(
        "--category", action="append",
        choices=[
            "oversized_malformed", "encryption_boundary",
            "integrity_bypass", "search_injection",
            "path_traversal", "metadata_pollution",
            "resource_exhaustion",
        ],
        help="限制场景类别（可多次指定）",
    )
    p_run.add_argument("--json", action="store_true", help="JSON 输出")
    p_run.add_argument("--verbose", action="store_true", help="详细输出")

    # profiles
    subparsers.add_parser("profiles", help="列出攻击者Profile")

    # scenarios
    p_scenarios = subparsers.add_parser("scenarios", help="列出攻击场景")
    p_scenarios.add_argument("--category", help="按类别筛选")
    p_scenarios.add_argument("--profile", help="按攻击者筛选")

    # report
    p_report = subparsers.add_parser("report", help="查看审查报告")
    p_report.add_argument("path", help="报告路径")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "run": cmd_run,
        "profiles": cmd_profiles,
        "scenarios": cmd_scenarios,
        "report": cmd_report,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())