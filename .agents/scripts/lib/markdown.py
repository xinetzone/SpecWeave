"""Markdown 文件处理共享模块。

整合 check-links、check-mermaid、generate-apps-index、generate-nav、
generate-dashboard 等脚本中重复的 Markdown 文件遍历、标题/描述提取、
内联链接解析、HTML 标记区替换等逻辑，提供统一引用入口。
"""

import re
from pathlib import Path

from constants import EXCLUDED_DIRS
from lib.link_fixer import INLINE_LINK_RE

# 标题提取：匹配第一个一级标题
TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
# 描述提取：匹配标题后第一个非空段落（排除引用块和元数据行）
DESC_RE = re.compile(r"^#\s+.+\n\n(?:>.*\n)*\n?([^\n#>`\-\|].+)", re.MULTILINE)


def find_markdown_files(
    root: Path, exclude_dirs: list[str] | set[str] | None = None
) -> list[Path]:
    """递归查找 root 目录下所有 Markdown 文件。

    默认排除 constants.EXCLUDED_DIRS 中的系统目录（.git、vendor、.venv、
    __pycache__、node_modules、.temp），可通过 exclude_dirs 传入额外排除
    目录（按相对 root 的路径前缀匹配）。

    Args:
        root: 扫描根目录。
        exclude_dirs: 额外排除的目录（list 或 set），按相对路径前缀匹配。

    Returns:
        匹配的 .md 文件 Path 列表。
    """
    extra = set(exclude_dirs) if exclude_dirs else set()
    md_files: list[Path] = []
    for md_path in root.rglob("*.md"):
        parts = set(md_path.parts)
        if EXCLUDED_DIRS & parts:
            continue
        try:
            rel_path = md_path.relative_to(root)
        except ValueError:
            rel_path = md_path
        rel_str = rel_path.as_posix()
        if any(rel_str.startswith(excl.replace("\\", "/")) for excl in extra):
            continue
        md_files.append(md_path)
    return md_files


def extract_title(path: Path | str) -> str:
    """从 Markdown 文件提取首个一级标题文本。

    Args:
        path: Markdown 文件路径（Path 对象或字符串）。

    Returns:
        标题文本字符串，无标题时返回空字符串。
    """
    content = Path(path).read_text(encoding="utf-8")
    m = TITLE_RE.search(content)
    if m:
        return m.group(1).strip()
    return ""


def extract_description(path: Path | str) -> str:
    """从 Markdown 文件提取标题下的首行描述文本。

    匹配首个一级标题后第一个非空段落（排除引用块和元数据行），
    取第一句作为描述。

    Args:
        path: Markdown 文件路径（Path 对象或字符串）。

    Returns:
        描述文本字符串，无描述时返回空字符串。
    """
    content = Path(path).read_text(encoding="utf-8")
    m = DESC_RE.search(content)
    if m:
        desc = m.group(1).strip()
        desc = re.split(r"[。\.]\s", desc)[0]
        return desc
    return ""


def parse_inline_links(content: str) -> list[tuple[str, str]]:
    """从 Markdown 内容提取所有内联链接。

    复用 lib.link_fixer.INLINE_LINK_RE 正则匹配 [text](url) 形式的链接。

    Args:
        content: Markdown 文本内容。

    Returns:
        (link_text, url) 元组列表。
    """
    return [
        (m.group(1), m.group(2).strip())
        for m in INLINE_LINK_RE.finditer(content)
    ]


def update_marker_region(
    file_path: Path | str,
    marker_start: str,
    marker_end: str,
    new_content: str,
) -> None:
    """替换 Markdown 文件中 marker_start 与 marker_end 标记之间的内容。

    保留标记本身和文件其他内容不变，仅在两个标记之间插入 new_content
    （前后各空一行）。

    Args:
        file_path: 目标文件路径（Path 对象或字符串）。
        marker_start: 起始标记字符串（如 HTML 注释）。
        marker_end: 结束标记字符串（如 HTML 注释）。
        new_content: 替换标记区域的新内容。

    Raises:
        ValueError: 文件中未找到 marker_start 或 marker_end 标记。
    """
    p = Path(file_path)
    content = p.read_text(encoding="utf-8")

    start_idx = content.find(marker_start)
    end_idx = content.find(marker_end)

    if start_idx == -1 or end_idx == -1:
        raise ValueError(
            f"{p} 中未找到标记 {marker_start!r} / {marker_end!r}，无法更新标记区域"
        )

    updated = (
        content[: start_idx + len(marker_start)]
        + "\n\n"
        + new_content
        + "\n\n"
        + content[end_idx:]
    )
    p.write_text(updated, encoding="utf-8")
