#!/usr/bin/env python3
"""
元数据分层校验工具（Metadata Layering Checker）。

基于 metadata-layering 模式（内容-元数据二分法原则），自动检测：
1. frontmatter 行数膨胀（>10行提示重构，>20行强警告）
2. 应外部化到TOML的字段（索引/管理/历史/聚合类字段出现在YAML中）
3. 核心标识字段缺失（id/source/x-toml-ref）
4. TOML外部元数据与内联字段不一致
5. 嵌套结构违反扁平原则
6. 重构建议：哪些字段应移至TOML

用法：
    python check-metadata-layering.py --dir docs/              # 检查指定目录
    python check-metadata-layering.py --dir . --exclude vendor  # 全项目检查
    python check-metadata-layering.py --file path/to/file.md    # 检查单个文件
    python check-metadata-layering.py --dir docs/ --strict      # 严格模式（警告视为错误）
    python check-metadata-layering.py --dir docs/ --suggest     # 输出详细重构建议
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.project import resolve_project_root
from lib.frontmatter import parse_yaml_frontmatter, extract_all_yaml_fields, _YAML_FRONTMATTER_RE
from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, add_common_args


FM_PATTERN = _YAML_FRONTMATTER_RE
INDENTED_BLOCK_RE = re.compile(r'^\s{2,}\S', re.MULTILINE)
ID_PATTERN = re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$')

INLINE_ALLOWED_FIELDS = {
    'id',
    'source',
    'x-toml-ref',
    'title',
    'name',
    'domain',
    'layer',
    'maturity',
    'validation_count',
    'reuse_count',
    'documentation_level',
    'rules',
    'references',
    'skills',
    'related_patterns',
    'bindings',
}

TOML_EXTERNAL_FIELDS = {
    'category',
    'tags',
    'date',
    'created',
    'updated',
    'version',
    'status',
    'changelog',
    'author',
    'authors',
    'part_of',
    'summary',
    'description',
    'aliases',
    'see_also',
}

FM_LINE_WARN = 10
FM_LINE_ERROR = 20


def check_file_layering(md_path: Path, project_root: Path, suggest: bool = False) -> dict:
    result = {
        'file': str(md_path),
        'errors': [],
        'warnings': [],
        'suggestions': [],
        'fm_lines': 0,
    }

    try:
        content = md_path.read_text(encoding='utf-8')
    except Exception as e:
        result['errors'].append(f'读取失败: {e}')
        return result

    rel_path = None
    try:
        rel_path = md_path.relative_to(project_root).as_posix()
    except ValueError:
        rel_path = str(md_path)

    if rel_path.startswith('.trae/specs/') or rel_path.startswith('vendor/'):
        return result

    fm_match = FM_PATTERN.match(content)
    if not fm_match:
        return result

    fm_text = fm_match.group(1)
    fm_lines = fm_text.strip().split('\n')
    result['fm_lines'] = len(fm_lines)

    if len(fm_lines) > FM_LINE_ERROR:
        result['errors'].append(
            f'frontmatter严重膨胀（{len(fm_lines)}行，超过{FM_LINE_ERROR}行阈值），'
            f'建议将索引/管理字段外部化至TOML'
        )
    elif len(fm_lines) > FM_LINE_WARN:
        result['warnings'].append(
            f'frontmatter偏长（{len(fm_lines)}行，建议≤{FM_LINE_WARN}行），'
            f'考虑是否有字段可外部化'
        )

    fields = extract_all_yaml_fields(fm_text)

    has_id = 'id' in fields
    has_source = 'source' in fields
    has_xref = 'x-toml-ref' in fields

    if not has_id:
        result['warnings'].append('缺少核心标识字段 id')
    if not has_xref:
        result['warnings'].append('缺少外部元数据引用 x-toml-ref，无法关联TOML元数据')

    is_derived = bool(
        re.search(r'/\d{2}-', rel_path)
        or rel_path.endswith(('-retrospective.md', '-insight.md', '-suggestions.md',
                              'insight-extraction.md', 'export-suggestions.md'))
    )
    if is_derived and not has_source:
        result['warnings'].append('派生产物缺少 source 溯源字段')

    external_in_yaml = []
    for f in fields:
        f_normalized = f.lower().replace('-', '_')
        if f in TOML_EXTERNAL_FIELDS or f_normalized in TOML_EXTERNAL_FIELDS:
            external_in_yaml.append(f)

    if external_in_yaml:
        result['warnings'].append(
            f'YAML中包含应外部化到TOML的字段: {", ".join(external_in_yaml)}'
        )
        if suggest:
            result['suggestions'].append(
                f'  → 将 {", ".join(external_in_yaml)} 移至 .meta/toml/ 对应的TOML文件中'
            )

    indented_lines = []
    for i, line in enumerate(fm_lines, 1):
        if INDENTED_BLOCK_RE.match(line) and not line.strip().startswith('#'):
            stripped = line.strip()
            if not stripped.startswith(('rules =', 'references =', 'skills =',
                                       'related_patterns =', 'bindings =',
                                       'rules:', 'references:', 'skills:',
                                       'related_patterns:', 'bindings:')):
                indented_lines.append(i)
    if indented_lines:
        result['warnings'].append(
            f'frontmatter包含非白名单嵌套结构（第{indented_lines[:3]}行），'
            f'复杂结构应外部化到TOML'
        )

    if has_xref:
        xref_val = fields.get('x-toml-ref', '')
        if isinstance(xref_val, str):
            xref_clean = xref_val.strip().strip('"').strip("'")
            toml_abs = (md_path.parent / xref_clean).resolve()
            if not toml_abs.exists():
                result['warnings'].append(
                    f'x-toml-ref指向的TOML文件不存在: {xref_clean}'
                )

    if suggest and len(fm_lines) > FM_LINE_WARN:
        yaml_only = set(fields.keys()) - INLINE_ALLOWED_FIELDS - TOML_EXTERNAL_FIELDS
        if yaml_only:
            result['suggestions'].append(
                f'  → 评审以下字段是否属于内容必要字段: {", ".join(sorted(yaml_only))}'
            )
        if len(fm_lines) > FM_LINE_ERROR:
            result['suggestions'].append(
                '  → 推荐重构：保留id/source/x-toml-ref + 内容直接引用的字段，'
                '其余移至TOML'
            )

    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description='元数据分层校验工具（基于内容-元数据二分法原则）')
    parser.add_argument('--dir', help='目标目录（递归扫描）')
    parser.add_argument('--file', help='单个文件路径')
    parser.add_argument('--strict', action='store_true', help='严格模式：警告也视为错误')
    parser.add_argument('--suggest', action='store_true', help='输出详细重构建议')
    parser.add_argument('--exclude', action='append', default=[], help='排除的目录名（可多次指定）')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示所有文件（包括通过的）')
    add_common_args(parser)
    args = parser.parse_args(argv)

    if not args.dir and not args.file:
        print('⚠️  请指定 --dir 或 --file')
        sys.exit(1)

    project_root = resolve_project_root(__file__)

    if args.file:
        md_files = [Path(args.file).resolve()]
    else:
        target_dir = Path(args.dir).resolve()
        if not target_dir.is_dir():
            print(f'❌ 目录不存在: {target_dir}')
            sys.exit(1)
        md_files = sorted(target_dir.rglob('*.md'))
        if args.exclude:
            md_files = [
                f for f in md_files
                if not any(ex in f.relative_to(project_root).as_posix().split('/') for ex in args.exclude)
            ]

    print_header('元数据分层校验')
    print(f'项目根: {project_root}')
    if args.dir:
        print(f'检查目录: {args.dir}')
    print(f'找到 {len(md_files)} 个Markdown文件')
    print(f'阈值: 警告>{FM_LINE_WARN}行, 错误>{FM_LINE_ERROR}行')
    if args.strict:
        print('模式: 严格（警告视为错误）')
    if args.suggest:
        print('模式: 输出重构建议')
    print()

    total_errors = 0
    total_warnings = 0
    files_with_issues = 0
    files_clean = 0
    fm_line_stats = []

    for fpath in md_files:
        try:
            rel = fpath.relative_to(project_root).as_posix()
        except ValueError:
            rel = str(fpath)

        result = check_file_layering(fpath, project_root, suggest=args.suggest)
        errors = result['errors']
        warnings = result['warnings']
        suggestions = result['suggestions']

        if result['fm_lines'] > 0:
            fm_line_stats.append(result['fm_lines'])

        if args.strict:
            all_issues = errors + warnings
        else:
            all_issues = errors

        if errors:
            total_errors += len(errors)
        if warnings:
            total_warnings += len(warnings)

        has_display = bool(errors) or (args.strict and bool(warnings))
        has_warn_only = bool(warnings) and not errors and not args.strict

        if has_display:
            files_with_issues += 1
            print(f'❌ {rel}')
            for e in errors:
                print(f'   [错误] {e}')
            for w in warnings:
                if args.strict:
                    print(f'   [错误] {w}')
                else:
                    print(f'   [警告] {w}')
            for s in suggestions:
                print(f'   [建议] {s}')
        elif has_warn_only:
            if args.verbose:
                files_with_issues += 1
                print(f'⚠️  {rel}')
                for w in warnings:
                    print(f'   [警告] {w}')
                for s in suggestions:
                    print(f'   [建议] {s}')
            else:
                files_clean += 1
        else:
            files_clean += 1
            if args.verbose:
                print(f'✅ {rel}')

    print()
    print_summary(
        pass_count=files_clean,
        warn_count=total_warnings if not args.strict else 0,
        error_count=total_errors + (total_warnings if args.strict else 0),
    )

    if fm_line_stats:
        avg_lines = sum(fm_line_stats) / len(fm_line_stats)
        max_lines = max(fm_line_stats)
        over_warn = sum(1 for l in fm_line_stats if l > FM_LINE_WARN)
        over_error = sum(1 for l in fm_line_stats if l > FM_LINE_ERROR)
        print(f'\nFrontmatter行数统计:')
        print(f'  平均行数: {avg_lines:.1f}')
        print(f'  最大行数: {max_lines}')
        print(f'  超过{FM_LINE_WARN}行: {over_warn}个文件')
        print(f'  超过{FM_LINE_ERROR}行: {over_error}个文件')

    exit_code = 1 if total_errors > 0 or (args.strict and total_warnings > 0) else 0
    if exit_code == 0:
        print(f'\n✅ 元数据分层校验通过')
    else:
        print(f'\n❌ 元数据分层存在问题')
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
