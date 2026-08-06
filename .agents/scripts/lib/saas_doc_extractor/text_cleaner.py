"""文本清理工具。

提供零宽字符清理、行拆分、URL提取等通用文本处理功能。
所有平台通用，不依赖浏览器抽象层。
"""

from __future__ import annotations

import re


# 零宽字符范围（实测飞书/钉钉/企微均会注入）
ZERO_WIDTH_CHARS = re.compile(r'[\u200b-\u200f\u2028-\u202f\ufeff]')

# URL匹配正则（兼容中英文括号闭合）
URL_PATTERN = re.compile(r'https?://[^\s\u200b\）\)】}]+')


def clean_text(text: str) -> str:
    """清理零宽字符和首尾空白。

    Args:
        text: 原始文本

    Returns:
        清理后的文本
    """
    if not text:
        return ""
    return ZERO_WIDTH_CHARS.sub('', text).strip()


def split_lines(inner_text: str) -> list[str]:
    """拆分DOM元素的innerText为独立文本行。

    一个`.ace-line`或类似行容器的innerText可能包含\\n（由<br>或内联块元素导致），
    需要拆分为真正的视觉行。同时清理零宽字符和空行。

    Args:
        inner_text: DOM元素的innerText

    Returns:
        清理后的非空文本行列表
    """
    if not inner_text:
        return []
    lines: list[str] = []
    for segment in inner_text.split('\n'):
        cleaned = clean_text(segment)
        if cleaned:
            lines.append(cleaned)
    return lines


def extract_urls(text: str) -> list[str]:
    """从文本中提取所有URL。

    Args:
        text: 输入文本

    Returns:
        去重后的URL列表（保序）
    """
    if not text:
        return []
    seen: set[str] = set()
    urls: list[str] = []
    for match in URL_PATTERN.finditer(text):
        url = match.group(0).rstrip('.,;:，。；：')
        if url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def has_zero_width_chars(text: str) -> bool:
    """检测文本是否包含零宽字符。

    Args:
        text: 待检测文本

    Returns:
        True表示包含零宽字符
    """
    return bool(ZERO_WIDTH_CHARS.search(text))
