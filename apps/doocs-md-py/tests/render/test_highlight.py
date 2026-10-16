"""render/highlight.py 测试（upstream: renderer-impl.ts code()/renderDiffCode + languages.ts）。

覆盖三条契约：
1. 行号布局（show_line_number=True 的 section 结构）与无行号``code-block__inner``包裹；
2. ``formatHighlightedCode``/``splitHighlightedHtmlByLines`` 的 HLJS 输出后处理
   （相邻 span 间空格内移、按行自动闭合重开 span 上下文）；
3. LRU 上限 128 的淘汰行为与缓存清理。

T5 注册语言集仅 ``plaintext``，带 span 的 HTML 只能经后处理函数直接喂入。
"""

import pytest

from doocs_md_py.render import highlight
from doocs_md_py.render.highlight import (
    MAC_CODE_SVG,
    _CACHE_MAX,
    _format_highlighted_code,
    _split_highlighted_html_by_lines,
    clear_highlight_cache,
    highlight_and_format_code,
    render_diff_code,
)


@pytest.fixture(autouse=True)
def _isolate_cache():
    clear_highlight_cache()
    yield
    clear_highlight_cache()


# ---- 行号布局 ----


def test_line_number_layout_has_numbered_sections_and_line_breaks():
    html = highlight_and_format_code("a\nb", "plaintext", True)
    assert '<section class="line-numbers"' in html
    assert '<section class="code-scroll"' in html
    assert '<section style="padding:0 10px 0 0;line-height:1.75">1</section>' in html
    assert '<section style="padding:0 10px 0 0;line-height:1.75">2</section>' in html
    assert "a<br/>b" in html


def test_blank_line_becomes_nbsp_placeholder():
    html = highlight_and_format_code("a\n\nb", "plaintext", True)
    assert "&nbsp;" in html
    # 空行被替换为占位符而非空串，避免行号与内容错位
    assert "a<br/>" in html and "<br/>b" in html


def test_without_line_number_wraps_escaped_body():
    html = highlight_and_format_code("a\n  <b>", "plaintext", False)
    assert html == (
        '<span class="code-block__inner" style="display:block">'
        "a<br/>&nbsp;&nbsp;&lt;b&gt;</span>"
    )


def test_cache_hit_returns_identical_object():
    first = highlight_and_format_code("console.log(1)", "plaintext", False)
    second = highlight_and_format_code("console.log(1)", "plaintext", False)
    assert first is second


def test_line_number_flag_is_part_of_cache_key():
    plain = highlight_and_format_code("x", "plaintext", False)
    numbered = highlight_and_format_code("x", "plaintext", True)
    assert plain != numbered
    assert "line-numbers" not in plain
    assert "line-numbers" in numbered


def test_lru_evicts_oldest_entry_when_capacity_exceeded():
    for index in range(_CACHE_MAX + 1):
        highlight_and_format_code(f"text-{index}", "plaintext", False)

    assert len(highlight._cache) == _CACHE_MAX
    assert "plaintext\x000\x00text-0" not in highlight._cache
    assert f"plaintext\x000\x00text-{_CACHE_MAX}" in highlight._cache


def test_clear_highlight_cache_drops_all_entries():
    highlight_and_format_code("x", "plaintext", False)
    assert highlight._cache
    clear_highlight_cache()
    assert not highlight._cache


# ---- formatHighlightedCode（languages.ts:69） ----


def test_format_highlighted_code_moves_space_into_next_span():
    html = (
        '<span class="hljs-keyword">const</span>'
        ' <span class="hljs-variable">a</span>'
    )
    assert _format_highlighted_code(html) == (
        '<span class="hljs-keyword">const</span>'
        '<span class="hljs-variable">&nbsp;a</span>'
    )


def test_format_highlighted_code_expands_tabs_to_four_spaces():
    assert _format_highlighted_code("a\tb") == "a&nbsp;&nbsp;&nbsp;&nbsp;b"


def test_format_highlighted_code_preserve_newlines_uses_br():
    assert _format_highlighted_code("a\nb", True) == "a<br/>b"
    assert _format_highlighted_code("a\r\nb", True) == "a<br/>b"
    # 非保留模式下换行随文本节点一并转为 &nbsp;（不做 <br/> 替换）
    assert _format_highlighted_code("a\nb", False) == "a&nbsp;b"


# ---- splitHighlightedHtmlByLines（languages.ts:90） ----


def test_split_by_lines_reopens_open_span_context():
    lines = _split_highlighted_html_by_lines('<span class="hljs-keyword">a\nb</span>')
    assert lines == [
        '<span class="hljs-keyword">a</span>',
        '<span class="hljs-keyword">b</span>',
    ]


def test_split_by_lines_closes_only_tracked_open_spans():
    # 无未闭合 span 时行尾不补 </span>
    assert _split_highlighted_html_by_lines("a\nb") == ["a", "b"]
    # 孤立的闭合标签不会使 open_tags 下溢
    assert _split_highlighted_html_by_lines("a</span>\nb") == ["a</span>", "b"]


def test_split_by_lines_tolerates_unterminated_tag_at_end_of_input():
    assert _split_highlighted_html_by_lines('<span class="hljs-keyword">a<') == [
        '<span class="hljs-keyword">a<'
    ]


# ---- renderDiffCode（renderer-impl.ts:120） ----


def test_render_diff_code_marks_added_and_removed_lines():
    html = render_diff_code("+a\n-b\n c", "js")
    assert MAC_CODE_SVG in html
    assert '<code class="language-diff-js">' in html
    assert "background:rgba(80,200,80,.18);" in html
    assert "background:rgba(255,80,80,.18);" in html
    assert '<span style="color:#52c41a;user-select:none;">+</span>a' in html
    assert '<span style="color:#ff4d4f;user-select:none;">-</span>b' in html
    # 普通行无底色，符号位为占位空格，原文（含行首空格）逐字保留
    context_row = (
        '<span style="display:block;"><span style="user-select:none;"> </span> c</span>'
    )
    assert context_row in html
    assert html.count("display:block;") == 3


def test_render_diff_code_empty_line_has_no_sign():
    html = render_diff_code("+a\n\n-b", "js")
    assert html.count("display:block;") == 3
    assert '<code class="language-diff-js">' in html


def test_render_diff_code_language_only_shows_up_in_code_class():
    plain = render_diff_code("+a\n-b", "plaintext")
    unknown = render_diff_code("+a\n-b", "js")
    assert '<code class="language-diff-plaintext">' in plain
    assert '<code class="language-diff-js">' in unknown
    # T5 注册语言与未注册语言同形：着色后端缺失时语言只体现在 code 的 class 上
    marker = (
        '<span style="display:block;background:rgba(80,200,80,.18);">'
        '<span style="color:#52c41a;user-select:none;">+</span>a</span>'
    )
    assert marker in plain and marker in unknown
