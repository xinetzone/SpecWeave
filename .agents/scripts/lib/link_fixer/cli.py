"""link_fixer 命令行入口与便捷API模块。

一站式断链修复便捷函数、项目根目录自动推断、CLI参数解析与主流程。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .models import LinkFix
from .processor import fix_directory_links, fix_file_links
from .report import print_fix_report


def _infer_project_root(start: Path) -> Path:
    """从起始路径向上查找包含 .agents/ 目录的项目根目录。"""
    current = start if start.is_dir() else start.parent
    for candidate in [current, *current.parents]:
        if (candidate / ".agents").is_dir():
            return candidate.resolve()
    return Path.cwd().resolve()


def fix_broken_links(
    target: str | Path,
    *,
    project_root: str | Path | None = None,
    rename_map: dict[str, str] | None = None,
    line_remap: dict[str, dict[int, int]] | None = None,
    prefer_subdir: str | Path | None = None,
    exclude_dirs: set[str] | None = None,
    dry_run: bool = True,
    verbose: bool = True,
) -> list[LinkFix]:
    """一站式断链修复便捷函数，自动推断项目根目录，一行调用即可修复。

    Args:
        target: 要修复的目录或文件路径（字符串或 Path 对象）。
        project_root: 项目根目录，默认自动从 target 向上查找含 .agents/ 的目录。
        rename_map: 文件名重命名映射 ``{"旧名.html": "新名.html"}``。
        line_remap: 行号重映射 ``{"文件名.md": {旧行号: 新行号}}``。
        prefer_subdir: 查找目标文件时优先搜索的子目录（如 ``"apps"``）。
        exclude_dirs: 额外排除的目录名集合。
        dry_run: True=仅预览不写入（默认），False=实际写入修复。
        verbose: True=打印修复报告，False=静默返回结果。

    Returns:
        修复操作列表（LinkFix 对象）。

    Examples:
        >>> # 最简用法：预览整个项目的断链
        >>> fixes = fix_broken_links(".")
        >>>
        >>> # 修复指定目录，同时处理文件重命名
        >>> fixes = fix_broken_links(
        ...     "apps/myapp",
        ...     rename_map={"old.html": "new.html"},
        ...     dry_run=False,
        ... )
        >>>
        >>> # 修复单个文件
        >>> fixes = fix_broken_links("docs/README.md", dry_run=False)
    """
    target_path = Path(target).resolve()

    if project_root is None:
        project_root_path = _infer_project_root(target_path)
    else:
        project_root_path = Path(project_root).resolve()

    prefer_subdir_path = Path(prefer_subdir).resolve() if prefer_subdir else None
    if prefer_subdir_path is not None and not prefer_subdir_path.is_absolute():
        prefer_subdir_path = (project_root_path / prefer_subdir).resolve()

    if verbose:
        mode = "预览（dry-run）" if dry_run else "实际修复"
        print(f"[link_fixer] 目标: {target_path}")
        print(f"[link_fixer] 项目根: {project_root_path}")
        print(f"[link_fixer] 模式: {mode}")

    if target_path.is_file():
        fixes = fix_file_links(
            target_path, project_root_path,
            rename_map=rename_map,
            line_remap=line_remap,
            prefer_subdir=prefer_subdir_path,
            dry_run=dry_run,
        )
    else:
        fixes = fix_directory_links(
            target_path, project_root_path,
            rename_map=rename_map,
            line_remap=line_remap,
            prefer_subdir=prefer_subdir_path,
            dry_run=dry_run,
            exclude_dirs=exclude_dirs,
        )

    if verbose:
        print_fix_report(fixes, dry_run=dry_run)

    return fixes


def main() -> None:
    """CLI 入口函数。"""
    parser = argparse.ArgumentParser(
        description="Markdown 断链自动修复工具",
        epilog="示例:\n"
               "  python -m lib.link_fixer --path apps/myapp           # 预览修复\n"
               "  python -m lib.link_fixer --path . --apply             # 修复全项目\n"
               "  python -m lib.link_fixer --path docs/README.md --apply\n"
               "  python -m lib.link_fixer --path apps --rename 旧.html=新.html",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--path", type=Path, required=True, help="要修复的目录或文件路径")
    parser.add_argument("--project-root", type=Path, default=None, help="项目根目录（默认自动推断）")
    parser.add_argument("--apply", action="store_true", default=False, help="实际写入修复（默认 dry-run 预览）")
    parser.add_argument("--prefer-subdir", type=str, default=None, help="查找目标文件时优先搜索的子目录")
    parser.add_argument("--exclude", type=str, nargs="*", default=[], help="额外排除的目录名")
    parser.add_argument(
        "--rename",
        nargs="*",
        default=[],
        metavar="OLD=NEW",
        help="文件名重命名映射，如 --rename 竹简悟道.html=竹简悟道_完整版.html",
    )
    args = parser.parse_args()

    rename_map = {}
    for mapping in args.rename:
        if "=" in mapping:
            old, new = mapping.split("=", 1)
            rename_map[old] = new

    exclude_set = set(args.exclude) if args.exclude else None

    fix_broken_links(
        target=args.path,
        project_root=args.project_root,
        rename_map=rename_map or None,
        prefer_subdir=args.prefer_subdir,
        exclude_dirs=exclude_set,
        dry_run=not args.apply,
        verbose=True,
    )


if __name__ == "__main__":
    main()
