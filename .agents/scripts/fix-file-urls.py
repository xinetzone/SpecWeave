#!/usr/bin/env python3
"""强制转换所有 file:///d:/spaces/SpecWeave/... 链接为相对路径。

本地运行时这些路径存在所以 check-links --fix 不会触发，
但 CI 中 Linux 路径解析不同会导致断链。
本脚本直接扫描并替换，不依赖路径是否存在。
"""
import re
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FILE_URL_RE = re.compile(
    r'file:///([a-zA-Z]:/spaces/SpecWeave)([/\\][^)\s]*)?',
    re.IGNORECASE,
)

EXCLUDED_DIRS = {".git", "vendor", ".venv", "__pycache__", "node_modules", ".temp",
                 "external", "playground", ".chaos", ".meta"}


def find_md_files(root: Path) -> list[Path]:
    result = []
    for entry in root.rglob("*.md"):
        try:
            if not entry.is_file():
                continue
            if any(ex in entry.parts for ex in EXCLUDED_DIRS):
                continue
            result.append(entry)
        except OSError:
            continue
    return result


def convert_file_urls(content: str, md_path: Path, project_root: Path) -> tuple[str, int]:
    count = 0

    def replace_match(m):
        nonlocal count
        suffix = m.group(2) or ""
        suffix_norm = suffix.replace("\\", "/")
        target_abs = project_root / suffix_norm.lstrip("/")
        try:
            target_abs = target_abs.resolve(strict=False)
        except (OSError, ValueError):
            return m.group(0)
        try:
            rel_path = os.path.relpath(str(target_abs), str(md_path.parent.resolve(strict=False)))
            rel_path = rel_path.replace("\\", "/")
        except (ValueError, OSError):
            return m.group(0)
        count += 1
        return rel_path

    new_content = FILE_URL_RE.sub(replace_match, content)
    return new_content, count


def main():
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("=== DRY RUN mode (preview only) ===\n")

    md_files = find_md_files(PROJECT_ROOT)
    print(f"Found {len(md_files)} .md files\n")

    total_replacements = 0
    total_files = 0
    affected_files = []

    for md_path in md_files:
        try:
            content = md_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            print(f"[warn] read failed: {md_path} ({e})")
            continue

        new_content, count = convert_file_urls(content, md_path, PROJECT_ROOT)
        if count > 0:
            total_replacements += count
            total_files += 1
            try:
                rel = md_path.relative_to(PROJECT_ROOT)
            except ValueError:
                rel = md_path
            affected_files.append((rel, count))
            if not dry_run:
                md_path.write_text(new_content, encoding="utf-8", newline="")
            print(f"  {'[preview]' if dry_run else '[fix]'} {rel} ({count} occurrences)")

    print(f"\nTotal: {'preview' if dry_run else 'fix'} {total_replacements} file:/// links in {total_files} files")

    if dry_run and total_files > 0:
        print("\n=== Affected files (top 20) ===")
        for rel, count in affected_files[:20]:
            print(f"  {count:3d}  {rel}")


if __name__ == "__main__":
    main()