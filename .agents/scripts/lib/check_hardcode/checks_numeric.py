import ast

from .constants import (
    HTTP_STATUS_CODES, UNIT_CONVERSION_NUMS, SENTINEL_NUMS,
)


class NumericChecksMixin:
    def _check_numeric_value(self, value_node, category: str, message: str):
        if isinstance(value_node, ast.Constant) and isinstance(value_node.value, (int, float)):
            val = value_node.value
            if val in SENTINEL_NUMS or val in UNIT_CONVERSION_NUMS:
                return
            self.issues.append(self._make_issue(
                category=category,
                severity="warn",
                message=message + f"：值为{val}",
                line=value_node.lineno,
                snippet=self._get_snippet(value_node.lineno),
            ))

    def _check_numeric_constant(self, val: int | float, line_no: int, snippet: str):
        if self.in_test_function:
            return
        if val in SENTINEL_NUMS:
            return
        if val in HTTP_STATUS_CODES:
            return
        if val in UNIT_CONVERSION_NUMS:
            return
        if isinstance(val, float) and 0 < val < 1:
            return

        if any(kw in snippet for kw in ["timeout", "retry", "max_", "pool", "ttl", "expire",
                                         "batch", "page_size", "limit", "threshold", "sleep"]):
            self.issues.append(self._make_issue(
                category="HARD-CFG",
                severity="warn",
                message=f"硬编码配置参数：值为{val}（建议从配置读取）",
                line=line_no,
                snippet=snippet,
            ))
            return

        if isinstance(val, int) and val > 1 and ("<" in snippet or ">" in snippet or "==" in snippet or "!=" in snippet):
            if not any(c.isalpha() for c in snippet.split("#")[0].split('"')[0].split("'")[0]):
                pass
            else:
                self.issues.append(self._make_issue(
                    category="HARD-NUM",
                    severity="warn",
                    message=f"硬编码业务数值：值为{val}（建议抽取为配置常量）",
                    line=line_no,
                    snippet=snippet,
                ))
