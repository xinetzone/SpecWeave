"""Mermaid 修复器抽象基类。"""

from abc import ABC, abstractmethod
from typing import List, Tuple

from ..common import fix_empty_lines, fix_backslash_n


class BaseDiagramFixer(ABC):
    """图表修复器抽象基类。"""

    @abstractmethod
    def get_diagram_type(self) -> str:
        pass

    @abstractmethod
    def fix(self, block_text: str) -> Tuple[str, List[str]]:
        pass
