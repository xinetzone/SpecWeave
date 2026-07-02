#!/usr/bin/env python3
"""
Frontmatter 完整性校验工具。

检查所有 Markdown 文件的 YAML frontmatter 是否符合规范，包括：
1. 必填字段检查：id、x-toml-ref
2. 条件必填字段检查：派生产物必须有 source
3. x-toml-ref 路径有效性：指向的 TOML 文件是否存在
4. 禁止字段检查：YAML 中不应包含 category/date/tags/version/changelog（应在TOML）
5. 扁平结构检查：YAML 不应有多行缩进嵌套
6. id 命名规范：kebab-case 格式
7. title 字段检查：YAML中有title时TOML中title应一致（TOML优先）

用法：
    python check-frontmatter.py --dir docs/                    # 检查指定目录
    python check-frontmatter.py --dir . --exclude vendor       # 全项目检查（排除vendor）
    python check-frontmatter.py --file path/to/file.md         # 检查单个文件
    python check-frontmatter.py --dir docs/ --strict           # 严格模式（所有警告都视为错误）
    python check-frontmatter.py --dir docs/ --fix-toml-ref     # 自动修复x-toml-ref路径错误
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.project import resolve_project_root
from lib.frontmatter import parse_yaml_frontmatter, extract_yaml_field, extract_all_yaml_fields, _YAML_FRONTMATTER_RE


FM_PATTERN = _YAML_FRONTMATTER_RE
H1_PATTERN = re.compile(r'^#\s+(.+?)\s*$', re.MULTILINE)
ID_PATTERN = re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$')

FORBIDDEN_YAML_FIELDS = {'category', 'date', 'tags', 'version', 'changelog'}

INDENTED_BLOCK_RE = re.compile(r'^\s{2,}\S', re.MULTILINE)


def compute_x_toml_ref(md_path: Path, project_root: Path) -> str:
    """计算正确的x-toml-ref值（与fix-x-toml-ref.py保持一致）。"""
    rel_path = md_path.relative_to(project_root).as_posix()
    toml_rel = '.meta/toml/' + rel_path.replace('.md', '.toml')
    parent_depth = len(Path(rel_path).parent.parts)
    if parent_depth == 0:
        return toml_rel
    return '../' * parent_depth + toml_rel


def check_file(md_path: Path, project_root: Path, strict: bool = False, fix_toml_ref: bool = False) -> dict:
    """检查单个文件的frontmatter完整性。

    Returns:
        dict with keys: file, errors, warnings, fixed
    """
    result = {
        'file': str(md_path),
        'errors': [],
        'warnings': [],
        'fixed': [],
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
        if '.agents/' in rel_path or rel_path.startswith('docs/'):
            result['warnings'].append('无YAML frontmatter')
        return result

    fm_text = fm_match.group(1)
    fields = extract_all_yaml_fields(fm_text)

    fm_id = fields.get('id')
    if not fm_id:
        result['errors'].append('缺少必填字段: id')
    elif isinstance(fm_id, str):
        clean_id = fm_id.strip().strip('"').strip("'")
        if not ID_PATTERN.match(clean_id):
            result['warnings'].append(f'id命名不符合kebab-case规范: "{clean_id}"')

    x_ref = fields.get('x-toml-ref')
    if not x_ref:
        result['errors'].append('缺少必填字段: x-toml-ref')
    elif isinstance(x_ref, str):
        expected_ref = compute_x_toml_ref(md_path, project_root)
        if x_ref.strip() != expected_ref:
            if fix_toml_ref:
                result['warnings'].append(f'x-toml-ref路径错误（已修复）: "{x_ref.strip()}" -> "{expected_ref}"')
            else:
                result['errors'].append(f'x-toml-ref路径错误: 当前="{x_ref.strip()}", 期望="{expected_ref}"')

        toml_path_candidate = x_ref.strip().strip('"').strip("'")
        toml_abs = (md_path.parent / toml_path_candidate).resolve()
        if not toml_abs.exists():
            result['warnings'].append(f'x-toml-ref指向的TOML文件不存在: {toml_path_candidate}')

    has_source = 'source' in fields
    is_in_mdi = 'mdi-research/' in rel_path
    is_in_retrospective = 'retrospective/reports/' in rel_path
    is_chapter_file = bool(re.search(r'/\d{2}-', rel_path))
    is_report_file = rel_path.endswith(('-retrospective.md', '-insight.md', '-suggestions.md', 'insight-extraction.md', 'export-suggestions.md', 'execution-retrospective.md'))

    is_derived = is_chapter_file or is_report_file or is_in_mdi
    is_index = rel_path.endswith('/README.md') or rel_path.endswith('README.md') and 'reports/' in rel_path
    is_rule = '.agents/rules/' in rel_path or '.agents/roles/' in rel_path or '.agents/protocols/' in rel_path

    if is_derived and not has_source and not is_index:
        result['warnings'].append('派生产物缺少source溯源字段')
    elif is_rule and not has_source:
        result['warnings'].append('规则/规范文件建议包含source字段标注来源')

    forbidden_found = [f for f in FORBIDDEN_YAML_FIELDS if f in fields]
    if forbidden_found:
        result['warnings'].append(f'YAML中包含应移至TOML的字段: {", ".join(forbidden_found)}')

    lines = fm_text.split('\n')
    indented_lines = []
    for i, line in enumerate(lines, 1):
        if INDENTED_BLOCK_RE.match(line) and not line.strip().startswith('#'):
            indented_lines.append(i)
    if indented_lines:
        result['warnings'].append(f'frontmatter疑似包含多行缩进嵌套（第{indented_lines[:3]}行），违反扁平结构规则')

    if 'title' in fields:
        h1_match = H1_PATTERN.search(content)
        if h1_match:
            h1_title = h1_match.group(1).strip()
            yaml_title = fields['title']
            if isinstance(yaml_title, str):
                clean_yaml_title = yaml_title.strip().strip('"').strip("'")
                if clean_yaml_title != h1_title and not clean_yaml_title.endswith(h1_title):
                    result['warnings'].append(f'title字段与H1标题不一致: YAML="{clean_yaml_title}", H1="{h1_title}"')

    if fix_toml_ref and any('x-toml-ref路径错误（已修复）' in w for w in result['warnings']):
        expected_ref = compute_x_toml_ref(md_path, project_root)
        new_content = fix_x_toml_ref_value(content, expected_ref)
        if new_content != content:
            md_path.write_text(new_content, encoding='utf-8')
            result['fixed'].append('x-toml-ref')

    return result


def fix_x_toml_ref_value(content: str, new_ref: str) -> str:
    """修复content中的x-toml-ref字段值。"""
    fm_match = FM_PATTERN.match(content)
    if not fm_match:
        return content
    fm_text = fm_match.group(1)
    fm_start = fm_match.start()
    fm_end = fm_match.end()
    lines = fm_text.split('\n')
    new_lines = []
    replaced = False
    for line in lines:
        if line.strip().startswith('x-toml-ref:') or line.strip().startswith('x-toml-ref :'):
            indent_match = re.match(r'^(\s*)', line)
            indent = indent_match.group(1) if indent_match else ''
            new_lines.append(f'{indent}x-toml-ref: "{new_ref}"')
            replaced = True
        else:
            new_lines.append(line)
    if not replaced:
        new_lines.append(f'x-toml-ref: "{new_ref}"')
    new_fm_text = '\n'.join(new_lines)
    return content[:fm_start] + '---\n' + new_fm_text + '\n---\n' + content[fm_end:]


def main(argv=None):
    parser = argparse.ArgumentParser(description='Frontmatter完整性校验工具')
    parser.add_argument('--dir', help='目标目录（递归扫描）')
    parser.add_argument('--file', help='单个文件路径')
    parser.add_argument('--strict', action='store_true', help='严格模式：警告也视为错误（退出码1）')
    parser.add_argument('--fix-toml-ref', action='store_true', help='自动修复x-toml-ref路径错误')
    parser.add_argument('--exclude', action='append', default=[], help='排除的目录名（可多次指定）')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示所有文件（包括通过的）')
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

    print(f'项目根: {project_root}')
    if args.dir:
        print(f'检查目录: {args.dir}')
    print(f'找到 {len(md_files)} 个Markdown文件')
    if args.strict:
        print('模式: 严格（警告视为错误）')
    if args.fix_toml_ref:
        print('自动修复: x-toml-ref路径错误')
    print()

    total_errors = 0
    total_warnings = 0
    total_fixed = 0
    files_with_issues = 0
    files_clean = 0

    for fpath in md_files:
        try:
            rel = fpath.relative_to(project_root).as_posix()
        except ValueError:
            rel = str(fpath)

        result = check_file(fpath, project_root, strict=args.strict, fix_toml_ref=args.fix_toml_ref)
        errors = result['errors']
        warnings = result['warnings']
        fixed = result['fixed']

        if args.strict:
            all_issues = errors + warnings
        else:
            all_issues = errors

        if errors:
            total_errors += len(errors)
        if warnings:
            total_warnings += len(warnings)
        if fixed:
            total_fixed += len(fixed)

        has_display = bool(errors or fixed) or (args.strict and bool(warnings))
        has_warn_only = bool(warnings) and not errors and not fixed and not args.strict

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
            for f in fixed:
                print(f'   [已修复] {f}')
        elif has_warn_only:
            if args.verbose:
                files_with_issues += 1
                print(f'⚠️  {rel}')
                for w in warnings:
                    print(f'   [警告] {w}')
            else:
                files_clean += 1
        else:
            files_clean += 1
            if args.verbose:
                print(f'✅ {rel}')

    print(f'\n{"=" * 60}')
    print('校验结果汇总:')
    print(f'  总文件数: {len(md_files)}')
    print(f'  通过: {files_clean}')
    print(f'  有问题: {files_with_issues}')
    print(f'  错误总数: {total_errors}')
    if not args.strict:
        print(f'  警告总数: {total_warnings}')
    if args.fix_toml_ref:
        print(f'  自动修复: {total_fixed}')

    exit_code = 1 if total_errors > 0 or (args.strict and total_warnings > 0) else 0
    if exit_code == 0:
        print(f'\n✅ 校验通过')
    else:
        print(f'\n❌ 校验未通过')
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
