#!/usr/bin/env python3
"""模式成熟度统一工具。

聚合模式成熟度相关的五个功能：
  stats        - 成熟度分布统计报告
  scan-upgrades - 成熟度偏差扫描（识别待升级/异常模式）
  verify       - README 统计表一致性验证
  check-index  - patterns/ 索引一致性检查与修复
  check        - CI 检查模式（结构性验证）

合并自：pattern-maturity-stats.py、scan-maturity-upgrades.py、
       check-atomization-duplication.py --verify-stats、
       check-retrospective-index.py（patterns 索引部分）。
"""

import argparse
import json
import re
import sys
from pathlib import Path

from lib.project import resolve_project_root
from lib.cli import (
    print_pass,
    print_warn,
    print_error,
    print_header,
    print_summary,
    add_common_args,
    setup_safe_output,
)
from lib.patterns import (
    MATURITY_LEVELS,
    PATTERN_DOMAINS,
    PATTERNS_DIR,
    EXCLUDED_FILENAMES,
    scan_patterns,
    classify_pattern,
    analyze_distribution,
    find_upgrade_candidates,
    build_upgrade_stats,
    build_report_data,
    count_patterns,
    grep_maturity_per_directory,
    parse_readme_stats_table,
    parse_readme_index_table,
    check_stats_consistency,
    update_readme_index_table,
)


# ── stats 子命令 ──────────────────────────────────────────────

def _print_text_report(data):
    """打印文本统计报告。"""
    print_header('模式库成熟度分布统计报告')
    print()

    print('【整体统计】')
    print(f"总模式数: {data['total']}")
    print('成熟度分布:')
    for level in MATURITY_LEVELS:
        count = data['maturity'].get(level, 0)
        percent = (count / data['total'] * 100) if data['total'] > 0 else 0
        print(f'  {level}: {count} ({percent:.1f}%)')
    print()

    print('【按领域统计】')
    print(f"{'领域':<20} {'总数':>6} {'L1':>4} {'L2':>4} {'L3':>4} {'L4':>4}")
    print('-' * 50)
    for domain in ['methodology', 'code', 'architecture']:
        stats = data['domains'][domain]
        print(f"{domain:<20} {stats['total']:>6} {stats['L1']:>4} {stats['L2']:>4} {stats['L3']:>4} {stats['L4']:>4}")
    print()

    print('【待升级模式】')
    has_candidates = False
    for label, key in [('L1 -> L2', 'L1_to_L2'), ('L2 -> L3', 'L2_to_L3')]:
        candidates = data['upgrade_candidates'][key]
        if candidates:
            has_candidates = True
            print(f'\n{label} 候选 ({len(candidates)} 个):')
            for pattern_id in candidates:
                print(f'  - {pattern_id}')
    if not has_candidates:
        print('  暂无待升级模式')
    print()

    if data['issues']:
        print('【结构问题】')
        for issue in data['issues']:
            print(f"  - {issue['path']}: {issue['message']}")
        print()

    print('【模式详细列表】')
    print(f"{'ID':<40} {'领域':<15} {'成熟度':<6} {'验证':<6} {'复用':<6}")
    print('-' * 90)
    for pattern in data['patterns']:
        print(
            f"{pattern['id']:<40} {pattern.get('domain', ''):<15} "
            f"{pattern.get('maturity', ''):<6} {pattern.get('validation_count', 0):<6} "
            f"{pattern.get('reuse_count', 0):<6}"
        )

    print()
    print_header(f"统计完成，共 {data['total']} 个模式文件")


def _print_markdown_report(data):
    """打印 Markdown 统计报告。"""
    print('# 模式库成熟度分布统计报告')
    print()
    print('## 整体统计')
    print()
    print(f"- 总模式数：{data['total']}")
    print()
    print('| 成熟度 | 数量 | 占比 |')
    print('|--------|------|------|')
    for level in MATURITY_LEVELS:
        count = data['maturity'].get(level, 0)
        percent = (count / data['total'] * 100) if data['total'] > 0 else 0
        print(f'| {level} | {count} | {percent:.1f}% |')
    print()

    print('## 按领域统计')
    print()
    print('| 领域 | 总数 | L1 | L2 | L3 | L4 |')
    print('|------|------|----|----|----|----|')
    for domain in ['methodology', 'code', 'architecture']:
        stats = data['domains'][domain]
        print(f"| {domain} | {stats['total']} | {stats['L1']} | {stats['L2']} | {stats['L3']} | {stats['L4']} |")
    print()

    print('## 待升级模式')
    print()
    candidates = data['upgrade_candidates']
    if not candidates['L1_to_L2'] and not candidates['L2_to_L3']:
        print('- 暂无待升级模式')
    else:
        for key, label in [('L1_to_L2', 'L1 -> L2'), ('L2_to_L3', 'L2 -> L3')]:
            if candidates[key]:
                print(f'- {label}：{", ".join(candidates[key])}')
    print()

    if data['issues']:
        print('## 结构问题')
        print()
        for issue in data['issues']:
            print(f"- `{issue['path']}`：{issue['message']}")


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

    data = build_report_data(patterns, issues)

    fmt = getattr(args, 'format', 'text')
    if fmt == 'json' or args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif fmt == 'markdown':
        _print_markdown_report(data)
    else:
        _print_text_report(data)

    if getattr(args, 'check', False) and issues:
        return 1

    return 0


# ── scan-upgrades 子命令 ──────────────────────────────────────

def _domain_label(file_path):
    """从文件路径推断领域中文标签。"""
    if 'architecture' in file_path:
        return '架构'
    elif 'code' in file_path:
        return '代码'
    elif 'methodology' in file_path:
        return '方法论'
    return '其他'


def _print_upgrade_report(patterns, stats):
    """打印偏差扫描报告（人类可读）。"""
    print_header('模式成熟度偏差扫描报告', width=70)

    print(f"\n  总模式数:        {stats['total']}")
    print(f"  累计验证次数:    {stats['validation_total']} 次")
    print(f"  平均验证次数:    {stats['avg_validation']} 次/模式")
    print(f"\n  成熟度分布:")
    for level in MATURITY_LEVELS:
        count = stats['maturity_counts'].get(level, 0)
        pct = round(count / stats['total'] * 100, 1) if stats['total'] > 0 else 0
        bar = '#' * max(1, int(pct / 5))
        print(f"    {level}: {count:>2} 个 ({pct:>5.1f}%) {bar}")

    if stats['upgrades']:
        print(f"\n  [!] 应升级的模式（validation_count >= 2 但 maturity = L1）: {len(stats['upgrades'])} 个")
        print(f"  {'-' * 60}")
        for p in stats['upgrades']:
            domain = _domain_label(p.get('file', ''))
            print(f"    [{domain}] {p.get('id', '')}")
            print(f"           文件: {p.get('file', '')}")
            print(f"           当前: {p.get('maturity', '')}  |  验证次数: {p.get('validation_count', 0)}  |  应升级至: L2")
            print()
    else:
        print(f"\n  [OK] 无需升级的模式")

    if stats['anomalies']:
        print(f"\n  [!!] 异常模式（validation_count = 1 但 maturity >= L2）: {len(stats['anomalies'])} 个")
        print(f"  {'-' * 60}")
        for p in stats['anomalies']:
            print(f"    {p.get('id', '')}: {p.get('file', '')}")
            print(f"         maturity={p.get('maturity', '')}, validation_count={p.get('validation_count', 0)}")
            print()

    print(f"\n  {'-' * 70}")
    print(f"  {'ID':<40} {'成熟度':>4} {'验证':>4} {'状态':>6}")
    print(f"  {'-' * 70}")
    for p in patterns:
        status = classify_pattern(p)
        status_icon = {'upgrade': '[UP]', 'anomaly': '[!!]', 'ok': '[OK]'}[status]
        print(f"  {p.get('id', ''):<40} {p.get('maturity', ''):>4} {p.get('validation_count', 0):>4} {status_icon:>6}")

    print()

    warn_count = len(stats['upgrades'])
    error_count = len(stats['anomalies'])
    pass_count = stats['total'] - warn_count - error_count
    print_summary(pass_count, warn_count, error_count, width=70)


def _print_all_summary(patterns, stats):
    """打印全量模式一览（--all 模式）。"""
    print_header('全量模式成熟度一览', width=80)

    by_category = {'methodology': [], 'architecture': [], 'code': [], 'other': []}
    for p in patterns:
        f = p.get('file', '')
        if 'architecture' in f:
            by_category['architecture'].append(p)
        elif 'code' in f:
            by_category['code'].append(p)
        elif 'methodology' in f:
            by_category['methodology'].append(p)
        else:
            by_category['other'].append(p)

    category_labels = {
        'methodology': '方法论模式',
        'architecture': '架构模式',
        'code': '代码模式',
        'other': '其他',
    }

    for cat, cat_patterns in by_category.items():
        if not cat_patterns:
            continue
        print(f"\n  {category_labels[cat]} ({len(cat_patterns)} 个)")
        print(f"  {'-' * 75}")
        print(f"  {'ID':<40} {'成熟度':>4} {'验证':>4} {'复用':>4} {'状态':>6}")
        print(f"  {'-' * 75}")
        for p in cat_patterns:
            status = classify_pattern(p)
            status_icon = {'upgrade': '[UP]', 'anomaly': '[!!]', 'ok': '[OK]'}[status]
            print(
                f"  {p.get('id', ''):<40} {p.get('maturity', ''):>4} "
                f"{p.get('validation_count', 0):>4} {p.get('reuse_count', 0):>4} {status_icon:>6}"
            )
        print()

    print(f"\n  {'-' * 75}")
    print(
        f"  总计: {stats['total']} 个模式  |  "
        f"L1: {stats['maturity_counts'].get('L1', 0)}  |  "
        f"L2: {stats['maturity_counts'].get('L2', 0)}  |  "
        f"L3: {stats['maturity_counts'].get('L3', 0)}  |  "
        f"L4: {stats['maturity_counts'].get('L4', 0)}"
    )
    print(
        f"  应升级: {len(stats['upgrades'])} 个  |  "
        f"异常: {len(stats['anomalies'])} 个  |  "
        f"平均验证次数: {stats['avg_validation']}"
    )

    warn_count = len(stats['upgrades'])
    error_count = len(stats['anomalies'])
    pass_count = stats['total'] - warn_count - error_count
    print()
    print_summary(pass_count, warn_count, error_count, width=75)


def _print_upgrade_json(patterns, stats):
    """以 JSON 格式输出偏差扫描结果。"""
    output = {
        'stats': {
            'total': stats['total'],
            'validation_total': stats['validation_total'],
            'avg_validation': stats['avg_validation'],
            'maturity_counts': stats['maturity_counts'],
        },
        'upgrades': [
            {
                'id': p['id'],
                'file': p.get('file', ''),
                'current_maturity': p.get('maturity', ''),
                'validation_count': p.get('validation_count', 0),
                'suggested_maturity': 'L2',
            }
            for p in stats['upgrades']
        ],
        'anomalies': [
            {
                'id': p['id'],
                'file': p.get('file', ''),
                'maturity': p.get('maturity', ''),
                'validation_count': p.get('validation_count', 0),
            }
            for p in stats['anomalies']
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


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
    stats = build_upgrade_stats(patterns)

    if args.json:
        _print_upgrade_json(patterns, stats)
    elif args.all:
        _print_all_summary(patterns, stats)
    else:
        _print_upgrade_report(patterns, stats)

    return 0


# ── verify 子命令 ─────────────────────────────────────────────

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


# ── check-index 子命令 ────────────────────────────────────────

def _update_date_readme(readme_path, content):
    """更新 patterns/README.md 中的统计日期行。"""
    from datetime import date
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
        actual_counts[d] = count_patterns(patterns_dir / d)

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


# ── check 子命令（CI 模式）────────────────────────────────────

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
        return 1

    print_pass(f'所有 {len(patterns)} 个模式文件结构完整')
    print_summary(len(patterns), 0, 0)
    return 0


# ── 主入口 ────────────────────────────────────────────────────

def main():
    setup_safe_output()
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

    # stats
    stats_parser = subparsers.add_parser('stats', help='成熟度分布统计报告')
    stats_parser.add_argument('base_dir', nargs='?', default=None, help='模式文件基础目录（默认 docs/retrospective/patterns）')
    stats_parser.add_argument('--format', choices=['text', 'json', 'markdown'], default='text', help='输出格式')
    stats_parser.add_argument('--check', action='store_true', help='CI 检查模式：存在结构问题时返回非 0')
    add_common_args(stats_parser)

    # scan-upgrades
    upgrade_parser = subparsers.add_parser('scan-upgrades', help='成熟度偏差扫描')
    upgrade_parser.add_argument('--all', '-a', action='store_true', help='输出所有模式的状态一览（按类别分组）')
    add_common_args(upgrade_parser)

    # verify
    verify_parser = subparsers.add_parser('verify', help='README 统计表一致性验证')
    add_common_args(verify_parser)

    # check-index
    index_parser = subparsers.add_parser('check-index', help='patterns/ 索引一致性检查与修复')
    index_parser.add_argument('--fix', action='store_true', help='自动更新 patterns/README.md 统计表')
    index_parser.add_argument('--verbose', '-v', action='store_true', help='详细模式：列出每个子目录的文件')
    add_common_args(index_parser)

    # check (CI)
    check_parser = subparsers.add_parser('check', help='CI 检查模式（结构性验证）')
    add_common_args(check_parser)

    args = parser.parse_args()

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
