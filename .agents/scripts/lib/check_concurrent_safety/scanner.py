"""并发安全扫描器 - 文件扫描与报告生成。"""

import ast
from pathlib import Path
from typing import Optional

from lib.rules import load_rules

from .models import FileReport, ConcurrencyIssue
from .visitor import ConcurrentSafetyVisitor


def scan_python_file(file_path: Path, root_dir: Path, rules_engine=None) -> FileReport:
    report = FileReport(file_path=file_path)
    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        report.issues.append(ConcurrencyIssue(
            dimension="PARSE",
            code="CC-PARSE",
            severity="warn",
            message="文件编码读取失败，跳过",
            line=0,
            snippet="",
            dimension_name="解析错误",
        ))
        return report

    lines = content.split("\n")
    report.lines_scanned = len(lines)

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError as e:
        report.issues.append(ConcurrencyIssue(
            dimension="PARSE",
            code="CC-PARSE",
            severity="warn",
            message=f"Python语法解析失败（{e.msg}，第{e.lineno}行），跳过",
            line=e.lineno or 0,
            snippet="",
            dimension_name="解析错误",
        ))
        report.score = 100
        return report

    visitor = ConcurrentSafetyVisitor(filepath=file_path, content_lines=lines)
    visitor.visit(tree)

    if rules_engine:
        filtered_issues = []
        for issue in visitor.issues:
            if issue.line > 0 and issue.line <= len(lines):
                norm_line = lines[issue.line - 1].strip()
                if rules_engine.is_excluded_line(norm_line):
                    continue
            try:
                rel = file_path.relative_to(root_dir)
                if rules_engine.should_exclude_path(rel):
                    continue
            except ValueError:
                pass
            filtered_issues.append(issue)
        report.issues = filtered_issues
    else:
        report.issues = visitor.issues

    error_count = sum(1 for i in report.issues if i.severity == "error")
    warn_count = sum(1 for i in report.issues if i.severity == "warn")
    info_count = sum(1 for i in report.issues if i.severity == "info")
    report.score = max(0, 100 - error_count * 15 - warn_count * 5 - info_count * 1)
    return report


def collect_python_files(root_dir: Path, target_file: Path | None, target_path: Path | None) -> list[Path]:
    rules = load_rules()
    if target_file and target_file.is_file():
        return [target_file]

    search_dirs = []
    if target_path and target_path.is_dir():
        search_dirs.append(target_path)
    else:
        scripts_dir = root_dir / ".agents" / "scripts"
        if scripts_dir.is_dir():
            search_dirs.append(scripts_dir)
        lib_dir = root_dir / ".agents" / "scripts" / "lib"
        if lib_dir.is_dir():
            pass

    py_files = []
    for search_dir in search_dirs:
        for py_file in search_dir.rglob("*.py"):
            try:
                should_skip, _ = rules.should_skip_file(py_file, root_dir=root_dir)
            except Exception:
                should_skip = False
            if should_skip:
                continue
            rel = str(py_file.relative_to(root_dir))
            if "__pycache__" in rel or "venv" in rel or ".venv" in rel:
                continue
            py_files.append(py_file)
    return sorted(set(py_files))
