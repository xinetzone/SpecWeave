"""Mermaid 检查器抽象基类。"""

from abc import ABC, abstractmethod
from typing import List, Tuple

from ..common import check_empty_lines, check_backslash_n


class BaseDiagramChecker(ABC):
    """图表检查器抽象基类。

    定义了检查流程模板：空行检查 → 特定规则检查 → 换行符检查。
    子类需实现 get_diagram_type() 和 _check_specific_rules()。
    """

    @abstractmethod
    def get_diagram_type(self) -> str:
        """返回该检查器处理的图表类型。"""
        pass

    def check(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        """模板方法：执行完整检查流程。

        流程：
        1. 空行检查 (check_empty_lines)
        2. 特定图表类型规则检查 (_check_specific_rules)
        3. \\n 换行符检查 (check_backslash_n)
        """
        issues = []
        issues.extend(check_empty_lines(block_text, start_line))
        issues.extend(self._check_specific_rules(block_text, start_line))
        issues.extend(check_backslash_n(block_text, start_line))
        return issues

    @abstractmethod
    def _check_specific_rules(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        """检查特定图表类型的规则，子类必须实现。"""
        pass
