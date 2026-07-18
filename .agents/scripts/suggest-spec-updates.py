#!/usr/bin/env python3
"""
模式反哺规范更新建议工具（Pattern→Spec Feedback Loop）。

实现"实践→复盘→模式→规范→实践"的闭环：
1. 扫描最近新增/更新的模式文件
2. 分析模式中涉及的规范领域
3. 检查相关基础规范是否需要同步更新
4. 生成规范更新建议报告

用法：
    python suggest-spec-updates.py                       # 扫描最近30天新增模式
    python suggest-spec-updates.py --days 7              # 扫描最近7天
    python suggest-spec-updates.py --since 2026-07-01    # 扫描指定日期后
    python suggest-spec-updates.py --json                # JSON格式输出
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.project import resolve_project_root
from lib.frontmatter import parse_yaml_frontmatter, extract_all_yaml_fields, _YAML_FRONTMATTER_RE, parse_toml_frontmatter_as_dict
from lib.markdown import find_markdown_files, extract_title
from lib.cli import print_header, add_common_args


FM_PATTERN = _YAML_FRONTMATTER_RE

SPEC_DIRS = [
    '.agents/rules',
    '.agents/protocols',
    '.agents/templates',
    'docs/development-standards.md',
    'AGENTS.md',
]

DOMAIN_KEYWORDS = {
    'frontmatter': ['frontmatter', '元数据', 'metadata', 'yaml', 'toml'],
    'atomization': ['原子化', 'atomization', '拆分', 'split'],
    'mermaid': ['mermaid', '流程图', '图表'],
    'links': ['链接', 'link', '导航', 'navigation'],
    'git': ['git', 'commit', '提交', '分支'],
    'testing': ['测试', 'test', 'coverage', '覆盖率'],
    'tools': ['工具', 'tool', '脚本', 'script', '自动化'],
    'naming': ['命名', 'naming', '文件名', 'convention'],
    'documentation': ['文档', 'doc', '文档架构'],
    'refactoring': ['重构', 'refactor', 'rewrite'],
    'patterns': ['模式', 'pattern', '复用'],
    'encoding': ['编码', 'encoding', 'utf-8', 'gbk'],
    'ci': ['ci', '门禁', 'gate', '流水线'],
}


def parse_pattern_file(pattern_path: Path, project_root: Path) -> dict:
    result = {
        'path': str(pattern_path),
        'rel_path': '',
        'id': '',
        'title': '',
        'maturity': '',
        'domain': '',
        'source': '',
        'keywords': set(),
        'has_spec_update_hint': False,
        'spec_hints': [],
    }

    try:
        rel_path = pattern_path.relative_to(project_root).as_posix()
        result['rel_path'] = rel_path
    except ValueError:
        pass

    try:
        content = pattern_path.read_text(encoding='utf-8')
    except Exception:
        return result

    result['title'] = extract_title(pattern_path) or pattern_path.stem

    fm_match = FM_PATTERN.match(content)
    if fm_match:
        fm_text = fm_match.group(1)
        fields = extract_all_yaml_fields(fm_text)
        result['id'] = fields.get('id', '')
        result['maturity'] = fields.get('maturity', '')
        result['domain'] = fields.get('domain', '')
        result['source'] = fields.get('source', '')

    body = content[fm_match.end():] if fm_match else content
    body_lower = body.lower()

    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in body_lower:
                result['keywords'].add(domain)
                break

    update_hints = [
        r'规范.*更新',
        r'建议.*修改.*(?:规则|规范|标准|AGENTS)',
        r'应(?:该|当)(?:加入|添加|补充|更新).*(?:规则|规范|检查)',
        r'CI.*(?:增加|添加|新增)',
        r'规范.*(?:缺少|缺失|未覆盖)',
        r'spec.*update',
        r'rule.*(?:missing|add|update)',
    ]
    for hint_pattern in update_hints:
        matches = re.findall(hint_pattern, body)
        if matches:
            result['has_spec_update_hint'] = True
            for m in matches[:3]:
                context_start = max(0, body.find(m) - 50)
                context_end = min(len(body), body.find(m) + len(m) + 50)
                context = body[context_start:context_end].strip().replace('\n', ' ')
                result['spec_hints'].append(context)

    return result


def find_related_specs(keywords: set, project_root: Path) -> list[dict]:
    related = []

    spec_files = []
    for spec_dir in SPEC_DIRS:
        spec_path = project_root / spec_dir
        if spec_path.is_file() and spec_path.suffix == '.md':
            spec_files.append(spec_path)
        elif spec_path.is_dir():
            spec_files.extend(spec_path.rglob('*.md'))

    for spec_file in spec_files:
        try:
            rel = spec_file.relative_to(project_root).as_posix()
            content = spec_file.read_text(encoding='utf-8').lower()
            title = extract_title(spec_file) or spec_file.name
        except Exception:
            continue

        matched_domains = set()
        for domain in keywords:
            kws = DOMAIN_KEYWORDS.get(domain, [])
            for kw in kws:
                if kw.lower() in content:
                    matched_domains.add(domain)
                    break

        if matched_domains:
            related.append({
                'path': str(spec_file),
                'rel_path': rel,
                'title': title,
                'matched_domains': matched_domains,
            })

    return related


def scan_patterns(project_root: Path, days: int = 30, since_date: str = None) -> list[dict]:
    patterns_root = project_root / '.agents/docs/retrospective/patterns'
    if not patterns_root.exists():
        return []

    since_dt = None
    if since_date:
        try:
            since_dt = datetime.strptime(since_date, '%Y-%m-%d')
        except ValueError:
            pass
    else:
        since_dt = datetime.now() - timedelta(days=days)

    pattern_files = []
    for pattern_file in find_markdown_files(patterns_root):
        try:
            rel = pattern_file.relative_to(project_root).as_posix()
        except ValueError:
            continue
        if rel.endswith('README.md') or rel.endswith('CATEGORIES.md'):
            continue
        try:
            mtime = datetime.fromtimestamp(pattern_file.stat().st_mtime)
            if mtime >= since_dt:
                pattern_files.append(pattern_file)
        except OSError:
            pattern_files.append(pattern_file)

    results = []
    for pf in sorted(pattern_files, key=lambda p: p.stat().st_mtime, reverse=True):
        info = parse_pattern_file(pf, project_root)
        info['related_specs'] = find_related_specs(info['keywords'], project_root)
        results.append(info)

    return results


def generate_suggestions(patterns: list[dict]) -> list[dict]:
    suggestions = []

    for p in patterns:
        if not p['keywords'] and not p['has_spec_update_hint']:
            continue

        spec_targets = {}
        for spec in p['related_specs']:
            for domain in spec['matched_domains']:
                if domain not in spec_targets:
                    spec_targets[domain] = []
                spec_targets[domain].append(spec)

        suggestion = {
            'pattern': p['title'],
            'pattern_path': p['rel_path'],
            'maturity': p['maturity'],
            'domains': list(p['keywords']),
            'suggested_spec_updates': [],
        }

        if p['has_spec_update_hint']:
            suggestion['suggested_spec_updates'].append({
                'type': 'explicit_hint',
                'description': '模式内容中显式提到规范需要更新',
                'contexts': p['spec_hints'][:2],
            })

        domain_guidance = {
            'frontmatter': '检查AGENTS.md/.agents/rules/中的frontmatter规范是否需要更新',
            'atomization': '检查.agents/workflows/中原子化操作流程是否需要更新',
            'links': '检查链接规范或双向导航相关规则是否需要补充',
            'tools': '检查工具开发规范和CI检查清单是否需要加入新检查',
            'ci': '检查CI流水线脚本是否需要新增门禁检查',
            'naming': '检查文件命名规范是否覆盖新场景',
            'encoding': '检查编码规范是否覆盖新发现的乱码场景',
            'mermaid': '检查Mermaid规范和检查脚本是否需要更新',
            'patterns': '检查CATEGORIES.md和模式库索引是否同步更新',
            'testing': '检查测试规范和覆盖率要求是否需要调整',
        }

        for domain in p['keywords']:
            if domain in domain_guidance:
                related = spec_targets.get(domain, [])
                suggestion['suggested_spec_updates'].append({
                    'type': 'domain_match',
                    'domain': domain,
                    'description': domain_guidance[domain],
                    'related_specs': [s['rel_path'] for s in related[:3]],
                })

        if suggestion['suggested_spec_updates']:
            suggestions.append(suggestion)

    return suggestions


def main(argv=None):
    parser = argparse.ArgumentParser(description='模式反哺规范更新建议工具')
    parser.add_argument('--days', type=int, default=30, help='扫描最近N天新增/修改的模式（默认30天）')
    parser.add_argument('--since', help='扫描指定日期(YYYY-MM-DD)后的模式')
    add_common_args(parser)
    args = parser.parse_args(argv)

    project_root = resolve_project_root(__file__)
    patterns_root = project_root / '.agents/docs/retrospective/patterns'

    print_header('模式→规范闭环更新建议')
    print(f'项目根: {project_root}')
    print(f'模式库: {patterns_root}')
    if args.since:
        print(f'扫描时间: {args.since} 之后')
    else:
        print(f'扫描时间: 最近 {args.days} 天')
    print()

    patterns = scan_patterns(project_root, days=args.days, since_date=args.since)
    print(f'发现 {len(patterns)} 个近期新增/更新的模式文件')

    if not patterns:
        print('没有发现需要反哺规范的新模式。闭环健康 ✅')
        sys.exit(0)

    suggestions = generate_suggestions(patterns)

    if args.json:
        output = {
            'scanned_patterns': len(patterns),
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat(),
        }
        print(json.dumps(output, ensure_ascii=False, indent=2, default=list))
        sys.exit(0)

    print(f'生成 {len(suggestions)} 条规范更新建议:')
    print()

    for i, s in enumerate(suggestions, 1):
        print(f'{i}. 模式: {s["pattern"]} (成熟度: {s["maturity"] or "未标注"})')
        print(f'   路径: {s["pattern_path"]}')
        print(f'   涉及领域: {", ".join(s["domains"])}')
        for u in s['suggested_spec_updates']:
            if u['type'] == 'explicit_hint':
                print(f'   [显式提示] {u["description"]}')
                for ctx in u.get('contexts', []):
                    print(f'     上下文: ...{ctx}...')
            else:
                print(f'   [领域关联] {u["description"]}')
                for spec in u.get('related_specs', []):
                    print(f'     → 检查: {spec}')
        print()

    if suggestions:
        print('💡 闭环操作建议:')
        print('   1. 评审每条建议，确认是否需要更新对应规范')
        print('   2. 更新规范后，在规范的source字段中反向引用新模式')
        print('   3. 如有必要，新增/更新对应的自动化检查脚本')
        print('   4. 更新CI检查清单，确保新规范被门禁覆盖')
        print('   5. 在模式文件中记录"规范已更新"状态')
    else:
        print('✅ 所有近期模式均已被现有规范覆盖，无需额外更新。')

    sys.exit(0)


if __name__ == '__main__':
    main()
