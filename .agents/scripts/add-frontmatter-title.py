#!/usr/bin/env python3
"""
批量为Markdown文件的YAML frontmatter添加title字段（从H1提取）。

遵循4字段frontmatter规范：id/title/source/x-toml-ref
title字段插入在id之后、source之前。

用法：
    python add-frontmatter-title.py --dir docs/retrospective/reports/ [--dry-run] [--write]
"""

import argparse
import re
import sys
from pathlib import Path


FM_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
H1_PATTERN = re.compile(r'^#\s+(.+?)\s*$', re.MULTILINE)


def extract_h1_title(content: str) -> str | None:
    """从Markdown内容中提取第一个H1标题文本"""
    match = H1_PATTERN.search(content)
    if match:
        title = match.group(1).strip()
        title = re.sub(r'\s+', ' ', title)
        return title
    return None


def parse_frontmatter(fm_text: str) -> dict:
    """简单解析YAML frontmatter为有序字典（保留注释和顺序）"""
    result = {}
    for line in fm_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            result[key] = value
    return result


def add_title_to_frontmatter(content: str, title: str) -> tuple[str, bool]:
    """
    在frontmatter中添加title字段（插入在id之后、source/x-toml-ref之前）。
    返回 (新内容, 是否修改)。
    """
    fm_match = FM_PATTERN.match(content)
    if not fm_match:
        return content, False

    fm_text = fm_match.group(1)
    fm_start = fm_match.start()
    fm_end = fm_match.end()

    existing = parse_frontmatter(fm_text)
    if 'title' in existing:
        return content, False

    lines = fm_text.split('\n')
    new_lines = []
    inserted = False

    for line in lines:
        new_lines.append(line)
        stripped = line.strip()
        if not inserted and (stripped.startswith('id:') or stripped.startswith('id :')):
            indent_match = re.match(r'^(\s*)', line)
            indent = indent_match.group(1) if indent_match else ''
            escaped_title = title.replace('"', '\\"')
            new_lines.append(f'{indent}title: "{escaped_title}"')
            inserted = True

    if not inserted:
        new_lines.append(f'title: "{title}"')
        inserted = True

    new_fm_text = '\n'.join(new_lines)
    new_content = content[:fm_start] + '---\n' + new_fm_text + '\n---\n' + content[fm_end:]
    return new_content, True


def process_file(filepath: Path, dry_run: bool = True) -> dict:
    """处理单个文件，返回处理结果"""
    result = {
        'file': str(filepath),
        'status': 'skip',
        'title': None,
        'reason': None,
    }

    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        result['status'] = 'error'
        result['reason'] = f'读取失败: {e}'
        return result

    fm_match = FM_PATTERN.match(content)
    if not fm_match:
        result['status'] = 'skip'
        result['reason'] = '无frontmatter'
        return result

    existing = parse_frontmatter(fm_match.group(1))
    if 'title' in existing:
        result['status'] = 'skip'
        result['reason'] = '已有title字段'
        return result

    title = extract_h1_title(content)
    if not title:
        result['status'] = 'skip'
        result['reason'] = '未找到H1标题'
        return result

    result['title'] = title

    new_content, modified = add_title_to_frontmatter(content, title)
    if not modified:
        result['status'] = 'skip'
        result['reason'] = '无需修改'
        return result

    if dry_run:
        result['status'] = 'would_modify'
    else:
        filepath.write_text(new_content, encoding='utf-8')
        result['status'] = 'modified'

    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description='批量为frontmatter添加title字段')
    parser.add_argument('--dir', required=True, help='目标目录')
    parser.add_argument('--dry-run', action='store_true', help='仅预览变更，不写入')
    parser.add_argument('--write', action='store_true', help='实际写入变更')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    args = parser.parse_args(argv)

    if not args.dry_run and not args.write:
        print("⚠️  请指定 --dry-run（预览）或 --write（写入）")
        sys.exit(1)

    target_dir = Path(args.dir)
    if not target_dir.is_dir():
        print(f"❌ 目录不存在: {target_dir}")
        sys.exit(1)

    md_files = list(target_dir.rglob('*.md'))
    print(f"扫描目录: {target_dir}")
    print(f"找到 {len(md_files)} 个Markdown文件")
    print(f"模式: {'预览(dry-run)' if args.dry_run else '写入(write)'}\n")

    stats = {
        'total': len(md_files),
        'modified': 0,
        'would_modify': 0,
        'skip_no_fm': 0,
        'skip_has_title': 0,
        'skip_no_h1': 0,
        'error': 0,
    }

    modified_files = []

    for fpath in sorted(md_files):
        rel = fpath.relative_to(target_dir.parent.parent.parent if 'docs' in str(target_dir) else target_dir)
        result = process_file(fpath, dry_run=args.dry_run)

        if result['status'] == 'modified':
            stats['modified'] += 1
            modified_files.append((rel, result['title']))
            print(f"  ✅ 已修改: {rel}")
            print(f"     title: {result['title']}")
        elif result['status'] == 'would_modify':
            stats['would_modify'] += 1
            modified_files.append((rel, result['title']))
            if args.verbose:
                print(f"  📝 将添加: {rel}")
                print(f"     title: {result['title']}")
        elif result['status'] == 'error':
            stats['error'] += 1
            print(f"  ❌ 错误: {rel} - {result['reason']}")
        else:
            if args.verbose:
                print(f"  ⏭️  跳过: {rel} ({result['reason']})")
            if result['reason'] == '无frontmatter':
                stats['skip_no_fm'] += 1
            elif result['reason'] == '已有title字段':
                stats['skip_has_title'] += 1
            elif result['reason'] == '未找到H1标题':
                stats['skip_no_h1'] += 1

    print(f"\n{'='*60}")
    print(f"统计汇总:")
    print(f"  总文件数: {stats['total']}")
    if args.dry_run:
        print(f"  将修改: {stats['would_modify']}")
    else:
        print(f"  已修改: {stats['modified']}")
    print(f"  跳过(已有title): {stats['skip_has_title']}")
    print(f"  跳过(无frontmatter): {stats['skip_no_fm']}")
    print(f"  跳过(无H1标题): {stats['skip_no_h1']}")
    print(f"  错误: {stats['error']}")

    if modified_files and args.verbose:
        print(f"\n将被修改/已修改的文件列表:")
        for rel, title in modified_files:
            print(f"  {rel}")
            print(f"    → title: {title}")


if __name__ == '__main__':
    main()
