"""Skill Loader CLI - 技能扫描与报告生成命令行工具。

使用 typer 实现，支持增量缓存、严格/宽松验证模式、多种输出格式。
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent.parent.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
if str(_PROJECT_ROOT / ".agents" / "scripts") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / ".agents" / "scripts"))

try:
    import typer
    from typer import Option
    import click
    _HAS_TYPER = True
except ImportError:
    import argparse
    _HAS_TYPER = False

from models import ScanResult
from cache import get_cached_or_parse
from report import generate_json_report, generate_markdown_report

__version__ = "0.1.0"

REPORT_DIR_RELPATH = ".agents/skills/load-flexloop-skills/reports"
DEFAULT_JSON_NAME = "skill-registry.json"
DEFAULT_MD_NAME = "skill-registry.md"


def _detect_project_root() -> Path:
    cwd = Path.cwd().resolve()
    for ancestor in [cwd] + list(cwd.parents):
        if (ancestor / "AGENTS.md").exists():
            return ancestor
    return cwd


def _print_summary(result: ScanResult) -> None:
    stats = result.add_stats()
    print()
    print("=" * 60)
    print("扫描完成")
    print("=" * 60)
    print("  扫描目录:")
    for d in result.scan_dirs:
        print(f"    - {d}")
    print()
    print(f"  技能总数: {stats['total']}")
    print(f"  OK:        {stats['ok']}")
    print(f"  Warning:   {stats['warning']}")
    print(f"  Error:     {stats['error']}")
    print(f"  Conflicts: {stats['conflicts']}")
    print("=" * 60)


def _print_errors_table(result: ScanResult) -> None:
    if not result.errors:
        return
    print()
    print("错误列表:")
    print("-" * 80)
    print(f"  {'文件':<40} {'类型':<20} {'消息':<30}")
    print("-" * 80)
    for err in result.errors:
        file_display = err.file_path
        if len(file_display) > 38:
            file_display = "..." + file_display[-35:]
        type_display = err.error_type[:18]
        msg_display = err.message[:28]
        print(f"  {file_display:<38} {type_display:<20} {msg_display:<30}")
    print("-" * 80)


def _print_conflicts_table(result: ScanResult) -> None:
    if not result.conflicts:
        return
    print()
    print("名称冲突:")
    print("-" * 80)
    for conflict in result.conflicts:
        name = conflict["name"]
        count = conflict["count"]
        files = conflict["files"]
        print(f"  - {name} ({count} 次出现):")
        for f in files:
            print(f"      {f}")
    print("-" * 80)


def _print_generated_files(files: list[Path]) -> None:
    if not files:
        return
    print()
    print("生成的报告文件:")
    for f in files:
        print(f"  - {f}")


def _determine_format(output: Optional[Path], fmt: str) -> str:
    if output is not None:
        suffix = output.suffix.lower()
        if suffix == ".json":
            return "json"
        if suffix in (".md", ".markdown"):
            return "markdown"
    return fmt


def _do_scan(
    project_root: Path,
    extra_dirs: list[str],
    mode: str,
    use_cache: bool,
    output: Optional[Path],
    fmt: str,
    verbose: bool,
) -> int:
    project_root = project_root.resolve()

    if verbose:
        print(f"项目根目录: {project_root}")
        print(f"验证模式: {mode}")
        print(f"使用缓存: {use_cache}")

    result = get_cached_or_parse(
        project_root=project_root,
        extra_dirs=extra_dirs if extra_dirs else None,
        mode=mode,
        use_cache=use_cache,
        verbose=verbose,
    )

    _print_summary(result)

    generated_files: list[Path] = []

    if output is not None:
        output = output.resolve()
        determined_fmt = _determine_format(output, fmt)
        output.parent.mkdir(parents=True, exist_ok=True)
        if determined_fmt == "markdown":
            generate_markdown_report(result, output)
        else:
            generate_json_report(result, output)
        generated_files.append(output)
    else:
        report_dir = (project_root / REPORT_DIR_RELPATH).resolve()
        report_dir.mkdir(parents=True, exist_ok=True)

        effective_fmt = fmt.lower()
        if effective_fmt in ("json", "both"):
            json_path = report_dir / DEFAULT_JSON_NAME
            generate_json_report(result, json_path)
            generated_files.append(json_path)
        if effective_fmt in ("markdown", "md", "both"):
            md_path = report_dir / DEFAULT_MD_NAME
            generate_markdown_report(result, md_path)
            generated_files.append(md_path)

    has_errors = len(result.errors) > 0
    has_conflicts = len(result.conflicts) > 0

    if has_errors:
        _print_errors_table(result)
    if has_conflicts:
        _print_conflicts_table(result)

    _print_generated_files(generated_files)

    if has_errors:
        return 1
    return 0


if _HAS_TYPER:
    app = typer.Typer(
        name="skill-loader",
        help="Skill Loader - 扫描项目中的 SKILL.md 文件，生成技能注册表报告。",
        add_completion=False,
        invoke_without_command=True,
        no_args_is_help=False,
    )

    @app.callback()
    def main(
        ctx: typer.Context,
        project_root: Optional[Path] = Option(
            None,
            "--project-root", "-r",
            help="项目根目录路径（默认自动检测，向上查找包含 AGENTS.md 的目录）",
        ),
        extra_dir: list[str] = Option(
            None,
            "--extra-dir", "-d",
            help="额外扫描目录（相对于 project_root，可多次指定）",
        ),
        mode: str = Option(
            "strict",
            "--mode", "-m",
            help="验证模式：strict（检查推荐章节）或 relaxed（仅检查必填字段）",
            case_sensitive=False,
            click_type=click.Choice(["strict", "relaxed"]),
        ),
        no_cache: bool = Option(
            False,
            "--no-cache",
            help="禁用增量缓存，全量重新扫描",
        ),
        force: bool = Option(
            False,
            "--force", "-f",
            help="强制全量重新扫描（相当于 --no-cache）",
        ),
        output: Optional[Path] = Option(
            None,
            "--output", "-o",
            help="输出文件路径；不指定则同时输出 JSON 和 Markdown 到默认 reports/ 目录",
        ),
        format: str = Option(
            "both",
            "--format", "-fmt",
            help="输出格式：json/markdown/both（当指定 --output 时以文件后缀为准）",
            case_sensitive=False,
            click_type=click.Choice(["json", "markdown", "both"]),
        ),
        verbose: bool = Option(
            False,
            "--verbose", "-v",
            help="打印详细日志",
        ),
        version: bool = Option(
            False,
            "--version",
            help="打印版本号并退出",
            is_eager=True,
        ),
    ) -> None:
        if version:
            print(f"skill-loader {__version__}")
            raise typer.Exit(code=0)

        if ctx.invoked_subcommand is not None:
            return

        root = project_root if project_root is not None else _detect_project_root()
        if not root.exists():
            print(f"错误: 项目根目录不存在: {root}", file=sys.stderr)
            raise typer.Exit(code=2)

        use_cache = not (no_cache or force)
        exit_code = _do_scan(
            project_root=root,
            extra_dirs=extra_dir if extra_dir else [],
            mode=mode,
            use_cache=use_cache,
            output=output,
            fmt=format,
            verbose=verbose,
        )
        raise typer.Exit(code=exit_code)

    def cli_main() -> None:
        app()

else:
    def cli_main() -> None:
        parser = argparse.ArgumentParser(
            prog="skill-loader",
            description="Skill Loader - 扫描项目中的 SKILL.md 文件，生成技能注册表报告。",
        )
        parser.add_argument(
            "--project-root", "-r",
            type=Path,
            default=None,
            help="项目根目录路径（默认自动检测，向上查找包含 AGENTS.md 的目录）",
        )
        parser.add_argument(
            "--extra-dir", "-d",
            action="append",
            default=[],
            help="额外扫描目录（相对于 project_root，可多次指定）",
        )
        parser.add_argument(
            "--mode", "-m",
            choices=["strict", "relaxed"],
            default="strict",
            help="验证模式：strict（检查推荐章节）或 relaxed（仅检查必填字段）",
        )
        parser.add_argument(
            "--no-cache",
            action="store_true",
            default=False,
            help="禁用增量缓存，全量重新扫描",
        )
        parser.add_argument(
            "--force", "-f",
            action="store_true",
            default=False,
            help="强制全量重新扫描（相当于 --no-cache）",
        )
        parser.add_argument(
            "--output", "-o",
            type=Path,
            default=None,
            help="输出文件路径；不指定则同时输出 JSON 和 Markdown 到默认 reports/ 目录",
        )
        parser.add_argument(
            "--format", "-fmt",
            choices=["json", "markdown", "both"],
            default="both",
            help="输出格式：json/markdown/both（当指定 --output 时以文件后缀为准）",
        )
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            default=False,
            help="打印详细日志",
        )
        parser.add_argument(
            "--version",
            action="store_true",
            default=False,
            help="打印版本号并退出",
        )

        args = parser.parse_args()

        if args.version:
            print(f"skill-loader {__version__}")
            sys.exit(0)

        root = args.project_root if args.project_root is not None else _detect_project_root()
        if not root.exists():
            print(f"错误: 项目根目录不存在: {root}", file=sys.stderr)
            sys.exit(2)

        use_cache = not (args.no_cache or args.force)
        exit_code = _do_scan(
            project_root=root,
            extra_dirs=args.extra_dir,
            mode=args.mode,
            use_cache=use_cache,
            output=args.output,
            fmt=args.format,
            verbose=args.verbose,
        )
        sys.exit(exit_code)


if __name__ == "__main__":
    cli_main()
