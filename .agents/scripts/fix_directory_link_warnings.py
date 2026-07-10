#!/usr/bin/env python3
"""批量修复目录链接警告：dir/ → dir/README.md

仅修复目录内有 README.md 的链接（786个），
跳过目录内无 README.md 的链接（63个）。
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = PROJECT_ROOT / 'docs'


def parse_dir_warnings(log_file: Path) -> dict[str, list[str]]:
    """解析目录链接警告，返回 {file: [target_path, ...]}。

    仅解析"应链接到 X/README.md"（目录有README.md）的警告。
    """
    by_file: dict[str, list[str]] = {}
    pattern = re.compile(
        r'\[(.+?):(\d+)\]\s+.+?\s+->\s+(.+?)\s+'
        r'\(链接到目录而非文件（应链接到'
    )
    with open(log_file, encoding='utf-8') as f:
        for line in f:
            m = pattern.search(line)
            if m:
                file_path = m.group(1).replace('\\', '/')
                target = m.group(3).strip()
                by_file.setdefault(file_path, []).append(target)
    return by_file


def resolve_md_path(file_path: str) -> Path | None:
    """尝试在 docs/ 和项目根目录下找到 md 文件。"""
    candidates = [
        DOCS_DIR / file_path,
        PROJECT_ROOT / file_path,
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            return p
    return None


def fix_directory_links(md_path: Path, targets: list[str]) -> int:
    """修复文件中的目录链接，返回修复数量。"""
    content = md_path.read_text(encoding='utf-8')
    original = content
    fix_count = 0

    for target in targets:
        base = target.rstrip('/')
        if not base:
            continue

        escaped = re.escape(base)
        # 匹配 [text](base) 或 [text](base/) — 不匹配 [text](base/file)
        pattern = re.compile(
            r'(\[([^\]]*)\]\()' + escaped + r'/?\)'
        )
        new_content, n = pattern.subn(
            lambda m: m.group(1) + base + '/README.md)',
            content
        )
        if n > 0:
            content = new_content
            fix_count += n

    if content != original:
        md_path.write_text(content, encoding='utf-8', newline='')

    return fix_count


def main():
    dry_run = '--dry-run' in sys.argv

    log_file = PROJECT_ROOT / '.trae' / 'documents' / 'dir-warnings.txt'
    if not log_file.exists():
        print(f'错误: 警告日志文件不存在: {log_file}')
        sys.exit(1)

    by_file = parse_dir_warnings(log_file)
    total_targets = sum(len(v) for v in by_file.values())
    print(f'解析到 {total_targets} 个可修复目录链接，涉及 {len(by_file)} 个文件\n')

    if dry_run:
        print('=== DRY RUN 模式（仅预览，不修改文件）===\n')

    total_fixed = 0
    total_files = 0
    not_found = []

    for file_path, targets in sorted(by_file.items()):
        md_path = resolve_md_path(file_path)
        if md_path is None:
            not_found.append(file_path)
            continue

        if dry_run:
            # Dry run: read but don't write
            content = md_path.read_text(encoding='utf-8')
            count = 0
            for target in targets:
                base = target.rstrip('/')
                if not base:
                    continue
                escaped = re.escape(base)
                pattern = re.compile(
                    r'(\[([^\]]*)\]\()' + escaped + r'/?\)'
                )
                _, n = pattern.subn('', content)
                count += n
            if count > 0:
                total_fixed += count
                total_files += 1
                print(f'  {file_path} ({count}个)')
        else:
            count = fix_directory_links(md_path, targets)
            if count > 0:
                total_fixed += count
                total_files += 1
                if count <= 3:
                    print(f'✅ {file_path} ({count}个)')
                else:
                    print(f'✅ {file_path} ({count}个)')

    print(f'\n总计: 修复 {total_fixed} 个目录链接，涉及 {total_files} 个文件')
    if not_found:
        print(f'未找到文件: {len(not_found)} 个')
        for f in not_found[:5]:
            print(f'  - {f}')


if __name__ == '__main__':
    main()
