"""KaTeX 占位扩展对拍测试。

转录自：
- renderer/inline-katex.test.ts（行内公式不被包块、软换行无 <br>）
- renderer/renderer.test.ts:79-99（独占行块公式无 <p> 包裹）
- utils/mathDetection.test.ts（块/行内规则边界、#1743）

服务端只产 katex-pending 占位（不引 MathJax），等价上游 window 未定义分支。
"""

import re

import pytest

from doocs_md_py.render import init_renderer
from doocs_md_py.render.extensions.katex import (
    BLOCK_MULTILINE_RE,
    BLOCK_SINGLE_RE,
    INLINE_NONSTD_RE,
    render_pending,
)

SINGLE = r"$$ITE_{i}=Y_{i,1}-Y_{i,0} \tag{1}$$"
MULTI = "$$\nITE_{i}=Y_{i,1}-Y_{i,0} \\tag{1}\n$$"


# ---- 规则层（mathDetection.test.ts 转录）----
def test_block_rules_discriminate_single_vs_multiline():
    assert BLOCK_MULTILINE_RE.match(MULTI)
    assert BLOCK_SINGLE_RE.match(SINGLE)
    # 多行公式不能命中单行规则：单行内容 [^\n]+ 后必须紧跟闭合 $$
    assert not BLOCK_SINGLE_RE.match(MULTI.split("\n", 1)[0])


def test_match_block_katex_single_extracts_latex():
    match = BLOCK_SINGLE_RE.match(SINGLE)
    assert match.group(2).strip() == r"ITE_{i}=Y_{i,1}-Y_{i,0} \tag{1}"


def test_inline_rule_matches_single_line_formula_directly():
    match = INLINE_NONSTD_RE.match(SINGLE)
    assert match.group(2).strip() == r"ITE_{i}=Y_{i,1}-Y_{i,0} \tag{1}"
    assert len(match.group(1)) == 2


def test_single_dollar_at_line_start_is_not_block():
    assert BLOCK_SINGLE_RE.match("$y_1 = y_2$") is None
    assert BLOCK_MULTILINE_RE.match("$y_1 = y_2$") is None
    assert BLOCK_SINGLE_RE.match("  $y_1 = y_2$") is None


# ---- 占位容器契约（katex.ts:74-80）----
def test_pending_placeholders_shapes():
    inline = render_pending("$x$", False)
    assert inline == (
        '<span class="katex-inline katex-pending" data-math-display="false"'
        ' data-math-raw="$x$"><span>…</span></span>'
    )
    block = render_pending("$$\nx\n$$", True)
    assert block == (
        '<section class="katex-block katex-pending" data-math-display="true"'
        ' data-math-raw="$$\nx\n$$"><span>Loading formula…</span></section>'
    )


def test_pending_loading_message_injected_and_escaped():
    block = render_pending("$$x$$", True, get_loading=lambda: "数式読込中")
    assert "数式読込中" in block
    assert 'class="katex-block katex-pending"' in block
    # 空文案回退英文默认
    fallback = render_pending("$$x$$", True, get_loading=lambda: "")
    assert "Loading formula…" in fallback
    # raw 进属性必须转义引号/尖括号
    xss = render_pending('$"><b>$', False)
    assert "<b>" not in xss
    assert "&quot;" in xss
    assert "&lt;b&gt;" in xss


# ---- 渲染层（inline-katex.test.ts 转录）----
def test_inline_formula_in_chinese_text():
    html = init_renderer().render_markdown_to_html(r"取$y_1 = y_2 = \cdots = y_n = -y$，就退化为二元的情形")
    assert "katex-inline" in html
    assert "katex-block" not in html
    assert re.search(r"取[\s\S]*katex-inline[\s\S]*就退化为二元的情形", html)


def test_inline_formula_surrounded_by_text():
    html = init_renderer().render_markdown_to_html("before $x+y$ after")
    assert "katex-inline" in html
    assert "katex-block" not in html


def test_inline_formula_after_soft_break_no_br_1743():
    md = "取\n$y_1 = y_2 = \\cdots = y_n = -y$，就退化为二元的情形"
    html = init_renderer().render_markdown_to_html(md)
    assert "katex-inline" in html
    assert "katex-block" not in html
    # 行内 katex 前的 <br> 由后处理剥离（T7e 接线）；此时上游 markdown 输出也不应出现裸 <br>
    assert re.search(r"取[\s\S]*katex-inline[\s\S]*就退化为二元的情形", html)


def test_line_start_single_dollar_is_inline():
    html = init_renderer().render_markdown_to_html(r"$y_1 = y_2 = \cdots = y_n = -y$")
    assert "katex-inline" in html
    assert "katex-block" not in html


def test_inline_formula_in_list_item():
    html = init_renderer().render_markdown_to_html(r"- 取$y_1 = y_2 = \cdots = y_n = -y$，退化")
    assert "katex-inline" in html
    assert "katex-block" not in html


# ---- renderer.test.ts:79-99 ----
def test_single_line_block_formula_no_paragraph_wrapper():
    html = init_renderer().render_markdown_to_html(SINGLE)
    assert "katex-block" in html
    assert "data-math-raw" in html
    assert r"\tag{1}" in html
    assert not re.search(r'<p[^>]*>\s*<section class="katex-block"', html)


def test_list_followed_by_block_formula_no_wrapper():
    md = "1.比如识别段落之间带有编号的latex公式，如 \n\n" + SINGLE
    html = init_renderer().render_markdown_to_html(md)
    assert "data-math-raw" in html
    assert r"\tag{1}" in html
    assert not re.search(r'<p[^>]*>\s*<section class="katex-block"', html)


def test_multiline_block_formula():
    html = init_renderer().render_markdown_to_html(MULTI)
    assert 'class="katex-block katex-pending"' in html
    assert 'data-math-display="true"' in html
    # 后续段落不被吞
    html2 = init_renderer().render_markdown_to_html(MULTI + "\n\n后续段落")
    assert "后续段落" in html2


# ---- LaTeX 分隔符 ----
def test_inline_latex_parens():
    html = init_renderer().render_markdown_to_html(r"行中 \(a+b\) 公式")
    assert 'data-math-display="false"' in html
    # \( 仅作为 data-math-raw 原样保留，不再以可见定界符出现
    assert html.count(r"\(") == 1
    assert 'data-math-raw="\\(a+b\\)"' in html


def test_block_latex_brackets_line_start():
    html = init_renderer().render_markdown_to_html(r"\[x^2+y^2=z^2\]")
    assert 'class="katex-block katex-pending"' in html
    assert not re.search(r'<p[^>]*>\s*<section class="katex-block"', html)


def test_inline_double_dollar_renders_display_marker():
    # 上游 inlineKatex：$$ 定界符 → displayMode=true（即便在段落中产出 section）
    html = init_renderer().render_markdown_to_html("a $$x$$ b")
    assert 'data-math-display="true"' in html


# ---- 守卫 ----
def test_formula_inside_fence_is_literal():
    html = init_renderer().render_markdown_to_html("```\n$$x$$\n```")
    assert "katex-pending" not in html


def test_formula_inside_inline_code_is_literal():
    html = init_renderer().render_markdown_to_html("`$x$`")
    assert "katex-pending" not in html
    assert "$x$" in html


def test_currency_amount_not_math():
    # isAmountDollarSign：数字后 $ 为金额
    html = init_renderer().render_markdown_to_html("20$ and 30$")
    assert "katex-pending" not in html


def test_unknown_injection_in_loading_option():
    renderer = init_renderer()
    renderer.opts.render_messages = None
    html = renderer.render_markdown_to_html("$x$")
    assert "Loading formula…" not in html  # 行内占位永远是 …
    assert 'data-math-display="false"' in html


class TestStripBreakBeforeInlineKatex:
    """upstream: utils/mathDetection.ts:114-116 stripBreakBeforeInlineKatex。"""

    def test_strips_br_before_inline_span(self):
        from doocs_md_py.render.extensions.katex import (
            strip_break_before_inline_katex,
        )

        html = '取<br />\n<span class="katex-inline katex-pending">x</span>'
        assert strip_break_before_inline_katex(html) == "取<span class=\"katex-inline katex-pending\">x</span>"

    def test_keeps_br_before_other_spans(self):
        from doocs_md_py.render.extensions.katex import (
            strip_break_before_inline_katex,
        )

        html = 'a<br><span class="other">b</span>'
        assert strip_break_before_inline_katex(html) == html

    def test_hard_break_before_formula_via_renderer(self):
        # #1743：硬换行（行尾两空格）后紧跟行内公式，<br> 必须被剥离。
        from doocs_md_py.render.extensions.katex import (
            strip_break_before_inline_katex,
        )

        html = strip_break_before_inline_katex(
            init_renderer().render_markdown_to_html("取  \n$x$")
        )
        assert "<br" not in html
        assert 'class="katex-inline' in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

