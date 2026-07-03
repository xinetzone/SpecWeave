import json
import sys
from datetime import datetime
from pathlib import Path

from lib.cli import print_header

from .constants import LARGE_FILE_THRESHOLD, PROFILES, FM_ISSUE_NAMES, FM_ISSUE_NAMES_SHORT


def print_single_result(result, args, project_root):
    metrics = result['metrics']
    scores = result['scores']
    profile = PROFILES[result['profile']]
    profile_name = result['profile']

    print_header('规范落地度量报告')
    print(f'项目根: {project_root}')
    print(f'度量目录: {result["dir"]}')
    print(f'使用配置: {profile_name} ({profile["description"]})')
    print(f'扫描文件数: {metrics["total_files"]}')

    exclude_dirs = result['exclude_dirs']
    user_excludes = result['user_exclude_dirs']
    default_excludes = (exclude_dirs - user_excludes - {'.pytest_cache', 'tests'})
    if default_excludes:
        print(f'默认排除目录: {", ".join(sorted(default_excludes))}')
    if user_excludes:
        print(f'用户排除目录: {", ".join(sorted(user_excludes))}')
    default_exclude_files = profile['default_exclude_files']
    if result['exclude_files'] - default_exclude_files:
        print(f'用户排除文件: {", ".join(sorted(result["exclude_files"] - default_exclude_files))}')
    if args.since:
        print(f'时间范围: {args.since} 之后修改的文件')
    print()

    print('📊 核心指标:')
    weight_map = profile['weights']
    indicator_list = [
        ('frontmatter_coverage', 'Frontmatter覆盖率', f'{metrics["files_with_fm"]}/{metrics["total_files"]}文件有frontmatter', False),
        ('frontmatter_compliance', 'Frontmatter合规率', f'{metrics["fm_compliant"]}/{metrics["files_with_fm"]}合规', True),
        ('link_validity', '链接有效率', f'{metrics["links_valid"]}/{metrics["links_total"]}链接有效', True),
        ('source_traceability', '溯源字段覆盖率', f'{metrics["source_traceable"]}/{metrics["files_with_fm"]}有source', True),
        ('pattern_reference_rate', '模式引用率', f'{metrics["files_with_pattern_refs"]}文件引用模式库', True),
        ('nav_link_compliance', '双向导航合规率', f'{metrics["nav_links_present"]}原子文件有完整导航', True),
    ]
    for key, label, detail, weighted in indicator_list:
        weight = weight_map.get(key, 0) if weighted else 0
        weight_tag = f' [权重{weight}]' if weight > 0 else ' [不计分]' if weighted else ''
        print(f'  {label:<22} {scores[key]:>6}%  ({detail}){weight_tag}')
    large_file_label = '大文档占比(>' + str(LARGE_FILE_THRESHOLD) + '行)'
    print(f'  {large_file_label:<22} {scores["large_file_ratio"]:>6}%  ({metrics["large_files"]}个待原子化)', end='')
    if 'large_file_ratio_inverted' in weight_map:
        w = weight_map['large_file_ratio_inverted']
        print(f' [反向权重{w}]')
    else:
        print(' [仅展示]')
    print()

    print(f'🎯 综合规范落地评分: {scores["overall_adoption_score"]}/100')
    print()

    if metrics['fm_issues']:
        print('⚠️  Frontmatter问题分布:')
        for issue, count in metrics['fm_issues'].items():
            if count > 0:
                print(f'  - {FM_ISSUE_NAMES.get(issue, issue)}: {count}个文件')
        print()

    broken = metrics['links_broken']
    if broken > 0:
        print(f'🔗 断链数量: {broken}（建议运行 check-links.py --fix 修复）')
        print()

    print(f'📈 评级: {result["grade"]}')


def _generate_batch_markdown(results, global_score, global_grade, total_files, project_root):
    md_lines = []
    md_lines.append('# 规范落地度量批量对比报告')
    md_lines.append('')
    md_lines.append(f'- **扫描时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    md_lines.append(f'- **项目根**: `{project_root}`')
    md_lines.append(f'- **全局加权评分**: **{global_score}/100** ({global_grade})')
    md_lines.append(f'- **扫描目录数**: {len(results)}')
    md_lines.append(f'- **总文件数**: {total_files}')
    md_lines.append('')
    md_lines.append('## 目录对比总览')
    md_lines.append('')
    md_lines.append('| 目录 | Profile | 文件数 | 综合评分 | 评级 | FM合规率 | 链接有效率 | 溯源覆盖率 | 模式引用率 | 断链数 | 大文件数 |')
    md_lines.append('|------|---------|--------|---------|------|---------|-----------|-----------|-----------|--------|---------|')
    for r in results:
        m = r['metrics']
        s = r['scores']
        grade_short = r['grade'].split(' ')[0]
        md_lines.append(
            f'| `{r["dir"]}` | {r["profile"]} | {m["total_files"]} | '
            f'**{s["overall_adoption_score"]}** | {grade_short} | '
            f'{s["frontmatter_compliance"]}% | {s["link_validity"]}% | '
            f'{s["source_traceability"]}% | {s["pattern_reference_rate"]}% | '
            f'{m["links_broken"]} | {m["large_files"]} |'
        )
    md_lines.append('')
    md_lines.append('## 权重配置')
    md_lines.append('')
    md_lines.append('| Profile | 适用场景 | 权重配置 |')
    md_lines.append('|---------|---------|---------|')
    for pname, pcfg in PROFILES.items():
        weight_str = ', '.join(f'{k}={v}' for k, v in pcfg['weights'].items())
        md_lines.append(f'| `{pname}` | {pcfg["description"]} | {weight_str} |')
    md_lines.append('')
    md_lines.append('## 各目录问题明细')
    md_lines.append('')
    for r in results:
        m = r['metrics']
        s = r['scores']
        md_lines.append(f'### {r["dir"]} ({r["profile"]}) — {s["overall_adoption_score"]}分/{r["grade"]}')
        md_lines.append('')
        issue_items = []
        for issue_key, count in m['fm_issues'].items():
            if count > 0:
                issue_items.append(f'- {FM_ISSUE_NAMES.get(issue_key, issue_key)}: {count}个文件')
        if issue_items:
            md_lines.append('**Frontmatter问题**:')
            md_lines.extend(issue_items)
        else:
            md_lines.append('- ✅ Frontmatter无问题')
        md_lines.append('')
        if m['links_broken'] > 0:
            md_lines.append(f'- 🔗 断链: {m["links_broken"]}个（建议运行 `check-links.py --fix`）')
        else:
            md_lines.append('- ✅ 链接全部有效')
        if m['large_files'] > 0:
            md_lines.append(f'- 📄 待原子化大文件(>{LARGE_FILE_THRESHOLD}行): {m["large_files"]}个')
        else:
            md_lines.append('- ✅ 无超大文件')
        md_lines.append('')

    return '\n'.join(md_lines)


def print_batch_result(results, global_score, global_grade, total_files, project_root, output_file=None):
    print_header('规范落地度量 - 批量对比报告')
    print(f'项目根: {project_root}')
    print(f'扫描时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'扫描目录数: {len(results)}')
    print(f'总文件数: {total_files}')
    print(f'全局加权评分: {global_score}/100  评级: {global_grade}')
    print()

    print('📊 各目录对比:')
    print()
    header = f'  {"目录":<25} {"Profile":<8} {"文件数":>6} {"综合评分":>8} {"评级":<10} {"FM合规":>7} {"链接有效":>8} {"溯源覆盖":>8} {"模式引用":>8} {"断链":>5} {"大文件":>6}'
    print(header)
    print('  ' + '─' * (len(header) - 2))

    for r in results:
        m = r['metrics']
        s = r['scores']
        dir_display = r['dir'] if len(r['dir']) <= 24 else '...' + r['dir'][-21:]
        print(f'  {dir_display:<25} {r["profile"]:<8} {m["total_files"]:>6} {s["overall_adoption_score"]:>7} {"  " + r["grade"]:<10} {s["frontmatter_compliance"]:>6}% {s["link_validity"]:>7}% {s["source_traceability"]:>7}% {s["pattern_reference_rate"]:>7}% {m["links_broken"]:>5} {m["large_files"]:>6}')

    print()
    print('📋 各目录详情摘要:')
    for r in results:
        m = r['metrics']
        s = r['scores']
        issues = []
        for issue_key, count in m['fm_issues'].items():
            if count > 0:
                issues.append(f'{FM_ISSUE_NAMES_SHORT.get(issue_key, issue_key)}:{count}')
        issue_str = ', '.join(issues) if issues else '无'
        print(f'  {r["dir"]} [{r["profile"]}]: {s["overall_adoption_score"]}分/{r["grade"]}')
        print(f'    FM问题: {issue_str}')
        if m['links_broken'] > 0:
            print(f'    断链: {m["links_broken"]}个')
        if m['large_files'] > 0:
            print(f'    待原子化大文件: {m["large_files"]}个 (>{LARGE_FILE_THRESHOLD}行)')
        print()

    if output_file:
        md_content = _generate_batch_markdown(results, global_score, global_grade, total_files, project_root)
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md_content, encoding='utf-8')
        print(f'📄 Markdown对比报告已保存至: {out_path.resolve()}')


def print_batch_json(results, global_score, global_grade, total_files, project_root, output_file=None):
    json_results = []
    for r in results:
        jr = {
            'dir': r['dir'],
            'profile': r['profile'],
            'total_files': r['metrics']['total_files'],
            'overall_score': r['scores']['overall_adoption_score'],
            'grade': r['grade'],
            'scores': {k: v for k, v in r['scores'].items() if k != 'weights_used'},
            'frontmatter_issues': {k: v for k, v in r['metrics']['fm_issues'].items() if v > 0},
            'broken_links': r['metrics']['links_broken'],
            'large_files': r['metrics']['large_files'],
        }
        json_results.append(jr)
    output = {
        'type': 'batch_report',
        'timestamp': datetime.now().isoformat(),
        'project_root': str(project_root),
        'global_score': global_score,
        'global_grade': global_grade,
        'total_files_scanned': total_files,
        'directories': json_results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if output_file:
        out_path = Path(output_file)
        out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'\n📄 JSON报告已保存至: {out_path}', file=sys.stderr)
