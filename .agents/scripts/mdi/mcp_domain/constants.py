"""MCP Domain 常量定义 - 正则表达式和类型映射。"""

from __future__ import annotations

import re
from typing import Any

try:
    from markdown_it import MarkdownIt
    from mdit_py_plugins.colon_fence import colon_fence_plugin
    from mdit_py_plugins.front_matter import front_matter_plugin
    HAS_MDIT = True
except ImportError:
    HAS_MDIT = False

_DIRECTIVE_RE = re.compile(r'^\{(\w[\w:.-]*)\}\s*(.*)$')
_OPTION_RE = re.compile(r'^:([\w][\w\s\-]*?)(\??)\s*:\s*(.*)$')
_COLON_OPEN_RE = re.compile(r'^(:{3,})(\{[\w][\w:.-]*\})\s*(.*)$')
_COLON_CLOSE_RE = re.compile(r'^(:{3,})\s*$')
_BACKTICK_OPEN_RE = re.compile(r'^(`{3,})(\{[\w][\w:.-]*\})\s*(.*)$')
_BACKTICK_CLOSE_RE = re.compile(r'^(`{3,})\s*$')

_JSON_SCHEMA_TYPE_MAP: dict[str, dict[str, Any]] = {
    "string": {"type": "string"},
    "str": {"type": "string"},
    "integer": {"type": "integer"},
    "int": {"type": "integer"},
    "number": {"type": "number"},
    "float": {"type": "number"},
    "boolean": {"type": "boolean"},
    "bool": {"type": "boolean"},
    "array": {"type": "array"},
    "object": {"type": "object"},
}

_PY_TYPE_MAP: dict[str, type] = {
    "string": str, "str": str,
    "integer": int, "int": int,
    "number": float, "float": float,
    "boolean": bool, "bool": bool,
    "array": list,
    "object": dict,
}


def _make_parser() -> "MarkdownIt":
    return MarkdownIt("commonmark").use(front_matter_plugin).use(colon_fence_plugin)
