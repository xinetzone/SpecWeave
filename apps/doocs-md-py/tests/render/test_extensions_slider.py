"""横向滑动图片块扩展测试（upstream: packages/core/src/extensions/slider.ts）。

两层断言：
1. 经完整渲染管线（``init_renderer()``）验证 ``<![...](...)>`` 整行语法被消费为
   横滑 section、残留文本或非整行匹配时退回段落；
2. 直接驱动 ``slider_block``/``render_slider`` 验证 markdown-it 规则协议
   （``silent`` 只探测不消费；缩进代码块行不得起块）与渲染守卫。
"""

import pytest
from markdown_it import MarkdownIt
from markdown_it.rules_block import StateBlock
from markdown_it.token import Token

from doocs_md_py.render import init_renderer
from doocs_md_py.render.extensions.slider import render_slider, slider_block

SLIDER = "<![图一](https://example.com/a.png),![图二](https://example.com/b.png)>"


@pytest.fixture()
def render():
    renderer = init_renderer()

    def _render(md: str) -> str:
        return renderer.render_markdown_to_html(md)

    return _render


@pytest.fixture()
def md() -> MarkdownIt:
    instance = MarkdownIt()
    instance.block.ruler.before("paragraph", "horizontal_slider", slider_block)
    return instance


# ---- 渲染管线 ----


def test_multi_image_container_and_caption(render):
    html = render(SLIDER)
    assert 'src="https://example.com/a.png"' in html
    assert 'src="https://example.com/b.png"' in html
    assert 'alt="图一"' in html
    assert 'title="图二"' in html
    assert "overflow-x: scroll" in html
    assert "white-space: nowrap" in html
    assert "左右滑动看更多" in html


def test_empty_alt_and_src_kept_verbatim(render):
    html = render("<![first](u1.png),![](u2.png)>")
    assert 'alt="first"' in html
    # 空 alt/src 不做兜底替换（img[0] or "" → 空串）
    assert 'src="u2.png" alt="" title=""' in html


def test_trailing_text_after_closer_is_not_a_slider(render):
    # 闭合 > 后仍有残留文本：match.end() != len(line) → 退回段落
    html = render("<![a](b.png)> tail")
    assert "overflow-x: scroll" not in html
    assert "tail" in html


def test_slider_must_own_the_whole_line(render):
    assert "overflow-x: scroll" not in render("plain <![ text")
    assert "overflow-x: scroll" in render("  " + SLIDER + "  ")


def test_slider_inside_fence_is_literal(render):
    html = render("```\n" + SLIDER + "\n```")
    assert "overflow-x: scroll" not in html


# ---- 规则协议（markdown-it block rule） ----


def test_slider_block_returns_true_and_pushes_token(md):
    src = "<![a](b.png)>"
    state = StateBlock(src, md, {}, [])
    assert slider_block(state, 0, 1, False) is True
    assert state.line == 1
    assert [token.type for token in state.tokens] == ["horizontal_slider"]
    assert state.tokens[0].content == "![a](b.png)"
    assert state.tokens[0].map == [0, 1]


def test_slider_block_silent_probes_without_consuming(md):
    src = "<![a](b.png)>"
    state = StateBlock(src, md, {}, [])
    assert slider_block(state, 0, 1, True) is True
    # silent 只探测：不推进 line、不产 token
    assert state.line == 0
    assert state.tokens == []


def test_slider_block_skips_indented_code_block_line(md):
    # 4 空格缩进 → is_code_block 为真，缩进代码块优先由 code 规则消费
    state = StateBlock("    <![a](b.png)>", md, {}, [])
    assert state.is_code_block(0) is True
    assert slider_block(state, 0, 1, False) is False


@pytest.mark.parametrize(
    "src",
    ["plain text", "<![a](b.png) extra", "<![a](b.png", "<![]", "  "],
)
def test_slider_block_rejects_non_slider_lines(md, src):
    state = StateBlock(src, md, {}, [])
    assert slider_block(state, 0, 1, False) is False


# ---- 渲染守卫 ----


def test_render_slider_without_image_returns_empty():
    # 块规则正则强制 content 至少含一个 ![](…)，此处为渲染侧防御守卫
    token = Token("horizontal_slider", "", 0)
    token.content = "无图片内容"
    assert render_slider([token], 0, {}, {}) == ""


def test_render_slider_image_order_matches_source():
    token = Token("horizontal_slider", "", 0)
    token.content = "![b](2.png),![a](1.png)"
    html = render_slider([token], 0, {}, {})
    assert html.index('src="2.png"') < html.index('src="1.png"')
