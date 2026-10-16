"""alert 扩展对拍（upstream: extensions.test.ts + alert.ts 全变体表）。

覆盖 GFM blockquote 提醒、Obsidian ::: 容器、34 个内置类型别名、
自定义标题（含非 ASCII）、HTML 转义与正文内联 Markdown。
"""

import pytest

from doocs_md_py.render import init_renderer
from doocs_md_py.render.extensions.alert import _ucfirst
from doocs_md_py.render.extensions.alert_data import VARIANTS


@pytest.fixture()
def render():
    renderer = init_renderer()

    def _render(md: str) -> str:
        return renderer.render_markdown_to_html(md)

    return _render


def _alert(type_: str, body: str = "body text") -> str:
    return f"> [!{type_.upper()}]\n> {body}"


class TestAllVariants:
    @pytest.mark.parametrize("vtype, vtitle, icon", VARIANTS)
    def test_each_variant_gfm(self, render, vtype, vtitle, icon):
        out = render(_alert(vtype))
        expected_title = vtitle if vtitle is not None else _ucfirst(vtype)
        assert f"markdown-alert-{vtype}" in out
        assert f"alert-title-{vtype}" in out
        assert f"alert-icon-{vtype}" in out  # 图标 class 注入
        assert f">{expected_title}</p>" in out
        assert "body text" in out

    def test_variants_count(self):
        # 6 GFM + 18 Obsidian + 10 学术 = 34
        assert len(VARIANTS) == 34

    @pytest.mark.parametrize(
        "raw_name",
        ["warning", "Warning", "WARNING", "WaRnInG"],
    )
    def test_case_insensitive(self, render, raw_name):
        out = render(f"> [!{raw_name}]\n> x")
        assert "markdown-alert-warning" in out
        assert ">Warning</p>" in out


class TestCustomTitle:
    def test_cjk_title(self, render):
        out = render("> [!NOTE] 自定义标题\n> body")
        assert "自定义标题" in out
        assert "body" in out

    def test_pro_tip_container(self, render):
        out = render(":::tip Pro Tip\nContainer body\n:::")
        assert "markdown-alert-tip" in out
        assert "Pro Tip" in out
        assert "Container body" in out

    def test_html_in_title_escaped(self, render):
        out = render("> [!NOTE] <b>bold</b>\n> body")
        assert "<b>bold</b>" not in out
        assert "&lt;b&gt;" in out

    def test_inline_markdown_in_title_is_literal(self, render):
        out = render("> [!NOTE] *斜体标题*\n> body")
        assert "*斜体标题*" in out
        assert "<em>" not in out

    def test_blank_custom_title_falls_back(self, render):
        out = render("> [!WARNING]   \n> body")
        assert ">Warning</p>" in out


class TestCustomName:
    def test_cjk_name_custom_variant(self, render):
        out = render("> [!我的提示]\n> 中文名字")
        assert "markdown-alert-custom" in out
        assert "alert-title-custom" in out
        assert "alert-icon-custom" not in out  # 自定义类型无图标
        assert ">我的提示</p>" in out
        assert "中文名字" in out

    def test_unknown_latin_name(self, render):
        out = render("> [!mytip]\n> x")
        assert "markdown-alert-custom" in out
        assert ">Mytip</p>" not in out
        assert ">mytip</p>" in out


class TestContainer:
    def test_basic_container(self, render):
        out = render(":::tip\nBody\n:::")
        assert "markdown-alert" in out
        assert "Body" in out

    def test_container_with_heading_and_list(self, render):
        out = render(":::info\n# Heading\n\n- a\n- b\n:::")
        assert "markdown-alert-info" in out
        assert 'data-heading="true"' in out
        assert out.count("<li") == 2
        assert "• a" in out and "• b" in out

    def test_container_inline_math_body_literal_for_now(self, render):
        # KaTeX 占位在 T7 接入；当前 $...$ 正文保持透传
        out = render(":::theorem Theorem 1\n$E = mc^2$\n:::")
        assert "markdown-alert-theorem" in out
        assert "Theorem 1" in out
        assert "$E = mc^2$" in out

    def test_unclosed_container_is_paragraph(self, render):
        out = render(":::tip\nbody no close")
        assert "markdown-alert" not in out
        assert ":::tip" in out

    def test_container_without_name_is_paragraph(self, render):
        out = render(":::\nbody\n:::")
        assert "markdown-alert" not in out

    def test_container_body_multiline(self, render):
        out = render(":::note\nline one\n\nline two\n:::")
        assert "line one" in out
        assert "line two" in out


class TestBlockquoteGuards:
    def test_plain_blockquote_untouched(self, render):
        out = render("> just a quote")
        assert "markdown-alert" not in out
        assert "just a quote" in out

    def test_empty_marker_not_alert(self, render):
        out = render("> [!]\n> body")
        assert "markdown-alert" not in out

    def test_marker_not_first_line(self, render):
        # 首行空行后才出现标记，不构成 alert
        out = render(">\n> [!NOTE]\n> body")
        assert "markdown-alert" not in out

    def test_marker_in_fence(self, render):
        out = render("```\n> [!NOTE]\n> body\n```")
        assert "markdown-alert" not in out
        assert "<pre" in out

    def test_marker_in_paragraph(self, render):
        out = render("[!NOTE] plain text")
        assert "markdown-alert" not in out

    def test_alert_with_empty_body(self, render):
        out = render("> [!NOTE]")
        assert "markdown-alert-note" in out
        assert ">Note</p>" in out
        assert '<p class="p">' not in out

    def test_body_inline_markdown(self, render):
        out = render("> [!TIP]\n> use **bold** here")
        assert "<strong" in out and "bold</strong>" in out

    def test_hard_break_after_title(self, render):
        out = render("> [!NOTE] title  \n> body")
        assert ">title</p>" in out
        assert "body" in out
        assert "title  " not in out
