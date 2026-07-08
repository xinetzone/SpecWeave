"""并发安全检查 CLI 入口模块。"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from lib.project import resolve_project_root
from lib.cli import print_warn, print_header, print_summary, add_common_args, setup_safe_output
from lib.rules import load_rules
import lib.quality_report as quality_report

from .scanner import scan_python_file, collect_python_files
from .constants import DIMENSIONS


def main() -> None:
    setup_safe_output()
    parser = argparse.ArgumentParser(
        description="并发模块安全检查：八维检查法（超时/幂等/边界/防御/配置/国际化/死锁顺序/资源泄漏）"
    )
    add_common_args(parser)
    parser.add_argument("--file", "-f", type=str, help="检查单个Python文件")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")
    parser.add_argument("--threshold", type=int, default=70, help="评分阈值（默认70）")
    parser.add_argument("--dimension", "-d", type=str, choices=list(DIMENSIONS.keys()),
                        help="仅检查指定维度（TIMEOUT/IDEMPOTENT/BOUNDARY/DEFENSIVE/CONFIG/I18N/DEADLOCK/LEAK）")
    parser.add_argument("--fail-on-error", action="store_true", default=True,
                        help="有error级问题时返回非零退出码（默认开启）")
    parser.add_argument("--fail-on-warn", action="store_true",
                        help="有warn级问题时也返回非零退出码（CI严格模式）")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger(__name__)
    logger.debug("日志级别设置为: %s", "DEBUG" if args.verbose else "WARNING")

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

    if args.dimension:
        dim_code = DIMENSIONS[args.dimension]["code"]
        for r in reports:
            r.issues = [i for i in r.issues if i.code == dim_code or i.code == "CC-PARSE"]
        dim_label = DIMENSIONS[args.dimension]["name"]
    else:
        dim_label = "全部维度"

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
                "score": r.score,
                "issue_count": len(r.issues),
                "issues": [
                    {
                        "dimension": i.dimension,
                        "dimension_name": i.dimension_name,
                        "code": i.code,
                        "severity": i.severity,
                        "message": i.message,
                        "line": i.line,
                    }
                    for i in r.issues
                ],
                **quality_report.common_report_fields(r),
            },
        )
        output["dimension_filter"] = args.dimension or "ALL"
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print_header("并发模块安全检查（八维检查法）")
    print(f"  维度: {dim_label}")
    dim_str = " | ".join(
        f"{DIMENSIONS[k]['code']}={DIMENSIONS[k]['name']}" for k in DIMENSIONS
    )
    print(f"  代码: {dim_str}")
    print(f"  发现 {len(reports)} 个Python文件")
    print()

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
                name="concurrent_safety_scan",
                passed=True,
                severity="info",
                message=f"扫描{report.lines_scanned}行，未发现并发安全问题",
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
    total_infos = sum(len(r.infos) for r in reports)
    print(f"  信息: {total_infos} | 警告: {total_warns} | 错误: {total_errors}")
    print_summary(
        pass_count=sum(1 for r in reports if r.score >= args.threshold),
        warn_count=total_warns,
        error_count=total_errors,
    )

    if args.fail_on_warn:
        sys.exit(1 if (total_errors > 0 or total_warns > 0) else 0)
    sys.exit(1 if total_errors > 0 else 0)
