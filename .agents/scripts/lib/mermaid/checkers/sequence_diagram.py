import re
from typing import List, Tuple

from ..common import CHINESE_CHARS_RE, text_needs_quotes
from .base import BaseDiagramChecker


class SequenceDiagramChecker(BaseDiagramChecker):
    def __init__(self):
        self.participant_pat = re.compile(
            r"^\s*participant\s+(\S+)\s+as\s+(.+)$", re.MULTILINE
        )

    def get_diagram_type(self) -> str:
        return "sequenceDiagram"

    def _check_specific_rules(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        issues = []

        for m in self.participant_pat.finditer(block_text):
            alias = m.group(2).strip()
            lb = block_text[:m.start()].count("\n") + 1
            if text_needs_quotes(alias) and not (alias.startswith('"') and alias.endswith('"')):
                issues.append((start_line + lb - 1, "error",
                              f'participant 别名「{alias[:20]}」含中文/空格但未加双引号'))

        return issues
