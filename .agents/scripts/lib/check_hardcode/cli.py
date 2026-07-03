import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from lib.project import resolve_project_root
from lib.cli import print_warn, print_header, print_summary, add_common_args, setup_safe_output
from lib.rules import load_rules
import lib.quality_report as quality_report

from .scanner import scan_python_file, collect_python_files


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
