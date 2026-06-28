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

# 匹配字段（支持带引号和无引号值）: key = "value" 或 key = unquoted_value
_FIELD_RE_FULL = re.compile(
    r'^(\w+)\s*=\s*(?:"([^"]*)"|(\S+))\s*$', re.MULTILINE
)


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

    支持的格式: field_name = "value" 和 field_name = unquoted_value

    Args:
        frontmatter: parse_toml_frontmatter 的返回值。
        field_name: 要提取的字段名（如 "id"、"tier"、"domain"、"validation_count"）。

    Returns:
        字段值字符串；未找到时返回 None。
    """
    # 先尝试带引号值格式
    pattern = re.compile(
        rf'^{re.escape(field_name)}\s*=\s*"([^"]*)"\s*$', re.MULTILINE
    )
    match = pattern.search(frontmatter)
    if match:
        return match.group(1)

    # 再尝试无引号值格式
    pattern = re.compile(
        rf'^{re.escape(field_name)}\s*=\s*(\S+)\s*$', re.MULTILINE
    )
    match = pattern.search(frontmatter)
    return match.group(1) if match else None


def extract_all_fields(frontmatter: str) -> dict[str, str]:
    """从 frontmatter 文本中提取所有字段（支持带引号和无引号值）。

    Args:
        frontmatter: parse_toml_frontmatter 的返回值。

    Returns:
        字段名到字段值的映射字典。
    """
    result = {}
    for match in _FIELD_RE_FULL.finditer(frontmatter):
        key = match.group(1)
        # group(2) 是带引号值，group(3) 是无引号值
        value = match.group(2) if match.group(2) is not None else match.group(3)
        result[key] = value
    return result


def parse_toml_frontmatter_as_dict(
    file_path: str | Path,
) -> dict[str, str] | None:
    """一步读取文件并解析 TOML frontmatter 为字段字典。

    便捷函数，等价于 ``parse_toml_frontmatter`` + ``extract_all_fields``。

    Args:
        file_path: .md 文件路径。

    Returns:
        字段名到字段值的映射字典；无 frontmatter 或读取异常时返回 None。
    """
    fm_text = parse_toml_frontmatter(file_path)
    if fm_text is None:
        return None
    return extract_all_fields(fm_text)
