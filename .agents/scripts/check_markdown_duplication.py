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

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from lib.project import resolve_project_root, resolve_scripts_dir
from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, add_common_args, setup_safe_output

DEFAULT_THRESHOLD = 15
DEFAULT_WINDOW = 3
DEFAULT_SCAN_PATH = "../docs/retrospective/reports/insight-extraction"

EXTRA_EXCLUDED_FILES = {"README.md"}
EXTRA_EXCLUDED_PREFIXES = ("_",)


@dataclass
class DuplicateBlock:
    fingerprint: str
    line_count: int
    normalized_preview: str
    occurrences: list["Occurrence"] = field(default_factory=list)


@dataclass
class Occurrence:
    file_path: Path
    start_line: int
    end_line: int
    raw_preview: str


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


def compute_fingerprint(lines: list[str]) -> str:
    joined = "\n".join(lines)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def expand_duplicate_block(
    seed_locations: list[tuple[Path, int, int]],
    file_norm_lines: dict[Path, list[tuple[int, str]]],
    visited_fps: set[str],
    window: int,
) -> list[tuple[Path, int, int]]:
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

    def get_prev_line(path: Path, current_ln: int) -> tuple[int, str] | None:
        origs = file_orig_lines[path]
        try:
            idx = origs.index(current_ln)
        except ValueError:
            return None
        if idx == 0:
            return None
        prev_orig = origs[idx - 1]
        return prev_orig, file_line_map[path][prev_orig]

    def get_next_line(path: Path, current_ln: int) -> tuple[int, str] | None:
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
    if total_lines >= window:
        for path, start_ln, end_ln in locations:
            norms = []
            for orig_ln, norm in file_norm_lines[path]:
                if start_ln <= orig_ln <= end_ln:
                    norms.append(norm)
            if len(norms) >= window:
                for i in range(len(norms) - window + 1):
                    sub_fp = compute_fingerprint(norms[i:i + window])
                    visited_fps.add(sub_fp)

    return locations


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

    visited_fps: set[str] = set()
    duplicates: list[DuplicateBlock] = []

    for fp in sorted(seeds.keys(), key=lambda k: -len(seeds[k])):
        if fp in visited_fps:
            continue

        locations = seeds[fp]
        blocks = expand_duplicate_block(locations, file_norm_lines, visited_fps, window)
        if not blocks:
            continue

        block = DuplicateBlock(
            fingerprint=fp,
            line_count=blocks[0][2] - blocks[0][1] + 1,
            normalized_preview="",
        )

        preview_set = False
        for md_path, start_line, end_line in blocks:
            norm_lines = file_norm_lines[md_path]
            try:
                raw_content = md_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                raw_content = ""
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
                file_path=md_path,
                start_line=start_line,
                end_line=end_line,
                raw_preview=raw_preview,
            ))

        if block.line_count >= threshold:
            duplicates.append(block)

    duplicates.sort(key=lambda b: (-b.line_count, len(b.occurrences)))
    return duplicates


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
    setup_safe_output()
    parser = argparse.ArgumentParser(
        description="Markdown 文档重复内容检测工具：扫描 Markdown 报告中的跨文件重复内容"
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
        scan_dir = args.path.resolve()
    else:
        scan_dir = (scripts_dir / DEFAULT_SCAN_PATH).resolve()

    try:
        rel_display = str(scan_dir.relative_to(project_root))
    except ValueError:
        rel_display = str(scan_dir)

    print_header(f"Markdown 文档重复检测: {rel_display}")
    print(f"  阈值: {args.threshold} 行 | 窗口: {args.window} 行")
    print(f"  排除文件: README.md, _*.md 私有文件")

    duplicates = find_markdown_duplicates(scan_dir, threshold=args.threshold, window=args.window)

    total_duplicate_lines = 0
    files_affected: set[str] = set()

    if args.json:
        result = {
            "threshold": args.threshold,
            "window": args.window,
            "scan_dir": str(scan_dir),
            "duplicate_count": len(duplicates),
            "duplicates": [],
        }
        for block in duplicates:
            dup_info = {
                "fingerprint": block.fingerprint,
                "line_count": block.line_count,
                "normalized_preview": block.normalized_preview,
                "suggested_action": suggest_merge_action(block.normalized_preview),
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
        sys.exit(1 if duplicates else 0)

    if not duplicates:
        print_pass(f"通过 — 未发现超过 {args.threshold} 行的跨文件重复内容")
        print_summary(pass_count=1, warn_count=0, error_count=0)
        return

    print_warn(f"发现 {len(duplicates)} 处重复内容块:")
    print()

    for i, block in enumerate(duplicates, 1):
        print(f"  [{i}] 重复 {block.line_count} 行 (指纹: {block.fingerprint})")
        suggestion = suggest_merge_action(block.normalized_preview)
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

    print(f"\n  建议：审查重复内容，考虑合并或抽象为共享模板以降低维护成本。")
    sys.exit(1 if duplicates else 0)


if __name__ == "__main__":
    main()
