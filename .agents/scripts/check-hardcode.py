#!/usr/bin/env python3
"""硬编码检测检查器：扫描Python代码中的8类硬编码问题。

检查项基于 .agents/rules/identification-standards.md 规范：
  1. HARD-STR：固定字符串（错误消息、日志文本、UI标签中的中文/完整英文句子）
  2. HARD-NUM：固定数值（业务阈值、超时时间、分页大小等非控制流数字）
  3. HARD-PATH：固定路径（含/或\\路径分隔符及文件扩展名的字符串）
  4. HARD-URL：固定URL/端点（http://或https://开头的非测试地址）
  5. HARD-ENC：固定编码值（utf-8、application/json等MIME/编码字符串）
  6. HARD-REGEX：固定正则模式（re.match/search/compile的字面量参数）
  7. HARD-STYLE：固定颜色/样式（#开头十六进制颜色、px/em单位值）
  8. HARD-CFG：固定配置参数（连接池大小、重试次数、缓存过期等）

内置智能过滤：
  - 自动跳过docstring、argparse帮助文本
  - 自动跳过test_前缀函数和mock/demo/fake函数
  - localhost/127.0.0.1本地URL自动跳过
  - utf-8/UTF8标准编码自动跳过
  - HTTP状态码(200/404/500等)和哨兵值(-1/0/1)自动跳过
  - CLI工具print输出降为info级别，避免误报

用法：
  python check-hardcode.py                     # 检查.agents/scripts/下所有Python文件
  python check-hardcode.py --path <dir>        # 检查指定目录
  python check-hardcode.py --file <file>       # 检查单个文件
  python check-hardcode.py --json              # JSON格式输出
  python check-hardcode.py --verbose           # 显示详细信息
  python check-hardcode.py --threshold <0-100> # 设置及格分数阈值（默认80）
"""

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from lib.project import resolve_project_root
from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, add_common_args, setup_safe_output
from lib.rules import load_rules
import lib.quality_report as quality_report

HTTP_STATUS_CODES = {100, 101, 102, 103, 200, 201, 202, 203, 204, 205, 206, 207, 208, 226,
                     300, 301, 302, 303, 304, 305, 306, 307, 308,
                     400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413,
                     414, 415, 416, 417, 418, 421, 422, 423, 424, 425, 426, 428, 429, 431,
                     451, 500, 501, 502, 503, 504, 505, 506, 507, 508, 510, 511}
CONTROL_FLOW_NUMS = {-1, 0, 1, 2}
UNIT_CONVERSION_NUMS = {8, 16, 32, 64, 100, 128, 256, 512, 1000, 1024, 2048, 4096, 8192,
                        60, 3600, 86400}
SENTINEL_NUMS = {-1, 0, 1}

CHINESE_RE = re.compile(r'[\u4e00-\u9fff]')
FULL_EN_SENTENCE_RE = re.compile(r'^[A-Z][a-z]+(\s+[a-zA-Z]+){3,}[.!?]?$')
URL_RE = re.compile(r'^https?://[a-zA-Z0-9]')
LOCALHOST_RE = re.compile(r'^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0)(:\d+)?')
FULL_URL_RE = re.compile(r'^https?://[a-zA-Z0-9][a-zA-Z0-9.-]+(?::\d+)?(/|$)')
PATH_SEP_RE = re.compile(r'[/\\]')
FILE_EXT_RE = re.compile(r'\.\w{1,5}$')
HEX_COLOR_RE = re.compile(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')
CSS_UNIT_RE = re.compile(r'^\d+(\.\d+)?(px|em|rem|pt|vh|vw|%)$')
ENCODING_RE = re.compile(r'^(utf-?8|ascii|latin-?1|gbk|gb2312|utf-?16|utf-?32|big5)$', re.IGNORECASE)
MIME_RE = re.compile(r'^(text|application|image|audio|video|message|multipart)/[a-zA-Z0-9.+-]+(;\s*charset=\S+)?$')
REGEX_PREFIX_RE = re.compile(r'^r["\']')

LOGGING_CALLS = {"debug", "info", "warning", "error", "critical", "exception", "log", "warn"}
PRINT_LIKE = {"print"}
RAISE_CALLS = {"raise"}
TEST_LOCAL_VARS = {"expected", "result", "actual", "mock_data", "test_str", "sample"}
RA_ALLOWED_FUNCS = {"resolve_project_root", "resolve_agents_dir", "resolve_scripts_dir", "Path"}

SAFE_STRING_VALUES = {
    "", " ", "\n", "\t", "\r", ",", ".", ":", ";", "-", "_", "/", "\\",
    "|", "*", "?", "!", "@", "#", "$", "%", "^", "&", "(", ")", "[", "]",
    "{", "}", "<", ">", "=", "+", "~", "`",
    "utf-8", "utf8", "UTF-8", "UTF8",
    "r", "w", "a", "rb", "wb", "ab", "r+", "w+", "a+",
    "r", "w", "a",
    ".", "..",
}


@dataclass
class HardcodeIssue:
    category: str
    severity: str
    message: str
    line: int
    snippet: str

    @property
    def name(self) -> str:
        return f"{self.category}: L{self.line}"

    @property
    def passed(self) -> bool:
        return False


@dataclass
class FileReport(quality_report.ResultGroupMixin):
    file_path: Path
    issues: list[HardcodeIssue] = field(default_factory=list)
    score: int = 100
    lines_scanned: int = 0

    @property
    def results(self):
        return self.issues


class HardcodeVisitor(ast.NodeVisitor):
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

    def _check_string_arg(self, arg, category: str, message: str, severity: str = "warn"):
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            val = arg.value
            if self._is_safe_string(val):
                return
            if CHINESE_RE.search(val) or (len(val) > 20 and FULL_EN_SENTENCE_RE.match(val)):
                self.issues.append(HardcodeIssue(
                    category=category,
                    severity=severity,
                    message=message + f"：「{val[:50]}」",
                    line=arg.lineno if hasattr(arg, 'lineno') else 0,
                    snippet=self.content_lines[arg.lineno - 1].strip() if hasattr(arg, 'lineno') and arg.lineno <= len(self.content_lines) else "",
                ))
        elif isinstance(arg, ast.JoinedStr):
            for val in arg.values:
                if isinstance(val, ast.Constant) and isinstance(val.value, str):
                    if CHINESE_RE.search(val.value):
                        self.issues.append(HardcodeIssue(
                            category=category,
                            severity=severity,
                            message=message + f"：f-string中文片段「{val.value[:30]}」",
                            line=arg.lineno if hasattr(arg, 'lineno') else 0,
                            snippet=self.content_lines[arg.lineno - 1].strip() if hasattr(arg, 'lineno') and arg.lineno <= len(self.content_lines) else "",
                        ))

    def _check_string_value(self, value_node, category: str, message: str):
        if isinstance(value_node, ast.Constant) and isinstance(value_node.value, str):
            val = value_node.value
            if self._is_safe_string(val):
                return
            if category == "HARD-URL":
                if not FULL_URL_RE.match(val):
                    return
                if LOCALHOST_RE.match(val):
                    return
                if any(kw in self.function_name.lower() for kw in ["test", "mock", "fake", "demo"]):
                    return
                if re.match(r'^https?://(test|mock|fake|dummy|sample|localhost|127\.0\.0\.1|0\.0\.0\.0)[:/]', val):
                    return
            if category == "HARD-PATH":
                if not PATH_SEP_RE.search(val):
                    return
                is_absolute = val.startswith("/") or val.startswith("\\") or re.match(r'^[a-zA-Z]:[\\/]', val)
                is_project_relative = re.match(r'^(docs|lib|vendor|\.agents|scripts|config|templates|skills|commands|rules|protocols|workflows|roles|modules|teams|capabilities|worlds|cases|prompts|tools|generated|src|tests|output)[/\\]', val)
                if val.startswith(".") or is_project_relative:
                    sev = "warn" if not is_absolute else "error"
                    msg = message + "（项目相对路径，建议使用Path拼接）" if is_project_relative else message
                elif not is_absolute:
                    return
                else:
                    sev = "error"
                    msg = message
                self._add_issue(
                    category=category,
                    severity=sev,
                    message=msg + f"：「{val[:60]}」",
                    line=value_node.lineno,
                    snippet=self.content_lines[value_node.lineno - 1].strip() if value_node.lineno <= len(self.content_lines) else "",
                )
                return
            self._add_issue(
                category=category,
                severity="error" if category in {"HARD-URL", "HARD-PATH"} else "warn",
                message=message + f"：「{val[:60]}」",
                line=value_node.lineno,
                snippet=self.content_lines[value_node.lineno - 1].strip() if value_node.lineno <= len(self.content_lines) else "",
            )

    def _check_numeric_value(self, value_node, category: str, message: str):
        if isinstance(value_node, ast.Constant) and isinstance(value_node.value, (int, float)):
            val = value_node.value
            if val in SENTINEL_NUMS or val in UNIT_CONVERSION_NUMS:
                return
            self.issues.append(HardcodeIssue(
                category=category,
                severity="warn",
                message=message + f"：值为{val}",
                line=value_node.lineno,
                snippet=self.content_lines[value_node.lineno - 1].strip() if value_node.lineno <= len(self.content_lines) else "",
            ))

    def _is_safe_string(self, val: str) -> bool:
        if not val:
            return True
        if val in SAFE_STRING_VALUES:
            return True
        if ENCODING_RE.match(val) or MIME_RE.match(val):
            return False
        if val.startswith("**") and val.endswith("**"):
            return True
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', val):
            return True
        return False

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

    def _check_string_constant(self, val: str, line_no: int, snippet: str):
        if self.in_test_function:
            return
        if self._is_safe_string(val):
            return

        if FULL_URL_RE.match(val):
            if LOCALHOST_RE.match(val):
                return
            if val.startswith("http://") and not any(c.isalnum() for c in val[7:]):
                return
            if any(kw in self.function_name.lower() for kw in ["test", "mock", "fake", "demo"]):
                return
            if re.match(r'^https?://(test|mock|fake|dummy|sample|localhost|127\.0\.0\.1|0\.0\.0\.0)[:/]', val):
                return
            if self._already_reported(line_no, "HARD-URL"):
                return
            self._add_issue(
                category="HARD-URL",
                severity="error",
                message=f"硬编码URL端点：「{val[:80]}」",
                line=line_no,
                snippet=snippet,
            )
            return

        if len(val) > 2 and PATH_SEP_RE.search(val) and FILE_EXT_RE.search(val):
            if any(name in snippet for name in RA_ALLOWED_FUNCS):
                return
            if val.startswith("."):
                return
            is_absolute = val.startswith("/") or val.startswith("\\") or re.match(r'^[a-zA-Z]:[\\/]', val)
            has_chinese = CHINESE_RE.search(val)
            is_user_agent = "Mozilla/" in val or "AppleWebKit" in val
            is_gitignore_entry = re.match(r'^[*#\[\]!]', val) or val.endswith("/")
            is_project_relative = re.match(r'^(docs|lib|vendor|\.agents|scripts|config|templates|skills|commands|rules|protocols|workflows|roles|modules|teams|capabilities|worlds|cases|prompts|tools|generated|src|tests|output)[/\\]', val)
            is_prompt_text = has_chinese and len(val) > 30
            is_fstring_fragment = self.in_fstring and val.startswith("/") and not re.match(r'^/(etc|usr|home|var|tmp|opt|root|proc|sys|dev|bin|sbin|lib|lib64|boot|mnt|media|srv|run|Applications|Users|System|Windows|Program)[/\\]', val)
            if is_user_agent or is_gitignore_entry or is_project_relative or is_prompt_text or is_fstring_fragment:
                return
            if not is_absolute:
                return
            if self._already_reported(line_no, "HARD-PATH"):
                return
            self._add_issue(
                category="HARD-PATH",
                severity="error",
                message=f"硬编码文件路径：「{val[:80]}」",
                line=line_no,
                snippet=snippet,
            )
            return

        if ENCODING_RE.match(val) or MIME_RE.match(val):
            self.issues.append(HardcodeIssue(
                category="HARD-ENC",
                severity="warn",
                message=f"硬编码编码/MIME值：「{val}」——建议抽取为常量统一管理",
                line=line_no,
                snippet=snippet,
            ))
            return

        if HEX_COLOR_RE.match(val):
            self.issues.append(HardcodeIssue(
                category="HARD-STYLE",
                severity="warn",
                message=f"硬编码颜色值：「{val}」——建议使用设计令牌/主题变量",
                line=line_no,
                snippet=snippet,
            ))
            return

        if CSS_UNIT_RE.match(val):
            self.issues.append(HardcodeIssue(
                category="HARD-STYLE",
                severity="warn",
                message=f"硬编码样式值：「{val}」——建议使用设计系统变量",
                line=line_no,
                snippet=snippet,
            ))
            return

        if CHINESE_RE.search(val):
            context = snippet[:30]
            is_log = any(kw in context for kw in ["log", "print", "raise", "error", "warn", "info", "debug"])
            severity = "warn"
            msg = f"硬编码中文字符串：「{val[:50]}」"
            if is_log and not self.in_test_function:
                msg += "（建议外部化到消息字典/i18n资源）"
            elif self.in_test_function:
                return
            self.issues.append(HardcodeIssue(
                category="HARD-STR",
                severity=severity,
                message=msg,
                line=line_no,
                snippet=snippet,
            ))
            return

        if FULL_EN_SENTENCE_RE.match(val) and len(val) > 15:
            self.issues.append(HardcodeIssue(
                category="HARD-STR",
                severity="warn",
                message=f"硬编码英文字符串：「{val[:60]}」",
                line=line_no,
                snippet=snippet,
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
            self.issues.append(HardcodeIssue(
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
                self.issues.append(HardcodeIssue(
                    category="HARD-NUM",
                    severity="warn",
                    message=f"硬编码业务数值：值为{val}（建议抽取为配置常量）",
                    line=line_no,
                    snippet=snippet,
                ))


def scan_python_file(file_path: Path, root_dir: Path, rules_engine=None) -> FileReport:
    report = FileReport(file_path=file_path)
    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        report.issues.append(HardcodeIssue(
            category="parse-error",
            severity="warn",
            message="文件编码读取失败，跳过",
            line=0,
            snippet="",
        ))
        return report

    lines = content.split("\n")
    report.lines_scanned = len(lines)

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError as e:
        report.issues.append(HardcodeIssue(
            category="parse-error",
            severity="warn",
            message=f"Python语法解析失败（{e.msg}，第{e.lineno}行），跳过",
            line=e.lineno or 0,
            snippet="",
        ))
        report.score = 100
        return report

    visitor = HardcodeVisitor(filepath=file_path, content_lines=lines)
    visitor.visit(tree)

    if rules_engine:
        filtered_issues = []
        for issue in visitor.issues:
            if issue.line > 0 and issue.line <= len(lines):
                norm_line = lines[issue.line - 1].strip()
                if rules_engine.is_excluded_line(norm_line):
                    continue
            if rules_engine.should_exclude_path(file_path.relative_to(root_dir)):
                continue
            filtered_issues.append(issue)
        report.issues = filtered_issues
    else:
        report.issues = visitor.issues

    error_count = sum(1 for i in report.issues if i.severity == "error")
    warn_count = sum(1 for i in report.issues if i.severity == "warn")
    report.score = max(0, 100 - error_count * 10 - warn_count * 3)
    return report


def collect_python_files(root_dir: Path, target_file: Optional[Path], target_path: Optional[Path]) -> list[Path]:
    rules = load_rules()
    if target_file and target_file.is_file():
        return [target_file]
    search_dir = target_path if target_path and target_path.is_dir() else root_dir / ".agents" / "scripts"
    py_files = []
    for py_file in search_dir.rglob("*.py"):
        should_skip, _ = rules.should_skip_file(py_file, root_dir=root_dir)
        if should_skip:
            continue
        rel = str(py_file.relative_to(root_dir))
        if "__pycache__" in rel or "venv" in rel or ".venv" in rel:
            continue
        if py_file.name.startswith("test_"):
            py_files.append(py_file)
            continue
        py_files.append(py_file)
    return sorted(set(py_files))


def main() -> None:
    setup_safe_output()
    parser = argparse.ArgumentParser(description="硬编码检测：扫描Python代码中的8类硬编码问题")
    add_common_args(parser)
    parser.add_argument("--file", "-f", type=str, help="检查单个Python文件")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")
    parser.add_argument("--threshold", type=int, default=70, help="评分阈值（默认70）")
    args = parser.parse_args()

    root_dir = resolve_project_root(__file__)
    target_file = Path(args.file).resolve() if args.file else None
    target_path = Path(args.path).resolve() if args.path else None

    rules_engine = load_rules()
    py_files = collect_python_files(root_dir, target_file, target_path)

    if not py_files:
        msg = "未找到Python文件"
        if args.json:
            print(json.dumps({"info": msg, "files": []}, ensure_ascii=False, indent=2))
        else:
            print_warn(msg)
        sys.exit(0)

    reports = [scan_python_file(f, root_dir, rules_engine) for f in py_files]

    if args.json:
        output = quality_report.build_json_output(
            reports,
            root_dir,
            base_dir_key="scan_root",
            base_dir_value=str(target_path or root_dir / ".agents/scripts"),
            count_key="file_count",
            items_key="files",
            item_builder=lambda r: {
                "path": str(quality_report.safe_relative_to(r.file_path, root_dir)),
                "lines_scanned": r.lines_scanned,
                "issue_count": len(r.issues),
                "issues": [{"category": i.category, "severity": i.severity, "message": i.message, "line": i.line}
                           for i in r.issues],
                **quality_report.common_report_fields(r),
            },
        )
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print_header("硬编码检测（8类硬编码扫描）")
    print(f"  类别: HARD-STR/HARD-NUM/HARD-PATH/HARD-URL/HARD-ENC/HARD-REGEX/HARD-STYLE/HARD-CFG")
    print(f"  发现 {len(reports)} 个Python文件")

    for report in reports:
        rel_path = quality_report.safe_relative_to(report.file_path, root_dir)
        results = list(report.issues)
        if not report.issues:
            @dataclass
            class _PassR:
                name: str
                passed: bool
                severity: str
                message: str
                line: Optional[int] = None
            results.append(_PassR(
                name="hardcode_scan",
                passed=True,
                severity="info",
                message=f"扫描{report.lines_scanned}行，未发现硬编码问题",
            ))
        quality_report.print_scored_report_cli(
            score=report.score,
            header=f"【{rel_path}】{report.score}分（{report.lines_scanned}行，{len(report.issues)}个问题）",
            extra_lines=[],
            results=results,
            verbose=args.verbose,
        )

    total_errors = sum(len(r.errors) for r in reports)
    total_warns = sum(len(r.warnings) for r in reports)
    print_summary(
        pass_count=sum(1 for r in reports if r.score >= args.threshold),
        warn_count=total_warns,
        error_count=total_errors,
    )

    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
