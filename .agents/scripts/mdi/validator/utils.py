"""MDI验证器工具函数。

提供代码块上下文检测、行号查找等通用工具。
"""

from __future__ import annotations

from pathlib import Path


def is_code_fence_context(content: str, pos: int) -> bool:
    """判断位置是否在代码块内。"""
    before = content[:pos]
    fence_count = before.count("```")
    if fence_count % 2 == 1:
        return True
    line_start = before.rfind("\n") + 1
    line_before = before[line_start:]
    tick_count = 0
    i = 0
    while i < len(line_before):
        if line_before[i] == "`":
            run = 1
            while i + run < len(line_before) and line_before[i + run] == "`":
                run += 1
            if run <= 2:
                tick_count += 1
            i += run
        else:
            i += 1
    return tick_count % 2 == 1


def find_line_number(content: str, search_text: str, start_from: int = 0) -> int | None:
    """在文本中查找指定文本所在行号。"""
    idx = content.find(search_text, start_from)
    if idx == -1:
        return None
    return content.count("\n", 0, idx) + 1


def find_project_root(start: Path) -> Path | None:
    """从起始路径向上查找包含.agents/的项目根目录。"""
    current = start if start.is_dir() else start.parent
    for candidate in [current, *current.parents]:
        if (candidate / ".agents").is_dir():
            return candidate.resolve()
    return None


def try_depth_adjust(url_path: str, base_dir: Path) -> Path | None:
    """尝试调整相对路径深度（最多向上3级尝试查找）。"""
    cleaned = url_path.replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    parts = cleaned.split("/")
    dotdot_count = 0
    for p in parts:
        if p == "..":
            dotdot_count += 1
        else:
            break
    remaining = parts[dotdot_count:]
    if not remaining:
        return None
    for delta in range(1, 4):
        new_parts = [".."] * (dotdot_count + delta) + remaining
        candidate = (base_dir / "/".join(new_parts)).resolve()
        if candidate.exists():
            return candidate
    return None
