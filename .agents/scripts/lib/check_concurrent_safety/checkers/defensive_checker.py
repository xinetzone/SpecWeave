"""防御检查器 - 检测可变默认参数和外部可变对象的防御性拷贝。"""


from ...python310_version_check import enforce_python310

enforce_python310()

import ast

from ..constants import MUTABLE_TYPES
from ..checker_base import BaseChecker


class DefensiveChecker(BaseChecker):

    @property
    def dimension(self) -> str:
        return "DEFENSIVE"

    def _get_annotation_name(self, ann: ast.expr | None) -> str:
        if ann is None:
            return ""
        if isinstance(ann, ast.Name):
            return ann.id
        if isinstance(ann, ast.Subscript):
            return self._get_annotation_name(ann.value)
        return ""

    def _is_copy_call(self, node: ast.expr) -> bool:
        if isinstance(node, ast.Call):
            cn = self.caller_name(node.func)
            cf = self.attr_chain(node.func) if isinstance(node.func, ast.Attribute) else ""
            return cn in {"copy", "deepcopy", "dict", "list", "set"} or ".copy" in cf
        return False

    def check_function_enter(self, node: ast.FunctionDef) -> None:
        if self._ctx.in_test_function:
            return

        for arg in node.args.args:
            self._ctx.function_params[arg.arg] = self._get_annotation_name(arg.annotation)

        for default_idx, default in enumerate(node.args.defaults):
            arg_idx = len(node.args.args) - len(node.args.defaults) + default_idx
            if arg_idx < len(node.args.args):
                arg_name = node.args.args[arg_idx].arg
                if isinstance(default, ast.List):
                    self.add_issue(
                        f"可变默认参数 list: {arg_name}=[]，应使用 None 作为默认值",
                        default.lineno,
                    )
                elif isinstance(default, ast.Dict):
                    self.add_issue(
                        f"可变默认参数 dict: {arg_name}={{}}，应使用 None 作为默认值",
                        default.lineno,
                    )
                elif isinstance(default, ast.Set):
                    self.add_issue(
                        f"可变默认参数 set: {arg_name}={{...}}，应使用 None 作为默认值",
                        default.lineno,
                    )

    def check_return(self, node: ast.Return) -> None:
        if self._ctx.in_test_function or node.value is None:
            return

        if isinstance(node.value, ast.Attribute) and isinstance(node.value.value, ast.Name):
            if node.value.value.id == "self":
                attr_name = node.value.attr
                if any(kw in attr_name.lower() for kw in [
                    "cache", "list", "dict", "map", "state", "queue", "set",
                    "agents", "results", "pending", "waiting", "rejected",
                ]):
                    self.add_issue(
                        f"直接返回self.{attr_name}（内部可变状态），外部修改会破坏封装，建议返回copy()或不可变视图",
                        node.lineno,
                    )

        if isinstance(node.value, ast.Name) and node.value.id in self._ctx.function_params:
            param_type = self._ctx.function_params.get(node.value.id, "")
            if param_type.lower() in MUTABLE_TYPES:
                self.add_issue(
                    f"直接返回外部传入的可变参数 {node.value.id}，建议做防御性拷贝",
                    node.lineno,
                )

    def check_assign(self, node: ast.Assign) -> None:
        if self._ctx.in_test_function:
            return

        for target in node.targets:
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                attr_name = target.attr
                val = node.value
                if isinstance(val, ast.Name) and val.id in self._ctx.function_params:
                    param_type = self._ctx.function_params.get(val.id, "")
                    is_mutable_attr = any(
                        kw in attr_name.lower() for kw in [
                            "list", "dict", "map", "cache", "state", "set",
                            "agents", "queue", "pending", "results",
                        ]
                    )
                    if param_type.lower() in MUTABLE_TYPES or is_mutable_attr:
                        if not self._is_copy_call(val):
                            self.add_issue(
                                f"self.{attr_name} = {val.id} 直接引用外部可变对象，外部修改会污染内部状态，建议copy()",
                                node.lineno,
                            )
