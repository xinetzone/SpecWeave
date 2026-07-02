#!/usr/bin/env python3
"""
批量为缺失id字段的Markdown文件frontmatter添加id字段。

id从文件路径生成kebab-case：文件名（去.md、去数字前缀）作为id，
对数字前缀章节文件（如00-overview.md）加上父目录名作为前缀。

用法：
    python add-frontmatter-id.py --dir docs/ [--dry-run] [--write]
"""

import argparse
import re
import sys
from pathlib import Path

FM_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)


def kebab_case(name: str) -> str:
    name = re.sub(r'^\d+[-_]?', '', name)
    name = name.replace('_', '-').replace(' ', '-')
    name = re.sub(r'[^a-zA-Z0-9-]', '-', name)
    name = re.sub(r'-+', '-', name).strip('-')
    return name.lower()


def generate_id(file_path: Path, project_root: Path) -> str:
    rel = file_path.relative_to(project_root).with_suffix('')
    parts = list(rel.parts)
    file_stem = parts[-1]

    if file_stem.lower() == 'readme':
        if len(parts) > 1:
            parent = kebab_case(parts[-2])
            return f"{parent}-readme"
        return 'readme'

    stem_kebab = kebab_case(file_stem)

    if re.match(r'^\d+[-_]', file_stem) and len(parts) > 1:
        parent = kebab_case(parts[-2])
        return f"{parent}-{stem_kebab}"

    depth_from_docs = len(parts) - 1
    if depth_from_docs >= 4:
        parent = kebab_case(parts[-2])
        return f"{parent}-{stem_kebab}"

    return stem_kebab


def has_id_field(fm_text: str) -> bool:
    return bool(re.search(r'^id\s*:', fm_text, re.MULTILINE))


def add_id_to_content(content: str, new_id: str) -> str:
    match = FM_PATTERN.match(content)
    if not match:
        return content
    fm_text = match.group(1)
    fm_end = match.end()
    lines = fm_text.split('\n')
    new_fm_lines = []
    id_inserted = False
    for line in lines:
        if not id_inserted and (line.startswith('title:') or line.startswith('id:')):
            new_fm_lines.append(f'id: "{new_id}"')
            id_inserted = True
            if line.startswith('id:'):
                continue
        new_fm_lines.append(line)
    if not id_inserted:
        new_fm_lines.insert(0, f'id: "{new_id}"')
    new_fm = '\n'.join(new_fm_lines)
    return f'---\n{new_fm}\n---\n' + content[fm_end:]


def process_file(file_path: Path, project_root: Path, dry_run: bool) -> tuple[bool, str]:
    try:
        content = file_path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as e:
        return False, f'读取失败: {e}'

    if not content.startswith('---'):
        return False, '无frontmatter'

    fm_match = FM_PATTERN.match(content)
    if not fm_match:
        return False, 'frontmatter格式错误'

    fm_text = fm_match.group(1)
    if has_id_field(fm_text):
        return False, '已有id'

    new_id = generate_id(file_path, project_root)

    if dry_run:
        return True, f'[dry-run] 将添加id="{new_id}"'

    new_content = add_id_to_content(content, new_id)
    file_path.write_text(new_content, encoding='utf-8')
    return True, f'已添加id="{new_id}"'


def iter_md_files(target_dir: Path, exclude: set) -> list:
    result = []
    for p in target_dir.rglob('*.md'):
        parts = set(p.relative_to(target_dir).parts)
        if any(ex in parts for ex in exclude):
            continue
        if any(part.startswith('.') for part in p.relative_to(target_dir).parts):
            continue
        result.append(p)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description='批量为缺失id的Markdown文件添加id字段')
    parser.add_argument('--dir', required=True, help='目标目录（相对于项目根）')
    parser.add_argument('--write', action='store_true', help='写入模式（默认dry-run）')
    parser.add_argument('--exclude', nargs='*', default=['vendor', '.trae', 'node_modules', '__pycache__'],
                       help='排除目录')
    args = parser.parse_args(argv)

    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    target_dir = (project_root / args.dir).resolve()

    if not target_dir.exists():
        print(f'错误: 目录不存在: {target_dir}')
        sys.exit(1)

    dry_run = not args.write
    mode = '写入(write)' if not dry_run else '预览(dry-run)'
    print(f'项目根: {project_root}')
    print(f'扫描目录: {target_dir.relative_to(project_root)}')
    print(f'模式: {mode}')
    print()

    exclude = set(args.exclude)
    md_files = iter_md_files(target_dir, exclude)

    fixed = 0
    skipped = 0
    errors = 0

    for md_path in sorted(md_files):
        try:
            changed, msg = process_file(md_path, project_root, dry_run=dry_run)
            rel = md_path.relative_to(project_root).as_posix()
            if changed:
                print(f'  {rel}: {msg}')
                fixed += 1
            else:
                skipped += 1
        except Exception as e:
            rel = md_path.relative_to(project_root).as_posix()
            print(f'  [错误] {rel}: {e}')
            errors += 1

    print()
    print('=' * 60)
    print('统计汇总:')
    print(f'  总文件数: {len(md_files)}')
    action = '将添加' if dry_run else '已添加'
    print(f'  {action}id: {fixed}')
    print(f'  跳过(已有id或无frontmatter): {skipped}')
    print(f'  错误: {errors}')
    if errors > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
