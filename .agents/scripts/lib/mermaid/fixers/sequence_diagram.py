"""序列图修复器。"""

import re
from typing import List, Tuple

from ..common import text_needs_quotes, fix_empty_lines
from .base import BaseDiagramFixer


class SequenceDiagramFixer(BaseDiagramFixer):
    def get_diagram_type(self) -> str:
        return "sequenceDiagram"

    def fix(self, block_text: str) -> Tuple[str, List[str]]:
        fixes = []
        text = block_text

        newline_before = text.count("\n")
        text = fix_empty_lines(text)
        if text.count("\n") < newline_before:
            fixes.append("空行")

        participant_pat = re.compile(
            r"^(\s*participant\s+)(\S+)\s+as\s+(.+)$", re.MULTILINE
        )

        def _part_rep(m):
            indent, pid, alias = m.group(1), m.group(2), m.group(3).strip()
            if text_needs_quotes(alias) and not (alias.startswith('"') and alias.endswith('"')):
                return f'{indent}{pid} as "{alias}"'
            return m.group(0)

        text_before = text
        text = participant_pat.sub(_part_rep, text)
        if text != text_before:
            fixes.append("participant别名引号")

        return text, fixes
