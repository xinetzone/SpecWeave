"""并发安全检查器基类和共享上下文。

提供检查器统一接口和共享状态管理，采用策略模式拆分8种检查维度。
"""


from ..python310_version_check import enforce_python310

enforce_python310()

import ast
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from .constants import DIMENSIONS
from .models import ConcurrencyIssue

logger = logging.getLogger(__name__)


@dataclass
class CheckerContext:
    """检查器共享上下文，避免状态变量散落。

    封装所有检查器可能需要的AST遍历状态，通过协调器统一管理生命周期。
    """
    filepath: Path
    content_lines: list[str] = field(default_factory=list)

    current_class: str = ""
    function_name: str = ""
    in_test_function: bool = False
    in_logging_call: bool = False
    loop_depth: int = 0
    is_resolver_class: bool = False

    function_params: dict[str, str] = field(default_factory=dict)
    if_guard_stack: list[set[str]] = field(default_factory=list)
    thread_vars: set[str] = field(default_factory=set)
    lock_vars: dict[str, str] = field(default_factory=dict)
    pool_vars: set[str] = field(default_factory=set)
    pool_shutdown: set[str] = field(default_factory=set)
    pool_context_managed: set[str] = field(default_factory=set)
    current_function_locks: list[str] = field(default_factory=list)
    lock_acquire_sequences: list[tuple[str, list[str], int]] = field(default_factory=list)

    reported_on_line: dict[int, set[str]] = field(default_factory=dict)

    def reset_function_state(self) -> None:
        self.function_params = {}
        self.thread_vars = set()
        self.current_function_locks = []
        self.pool_shutdown = set()
        self.pool_context_managed = set()
        self.pool_vars = set()
        self.lock_vars = {}


class BaseChecker(ABC):
    """检查器基类，定义统一接口。

    每个具体检查器实现一个维度的检查逻辑，通过协调器统一调度。
    """

    def __init__(self, context: CheckerContext):
        self._ctx = context
        self._issues: list[ConcurrencyIssue] = []

    @property
    @abstractmethod
    def dimension(self) -> str:
        """检查维度标识（如TIMEOUT、IDEMPOTENT）"""

    def get_snippet(self, line_no: int) -> str:
        if line_no and 0 < line_no <= len(self._ctx.content_lines):
            return self._ctx.content_lines[line_no - 1].strip()
        return ""

    def add_issue(self, message: str, line: int, snippet: str = "") -> None:
        dedup_key = f"{self.dimension}:{message[:80]}"
        line_cats = self._ctx.reported_on_line.setdefault(line, set())
        if dedup_key in line_cats:
            logger.debug("去重跳过重复问题 [%s] L%d: %s", self.dimension, line, message[:60])
            return
        line_cats.add(dedup_key)

        dim_info = DIMENSIONS[self.dimension]
        issue = ConcurrencyIssue(
            dimension=self.dimension,
            code=dim_info["code"],
            severity=dim_info["default_severity"],
            message=message,
            line=line,
            snippet=snippet or self.get_snippet(line),
            dimension_name=dim_info["name"],
        )
        self._issues.append(issue)
        logger.warning("发现问题 [%s] %s L%d: %s", self.dimension, issue.severity.upper(), line, message[:100])

    @property
    def issues(self) -> list[ConcurrencyIssue]:
        return self._issues

    def check_module_enter(self, node: ast.Module) -> None:
        pass

    def check_module_exit(self, node: ast.Module) -> None:
        pass

    def check_class_enter(self, node: ast.ClassDef) -> None:
        pass

    def check_class_exit(self, node: ast.ClassDef) -> None:
        pass

    def check_function_enter(self, node: ast.FunctionDef) -> None:
        pass

    def check_function_exit(self, node: ast.FunctionDef) -> None:
        pass

    def check_if_enter(self, node: ast.If) -> None:
        pass

    def check_if_exit(self, node: ast.If) -> None:
        pass

    def check_while_enter(self, node: ast.While) -> None:
        pass

    def check_while_exit(self, node: ast.While) -> None:
        pass

    def check_for_enter(self, node: ast.For | ast.AsyncFor) -> None:
        pass

    def check_for_exit(self, node: ast.For | ast.AsyncFor) -> None:
        pass

    def check_compare(self, node: ast.Compare) -> None:
        pass

    def check_return(self, node: ast.Return) -> None:
        pass

    def check_with_enter(self, node: ast.With) -> None:
        pass

    def check_with_exit(self, node: ast.With) -> None:
        pass

    def check_subscript(self, node: ast.Subscript) -> None:
        pass

    def check_assign(self, node: ast.Assign) -> None:
        pass

    def check_call(self, node: ast.Call) -> None:
        pass

    @staticmethod
    def caller_name(func: ast.expr) -> str:
        if isinstance(func, ast.Attribute):
            return func.attr
        if isinstance(func, ast.Name):
            return func.id
        return ""

    @staticmethod
    def attr_chain(node: ast.expr) -> str:
        parts = []
        cur = node
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
        return ".".join(reversed(parts))

    @staticmethod
    def attr_base_name(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id.lower()
        if isinstance(node, ast.Attribute):
            return node.attr.lower()
        return ""

    @staticmethod
    def has_chinese(text: str) -> bool:
        from .constants import CHINESE_CHAR_RANGE
        return any(CHINESE_CHAR_RANGE[0] <= ch <= CHINESE_CHAR_RANGE[1] for ch in text)

    @staticmethod
    def has_timeout_arg(node: ast.Call) -> bool:
        for kw in node.keywords:
            if kw.arg == "timeout":
                return True
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)):
                return True
        return False
