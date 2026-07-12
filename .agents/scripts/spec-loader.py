#!/usr/bin/env python3
"""L2 渐进式披露规范加载器 CLI。

根据任务描述自动路由并加载所需的 L0/L1/L2 规范文件，
实现上下文按需加载，避免一次性加载全部规范导致上下文爆炸。

用法：
  python spec-loader.py task "代码审查"          # 加载代码审查所需规范
  python spec-loader.py task "复盘项目" -c       # 加载并输出内容
  python spec-loader.py layer L0                 # 仅加载L0层
  python spec-loader.py layer L1                 # 加载L0+L1层
  python spec-loader.py list-types               # 列出所有支持的任务类型
  python spec-loader.py audit                    # 审计所有路由引用的文件是否存在
"""

import argparse
import sys
from pathlib import Path

from lib.cli import setup_safe_output
from lib.project import resolve_project_root
from lib.spec_loader import SpecLoader, TASK_ROUTING, LAYER_DESCRIPTIONS, setup_logging


def cmd_task(args) -> int:
    setup_logging(verbose=args.verbose)
    root = args.path or resolve_project_root(__file__)
    loader = SpecLoader(root, verbose=args.verbose)
    result = loader.load_for_task(
        args.task_description,
        stage=args.stage,
        include_l1=not args.no_l1,
        max_chars=args.max_chars,
    )

    output = loader.format_for_prompt(result, include_content=args.content)
    print(output)

    if result.missing_specs and args.warn_missing:
        print(f"\n⚠️ 以下规范文件未找到: {', '.join(result.missing_specs)}", file=sys.stderr)
        return 1
    return 0


def cmd_layer(args) -> int:
    setup_logging(verbose=args.verbose)
    root = args.path or resolve_project_root(__file__)
    loader = SpecLoader(root, verbose=args.verbose)

    if args.layer == "L0":
        result = loader.load_layer("L0")
    elif args.layer in ("L1", "all"):
        l0 = loader.load_layer("L0")
        result = loader.load_layer("L1")
        result.loaded_specs = l0.loaded_specs + result.loaded_specs
        result.total_chars += l0.total_chars
        result.layer_summary["L0"] = l0.layer_summary["L0"]
        result.missing_specs = l0.missing_specs + result.missing_specs
    else:
        print(f"错误: 未知层 {args.layer}，支持 L0/L1", file=sys.stderr)
        return 1

    output = loader.format_for_prompt(result, include_content=args.content)
    print(output)
    return 0


def cmd_list_types(args) -> int:
    print("支持的任务类型路由：")
    print()
    print(f"{'任务类型':<25} {'触发关键词示例':<40} {'L2规范数'}")
    print("-" * 90)
    for task_type, config in sorted(TASK_ROUTING.items()):
        kws = ", ".join(config["keywords"][:3])
        if len(config["keywords"]) > 3:
            kws += "..."
        print(f"{task_type:<25} {kws:<40} {len(config['l2_specs'])}")
    print()
    print(f"合计: {len(TASK_ROUTING)} 种任务类型")
    return 0


def cmd_audit(args) -> int:
    setup_logging(verbose=args.verbose)
    root = args.path or resolve_project_root(__file__)
    loader = SpecLoader(root, verbose=args.verbose)

    missing = []
    ok = 0

    print("审计 L0 规范...")
    for rel_path in loader.L0_SPECS:
        full = loader.agents_dir / rel_path
        alt = loader.root / rel_path
        if full.exists() or alt.exists():
            ok += 1
            if args.verbose:
                print(f"  ✅ L0: {rel_path}")
        else:
            missing.append(("L0", rel_path))
            if args.verbose:
                print(f"  ❌ L0: {rel_path}")

    print("审计 L1 规范...")
    for rel_path in loader.L1_SPECS:
        full = loader.agents_dir / rel_path
        alt = loader.root / rel_path
        if full.exists() or alt.exists():
            ok += 1
            if args.verbose:
                print(f"  ✅ L1: {rel_path}")
        else:
            missing.append(("L1", rel_path))
            if args.verbose:
                print(f"  ❌ L1: {rel_path}")

    print("审计 L2 任务路由...")
    for task_type, config in TASK_ROUTING.items():
        for rel_path in config["l2_specs"]:
            full = loader.agents_dir / rel_path
            alt = loader.root / rel_path
            if full.exists() or alt.exists():
                ok += 1
                if args.verbose:
                    print(f"  ✅ L2: {rel_path} (type={task_type})")
            else:
                missing.append(("L2", rel_path, task_type))
                if args.verbose:
                    print(f"  ❌ L2: {rel_path} (type={task_type})")

    print()
    if missing:
        print(f"❌ 发现 {len(missing)} 个缺失文件（{ok} 个正常）：")
        for item in missing:
            if len(item) == 3:
                layer, path, task_type = item
                print(f"  [{layer}] {path} (任务类型: {task_type})")
            else:
                layer, path = item
                print(f"  [{layer}] {path}")
        return 1
    else:
        print(f"✅ 所有 {ok} 个规范文件均存在")
        return 0


def main():
    setup_safe_output()
    parser = argparse.ArgumentParser(description="L2 渐进式披露规范加载器")
    subparsers = parser.add_subparsers(dest="command", help="可用子命令")

    p_task = subparsers.add_parser("task", help="按任务描述加载规范")
    p_task.add_argument("task_description", help="任务描述文本")
    p_task.add_argument("--stage", default="execution", choices=["startup", "planning", "execution", "verification"], help="任务阶段")
    p_task.add_argument("--no-l1", action="store_true", help="不加载L1索引层")
    p_task.add_argument("-c", "--content", action="store_true", help="输出规范内容（默认仅输出清单）")
    p_task.add_argument("--max-chars", type=int, default=None, help="L2最大加载字符数")
    p_task.add_argument("--warn-missing", action="store_true", help="有缺失文件时返回错误码")
    p_task.add_argument("-v", "--verbose", action="store_true", help="输出详细加载日志（到stderr）")
    p_task.add_argument("--path", type=Path, default=None, help="项目根目录路径")

    p_layer = subparsers.add_parser("layer", help="按层加载规范")
    p_layer.add_argument("layer", choices=["L0", "L1", "all"], help="加载到指定层")
    p_layer.add_argument("-c", "--content", action="store_true", help="输出规范内容")
    p_layer.add_argument("-v", "--verbose", action="store_true", help="输出详细加载日志")
    p_layer.add_argument("--path", type=Path, default=None)

    p_list = subparsers.add_parser("list-types", help="列出所有支持的任务类型")

    p_audit = subparsers.add_parser("audit", help="审计所有路由引用的文件是否存在")
    p_audit.add_argument("-v", "--verbose", action="store_true", help="输出每个文件的审计结果")
    p_audit.add_argument("--path", type=Path, default=None)

    args = parser.parse_args()

    cmd_map = {
        "task": cmd_task,
        "layer": cmd_layer,
        "list-types": cmd_list_types,
        "audit": cmd_audit,
    }

    if not args.command:
        parser.print_help()
        return 1

    return cmd_map[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
