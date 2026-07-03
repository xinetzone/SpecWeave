"""vendor VERSION.md 解析模块。

VERSION.md 表格解析、子模块类型判断、commit提取等功能。
"""

from __future__ import annotations

import re
from pathlib import Path


def _parse_version_md_table(version_md_path: Path) -> tuple[list[str], list[list[str]]]:
    """解析 VERSION.md 中的 Markdown 表格，返回 (表头列表, 数据行列表)。

    表头和数据行都按列分割为字符串列表（已 strip）。
    如果文件不存在或无表格，返回 ([], [])。
    """
    if not version_md_path.exists():
        return [], []
    content = version_md_path.read_text(encoding="utf-8")
    headers: list[str] = []
    rows: list[list[str]] = []
    in_table = False
    separator_seen = False

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table and separator_seen:
                break
            continue
        cells = [c.strip() for c in stripped.split("|")]
        cells = [c for c in cells if c != ""]
        if not cells:
            continue
        if not in_table:
            headers = cells
            in_table = True
            continue
        if not separator_seen:
            if all(re.match(r'^[-:]+$', c) for c in cells):
                separator_seen = True
            else:
                headers = cells
            continue
        rows.append(cells)

    return headers, rows


def _get_submodule_type(project_root: Path, submodule_name: str) -> str:
    """判断子模块类型：third_party（第三方只读）或 owned_collab（自有协作）。

    读取 vendor/VERSION.md 表格，查找包含 submodule_name 的表格行，
    检查"类型"列值是否为 "owned_collab"；如果 VERSION.md 中没有类型列
    或找不到条目，默认返回 "third_party"（向后兼容）。
    """
    vendor_dir = project_root / "vendor"
    version_md = vendor_dir / "VERSION.md"
    headers, rows = _parse_version_md_table(version_md)

    type_col_idx = None
    for idx, h in enumerate(headers):
        if "类型" in h:
            type_col_idx = idx
            break

    if type_col_idx is None:
        return "third_party"

    for row in rows:
        if len(row) > 0 and row[0] == submodule_name:
            if type_col_idx < len(row) and row[type_col_idx].strip() == "owned_collab":
                return "owned_collab"
            return "third_party"

    return "third_party"


def _parse_version_md_for_submodule(version_md_path: Path, submodule_name: str) -> str | None:
    """解析 VERSION.md 中指定 submodule 的版本/commit 信息。

    返回条目字符串（表格行），未找到则返回 None。
    """
    if not version_md_path.exists():
        return None
    content = version_md_path.read_text(encoding="utf-8")
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("|") and submodule_name in line:
            cells = [c.strip() for c in line.split("|")]
            cells = [c for c in cells if c]
            if len(cells) >= 1 and cells[0] == submodule_name:
                return line
    return None


def _extract_commit_from_version_entry(entry_line: str) -> str | None:
    """从 VERSION.md 表格行中提取 commit 哈希。"""
    match = re.search(r'\b([0-9a-f]{7,40})\b', entry_line)
    if match:
        return match.group(1)
    return None
