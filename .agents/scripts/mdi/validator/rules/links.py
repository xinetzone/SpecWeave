"""链接验证规则。

检查file:///绝对路径和相对链接有效性。
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ..constants import FILE_URL_RE, INLINE_LINK_RE
from ..models import ValidationReport
from ..utils import is_code_fence_context, find_line_number, find_project_root, try_depth_adjust

if TYPE_CHECKING:
    from ...models import MDIDocument


def validate_file_urls(content: str, report: ValidationReport) -> None:
    """检查并警告file:///绝对路径使用。"""
    for m in FILE_URL_RE.finditer(content):
        if is_code_fence_context(content, m.start()):
            continue
        line = content.count("\n", 0, m.start()) + 1
        report.add_issue(
            "warn", "W008",
            f"使用了file:///绝对路径: {m.group(0)[:80]}",
            line=line,
            suggestion="应使用相对路径引用项目内文件",
        )


def validate_relative_links(content: str, source_path: str, report: ValidationReport) -> None:
    """检查相对链接是否指向存在的文件。"""
    if source_path == "<doc>":
        return

    source_file = Path(source_path)
    if not source_file.exists():
        return

    base_dir = source_file.parent
    project_root = find_project_root(source_file)

    for m in INLINE_LINK_RE.finditer(content):
        if is_code_fence_context(content, m.start()):
            continue
        url = m.group(2).strip()

        if url.startswith("http://") or url.startswith("https://") or url.startswith("mailto:") or url.startswith("#"):
            continue
        if url.startswith("file:///"):
            continue

        url_path = url.split("#")[0]
        if not url_path:
            continue

        if url_path.startswith("/"):
            resolved = (project_root / url_path.lstrip("/")).resolve() if project_root else None
        else:
            resolved = (base_dir / url_path).resolve()

        if resolved and not resolved.exists():
            depth_adjusted = try_depth_adjust(url_path, base_dir)
            if depth_adjusted is None:
                line = content.count("\n", 0, m.start()) + 1
                report.add_issue(
                    "warn", "W007",
                    f"内部相对链接可能无效: [{m.group(1)}]({url_path})",
                    line=line,
                    suggestion="检查目标文件是否存在或路径是否正确",
                )
