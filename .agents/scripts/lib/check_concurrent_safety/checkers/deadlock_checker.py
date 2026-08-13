"""死锁顺序检查器 - 检测多锁获取顺序一致性，防止死锁。"""


from ...python310_version_check import enforce_python310

enforce_python310()

import ast
import logging

from ..constants import LOCK_METHODS, LOCK_CLASSES
from ..checker_base import BaseChecker

logger = logging.getLogger(__name__)


class DeadlockChecker(BaseChecker):

    @property
    def dimension(self) -> str:
        return "DEADLOCK"

    def _lock_type_from_call(self, call_node: ast.Call) -> str:
        func = call_node.func
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
        return "Lock"

    def _is_lock_constructor(self, val: ast.expr) -> bool:
        if not isinstance(val, ast.Call):
            return False
        func = val.func
        if isinstance(func, ast.Name) and func.id in LOCK_CLASSES:
            return True
        if isinstance(func, ast.Attribute):
            if func.attr in LOCK_CLASSES:
                return True
        return False

    def _is_lock_acquire_on_var(self, node: ast.Call) -> bool:
        if not isinstance(node.func, ast.Attribute):
            return False
        val = node.func.value
        lock_name = self._get_lock_target_name(node.func)
        if lock_name and (lock_name in self._ctx.lock_vars or any(
            kw in lock_name.lower() for kw in ["lock", "mutex", "semaphore", "_lock", "rwlock"]
        )):
            return True
        if isinstance(val, ast.Name) and any(
            kw in val.id.lower() for kw in ["lock", "mutex", "semaphore", "rwlock", "_lock"]
        ):
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

    def _extract_lock_expr_name(self, ctx: ast.expr) -> str:
        if isinstance(ctx, ast.Attribute):
            return self.attr_chain(ctx)
        if isinstance(ctx, ast.Name):
            return ctx.id
        if isinstance(ctx, ast.Call):
            return self._lock_type_from_call(ctx).lower() + "_anon"
        return ""

    def check_assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                if self._is_lock_constructor(node.value):
                    lock_type = self._lock_type_from_call(node.value)
                    self._ctx.lock_vars[target.id] = lock_type
                    logger.debug("[DEADLOCK] 识别到锁变量: %s (类型=%s)", target.id, lock_type)
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                attr_name = target.attr
                val = node.value
                if isinstance(val, ast.Call):
                    if self._is_lock_constructor(val):
                        lock_type = self._lock_type_from_call(val)
                        self._ctx.lock_vars[f"self.{attr_name}"] = lock_type
                        logger.debug("[DEADLOCK] 识别到self锁变量: self.%s (类型=%s)", attr_name, lock_type)

    def check_with_enter(self, node: ast.With) -> None:
        for item in node.items:
            ctx = item.context_expr
            ctx_name = ""
            is_lock_ctx = False

            if isinstance(ctx, ast.Call):
                cn = self.caller_name(ctx.func)
                if cn in LOCK_CLASSES or (isinstance(ctx.func, ast.Attribute) and ctx.func.attr in LOCK_CLASSES):
                    is_lock_ctx = True
                    logger.debug("[DEADLOCK] with块 L%d: 识别到锁构造器调用 %s()", node.lineno, cn)
            elif isinstance(ctx, (ast.Name, ast.Attribute)):
                ctx_name = self.attr_chain(ctx) if isinstance(ctx, ast.Attribute) else (ctx.id if isinstance(ctx, ast.Name) else "")
                if ctx_name in self._ctx.lock_vars or any(kw in ctx_name.lower() for kw in ["lock", "mutex", "semaphore", "_lock", "rwlock"]):
                    is_lock_ctx = True
                    logger.debug("[DEADLOCK] with块 L%d: 识别到锁变量 %s", node.lineno, ctx_name)

            as_name = ""
            if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                as_name = item.optional_vars.id

            if is_lock_ctx:
                lock_target = as_name or ctx_name or self._extract_lock_expr_name(ctx)
                if lock_target:
                    if as_name:
                        self._ctx.lock_vars[as_name] = "with_lock"
                    if lock_target not in self._ctx.current_function_locks:
                        self._ctx.current_function_locks.append(lock_target)
                        logger.info("[DEADLOCK] 记录锁获取: %s (当前序列: %s)", lock_target, self._ctx.current_function_locks)

    def check_call(self, node: ast.Call) -> None:
        if self._ctx.in_test_function:
            return

        caller_name = self.caller_name(node.func)
        if caller_name not in LOCK_METHODS:
            return
        if not self._is_lock_acquire_on_var(node):
            return

        lock_name = self._get_lock_target_name(node.func)
        if lock_name:
            if lock_name not in self._ctx.current_function_locks:
                self._ctx.current_function_locks.append(lock_name)
                logger.info("[DEADLOCK] 显式acquire()记录锁获取: %s L%d (序列: %s)", lock_name, node.lineno, self._ctx.current_function_locks)

    def check_function_exit(self, node: ast.FunctionDef) -> None:
        if len(self._ctx.current_function_locks) < 2:
            logger.debug("[DEADLOCK] 函数 %s 锁数量<2，跳过顺序检查", node.name)
            return

        sequences = self._ctx.lock_acquire_sequences
        current_seq = self._ctx.current_function_locks
        func_qname = f"{self._ctx.current_class}.{node.name}" if self._ctx.current_class else node.name

        logger.info("[DEADLOCK] 检查函数 [%s] 锁序列: %s (已有%d个参考序列)", func_qname, current_seq, len(sequences))

        if not sequences:
            sequences.append((func_qname, list(current_seq), node.lineno))
            logger.info("[DEADLOCK] 记录首个锁序列: %s -> %s", func_qname, current_seq)
            return

        for existing_func, existing_seq, existing_line in sequences:
            logger.debug("[DEADLOCK] 对比参考 [%s] 序列: %s", existing_func, existing_seq)
            if len(existing_seq) >= 2 and len(current_seq) >= 2:
                for i, l1 in enumerate(existing_seq):
                    for j, l2 in enumerate(existing_seq):
                        if i < j:
                            try:
                                ci = current_seq.index(l1)
                                cj = current_seq.index(l2)
                                if ci > cj:
                                    logger.error("[DEADLOCK] 检测到AB-BA逆序! %s: %s→%s(L%d) vs %s: %s→%s(L%d)",
                                                 existing_func, l1, l2, existing_line,
                                                 func_qname, l2, l1, node.lineno)
                                    self.add_issue(
                                        f"锁获取顺序不一致！在 {existing_func} (L{existing_line}) 中按 {l1}→{l2} 顺序获取，"
                                        f"但在 {func_qname} (L{node.lineno}) 中按 {l2}→{l1} 顺序获取，可能导致死锁",
                                        node.lineno,
                                    )
                                    return
                            except ValueError:
                                pass

        sequences.append((func_qname, list(current_seq), node.lineno))
        logger.debug("[DEADLOCK] 序列一致，已记录: %s", func_qname)
