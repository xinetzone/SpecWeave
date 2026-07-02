#!/usr/bin/env python3
"""
规范落地度量指标跟踪工具（Spec Adoption Metrics）。

度量新规范发布后的遵循率，识别落地失败的规范，提供数据驱动的规范治理能力。

度量维度：
1. frontmatter规范遵循率（四字段完整性、扁平结构）
2. 链接有效性率（内部链接可达性）
3. 原子化覆盖率（大文档是否已原子化）
4. 模式引用率（文档中引用可复用模式的比例）
5. 元数据分层合规率（frontmatter无膨胀、字段归位正确）
6. 规范发现率（规范在总览/导航中被引用的比例）

用法：
    python check-spec-adoption.py --dir docs/                                      # 度量指定目录
    python check-spec-adoption.py --dir . --exclude-dirs vendor                    # 全项目度量排除vendor
    python check-spec-adoption.py --dir .agents/ --exclude-dirs skills             # 排除Skill专用目录（任意层级）
    python check-spec-adoption.py --dir .agents/ --exclude-dirs scripts/mdi/examples  # 排除子路径
    python check-spec-adoption.py --dir .agents/ --exclude-files SKILL-TEMPLATE.md # 排除特定文件
    python check-spec-adoption.py --json                                           # JSON格式输出（供CI/仪表盘使用）
    python check-spec-adoption.py --since 2026-07-01                               # 只度量指定日期后修改的文件

默认排除：.pytest_cache、tests、__pycache__（系统目录）
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.project import resolve_project_root
from lib.frontmatter import parse_yaml_frontmatter, extract_all_yaml_fields, _YAML_FRONTMATTER_RE
from lib.markdown import find_markdown_files, parse_inline_links
from lib.cli import print_header, print_summary, add_common_args


FM_PATTERN = _YAML_FRONTMATTER_RE
REQUIRED_CORE_FIELDS = {'id', 'x-toml-ref'}
FORBIDDEN_EXTERNAL_FIELDS = {'category', 'date', 'tags', 'version', 'changelog'}
PATTERN_LINK_RE = re.compile(r'\]\((?:\.\./)*patterns/[^)]+\.md\)')
LARGE_FILE_THRESHOLD = 300


def compute_metrics(md_files: list[Path], project_root: Path, since_date: str = None) -> dict:
    metrics = {
        'total_files': 0,
        'files_with_fm': 0,
        'fm_compliant': 0,
        'fm_issues': {
            'missing_id': 0,
            'missing_xref': 0,
            'has_forbidden_fields': 0,
            'has_nested': 0,
            'bloated_fm': 0,
        },
        'links_total': 0,
        'links_valid': 0,
        'links_broken': 0,
        'large_files': 0,
        'atomized_files': 0,
        'pattern_references': 0,
        'files_with_pattern_refs': 0,
        'nav_links_present': 0,
        'source_traceable': 0,
        'files_scanned': [],
    }

    since_dt = None
    if since_date:
        try:
            since_dt = datetime.strptime(since_date, '%Y-%m-%d')
        except ValueError:
            pass

    for fpath in md_files:
        rel_path = None
        try:
            rel_path = fpath.relative_to(project_root).as_posix()
        except ValueError:
            rel_path = str(fpath)

        if since_dt:
            try:
                mtime = datetime.fromtimestamp(fpath.stat().st_mtime)
                if mtime < since_dt:
                    continue
            except OSError:
                pass

        metrics['total_files'] += 1

        try:
            content = fpath.read_text(encoding='utf-8')
        except Exception:
            continue

        fm_match = FM_PATTERN.match(content)
        if fm_match:
            metrics['files_with_fm'] += 1
            fm_text = fm_match.group(1)
            fields = extract_all_yaml_fields(fm_text)
            issues = []

            if 'id' not in fields:
                metrics['fm_issues']['missing_id'] += 1
                issues.append('missing_id')
            if 'x-toml-ref' not in fields:
                metrics['fm_issues']['missing_xref'] += 1
                issues.append('missing_xref')

            forbidden = [f for f in FORBIDDEN_EXTERNAL_FIELDS if f in fields]
            if forbidden:
                metrics['fm_issues']['has_forbidden_fields'] += 1
                issues.append('has_forbidden_fields')

            indented = sum(1 for line in fm_text.split('\n')
                          if re.match(r'^\s{2,}\S', line) and not line.strip().startswith('#'))
            if indented > 0:
                metrics['fm_issues']['has_nested'] += 1
                issues.append('has_nested')

            fm_line_count = len(fm_text.strip().split('\n'))
            if fm_line_count > 15:
                metrics['fm_issues']['bloated_fm'] += 1
                issues.append('bloated_fm')

            if not issues:
                metrics['fm_compliant'] += 1

            if 'source' in fields:
                metrics['source_traceable'] += 1
        else:
            metrics['fm_issues']['missing_id'] += 1
            metrics['fm_issues']['missing_xref'] += 1

        links = parse_inline_links(content)
        local_links = [(text, url) for text, url in links
                      if not url.startswith(('http://', 'https://', 'file:///', '#'))
                      and not url.startswith('mailto:')]
        metrics['links_total'] += len(local_links)
        for text, url in local_links:
            clean_url = url.split('#')[0].split('?')[0]
            target = (fpath.parent / clean_url).resolve()
            if target.exists():
                metrics['links_valid'] += 1
            else:
                metrics['links_broken'] += 1

        line_count = len(content.split('\n'))
        if line_count > LARGE_FILE_THRESHOLD:
            metrics['large_files'] += 1

        chapter_match = re.search(r'/\d{2}-[a-z]', rel_path)
        index_file = rel_path.endswith('/README.md')
        nav_patterns = ['上一章', '下一章', '返回目录', 'prev', 'next', '返回索引']
        has_nav = any(p in content for p in nav_patterns)
        if chapter_match and has_nav:
            metrics['nav_links_present'] += 1
            metrics['atomized_files'] += 1
        elif chapter_match and not has_nav:
            pass

        if PATTERN_LINK_RE.search(content):
            metrics['pattern_references'] += len(PATTERN_LINK_RE.findall(content))
            metrics['files_with_pattern_refs'] += 1

        metrics['files_scanned'].append(rel_path)

    return metrics


def compute_scores(metrics: dict) -> dict:
    scores = {}
    total = metrics['total_files']
    if total == 0:
        return {'error': 'no_files'}

    with_fm = metrics['files_with_fm']
    scores['frontmatter_coverage'] = round(with_fm / total * 100, 1) if total > 0 else 0
    scores['frontmatter_compliance'] = round(metrics['fm_compliant'] / max(with_fm, 1) * 100, 1)
    scores['link_validity'] = round(metrics['links_valid'] / max(metrics['links_total'], 1) * 100, 1)
    scores['source_traceability'] = round(metrics['source_traceable'] / max(with_fm, 1) * 100, 1)
    scores['pattern_reference_rate'] = round(metrics['files_with_pattern_refs'] / max(total, 1) * 100, 1)
    scores['large_file_ratio'] = round(metrics['large_files'] / max(total, 1) * 100, 1)
    scores['nav_link_compliance'] = round(metrics['nav_links_present'] / max(metrics['atomized_files'] + 1, 1) * 100, 1)

    weights = {
        'frontmatter_compliance': 0.25,
        'link_validity': 0.25,
        'source_traceability': 0.20,
        'pattern_reference_rate': 0.15,
        'nav_link_compliance': 0.15,
    }
    overall = sum(scores[k] * w for k, w in weights.items() if k in scores)
    scores['overall_adoption_score'] = round(overall, 1)

    return scores


def main(argv=None):
    parser = argparse.ArgumentParser(description='规范落地度量指标跟踪工具')
    parser.add_argument('--dir', help='目标目录（递归扫描）')
    parser.add_argument('--file', help='单个文件路径')
    parser.add_argument('--since', help='只度量指定日期(YYYY-MM-DD)后修改的文件')
    parser.add_argument('--exclude-dirs', action='append', default=[], dest='exclude_dirs',
                        help='排除的目录名（可多次指定，如 --exclude-dirs skills --exclude-dirs .pytest_cache）')
    parser.add_argument('--exclude', action='append', default=[], dest='_exclude_legacy',
                        help=argparse.SUPPRESS)
    parser.add_argument('--exclude-files', action='append', default=[], dest='exclude_files',
                        help='排除的具体文件名（可多次指定，如 --exclude-files ONBOARDING.md）')
    add_common_args(parser)
    args = parser.parse_args(argv)

    if not args.dir and not args.file:
        print('⚠️  请指定 --dir 或 --file')
        sys.exit(1)

    project_root = resolve_project_root(__file__)

    exclude_dirs = set(args.exclude_dirs) | set(args._exclude_legacy)
    exclude_dirs.add('.pytest_cache')
    exclude_dirs.add('tests')
    exclude_files = set(args.exclude_files)

    if args.file:
        md_files = [Path(args.file).resolve()]
    else:
        target_dir = Path(args.dir).resolve() if args.dir else project_root
        md_files = find_markdown_files(target_dir, exclude_dirs=exclude_dirs)
        if exclude_dirs:
            dir_name_excludes = {d for d in exclude_dirs if '/' not in d}
            path_prefix_excludes = {d.rstrip('/') + '/' for d in exclude_dirs if '/' in d}
            md_files_filtered = []
            for f in md_files:
                rel_posix = f.relative_to(target_dir).as_posix()
                rel_parts = rel_posix.split('/')
                excluded = False
                for part in rel_parts[:-1]:
                    if part in dir_name_excludes:
                        excluded = True
                        break
                if not excluded:
                    for prefix in path_prefix_excludes:
                        if rel_posix.startswith(prefix):
                            excluded = True
                            break
                if not excluded:
                    md_files_filtered.append(f)
            md_files = md_files_filtered
        if exclude_files:
            md_files = [
                f for f in md_files
                if f.name not in exclude_files
            ]

    metrics = compute_metrics(md_files, project_root, since_date=args.since)
    scores = compute_scores(metrics)

    if args.json:
        output = {
            'metrics': metrics,
            'scores': scores,
            'timestamp': datetime.now().isoformat(),
            'project_root': str(project_root),
        }
        del output['metrics']['files_scanned']
        print(json.dumps(output, ensure_ascii=False, indent=2))
        sys.exit(0)

    print_header('规范落地度量报告')
    print(f'项目根: {project_root}')
    if args.dir:
        print(f'度量目录: {args.dir}')
    print(f'扫描文件数: {metrics["total_files"]}')
    if args.since:
        print(f'时间范围: {args.since} 之后修改的文件')
    print()

    print('📊 核心指标:')
    print(f'  Frontmatter覆盖率:        {scores["frontmatter_coverage"]:>6}%  ({metrics["files_with_fm"]}/{metrics["total_files"]}文件有frontmatter)')
    print(f'  Frontmatter合规率:        {scores["frontmatter_compliance"]:>6}%  ({metrics["fm_compliant"]}/{metrics["files_with_fm"]}合规)')
    print(f'  链接有效率:               {scores["link_validity"]:>6}%  ({metrics["links_valid"]}/{metrics["links_total"]}链接有效)')
    print(f'  溯源字段覆盖率:           {scores["source_traceability"]:>6}%  ({metrics["source_traceable"]}/{metrics["files_with_fm"]}有source)')
    print(f'  模式引用率:               {scores["pattern_reference_rate"]:>6}%  ({metrics["files_with_pattern_refs"]}文件引用模式库)')
    print(f'  双向导航合规率:           {scores["nav_link_compliance"]:>6}%  ({metrics["nav_links_present"]}原子文件有完整导航)')
    print(f'  大文档占比(>{LARGE_FILE_THRESHOLD}行): {scores["large_file_ratio"]:>6}%  ({metrics["large_files"]}个待原子化)')
    print()

    print(f'🎯 综合规范落地评分: {scores["overall_adoption_score"]}/100')
    print()

    if metrics['fm_issues']:
        print('⚠️  Frontmatter问题分布:')
        for issue, count in metrics['fm_issues'].items():
            if count > 0:
                issue_names = {
                    'missing_id': '缺少id字段',
                    'missing_xref': '缺少x-toml-ref',
                    'has_forbidden_fields': '包含应外部化字段',
                    'has_nested': '存在嵌套结构',
                    'bloated_fm': 'frontmatter膨胀(>15行)',
                }
                print(f'  - {issue_names.get(issue, issue)}: {count}个文件')
        print()

    broken = metrics['links_broken']
    if broken > 0:
        print(f'🔗 断链数量: {broken}（建议运行 check-links.py --fix 修复）')
        print()

    if scores['overall_adoption_score'] >= 90:
        grade = 'A (优秀)'
    elif scores['overall_adoption_score'] >= 80:
        grade = 'B (良好)'
    elif scores['overall_adoption_score'] >= 70:
        grade = 'C (需改进)'
    elif scores['overall_adoption_score'] >= 60:
        grade = 'D (较差)'
    else:
        grade = 'F (不及格)'
    print(f'📈 评级: {grade}')

    sys.exit(0 if scores['overall_adoption_score'] >= 70 else 1)


if __name__ == '__main__':
    main()
