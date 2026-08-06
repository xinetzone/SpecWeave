"""思维导图修复器。"""


# 版本校验：相对导入共享库（depth=2）
from ...python310_version_check import enforce_python310

enforce_python310()

from typing import List, Tuple

from ..common import fix_empty_lines
from .base import BaseDiagramFixer


class MindmapFixer(BaseDiagramFixer):
    def get_diagram_type(self) -> str:
        return "mindmap"

    def fix(self, block_text: str) -> Tuple[str, List[str]]:
        fixes = []
        text = block_text
        newline_before = text.count("\n")
        text = fix_empty_lines(text)
        if text.count("\n") < newline_before:
            fixes.append("空行")
        return text, fixes

