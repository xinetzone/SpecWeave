import json
from pathlib import Path

from .models import AuditResult


def format_text_report(result: AuditResult, project_root: Path) -> str:
    lines = []
    lines.append('=' * 60)
    lines.append('元数据生态健康度审计报告')
    lines.append('=' * 60)
    lines.append(f'项目根: {project_root}')
    lines.append('')

    lines.append('── 覆盖率统计 ──')
    fm_rate = (result.md_with_frontmatter / result.total_md_files * 100) if result.total_md_files > 0 else 0
    toml_rate = (result.md_with_x_toml_ref / result.md_with_frontmatter * 100) if result.md_with_frontmatter > 0 else 0
    lines.append(f'  MD文件总数:          {result.total_md_files}')
    lines.append(f'  有frontmatter:      {result.md_with_frontmatter} ({fm_rate:.1f}%)')
    lines.append(f'  有x-toml-ref:       {result.md_with_x_toml_ref} ({toml_rate:.1f}% of FM)')
    lines.append(f'  TOML文件总数:        {result.total_toml_files}')
    lines.append(f'  TOML有有效id:       {result.toml_with_valid_id}')
    lines.append('')

    if result.errors:
        lines.append(f'── 错误 ({len(result.errors)}) ──')
        by_cat = {}
        for e in result.errors:
            by_cat.setdefault(e.category, []).append(e)
        for cat, issues in sorted(by_cat.items()):
            lines.append(f'  [{cat}] ({len(issues)}个)')
            for issue in issues[:10]:
                lines.append(f'    ❌ {issue.file}')
                lines.append(f'       {issue.message}')
            if len(issues) > 10:
                lines.append(f'    ... 还有{len(issues) - 10}个')
        lines.append('')

    if result.warnings:
        lines.append(f'── 警告 ({len(result.warnings)}) ──')
        by_cat = {}
        for w in result.warnings:
            by_cat.setdefault(w.category, []).append(w)
        for cat, issues in sorted(by_cat.items()):
            lines.append(f'  [{cat}] ({len(issues)}个)')
            for issue in issues[:10]:
                lines.append(f'    ⚠️  {issue.file}')
                lines.append(f'       {issue.message}')
            if len(issues) > 10:
                lines.append(f'    ... 还有{len(issues) - 10}个')
        lines.append('')

    if result.fixed:
        lines.append(f'── 自动修复 ({len(result.fixed)}) ──')
        for f in result.fixed:
            lines.append(f'  ✅ {f}')
        lines.append('')

    error_count = len(result.errors)
    warn_count = len(result.warnings)
    lines.append('=' * 60)
    if error_count == 0:
        lines.append(f'✅ 审计通过（{warn_count}个警告）')
    else:
        lines.append(f'❌ 审计发现{error_count}个错误，{warn_count}个警告')
    lines.append('=' * 60)

    return '\n'.join(lines)


def format_json_report(result: AuditResult, project_root: Path) -> str:
    data = {
        'project_root': str(project_root),
        'summary': {
            'total_md_files': result.total_md_files,
            'md_with_frontmatter': result.md_with_frontmatter,
            'md_with_x_toml_ref': result.md_with_x_toml_ref,
            'total_toml_files': result.total_toml_files,
            'toml_with_valid_id': result.toml_with_valid_id,
            'error_count': len(result.errors),
            'warning_count': len(result.warnings),
            'fixed_count': len(result.fixed),
        },
        'errors': [
            {'severity': e.severity, 'category': e.category, 'file': e.file, 'message': e.message}
            for e in result.errors
        ],
        'warnings': [
            {'severity': w.severity, 'category': w.category, 'file': w.file, 'message': w.message}
            for w in result.warnings
        ],
        'fixed': result.fixed,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)
