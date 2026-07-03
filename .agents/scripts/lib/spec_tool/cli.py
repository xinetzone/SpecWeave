import argparse
from pathlib import Path

from constants import SPEC_MATCH_THRESHOLD
from lib.cli import setup_safe_output

from .check_cmd import cmd_check
from .format_cmd import cmd_format
from .test_gen import cmd_gen_tests


def add_common_args(sp):
    sp.add_argument('--path', type=Path, default=None, help='项目根目录路径（默认自动解析）')
    sp.add_argument('--json', action='store_true', default=False, help='以 JSON 格式输出结果')


def main():
    setup_safe_output()
    parser = argparse.ArgumentParser(description='Spec 文档工具集')
    subparsers = parser.add_subparsers(dest='command', help='可用子命令')

    p_check = subparsers.add_parser('check', help='规格文档一致性检查')
    add_common_args(p_check)
    p_check.add_argument('--spec-dir', type=str, default=None, help='指定要检查的 spec 目录')
    p_check.add_argument('--all', action='store_true', default=False, help='扫描所有 spec 目录（默认行为）')
    p_check.add_argument('--match-threshold', type=int, default=SPEC_MATCH_THRESHOLD, help='语义匹配最少共同关键词数')

    p_fmt = subparsers.add_parser('format', help='Spec 文档标准化格式检查')
    add_common_args(p_fmt)
    p_fmt.add_argument('--spec-dir', type=str, default='.trae/specs/', help='spec 基目录（默认: .trae/specs/）')
    p_fmt.add_argument('--check-all', action='store_true', help='递归检查所有子目录')
    p_fmt.add_argument('--format', choices=['text', 'json', 'yaml'], default='text', help='输出格式（默认: text）')
    p_fmt.add_argument('--verbose', '-v', action='store_true', help='显示详细输出')

    p_gt = subparsers.add_parser('gen-tests', help='从 spec.md 生成 pytest 测试骨架')
    add_common_args(p_gt)
    g = p_gt.add_mutually_exclusive_group()
    g.add_argument('--spec', type=str, help='单个 spec 目录路径')
    g.add_argument('--all', action='store_true', help='扫描所有 spec 目录')
    p_gt.add_argument('--output', type=str, default=None, help='输出文件路径（单文件模式）')
    p_gt.add_argument('--output-dir', type=str, default=None, help='输出目录（--all 模式）')
    p_gt.add_argument('--dry-run', action='store_true', help='仅打印生成内容，不写入文件')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1

    cmd_map = {'check': cmd_check, 'format': cmd_format, 'gen-tests': cmd_gen_tests}
    return cmd_map[args.command](args)
