#!/usr/bin/env python3
"""
七概念方法论触发匹配工具
输入：自然语言任务描述
输出：推荐的概念组合、执行顺序、参考流程、质量门提醒
"""
import argparse
import sys

from lib.seven_concepts import (
    match_task,
    format_match_result,
    format_scenario_list,
)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="七概念方法论触发匹配工具 - 根据任务描述推荐概念组合",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python seven-concepts-trigger.py "Sprint结束做复盘"
  python seven-concepts-trigger.py "修复线上支付Bug"
  python seven-concepts-trigger.py "重构超长文档" --top 3
        """,
    )
    parser.add_argument(
        "task",
        nargs="*",
        help="任务描述（自然语言）",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=1,
        choices=[1, 2, 3],
        help="返回前N个匹配（默认1，最大3）",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有支持的场景",
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.list:
        print(format_scenario_list())
        return 0

    if not args.task:
        parser.print_help()
        return 1

    task_text = " ".join(args.task)
    print(f"📋 任务描述：{task_text}")
    print("=" * 60)

    results = match_task(task_text)
    top_n = min(args.top, len(results))

    for i in range(top_n):
        print(format_match_result(results[i], i), end="")

    print("\n" + "=" * 60)
    print("📖 详细规则参考：seven-concepts-quick-reference.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
