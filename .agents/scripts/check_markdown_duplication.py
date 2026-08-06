#!/usr/bin/env python3
"""Markdown 文档重复内容检测工具。

扫描指定目录下的 Markdown 报告，识别跨文件重复的内容块，
输出重复行数、位置和归并建议。

检测策略：
  1. 归一化 Markdown（移除 frontmatter、代码块、标题/列表标记、格式符号）
  2. 使用滑动窗口 N 元语法（N 行）提取内容指纹
  3. 跨文件比对指纹，识别重复片段
  4. 合并相邻重复行，输出完整重复块

用法：
  python check_markdown_duplication.py                    # 默认阈值 15 行
  python check_markdown_duplication.py --threshold 5      # 阈值 5 行
  python check_markdown_duplication.py --json             # JSON 格式输出
  python check_markdown_duplication.py --path ../docs     # 指定扫描路径
"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import re
import sys
from pathlib import Path

from lib.duplication import (
    DuplicateBlock,
    Occurrence,
    compute_fingerprint,
    process_duplicate_seeds,
)
from lib.project import resolve_project_root, resolve_scripts_dir
from lib.cli import (
    print_pass,
    print_warn,
    print_error,
    print_header,
    print_summary,
    add_common_args,
    add_threshold_window_args,
    output_duplication_results,
    setup_safe_output,
    setup_duplication_main,
)

DEFAULT_THRESHOLD = 15
DEFAULT_WINDOW = 3
DEFAULT_SCAN_PATH = "../docs/retrospective/reports/insight-extraction"

EXTRA_EXCLUDED_FILES = {"README.md"}
EXTRA_EXCLUDED_PREFIXES = ("_",)


def strip_frontmatter(content: str) -> str:
    if not content.startswith("---"):
        return content
    lines = content.split("\n", 2)
    if len(lines) < 2:
        return content
    if lines[0] != "---":
        return content
    end_idx = content.find("\n---", 4)
    if end_idx == -1:
        return content
    return content[end_idx + 5:]


def is_code_fence(line: str) -> bool:
    stripped = line.lstrip()
    return stripped.startswith("```")


def normalize_markdown_line(line: str) -> str:
    stripped = line.strip()

    if not stripped:
        return ""

    full_width_space = "\u3000"
    stripped = stripped.replace(full_width_space, " ")

    heading_match = re.match(r"^#{1,6}\s+(.*)", stripped)
    if heading_match:
        stripped = heading_match.group(1)

    list_match = re.match(r"^[\-\*\+]\s+(.*)", stripped)
    if list_match:
        stripped = list_match.group(1)

    num_list_match = re.match(r"^\d+\.\s+(.*)", stripped)
    if num_list_match:
        stripped = num_list_match.group(1)

    stripped = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", stripped)
    stripped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", stripped)
    stripped = re.sub(r"\*\*([^*]+)\*\*", r"\1", stripped)
    stripped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", stripped)
    stripped = re.sub(r"__([^_]+)__", r"\1", stripped)
    stripped = re.sub(r"(?<!_)_([^_]+)_(?!_)", r"\1", stripped)
    stripped = re.sub(r"`([^`]+)`", r"\1", stripped)
    stripped = re.sub(r"<[^>]+>", "", stripped)

    if re.match(r"^[\=\-]+$", stripped):
        return ""

    if stripped.startswith("|") and stripped.endswith("|"):
        return ""

    return stripped.strip()


def extract_normalized_md_lines(content: str) -> list[tuple[int, str]]:
    content = strip_frontmatter(content)
    result = []
    in_code_block = False

    for line_no, raw_line in enumerate(content.splitlines(), start=1):
        if is_code_fence(raw_line):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        norm = normalize_markdown_line(raw_line)
        if norm:
            result.append((line_no, norm))

    return result


def find_markdown_duplicates(
    dir_path: Path,
    threshold: int = DEFAULT_THRESHOLD,
    window: int = DEFAULT_WINDOW,
    exclude_dirs: set[str] | None = None,
) -> list[DuplicateBlock]:
    if exclude_dirs is None:
        exclude_dirs = set()

    md_files = []
    for md_path in sorted(dir_path.rglob("*.md")):
        rel_parts = md_path.relative_to(dir_path).parts
        if any(part in exclude_dirs for part in rel_parts):
            continue
        if md_path.name in EXTRA_EXCLUDED_FILES:
            continue
        if any(md_path.name.startswith(prefix) for prefix in EXTRA_EXCLUDED_PREFIXES):
            continue
        md_files.append(md_path)

    file_norm_lines: dict[Path, list[tuple[int, str]]] = {}
    for md_path in md_files:
        try:
            content = md_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        file_norm_lines[md_path] = extract_normalized_md_lines(content)

    fingerprint_map: dict[str, list[tuple[Path, int]]] = {}
    for md_path, norm_lines in file_norm_lines.items():
        norms = [nl for _, nl in norm_lines]
        line_nos = [ln for ln, _ in norm_lines]
        for i in range(len(norms) - window + 1):
            window_lines = norms[i:i + window]
            fp = compute_fingerprint(window_lines)
            fingerprint_map.setdefault(fp, []).append((md_path, line_nos[i]))

    seeds: dict[str, list[tuple[Path, int, int]]] = {}
    for fp, locations in fingerprint_map.items():
        if len(locations) < 2:
            continue
        files = set(loc[0] for loc in locations)
        if len(files) < 2:
            continue
        for md_path, start_line in locations:
            seeds.setdefault(fp, []).append((md_path, start_line, window))

    return process_duplicate_seeds(
        seeds, file_norm_lines, window,
        threshold=threshold,
    )


def suggest_merge_action(normalized_preview: str) -> str:
    preview_lower = normalized_preview.lower()
    if any(kw in preview_lower for kw in ["背景", "问题", "根因", "原因"]):
        return "建议合并为通用问题分析模板或提取到公共方法论章节"
    if any(kw in preview_lower for kw in ["建议", "改进", "措施", "行动"]):
        return "建议合并为通用改进措施库"
    if any(kw in preview_lower for kw in ["总结", "结论", "经验", "教训"]):
        return "建议合并为经验教训库"
    if any(kw in preview_lower for kw in ["数据", "指标", "统计"]):
        return "建议统一数据口径，提取到公共数据章节"
    return "建议审查重复内容，考虑合并或抽象为共享模板"


def main():
    args, threshold, window, project_root, scripts_dir = setup_duplication_main(
        "Markdown 文档重复内容检测工具：扫描 Markdown 报告中的跨文件重复内容",
        DEFAULT_THRESHOLD, DEFAULT_WINDOW, __file__,
    )
    if args.path:
        scan_dir = args.path.resolve()
    else:
        scan_dir = (scripts_dir / DEFAULT_SCAN_PATH).resolve()

    try:
        rel_display = str(scan_dir.relative_to(project_root))
    except ValueError:
        rel_display = str(scan_dir)

    print_header(f"Markdown 文档重复检测: {rel_display}")
    print(f"  阈值: {threshold} 行 | 窗口: {window} 行")
    print(f"  排除文件: README.md, _*.md 私有文件")

    duplicates = find_markdown_duplicates(scan_dir, threshold=threshold, window=window)

    output_duplication_results(duplicates, project_root, scan_dir, args, suggest_merge_action)

    if not args.json:
        if duplicates:
            print(f"\n  建议：审查重复内容，考虑合并或抽象为共享模板以降低维护成本。")
        sys.exit(1 if duplicates else 0)


if __name__ == "__main__":
    main()
