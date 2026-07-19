"""模式成熟度工具 - 各子命令检查逻辑。"""

import json
import re
from datetime import date
from pathlib import Path

from lib.cli import print_error, print_header, print_pass, print_summary, print_warn
from lib.project import resolve_project_root

from .constants import (
    EXCLUDED_FILENAMES,
    PATTERN_DOMAINS,
    PATTERNS_DIR,
)
from .readme_ops import (
    check_stats_consistency,
    parse_readme_index_table,
    update_readme_index_table,
)
from .scanner import grep_maturity_per_directory, scan_patterns
from .reporter import (
    print_all_summary,
    print_markdown_report,
    print_text_report,
    print_upgrade_json,
    print_upgrade_report,
)
from .scoring import count_patterns_in_directory, generate_report_data, calculate_upgrade_stats


def cmd_stats(args):
    """stats 子命令：成熟度分布统计。"""
    root_dir = resolve_project_root(__file__)
    base_dir = args.base_dir if hasattr(args, 'base_dir') and args.base_dir else str(root_dir / PATTERNS_DIR)

    if args.path:
        base_dir = str(args.path)

    base_path = Path(base_dir)
    if not base_path.is_dir():
        if not base_path.is_absolute():
            base_path = root_dir / base_dir
        if not base_path.is_dir():
            print_error(f"目录 '{base_dir}' 不存在")
            return 1

    patterns, issues = scan_patterns(str(base_path))
    if not patterns:
        print_warn('未找到模式文件')
        return 1 if getattr(args, 'check', False) else 0

    data = generate_report_data(patterns, issues)

    fmt = getattr(args, 'format', 'text')
    if fmt == 'json' or args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif fmt == 'markdown':
        print_markdown_report(data)
    else:
        print_text_report(data)

    if getattr(args, 'check', False) and issues:
        return 1

    return 0


def cmd_scan_upgrades(args):
    """scan-upgrades 子命令：成熟度偏差扫描。"""
    root_dir = resolve_project_root(__file__)
    patterns_dir = root_dir / PATTERNS_DIR

    if args.path:
        patterns_dir = args.path

    if not patterns_dir.exists():
        print_error(f"模式目录不存在: {patterns_dir}")
        return 1

    patterns, _ = scan_patterns(str(patterns_dir))
    stats = calculate_upgrade_stats(patterns)

    if args.json:
        print_upgrade_json(patterns, stats)
    elif args.all:
        print_all_summary(patterns, stats)
    else:
        print_upgrade_report(patterns, stats)

    return 0


def cmd_verify(args):
    """verify 子命令：README 统计表一致性验证。"""
    root_dir = resolve_project_root(__file__)
    patterns_root = root_dir / PATTERNS_DIR
    readme_path = patterns_root / 'README.md'

    if not readme_path.exists():
        print_error(f"README 不存在: {readme_path}")
        return 1

    print_header('成熟度统计一致性验证')
    discrepancies = check_stats_consistency(patterns_root, readme_path)

    if not discrepancies:
        print_pass('通过 — grep 成熟度分布与 README 统计表完全一致')
        grep_stats = grep_maturity_per_directory(patterns_root)
        total_all = {'L1': 0, 'L2': 0, 'L3': 0, 'L4': 0, '_total': 0}
        for dir_name, data in grep_stats.items():
            if dir_name == '合计':
                continue
            print(f"  {dir_name}: L1={data['L1']} L2={data['L2']} L3={data['L3']} L4={data['L4']} (共 {data['_total']} 模式)")
            for k in total_all:
                total_all[k] += data.get(k, 0)
        print(f"  合计: L1={total_all['L1']} L2={total_all['L2']} L3={total_all['L3']} L4={total_all['L4']} (共 {total_all['_total']} 模式)")
        return 0

    print_warn(f"发现 {len(discrepancies)} 处统计偏差:")
    for i, d in enumerate(discrepancies, 1):
        direction = '+' if d['diff'] > 0 else ''
        print(f"  [{i}] {d['directory']} {d['field']}: grep={d['grep']} README={d['readme']} (偏差 {direction}{d['diff']})")

    print(f"\n  建议：更新 patterns/README.md 统计表，或将 grep 结果同步到报告。")
    return 1


def _update_date_readme(readme_path: Path, content: str) -> str:
    """更新 patterns/README.md 中的统计日期行。"""
    old_date_pattern = r"注：统计数据截至 \d{4}-\d{2}-\d{2}.*"
    new_date = f"> 注：统计数据截至 {date.today().isoformat()}，由 pattern-maturity.py check-index --fix 自动更新。"
    content = re.sub(old_date_pattern, new_date, content)
    return content


def cmd_check_index(args):
    """check-index 子命令：patterns/ 索引一致性检查与修复。"""
    root_dir = resolve_project_root(__file__)
    patterns_dir = root_dir / PATTERNS_DIR
    readme_path = patterns_dir / 'README.md'

    if not patterns_dir.exists():
        print_error(f"目录不存在: {patterns_dir}")
        return 1
    if not readme_path.exists():
        print_error(f"统计表不存在: {readme_path}")
        return 1

    dirs_to_check = [d + '/' for d in PATTERN_DOMAINS]
    actual_counts = {}
    for d in dirs_to_check:
        actual_counts[d] = count_patterns_in_directory(patterns_dir / d)

    declared_stats = parse_readme_index_table(readme_path)

    discrepancies = []
    for d in dirs_to_check:
        actual = actual_counts.get(d, 0)
        declared = declared_stats.get(d, {}).get('patterns', 0)
        if actual != declared:
            discrepancies.append((d, declared, actual))

    if args.verbose:
        for d in dirs_to_check:
            dir_path = patterns_dir / d
            files = sorted([f.name for f in dir_path.glob('*.md') if f.name not in EXCLUDED_FILENAMES])
            print(f"\n{d} ({len(files)} 个模式):")
            for f in files:
                print(f"  - {f}")

    print('\n' + '=' * 60)
    print('retrospective/patterns/ Index Consistency Check')
    print('=' * 60)

    for d in dirs_to_check:
        actual = actual_counts.get(d, 0)
        declared = declared_stats.get(d, {}).get('patterns', 0)
        status = 'OK' if actual == declared else 'MISMATCH'
        print(f"  {d:30s}  declared={declared:>3}  actual={actual:>3}  {status}")

    declared_total = sum(v.get('patterns', 0) for v in declared_stats.values())
    actual_total = sum(actual_counts.values())
    total_status = 'OK' if declared_total == actual_total else 'MISMATCH'
    print(f"  {'TOTAL':30s}  declared={declared_total:>3}  actual={actual_total:>3}  {total_status}")
    print()

    if not discrepancies:
        print('OK - stats consistent, no update needed.')
        print('=' * 60)
        return 0

    print(f"Found {len(discrepancies)} discrepancies:")
    for d, declared, actual in discrepancies:
        print(f"  - {d}: declared {declared}, actual {actual}")

    if not args.fix:
        print('\n使用 --fix 自动更新 patterns/README.md 统计表。')
        print('=' * 60)
        return 1

    print('\nUpdating patterns/README.md ...')
    new_content = update_readme_index_table(readme_path, declared_stats, actual_counts)
    new_content = _update_date_readme(readme_path, new_content)
    readme_path.write_text(new_content, encoding='utf-8')
    print('OK - patterns/README.md stats table updated.')
    print('=' * 60)
    return 0


def cmd_check(args):
    """check 子命令：CI 检查模式，运行结构性验证。"""
    root_dir = resolve_project_root(__file__)
    patterns_dir = root_dir / PATTERNS_DIR

    if args.path:
        patterns_dir = args.path

    if not patterns_dir.exists():
        print_error(f"模式目录不存在: {patterns_dir}")
        return 1

    patterns, issues = scan_patterns(str(patterns_dir))

    print_header('模式库 CI 结构检查')
    print(f"  扫描目录: {patterns_dir}")
    print(f"  发现模式: {len(patterns)} 个")
    print()

    if issues:
        error_count = 0
        warn_count = 0
        for issue in issues:
            if issue['type'] in ('missing_directory', 'missing_frontmatter'):
                print_error(f"{issue['path']}: {issue['message']}")
                error_count += 1
            else:
                print_warn(f"{issue['path']}: {issue['message']}")
                warn_count += 1
        print()
        print_summary(len(patterns) - error_count - warn_count, warn_count, error_count)
        return 1 if error_count > 0 else 0

    print_pass(f'所有 {len(patterns)} 个模式文件结构完整')
    print_summary(len(patterns), 0, 0)
    return 0
