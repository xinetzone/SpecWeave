import ast
from pathlib import Path

from .constants import LOGGING_CALLS, PRINT_LIKE, TEST_LOCAL_VARS
from .models import HardcodeIssue
from .checks_string import StringChecksMixin
from .checks_numeric import NumericChecksMixin


class HardcodeVisitor(StringChecksMixin, NumericChecksMixin, ast.NodeVisitor):
    def __init__(self, filepath: Path, content_lines: list[str]):
        self.filepath = filepath
        self.content_lines = content_lines
        self.issues: list[HardcodeIssue] = []
        self.in_test_function = False
        self.function_name = ""
        self.in_argparse_setup = False
        self.in_fstring = False
        self._skip_docstring_ranges: set[int] = set()
        self._reported_on_line: dict[int, set[str]] = {}

    def _get_snippet(self, line_no: int) -> str:
        if line_no and line_no <= len(self.content_lines):
            return self.content_lines[line_no - 1].strip()
        return ""

    def _make_issue(self, category: str, severity: str, message: str, line: int, snippet: str = "") -> HardcodeIssue:
        return HardcodeIssue(
            category=category,
            severity=severity,
            message=message,
            line=line,
            snippet=snippet or self._get_snippet(line),
        )

    def _collect_docstrings(self, tree: ast.Module):
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if (node.body and isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant) and
                        isinstance(node.body[0].value.value, str)):
                    ds = node.body[0]
                    start = ds.lineno
                    end = ds.end_lineno or start
                    for ln in range(start, end + 1):
                        self._skip_docstring_ranges.add(ln)

    def visit_Module(self, node: ast.Module):
        self._collect_docstrings(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        old_in_test = self.in_test_function
        old_func_name = self.function_name
        old_in_argparse = self.in_argparse_setup
        self.in_test_function = node.name.startswith("test_") or node.name.startswith("_test_")
        self.function_name = node.name
        self.generic_visit(node)
        self.in_test_function = old_in_test
        self.function_name = old_func_name
        self.in_argparse_setup = old_in_argparse

    def visit_JoinedStr(self, node: ast.JoinedStr):
        old_fstring = self.in_fstring
        self.in_fstring = True
        self.generic_visit(node)
        self.in_fstring = old_fstring

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Attribute):
            caller = node.func.attr
        elif isinstance(node.func, ast.Name):
            caller = node.func.id
        else:
            caller = ""

        is_argparse_call = (
            (isinstance(node.func, ast.Attribute) and node.func.attr in {"add_argument", "add_parser"})
            or (caller in {"ArgumentParser"})
        )

        if caller in LOGGING_CALLS or caller in PRINT_LIKE:
            for arg in node.args:
                if caller in PRINT_LIKE:
                    self._check_string_arg(arg, "HARD-STR", f"打印消息（CLI输出文本）", severity="info")
                else:
                    self._check_string_arg(arg, "HARD-STR", f"日志消息硬编码（{caller}调用）", severity="warn")

        if is_argparse_call:
            for kw in node.keywords:
                if kw.arg in {"help", "description", "epilog", "prog", "usage"}:
                    pass
            old_argparse = self.in_argparse_setup
            self.in_argparse_setup = True
            self.generic_visit(node)
            self.in_argparse_setup = old_argparse
            return

        self.generic_visit(node)

    def visit_keyword(self, node: ast.keyword):
        if self.in_argparse_setup and node.arg in {"help", "description", "epilog", "prog", "usage"}:
            return
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise):
        if node.exc and isinstance(node.exc, ast.Call):
            for arg in node.exc.args:
                self._check_string_arg(arg, "HARD-STR", "异常消息硬编码（raise语句）", severity="warn")
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id.lower()
                if self.in_test_function and any(t in name for t in TEST_LOCAL_VARS):
                    self.generic_visit(node)
                    return
                if name.endswith("_url") or name.endswith("_endpoint") or name.endswith("_api"):
                    self._check_string_value(node.value, "HARD-URL", f"URL配置硬编码（变量{target.id}）")
                elif name.endswith("_path") or name.endswith("_dir") or name.endswith("_file"):
                    self._check_string_value(node.value, "HARD-PATH", f"路径配置硬编码（变量{target.id}）")
                elif name.endswith("_timeout") or name.endswith("_ttl") or name.endswith("_retry") or \
                        name.endswith("_pool_size") or name.endswith("_max_workers") or \
                        name.endswith("_batch_size") or name.endswith("_cache_ttl") or \
                        name.endswith("_threshold") or name.endswith("_limit") or \
                        name.endswith("_page_size"):
                    self._check_numeric_value(node.value, "HARD-CFG", f"配置参数硬编码（变量{target.id}）")
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant):
        if node.lineno is None:
            return
        line_no = node.lineno
        if line_no in self._skip_docstring_ranges:
            return
        if self.in_argparse_setup:
            return
        snippet = self.content_lines[line_no - 1].strip() if line_no <= len(self.content_lines) else ""

        if isinstance(node.value, str):
            self._check_string_constant(node.value, line_no, snippet)
        elif isinstance(node.value, (int, float)):
            self._check_numeric_constant(node.value, line_no, snippet)

    def _add_issue(self, category: str, severity: str, message: str, line: int, snippet: str):
        line_cats = self._reported_on_line.setdefault(line, set())
        dedup_key = f"{category}:{severity}"
        if dedup_key in line_cats:
            return
        line_cats.add(dedup_key)
        self.issues.append(HardcodeIssue(
            category=category, severity=severity, message=message, line=line, snippet=snippet,
        ))

    def _already_reported(self, line: int, category: str, severity: str = "error") -> bool:
        return f"{category}:{severity}" in self._reported_on_line.get(line, set())
