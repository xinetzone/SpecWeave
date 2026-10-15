"""渲染流水线（upstream: packages/core/src/utils/markdownHelpers.ts）。"""

from typing import Any

from .extensions.katex import strip_break_before_inline_katex
from .reading_time import ReadTimeResults
from .renderer import Renderer
from .sanitize import sanitize_html

# upstream: markdownHelpers.ts:64-77
_MAC_STYLE = """
    <style>
      .hljs.code__pre > .mac-sign {
        display: %(mac)s;
      }
    </style>
  """

_H2_STRONG_STYLE = """
    <style>
      h2 strong {
        color: inherit !important;
      }
    </style>
  """


def render_markdown(raw: str, renderer: Renderer) -> dict[str, Any]:
    """upstream: markdownHelpers.ts:48。"""
    parsed = renderer.parse_front_matter_and_content(raw)
    html = renderer.render_markdown_to_html(parsed.markdown_content)
    html = strip_break_before_inline_katex(html)
    html = sanitize_html(html)
    return {"html": html, "reading_time": parsed.reading_time}


# 兼容英文键（测试/API 层使用）
def render_markdown_english(raw: str, renderer: Renderer) -> dict[str, Any]:
    result = render_markdown(raw, renderer)
    return {"html": result["html"], "readingTime": result["reading_time"]}


def post_process_html(base_html: str, reading: ReadTimeResults, renderer: Renderer) -> str:
    """upstream: markdownHelpers.ts:59。"""
    html = renderer.build_reading_time(reading) + base_html
    html += renderer.build_footnotes()
    html += renderer.build_addition()
    html += _MAC_STYLE % {"mac": "flex" if renderer.get_opts().is_mac_code_block else "none"}
    html += _H2_STRONG_STYLE
    return renderer.create_container(html)


def modify_html_content(content: str, renderer: Renderer) -> str:
    """upstream: markdownHelpers.ts:81。"""
    parsed = renderer.parse_front_matter_and_content(content)
    html = renderer.render_markdown_to_html(parsed.markdown_content)
    html = strip_break_before_inline_katex(html)
    html = sanitize_html(html)
    return post_process_html(html, parsed.reading_time, renderer)
