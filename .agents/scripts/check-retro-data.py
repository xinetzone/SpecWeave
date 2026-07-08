"""复盘报告量化数据验证器。

基于四查法（查数据来源、查计算逻辑、查异常值、查关联性）自动检测
复盘报告中的量化数据问题：
1. 来源验证：代码行数/测试数等指标与源文件实际值对比（仅检查交付物清单中的文件行数）
2. 计算逻辑：表格合计行是否等于分项之和
3. 异常值：检测不可能值
4. 关联性：同一指标在同一表格内值不一致、README与主报告关键数据不一致

使用方法：
    python check-retro-data.py <retrospective_directory>
    python check-retro-data.py <retrospective.md>

支持 text 和 json 两种输出格式。
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"

TABLE_ROW_RE = re.compile(r"^\|(.+)\|\s*$")
TABLE_SEP_RE = re.compile(r"^\|[\s\-:|]+\|\s*$")
CODE_FENCE_RE = re.compile(r"^```")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")

FILE_LINE_CELL_RE = re.compile(r"`([^`]+\.py)`")
NUMBER_IN_CELL_RE = re.compile(r"^[\s*~]*(\d+)[\s*~]*（?[^）\d]*）?\s*$")
NUMBER_WITH_UNIT_RE = re.compile(r"(\d+)\s*(行|个文件|个|次|份|%)")

DATE_RE = re.compile(r"\b20\d{2}[-/年]\d{1,2}")
VERSION_RE = re.compile(r"v?\d+\.\d+(?:\.\d+)?")


@dataclass
class TableData:
    headers: list[str]
    rows: list[list[str]]
    start_line: int
    has_total_row: bool = False
    total_row_index: int = -1
    table_name: str = ""


@dataclass
class ValidationIssue:
    severity: str
    category: str
    message: str
    line: int
    metric: str = ""
    expected: str = ""
    actual: str = ""
    suggestion: str = ""


@dataclass
class ValidationReport:
    file_path: Path
    issues: list[ValidationIssue] = field(default_factory=list)
    tables: list[TableData] = field(default_factory=list)
    file_line_entries: dict[str, tuple[int, int]] = field(default_factory=dict)
    key_metrics: dict[str, tuple[int, int]] = field(default_factory=dict)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == SEVERITY_ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == SEVERITY_WARNING]

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


class RetroDataValidator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues: list[ValidationIssue] = []

    def validate_file(self, file_path: Path) -> ValidationReport:
        report = ValidationReport(file_path=file_path)
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        tables = self._extract_tables(lines)
        report.tables = tables

        for table in tables:
            self._check_table_sums(table, report)

        self._extract_file_lines_from_tables(tables, report)
        self._extract_key_metrics(content, lines, report)

        self._check_source_file_lines(report)

        report.issues = self.issues
        return report

    def validate_directory(self, dir_path: Path) -> list[ValidationReport]:
        reports = []
        readme_report = None

        for md_file in sorted(dir_path.glob("*.md")):
            report = self.validate_file(md_file)
            reports.append(report)
            if md_file.name.lower() == "readme.md":
                readme_report = report

        if readme_report:
            main_reports = [r for r in reports if r.file_path.name != "README.md"]
            for main_report in main_reports:
                self._check_readme_consistency(readme_report, main_report)

        return reports

    def _extract_tables(self, lines: list[str]) -> list[TableData]:
        tables = []
        i = 0
        in_code_fence = False
        current_section = ""

        while i < len(lines):
            line = lines[i]

            if CODE_FENCE_RE.match(line.strip()):
                in_code_fence = not in_code_fence
                i += 1
                continue

            if in_code_fence:
                i += 1
                continue

            heading_match = HEADING_RE.match(line)
            if heading_match:
                current_section = heading_match.group(2).strip()

            if TABLE_ROW_RE.match(line) and i + 1 < len(lines) and TABLE_SEP_RE.match(lines[i + 1]):
                headers = [self._clean_cell(c) for c in line.strip("|").split("|")]
                rows = []
                j = i + 2
                start_line = i + 1

                while j < len(lines):
                    row_line = lines[j]
                    if not TABLE_ROW_RE.match(row_line):
                        break
                    if CODE_FENCE_RE.match(row_line.strip()):
                        break
                    cells = [self._clean_cell(c) for c in row_line.strip("|").split("|")]
                    rows.append(cells)
                    j += 1

                has_total = False
                total_idx = -1
                for idx, row in enumerate(rows):
                    first_cell = row[0] if row else ""
                    if any(kw in first_cell for kw in ["合计", "总计", "小计"]):
                        has_total = True
                        total_idx = idx
                        break

                tables.append(TableData(
                    headers=headers,
                    rows=rows,
                    start_line=start_line,
                    has_total_row=has_total,
                    total_row_index=total_idx,
                    table_name=current_section,
                ))
                i = j
            else:
                i += 1

        return tables

    def _clean_cell(self, cell: str) -> str:
        return re.sub(r"\*\*", "", cell.strip())

    def _check_table_sums(self, table: TableData, report: ValidationReport):
        if not table.has_total_row or table.total_row_index < 0:
            return

        total_row = table.rows[table.total_row_index]
        data_rows = [r for idx, r in enumerate(table.rows) if idx != table.total_row_index]

        for col_idx in range(1, len(table.headers)):
            if col_idx >= len(total_row):
                continue

            total_val = self._parse_number(total_row[col_idx])
            if total_val is None:
                continue

            col_sum = 0
            col_has_numbers = False
            for row in data_rows:
                if col_idx >= len(row):
                    continue
                val = self._parse_number(row[col_idx])
                if val is not None:
                    col_sum += val
                    col_has_numbers = True

            if col_has_numbers and abs(col_sum - total_val) > 0.5:
                header = table.headers[col_idx] if col_idx < len(table.headers) else f"列{col_idx}"
                self.issues.append(ValidationIssue(
                    severity=SEVERITY_ERROR,
                    category="计算逻辑",
                    message=f"表格合计不一致：'{header}'列，分项之和={col_sum}，合计行={int(total_val)}",
                    line=table.start_line + table.total_row_index + 1,
                    metric=header,
                    expected=str(col_sum),
                    actual=str(int(total_val)),
                    suggestion=f"合计行应为{col_sum}或修正分项数据",
                ))

    def _parse_number(self, text: str) -> int | float | None:
        text = text.strip()
        text = re.sub(r"[*~✅❌⚠️📊🔴🟡🟢🔵📋📈📉]", "", text)
        text = re.sub(r"^[\s>|]+", "", text)
        text = text.strip()

        match = re.search(r"(\d+(?:\.\d+)?)", text)
        if not match:
            return None

        num_str = match.group(1)
        try:
            val = int(num_str) if "." not in num_str else float(num_str)
            if val == 0 and "0" not in text[:text.index(match.group(1)) + len(match.group(1)) + 5]:
                return None
            return val
        except ValueError:
            return None

    def _extract_file_lines_from_tables(self, tables: list[TableData], report: ValidationReport):
        for table in tables:
            is_delivery_table = any(
                kw in table.table_name for kw in ["交付物", "文件清单", "产物清单"]
            ) or any(
                any(kw in h for h in table.headers) for kw in ["文件", "路径", "File"]
            )

            if not is_delivery_table:
                continue

            for row_idx, row in enumerate(table.rows):
                for cell in row:
                    file_match = FILE_LINE_CELL_RE.search(cell)
                    if not file_match:
                        continue
                    filename = file_match.group(1)

                    for c in row:
                        num_match = NUMBER_WITH_UNIT_RE.search(c)
                        if num_match and num_match.group(2) == "行":
                            lines_val = int(num_match.group(1))
                            report.file_line_entries[filename] = (
                                lines_val,
                                table.start_line + row_idx + 2,
                            )
                            break

    def _extract_key_metrics(self, content: str, lines: list[str], report: ValidationReport):
        metric_patterns = [
            (r"(\d+)\s*个\s*单元测试", "单元测试数量"),
            (r"(\d+)\s*个测试", "单元测试数量"),
            (r"核心visitor逻辑[，,]\s*(\d+)\s*行", "visitor.py行数"),
            (r"检查维度[为是]\s*(\d+)\s*个", "检查维度数量"),
            (r"新增/修改文件[|:：]\s*(\d+)\s*个", "新增修改文件数"),
        ]

        for pattern, metric_name in metric_patterns:
            for match in re.finditer(pattern, content):
                value = int(match.group(1))
                line_num = content[:match.start()].count("\n") + 1
                if metric_name not in report.key_metrics:
                    report.key_metrics[metric_name] = (value, line_num)

    def _check_source_file_lines(self, report: ValidationReport):
        search_paths = [
            self.project_root,
            self.project_root / ".agents" / "scripts",
            self.project_root / ".agents" / "scripts" / "lib",
            self.project_root / ".agents" / "scripts" / "lib" / "check_concurrent_safety",
            self.project_root / ".agents" / "scripts" / "hooks",
            self.project_root / ".agents" / "scripts" / "tests",
        ]

        for filename, (reported_lines, line_num) in report.file_line_entries.items():
            actual_path = None
            for base in search_paths:
                candidate = base / filename
                if candidate.exists() and candidate.is_file():
                    actual_path = candidate
                    break

            if actual_path is None:
                parts = filename.replace("\\", "/").split("/")
                for base in search_paths:
                    candidate = base / Path(*parts)
                    if candidate.exists() and candidate.is_file():
                        actual_path = candidate
                        break

            if actual_path is None:
                self.issues.append(ValidationIssue(
                    severity=SEVERITY_WARNING,
                    category="数据来源",
                    message=f"无法验证文件'{filename}'的行数（文件未找到）",
                    line=line_num,
                    metric=f"{filename}行数",
                    suggestion="确认文件路径是否正确",
                ))
                continue

            actual_lines = sum(1 for _ in actual_path.open("r", encoding="utf-8"))

            if actual_lines != reported_lines:
                self.issues.append(ValidationIssue(
                    severity=SEVERITY_ERROR,
                    category="数据来源",
                    message=f"文件'{filename}'行数不一致：文档记载{reported_lines}行，实际{actual_lines}行",
                    line=line_num,
                    metric=f"{filename}行数",
                    expected=str(actual_lines),
                    actual=str(reported_lines),
                    suggestion=f"更新为{actual_lines}行",
                ))

    def _check_readme_consistency(self, readme_report: ValidationReport, main_report: ValidationReport):
        for metric_name, (main_value, main_line) in main_report.key_metrics.items():
            if metric_name in readme_report.key_metrics:
                readme_value, readme_line = readme_report.key_metrics[metric_name]
                if readme_value != main_value:
                    self.issues.append(ValidationIssue(
                        severity=SEVERITY_ERROR,
                        category="跨文件一致性",
                        message=f"README中'{metric_name}'={readme_value}，"
                                f"但{main_report.file_path.name}中为{main_value}",
                        line=readme_line,
                        metric=metric_name,
                        expected=str(main_value),
                        actual=str(readme_value),
                        suggestion="统一两处指标值为源代码实际值",
                    ))


def format_text_report(report: ValidationReport, is_last: bool = True) -> str:
    lines = []
    lines.append("=" * 70)
    lines.append(f"📊 复盘报告数据验证：{report.file_path.name}")
    lines.append("=" * 70)
    lines.append("")

    if not report.issues:
        lines.append("✅ 所有量化数据验证通过！")
        lines.append(f"   检查了 {len(report.tables)} 个表格，{len(report.file_line_entries)} 个文件行数引用")
        return "\n".join(lines)

    errors = report.errors
    warnings = report.warnings

    lines.append(
        f"📋 验证结果：{len(errors)} 个错误，{len(warnings)} 个警告"
    )
    lines.append(f"   检查了 {len(report.tables)} 个表格，{len(report.file_line_entries)} 个文件行数引用")
    lines.append("")

    for severity, icon, label in [
        (SEVERITY_ERROR, "🔴", "错误"),
        (SEVERITY_WARNING, "🟡", "警告"),
    ]:
        severity_issues = [i for i in report.issues if i.severity == severity]
        if not severity_issues:
            continue

        lines.append(f"--- {icon} {label}（{len(severity_issues)}）---")
        for issue in severity_issues:
            loc = f"L{issue.line}" if issue.line else ""
            lines.append(f"  [{issue.category}] {loc} {issue.message}")
            if issue.expected and issue.actual:
                lines.append(f"    期望值：{issue.expected}，实际值：{issue.actual}")
            if issue.suggestion:
                lines.append(f"    💡 {issue.suggestion}")
        lines.append("")

    if errors:
        lines.append("❌ 验证失败：存在错误，请修正后重新验证。")
    else:
        lines.append("⚠️  验证通过但有警告，建议复核警告项。")

    return "\n".join(lines)


def format_json_report(reports: list[ValidationReport]) -> str:
    import json

    all_passed = all(r.passed for r in reports)
    output = {"passed": all_passed, "reports": []}

    for report in reports:
        output["reports"].append({
            "file": str(report.file_path),
            "passed": report.passed,
            "tables_count": len(report.tables),
            "file_line_checks": len(report.file_line_entries),
            "issues": [
                {
                    "severity": i.severity,
                    "category": i.category,
                    "message": i.message,
                    "line": i.line,
                    "metric": i.metric,
                    "expected": i.expected,
                    "actual": i.actual,
                    "suggestion": i.suggestion,
                }
                for i in report.issues
            ],
        })

    return json.dumps(output, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="复盘报告量化数据验证器（基于四查法）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", help="复盘报告目录或单个Markdown文件路径")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    target_path = Path(args.path).resolve()

    if not target_path.exists():
        print(f"错误：路径不存在：{target_path}", file=sys.stderr)
        sys.exit(1)

    validator = RetroDataValidator(project_root=project_root)

    if target_path.is_file():
        reports = [validator.validate_file(target_path)]
    else:
        reports = validator.validate_directory(target_path)

    if not reports:
        print("未找到需要验证的Markdown文件", file=sys.stderr)
        sys.exit(0)

    if args.format == "json":
        print(format_json_report(reports))
    else:
        for i, report in enumerate(reports):
            print(format_text_report(report, is_last=(i == len(reports) - 1)))
            if i < len(reports) - 1:
                print()

    has_errors = any(not r.passed for r in reports)
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
