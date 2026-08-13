"""资源泄漏检查器 - 检测线程池/进程池是否正确shutdown。"""


from ...python310_version_check import enforce_python310

enforce_python310()

import ast
import logging

from ..constants import POOL_CLASSES, POOL_SHUTDOWN_METHODS
from ..checker_base import BaseChecker

logger = logging.getLogger(__name__)


class LeakChecker(BaseChecker):

    @property
    def dimension(self) -> str:
        return "LEAK"

    def _is_pool_constructor(self, val: ast.expr) -> bool:
        if not isinstance(val, ast.Call):
            return False
        func = val.func
        if isinstance(func, ast.Name) and func.id in POOL_CLASSES:
            return True
        if isinstance(func, ast.Attribute):
            if func.attr in POOL_CLASSES:
                return True
        return False

    def _get_lock_target_name(self, func: ast.expr) -> str:
        if isinstance(func, ast.Attribute):
            val = func.value
            if isinstance(val, ast.Name):
                return val.id
            if isinstance(val, ast.Attribute):
                return self.attr_chain(val)
        return ""

    def check_assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                if self._is_pool_constructor(node.value):
                    self._ctx.pool_vars.add(target.id)
                    logger.debug("[LEAK] 识别到局部池变量: %s (未确认是否安全关闭)", target.id)
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                attr_name = target.attr
                val = node.value
                if isinstance(val, ast.Call):
                    if self._is_pool_constructor(val):
                        self._ctx.pool_vars.add(f"self.{attr_name}")
                        logger.debug("[LEAK] 识别到self成员池: self.%s (成员变量不检查泄漏)", attr_name)

    def check_with_enter(self, node: ast.With) -> None:
        for item in node.items:
            ctx = item.context_expr
            is_pool_ctx = False

            if isinstance(ctx, ast.Call):
                cn = self.caller_name(ctx.func)
                if cn in POOL_CLASSES or (isinstance(ctx.func, ast.Attribute) and ctx.func.attr in POOL_CLASSES):
                    is_pool_ctx = True
                    logger.debug("[LEAK] with块 L%d: 识别到池构造器调用 %s() (上下文管理)", node.lineno, cn)

            as_name = ""
            if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                as_name = item.optional_vars.id

            if is_pool_ctx:
                if as_name:
                    self._ctx.pool_vars.add(as_name)
                    self._ctx.pool_context_managed.add(as_name)
                    logger.info("[LEAK] 池 %s 使用with上下文管理，已标记安全", as_name)

    def check_call(self, node: ast.Call) -> None:
        if self._ctx.in_test_function:
            return

        caller_name = self.caller_name(node.func)
        if caller_name not in POOL_SHUTDOWN_METHODS:
            return
        target = self._get_lock_target_name(node.func)
        if target and target in self._ctx.pool_vars:
            self._ctx.pool_shutdown.add(target)
            logger.info("[LEAK] 检测到池shutdown/close调用: %s.%s() L%d", target, caller_name, node.lineno)
        if target:
            for pool_var in self._ctx.pool_vars:
                if pool_var.endswith("." + target.split(".")[-1]) or target == pool_var:
                    self._ctx.pool_shutdown.add(pool_var)

    def check_function_exit(self, node: ast.FunctionDef) -> None:
        if self._ctx.in_test_function:
            return

        func_qname = f"{self._ctx.current_class}.{node.name}" if self._ctx.current_class else node.name
        logger.debug("[LEAK] 检查函数 [%s] 池关闭状态: 池变量=%s, 上下文管理=%s, 已shutdown=%s",
                     func_qname, self._ctx.pool_vars, self._ctx.pool_context_managed, self._ctx.pool_shutdown)

        for pool_var in self._ctx.pool_vars:
            if pool_var in self._ctx.pool_context_managed:
                logger.debug("[LEAK] 池 %s: 使用with上下文管理，安全", pool_var)
                continue
            if pool_var in self._ctx.pool_shutdown:
                logger.debug("[LEAK] 池 %s: 显式调用了shutdown，安全", pool_var)
                continue

            pool_short = pool_var.split(".")[-1]
            is_local_pool = not pool_var.startswith("self.")

            if is_local_pool:
                logger.error("[LEAK] 检测到局部池泄漏: %s 在函数 %s 中未正确关闭", pool_short, func_qname)
                self.add_issue(
                    f"线程池/进程池 {pool_short} 未调用 shutdown()/close() 且未使用 with 语句管理，"
                    f"可能导致资源泄漏",
                    node.lineno,
                )
            else:
                logger.debug("[LEAK] 池 %s: self成员变量，跳过泄漏检查", pool_var)
