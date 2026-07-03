import ast
from pathlib import Path
from typing import Optional

from lib.rules import load_rules

from .models import FileReport, HardcodeIssue
from .visitor import HardcodeVisitor


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
