"""边界检查器 - 检测热路径中对列表使用'in'操作符导致O(n)线性查找。"""


from ...python310_version_check import enforce_python310

enforce_python310()

import ast

from ..checker_base import BaseChecker


class BoundaryChecker(BaseChecker):

    @property
    def dimension(self) -> str:
        return "BOUNDARY"

    def check_compare(self, node: ast.Compare) -> None:
        if self._ctx.in_test_function or self._ctx.in_logging_call:
            return

        for op, comparator in zip(node.ops, node.comparators):
            if isinstance(op, (ast.In, ast.NotIn)):
                self._check_in_operator(comparator, node.lineno)

    def _check_in_operator(self, collection: ast.expr, lineno: int):
        coll_name = ""
        if isinstance(collection, ast.Name):
            coll_name = collection.id
        elif isinstance(collection, ast.Attribute):
            coll_name = self.attr_chain(collection)

        if not coll_name:
            return

        if self._ctx.loop_depth == 0 and not self._ctx.is_resolver_class:
            return

        name_lower = coll_name.lower()
        if name_lower.endswith("_set") or name_lower.endswith("_dict") or name_lower.endswith("_map"):
            return

        list_hints = ["_list", "agents_list", "items_list", "results", "candidates", "entries", "pending_list", "queue", "waiting_list"]
        is_list_var = (
            name_lower.endswith("_list")
            or any(kw in name_lower for kw in list_hints)
            or (self._ctx.is_resolver_class and "agents" in name_lower and not name_lower.endswith("_set"))
        )
        is_self_or_name = isinstance(collection, ast.Name) or (
            isinstance(collection, ast.Attribute)
            and isinstance(collection.value, ast.Name)
            and collection.value.id in {"self", "cls"}
        )

        if is_list_var and is_self_or_name and self._ctx.loop_depth >= 1:
            self.add_issue(
                f"循环热路径中对列表 {coll_name} 使用'in'线性查找(O(n))，总体复杂度O(n²)，建议用dict/set实现O(1)查找",
                lineno,
            )
