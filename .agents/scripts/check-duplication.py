#!/usr/bin/env python3
"""自动化重复代码检测工具。

扫描 .agents/scripts/ 目录下的 Python 脚本，识别跨文件重复的代码块，
输出重复行数、位置和建议的共享库提取位置。

检测策略：
  1. 归一化代码（移除注释、空行、标准化空白）
  2. 使用滑动窗口 N 元语法（N 行）提取代码指纹
  3. 跨文件比对指纹，识别重复片段
  4. 合并相邻重复行，输出完整重复块

用法：
  python check-duplication.py                    # 默认阈值 10 行
  python check-duplication.py --threshold 5      # 阈值 5 行
  python check-duplication.py --json             # JSON 格式输出
  python check-duplication.py --path ../other    # 指定扫描路径
"""

import argparse
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
from lib.rules import load_rules, FalsePositiveRules

DEFAULT_THRESHOLD = 10
DEFAULT_WINDOW = 5

EXTRA_EXCLUDED_DIRS = {"lib", "tests", "config"}


def normalize_line(line: str) -> str:
    """归一化单行代码：移除注释、strip空白、标准化缩进。

    注释（#开头的整行注释和行内注释）被移除，空行返回空字符串。
    """
    stripped = line.strip()

    if not stripped:
        return ""

    if stripped.startswith("#"):
        return ""

    in_string = False
    string_char = None
    result = []
    i = 0
    while i < len(stripped):
        ch = stripped[i]
        if in_string:
            result.append(ch)
            if ch == "\\" and i + 1 < len(stripped):
                result.append(stripped[i + 1])
                i += 2
                continue
            if ch == string_char:
                in_string = False
                string_char = None
        else:
            if ch in ('"', "'"):
                in_string = True
                string_char = ch
                result.append(ch)
            elif ch == "#":
                break
            else:
                result.append(ch)
        i += 1

    normalized = "".join(result).strip()
    return normalized


def extract_normalized_lines(content: str, rules: FalsePositiveRules) -> list[tuple[int, str]]:
    """提取归一化代码行，返回 (原始行号, 归一化内容) 列表。

    空行、纯注释行和规则中定义的排除行被跳过。
    """
    result = []
    for line_no, raw_line in enumerate(content.splitlines(), start=1):
        norm = normalize_line(raw_line)
        if norm and not rules.is_excluded_line(norm):
            result.append((line_no, norm))
    return result


def find_duplicates(
    scripts_dir: Path,
    rules: FalsePositiveRules,
    threshold: int = DEFAULT_THRESHOLD,
    window: int = DEFAULT_WINDOW,
) -> list[DuplicateBlock]:
    """扫描目录下所有 Python 文件，查找跨文件重复代码块。

    Args:
        scripts_dir: 要扫描的脚本目录。
        rules: 误报过滤规则集。
        threshold: 最小重复行数阈值（低于此值不报告）。
        window: N 元语法窗口大小。

    Returns:
        DuplicateBlock 列表，按重复行数降序排列。
    """
    py_files = []
    for py_path in sorted(scripts_dir.rglob("*.py")):
        rel_parts = py_path.relative_to(scripts_dir).parts
        if any(part in EXTRA_EXCLUDED_DIRS for part in rel_parts):
            continue
        should_skip, reason = rules.should_skip_file(py_path, root_dir=scripts_dir)
        if should_skip:
            continue
        py_files.append(py_path)

    file_norm_lines: dict[Path, list[tuple[int, str]]] = {}
    for py_path in py_files:
        try:
            content = py_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        file_norm_lines[py_path] = extract_normalized_lines(content, rules)

    fingerprint_map: dict[str, list[tuple[Path, int]]] = {}
    for py_path, norm_lines in file_norm_lines.items():
        norms = [nl for _, nl in norm_lines]
        line_nos = [ln for ln, _ in norm_lines]
        for i in range(len(norms) - window + 1):
            window_lines = norms[i:i + window]
            fp = compute_fingerprint(window_lines)
            fingerprint_map.setdefault(fp, []).append((py_path, line_nos[i]))

    seeds: dict[str, list[tuple[Path, int, int]]] = {}
    for fp, locations in fingerprint_map.items():
        if len(locations) < 2:
            continue
        files = set(loc[0] for loc in locations)
        if len(files) < 2:
            continue
        for py_path, start_line in locations:
            seeds.setdefault(fp, []).append((py_path, start_line, window))

    def _py_block_filter(block: DuplicateBlock, fnl: dict) -> bool:
        occ0 = block.occurrences[0]
        block_norms = []
        for orig_ln, norm in fnl[occ0.file_path]:
            if occ0.start_line <= orig_ln <= occ0.end_line:
                block_norms.append(norm)
        is_excluded, _ = rules.is_excluded_block(block_norms)
        return is_excluded

    return process_duplicate_seeds(
        seeds, file_norm_lines, window,
        threshold=threshold,
        block_filter=_py_block_filter,
    )


def suggest_lib_location(normalized_preview: str) -> str:
    """根据重复代码内容建议应放入的共享库模块。"""
    preview_lower = normalized_preview.lower()

    if any(kw in preview_lower for kw in ["argparse", "add_argument", "parser", "print_", "header", "summary"]):
        return "建议提取到 lib/cli.py"
    if any(kw in preview_lower for kw in ["frontmatter", "toml", "extract_field", "parse_"]):
        return "建议提取到 lib/frontmatter.py"
    if any(kw in preview_lower for kw in ["link", "href", "fix_link", "relative"]):
        return "建议提取到 lib/link_fixer.py"
    if any(kw in preview_lower for kw in ["markdown", ".md", "title", "description", "find_markdown"]):
        return "建议提取到 lib/markdown.py"
    if any(kw in preview_lower for kw in ["spec", "checklist", "tasks"]):
        return "建议提取到 lib/spec/"
    if any(kw in preview_lower for kw in ["path", "resolve", "root", "__file__", "parent"]):
        return "建议提取到 lib/project.py"
    if any(kw in preview_lower for kw in ["pattern", "maturity", "domain", "layer"]):
        return "建议提取到 lib/patterns.py"
    return "建议新建 lib/ 模块或在对应模块中添加函数"


def main():
    args, threshold, window, project_root, scripts_dir = setup_duplication_main(
        "自动化重复代码检测工具：扫描Python脚本中的跨文件重复代码块",
        DEFAULT_THRESHOLD, DEFAULT_WINDOW, __file__,
    )
    if args.path:
        scripts_dir = args.path.resolve()

    rules = load_rules()

    try:
        rel_display = str(scripts_dir.relative_to(project_root))
    except ValueError:
        rel_display = str(scripts_dir)

    print_header(f"重复代码检测: {rel_display}")
    print(f"  阈值: {threshold} 行 | 窗口: {window} 行")
    print(f"  排除规则: config/false-positive-rules.toml ({len(rules.excluded_dir_names)}目录, {len(rules.excluded_file_names)}文件, {len(rules.file_marker_rules)}标记规则, {len(rules.block_filter_rules)}块过滤规则)")

    duplicates = find_duplicates(scripts_dir, rules, threshold=threshold, window=window)

    output_duplication_results(duplicates, project_root, scripts_dir, args, suggest_lib_location)

    if not args.json:
        if duplicates:
            print(f"\n  建议：将重复代码提取到共享库，降低维护成本。")
            print(f"  参考：.agents/scripts/lib/ 下的现有共享模块。")
        sys.exit(1 if duplicates else 0)


if __name__ == "__main__":
    main()