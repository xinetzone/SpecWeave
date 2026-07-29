"""状态图修复器。"""

import re
from typing import List, Tuple

from ..common import state_text_needs_quotes, fix_empty_lines, fix_backslash_n
from .base import BaseDiagramFixer


class StateDiagramFixer(BaseDiagramFixer):
    def get_diagram_type(self) -> str:
        return "stateDiagram"

    def fix(self, block_text: str) -> Tuple[str, List[str]]:
        fixes = []
        text = block_text

        newline_before = text.count("\n")
        text = fix_empty_lines(text)
        if text.count("\n") < newline_before:
            fixes.append("空行")

        state_label_pat = re.compile(r"^(\s*state\s+)(\S+)\s*:\s*(.+)$", re.MULTILINE)

        def _state_label_rep(m):
            indent, sid, label = m.group(1), m.group(2), m.group(3).strip()
            needs_q = state_text_needs_quotes(label)
            if needs_q:
                return f'{indent}{sid} : "{label}"'
            return m.group(0)

        text_before = text
        text = state_label_pat.sub(_state_label_rep, text)
        if text != text_before:
            fixes.append("状态描述引号")

        note_pat = re.compile(r"^(\s*note\s+(?:right|left|over)\s+of\s+\S+\s*:\s*)(.+)$", re.MULTILINE)

        def _note_rep(m):
            prefix, note_text = m.group(1), m.group(2).strip()
            needs_q = state_text_needs_quotes(note_text)
            if needs_q:
                return f'{prefix}"{note_text}"'
            return m.group(0)

        text_before = text
        text = note_pat.sub(_note_rep, text)
        if text != text_before:
            fixes.append("note文本引号")

        trans_pat = re.compile(
            r"^(\s*(?:" + r'"[^"]*"' + r"|\[[\*]\]|\S+)\s*-->\s*(?:"
            + r'"[^"]*"' + r"|\[[\*]\]|\S+)\s*:\s*)(.+)$",
            re.MULTILINE,
        )

        def _trans_label_rep(m):
            prefix, label = m.group(1), m.group(2).strip()
            needs_q = state_text_needs_quotes(label)
            if needs_q:
                return f'{prefix}"{label}"'
            return m.group(0)

        text_before = text
        text = trans_pat.sub(_trans_label_rep, text)
        if text != text_before:
            fixes.append("迁移标签引号")

        text_before = text
        text = fix_backslash_n(text)
        if text != text_before:
            fixes.append("换行符(\\n→<br/>)")

        return text, fixes
