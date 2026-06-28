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
import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from lib.project import resolve_project_root, resolve_scripts_dir
from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, add_common_args

DEFAULT_THRESHOLD = 10
DEFAULT_WINDOW = 5
EXCLUDED_DIRS = {"__pycache__", "lib", ".temp", "vendor", ".git"}
EXCLUDED_FILES = {"__init__.py"}


@dataclass
class DuplicateBlock:
    """一个重复代码块。"""
    fingerprint: str
    line_count: int
    normalized_preview: str
    occurrences: list["Occurrence"] = field(default_factory=list)


@dataclass
class Occurrence:
    """重复代码块在单个文件中的出现位置。"""
    file_path: Path
    start_line: int
    end_line: int
    raw_preview: str


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


def extract_normalized_lines(content: str) -> list[tuple[int, str]]:
    """提取归一化代码行，返回 (原始行号, 归一化内容) 列表。

    空行和纯注释行被跳过。
    """
    result = []
    for line_no, raw_line in enumerate(content.splitlines(), start=1):
        norm = normalize_line(raw_line)
        if norm:
            result.append((line_no, norm))
    return result


def compute_fingerprint(lines: list[str]) -> str:
    """计算一组归一化代码行的指纹（SHA256 前16位）。"""
    joined = "\n".join(lines)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def find_duplicates(
    scripts_dir: Path,
    threshold: int = DEFAULT_THRESHOLD,
    window: int = DEFAULT_WINDOW,
) -> list[DuplicateBlock]:
    """扫描目录下所有 Python 文件，查找跨文件重复代码块。

    Args:
        scripts_dir: 要扫描的脚本目录。
        threshold: 最小重复行数阈值（低于此值不报告）。
        window: N 元语法窗口大小。

    Returns:
        DuplicateBlock 列表，按重复行数降序排列。
    """
    py_files = []
    for py_path in sorted(scripts_dir.rglob("*.py")):
        rel_parts = py_path.relative_to(scripts_dir).parts
        if any(part in EXCLUDED_DIRS for part in rel_parts):
            continue
        if py_path.name in EXCLUDED_FILES:
            continue
        py_files.append(py_path)

    file_norm_lines: dict[Path, list[tuple[int, str]]] = {}
    for py_path in py_files:
        try:
            content = py_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        file_norm_lines[py_path] = extract_normalized_lines(content)

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

    visited_fps: set[str] = set()
    duplicates: list[DuplicateBlock] = []

    for fp in sorted(seeds.keys(), key=lambda k: -len(seeds[k])):
        if fp in visited_fps:
            continue

        locations = seeds[fp]
        blocks = expand_duplicate_block(locations, file_norm_lines, visited_fps)
        if not blocks:
            continue

        block = DuplicateBlock(
            fingerprint=fp,
            line_count=blocks[0][2] - blocks[0][1] + 1,
            normalized_preview="",
        )

        preview_set = False
        for py_path, start_line, end_line in blocks:
            norm_lines = file_norm_lines[py_path]
            raw_content = py_path.read_text(encoding="utf-8")
            raw_lines = raw_content.splitlines()
            raw_preview_lines = []
            for ln in range(start_line, min(end_line + 1, start_line + 5)):
                if 1 <= ln <= len(raw_lines):
                    raw_preview_lines.append(raw_lines[ln - 1].rstrip())
            raw_preview = "\n".join(raw_preview_lines)
            if end_line - start_line + 1 > 5:
                raw_preview += "\n  ..."

            if not preview_set:
                norm_preview_lines = []
                for orig_ln, norm in norm_lines:
                    if start_line <= orig_ln <= end_line:
                        norm_preview_lines.append(norm)
                        if len(norm_preview_lines) >= 4:
                            break
                block.normalized_preview = "\n".join(norm_preview_lines)
                if end_line - start_line + 1 > 4:
                    block.normalized_preview += "\n  ..."
                preview_set = True

            block.occurrences.append(Occurrence(
                file_path=py_path,
                start_line=start_line,
                end_line=end_line,
                raw_preview=raw_preview,
            ))

        if block.line_count >= threshold:
            duplicates.append(block)

    duplicates.sort(key=lambda b: (-b.line_count, len(b.occurrences)))
    return duplicates


def expand_duplicate_block(
    seed_locations: list[tuple[Path, int, int]],
    file_norm_lines: dict[Path, list[tuple[int, str]]],
    visited_fps: set[str],
) -> list[tuple[Path, int, int]]:
    """从种子窗口出发，向前后扩展到最大重复块。

    尝试在每个文件中向前/向后扩展归一化行，只要所有文件的对应行归一化后相等就继续扩展。
    返回每个文件中的 (path, start_line, end_line)。
    """
    locations = [(path, start_ln, start_ln + win - 1) for path, start_ln, win in seed_locations]

    if not locations:
        return []

    file_line_map: dict[Path, dict[int, str]] = {}
    file_orig_lines: dict[Path, list[int]] = {}
    for path in file_norm_lines:
        line_map = {}
        orig_list = []
        for orig_ln, norm in file_norm_lines[path]:
            line_map[orig_ln] = norm
            orig_list.append(orig_ln)
        file_line_map[path] = line_map
        file_orig_lines[path] = orig_list

    def get_prev_line(path: Path, current_ln: int) -> Optional[tuple[int, str]]:
        origs = file_orig_lines[path]
        try:
            idx = origs.index(current_ln)
        except ValueError:
            return None
        if idx == 0:
            return None
        prev_orig = origs[idx - 1]
        return prev_orig, file_line_map[path][prev_orig]

    def get_next_line(path: Path, current_ln: int) -> Optional[tuple[int, str]]:
        origs = file_orig_lines[path]
        try:
            idx = origs.index(current_ln)
        except ValueError:
            return None
        if idx >= len(origs) - 1:
            return None
        next_orig = origs[idx + 1]
        return next_orig, file_line_map[path][next_orig]

    while True:
        can_expand_back = True
        prev_norms = []
        prev_locs = []
        for path, start_ln, _ in locations:
            prev = get_prev_line(path, start_ln)
            if prev is None:
                can_expand_back = False
                break
            prev_orig, prev_norm = prev
            prev_norms.append(prev_norm)
            prev_locs.append((path, prev_orig))

        if can_expand_back and len(set(prev_norms)) == 1:
            new_locations = []
            for i, (path, start_ln, end_ln) in enumerate(locations):
                new_locations.append((path, prev_locs[i][1], end_ln))
            locations = new_locations
        else:
            break

    while True:
        can_expand_fwd = True
        next_norms = []
        next_locs = []
        for path, _, end_ln in locations:
            nxt = get_next_line(path, end_ln)
            if nxt is None:
                can_expand_fwd = False
                break
            next_orig, next_norm = nxt
            next_norms.append(next_norm)
            next_locs.append((path, next_orig))

        if can_expand_fwd and len(set(next_norms)) == 1:
            new_locations = []
            for i, (path, start_ln, end_ln) in enumerate(locations):
                new_locations.append((path, start_ln, next_locs[i][1]))
            locations = new_locations
        else:
            break

    total_lines = locations[0][2] - locations[0][1] + 1
    if total_lines >= DEFAULT_WINDOW:
        for path, start_ln, end_ln in locations:
            norms = []
            for orig_ln, norm in file_norm_lines[path]:
                if start_ln <= orig_ln <= end_ln:
                    norms.append(norm)
            if len(norms) >= DEFAULT_WINDOW:
                for i in range(len(norms) - DEFAULT_WINDOW + 1):
                    sub_fp = compute_fingerprint(norms[i:i + DEFAULT_WINDOW])
                    visited_fps.add(sub_fp)

    return locations


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
    parser = argparse.ArgumentParser(
        description="自动化重复代码检测工具：扫描Python脚本中的跨文件重复代码块"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=int,
        default=DEFAULT_THRESHOLD,
        help=f"重复行数阈值（默认 {DEFAULT_THRESHOLD}，低于此值不报告）",
    )
    parser.add_argument(
        "--window", "-w",
        type=int,
        default=DEFAULT_WINDOW,
        help=f"N元语法窗口大小（默认 {DEFAULT_WINDOW} 行）",
    )
    add_common_args(parser)
    args = parser.parse_args()

    project_root = resolve_project_root(__file__)
    scripts_dir = resolve_scripts_dir(__file__)
    if args.path:
        scripts_dir = args.path.resolve()

    try:
        rel_display = str(scripts_dir.relative_to(project_root))
    except ValueError:
        rel_display = str(scripts_dir)

    print_header(f"重复代码检测: {rel_display}")
    print(f"  阈值: {args.threshold} 行 | 窗口: {args.window} 行")
    print(f"  排除目录: {', '.join(sorted(EXCLUDED_DIRS))}")

    duplicates = find_duplicates(scripts_dir, threshold=args.threshold, window=args.window)

    total_duplicate_lines = 0
    files_affected: set[str] = set()

    if args.json:
        result = {
            "threshold": args.threshold,
            "window": args.window,
            "scan_dir": str(scripts_dir),
            "duplicate_count": len(duplicates),
            "duplicates": [],
        }
        for block in duplicates:
            dup_info = {
                "fingerprint": block.fingerprint,
                "line_count": block.line_count,
                "normalized_preview": block.normalized_preview,
                "suggested_location": suggest_lib_location(block.normalized_preview),
                "occurrences": [],
            }
            for occ in block.occurrences:
                dup_info["occurrences"].append({
                    "file": str(occ.file_path),
                    "start_line": occ.start_line,
                    "end_line": occ.end_line,
                })
                total_duplicate_lines += block.line_count
                files_affected.add(str(occ.file_path))
            result["duplicates"].append(dup_info)
        result["total_duplicate_lines"] = total_duplicate_lines
        result["files_affected"] = len(files_affected)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if not duplicates:
        print_pass(f"通过 — 未发现超过 {args.threshold} 行的跨文件重复代码块")
        print_summary(pass_count=1, warn_count=0, error_count=0)
        return

    print_warn(f"发现 {len(duplicates)} 处重复代码块:")
    print()

    for i, block in enumerate(duplicates, 1):
        print(f"  [{i}] 重复 {block.line_count} 行 (指纹: {block.fingerprint})")
        suggestion = suggest_lib_location(block.normalized_preview)
        print(f"      {suggestion}")
        for occ in block.occurrences:
            try:
                rel_path = occ.file_path.relative_to(project_root)
            except ValueError:
                rel_path = occ.file_path
            print(f"      {rel_path}:{occ.start_line}-{occ.end_line}")
            total_duplicate_lines += block.line_count
            files_affected.add(str(rel_path))
        print()

    print(f"  扫描目录: {rel_display}")
    print(f"  受影响文件: {len(files_affected)} 个")
    print(f"  累计重复行数: 约 {total_duplicate_lines} 行")
    print()
    print_summary(pass_count=0, warn_count=len(duplicates), error_count=0)

    print(f"\n  建议：将重复代码提取到共享库，降低维护成本。")
    print(f"  参考：.agents/scripts/lib/ 下的现有共享模块。")
    sys.exit(1 if duplicates else 0)


if __name__ == "__main__":
    main()
