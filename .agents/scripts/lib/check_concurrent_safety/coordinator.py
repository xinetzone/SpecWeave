"""并发安全检查协调器 - 遍历AST并分发检查任务。

采用策略模式，将8种并发安全检查维度拆分到独立检查器类，
协调器只负责AST遍历生命周期管理和检查器调度。
"""


from ..python310_version_check import enforce_python310

enforce_python310()

import ast
import logging
import re
from pathlib import Path

from .checker_base import CheckerContext
from .checkers import ALL_CHECKERS
from .models import ConcurrencyIssue

logger = logging.getLogger(__name__)


def _extract_guard_targets(test_node: ast.expr) -> set[str]:
    targets = set()
    for node in ast.walk(test_node):
        if isinstance(node, ast.Compare):
            for op, comp in zip(node.ops, node.comparators):
                if isinstance(op, (ast.In, ast.NotIn)):
                    if isinstance(comp, ast.Name):
                        targets.add(comp.id)
                    elif isinstance(comp, ast.Attribute):
                        chain_parts = []
                        cur = comp
                        while isinstance(cur, ast.Attribute):
                            chain_parts.append(cur.attr)
                            cur = cur.value
                        if isinstance(cur, ast.Name):
                            chain_parts.append(cur.id)
                            chain = ".".join(reversed(chain_parts))
                            if chain:
                                targets.add(chain)
    return targets


def _split_class_words(name: str) -> set[str]:
    words = set()
    for part in name.split("_"):
        if not part:
            continue
        sub = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|$)", part)
        if sub:
            words.update(w.lower() for w in sub)
        else:
            words.add(part.lower())
    return words


class ConcurrentSafetyCoordinator(ast.NodeVisitor):
    """并发安全检查协调器：遍历AST并分发检查任务。"""

    def __init__(self, filepath: Path, content_lines: list[str]):
        self.filepath = filepath
        self.content_lines = list(content_lines)

        self._ctx = CheckerContext(
            filepath=filepath,
            content_lines=self.content_lines,
        )

        self._checkers = [checker_cls(self._ctx) for checker_cls in ALL_CHECKERS]

        logger.info("=" * 60)
        logger.info("开始扫描文件: %s (%d行)", filepath, len(content_lines))

    @property
    def issues(self) -> list[ConcurrencyIssue]:
        all_issues = []
        for checker in self._checkers:
            all_issues.extend(checker.issues)
        return all_issues

    def visit_Module(self, node: ast.Module) -> None:
        for checker in self._checkers:
            checker.check_module_enter(node)
        self.generic_visit(node)
        for checker in self._checkers:
            checker.check_module_exit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_class = self._ctx.current_class
        old_resolver = self._ctx.is_resolver_class

        self._ctx.current_class = node.name
        class_words = _split_class_words(node.name)
        self._ctx.is_resolver_class = any(
            kw in class_words for kw in [
                "resolver", "scheduler", "manager", "dispatcher", "arbiter",
                "lock", "queue", "pool", "worker", "concurrent",
            ]
        )
        if self._ctx.is_resolver_class:
            logger.debug("识别到resolver/concurrent类: %s", node.name)

        for checker in self._checkers:
            checker.check_class_enter(node)
        self.generic_visit(node)
        for checker in self._checkers:
            checker.check_class_exit(node)

        self._ctx.current_class = old_class
        self._ctx.is_resolver_class = old_resolver

    def _is_thread_constructor(self, val: ast.expr) -> bool:
        if not isinstance(val, ast.Call):
            return False
        func = val.func
        if isinstance(func, ast.Name) and func.id in {"Thread", "Process", "Future", "Worker"}:
            return True
        if isinstance(func, ast.Attribute):
            if func.attr in {"Thread", "Process", "Future"}:
                return True
        return False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        old_func = self._ctx.function_name
        old_in_test = self._ctx.in_test_function

        self._ctx.function_name = node.name
        self._ctx.in_test_function = node.name.startswith("test_") or node.name.startswith("_test_")
        self._ctx.reset_function_state()

        func_qname = f"{self._ctx.current_class}.{node.name}" if self._ctx.current_class else node.name
        if self._ctx.in_test_function:
            logger.debug("进入测试函数: %s L%d (跳过检测)", func_qname, node.lineno)
        else:
            logger.debug("进入函数: %s L%d", func_qname, node.lineno)

        for checker in self._checkers:
            checker.check_function_enter(node)
        self.generic_visit(node)
        for checker in self._checkers:
            checker.check_function_exit(node)

        if not self._ctx.in_test_function:
            logger.debug("退出函数: %s", func_qname)

        self._ctx.function_name = old_func
        self._ctx.in_test_function = old_in_test

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)

    def visit_If(self, node: ast.If) -> None:
        guard_targets = _extract_guard_targets(node.test)
        self._ctx.if_guard_stack.append(guard_targets)
        for checker in self._checkers:
            checker.check_if_enter(node)
        self.generic_visit(node)
        for checker in self._checkers:
            checker.check_if_exit(node)
        self._ctx.if_guard_stack.pop()

    def visit_While(self, node: ast.While) -> None:
        for checker in self._checkers:
            checker.check_while_enter(node)
        old_depth = self._ctx.loop_depth
        self._ctx.loop_depth += 1
        self.generic_visit(node)
        self._ctx.loop_depth = old_depth
        for checker in self._checkers:
            checker.check_while_exit(node)

    def visit_For(self, node: ast.For | ast.AsyncFor) -> None:
        for checker in self._checkers:
            checker.check_for_enter(node)
        old_depth = self._ctx.loop_depth
        self._ctx.loop_depth += 1
        self.generic_visit(node)
        self._ctx.loop_depth = old_depth
        for checker in self._checkers:
            checker.check_for_exit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        if self._ctx.in_test_function or self._ctx.in_logging_call:
            self.generic_visit(node)
            return
        for checker in self._checkers:
            checker.check_compare(node)
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        if self._ctx.in_test_function or node.value is None:
            self.generic_visit(node)
            return
        for checker in self._checkers:
            checker.check_return(node)
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        for checker in self._checkers:
            checker.check_with_enter(node)
        self.generic_visit(node)
        for checker in self._checkers:
            checker.check_with_exit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if self._ctx.in_test_function or self._ctx.in_logging_call:
            self.generic_visit(node)
            return
        for checker in self._checkers:
            checker.check_subscript(node)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                if self._is_thread_constructor(node.value):
                    self._ctx.thread_vars.add(target.id.lower())
                    logger.debug("[TIMEOUT] 识别到线程变量: %s", target.id)
        for checker in self._checkers:
            checker.check_assign(node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if self._ctx.in_test_function:
            self.generic_visit(node)
            return

        caller_name = ""
        if isinstance(node.func, ast.Attribute):
            caller_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            caller_name = node.func.id

        from .constants import LOGGING_CALLS
        if caller_name in LOGGING_CALLS:
            old_logging = self._ctx.in_logging_call
            self._ctx.in_logging_call = True
            self.generic_visit(node)
            self._ctx.in_logging_call = old_logging
            return

        for checker in self._checkers:
            checker.check_call(node)

        self.generic_visit(node)


ConcurrentSafetyVisitor = ConcurrentSafetyCoordinator
