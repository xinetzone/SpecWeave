#!/usr/bin/env python3
"""RACI合规性检查器：验证Markdown文档中的RACI矩阵是否符合治理规范。

检查项基于 .agents/rules/raci-governance-standards.md 规范：
  1. A唯一性约束：每行有且仅有一个A（**A**或**R/A**），A必须加粗
  2. R≠A分离原则：执行操作类活动R≠A（developer R→reviewer A），质量门禁类允许reviewer R/A
  3. 角色列完整性：RACI表头包含标准6角色列
  4. co-founder审批合理性：co-founder作为A仅限于重大/关键场景

用法：
  python check-raci-compliance.py                     # 检查.agents/下所有含RACI矩阵的文档
  python check-raci-compliance.py --file <file>       # 检查指定文件
  python check-raci-compliance.py --path <dir>        # 检查指定目录
  python check-raci-compliance.py --json              # JSON格式输出
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from lib.project import resolve_project_root
from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, add_common_args, setup_safe_output
from lib.markdown import find_markdown_files
from lib.rules import load_rules
import lib.quality_report as quality_report

RACI_ROLES = {"orchestrator", "architect", "developer", "reviewer", "tester", "co-founder"}
RACI_VALUES = {"R", "A", "C", "I", "R/A"}

TABLE_ROW_RE = re.compile(r"^\|.*\|\s*$")
TABLE_SEPARATOR_RE = re.compile(r"^\|[\s:|-]+\|\s*$")
BOLD_A_RE = re.compile(r"\*\*A\*\*")
BOLD_RA_RE = re.compile(r"\*\*R/A\*\*")
PLAIN_A_RE = re.compile(r"(?<!\*)A(?!\*)")
BOLD_R_RE = re.compile(r"\*\*R\*\*")

EXECUTION_KEYWORDS = ["代码实现", "文件修改", "提交", "文件拆分", "引用更新", "格式转换", "实现", "开发", "编码", "执行操作"]
QUALITY_GATE_KEYWORDS = ["质量验收", "安全审计", "审查", "审批", "门禁", "验收", "检查", "评审", "审计", "review"]
MAJOR_DECISION_KEYWORDS = ["重大", "关键", "架构变更", "核心数据", "敏感操作", "紧急绕过", "co-founder最终审批"]

RACI_MATRIX_HEADER_HINTS = ["RACI", "责任分配", "orchestrator", "architect", "developer", "reviewer", "tester", "co-founder"]


@dataclass
class CheckResult:
    name: str
    passed: bool
    severity: str
    message: str
    line: Optional[int] = None
    row: Optional[int] = None


@dataclass
class RaciTable:
    header_line: int
    columns: list[str]
    role_columns: dict[str, int]
    rows: list[tuple[int, list[str]]]


@dataclass
class FileReport(quality_report.ResultGroupMixin):
    file_path: Path
    results: list[CheckResult] = field(default_factory=list)
    score: int = 0
    raci_tables_found: int = 0


def is_raci_table_header(line: str) -> bool:
    lower = line.lower()
    role_hits = sum(1 for role in RACI_ROLES if role in lower)
    return role_hits >= 3 or "raci" in lower and role_hits >= 2


def parse_markdown_tables(content: str) -> list[tuple[int, list[str], list[tuple[int, list[str]]]]]:
    lines = content.split("\n")
    tables = []
    in_code_block = False
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            i += 1
            continue
        if in_code_block:
            i += 1
            continue
        if TABLE_ROW_RE.match(line) and i + 1 < len(lines) and TABLE_SEPARATOR_RE.match(lines[i + 1]):
            if is_raci_table_header(line):
                header_cells = [c.strip() for c in line.strip("|").split("|")]
                data_rows = []
                j = i + 2
                while j < len(lines):
                    row_line = lines[j]
                    if row_line.strip().startswith("```"):
                        break
                    if not TABLE_ROW_RE.match(row_line):
                        break
                    cells = [c.strip() for c in row_line.strip("|").split("|")]
                    first_cell = cells[0].strip() if cells else ""
                    if first_cell in ("...", "…", "...") or set(first_cell) <= {'.', ' ', '\t'}:
                        j += 1
                        continue
                    data_rows.append((j + 1, cells))
                    j += 1
                tables.append((i + 1, header_cells, data_rows))
                i = j
                continue
        i += 1
    return tables


def parse_raci_table(content: str) -> list[RaciTable]:
    raw_tables = parse_markdown_tables(content)
    raci_tables = []
    for header_line, header_cells, data_rows in raw_tables:
        role_columns = {}
        for idx, cell in enumerate(header_cells):
            cell_lower = cell.lower().strip("*").strip()
            for role in RACI_ROLES:
                if role in cell_lower:
                    role_columns[role] = idx
                    break
        if len(role_columns) >= 3:
            raci_tables.append(RaciTable(
                header_line=header_line,
                columns=header_cells,
                role_columns=role_columns,
                rows=data_rows,
            ))
    return raci_tables


def count_a_in_row(cells: list[str], role_columns: dict[str, int]) -> tuple[int, bool, list[str]]:
    a_count = 0
    has_plain_a = False
    a_roles = []
    for role, col_idx in role_columns.items():
        if col_idx >= len(cells):
            continue
        cell = cells[col_idx].strip()
        if BOLD_A_RE.search(cell) or BOLD_RA_RE.search(cell):
            a_count += 1
            a_roles.append(role)
        elif re.search(r'(?<!\*)(?<!\w)/?A(?!\w)(?!\*)', cell):
            if not BOLD_A_RE.search(cell):
                has_plain_a = True
                a_count += 1
                a_roles.append(f"{role}(未加粗)")
    return a_count, has_plain_a, a_roles


def check_a_uniqueness(table: RaciTable) -> list[CheckResult]:
    results = []
    for row_num, (line_no, cells) in enumerate(table.rows, 1):
        if len(cells) < 2:
            continue
        activity = cells[0] if cells else ""
        a_count, has_plain_a, a_roles = count_a_in_row(cells, table.role_columns)

        if a_count == 0:
            results.append(CheckResult(
                name="a_uniqueness",
                passed=False,
                severity="error",
                message=f"第{row_num}行「{activity[:30]}」缺少A（最终审批者），每行必须有且仅有一个A",
                line=line_no,
                row=row_num,
            ))
        elif a_count > 1:
            results.append(CheckResult(
                name="a_uniqueness",
                passed=False,
                severity="error",
                message=f"第{row_num}行「{activity[:30]}」存在{a_count}个A（{', '.join(a_roles)}），违反A唯一性约束——须按场景拆分为多行或重新分配",
                line=line_no,
                row=row_num,
            ))
        elif has_plain_a:
            results.append(CheckResult(
                name="a_bold_format",
                passed=False,
                severity="error",
                message=f"第{row_num}行「{activity[:30]}」的A未加粗，必须使用**A**或**R/A**格式以便视觉识别和自动检测",
                line=line_no,
                row=row_num,
            ))
        else:
            results.append(CheckResult(
                name="a_uniqueness",
                passed=True,
                severity="error",
                message=f"第{row_num}行A唯一（{', '.join(a_roles)}）",
                line=line_no,
                row=row_num,
            ))
    return results


def is_execution_activity(activity: str) -> bool:
    return any(kw in activity for kw in EXECUTION_KEYWORDS)


def is_quality_gate_activity(activity: str) -> bool:
    return any(kw in activity for kw in QUALITY_GATE_KEYWORDS)


def is_major_decision(activity: str) -> bool:
    return any(kw in activity for kw in MAJOR_DECISION_KEYWORDS)


def check_r_a_separation(table: RaciTable) -> list[CheckResult]:
    results = []
    for row_num, (line_no, cells) in enumerate(table.rows, 1):
        if len(cells) < 2:
            continue
        activity = cells[0] if cells else ""

        dev_col = table.role_columns.get("developer")
        rev_col = table.role_columns.get("reviewer")
        cof_col = table.role_columns.get("co-founder")

        if dev_col is None or rev_col is None:
            continue

        dev_cell = cells[dev_col] if dev_col < len(cells) else ""
        rev_cell = cells[rev_col] if rev_col < len(cells) else ""
        cof_cell = cells[cof_col] if cof_col is not None and cof_col < len(cells) else ""

        dev_has_r = bool(BOLD_R_RE.search(dev_cell) or "R" in dev_cell.replace("C", "").replace("I", "").replace("A", "").replace("/", "").strip())
        dev_has_a = bool(BOLD_A_RE.search(dev_cell) or BOLD_RA_RE.search(dev_cell))
        rev_has_r = bool(BOLD_R_RE.search(rev_cell) or re.search(r'(^|[^*])R([^*]|$)', rev_cell))
        rev_has_a = bool(BOLD_A_RE.search(rev_cell) or BOLD_RA_RE.search(rev_cell))
        rev_has_ra = bool(BOLD_RA_RE.search(rev_cell))
        cof_has_a = bool(BOLD_A_RE.search(cof_cell) or BOLD_RA_RE.search(cof_cell))

        if is_execution_activity(activity) and dev_has_r:
            if dev_has_a:
                results.append(CheckResult(
                    name="r_a_separation",
                    passed=False,
                    severity="error",
                    message=f"第{row_num}行「{activity[:30]}」developer同时为R和A，违反R≠A分离原则——执行类活动必须由reviewer审批",
                    line=line_no,
                    row=row_num,
                ))
            elif not rev_has_a:
                results.append(CheckResult(
                    name="r_a_separation",
                    passed=False,
                    severity="warn",
                    message=f"第{row_num}行「{activity[:30]}」developer为R但reviewer非A——执行类活动建议由reviewer作为最终审批者",
                    line=line_no,
                    row=row_num,
                ))
            else:
                results.append(CheckResult(
                    name="r_a_separation",
                    passed=True,
                    severity="error",
                    message=f"第{row_num}行R≠A分离合规（developer R, reviewer A）",
                    line=line_no,
                    row=row_num,
                ))

        if rev_has_ra:
            if is_quality_gate_activity(activity):
                results.append(CheckResult(
                    name="r_a_separation.reviewer_exception",
                    passed=True,
                    severity="warn",
                    message=f"第{row_num}行reviewer R/A符合质量门禁例外条款",
                    line=line_no,
                    row=row_num,
                ))
            elif is_execution_activity(activity):
                results.append(CheckResult(
                    name="r_a_separation.reviewer_exception",
                    passed=False,
                    severity="error",
                    message=f"第{row_num}行「{activity[:30]}」是执行类活动，reviewer R/A仅适用于质量门禁类（检查/审计/验收），执行类须R≠A",
                    line=line_no,
                    row=row_num,
                ))

        if cof_has_a and not is_major_decision(activity):
            results.append(CheckResult(
                name="cofounder_approval_scope",
                passed=False,
                severity="warn",
                message=f"第{row_num}行「{activity[:30]}」co-founder作为A——co-founder审批仅限重大/关键场景（L5），常规活动不应过度审批",
                line=line_no,
                row=row_num,
            ))

    return results


def check_role_columns(table: RaciTable) -> list[CheckResult]:
    results = []
    missing_roles = RACI_ROLES - set(table.role_columns.keys())
    if missing_roles:
        results.append(CheckResult(
            name="role_columns_complete",
            passed=False,
            severity="warn",
            message=f"RACI表头缺少标准角色列：{', '.join(sorted(missing_roles))}（建议包含全部6个角色：orchestrator/architect/developer/reviewer/tester/co-founder）",
            line=table.header_line,
        ))
    else:
        results.append(CheckResult(
            name="role_columns_complete",
            passed=True,
            severity="warn",
            message="RACI表头包含全部6个标准角色列",
            line=table.header_line,
        ))
    return results


def calculate_score(report: FileReport) -> int:
    score = 100
    for r in report.results:
        if r.passed:
            continue
        if r.severity == "error":
            score -= 10
        elif r.severity == "warn":
            score -= 3
    return max(0, min(100, score))


def check_file(file_path: Path, root: Path) -> FileReport:
    content = file_path.read_text(encoding="utf-8")
    report = FileReport(file_path=file_path)

    tables = parse_raci_table(content)
    report.raci_tables_found = len(tables)

    if not tables:
        report.results.append(CheckResult(
            name="raci_table_exists",
            passed=True,
            severity="info",
            message="未检测到RACI矩阵表（如文档不包含RACI责任分配可忽略）",
        ))
        report.score = 100
        return report

    for table in tables:
        report.results.extend(check_role_columns(table))
        report.results.extend(check_a_uniqueness(table))
        report.results.extend(check_r_a_separation(table))

    report.score = calculate_score(report)
    return report


def print_file_report(report: FileReport, root_dir: Path, verbose: bool = False) -> None:
    rel_path = quality_report.safe_relative_to(report.file_path, root_dir)
    quality_report.print_scored_report_cli(
        score=report.score,
        header=f"【{rel_path}】{report.score}分（{report.raci_tables_found}个RACI表）",
        extra_lines=[],
        results=report.results,
        verbose=verbose,
    )


def collect_target_files(root_dir: Path, target_file: Optional[Path], target_path: Optional[Path]) -> list[Path]:
    rules = load_rules()

    if target_file and target_file.is_file():
        return [target_file]

    search_dir = target_path if target_path and target_path.is_dir() else root_dir / ".agents"

    files = []
    for md_file in find_markdown_files(search_dir):
        should_skip, _ = rules.should_skip_file(md_file, root_dir=root_dir)
        if should_skip:
            continue
        if "vendor" in str(md_file.relative_to(root_dir)).split("\\")[0:2]:
            continue
        files.append(md_file)

    docs_dir = root_dir / "docs"
    if docs_dir.exists() and (not target_path):
        for md_file in find_markdown_files(docs_dir):
            should_skip, _ = rules.should_skip_file(md_file, root_dir=root_dir)
            if should_skip:
                continue
            files.append(md_file)

    return sorted(set(files))


def main() -> None:
    setup_safe_output()
    parser = argparse.ArgumentParser(description="RACI合规性检查：验证RACI矩阵符合A唯一性/R≠A分离/角色完整性规范")
    add_common_args(parser)
    parser.add_argument("--file", "-f", type=str, help="检查单个文件")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示通过项详情")
    parser.add_argument("--threshold", type=int, default=80, help="评分阈值（低于则退出码1，默认80）")
    args = parser.parse_args()

    root_dir = resolve_project_root(__file__)

    target_file = Path(args.file).resolve() if args.file else None
    target_path = Path(args.path).resolve() if args.path else None

    if target_file and not target_file.exists():
        print_error(f"文件不存在: {target_file}")
        sys.exit(1)

    all_files = collect_target_files(root_dir, target_file, target_path)

    reports = []
    for f in all_files:
        report = check_file(f, root_dir)
        if report.raci_tables_found > 0 or (target_file and f == target_file):
            reports.append(report)

    if not reports:
        msg = "未发现包含RACI矩阵的文档"
        if args.json:
            print(json.dumps({"info": msg, "files": []}, ensure_ascii=False, indent=2))
        else:
            print_warn(msg)
        sys.exit(0)

    if args.json:
        output = quality_report.build_json_output(
            reports,
            root_dir,
            base_dir_key="scan_root",
            base_dir_value=str(target_path or root_dir / ".agents"),
            count_key="file_count",
            items_key="files",
            item_builder=lambda r: {
                "path": str(quality_report.safe_relative_to(r.file_path, root_dir)),
                "raci_tables": r.raci_tables_found,
                **quality_report.common_report_fields(r),
            },
        )
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print_header("RACI 合规性检查")
    print(f"  检查项: A唯一性/R≠A分离/角色列完整性/co-founder审批范围")
    print(f"  发现 {len(reports)} 个含RACI矩阵的文件")

    for report in reports:
        print_file_report(report, root_dir, verbose=args.verbose)

    stats = quality_report.print_aggregate_summary(reports)

    failed = [r for r in reports if r.errors]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
