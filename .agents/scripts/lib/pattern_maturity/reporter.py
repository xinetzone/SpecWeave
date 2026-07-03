"""模式成熟度工具 - 报告生成。"""

import json

from lib.cli import print_header, print_summary

from .constants import CATEGORY_LABELS, DOMAIN_ORDER, DOMAIN_LABELS, MATURITY_LEVELS, STATUS_ICONS
from .scanner import classify_pattern


def domain_label(file_path: str) -> str:
    """从文件路径推断领域中文标签。"""
    for key, label in DOMAIN_LABELS.items():
        if key in file_path and key != 'other':
            return label
    return DOMAIN_LABELS['other']


def print_text_report(data: dict) -> None:
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
    for domain in DOMAIN_ORDER:
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


def print_markdown_report(data: dict) -> None:
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
    for domain in DOMAIN_ORDER:
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


def print_upgrade_report(patterns: list, stats: dict) -> None:
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
            domain = domain_label(p.get('file', ''))
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
        status_icon = STATUS_ICONS[status]
        print(f"  {p.get('id', ''):<40} {p.get('maturity', ''):>4} {p.get('validation_count', 0):>4} {status_icon:>6}")

    print()

    warn_count = len(stats['upgrades'])
    error_count = len(stats['anomalies'])
    pass_count = stats['total'] - warn_count - error_count
    print_summary(pass_count, warn_count, error_count, width=70)


def print_all_summary(patterns: list, stats: dict) -> None:
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

    for cat, cat_patterns in by_category.items():
        if not cat_patterns:
            continue
        print(f"\n  {CATEGORY_LABELS[cat]} ({len(cat_patterns)} 个)")
        print(f"  {'-' * 75}")
        print(f"  {'ID':<40} {'成熟度':>4} {'验证':>4} {'复用':>4} {'状态':>6}")
        print(f"  {'-' * 75}")
        for p in cat_patterns:
            status = classify_pattern(p)
            status_icon = STATUS_ICONS[status]
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


def print_upgrade_json(patterns: list, stats: dict) -> None:
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
