#!/usr/bin/env python3
"""Phase 7: 批量修复63个内联断链。

修复策略：
  1. .chaos/ 路径 → 外部项目引用，转为行内代码
  2. file:///d:/AI/ 绝对路径 → 跨项目引用，转为行内代码
  3. 根路径 /zh-Hans-CN/、/codex/ → 转为完整URL
  4. 同目录缺失文件 → 转为行内代码
  5. 相对路径错误 → 修复路径
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def parse_broken_links(log_file: Path) -> list[dict]:
    """解析 check-links 输出，提取断链信息。"""
    entries = []
    pattern = re.compile(
        r'\[(.+?):(\d+)\]\s+(.+?)\s+->\s+(.+?)\s+\(文件不存在:'
    )
    with open(log_file, encoding='utf-8') as f:
        for line in f:
            m = pattern.search(line)
            if m:
                entries.append({
                    'file': m.group(1).replace('\\', '/'),
                    'line': int(m.group(2)),
                    'display': m.group(3).strip(),
                    'target': m.group(4).strip(),
                })
    return entries


def fix_link_to_inline_code(content: str, target_path: str) -> tuple[str, bool]:
    """将包含 target_path 的 markdown 链接转为行内代码。

    匹配 [text](target_path) 或 [text](target_path#anchor) 格式。
    """
    escaped = re.escape(target_path)
    pattern = re.compile(
        r'\[([^\]]*)\]\(' + escaped + r'[^)]*\)'
    )
    new_content, count = pattern.subn(r'`\1`', content)
    return new_content, count > 0


def fix_root_path_links(content: str) -> tuple[str, int]:
    """将根路径 /zh-Hans-CN/ 和 /codex/ 转为完整URL。"""
    count = 0
    # /zh-Hans-CN/codex/for-work → https://platform.openai.com/zh-Hans-CN/codex/for-work
    new_content, n = re.subn(
        r'\[([^\]]*)\]\((/zh-Hans-CN/[^)]+)\)',
        r'[\1](https://platform.openai.com\2)',
        content
    )
    count += n
    # /codex/pricing/ → https://platform.openai.com/codex/pricing/
    new_content, n = re.subn(
        r'\[([^\]]*)\]\((/codex/[^)]+)\)',
        r'[\1](https://platform.openai.com\2)',
        new_content
    )
    count += n
    return new_content, count


def fix_relative_path_error(content: str) -> tuple[str, int]:
    """修复相对路径错误：../../../../patterns/ → ../../../../../patterns/"""
    new_content, count = re.subn(
        r'\]\(\.\./\.\./\.\./\.\./patterns/',
        r'](../../../../../patterns/',
        content
    )
    return new_content, count


def categorize_target(target: str) -> str:
    """分类断链目标路径。"""
    if '.chaos/' in target:
        return 'chaos'
    if target.startswith('file:///d:/AI/') or target.startswith('file:///d:/ai/'):
        return 'cross_project'
    if target.startswith('/zh-Hans-CN/') or target.startswith('/codex/'):
        return 'root_path'
    if target in ('mini_init.md', 'session-leader.md', 'interop.md',
                   './images/login-screenshot.png', 'images/workflow.png'):
        return 'missing_local'
    return 'other'


def process_file(file_rel_path: str, entries: list[dict]) -> tuple[int, list[str]]:
    """处理单个文件的所有断链。"""
    md_path = PROJECT_ROOT / 'docs' / file_rel_path
    if not md_path.exists():
        return 0, [f'文件不存在: {md_path}']

    content = md_path.read_text(encoding='utf-8')
    original = content
    fixes = []
    fix_count = 0

    # 1. 修复根路径链接
    content, n = fix_root_path_links(content)
    if n:
        fix_count += n
        fixes.append(f'根路径转URL: {n}个')

    # 2. 修复相对路径错误
    content, n = fix_relative_path_error(content)
    if n:
        fix_count += n
        fixes.append(f'相对路径修复: {n}个')

    # 3. 修复 .chaos/ 和 file:///d:/AI/ 路径 → 转为行内代码
    for entry in entries:
        cat = categorize_target(entry['target'])
        if cat in ('chaos', 'cross_project', 'missing_local'):
            content, fixed = fix_link_to_inline_code(content, entry['target'])
            if fixed:
                fix_count += 1
                if cat == 'chaos':
                    fixes.append(f'.chaos/路径转代码: {entry["display"][:30]}')
                elif cat == 'cross_project':
                    fixes.append(f'跨项目路径转代码: {entry["display"][:30]}')
                else:
                    fixes.append(f'缺失文件转代码: {entry["display"][:30]}')

    if content != original:
        md_path.write_text(content, encoding='utf-8', newline='')
        return fix_count, fixes
    return 0, ['无修改（未找到匹配的链接）']


def main():
    log_file = PROJECT_ROOT / '.trae' / 'documents' / 'broken-links-phase7.txt'
    if not log_file.exists():
        print(f'错误: 断链日志文件不存在: {log_file}')
        sys.exit(1)

    entries = parse_broken_links(log_file)
    print(f'解析到 {len(entries)} 个断链')

    # 按文件分组
    by_file: dict[str, list[dict]] = {}
    for e in entries:
        by_file.setdefault(e['file'], []).append(e)

    print(f'涉及 {len(by_file)} 个文件\n')

    total_fixed = 0
    total_files = 0
    for file_path, file_entries in sorted(by_file.items()):
        count, fixes = process_file(file_path, file_entries)
        if count > 0:
            total_fixed += count
            total_files += 1
            print(f'✅ {file_path} ({count}个修复)')
            for f in fixes[:3]:
                print(f'   - {f}')
        else:
            print(f'⚠️  {file_path} ({fixes[0]})')

    print(f'\n总计: 修复 {total_fixed} 个断链，涉及 {total_files} 个文件')


if __name__ == '__main__':
    main()
