#!/usr/bin/env python3
"""
自动生成/修复 Markdown 文件的 x-toml-ref 相对路径。

根据文件在项目中的位置，自动计算到 .meta/toml/ 下对应 TOML 文件的相对路径。
路径计算公式：
  1. MD文件相对于项目根的路径 P（如 docs/knowledge/mdi-research/00-executive-summary.md）
  2. MD文件所在目录距项目根的深度 N（路径中父目录的 / 数量）
  3. x-toml-ref = '../' * N + '.meta/toml/' + P.replace('.md', '.toml')

用法：
    python fix-x-toml-ref.py --dir docs/knowledge/ [--dry-run] [--write] [--create-toml]
    python fix-x-toml-ref.py --file docs/knowledge/mdi-research/00-executive-summary.md --dry-run
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.project import resolve_project_root
from lib.frontmatter import parse_yaml_frontmatter, extract_yaml_field, extract_all_yaml_fields


FM_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)


def compute_x_toml_ref(md_path: Path, project_root: Path) -> str:
    """计算MD文件对应的x-toml-ref相对路径值。

    Args:
        md_path: MD文件绝对路径。
        project_root: 项目根目录绝对路径。

    Returns:
        x-toml-ref的相对路径字符串（正斜杠分隔）。
    """
    rel_path = md_path.relative_to(project_root).as_posix()
    toml_rel = '.meta/toml/' + rel_path.replace('.md', '.toml')
    parent_depth = len(Path(rel_path).parent.parts)
    if parent_depth == 0:
        return toml_rel
    return '../' * parent_depth + toml_rel


def get_toml_target_path(md_path: Path, project_root: Path) -> Path:
    """获取MD文件对应的TOML文件绝对路径。"""
    rel_path = md_path.relative_to(project_root).as_posix()
    toml_rel = '.meta/toml/' + rel_path.replace('.md', '.toml')
    return (project_root / toml_rel).resolve()


def fix_x_toml_ref_in_content(content: str, new_ref: str) -> tuple[str, bool, str | None]:
    """在frontmatter中修复或添加x-toml-ref字段。

    返回 (新内容, 是否修改, 旧值)。
    字段顺序：保持id→title→source→x-toml-ref的约定顺序。
    """
    fm_match = FM_PATTERN.match(content)
    if not fm_match:
        return content, False, None

    fm_text = fm_match.group(1)
    fm_start = fm_match.start()
    fm_end = fm_match.end()

    existing_ref = extract_yaml_field(fm_text, 'x-toml-ref')
    if existing_ref is not None and existing_ref.strip() == new_ref:
        return content, False, existing_ref

    lines = fm_text.split('\n')
    new_lines = []
    replaced = False
    inserted = False

    anchor_fields = ('x-toml-ref', 'source', 'title')
    anchor_found = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('x-toml-ref:') or stripped.startswith('x-toml-ref :'):
            indent_match = re.match(r'^(\s*)', line)
            indent = indent_match.group(1) if indent_match else ''
            new_lines.append(f'{indent}x-toml-ref: "{new_ref}"')
            replaced = True
            continue
        new_lines.append(line)

    if not replaced:
        insert_after_idx = -1
        for i, line in enumerate(new_lines):
            s = line.strip()
            if s.startswith('source:') or s.startswith('source :'):
                insert_after_idx = i
                break
        if insert_after_idx == -1:
            for i, line in enumerate(new_lines):
                s = line.strip()
                if s.startswith('title:') or s.startswith('title :'):
                    insert_after_idx = i
                    break
        if insert_after_idx == -1:
            for i, line in enumerate(new_lines):
                s = line.strip()
                if s.startswith('id:') or s.startswith('id :'):
                    insert_after_idx = i
                    break

        if insert_after_idx >= 0:
            indent_match = re.match(r'^(\s*)', new_lines[insert_after_idx])
            indent = indent_match.group(1) if indent_match else ''
            new_lines.insert(insert_after_idx + 1, f'{indent}x-toml-ref: "{new_ref}"')
        else:
            new_lines.append(f'x-toml-ref: "{new_ref}"')
        inserted = True

    new_fm_text = '\n'.join(new_lines)
    new_content = content[:fm_start] + '---\n' + new_fm_text + '\n---\n' + content[fm_end:]
    return new_content, True, existing_ref


def create_toml_file(toml_path: Path, md_path: Path, project_root: Path, title_hint: str | None = None, md_id: str | None = None) -> bool:
    """创建TOML元数据文件（如果不存在）。

    Args:
        toml_path: TOML文件绝对路径。
        md_path: 对应的MD文件绝对路径。
        project_root: 项目根目录。
        title_hint: 标题提示（从H1提取）。
        md_id: MD frontmatter中的id字段值。

    Returns:
        是否创建了新文件。
    """
    if toml_path.exists():
        return False

    toml_path.parent.mkdir(parents=True, exist_ok=True)

    rel = md_path.relative_to(project_root).as_posix()
    parts = Path(rel).parts
    if '.agents' in parts:
        idx = parts.index('.agents')
        category = '/'.join(parts[idx + 1:-1]) if len(parts) > idx + 2 else 'agents'
    elif 'docs' in parts:
        idx = parts.index('docs')
        if len(parts) > idx + 1:
            category = '/'.join(parts[idx + 1:-1])
        else:
            category = 'docs'
    else:
        category = 'other'

    title = title_hint or md_path.stem
    if title.endswith('.md'):
        title = title[:-3]

    if not md_id:
        stem = md_path.stem.lower()
        parent = md_path.parent.name.lower() if md_path.parent != project_root else ''
        if stem == 'readme' and parent:
            md_id = f'{parent}-readme'
        else:
            md_id = stem

    content = f'''id = "{md_id}"
title = "{title}"
category = "{category}"
date = "2026-07-02"
version = "1.0"
'''
    toml_path.write_text(content, encoding='utf-8')
    return True


def extract_h1(content: str) -> str | None:
    """提取第一个H1标题。"""
    m = re.search(r'^#\s+(.+?)\s*$', content, re.MULTILINE)
    return m.group(1).strip() if m else None


def process_file(md_path: Path, project_root: Path, dry_run: bool = True, create_toml: bool = False) -> dict:
    """处理单个文件。"""
    result = {
        'file': str(md_path),
        'status': 'skip',
        'old_ref': None,
        'new_ref': None,
        'toml_created': False,
        'reason': None,
    }

    try:
        content = md_path.read_text(encoding='utf-8')
    except Exception as e:
        result['status'] = 'error'
        result['reason'] = f'读取失败: {e}'
        return result

    fm_match = FM_PATTERN.match(content)
    if not fm_match:
        result['status'] = 'skip'
        result['reason'] = '无YAML frontmatter'
        return result

    fm_text = fm_match.group(1)
    fm_fields = extract_all_yaml_fields(fm_text)
    md_id = None
    for key in ('id', '"id"', "'id'"):
        if key in fm_fields:
            md_id = fm_fields[key]
            if isinstance(md_id, str):
                md_id = md_id.strip().strip('"').strip("'")
            break

    new_ref = compute_x_toml_ref(md_path, project_root)
    result['new_ref'] = new_ref

    existing_ref = extract_yaml_field(fm_text, 'x-toml-ref')
    if existing_ref is not None and existing_ref.strip() == new_ref:
        result['status'] = 'skip'
        result['old_ref'] = existing_ref
        result['reason'] = 'x-toml-ref已正确'
        if create_toml:
            toml_path = get_toml_target_path(md_path, project_root)
            if not toml_path.exists():
                title = extract_h1(content)
                if not dry_run:
                    created = create_toml_file(toml_path, md_path, project_root, title, md_id)
                    result['toml_created'] = created
                    if created:
                        result['status'] = 'toml_created'
                else:
                    result['status'] = 'would_create_toml'
        return result

    new_content, modified, old_ref = fix_x_toml_ref_in_content(content, new_ref)
    result['old_ref'] = old_ref

    if not modified:
        result['status'] = 'skip'
        result['reason'] = '无需修改'
        return result

    if dry_run:
        result['status'] = 'would_modify'
        if create_toml:
            toml_path = get_toml_target_path(md_path, project_root)
            if not toml_path.exists():
                result['status'] = 'would_modify_and_create_toml'
    else:
        md_path.write_text(new_content, encoding='utf-8')
        result['status'] = 'modified'
        if create_toml:
            toml_path = get_toml_target_path(md_path, project_root)
            if not toml_path.exists():
                title = extract_h1(content)
                created = create_toml_file(toml_path, md_path, project_root, title, md_id)
                result['toml_created'] = created
                if created:
                    result['status'] = 'modified_and_toml_created'

    return result


def main():
    parser = argparse.ArgumentParser(description='自动生成/修复x-toml-ref相对路径')
    parser.add_argument('--dir', help='目标目录（递归扫描）')
    parser.add_argument('--file', help='单个文件路径')
    parser.add_argument('--dry-run', action='store_true', help='仅预览变更，不写入')
    parser.add_argument('--write', action='store_true', help='实际写入变更')
    parser.add_argument('--create-toml', action='store_true', help='为缺失的TOML文件创建骨架')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    args = parser.parse_args()

    if not args.dry_run and not args.write:
        print('⚠️  请指定 --dry-run（预览）或 --write（写入）')
        sys.exit(1)
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

    print(f'项目根: {project_root}')
    if args.dir:
        print(f'扫描目录: {args.dir}')
    print(f'找到 {len(md_files)} 个Markdown文件')
    print(f'模式: {"预览(dry-run)" if args.dry_run else "写入(write)"}')
    if args.create_toml:
        print(f'TOML创建: 启用（自动创建缺失的TOML骨架文件）')
    print()

    stats = {
        'total': len(md_files),
        'modified': 0,
        'would_modify': 0,
        'toml_created': 0,
        'would_create_toml': 0,
        'skip_correct': 0,
        'skip_no_fm': 0,
        'error': 0,
    }

    for fpath in md_files:
        try:
            rel = fpath.relative_to(project_root)
        except ValueError:
            rel = fpath
        result = process_file(fpath, project_root, dry_run=args.dry_run, create_toml=args.create_toml)
        status = result['status']

        if status == 'modified':
            stats['modified'] += 1
            print(f'  ✅ 已修复: {rel}')
            if args.verbose:
                print(f'     旧值: {result["old_ref"]}')
                print(f'     新值: {result["new_ref"]}')
        elif status == 'modified_and_toml_created':
            stats['modified'] += 1
            stats['toml_created'] += 1
            print(f'  ✅ 已修复+创建TOML: {rel}')
            print(f'     x-toml-ref: {result["new_ref"]}')
        elif status == 'toml_created':
            stats['toml_created'] += 1
            print(f'  📄 已创建TOML: {rel}')
        elif status == 'would_modify':
            stats['would_modify'] += 1
            print(f'  📝 将修复: {rel}')
            if args.verbose or result['old_ref']:
                print(f'     旧值: {result["old_ref"]}')
                print(f'     新值: {result["new_ref"]}')
        elif status == 'would_modify_and_create_toml':
            stats['would_modify'] += 1
            stats['would_create_toml'] += 1
            print(f'  📝 将修复+创建TOML: {rel}')
            print(f'     新值: {result["new_ref"]}')
        elif status == 'would_create_toml':
            stats['would_create_toml'] += 1
            if args.verbose:
                print(f'  📄 将创建TOML: {rel}')
        elif status == 'error':
            stats['error'] += 1
            print(f'  ❌ 错误: {rel} - {result["reason"]}')
        else:
            if args.verbose:
                print(f'  ⏭️  跳过: {rel} ({result["reason"]})')
            if result['reason'] == 'x-toml-ref已正确':
                stats['skip_correct'] += 1
            elif result['reason'] == '无YAML frontmatter':
                stats['skip_no_fm'] += 1

    print(f'\n{"=" * 60}')
    print('统计汇总:')
    print(f'  总文件数: {stats["total"]}')
    if args.dry_run:
        print(f'  将修复x-toml-ref: {stats["would_modify"]}')
        if args.create_toml:
            print(f'  将创建TOML: {stats["would_create_toml"]}')
    else:
        print(f'  已修复x-toml-ref: {stats["modified"]}')
        if args.create_toml:
            print(f'  已创建TOML: {stats["toml_created"]}')
    print(f'  跳过(已是正确值): {stats["skip_correct"]}')
    print(f'  跳过(无frontmatter): {stats["skip_no_fm"]}')
    print(f'  错误: {stats["error"]}')


if __name__ == '__main__':
    main()
