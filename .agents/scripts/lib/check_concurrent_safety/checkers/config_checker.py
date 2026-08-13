"""配置检查器 - 检测并发参数是否硬编码不可配置。"""


from ...python310_version_check import enforce_python310

enforce_python310()

import ast

from ..checker_base import BaseChecker


class ConfigChecker(BaseChecker):

    @property
    def dimension(self) -> str:
        return "CONFIG"

    def _extract_numeric_arg(self, node: ast.Call):
        for kw in node.keywords:
            if kw.arg == "timeout" and isinstance(kw.value, ast.Constant):
                return kw.value.value if isinstance(kw.value.value, (int, float)) else None
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)):
                return arg.value
        return None

    def check_call(self, node: ast.Call) -> None:
        if self._ctx.in_test_function:
            return
        if not self._ctx.is_resolver_class:
            return

        caller_name = self.caller_name(node.func)
        if caller_name in {"sleep", "acquire"}:
            timeout_val = self._extract_numeric_arg(node)
            if timeout_val is not None and timeout_val > 0:
                has_constant_ref = any(
                    isinstance(a, ast.Name) and a.id.isupper()
                    for a in node.args
                )
                if not has_constant_ref and timeout_val >= 1:
                    self.add_issue(
                        f"并发参数 {caller_name}({timeout_val}) 使用硬编码数值，建议提取为类常量或构造函数可配置参数",
                        node.lineno,
                    )
