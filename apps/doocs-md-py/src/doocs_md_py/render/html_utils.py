"""HTML 文本工具（upstream: basicHelpers.ts + renderer-impl.stripInlineHtml）。"""

import html as _html
import re

_HTML_TAG_RE = re.compile(r"<[^>]*>")


def escape_html(text: str) -> str:
    """upstream: basicHelpers.ts:5（替换顺序固定：& < > " '）。"""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def unescape_html(text: str) -> str:
    """upstream: basicHelpers.ts:14。"""
    return (
        text.replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
    )


def strip_inline_html(fragment: str) -> str:
    """upstream: renderer-impl.ts:40（去标签后解码全部实体，等价 DOM textContent）。"""
    return _html.unescape(_HTML_TAG_RE.sub("", fragment))


def _to_int32(value: int) -> int:
    """JS ``hash & hash`` 的有符号 32 位整数截断。"""
    value &= 0xFFFFFFFF
    return value - 0x100000000 if value >= 0x80000000 else value


def simple_hash(text: str) -> str:
    """upstream: basicHelpers.ts:23（djb2 变体，int32 溢出，base36 输出）。

    JS 按 UTF-16 码元迭代；图表代码均为 ASCII，ord 与 charCodeAt 等价。
    """
    h = 0
    for ch in text:
        # JS: hash = ((hash << 5) - hash) + char; hash = hash & hash
        h = _to_int32((h << 5) - h + ord(ch))
    value = abs(h)
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    if value == 0:
        return "0"
    result = ""
    while value:
        value, rem = divmod(value, 36)
        result = digits[rem] + result
    return result
