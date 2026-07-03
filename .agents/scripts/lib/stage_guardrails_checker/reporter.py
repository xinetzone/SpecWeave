import json

from lib.cli import print_pass, print_warn, print_error, print_header, print_summary

from .models import AnalysisIssue
from .parser import parse_log_file
from .analyzer import analyze


def run_analysis(content: str, json_output: bool = False, strict: bool = False) -> int:
    entries, parse_issues = parse_log_file(content)
    analysis_issues = analyze(entries)
    all_issues = parse_issues + analysis_issues

    error_count = sum(1 for i in all_issues if i.severity == 'ERROR')
    warn_count = sum(1 for i in all_issues if i.severity == 'WARN')
    pass_count = max(0, len(entries) - error_count - warn_count)

    if json_output:
        result = {
            "summary": {
                "strict": strict,
                "total_log_entries": len(entries),
                "sg_entries": sum(1 for e in entries if e.is_sg),
                "pdr_entries": sum(1 for e in entries if e.is_pdr),
                "errors": error_count,
                "warnings": warn_count,
                "passed": pass_count,
            },
            "issues": [
                {
                    "severity": i.severity,
                    "code": i.code,
                    "message": i.message,
                    "line": i.line_num,
                    "stage": i.entry.stage if i.entry else None,
                    "event": i.entry.event if i.entry else None,
                }
                for i in all_issues
            ],
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if (error_count > 0 or (strict and warn_count > 0)) else 0

    header_title = "阶段守卫日志分析 [STRICT MODE]" if strict else "阶段守卫日志分析"
    print_header(header_title)
    print(f"  日志条目总数: {len(entries)} (SG: {sum(1 for e in entries if e.is_sg)}, PDR: {sum(1 for e in entries if e.is_pdr)})")
    if strict:
        print(f"  严格模式: WARN级别异常将导致非零退出码")

    if not all_issues:
        print_pass("未发现任何异常，阶段守卫执行记录完整合规")
    else:
        for issue in all_issues:
            if issue.severity == 'ERROR':
                detail = f" (line {issue.line_num})" if issue.line_num else ""
                print_error(f"[{issue.code}] {issue.message}{detail}")
            else:
                detail = f" (line {issue.line_num})" if issue.line_num else ""
                print_warn(f"[{issue.code}] {issue.message}{detail}")

    print_summary(pass_count=pass_count, warn_count=warn_count, error_count=error_count)
    return 1 if (error_count > 0 or (strict and warn_count > 0)) else 0