#!/usr/bin/env python3
"""模式库成熟度分布统计脚本。

自动扫描三个子目录所有模式文件，解析 frontmatter 中的成熟度字段，
输出分布统计表、待升级模式清单，并支持 CI 检查与机器可读输出。
"""

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict

REQUIRED_FIELDS = [
    'id',
    'domain',
    'layer',
    'maturity',
    'validation_count',
    'reuse_count',
    'documentation_level',
    'source',
]
DOMAINS = ['methodology-patterns', 'code-patterns', 'architecture-patterns']
MATURITY_LEVELS = ['L1', 'L2', 'L3', 'L4']


def parse_frontmatter(filepath):
    """解析 Markdown 文件的 TOML frontmatter。"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.match(r'^\+\+\+\n(.*?)\n\+\+\+', content, re.DOTALL)
    if not match:
        return None

    frontmatter = match.group(1)
    result = {}

    string_fields = ['id', 'domain', 'layer', 'maturity', 'documentation_level', 'source']
    for field in string_fields:
        field_match = re.search(rf'{field} = "([^"]+)"', frontmatter)
        if field_match:
            result[field] = field_match.group(1)

    int_fields = ['validation_count', 'reuse_count']
    for field in int_fields:
        field_match = re.search(rf'{field} = (\d+)', frontmatter)
        if field_match:
            result[field] = int(field_match.group(1))

    return result


def scan_patterns(base_dir):
    """扫描指定目录下所有模式文件。"""
    patterns = []
    issues = []

    for domain_dir in DOMAINS:
        domain_path = os.path.join(base_dir, domain_dir)
        if not os.path.isdir(domain_path):
            issues.append({
                'type': 'missing_directory',
                'path': domain_path,
                'message': '模式目录不存在',
            })
            continue

        for filepath in glob.glob(os.path.join(domain_path, '*.md')):
            if os.path.basename(filepath) == 'README.md':
                continue

            frontmatter = parse_frontmatter(filepath)
            if not frontmatter:
                issues.append({
                    'type': 'missing_frontmatter',
                    'path': filepath,
                    'message': '缺少 TOML frontmatter',
                })
                continue

            missing_fields = [field for field in REQUIRED_FIELDS if field not in frontmatter]
            if missing_fields:
                issues.append({
                    'type': 'missing_fields',
                    'path': filepath,
                    'message': f"缺少字段: {', '.join(missing_fields)}",
                    'fields': missing_fields,
                })

            frontmatter['filepath'] = filepath
            frontmatter['domain'] = domain_dir.replace('-patterns', '')
            patterns.append(frontmatter)

    return patterns, issues


def analyze_patterns(patterns):
    """分析模式成熟度分布。"""
    stats = {
        'maturity': defaultdict(int),
        'domain': defaultdict(int),
        'total': 0,
    }
    domain_stats = defaultdict(lambda: {'total': 0, 'L1': 0, 'L2': 0, 'L3': 0, 'L4': 0})

    for pattern in patterns:
        maturity = pattern.get('maturity', 'unknown')
        domain = pattern.get('domain', 'unknown')

        stats['maturity'][maturity] += 1
        stats['domain'][domain] += 1
        stats['total'] += 1

        domain_stats[domain]['total'] += 1
        domain_stats[domain][maturity] += 1

    return stats, domain_stats


def find_upgrade_candidates(patterns):
    """找出待升级模式。"""
    candidates = {
        'L1_to_L2': [],
        'L2_to_L3': [],
    }

    for pattern in patterns:
        maturity = pattern.get('maturity', '')
        validation_count = pattern.get('validation_count', 0)
        reuse_count = pattern.get('reuse_count', 0)

        if maturity == 'L1' and validation_count >= 2:
            candidates['L1_to_L2'].append(pattern)
        elif maturity == 'L2' and reuse_count >= 1:
            candidates['L2_to_L3'].append(pattern)

    return candidates


def build_report_data(patterns, issues):
    """构建统一报告数据。"""
    stats, domain_stats = analyze_patterns(patterns)
    candidates = find_upgrade_candidates(patterns)

    return {
        'total': stats['total'],
        'maturity': {level: stats['maturity'].get(level, 0) for level in MATURITY_LEVELS},
        'domains': {
            domain: domain_stats[domain]
            for domain in ['methodology', 'code', 'architecture']
        },
        'upgrade_candidates': {
            key: [pattern['id'] for pattern in value]
            for key, value in candidates.items()
        },
        'patterns': sorted(patterns, key=lambda x: (x.get('domain', ''), x.get('id', ''))),
        'issues': issues,
    }


def print_text_report(data):
    """打印文本统计报告。"""
    print('=' * 60)
    print('模式库成熟度分布统计报告')
    print('=' * 60)
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
    for label, key in [('L1 → L2', 'L1_to_L2'), ('L2 → L3', 'L2_to_L3')]:
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
        print(f"{pattern['id']:<40} {pattern.get('domain', ''):<15} {pattern.get('maturity', ''):<6} {pattern.get('validation_count', 0):<6} {pattern.get('reuse_count', 0):<6}")

    print()
    print('=' * 60)
    print(f"统计完成，共 {data['total']} 个模式文件")
    print('=' * 60)


def print_markdown_report(data):
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
        for key, label in [('L1_to_L2', 'L1 → L2'), ('L2_to_L3', 'L2 → L3')]:
            if candidates[key]:
                print(f'- {label}：{", ".join(candidates[key])}')
    print()

    if data['issues']:
        print('## 结构问题')
        print()
        for issue in data['issues']:
            print(f"- `{issue['path']}`：{issue['message']}")


def main():
    parser = argparse.ArgumentParser(description='模式库成熟度分布统计')
    parser.add_argument('base_dir', nargs='?', default='docs/retrospective/patterns', help='模式文件基础目录')
    parser.add_argument('--format', choices=['text', 'json', 'markdown'], default='text', help='输出格式')
    parser.add_argument('--check', action='store_true', help='CI 检查模式：存在结构问题时返回非 0')
    args = parser.parse_args()

    if not os.path.isdir(args.base_dir):
        print(f"错误: 目录 '{args.base_dir}' 不存在", file=sys.stderr)
        sys.exit(1)

    patterns, issues = scan_patterns(args.base_dir)
    if not patterns:
        print('警告: 未找到模式文件', file=sys.stderr)
        sys.exit(1 if args.check else 0)

    data = build_report_data(patterns, issues)

    if args.format == 'json':
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.format == 'markdown':
        print_markdown_report(data)
    else:
        print_text_report(data)

    if args.check and issues:
        sys.exit(1)


if __name__ == '__main__':
    main()
