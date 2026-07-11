"""link_fixer 链接解析与修复核心模块。

实现单链接URL修复的核心策略调度：绝对路径转换、深度校正、文件名映射、断链搜索等。
"""

from __future__ import annotations

from pathlib import Path

from .constants import FILE_URL_RE
from .depth import try_adjust_relative_depth
from .finder import find_target_by_stem
from .utils import (
    apply_filename_mapping,
    apply_line_remap,
    compute_relative_path,
    extract_filename_from_url,
    is_template_link,
    os_path_to_posix,
    parse_file_url,
)


def fix_link_url(
    old_url: str,
    source_file: Path,
    project_root: Path,
    rename_map: dict[str, str] | None = None,
    line_remap: dict[str, dict[int, int]] | None = None,
    prefer_subdir: Path | None = None,
    link_text: str = "",
) -> tuple[str, str, str] | None:
    """修复单个链接 URL，返回 (new_url, fix_type, reason) 或 None（无需修复）。

    修复策略（按优先级）：
    1. file:/// 绝对路径 → 解析目标文件位置并计算相对路径
    2. 相对路径断链 → 通过文件名/目录名搜索找到正确目标并重算路径
    3. 文件名映射 → 替换重命名的文件名
    4. 同文件引用 → 简化为纯锚点
    5. 行号重映射 → 调整移位后的行号
    """
    anchor = ""
    file_part = old_url

    file_url_match = FILE_URL_RE.match(old_url)
    if file_url_match:
        raw_path = file_url_match.group(1)
        file_part, anchor = parse_file_url(raw_path)
        filename = extract_filename_from_url(file_part)
        filename = apply_filename_mapping(filename, rename_map)

        search_url = file_part.replace("\\", "/")
        target_file = find_target_by_stem(search_url, project_root, prefer_subdir, near=source_file)
        if target_file is None:
            target_file = find_target_by_stem(filename, project_root, prefer_subdir, near=source_file)
        if target_file is None:
            return None

        anchor = apply_line_remap(anchor, line_remap, target_file.name)
        rel_path = compute_relative_path(source_file, target_file)

        if rel_path == "":
            new_url = anchor if anchor else "#"
            fix_type = "same_file_anchor"
            reason = "同文件引用简化为纯锚点"
        else:
            new_url = f"{rel_path}{anchor}"
            fix_type = "absolute_to_relative"
            reason = f"绝对路径 → 相对路径（目标: {target_file.name}）"

        return (new_url, fix_type, reason)

    if old_url.startswith("#"):
        return None

    if old_url.startswith("http://") or old_url.startswith("https://") or old_url.startswith("mailto:"):
        return None

    if link_text and is_template_link(link_text, old_url):
        return None

    url_without_anchor = old_url.split("#")[0]
    if not url_without_anchor:
        return None

    anchor_part = old_url[len(url_without_anchor):]

    resolved = (source_file.parent / url_without_anchor).resolve()
    if resolved.exists():
        if resolved.is_dir():
            if not url_without_anchor.endswith("/"):
                new_url = url_without_anchor + "/" + anchor_part
                return (new_url, "dir_slash", "目录链接补充尾部斜杠")
        return None

    depth_adjusted = try_adjust_relative_depth(url_without_anchor, source_file)
    if depth_adjusted is not None:
        rel_path = compute_relative_path(source_file, depth_adjusted)
        anchor_part = apply_line_remap(anchor_part, line_remap, depth_adjusted.name)
        if rel_path == "":
            new_url = anchor_part if anchor_part else "#"
            fix_type = "same_file_anchor"
            reason = "同文件引用简化为纯锚点"
        else:
            new_url = f"{rel_path}{anchor_part}"
            fix_type = "depth_adjusted"
            old_depth = url_without_anchor.count("../")
            new_depth = rel_path.count("../")
            depth_diff = new_depth - old_depth
            direction = f"增加 {depth_diff} 层 ../" if depth_diff > 0 else f"减少 {-depth_diff} 层 ../"
            reason = f"相对路径层级校正（{direction}）：{url_without_anchor} → {rel_path.rstrip('/')}"
        return (new_url, fix_type, reason)

    target_filename = Path(url_without_anchor).name

    if rename_map and target_filename in rename_map:
        new_filename = rename_map[target_filename]
        p = Path(url_without_anchor)
        new_clean = os_path_to_posix(p.parent / new_filename) if p.parent.name else new_filename
        new_target = (source_file.parent / new_clean).resolve()
        if new_target.exists():
            anchor_part = apply_line_remap(anchor_part, line_remap, new_filename)
            new_url = f"{new_clean}{anchor_part}"
            return (new_url, "filename_mapped", f"文件名映射: {target_filename} → {new_filename}")

    guessed = find_target_by_stem(url_without_anchor, project_root, prefer_subdir, near=source_file)
    if guessed is not None:
        rel_path = compute_relative_path(source_file, guessed)
        anchor_part = apply_line_remap(anchor_part, line_remap, guessed.name)

        if rel_path == "":
            new_url = anchor_part if anchor_part else "#"
            fix_type = "same_file_anchor"
            reason = "同文件引用简化为纯锚点"
        else:
            new_url = f"{rel_path}{anchor_part}"
            fix_type = "broken_relative_fixed"
            reason = f"相对路径断链修复: {url_without_anchor} → {rel_path.rstrip('/')}"

        return (new_url, fix_type, reason)

    return None
