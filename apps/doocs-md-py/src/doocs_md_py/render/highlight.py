"""代码块输出（upstream: renderer-impl.ts code()/renderDiffCode + languages.ts）。

T5 等价口径：Python 端暂无 highlight.js 语法着色（语法 span 差异登记于
contract-differences，T6 决策着色后端），注册语言集仅 ``plaintext``；
但包裹结构、Mac 三点、data-language-pending 三属性、行号布局、diff-<lang>
红绿行全部 1:1，未注册语言仍由前端 CDN 语法包在浏览器侧延迟高亮。
"""

import re
from collections import OrderedDict

from .html_utils import escape_html

# upstream: renderer-impl.ts:108-114
MAC_CODE_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" x="0px" y="0px" width="45px" height="13px" viewBox="0 0 450 130">
    <ellipse cx="50" cy="65" rx="50" ry="52" stroke="rgb(220,60,54)" stroke-width="2" fill="rgb(237,108,96)" />
    <ellipse cx="225" cy="65" rx="50" ry="52" stroke="rgb(218,151,33)" stroke-width="2" fill="rgb(247,193,81)" />
    <ellipse cx="400" cy="65" rx="50" ry="52" stroke="rgb(27,161,37)" stroke-width="2" fill="rgb(100,200,86)" />
</svg>""".strip()

# upstream: languages.ts:18-29（Python 端 T5 无 hljs 语法集，仅 plaintext 视为已注册）
REGISTERED_LANGUAGES = frozenset({"plaintext"})

# 简单 LRU（upstream: languages.ts:144 LRUMap<string>(128)）
_CACHE_MAX = 128
_cache: "OrderedDict[str, str]" = OrderedDict()

_SPAN_ADJACENT_RE = re.compile(
    r"(<span[^>]*>[^<]*</span>)(\s+)(<span[^>]*>[^<]*</span>)"
)
_SPACE_BEFORE_SPAN_RE = re.compile(r"(\s+)(<span[^>]*>)")
_TEXT_NODE_RE = re.compile(r">(?:[^<]+)|^(?:[^<]+)")
_WS_RE = re.compile(r"\s")


def _format_highlighted_code(html: str, preserve_newlines: bool = False) -> str:
    """upstream: languages.ts:69 formatHighlightedCode。"""

    def _adjacent(m: re.Match[str]) -> str:
        span1, spaces, span2 = m.group(1), m.group(2), m.group(3)
        return span1 + re.sub(r"^(<span[^>]*>)", rf"\1{spaces}", span2, count=1)

    formatted = _SPAN_ADJACENT_RE.sub(_adjacent, html)
    formatted = _SPACE_BEFORE_SPAN_RE.sub(
        lambda m: re.sub(r"^(<span[^>]*>)", rf"\1{m.group(1)}", m.group(2), count=1),
        formatted,
    )
    formatted = formatted.replace("\t", "    ")

    if preserve_newlines:
        formatted = formatted.replace("\r\n", "<br/>").replace("\n", "<br/>")

    def _nbsp_text(m: re.Match[str]) -> str:
        return _WS_RE.sub("&nbsp;", m.group(0))

    return _TEXT_NODE_RE.sub(_nbsp_text, formatted)


def _split_highlighted_html_by_lines(html: str) -> list[str]:
    """upstream: languages.ts:90（按行切分，自动闭合/重开 <span> 上下文）。"""
    lines: list[str] = []
    current = ""
    open_tags: list[str] = []
    i = 0
    while i < len(html):
        ch = html[i]
        if ch == "<":
            tag = "<"
            i += 1
            while i < len(html) and html[i] != ">":
                tag += html[i]
                i += 1
            if i < len(html):
                tag += ">"
                i += 1
            current += tag
            if tag.startswith("</span"):
                if open_tags:
                    open_tags.pop()
            elif tag.startswith("<span"):
                open_tags.append(tag)
        elif ch == "\n":
            lines.append(current + "</span>" * len(open_tags))
            current = "".join(open_tags)
            i += 1
        else:
            current += ch
            i += 1
    lines.append(current)
    return lines


def _plaintext_highlight(text: str) -> str:
    """hljs plaintext 语法等价输出：仅 HTML 转义。"""
    return escape_html(text)


def highlight_and_format_code(text: str, language: str, show_line_number: bool) -> str:
    """upstream: languages.ts:147。"""
    cache_key = f"{language}\x00{'1' if show_line_number else '0'}\x00{text}"
    cached = _cache.get(cache_key)
    if cached is not None:
        _cache.move_to_end(cache_key)
        return cached

    if show_line_number:
        normalized = text.replace("\r\n", "\n")
        full = _plaintext_highlight(normalized)
        highlighted_lines = []
        for line_html in _split_highlighted_html_by_lines(full):
            formatted = _format_highlighted_code(line_html, False)
            highlighted_lines.append(formatted if formatted else "&nbsp;")

        line_numbers = "".join(
            f'<section style="padding:0 10px 0 0;line-height:1.75">{i + 1}</section>'
            for i in range(len(highlighted_lines))
        )
        code_inner = "<br/>".join(highlighted_lines)
        code_lines = (
            '<div style="white-space:pre;min-width:max-content;line-height:1.75">'
            f"{code_inner}</div>"
        )
        column_styles = (
            "text-align:right;padding:8px 0;border-right:1px solid rgba(0,0,0,0.04);"
            "user-select:none;background:var(--code-bg,transparent);"
        )
        highlighted = f"""
      <section style="display:flex;align-items:flex-start;overflow-x:hidden;overflow-y:auto;width:100%;max-width:100%;padding:0;box-sizing:border-box">
        <section class="line-numbers" style="{column_styles}">{line_numbers}</section>
        <section class="code-scroll" style="flex:1 1 auto;overflow-x:auto;overflow-y:visible;padding:8px;min-width:0;box-sizing:border-box">{code_lines}</section>
      </section>
    """
    else:
        raw = _plaintext_highlight(text)
        formatted = _format_highlighted_code(raw, True)
        highlighted = f'<span class="code-block__inner" style="display:block">{formatted}</span>'

    _cache[cache_key] = highlighted
    if len(_cache) > _CACHE_MAX:
        _cache.popitem(last=False)
    return highlighted


def clear_highlight_cache() -> None:
    """upstream: languages.ts:195。"""
    _cache.clear()


def render_diff_code(text: str, base_lang: str) -> str:
    """upstream: renderer-impl.ts:120（diff-<lang>：+ 绿/- 红，其余行普通转义）。"""
    registered = base_lang in REGISTERED_LANGUAGES
    lines = text.split("\n")
    prefixes = [line[0] if line else "" for line in lines]
    stripped = [
        line[1:] if p in ("+", "-") else line for line, p in zip(lines, prefixes, strict=True)
    ]
    # T5 注册集仅 plaintext，与未注册回退同形（逐行转义）；T6 接入着色后端时
    # 仅需把 registered=True 路径换成 hljs 高亮结果。
    _ = registered
    highlighted_lines = [escape_html(s) for s in stripped]

    rendered_parts = []
    for i, prefix in enumerate(prefixes):
        if prefix == "+":
            bg = "background:rgba(80,200,80,.18);"
            sign = '<span style="color:#52c41a;user-select:none;">+</span>'
        elif prefix == "-":
            bg = "background:rgba(255,80,80,.18);"
            sign = '<span style="color:#ff4d4f;user-select:none;">-</span>'
        else:
            bg = ""
            sign = '<span style="user-select:none;"> </span>'
        highlighted = highlighted_lines[i] if i < len(highlighted_lines) else ""
        rendered_parts.append(
            f'<span style="display:block;{bg}">{sign}{highlighted}</span>'
        )

    span = '<span class="mac-sign" style="padding: 10px 14px 0;">' + MAC_CODE_SVG + "</span>"
    return (
        f'<pre class="hljs code__pre">{span}'
        f'<code class="language-diff-{base_lang}">'
        f'<span class="code-block__inner" style="display:block">{"".join(rendered_parts)}</span>'
        "</code></pre>"
    )
