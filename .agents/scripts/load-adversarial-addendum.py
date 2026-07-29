#!/usr/bin/env python3
"""
对抗审查补充内容自动加载器 - CLI入口

用法:
  python load-adversarial-addendum.py <目标文件路径>         # 自动检测并输出注入后的prompt
  python load-adversarial-addendum.py <目标文件路径> --list   # 仅列出将被加载的补充项
  python load-adversarial-addendum.py <目标文件路径> --scenario governance  # 手动指定审查类型
  python load-adversarial-addendum.py <目标文件路径> --force-all  # 强制加载所有补充项
  python load-adversarial-addendum.py <目标文件路径> --inject-to <output.md>  # 注入到文件

示例:
  python load-adversarial-addendum.py .agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/bounded-iteration-budget.md
  python load-adversarial-addendum.py review-prompt.md --inject-to review-prompt-augmented.md
"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.adversarial_addendum import (
    ReviewContext,
    get_all_addenda,
    inject_into_prompt,
    list_addenda_summary,
    load_applicable_addenda,
)
from lib.cli import setup_safe_output, _supports_unicode, _symbol


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="对抗审查补充内容自动加载器 - 自动检测并注入补充攻击视角/检查清单/模板",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "target",
        nargs="?",
        help="待审查的目标文件路径（模式文档/方案文档/代码文件等）",
    )
    parser.add_argument(
        "--scenario",
        choices=["auto", "governance", "architecture", "pattern", "general"],
        default="auto",
        help="手动指定审查场景类型（默认auto自动检测）",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="仅列出将被加载的补充项，不输出完整prompt",
    )
    parser.add_argument(
        "--force-all",
        action="store_true",
        help="强制加载所有补充项（忽略自动检测）",
    )
    parser.add_argument(
        "--disable",
        nargs="*",
        default=[],
        help="禁用指定补充项（按名称）",
    )
    parser.add_argument(
        "--inject-to",
        metavar="FILE",
        help="将注入结果写入指定文件而非stdout",
    )
    parser.add_argument(
        "--base-prompt",
        metavar="FILE",
        help="指定基础prompt文件（默认读取target文件内容作为基础）",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="检查补充文件完整性，不执行注入",
    )
    return parser


def cmd_check() -> int:
    setup_safe_output()
    all_addenda = get_all_addenda()
    all_ok = True
    for a in all_addenda:
        ok = a.exists
        sym = _symbol("pass") if ok else _symbol("error")
        status = "存在" if ok else "缺失"
        print(f"  {sym} [{a.category}] {a.name}: {status}")
        print(f"      路径: {a.path}")
        if not ok:
            all_ok = False
    print()
    if all_ok:
        print(f"{_symbol('pass')} 所有补充文件均存在")
        return 0
    else:
        print(f"{_symbol('error')} 存在缺失的补充文件")
        return 1


def cmd_list(ctx: ReviewContext) -> int:
    setup_safe_output()
    if ctx.forced_addenda:
        print(f"模式: 手动强制加载 ({', '.join(ctx.forced_addenda)})")
    result = load_applicable_addenda(ctx)
    print(list_addenda_summary(result))
    return 0


def cmd_inject(ctx: ReviewContext, base_prompt_path: Path | None, output_path: Path | None) -> int:
    setup_safe_output()

    if base_prompt_path is not None:
        if not base_prompt_path.is_file():
            print(f"{_symbol('error')} 基础prompt文件不存在: {base_prompt_path}", file=sys.stderr)
            return 1
        base_content = base_prompt_path.read_text(encoding="utf-8")
    elif ctx.target_path is not None and ctx.target_path.is_file():
        base_content = ctx.target_path.read_text(encoding="utf-8")
    else:
        base_content = "# 对抗审查\n\n请对以下对象执行对抗审查。\n"

    result = load_applicable_addenda(ctx)
    augmented = inject_into_prompt(base_content, ctx)

    if output_path is not None:
        output_path.write_text(augmented, encoding="utf-8")
        print(f"{_symbol('pass')} 注入结果已写入: {output_path}")
        print(list_addenda_summary(result))
    else:
        sys.stdout.write(augmented)

    return 0


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()

    if args.check:
        return cmd_check()

    if not args.target and not args.base_prompt:
        parser.print_help()
        return 1

    target_path = Path(args.target).resolve() if args.target else None
    base_prompt_path = Path(args.base_prompt).resolve() if args.base_prompt else None

    if args.target and not target_path.exists():
        print(f"{_symbol('warn')} 目标路径不存在: {target_path}", file=sys.stderr)

    ctx = ReviewContext.from_path(target_path, scenario=args.scenario) if target_path else ReviewContext(scenario=args.scenario)

    if args.force_all:
        ctx.forced_addenda = {a.name for a in get_all_addenda()}

    for name in args.disable:
        ctx.disabled_addenda.add(name)

    if args.list:
        return cmd_list(ctx)

    output_path = Path(args.inject_to).resolve() if args.inject_to else None
    return cmd_inject(ctx, base_prompt_path, output_path)


if __name__ == "__main__":
    sys.exit(main())

