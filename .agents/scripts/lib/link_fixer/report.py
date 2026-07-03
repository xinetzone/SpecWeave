"""link_fixer 修复报告输出模块。

格式化并打印链接修复结果，包括按类型统计和按文件分组展示。
"""

from __future__ import annotations

from pathlib import Path

from .models import LinkFix


_TYPE_NAMES = {
    "absolute_to_relative": "绝对路径→相对路径",
    "same_file_anchor": "同文件锚点简化",
    "filename_mapped": "文件名映射",
    "broken_relative_fixed": "相对路径断链修复（文件名搜索）",
    "depth_adjusted": "相对路径层级校正",
    "dir_slash": "目录链接斜杠补全",
    "line_remapped": "行号重映射",
}


def print_fix_report(fixes: list[LinkFix], dry_run: bool = True) -> None:
    """打印修复报告。"""
    if not fixes:
        print("  未发现需要修复的断链。")
        return

    mode = "预览（未写入）" if dry_run else "已修复"
    print(f"\n链接修复{mode}，共 {len(fixes)} 处：")

    by_type: dict[str, int] = {}
    for fix in fixes:
        by_type[fix.fix_type] = by_type.get(fix.fix_type, 0) + 1

    type_summary = ", ".join(f"{_TYPE_NAMES.get(t, t)}: {c}" for t, c in sorted(by_type.items()))
    print(f"  修复类型分布: {type_summary}")

    by_file: dict[Path, list[LinkFix]] = {}
    for fix in fixes:
        by_file.setdefault(fix.file_path, []).append(fix)

    for file_path, file_fixes in sorted(by_file.items()):
        try:
            display = file_path.relative_to(Path.cwd())
        except ValueError:
            display = file_path
        print(f"\n  {display}（{len(file_fixes)} 处）：")
        for fix in file_fixes:
            print(f"  L{fix.line_num}: [{fix.link_text}] {fix.old_url}")
            print(f"         → {fix.new_url}  [{fix.fix_type}]")
