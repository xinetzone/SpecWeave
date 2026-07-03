"""模式成熟度工具 - CLI 主入口。"""

import argparse
import sys

from lib.cli import add_common_args, setup_safe_output

from .checks import cmd_check, cmd_check_index, cmd_scan_upgrades, cmd_stats, cmd_verify


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        description='模式成熟度统一工具：统计、偏差扫描、README 验证、索引检查',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
子命令:
  stats          成熟度分布统计报告
  scan-upgrades  成熟度偏差扫描（待升级/异常模式）
  verify         README 统计表一致性验证
  check-index    patterns/ 索引一致性检查与修复
  check          CI 检查模式（结构性验证）

示例:
  pattern-maturity.py stats
  pattern-maturity.py stats --format markdown
  pattern-maturity.py scan-upgrades --all
  pattern-maturity.py scan-upgrades --json
  pattern-maturity.py verify
  pattern-maturity.py check-index
  pattern-maturity.py check-index --fix
  pattern-maturity.py check
        """,
    )
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    stats_parser = subparsers.add_parser('stats', help='成熟度分布统计报告')
    stats_parser.add_argument('base_dir', nargs='?', default=None, help='模式文件基础目录（默认 docs/retrospective/patterns）')
    stats_parser.add_argument('--format', choices=['text', 'json', 'markdown'], default='text', help='输出格式')
    stats_parser.add_argument('--check', action='store_true', help='CI 检查模式：存在结构问题时返回非 0')
    add_common_args(stats_parser)

    upgrade_parser = subparsers.add_parser('scan-upgrades', help='成熟度偏差扫描')
    upgrade_parser.add_argument('--all', '-a', action='store_true', help='输出所有模式的状态一览（按类别分组）')
    add_common_args(upgrade_parser)

    verify_parser = subparsers.add_parser('verify', help='README 统计表一致性验证')
    add_common_args(verify_parser)

    index_parser = subparsers.add_parser('check-index', help='patterns/ 索引一致性检查与修复')
    index_parser.add_argument('--fix', action='store_true', help='自动更新 patterns/README.md 统计表')
    index_parser.add_argument('--verbose', '-v', action='store_true', help='详细模式：列出每个子目录的文件')
    add_common_args(index_parser)

    check_parser = subparsers.add_parser('check', help='CI 检查模式（结构性验证）')
    add_common_args(check_parser)

    return parser


def main(argv=None) -> int:
    """主入口函数。"""
    setup_safe_output()
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        'stats': cmd_stats,
        'scan-upgrades': cmd_scan_upgrades,
        'verify': cmd_verify,
        'check-index': cmd_check_index,
        'check': cmd_check,
    }

    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
