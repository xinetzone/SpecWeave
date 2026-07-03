"""link_fixer 文件处理模块。

单文件链接修复、目录递归修复等处理逻辑。
"""

from __future__ import annotations

from pathlib import Path

from .constants import INLINE_LINK_RE
from .models import LinkFix
from .resolver import fix_link_url
from .utils import is_code_fence_context


def fix_file_links(
    file_path: Path,
    project_root: Path,
    rename_map: dict[str, str] | None = None,
    line_remap: dict[str, dict[int, int]] | None = None,
    prefer_subdir: Path | None = None,
    dry_run: bool = False,
) -> list[LinkFix]:
    """修复单个 Markdown 文件中的断链。"""
    file_path = file_path.resolve()
    content = file_path.read_text(encoding="utf-8")
    fixes: list[LinkFix] = []
    new_content = content

    offset = 0
    for m in INLINE_LINK_RE.finditer(content):
        text = m.group(1)
        old_url = m.group(2).strip()

        if is_code_fence_context(content, m.start()):
            continue

        result = fix_link_url(
            old_url,
            file_path,
            project_root,
            rename_map=rename_map,
            line_remap=line_remap,
            prefer_subdir=prefer_subdir,
            link_text=text,
        )

        if result is None:
            continue

        new_url, fix_type, reason = result
        old_link = f"[{text}]({old_url})"
        new_link = f"[{text}]({new_url})"

        start = m.start() + offset
        end = m.end() + offset
        new_content = new_content[:start] + new_link + new_content[end:]
        offset += len(new_link) - len(old_link)

        line_num = content[:m.start()].count("\n") + 1
        fixes.append(LinkFix(
            file_path=file_path,
            line_num=line_num,
            link_text=text,
            old_url=old_url,
            new_url=new_url,
            fix_type=fix_type,
            reason=reason,
        ))

    if fixes and not dry_run:
        file_path.write_text(new_content, encoding="utf-8")

    return fixes


def fix_directory_links(
    root_dir: Path,
    project_root: Path,
    rename_map: dict[str, str] | None = None,
    line_remap: dict[str, dict[int, int]] | None = None,
    prefer_subdir: Path | None = None,
    dry_run: bool = True,
    exclude_dirs: set[str] | None = None,
) -> list[LinkFix]:
    """递归修复目录下所有 Markdown 文件中的断链。"""
    try:
        from constants import EXCLUDED_DIRS as _BASE_EXCLUDED
    except ImportError:
        _BASE_EXCLUDED = {".git", "vendor", ".venv", "__pycache__", "node_modules", ".temp"}

    if exclude_dirs is None:
        exclude_dirs = set()
    all_excluded = _BASE_EXCLUDED | exclude_dirs

    root_dir = root_dir.resolve()
    project_root = project_root.resolve()
    all_fixes: list[LinkFix] = []

    for md_path in sorted(root_dir.rglob("*.md")):
        parts = set(md_path.parts)
        if all_excluded & parts:
            continue
        fixes = fix_file_links(
            md_path,
            project_root,
            rename_map=rename_map,
            line_remap=line_remap,
            prefer_subdir=prefer_subdir,
            dry_run=dry_run,
        )
        all_fixes.extend(fixes)

    return all_fixes
