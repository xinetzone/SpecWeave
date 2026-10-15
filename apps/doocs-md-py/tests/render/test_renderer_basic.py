"""renderer-impl.ts 17 规则黄金样例（归一化 DOM 比对）。"""

import pytest

from doocs_md_py.render import IOpts, init_renderer
from doocs_md_py.render.domcompare import assert_dom_equal


@pytest.fixture()
def renderer():
    return init_renderer()


class TestHeading:
    def test_heading_structure(self, renderer):
        html = renderer.render_markdown_to_html("## Subtitle")
        assert_dom_equal('<h2 class="h2" data-heading="true">Subtitle</h2>', html)

    def test_headings_collected_plain_text(self, renderer):
        renderer.render_markdown_to_html("# Title\n\n## Sub `code` & **bold**\n\n### Third")
        assert [h.as_dict() for h in renderer.get_headings()] == [
            {"level": 1, "text": "Title"},
            {"level": 2, "text": "Sub code & bold"},
            {"level": 3, "text": "Third"},
        ]

    def test_heading_entities_decoded_like_text_content(self, renderer):
        renderer.render_markdown_to_html("# Fish &amp; Chips &mdash; &#x2026; &nbsp;end")
        assert renderer.get_headings()[0].text == "Fish & Chips — … \u00A0end"


class TestParagraph:
    def test_plain_paragraph(self, renderer):
        assert_dom_equal('<p class="p">Hello</p>', renderer.render_markdown_to_html("Hello"))

    def test_figure_paragraph_unwrapped(self, renderer):
        html = renderer.render_markdown_to_html("![a](u.png)")
        assert "<p" not in html
        assert html.startswith("<figure>")

    def test_breaks_enabled(self, renderer):
        html = renderer.render_markdown_to_html("line1\nline2")
        assert_dom_equal('<p class="p">line1<br>line2</p>', html)


class TestBlockquote:
    def test_blockquote(self, renderer):
        html = renderer.render_markdown_to_html("> quote")
        assert_dom_equal(
            '<blockquote class="blockquote"><p class="p">quote</p></blockquote>', html
        )


class TestCode:
    def test_plaintext_code_block_structure(self, renderer):
        html = renderer.render_markdown_to_html("```\nraw <x> &\n```")
        assert html.startswith('<pre class="hljs code__pre">')
        assert 'class="mac-sign"' in html
        # 无 info 时 marked lang 为空串：class 后缀为空且 pending 也为空（忠实上游）
        assert 'class="language-"' in html
        assert 'data-language-pending=""' in html
        assert "raw&nbsp;&lt;x&gt;&nbsp;&amp;" in html

    def test_unregistered_language_pending_attrs(self, renderer):
        html = renderer.render_markdown_to_html('```rust\nlet x = "q";\n```')
        assert 'data-language-pending="rust"' in html
        assert "data-raw-code=" in html
        assert "let x = &quot;q&quot;;" in html
        assert 'data-show-line-number="false"' in html
        assert 'class="language-rust"' in html

    def test_diff_lang_green_red_lines(self, renderer):
        html = renderer.render_markdown_to_html("```diff-python\n+keep\n-drop\n ctx\n```")
        assert 'class="language-diff-python"' in html
        assert "background:rgba(80,200,80,.18);" in html
        assert "background:rgba(255,80,80,.18);" in html
        assert "#52c41a" in html and "#ff4d4f" in html

    def test_line_number_layout(self):
        renderer = init_renderer(IOpts(is_show_line_number=True))
        html = renderer.render_markdown_to_html("```\na\nb\n```")
        assert 'class="line-numbers"' in html
        assert 'class="code-scroll"' in html
        assert "line-height:1.75" in html
        assert ">1</section>" in html and ">2</section>" in html

    def test_codespan(self, renderer):
        assert_dom_equal(
            '<p class="p"><code class="codespan">a &amp; b</code></p>',
            renderer.render_markdown_to_html("`a & b`"),
        )


class TestList:
    def test_unordered_prefix(self, renderer):
        html = renderer.render_markdown_to_html("- a\n- b")
        assert_dom_equal(
            '<ul class="ul"><li class="listitem">• a</li><li class="listitem">• b</li></ul>',
            html,
        )

    def test_ordered_prefix_and_start(self, renderer):
        html = renderer.render_markdown_to_html("3. third\n4. fourth")
        assert_dom_equal(
            '<ol class="ol" start="3">'
            '<li class="listitem">3. third</li>'
            '<li class="listitem">4. fourth</li></ol>',
            html,
        )

    def test_nested_lists_counters(self, renderer):
        html = renderer.render_markdown_to_html("1. a\n   - x\n   - y\n2. b")
        assert_dom_equal(
            '<ol class="ol">'
            '<li class="listitem">1. a'
            '<ul class="ul"><li class="listitem">• x</li><li class="listitem">• y</li></ul>'
            "</li>"
            '<li class="listitem">2. b</li></ol>',
            html,
        )

    def test_loose_list_unwraps_first_paragraph(self, renderer):
        # 松散列表（同一 item 两段）：首段去 p 包装，后续段落保留 <p>
        html = renderer.render_markdown_to_html("- first\n\n  second para\n")
        assert '<li class="listitem">• first<p class="p">second para</p></li>' in html


class TestImage:
    def test_figure_with_size(self, renderer):
        html = renderer.render_markdown_to_html('![cat|100x200](https://x/c.png "T")')
        assert_dom_equal(
            '<figure><img src="https://x/c.png" title="T" width="100" height="200" '
            'alt="cat"></figure>',
            html,
        )

    def test_width_only(self, renderer):
        html = renderer.render_markdown_to_html("![cat|80](u)")
        assert 'width="80"' in html
        assert "height=" not in html
        assert 'alt="cat"' in html

    def test_legend_alt(self):
        renderer = init_renderer(IOpts(legend="alt"))
        html = renderer.render_markdown_to_html("![descriptive](https://x.com/a/b/c.png)")
        assert_dom_equal(
            '<figure><img src="https://x.com/a/b/c.png" alt="descriptive">'
            '<figcaption class="figcaption">descriptive</figcaption></figure>',
            html,
        )

    def test_legend_filename(self):
        renderer = init_renderer(IOpts(legend="filename"))
        html = renderer.render_markdown_to_html("![whatever](https://x.com/a/my-file.png?v=1)")
        assert "<figcaption" in html
        assert "my-file" in html

    def test_legend_priority_alt_first(self):
        renderer = init_renderer(IOpts(legend="alt-title"))
        html = renderer.render_markdown_to_html('![alttext](u "titletext")')
        # alt 优先决定 figcaption 文案；img 的 title 属性仍保留（上游行为）
        assert '<figcaption class="figcaption">alttext</figcaption>' in html


class TestLink:
    def test_basic_link(self, renderer):
        html = renderer.render_markdown_to_html("[Doocs](https://github.com/doocs)")
        assert_dom_equal(
            '<p class="p"><a href="https://github.com/doocs" title="Doocs">Doocs</a></p>',
            html,
        )

    def test_autolink_href_equals_text_is_plain(self, renderer):
        html = renderer.render_markdown_to_html("<https://github.com/doocs>")
        assert "<a " not in html
        assert "https://github.com/doocs" in html

    def test_mp_weixin_link_preserved(self, renderer):
        html = renderer.render_markdown_to_html("[文章](https://mp.weixin.qq.com/s/abc)")
        assert 'href="https://mp.weixin.qq.com/s/abc"' in html

    def test_cite_status_footnote(self):
        renderer = init_renderer(IOpts(cite_status=True))
        html = renderer.render_markdown_to_html(
            "[a](https://e.com)\n\n[b](https://e.com)\n\n[c](https://other.com)"
        )
        # 同 link 去重复用编号
        assert "<sup>[1]</sup>" in html
        assert "<sup>[2]</sup>" in html
        footnotes = renderer.build_footnotes()
        assert footnotes.count("<sup") == 0
        assert "[1]" in footnotes and "[2]" in footnotes
        assert "https://e.com" in footnotes

    def test_cite_uses_title_when_present(self):
        renderer = init_renderer(IOpts(cite_status=True))
        html = renderer.render_markdown_to_html('[text](https://e.com "My Title")')
        assert "My Title" in html
        footnotes = renderer.build_footnotes()
        assert "My Title" in footnotes


class TestEmphasis:
    def test_strong_em_del(self, renderer):
        html = renderer.render_markdown_to_html("**a** *b* ~~c~~")
        assert_dom_equal(
            '<p class="p"><strong class="strong">a</strong> '
            '<em class="em">b</em> <del class="del">c</del></p>',
            html,
        )


class TestTable:
    def test_table_structure_and_alignment(self, renderer):
        md = "| L | C | R |\n|:--|:-:|--:|\n| a | b | c |"
        html = renderer.render_markdown_to_html(md)
        assert_dom_equal(
            '<section style="max-width: 100%; overflow: auto;'
            ' -webkit-overflow-scrolling: touch">'
            '<table class="preview-table"><thead>'
            '<th class="th" style="text-align: left">L</th>'
            '<th class="th" style="text-align: center">C</th>'
            '<th class="th" style="text-align: right">R</th>'
            "</thead><tbody><tr class=\"tr\">"
            '<td class="td" style="text-align: left">a</td>'
            '<td class="td" style="text-align: center">b</td>'
            '<td class="td" style="text-align: right">c</td>'
            "</tr></tbody></table></section>",
            html,
        )

    def test_default_alignment_left(self, renderer):
        html = renderer.render_markdown_to_html("| H |\n|---|\n| x |")
        assert 'style="text-align: left"' in html


class TestHr:
    def test_three_variants(self, renderer):
        html = renderer.render_markdown_to_html("***\n\n---\n\n___")
        assert 'hr hr-star' in html
        assert 'hr hr-dash' in html
        assert 'hr hr-underscore' in html


class TestReset:
    def test_reset_clears_headings(self, renderer):
        renderer.render_markdown_to_html("# Old")
        assert len(renderer.get_headings()) == 1
        renderer.reset({})
        assert renderer.get_headings() == []
        renderer.render_markdown_to_html("## New")
        assert [h.as_dict() for h in renderer.get_headings()] == [
            {"level": 2, "text": "New"}
        ]
