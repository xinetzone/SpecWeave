#!/usr/bin/env python3
"""将 file:///<盘符>/spaces/SpecWeave/... 绝对链接转换为相对路径。

转换前置条件（缺一不可）：
- 目标确实存在且为文件：目标缺失或为目录时跳过并列入报告，
  避免把绝对引用"修复"成新的断链或目录链接；
- 位置不在代码围栏/行内代码内：示例片段不参与改写。

扫描范围排除 vendor/、projects/ 等 submodule 与临时区，复用共享常量
constants.EXCLUDED_DIRS，避免主仓脚本改动只读子模块。

读写按字节保真：不改动行尾（CRLF/LF）与 BOM。
"""

# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import os
import re
import sys
from pathlib import Path

from constants import EXCLUDED_DIRS
from lib.link_fixer import is_code_fence_context, parse_file_url

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FILE_URL_RE = re.compile(
    r'file:///([a-zA-Z]:/spaces/SpecWeave)([/\\][^)\s]*)?',
    re.IGNORECASE,
)

BOM = b"\xef\xbb\xbf"
# 共享常量之外的本地排除项：.meta 为元数据、external/playground 为 .gitignore 覆盖的本地目录
EXTRA_EXCLUDED_DIRS = {".meta", "external", "playground"}
SKIP_DIRS = EXCLUDED_DIRS | EXTRA_EXCLUDED_DIRS


def find_md_files(root: Path) -> list[Path]:
    """遍历根目录下的 Markdown 文件，剪枝排除目录（不进入 submodule 与临时区）。"""
    result = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(".md"):
                result.append(Path(dirpath) / name)
    return result


def convert_file_urls(content: str, md_path: Path, project_root: Path) -> tuple[str, int, list[tuple[str, str]]]:
    """转换单个文件中的 file:/// 链接。

    返回 (新内容, 转换处数, 跳过项列表)；跳过项为 (原链接, 跳过原因)。
    """
    parts: list[str] = []
    last = 0
    converted = 0
    skipped: list[tuple[str, str]] = []

    for m in FILE_URL_RE.finditer(content):
        if is_code_fence_context(content, m.start()):
            continue

        suffix = (m.group(2) or "").replace("\\", "/")
        path_part, anchor = parse_file_url(suffix)
        target = project_root / path_part.lstrip("/")

        if not target.is_file():
            skipped.append((m.group(0), "目标为目录" if target.is_dir() else "目标不存在"))
            continue

        try:
            rel_path = os.path.relpath(str(target.resolve()), str(md_path.parent.resolve()))
        except (OSError, ValueError):
            skipped.append((m.group(0), "相对路径计算失败"))
            continue

        parts.append(content[last:m.start()])
        parts.append(rel_path.replace(os.sep, "/") + anchor)
        last = m.end()
        converted += 1

    if converted == 0:
        return content, 0, skipped
    parts.append(content[last:])
    return "".join(parts), converted, skipped


def read_text_exact(path: Path) -> tuple[str, bool]:
    """按原样读取文本，返回 (文本, 是否有 BOM)；不做行尾归一化。"""
    raw = path.read_bytes()
    has_bom = raw.startswith(BOM)
    return raw.decode("utf-8-sig" if has_bom else "utf-8"), has_bom


def write_text_exact(path: Path, text: str, has_bom: bool) -> None:
    """按原样写回文本，保留原行尾与 BOM。"""
    data = text.encode("utf-8")
    path.write_bytes(BOM + data if has_bom else data)


def main():
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("=== DRY RUN mode (preview only) ===\n")

    md_files = find_md_files(PROJECT_ROOT)
    print(f"Found {len(md_files)} .md files\n")

    total_replacements = 0
    total_files = 0
    total_skipped: list[tuple[Path, str, str]] = []
    affected_files = []

    for md_path in md_files:
        try:
            content, has_bom = read_text_exact(md_path)
        except (OSError, UnicodeDecodeError) as e:
            print(f"[warn] read failed: {md_path} ({e})")
            continue

        new_content, count, skipped = convert_file_urls(content, md_path, PROJECT_ROOT)
        try:
            rel = md_path.relative_to(PROJECT_ROOT)
        except ValueError:
            rel = md_path

        if skipped:
            total_skipped.extend((rel, url, reason) for url, reason in skipped)
            for url, reason in skipped:
                print(f"  [skip] {rel}: {url} ({reason})")

        if count > 0:
            total_replacements += count
            total_files += 1
            affected_files.append((rel, count))
            if not dry_run:
                write_text_exact(md_path, new_content, has_bom)
            print(f"  {'[preview]' if dry_run else '[fix]'} {rel} ({count} occurrences)")

    print(f"\nTotal: {'preview' if dry_run else 'fix'} {total_replacements} file:/// links in {total_files} files")
    if total_skipped:
        print(f"Skipped: {len(total_skipped)}（目标缺失或为目录，需人工决定改指 README 或转为行内代码）")

    if dry_run and total_files > 0:
        print("\n=== Affected files (top 20) ===")
        for rel, count in affected_files[:20]:
            print(f"  {count:3d}  {rel}")


if __name__ == "__main__":
    main()
