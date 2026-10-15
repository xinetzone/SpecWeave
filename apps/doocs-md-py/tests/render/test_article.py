"""render/article.py 测试（upstream: mcp-server/src/render-article.ts）。"""

import pytest

from doocs_md_py.render import article
from doocs_md_py.render.article import (
    DEFAULT_RENDER_OPTIONS,
    RenderArticleInput,
    build_rendered_output,
    normalize_heading_styles,
)

HLJS_FIXTURE = "/* hljs fixture */"


@pytest.fixture
def fake_fetcher():
    fetched: list[str] = []

    def fetch(url: str) -> str:
        fetched.append(url)
        return HLJS_FIXTURE

    fetch.fetched = fetched
    return fetch


def render(markdown: str = "# Hello\n\nworld **bold**", **kwargs):
    fetcher = kwargs.pop("_fetcher", None) or (lambda url: HLJS_FIXTURE)
    return build_rendered_output(
        RenderArticleInput(markdown=markdown, **kwargs),
        code_css_fetcher=fetcher,
    )


# ---- 默认值（upstream: config-options.ts:138-156，逐字） ----


def test_default_options_literal():
    d = DEFAULT_RENDER_OPTIONS
    assert d["theme"] == "default"
    assert d["primary_color"] == "#0F4C81"
    assert d["font_size"] == "16px"
    assert d["line_height"] == "1.75"
    assert d["block_spacing"] == "1"
    assert d["link_color"] == "#576b95"
    assert d["blockquote_background"] == "default"
    assert d["legend"] == "alt"
    assert d["theme_mode"] == "light"
    assert d["is_mac_code_block"] is False
    assert d["is_show_line_number"] is False
    assert d["cite_status"] is False
    assert d["count_status"] is False
    assert d["is_use_indent"] is False
    assert d["is_use_justify"] is False
    assert d["code_block_theme"].endswith("/github.min.css")
    assert "PingFang SC" in d["font_family"]
    assert d["font_family"].endswith(",Arial,sans-serif")


# ---- 资产加载 ----


def test_assets_loaded():
    assert "MD base theme" in article.BASE_CSS_CONTENT
    assert set(article.THEME_MAP) == {"default", "grace", "simple"}
    assert "MD default theme (classic)" in article.THEME_MAP["default"]
    assert "MD grace theme" in article.THEME_MAP["grace"]


# ---- 装配 ----


def test_default_assembly_structure_and_order(fake_fetcher):
    result = build_rendered_output(
        RenderArticleInput(markdown="# Hi\n\ntext"),
        code_css_fetcher=fake_fetcher,
    )
    html = result.html

    assert html.startswith("<style>\n:root {")
    # 默认 codeBlockTheme 触发抓取，URL 为 github 预设
    assert fake_fetcher.fetched == [DEFAULT_RENDER_OPTIONS["code_block_theme"]]

    i_variables = html.index("--md-primary-color")
    i_base = html.index("MD base theme")
    i_theme = html.index("MD default theme (classic)")
    i_hljs = html.index(HLJS_FIXTURE)
    i_style_end = html.index("</style>")
    assert i_variables < i_base < i_theme < i_hljs < i_style_end

    # 样式块后接渲染正文（容器 + 标题）
    body = html[i_style_end:]
    assert "<section" in body
    assert "data-heading" in body


def test_css_parts_joined_with_blank_line(fake_fetcher):
    result = build_rendered_output(
        RenderArticleInput(markdown="# Hi"), code_css_fetcher=fake_fetcher
    )
    # variables 与 base 之间为空行连接
    assert "}\n\n/**\n * MD base theme" in result.html


def test_grace_theme(fake_fetcher):
    result = build_rendered_output(
        RenderArticleInput(markdown="# Hi", theme="grace"),
        code_css_fetcher=fake_fetcher,
    )
    assert "MD grace theme" in result.html
    assert "MD default theme (classic)" not in result.html


def test_unknown_theme_falls_back_to_default(fake_fetcher):
    result = build_rendered_output(
        RenderArticleInput(markdown="# Hi", theme="mp:nonexistent"),
        code_css_fetcher=fake_fetcher,
    )
    assert "MD default theme (classic)" in result.html


def test_custom_css_trimmed_and_escaped(fake_fetcher):
    result = build_rendered_output(
        RenderArticleInput(
            markdown="# Hi",
            custom_css="  body { color: red }\n</style break>  ",
        ),
        code_css_fetcher=fake_fetcher,
    )
    assert "body { color: red }" in result.html
    assert "<\\/style break>" in result.html
    assert "</style break>" not in result.html.split("</style>")[0]


def test_empty_code_block_theme_skips_fetch():
    fetched = []

    def fetcher(url):
        fetched.append(url)
        return HLJS_FIXTURE

    result = build_rendered_output(
        RenderArticleInput(markdown="# Hi", code_block_theme=""),
        code_css_fetcher=fetcher,
    )
    assert fetched == []
    assert HLJS_FIXTURE not in result.html


def test_heading_styles_in_merged_css(fake_fetcher):
    result = build_rendered_output(
        RenderArticleInput(
            markdown="# Hi",
            heading_styles={"h2": "border-bottom"},
        ),
        code_css_fetcher=fake_fetcher,
    )
    assert "#output h2" in result.html
    # merged CSS 经 processCSS，var(--md-primary-color) 已解析为实际色值
    assert "border-bottom: 2px solid #0F4C81;" in result.html


def test_frontmatter_and_reading_time(fake_fetcher):
    md = "---\ntitle: 标题\n---\n# Hi\n\n这是正文内容。"
    result = build_rendered_output(
        RenderArticleInput(markdown=md), code_css_fetcher=fake_fetcher
    )
    assert result.front_matter == {"title": "标题"}
    assert result.reading_time["words"] > 0
    assert result.reading_time["minutes"] >= 0
    assert set(result.reading_time) == {"words", "minutes"}


def test_empty_frontmatter(fake_fetcher):
    result = build_rendered_output(
        RenderArticleInput(markdown="# No front matter"),
        code_css_fetcher=fake_fetcher,
    )
    assert result.front_matter == {}


def test_renderer_options_passthrough():
    # isMacCodeBlock 影响后处理内 mac-sign 的 display 值
    result = build_rendered_output(
        RenderArticleInput(markdown="```py\nprint(1)\n```", is_mac_code_block=True),
        code_css_fetcher=lambda url: "",
    )
    assert ".mac-sign" in result.html
    # mac 模式 display:flex（上游 _MAC_STYLE 模板）
    assert "display: flex" in result.html


# ---- normalizeHeadingStyles（upstream: render-article.ts:96-106） ----


def test_normalize_heading_styles_filters_default_keeps_custom():
    assert normalize_heading_styles(None) is None
    assert normalize_heading_styles({}) is None
    assert normalize_heading_styles({"h1": "default"}) is None
    # 逐字行为：custom 保留（generate_heading_styles 内部再跳过）
    assert normalize_heading_styles({"h1": "default", "h2": "custom", "h3": ""}) == {
        "h2": "custom"
    }
    assert normalize_heading_styles({"h1": "color-only"}) == {"h1": "color-only"}


def test_mac_render_without_fetcher_uses_default_signature():
    # 签名健全性：fetcher 注入位置仅为关键字参数
    with pytest.raises(TypeError):
        build_rendered_output(
            RenderArticleInput(markdown="x"), lambda url: ""  # type: ignore[arg-type]
        )
