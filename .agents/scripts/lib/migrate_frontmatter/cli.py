import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from ..cli import (
    print_error,
    print_header,
    print_pass,
    print_summary,
    print_warn,
    setup_safe_output,
)
from ..atomic_write import atomic_write_json
from .constants import PROJECT_ROOT
from .converter import (
    batch_convert,
    compute_toml_ref_path,
    rollback,
    verify_consistency,
)
from .models import Report
from .scanner import scan_files

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """配置日志输出格式和级别。

    Args:
        verbose: 是否启用 DEBUG 级别日志。
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


def build_arg_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。

    Returns:
        配置好的 argparse.ArgumentParser 实例。
    """
    parser = argparse.ArgumentParser(
        description="批量迁移 TOML frontmatter 文件为 YAML+x-toml-ref 格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python .agents/scripts/migrate-frontmatter.py --dry-run
  python .agents/scripts/migrate-frontmatter.py --backup --verify
  python .agents/scripts/migrate-frontmatter.py --rollback
  python .agents/scripts/migrate-frontmatter.py --path docs/knowledge --report report.json
        """,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览模式：只打印计划变更，不写入任何文件",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="转换前备份原文件到 .meta/backup/ 目录",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="转换后自动验证与基线清单的一致性",
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="从 .meta/backup/ 恢复原始文件并清理外部 TOML",
    )
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="只转换指定目录下的文件（默认整个项目）",
    )
    parser.add_argument(
        "--report",
        type=str,
        default=None,
        help="输出 JSON 迁移报告到指定路径",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="启用 DEBUG 级别日志输出",
    )
    return parser


def _write_report(report: Report, report_path: str) -> None:
    """将报告写入 JSON 文件。

    Args:
        report: 报告数据字典。
        report_path: 输出文件路径。
    """
    path = Path(report_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(path, report, ensure_ascii=False, indent=2)
    logger.info("报告已写入: %s", path)


def main() -> int:
    """脚本主入口。

    Returns:
        进程退出码（0 表示成功，非 0 表示有错误）。
    """
    setup_safe_output()
    parser = build_arg_parser()
    args = parser.parse_args()
    setup_logging(verbose=args.verbose)

    root = PROJECT_ROOT
    if args.path:
        scan_root = (root / args.path).resolve()
        if not scan_root.exists():
            print_error(f"指定路径不存在: {scan_root}")
            return 1
    else:
        scan_root = root

    report: Report = {
        "timestamp": datetime.now().isoformat(),
        "mode": [],
        "scan_path": str(scan_root),
    }

    if args.rollback:
        print_header("回滚模式：从备份恢复原始文件")
        report["mode"].append("rollback")
        rb_result = rollback(root)
        report["rollback"] = rb_result

        for item in rb_result["restored"]:
            print_pass(f"已恢复: {item['path']}")
        for item in rb_result["failed"]:
            print_error(f"恢复失败: {item['path']} - {item.get('reason', 'unknown')}")

        print_summary(
            len(rb_result["restored"]),
            0,
            len(rb_result["failed"]),
        )

        if args.report:
            _write_report(report, args.report)
        return 0 if not rb_result["failed"] else 1

    print_header("TOML → YAML+x-toml-ref 批量迁移")
    if args.dry_run:
        report["mode"].append("dry-run")
        print("(dry-run 模式：不会修改任何文件)\n")
    if args.backup:
        report["mode"].append("backup")
    if args.verify:
        report["mode"].append("verify")

    print(f"扫描目录: {scan_root}")
    files = scan_files(scan_root)
    print(f"发现 {len(files)} 个 TOML frontmatter 文件\n")

    if not files:
        print("没有需要迁移的文件")
        report["conversion"] = {"total": 0, "success": 0, "failed": 0, "skipped": 0}
        if args.report:
            _write_report(report, args.report)
        return 0

    if args.dry_run:
        for i, f in enumerate(files, 1):
            rel = str(f.relative_to(root)).replace("\\", "/")
            toml_ref = compute_toml_ref_path(rel)
            print(f"  [{i}] {rel}")
            print(f"      → toml_ref: {toml_ref}")

    result = batch_convert(files, root, dry_run=args.dry_run, backup=args.backup)
    report["conversion"] = {
        "total": result["total"],
        "success": len(result["success"]),
        "failed": len(result["failed"]),
        "skipped": len(result["skipped"]),
        "details": result,
    }

    for item in result["success"]:
        print_pass(f"{'计划' if args.dry_run else '转换'}: {item['path']}")
    for item in result["skipped"]:
        print_warn(f"跳过: {item['path']} ({item.get('reason', '')})")
    for item in result["failed"]:
        print_error(f"失败: {item['path']} - {item.get('error', 'unknown')}")

    print_summary(
        len(result["success"]),
        len(result["skipped"]),
        len(result["failed"]),
    )

    if args.verify and not args.dry_run:
        print_header("一致性验证")
        verification = verify_consistency(root)
        report["verification"] = verification

        for item in verification["passed"]:
            print_pass(f"验证通过: {item['path']}")
        for item in verification["failed"]:
            print_error(f"验证失败: {item['path']} - {item.get('reason', '')}")
        for err in verification["errors"]:
            print_error(f"错误: {err}")

        print_summary(
            len(verification["passed"]),
            0,
            len(verification["failed"]) + len(verification["errors"]),
        )

    if args.report:
        _write_report(report, args.report)

    if result["failed"]:
        return 1
    return 0
