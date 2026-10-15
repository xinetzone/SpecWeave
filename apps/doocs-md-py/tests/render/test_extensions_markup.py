"""markup/toc/slider 扩展对拍（upstream: extensions.test.ts）。

覆盖 markup.ts 边界规则、toc.ts 嵌套目录、slider.ts 横滑容器。
"""

import pytest

from doocs_md_py.render import init_renderer


@pytest.fixture()
def render():
    renderer = init_renderer()

    def _render(md: str) -> str:
        return renderer.render_markdown_to_html(md)

    return _render


class TestMarkup:
    def test_three_spans(self, render):
        html = render("==hl== ++ul++ ~wv~")
        assert 'class="markup-highlight"' in html
        assert 'class="markup-underline"' in html
        assert 'class="markup-wavyline"' in html
        assert ">hl<" in html and ">ul<" in html and ">wv<" in html

    def test_cpp_stays_literal(self, render):
        text = "C++是最好的语言，C++是最好的语言"
        html = render(text)
        assert "markup-underline" not in html
        assert text in html

    def test_word_char_attached_delimiters_literal(self, render):
        assert "markup-highlight" not in render("x==1==y")
        assert "markup-wavyline" not in render("v1~2~3")
        assert "C++17" in render("C++17")

    def test_delimiter_after_word_token_literal(self, render):
        html = render("**C**++不是下划线++")
        assert '<strong class="strong">C</strong>' in html
        assert "markup-underline" not in html

    def test_whitespace_wrapped_content_rejected(self, render):
        assert "markup-underline" not in render("++ 文字 ++")
        assert "markup-highlight" not in render("a == b == c")
        assert "markup-wavyline" not in render("~ 文字 ~")

    def test_skip_longer_runs_pair_later(self, render):
        assert 'class="markup-highlight"' in render("前面 === 后面 ==高亮==")
        assert 'class="markup-underline"' in render("+++ 然后 ++下划线++")

    def test_intraword_cjk_markup(self, render):
        html = render("把++重点++标出==高亮==和~波浪~")
        assert 'class="markup-underline"' in html
        assert 'class="markup-highlight"' in html
        assert 'class="markup-wavyline"' in html

    def test_superscript_after_word_char(self, render):
        html = render("x^2^ + y^10^ = z")
        assert html.count('class="markup-superscript"') == 2
        assert '<sup class="markup-superscript">2</sup>' in html
        assert '<sup class="markup-superscript">10</sup>' in html

    def test_unpaired_carets_literal(self, render):
        assert "markup-superscript" not in render("a ^ b ^ c")
        assert "markup-superscript" not in render("2^10 is 1024")
        assert "markup-superscript" not in render("^ leading caret")

    def test_superscript_leaves_ruby_hat(self, render):
        # 真正归属在 T7 ruby 扩展验证 data-format；此处仅确认不被上标吞掉
        html = render("[汉字]^(han-zi)")
        assert "markup-superscript" not in html


class TestMarkupVsStrikethrough:
    def test_del_with_theme_class(self, render):
        assert '<del class="del">gone</del>' in render("~~gone~~")

    def test_wavyline_distinct_from_strikethrough(self, render):
        html = render("~~gone~~ and ~wave~")
        assert '<del class="del">gone</del>' in html
        assert 'class="markup-wavyline"' in html


class TestToc:
    def test_nested_toc_skips_h1(self, render):
        html = render(
            "# Title\n\n[TOC]\n\n## Section A\n\n### Sub A1\n\n## Section B"
        )
        assert "markdown-toc" in html
        assert "Section A" in html
        assert "Sub A1" in html
        assert 'href="#1"' in html
        assert 'href="#0"' not in html
        assert "toc-level-3" in html

    def test_empty_without_subheadings(self, render):
        html = render("# Only Title\n\n[TOC]")
        assert "markdown-toc" not in html

    def test_toc_literal_inside_fence(self, render):
        html = render("# H\n\n```\n[TOC]\n```")
        assert "markdown-toc" not in html
        assert "[TOC]" in html

    def test_toc_collects_later_headings(self, render):
        # walkTokens 先于渲染遍历全树：[TOC] 位于标题之前仍能列出后文标题
        html = render("[TOC]\n\n## Later")
        assert "markdown-toc" in html
        assert ">Later<" in html


class TestSlider:
    def test_horizontal_scroll_container(self, render):
        html = render(
            "<![alt1](https://example.com/1.png),"
            "![alt2](https://example.com/2.png)>"
        )
        assert 'src="https://example.com/1.png"' in html
        assert 'src="https://example.com/2.png"' in html
        assert 'alt="alt1"' in html
        assert "overflow-x: scroll" in html
        assert "左右滑动看更多" in html

    def test_non_slider_line_stays_paragraph(self, render):
        html = render("plain <![ text")
        assert "horizontal" not in html
