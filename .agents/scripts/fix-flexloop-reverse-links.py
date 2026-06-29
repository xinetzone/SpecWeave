#!/usr/bin/env python3
"""
修复 flexloop 子模块中遗留的反向依赖 Markdown 链接。

功能：
1. 扫描指定子模块目录中的 .md 文件，检测指向子模块外部的相对链接
2. 对于指向原项目路径（../../../apps/chaos/）的遗留链接，自动转换为代码引用（保留文件名，去掉超链接）
3. 生成详细修复报告
4. 支持 --dry-run 模式预览变更

使用方式：
  python .agents/scripts/fix-flexloop-reverse-links.py              # 执行修复
  python .agents/scripts/fix-flexloop-reverse-links.py --dry-run    # 预览变更
  python .agents/scripts/fix-flexloop-reverse-links.py --path vendor/flexloop/docs/topics  # 指定目录
"""

import sys
import io
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
os.environ["PYTHONIOENCODING"] = "utf-8"

import argparse
import re
from pathlib import Path
from dataclasses import dataclass


@dataclass
class LinkFix:
    file: Path
    line_num: int
    original: str
    fixed: str
    link_target: str
    fix_type: str


def fix_external_markdown_link(match: re.Match) -> tuple[str, str, str]:
    """处理单个 Markdown 链接，返回 (修复后文本, 链接目标, 修复类型)。"""
    full_match = match.group(0)
    link_text = match.group(1)
    link_target = match.group(2)

    target_clean = link_target.split("#")[0].split("?")[0].strip()

    if target_clean.startswith(("http", "mailto:", "/", "file:")):
        return full_match, link_target, "external_skip"

    if not target_clean.startswith("../"):
        return full_match, link_target, "internal_skip"

    if "../../../apps/chaos/" in target_clean.replace("\\", "/"):
        filename = Path(target_clean).name
        stripped_text = link_text.strip()
        if stripped_text.startswith("`") and stripped_text.endswith("`"):
            fixed = link_text
        else:
            fixed = f"{link_text}（`{filename}`）"
        return fixed, link_target, "legacy_chaos_ref"

    return full_match, link_target, "unknown_external"


def process_file(md_file: Path, sm_dir_resolved: Path, dry_run: bool = False) -> list[LinkFix]:
    """处理单个 Markdown 文件，返回修复列表。"""
    fixes = []
    content = md_file.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    new_lines = []
    changed = False

    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    for i, line in enumerate(lines, 1):
        original_line = line
        matches = list(link_pattern.finditer(line))
        if not matches:
            new_lines.append(line)
            continue

        line_fixes = []
        new_line = line
        for m in reversed(matches):
            fixed_text, link_target, fix_type = fix_external_markdown_link(m)
            if fix_type in ("legacy_chaos_ref",):
                start, end = m.span()
                new_line = new_line[:start] + fixed_text + new_line[end:]
                line_fixes.append(LinkFix(
                    file=md_file,
                    line_num=i,
                    original=m.group(0),
                    fixed=fixed_text,
                    link_target=link_target,
                    fix_type=fix_type,
                ))
                changed = True

        new_lines.append(new_line)
        fixes.extend(line_fixes)

    if changed and not dry_run:
        md_file.write_text("".join(new_lines), encoding="utf-8")

    return fixes


def scan_and_fix(
    submodule_dir: Path,
    target_subdir: str = "",
    dry_run: bool = False
) -> tuple[list[LinkFix], list[str]]:
    """扫描并修复子模块中的遗留反向链接。

    Args:
        submodule_dir: 子模块根目录
        target_subdir: 仅扫描指定子目录（如 "docs/topics"），空则扫描全部
        dry_run: True 则仅预览不修改

    Returns:
        (修复列表, 警告/信息列表)
    """
    all_fixes = []
    messages = []

    sm_dir = submodule_dir
    if target_subdir:
        sm_dir = submodule_dir / target_subdir
    if not sm_dir.exists():
        return all_fixes, [f"目录不存在: {sm_dir}"]

    sm_resolved = submodule_dir.resolve()

    md_files = list(sm_dir.rglob("*.md"))
    messages.append(f"扫描目录: {sm_dir}")
    messages.append(f"找到 {len(md_files)} 个 Markdown 文件")

    for md_file in sorted(md_files):
        if not md_file.is_file():
            continue
        rel_parts = md_file.relative_to(submodule_dir).parts
        if any(p in (".git", "__pycache__", "node_modules") for p in rel_parts):
            continue
        fixes = process_file(md_file, sm_resolved, dry_run=dry_run)
        all_fixes.extend(fixes)

    return all_fixes, messages


def print_report(fixes: list[LinkFix], messages: list[str], dry_run: bool):
    """打印修复报告。"""
    mode_str = "[DRY-RUN 预览模式]" if dry_run else "[执行修复]"
    print(f"\n{'='*60}")
    print(f"  flexloop 遗留反向链接修复工具 {mode_str}")
    print(f"{'='*60}\n")

    for msg in messages:
        print(f"  {msg}")

    print(f"\n  发现 {len(fixes)} 处需要修复的链接:\n")

    by_file: dict[Path, list[LinkFix]] = {}
    for fix in fixes:
        by_file.setdefault(fix.file, []).append(fix)

    for file_path, file_fixes in sorted(by_file.items()):
        print(f"  [FILE] {file_path}")
        for fix in file_fixes:
            print(f"     L{fix.line_num}: {fix.original}")
            print(f"           -> {fix.fixed}")
        print()

    fix_types: dict[str, int] = {}
    for fix in fixes:
        fix_types[fix.fix_type] = fix_types.get(fix.fix_type, 0) + 1
    print(f"  修复统计:")
    for ftype, count in sorted(fix_types.items()):
        type_desc = {
            "legacy_chaos_ref": "AgentForge遗留引用 -> 代码引用",
        }.get(ftype, ftype)
        print(f"    - {type_desc}: {count} 处")

    if not dry_run and fixes:
        print(f"\n  [OK] 已完成 {len(fixes)} 处修复")
    elif dry_run and fixes:
        print(f"\n  [WARN] 以上为预览，实际修复请去掉 --dry-run 参数")
    else:
        print(f"\n  [OK] 无需修复，所有链接正常")
    print()


def main():
    parser = argparse.ArgumentParser(description="修复 flexloop 子模块中遗留的反向依赖 Markdown 链接")
    parser.add_argument("--path", default="vendor/flexloop", help="子模块路径（默认: vendor/flexloop）")
    parser.add_argument("--subdir", default="docs/topics", help="仅扫描指定子目录（默认: docs/topics）")
    parser.add_argument("--dry-run", action="store_true", help="仅预览变更，不实际修改文件")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    submodule_dir = project_root / args.path

    if not submodule_dir.exists():
        print(f"[ERROR] 子模块目录不存在: {submodule_dir}")
        print(f"        请先初始化子模块: git submodule update --init {args.path}")
        sys.exit(1)
    fixes, messages = scan_and_fix(
        submodule_dir=submodule_dir,
        target_subdir=args.subdir,
        dry_run=args.dry_run,
    )
    print_report(fixes, messages, args.dry_run)

    return 0 if not fixes or args.dry_run else 1


if __name__ == "__main__":
    sys.exit(main())
