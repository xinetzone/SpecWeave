"""超时检查器 - 检测锁/等待操作是否设置超时，防止死锁。"""


from ...python310_version_check import enforce_python310

enforce_python310()

import ast

from ..constants import LOCK_METHODS
from ..checker_base import BaseChecker


class TimeoutChecker(BaseChecker):

    @property
    def dimension(self) -> str:
        return "TIMEOUT"

    def _is_lock_object(self, func: ast.expr) -> bool:
        if isinstance(func, ast.Attribute):
            val = func.value
            if isinstance(val, ast.Name):
                return any(kw in val.id.lower() for kw in ["lock", "mutex", "semaphore", "rwlock", "_lock", "cond", "event"])
        return False

    def _is_thread_join(self, func: ast.expr) -> bool:
        if not isinstance(func, ast.Attribute):
            return False
        val = func.value
        if isinstance(val, ast.Constant) and isinstance(val.value, str):
            return False
        if isinstance(val, ast.Name):
            name = val.id.lower()
            if name in {"sep", "delim", "delimiter", "separator"}:
                return False
            if name in self._ctx.thread_vars:
                return True
        thread_hints = ["thread", "worker", "proc", "process", "task", "fut", "future", "coro", "greenlet"]
        name_to_check = self.attr_base_name(val)
        return any(h in name_to_check for h in thread_hints)

    def _is_concurrency_wait(self, func: ast.expr) -> bool:
        if not isinstance(func, ast.Attribute):
            return False
        wait_hints = ["lock", "event", "cond", "condition", "barrier", "queue", "latch",
                      "semaphore", "gate", "_wait", "waiter", "ready", "done"]
        name_to_check = self.attr_base_name(func.value)
        return any(h in name_to_check for h in wait_hints)

    def check_call(self, node: ast.Call) -> None:
        if self._ctx.in_test_function:
            return

        caller_name = self.caller_name(node.func)
        if not caller_name:
            return

        is_lock_acquire = (
            caller_name in LOCK_METHODS
            or (caller_name == "acquire" and self._is_lock_object(node.func))
        )

        if is_lock_acquire:
            has_timeout = False
            has_nonblocking = False
            for kw in node.keywords:
                if kw.arg == "timeout":
                    has_timeout = True
                if kw.arg == "blocking" and isinstance(kw.value, ast.Constant) and kw.value.value is False:
                    has_nonblocking = True
            if len(node.args) >= 1:
                first = node.args[0]
                if isinstance(first, ast.Constant) and first.value is False:
                    has_nonblocking = True
            if not has_timeout and not has_nonblocking:
                self.add_issue(
                    f"锁操作 {caller_name}() 未设置timeout，可能导致死锁",
                    node.lineno,
                )

        if caller_name == "wait" and self._is_concurrency_wait(node.func):
            if not self.has_timeout_arg(node):
                self.add_issue(
                    "wait() 调用未设置timeout，可能永久阻塞",
                    node.lineno,
                )

        if caller_name == "join" and self._is_thread_join(node.func):
            if not self.has_timeout_arg(node):
                self.add_issue(
                    "join() 调用未设置timeout，可能永久阻塞",
                    node.lineno,
                )

        if caller_name == "wait_for":
            if len(node.args) < 2 and not any(kw.arg == "timeout" for kw in node.keywords):
                self.add_issue(
                    "asyncio.wait_for() 缺少timeout参数",
                    node.lineno,
                )

    def check_while_enter(self, node: ast.While) -> None:
        if self._ctx.in_test_function:
            return

        is_infinite = (
            (isinstance(node.test, ast.Constant) and node.test.value is True)
            or (isinstance(node.test, ast.Name) and node.test.id == "True")
        )

        if is_infinite:
            has_exit = self._has_exit_in_loop(node)
            has_timeout = self._has_timeout_in_loop(node)
            if not has_exit and not has_timeout:
                self.add_issue(
                    "while True 无限循环未检测到break/return/raise/超时退出机制，存在死循环风险",
                    node.lineno,
                )

    def _has_exit_in_loop(self, loop_node: ast.While | ast.For) -> bool:
        for child in ast.walk(loop_node):
            if child is loop_node:
                continue
            if isinstance(child, (ast.Break, ast.Return, ast.Raise)):
                if hasattr(child, 'lineno') and child.lineno > loop_node.lineno:
                    return True
        return False

    def _has_timeout_in_loop(self, loop_node: ast.While | ast.For) -> bool:
        for child in ast.walk(loop_node):
            if isinstance(child, ast.Call):
                cn = self.caller_name(child.func)
                if cn in {"wait", "acquire", "join", "sleep"} and self.has_timeout_arg(child):
                    return True
        return False
