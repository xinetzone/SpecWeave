"""重复检测共享核心模块。

提供跨 Python 脚本和 Markdown 文档的重复检测通用组件：
  - DuplicateBlock / Occurrence 数据类
  - compute_fingerprint() 指纹计算
  - expand_duplicate_block() 核心扩展算法
  - build_duplicate_block() 块构造辅助
"""

import hashlib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DuplicateBlock:
    """一个重复代码/内容块。"""
    fingerprint: str
    line_count: int
    normalized_preview: str
    occurrences: list["Occurrence"] = field(default_factory=list)


@dataclass
class Occurrence:
    """重复块在单个文件中的出现位置。"""
    file_path: Path
    start_line: int
    end_line: int
    raw_preview: str


def compute_fingerprint(lines: list[str]) -> str:
    """计算一组归一化行的指纹（SHA256 前16位）。"""
    joined = "\n".join(lines)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def expand_duplicate_block(
    seed_locations: list[tuple[Path, int, int]],
    file_norm_lines: dict[Path, list[tuple[int, str]]],
    visited_fps: set[str],
    window: int,
) -> list[tuple[Path, int, int]]:
    """从种子窗口出发，向前后扩展到最大重复块。

    尝试在每个文件中向前/向后扩展归一化行，只要所有文件的对应行归一化后相等就继续扩展。
    返回每个文件中的 (path, start_line, end_line)。

    Args:
        seed_locations: 种子位置列表，每个元素为 (path, start_line, window_size)。
        file_norm_lines: 每个文件的归一化行数据，值为 (原始行号, 归一化内容) 列表。
        visited_fps: 已访问的指纹集合，用于去重标记。
        window: N 元语法窗口大小，用于指纹标记。

    Returns:
        扩展后的位置列表，每个元素为 (path, start_line, end_line)。
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


def build_duplicate_block(
    fp: str,
    blocks: list[tuple[Path, int, int]],
    file_norm_lines: dict[Path, list[tuple[int, str]]],
) -> DuplicateBlock:
    """从扩展后的块位置构建完整的 DuplicateBlock（含 raw_preview 和 normalized_preview）。

    Args:
        fp: 指纹字符串。
        blocks: 扩展后的块位置列表，每个元素为 (path, start_line, end_line)。
        file_norm_lines: 每个文件的归一化行数据。

    Returns:
        填充了 occurrences 和 normalized_preview 的 DuplicateBlock。
    """
    block = DuplicateBlock(
        fingerprint=fp,
        line_count=blocks[0][2] - blocks[0][1] + 1,
        normalized_preview="",
    )

    preview_set = False
    for py_path, start_line, end_line in blocks:
        norm_lines = file_norm_lines[py_path]
        try:
            raw_content = py_path.read_text(encoding="utf-8")
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
            file_path=py_path,
            start_line=start_line,
            end_line=end_line,
            raw_preview=raw_preview,
        ))

    return block


def process_duplicate_seeds(
    seeds: dict[str, list[tuple[Path, int, int]]],
    file_norm_lines: dict[Path, list[tuple[int, str]]],
    window: int,
    *,
    threshold: int,
    block_filter: callable = None,
) -> list[DuplicateBlock]:
    """从种子指纹映射中处理重复块，返回通过阈值和过滤的 DuplicateBlock 列表。

    这是 check-duplication.py 和 check_markdown_duplication.py 中
    重复检测核心循环的共享实现。

    Args:
        seeds: 指纹→种子位置列表的映射。
        file_norm_lines: 每个文件的归一化行数据。
        window: N 元语法窗口大小。
        threshold: 最小重复行数阈值。
        block_filter: 可选过滤器，签名为 (DuplicateBlock, file_norm_lines) -> bool，
                      返回 True 表示排除该块。

    Returns:
        DuplicateBlock 列表，已按行数降序排列。
    """
    visited_fps: set[str] = set()
    duplicates: list[DuplicateBlock] = []

    for fp in sorted(seeds.keys(), key=lambda k: -len(seeds[k])):
        if fp in visited_fps:
            continue

        locations = seeds[fp]
        blocks = expand_duplicate_block(locations, file_norm_lines, visited_fps, window)
        if not blocks:
            continue

        block = build_duplicate_block(fp, blocks, file_norm_lines)

        if block.line_count >= threshold:
            if block_filter and block_filter(block, file_norm_lines):
                continue
            duplicates.append(block)

    duplicates.sort(key=lambda b: (-b.line_count, len(b.occurrences)))
    return duplicates