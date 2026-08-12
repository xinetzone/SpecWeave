"""幂等检查器 - 检测列表追加操作是否有去重保护。"""


from ...python310_version_check import enforce_python310

enforce_python310()

import ast

from ..checker_base import BaseChecker


class IdempotentChecker(BaseChecker):

    @property
    def dimension(self) -> str:
        return "IDEMPOTENT"

    def _append_target_name(self, func: ast.expr) -> str | None:
        if isinstance(func, ast.Attribute) and isinstance(func.value, (ast.Name, ast.Attribute)):
            return self.attr_chain(func.value)
        return None

    def check_call(self, node: ast.Call) -> None:
        if self._ctx.in_test_function or self._ctx.in_logging_call:
            return

        caller_name = self.caller_name(node.func)
        if caller_name != "append":
            return

        target_name = self._append_target_name(node.func)
        if target_name is None:
            return

        target_short = target_name.split(".")[-1].lower()

        if target_short.endswith("_stack"):
            return
        if target_short in {"sequences", "collected", "records", "results", "items_all"}:
            return
        if target_short.endswith("_sequences") or target_short.endswith("_records"):
            return

        for guards in self._ctx.if_guard_stack:
            if target_name in guards:
                return
            short = target_name.split(".")[-1]
            for g in guards:
                if g.endswith("." + short) or g == short:
                    return

        if target_short in {"issues"}:
            return

        if not self._ctx.is_resolver_class or not any(
            kw in target_name.lower() for kw in ["rejected", "pending", "queue", "waiting", "blocked"]
        ):
            return

        self.add_issue(
            f"对列表/集合 {target_name} 执行 append() 前未做 'not in' 去重检查，重复调用可能导致重复记录（活锁风险）",
            node.lineno,
        )
