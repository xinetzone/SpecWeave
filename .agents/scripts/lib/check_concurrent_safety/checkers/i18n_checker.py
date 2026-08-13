"""国际化检查器 - 检测业务逻辑中是否存在脆弱的中文匹配。"""


from ...python310_version_check import enforce_python310

enforce_python310()

import ast

from ..constants import LOGGING_CALLS, I18N_EXEMPT_CALLS, I18N_DICT_METHODS
from ..checker_base import BaseChecker


class I18nChecker(BaseChecker):

    @property
    def dimension(self) -> str:
        return "I18N"

    def _caller_receiver_name(self, func: ast.expr) -> str:
        if isinstance(func, ast.Attribute):
            val = func.value
            if isinstance(val, ast.Name):
                return val.id
            if isinstance(val, ast.Attribute):
                return self.attr_chain(val)
        return ""

    def check_call(self, node: ast.Call) -> None:
        if self._ctx.in_logging_call or self._ctx.in_test_function:
            return

        caller_name = self.caller_name(node.func)
        if caller_name in LOGGING_CALLS:
            return
        if caller_name in {"strip", "lower", "upper", "format", "replace", "encode", "decode"}:
            return

        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                text = arg.value
                if self.has_chinese(text) and len(text) >= 2:
                    if caller_name in {"startswith", "endswith", "find", "index", "__contains__", "__eq__"}:
                        self.add_issue(
                            f"业务逻辑中直接匹配中文文本「{text[:20]}」，建议使用枚举/常量而非字面量",
                            node.lineno,
                        )

        if caller_name in {"__contains__", "get"} or caller_name in I18N_DICT_METHODS:
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    text = arg.value
                    if self.has_chinese(text) and len(text) >= 2:
                        receiver = self._caller_receiver_name(node.func)
                        if receiver and not self._ctx.in_logging_call:
                            is_exempt = caller_name in I18N_EXEMPT_CALLS
                            if not is_exempt and caller_name in {"__contains__", "get", "pop"}:
                                self.add_issue(
                                    f"成员检测或字典查找中使用中文字面量「{text[:20]}」，建议使用枚举常量替代",
                                    node.lineno,
                                )

    def check_compare(self, node: ast.Compare) -> None:
        if self._ctx.in_test_function or self._ctx.in_logging_call:
            return

        for op, comparator in zip(node.ops, node.comparators):
            for side in [node.left, comparator]:
                if isinstance(side, ast.Constant) and isinstance(side.value, str):
                    if self.has_chinese(side.value) and len(side.value) >= 2:
                        self.add_issue(
                            f"比较中使用中文字面量「{side.value[:20]}」，建议提取为枚举常量",
                            node.lineno,
                        )

    def check_subscript(self, node: ast.Subscript) -> None:
        if self._ctx.in_test_function or self._ctx.in_logging_call:
            return

        if not isinstance(node.value, (ast.Name, ast.Attribute)):
            return
        slice_val = node.slice
        if isinstance(slice_val, ast.Constant) and isinstance(slice_val.value, str):
            key_val = str(slice_val.value)
            if self.has_chinese(key_val) and len(key_val) >= 2:
                if not self._ctx.in_logging_call:
                    self.add_issue(
                        f"使用中文字面量「{key_val[:20]}」作为字典/列表索引键，建议使用枚举常量替代",
                        node.lineno,
                    )
