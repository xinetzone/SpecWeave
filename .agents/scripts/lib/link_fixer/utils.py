"""link_fixer 基础工具函数模块。

URL解析、路径转换、文件名/行号映射、模板链接检测、代码块上下文判断等。
"""

from __future__ import annotations

import os
from pathlib import Path

from .constants import TEMPLATE_LINK_TEXTS, TEMPLATE_URL_PATTERNS


def parse_file_url(url: str) -> tuple[str, str]:
    """解析 file:/// URL，返回 (文件路径部分, 锚点部分)。"""
    if "#" in url:
        path_part, anchor = url.split("#", 1)
        return path_part, f"#{anchor}"
    return url, ""


def extract_filename_from_url(file_url_path: str) -> str:
    """从 file:/// 路径中提取文件名。"""
    return Path(file_url_path).name


def os_path_to_posix(path: Path | str) -> str:
    """将 OS 路径转换为 POSIX 格式（Markdown 链接通用）。"""
    return str(path).replace("\\", "/")


def compute_relative_path(source_file: Path, target_file: Path) -> str:
    """计算从 source_file 到 target_file 的相对路径（POSIX 格式）。

    如果 target 是 README.md（表示目录链接），返回目录的相对路径加斜杠。
    如果 source 和 target 是同一文件，返回空字符串。
    """
    source_file = source_file.resolve()
    target_file = target_file.resolve()

    if source_file == target_file:
        return ""

    if target_file.name == "README.md":
        target_dir = target_file.parent
        source_dir = source_file.parent
        if source_dir == target_dir:
            return "./"
        rel = os_path_to_posix(Path(os.path.relpath(str(target_dir), str(source_dir))))
        return rel + "/"

    if target_file.is_dir():
        source_dir = source_file.parent
        if source_dir == target_file:
            return "./"
        rel = os_path_to_posix(Path(os.path.relpath(str(target_file), str(source_dir))))
        return rel + "/"

    source_dir = source_file.parent
    return os_path_to_posix(Path(os.path.relpath(str(target_file), str(source_dir))))


def apply_filename_mapping(file_path: str, rename_map: dict[str, str] | None) -> str:
    """应用文件名映射，处理文件重命名场景。"""
    if not rename_map:
        return file_path

    p = Path(file_path)
    old_name = p.name
    if old_name in rename_map:
        new_name = rename_map[old_name]
        return os_path_to_posix(p.parent / new_name) if p.parent.name else new_name
    return file_path


def apply_line_remap(anchor: str, line_remap: dict[str, dict[int, int]] | None, source_filename: str) -> str:
    """应用行号重映射，处理文件内容移位后行号变化的场景。"""
    if not line_remap or not anchor or not anchor.startswith("#L"):
        return anchor

    basename = Path(source_filename).name
    if basename not in line_remap:
        return anchor

    mapping = line_remap[basename]
    line_spec = anchor[2:]

    def _parse_line_num(s: str) -> int | None:
        s = s.lstrip("L")
        try:
            return int(s)
        except ValueError:
            return None

    if "-" in line_spec:
        start_str, end_str = line_spec.split("-", 1)
        start_line = _parse_line_num(start_str)
        end_line = _parse_line_num(end_str)
        if start_line is not None and end_line is not None:
            new_start = mapping.get(start_line, start_line)
            new_end = mapping.get(end_line, end_line)
            return f"#L{new_start}-L{new_end}"
        return anchor
    else:
        line_num = _parse_line_num(line_spec)
        if line_num is not None:
            new_line = mapping.get(line_num, line_num)
            return f"#L{new_line}"
        return anchor


def is_template_link(text: str, url: str) -> bool:
    """判断链接是否为模板/示例占位符（不应修复）。"""
    text_clean = text.strip()
    url_clean = url.strip().split("#")[0].rstrip("/")

    if text_clean in TEMPLATE_LINK_TEXTS:
        return True

    for pattern in TEMPLATE_URL_PATTERNS:
        if pattern.match(url_clean):
            return True

    if text_clean.endswith(".md") and url_clean == "path":
        return True
    if "->" in text_clean or "→" in text_clean:
        if url_clean in {"path", "path/old_name.md", "old_name.md", "URL"}:
            return True

    return False


def is_code_fence_context(content: str, pos: int) -> bool:
    """判断位置 pos 是否在代码块或行内代码内部（避免修改代码示例中的链接）。"""
    before = content[:pos]
    fence_count = before.count("```")
    if fence_count % 2 == 1:
        return True
    line_start = before.rfind("\n") + 1
    line_before = before[line_start:]
    tick_count = 0
    i = 0
    while i < len(line_before):
        if line_before[i] == "`":
            run = 1
            while i + run < len(line_before) and line_before[i + run] == "`":
                run += 1
            if run <= 2:
                tick_count += 1
            i += run
        else:
            i += 1
    return tick_count % 2 == 1
