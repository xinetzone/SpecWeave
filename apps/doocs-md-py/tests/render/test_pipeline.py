"""markdownHelpers.ts 流水线与 RendererAPI 装配测试。"""

from doocs_md_py.render import IOpts, RenderMessages, init_renderer
from doocs_md_py.render.markdown import (
    modify_html_content,
    post_process_html,
    render_markdown,
)


def test_render_markdown_returns_reading_time():
    renderer = init_renderer()
    result = render_markdown("---\ntitle: T\n---\n\n# Body", renderer)
    assert result["reading_time"].words >= 1
    assert '<h1 class="h1" data-heading="true">Body</h1>' in result["html"]


def test_post_process_wraps_container():
    renderer = init_renderer()
    out = post_process_html("<p>x</p>", renderer.parse_front_matter_and_content("x").reading_time, renderer)
    assert out.startswith('<section class="container">')
    assert out.endswith("</section>")
    # Mac 三点默认隐藏（isMacCodeBlock 缺省 false）
    assert ".hljs.code__pre > .mac-sign" in out
    assert "display: none" in out


def test_mac_code_block_flag_shows_sign():
    renderer = init_renderer(IOpts(is_mac_code_block=True))
    out = modify_html_content("x", renderer)
    assert "display: flex" in out


def test_count_status_summary_default():
    renderer = init_renderer(IOpts(count_status=True))
    out = modify_html_content("hello world", renderer)
    assert "words, about" in out
    assert "min read" in out
    assert 'class="md-blockquote"' in out


def test_count_status_custom_template():
    from doocs_md_py.render.options import CountMessages

    renderer = init_renderer(
        IOpts(count_status=True, count_messages=CountMessages(summary="単語 {words} / {minutes} 分"))
    )
    out = modify_html_content("hello", renderer)
    assert "単語 1 / 1 分" in out


def test_footnotes_appended_with_localized_title():
    renderer = init_renderer(
        IOpts(
            cite_status=True,
            render_messages=RenderMessages(footnote_title="脚注", unknown_component="", katex_loading=""),
        )
    )
    modify_html_content("[link](https://example.com)", renderer)
    headings = [h.as_dict() for h in renderer.get_headings()]
    assert headings[-1] == {"level": 4, "text": "脚注"}
    assert "https://example.com" in renderer.build_footnotes()


def test_no_footnotes_when_disabled():
    renderer = init_renderer()
    out = modify_html_content("[link](https://example.com)", renderer)
    assert "References" not in out
    assert "[1]" not in out
