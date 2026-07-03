"""link_fixer 常量定义模块。

正则表达式、模板链接集合、通用文件名常量等。
"""

from __future__ import annotations

import re

FILE_URL_RE = re.compile(
    r"file:///([A-Za-z]:/[^\s)]+|/[^\s)]+)"
)

INLINE_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

TEMPLATE_LINK_TEXTS = {
    "link", "path", "url", "来源", "pattern-name.md",
    "old_name.md", "new_name.md", "xxx", "xxx.md",
}

TEMPLATE_URL_PATTERNS = [
    re.compile(r"^path(/|$)"),
    re.compile(r"^URL$"),
]

_GENERIC_FILENAMES = {"README.md", "index.md", ".gitkeep"}
_DIR_FILENAMES = {"README.md"}
