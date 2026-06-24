"""TOML frontmatter 解析工具。

提供从 .agents/ Markdown 文件中提取 TOML frontmatter（+++ ... +++）
并解析 key = "value" 字段的通用能力。
"""

import re
from pathlib import Path

# 匹配 TOML frontmatter 块: +++ ... +++
_FRONTMATTER_RE = re.compile(
    r"^\+\+\+\s*\n(.*?)\n\+\+\+\s*$", re.MULTILINE | re.DOTALL
)

# 匹配简单字段: key = "value"
_FIELD_RE = re.compile(r'^(\w+)\s*=\s*"([^"]*)"\s*$', re.MULTILINE)


def parse_toml_frontmatter(file_path: str | Path) -> str | None:
    """读取文件并返回 TOML frontmatter 内容（不含 +++ 标记）。

    Args:
        file_path: .md 文件路径。

    Returns:
        frontmatter 纯文本内容；无 frontmatter 或读取异常时返回 None。
    """
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    match = _FRONTMATTER_RE.match(content)
    if not match:
        return None

    return match.group(1)


def extract_frontmatter_field(
    frontmatter: str, field_name: str
) -> str | None:
    """从 frontmatter 文本中提取指定字段的值。

    支持的格式: field_name = "value"

    Args:
        frontmatter: parse_toml_frontmatter 的返回值。
        field_name: 要提取的字段名（如 "id"、"tier"、"domain"）。

    Returns:
        字段值字符串；未找到时返回 None。
    """
    # 精准匹配指定字段名
    pattern = re.compile(
        rf'^{re.escape(field_name)}\s*=\s*"([^"]*)"\s*$', re.MULTILINE
    )
    match = pattern.search(frontmatter)
    return match.group(1) if match else None


def extract_all_fields(frontmatter: str) -> dict[str, str]:
    """从 frontmatter 文本中提取所有 key = "value" 字段。

    Args:
        frontmatter: parse_toml_frontmatter 的返回值。

    Returns:
        字段名到字段值的映射字典。
    """
    return dict(_FIELD_RE.findall(frontmatter))
