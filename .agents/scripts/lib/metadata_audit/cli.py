import argparse
import sys
from pathlib import Path

from lib.project import resolve_project_root

from .auditor import audit
from .reporter import format_json_report, format_text_report


def main(argv=None):
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description='元数据生态健康度审计工具')
    parser.add_argument('--dir', help='目标目录（默认全项目）')
    parser.add_argument('--file', help='单个文件路径')
    parser.add_argument('--fix', action='store_true', help='自动创建缺失TOML骨架并补全id')
    parser.add_argument('--strict', action='store_true', help='严格模式：警告视为错误')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')
    parser.add_argument('--report', help='报告输出文件路径')
    parser.add_argument('--exclude', action='append', default=[], help='排除目录名（可多次指定）')
    args = parser.parse_args(argv)

    project_root = resolve_project_root(__file__)
    exclude_dirs = {'vendor', '.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', '.trae'}
    exclude_dirs.update(args.exclude)

    target_dir = Path(args.dir).resolve() if args.dir else project_root
    single_file = None

    if args.file:
        single_file = Path(args.file).resolve()
        target_dir = single_file.parent

    result = audit(project_root, target_dir, exclude_dirs, fix=args.fix, single_file=single_file)

    if args.format == 'json':
        output = format_json_report(result, project_root)
    else:
        output = format_text_report(result, project_root)

    print(output)

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(output, encoding='utf-8')
        print(f'\n报告已保存到: {report_path}')

    exit_code = 1 if result.errors or (args.strict and result.warnings) else 0
    sys.exit(exit_code)
