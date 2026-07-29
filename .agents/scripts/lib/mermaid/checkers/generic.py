import re
from typing import List, Tuple

from .base import BaseDiagramChecker


class PieChecker(BaseDiagramChecker):
    def __init__(self):
        pass

    def get_diagram_type(self) -> str:
        return "pie"

    def _check_specific_rules(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        return []


class GanttChecker(BaseDiagramChecker):
    def __init__(self):
        self.title_pat = re.compile(r"^\s*title\s+(.+)$", re.MULTILINE)

    def get_diagram_type(self) -> str:
        return "gantt"

    def _check_specific_rules(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        issues = []
        for m in self.title_pat.finditer(block_text):
            title_text = m.group(1).strip()
            if title_text.startswith('"') or title_text.startswith("'"):
                lb = block_text[:m.start()].count("\n") + 1
                issues.append((start_line + lb - 1, "warning",
                              'gantt title 不需要引号包裹，Mermaid会自动解析'))
        return issues


class TimelineChecker(BaseDiagramChecker):
    def __init__(self):
        pass

    def get_diagram_type(self) -> str:
        return "timeline"

    def _check_specific_rules(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        return []


class XyChartChecker(BaseDiagramChecker):
    def __init__(self):
        pass

    def get_diagram_type(self) -> str:
        return "xychart-beta"

    def _check_specific_rules(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        return []


class QuadrantChecker(BaseDiagramChecker):
    def __init__(self):
        pass

    def get_diagram_type(self) -> str:
        return "quadrantchart"

    def _check_specific_rules(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        return []
