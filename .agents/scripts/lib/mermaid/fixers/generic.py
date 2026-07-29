"""通用修复器。"""


# 版本校验：相对导入共享库（depth=2）
from ...python310_version_check import enforce_python310

enforce_python310()

from typing import List, Tuple

from ..common import fix_empty_lines
from .base import BaseDiagramFixer


class PieFixer(BaseDiagramFixer):
    def get_diagram_type(self) -> str:
        return "pie"

    def fix(self, block_text: str) -> Tuple[str, List[str]]:
        fixes = []
        text = block_text
        newline_before = text.count("\n")
        text = fix_empty_lines(text)
        if text.count("\n") < newline_before:
            fixes.append("空行")
        return text, fixes


class GanttFixer(BaseDiagramFixer):
    def get_diagram_type(self) -> str:
        return "gantt"

    def fix(self, block_text: str) -> Tuple[str, List[str]]:
        fixes = []
        text = block_text
        newline_before = text.count("\n")
        text = fix_empty_lines(text)
        if text.count("\n") < newline_before:
            fixes.append("空行")
        return text, fixes


class GenericFixer(BaseDiagramFixer):
    def __init__(self, diagram_type: str = "generic"):
        self._diagram_type = diagram_type

    def get_diagram_type(self) -> str:
        return self._diagram_type

    def fix(self, block_text: str) -> Tuple[str, List[str]]:
        fixes = []
        text = block_text
        newline_before = text.count("\n")
        text = fix_empty_lines(text)
        if text.count("\n") < newline_before:
            fixes.append("空行")
        return text, fixes

