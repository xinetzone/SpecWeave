"""MDI CLI 入口。

提供 validate 和 gen 子命令。
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import (
    print_pass, print_warn, print_error, print_header, print_summary,
    setup_safe_output,
)
from mdi.validator import MDIValidator, ValidationReport
from mdi.parser import MDIParser
from mdi.generator import MDIGenerator


def _collect_mdi_files(path: Path) -> list[Path]:
    """收集路径下所有MDI文件。"""
    if path.is_file():
        return [path.resolve()]
    files = []
    for md in sorted(path.rglob("SKILL.md")):
        if "SKILL-TEMPLATE" in md.name or "SKILL-TEMPLATE" in str(md):
            continue
        files.append(md.resolve())
    if not files:
        for md in sorted(path.rglob("*.md")):
            if md.name.upper() == "SKILL.MD":
                continue
            if md.name.upper().startswith("README"):
                continue
            try:
                content = md.read_text(encoding="utf-8")[:500]
                if content.startswith("---") and ("name:" in content and "description:" in content):
                    files.append(md.resolve())
            except Exception:
                pass
    return files


def _print_report(report: ValidationReport, verbose: bool = True) -> None:
    """打印单个验证报告。"""
    rel = Path(report.file)
    try:
        rel = rel.relative_to(Path.cwd())
    except ValueError:
        pass

    status = "PASS" if report.passed() else "FAIL"
    score_str = f"{report.score}分"
    print(f"\n  [{status}] {rel}  ({score_str}, profile={report.profile_type})")

    errors = report.errors()
    warnings = report.warnings()
    infos = report.infos()

    for issue in errors:
        line_info = f"L{issue.line} " if issue.line else ""
        print_error(f"{line_info}{issue.code}: {issue.message}")
        if issue.suggestion and verbose:
            print_warn(f"     建议: {issue.suggestion}")

    if verbose:
        for issue in warnings:
            line_info = f"L{issue.line} " if issue.line else ""
            print_warn(f"{line_info}{issue.code}: {issue.message}")

        for issue in infos:
            line_info = f"L{issue.line} " if issue.line else ""
            print(f"     ℹ️ {line_info}{issue.code}: {issue.message}")

    if not errors and not warnings and verbose:
        print_pass("无任何问题")


def cmd_validate(args: argparse.Namespace) -> int:
    """执行validate子命令。"""
    target = Path(args.path).resolve()
    if not target.exists():
        print_error(f"路径不存在: {target}")
        return 1

    validator = MDIValidator(profile_type=args.profile)

    if target.is_file():
        files = [target]
    else:
        files = _collect_mdi_files(target)

    if not files:
        print_error(f"未发现MDI文件: {target}")
        return 1

    reports = [validator.validate_file(f) for f in files]

    if args.score and not args.json:
        for r in reports:
            name = Path(r.file).parent.name if Path(r.file).name.upper() == "SKILL.MD" else Path(r.file).name
            print(f"{name}: {r.score}")
        if len(reports) > 1:
            avg = sum(r.score for r in reports) // len(reports)
            print(f"平均: {avg}")

        failed = [r for r in reports if r.score < args.threshold]
        has_errors = any(not r.passed() for r in reports)
        return 1 if failed or has_errors else 0

    if args.json:
        output = {
            "count": len(reports),
            "allPassed": all(r.passed() for r in reports),
            "avgScore": sum(r.score for r in reports) // len(reports) if reports else 0,
            "reports": [r.to_dict() for r in reports],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    elif not args.score:
        print_header("MDI 规范验证")
        print(f"  目标: {target}")
        print(f"  Profile: {args.profile}")
        print(f"  发现 {len(reports)} 个MDI文件")

        for r in reports:
            _print_report(r, verbose=args.verbose)

        total_errors = sum(len(r.errors()) for r in reports)
        total_warnings = sum(len(r.warnings()) for r in reports)
        total_infos = sum(len(r.infos()) for r in reports)
        print_summary(
            pass_count=len(reports) - sum(1 for r in reports if not r.passed()),
            warn_count=total_warnings,
            error_count=total_errors,
        )
        avg_score = sum(r.score for r in reports) // len(reports) if reports else 0
        print(f"  平均分数: {avg_score}")

    failed = [r for r in reports if r.score < args.threshold]
    has_errors = any(not r.passed() for r in reports)
    return 1 if failed or has_errors else 0


def cmd_gen(args: argparse.Namespace) -> int:
    """执行gen子命令。"""
    target = Path(args.path).resolve()
    output_dir = Path(args.output).resolve()

    if not target.exists():
        print_error(f"路径不存在: {target}")
        return 1

    try:
        generator = MDIGenerator(lang=args.lang, template_dir=args.template_dir)
    except ValueError as e:
        print_error(str(e))
        return 1

    files = _collect_mdi_files(target) if target.is_dir() else [target]

    if not files:
        print_error(f"未发现MDI文件: {target}")
        return 1

    print_header("MDI 代码生成")
    print(f"  目标: {target}")
    print(f"  语言: {args.lang}")
    print(f"  输出: {output_dir}")
    print(f"  发现 {len(files)} 个MDI文件")

    total_generated = 0
    for f in files:
        try:
            generated = generator.generate_file(f, output_dir)
            total_generated += len(generated)
            rel = f
            try:
                rel = f.relative_to(Path.cwd())
            except ValueError:
                pass
            print_pass(f"  {rel} -> 生成 {len(generated)} 个文件")
            for g in generated:
                try:
                    g_rel = g.relative_to(output_dir)
                    print(f"       {g_rel}")
                except ValueError:
                    print(f"       {g}")
        except Exception as e:
            print_error(f"  生成失败 {f}: {e}")
            return 1

    print_summary(
        pass_count=len(files),
        warn_count=0,
        error_count=0,
    )
    print(f"  共生成 {total_generated} 个文件到 {output_dir}")
    return 0


def main() -> None:
    """CLI 主入口。"""
    setup_safe_output()

    parser = argparse.ArgumentParser(
        prog="mdi",
        description="MDI (Markdown Interface) 文档工具",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用子命令")

    validate_parser = subparsers.add_parser("validate", help="验证 MDI 文档")
    validate_parser.add_argument("path", type=Path, help="MDI 文件或目录路径")
    validate_parser.add_argument("--json", action="store_true", help="JSON格式输出")
    validate_parser.add_argument("--score", action="store_true", help="仅输出分数")
    validate_parser.add_argument(
        "--profile", type=str, default="auto",
        choices=["auto", "skill", "webapi", "clitool"],
        help="指定Profile类型（默认auto自动检测）",
    )
    validate_parser.add_argument(
        "--threshold", type=int, default=70,
        help="分数阈值（低于此分数返回非零退出码，默认70）",
    )
    validate_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息（包括info和warning详情）")

    gen_parser = subparsers.add_parser("gen", help="生成代码/文档")
    gen_parser.add_argument("path", type=Path, help="MDI 文件或目录路径")
    gen_parser.add_argument(
        "-l", "--lang", type=str, default="python",
        choices=MDIGenerator.supported_languages(),
        help="目标语言/格式（默认python）",
    )
    gen_parser.add_argument(
        "-t", "--template-dir", type=Path, default=None,
        help="自定义Jinja2模板目录",
    )
    gen_parser.add_argument(
        "-o", "--output", type=Path, help="输出目录", default=Path("./output")
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "validate":
        sys.exit(cmd_validate(args))
    elif args.command == "gen":
        sys.exit(cmd_gen(args))


if __name__ == "__main__":
    main()
