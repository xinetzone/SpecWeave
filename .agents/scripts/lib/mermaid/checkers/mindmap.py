import re
from typing import List, Tuple

from ..common import CHINESE_CHARS_RE, check_list_trigger, strip_mindmap_shape, has_list_trigger
from .base import BaseDiagramChecker


class MindmapChecker(BaseDiagramChecker):
    def __init__(self):
        pass

    def get_diagram_type(self) -> str:
        return "mindmap"

    def _check_specific_rules(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        issues = []
        lines = block_text.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped == "mindmap" or stripped.startswith("mindmap"):
                if i == 0 or (i == 0 and stripped.lower().startswith("mindmap")):
                    continue
            if stripped.startswith("mindmap"):
                continue
            node_text = strip_mindmap_shape(stripped)
            if not node_text:
                continue
            lb = i + 1
            w = check_list_trigger(node_text, i, start_line, 'mindmap节点')
            if w:
                issues.append(w)
            if ":" in node_text and not node_text.startswith('"'):
                issues.append((start_line + lb - 1, "warning",
                              f'mindmap节点「{node_text[:20]}」含冒号，可能导致解析错误，建议避免'))
        return issues
