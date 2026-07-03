"""link_fixer 数据模型模块。

定义链接修复记录的数据结构。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class LinkFix:
    """记录一次链接修复操作。"""
    file_path: Path
    line_num: int
    link_text: str
    old_url: str
    new_url: str
    fix_type: str
    reason: str = ""

    def __str__(self) -> str:
        return f"  L{self.line_num}: [{self.link_text}] {self.old_url} → {self.new_url} ({self.fix_type})"
