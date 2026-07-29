"""Mermaid 语法安全检查模块（重构版）。

采用策略模式和职责拆分的新架构，保持与旧版 mermaid.py 的完全向后兼容。
"""

from .common import (
    MERMAID_FENCE_RE,
    CHINESE_CHARS_RE,
    LIST_TRIGGER_RE,
    SPECIAL_CHARS,
    detect_diagram_type,
    text_needs_quotes,
    state_text_needs_quotes,
    has_list_trigger,
    line_from_offset,
    strip_inline_comment,
    check_empty_lines,
    check_backslash_n,
    fix_backslash_n,
    fix_empty_lines,
    check_list_trigger,
    strip_mindmap_shape,
)
from .scanner import FileScanner
from .registry import (
    CheckerRegistry,
    FixerRegistry,
    create_default_checker_registry,
    create_default_fixer_registry,
)
from .processor import process_mermaid_fences
from .runner import (
    ConsoleColors,
    MermaidRunner,
)

__all__ = [
    "MERMAID_FENCE_RE",
    "CHINESE_CHARS_RE",
    "LIST_TRIGGER_RE",
    "SPECIAL_CHARS",
    "detect_diagram_type",
    "text_needs_quotes",
    "state_text_needs_quotes",
    "has_list_trigger",
    "line_from_offset",
    "strip_inline_comment",
    "check_empty_lines",
    "check_backslash_n",
    "fix_backslash_n",
    "fix_empty_lines",
    "check_list_trigger",
    "strip_mindmap_shape",
    "FileScanner",
    "CheckerRegistry",
    "FixerRegistry",
    "create_default_checker_registry",
    "create_default_fixer_registry",
    "process_mermaid_fences",
    "ConsoleColors",
    "MermaidRunner",
]
