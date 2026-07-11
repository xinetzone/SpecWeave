#!/usr/bin/env python3
"""Mermaid 全量扫描工具：定期扫描 docs 目录下所有 Markdown 文件的 Mermaid 语法。

相比 check-mermaid.py：
- 默认扫描 docs/ 目录（而非整个项目根）
- 可生成 Markdown 格式的扫描报告
- 支持 --fix 自动修复
- 输出按文件分组的结构化摘要，便于定期审查

用法:
  python mermaid-full-scan.py [--path DOCS_DIR] [--fix] [--report REPORT.md]
                               [--dry-run] [--json]

典型场景:
  # 扫描 docs 目录，输出终端报告
  python mermaid-full-scan.py

  # 扫描并自动修复可修复问题
  python mermaid-full-scan.py --fix

  # 生成 Markdown 报告文件
  python mermaid-full-scan.py --report docs/quality/mermaid-scan-report.md

  # 预览修复效果（不写入文件）
  python mermaid-full-scan.py --fix --dry-run
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import print_pass, print_error, print_warn, print_summary
from lib.checks import mermaid as mermaid_checker


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def run_scan(scan_root: Path, project_root: Path, fix: bool = False,
             dry_run: bool = False) -> dict:
    class Args:
        pass

    args = Args()
    args.path = str(scan_root)
    args.fix = fix
    args.dry_run = dry_run
    args.exclude = []
    args.debug = False

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    import io
    buf = io.StringIO()
    sys.stdout = buf
    sys.stderr = buf

    try:
        exit_code = mermaid_checker.run(project_root, args)
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    console_output = buf.getvalue()

    md_files = mermaid_checker._find_md_files(scan_root, set())
    total_diagrams = 0
    files_with_issues = []
    all_errors = []
    all_warnings = []
    total_fixes = 0

    for md in sorted(md_files):
        issues, fixes, _ = mermaid_checker._process_file(
            md, project_root, fix=fix, dry_run=dry_run
        )
        rel_path = _rel(md, project_root)
        content = md.read_text(encoding="utf-8")
        diagram_count = len(mermaid_checker.MERMAID_FENCE_RE.findall(content))
        total_diagrams += diagram_count

        if issues:
            errs = [i for i in issues if i[1] == "error"]
            warns = [i for i in issues if i[1] == "warning"]
            all_errors.extend([(rel_path, ln, msg) for ln, lvl, msg in errs])
            all_warnings.extend([(rel_path, ln, msg) for ln, lvl, msg in warns])
            if fixes:
                total_fixes += fixes
            files_with_issues.append({
                "file": rel_path,
                "diagrams": diagram_count,
                "errors": len(errs),
                "warnings": len(warns),
                "fixes_applied": fixes if fix and not dry_run else 0,
                "issues": [
                    {"line": ln, "level": lvl, "message": msg}
                    for ln, lvl, msg in sorted(issues, key=lambda x: x[0])
                ],
            })

    return {
        "scan_root": str(scan_root),
        "project_root": str(project_root),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "total_files": len(md_files),
        "total_diagrams": total_diagrams,
        "files_with_issues": len(files_with_issues),
        "total_errors": len(all_errors),
        "total_warnings": len(all_warnings),
        "total_fixes": total_fixes if fix else 0,
        "fix_mode": "dry-run" if dry_run else ("fix" if fix else "check"),
        "files_detail": files_with_issues,
        "errors_detail": [
            {"file": f, "line": ln, "message": msg} for f, ln, msg in all_errors
        ],
        "warnings_detail": [
            {"file": f, "line": ln, "message": msg} for f, ln, msg in all_warnings
        ],
    }


def generate_report(result: dict) -> str:
    ts = result["timestamp"]
    lines = [
        "---",
        f'title: "Mermaid 语法全量扫描报告"',
        f'date: "{ts[:10]}"',
        "category: quality",
        "---",
        "",
        f"# Mermaid 语法全量扫描报告",
        "",
        f"> 扫描时间：{ts}",
        f"> 扫描目录：`{result['scan_root']}`",
        f"> 扫描模式：{result['fix_mode']}",
        "",
        "## 摘要",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| 扫描文件数 | {result['total_files']} |",
        f"| Mermaid 图总数 | {result['total_diagrams']} |",
        f"| 有问题的文件 | {result['files_with_issues']} |",
        f"| 错误数 | {result['total_errors']} |",
        f"| 警告数 | {result['total_warnings']} |",
    ]
    if result["fix_mode"] in ("fix", "dry-run"):
        lines.append(f"| 自动修复块数 | {result['total_fixes']} |")
    lines.append("")

    if result["total_errors"] == 0 and result["total_warnings"] == 0:
        lines.append("**结果：所有 Mermaid 图语法正常，无问题发现。**")
        lines.append("")
        return "\n".join(lines)

    if result["errors_detail"]:
        lines.append("## 错误列表")
        lines.append("")
        for err in result["errors_detail"]:
            lines.append(f"- **{err['file']}**:L{err['line']} — {err['message']}")
        lines.append("")

    if result["warnings_detail"]:
        lines.append("## 警告列表")
        lines.append("")
        for warn in result["warnings_detail"]:
            lines.append(f"- **{warn['file']}**:L{warn['line']} — {warn['message']}")
        lines.append("")

    if result["files_detail"]:
        lines.append("## 按文件详情")
        lines.append("")
        for f in result["files_detail"]:
            icon = "🔴" if f["errors"] > 0 else "🟡"
            lines.append(f"### {icon} {f['file']}")
            lines.append("")
            lines.append(f"- Mermaid 图：{f['diagrams']} 个")
            lines.append(f"- 错误：{f['errors']}，警告：{f['warnings']}")
            if f["fixes_applied"]:
                lines.append(f"- 已自动修复：{f['fixes_applied']} 个代码块")
            lines.append("")
            for issue in f["issues"]:
                lvl_icon = "❌" if issue["level"] == "error" else "⚠️"
                lines.append(f"  - {lvl_icon} L{issue['line']}: {issue['message']}")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*本报告由 `mermaid-full-scan.py` 自动生成。*")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Mermaid 全量扫描：定期检查 docs/ 目录下所有 Mermaid 图语法"
    )
    parser.add_argument("--path", type=Path, default=None,
                        help="扫描目录（默认: <project_root>/docs）")
    parser.add_argument("--fix", action="store_true",
                        help="自动修复可修复的问题（引号、空行等）")
    parser.add_argument("--dry-run", action="store_true",
                        help="预览修复效果但不写入文件")
    parser.add_argument("--report", type=Path, default=None,
                        help="生成 Markdown 格式扫描报告到指定路径")
    parser.add_argument("--json", action="store_true",
                        help="以 JSON 格式输出结果到 stdout")
    parser.add_argument("--exclude", nargs="*", default=[],
                        help="排除的目录名列表")

    args = parser.parse_args()
    os.environ["PYTHONIOENCODING"] = "utf-8"

    project_root = Path(__file__).resolve().parent.parent.parent
    scan_root = args.path.resolve() if args.path else (project_root / "docs")

    if not scan_root.is_dir():
        print_error(f"扫描目录不存在: {scan_root}")
        return 1

    result = run_scan(
        scan_root=scan_root,
        project_root=project_root,
        fix=args.fix,
        dry_run=args.dry_run,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("Mermaid 全量扫描结果")
        print("=" * 60)
        print(f"  扫描目录: {scan_root}")
        print(f"  扫描文件: {result['total_files']}")
        print(f"  Mermaid 图: {result['total_diagrams']}")
        print(f"  问题文件: {result['files_with_issues']}")
        print()

        if result["total_errors"] == 0 and result["total_warnings"] == 0:
            print_pass("所有 Mermaid 图语法正常，无问题")
        else:
            for f in result["files_detail"]:
                icon = "X" if f["errors"] > 0 else "!"
                print(f"  [{icon}] {f['file']}: {f['errors']} 错误, {f['warnings']} 警告")
                for issue in f["issues"]:
                    lvl = "ERROR" if issue["level"] == "error" else "WARN"
                    print(f"      L{issue['line']} [{lvl}] {issue['message']}")
            print()
            print_summary(
                pass_count=result["total_files"] - result["files_with_issues"],
                warn_count=result["total_warnings"],
                error_count=result["total_errors"],
            )

    if args.report:
        report_path = args.report.resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_md = generate_report(result)
        report_path.write_text(report_md, encoding="utf-8")
        print_pass(f"扫描报告已保存: {report_path}")

    return 1 if result["total_errors"] > 0 and not args.fix else 0


if __name__ == "__main__":
    sys.exit(main())
