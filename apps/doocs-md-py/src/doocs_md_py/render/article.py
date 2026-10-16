"""独立文章渲染（内联全量 CSS，无浏览器依赖）。

upstream: packages/mcp-server/src/render-article.ts（buildRenderedOutput 1:1）
         packages/mcp-server/src/config-options.ts（defaultRenderOptions）
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from importlib.resources import files

from .code_themes import CODE_BLOCK_THEME_OPTIONS, fetch_code_block_css
from .css import (
    CSSVariableConfig,
    escape_style_content,
    generate_css_variables,
    generate_heading_styles,
    process_css,
)
from .markdown import post_process_html, render_markdown
from . import init_renderer
from .options import IOpts
from .renderer import Renderer

# upstream: config-options.ts:138-156
DEFAULT_RENDER_OPTIONS = {
    "theme": "default",
    "primary_color": "#0F4C81",
    # upstream: config-options.ts:33（逐字保留逗号后空格的不一致形态）
    "font_family": (
        "-apple-system-font,BlinkMacSystemFont, Helvetica Neue, PingFang SC, "
        "Hiragino Sans GB , Microsoft YaHei UI , Microsoft YaHei ,Arial,sans-serif"
    ),
    "font_size": "16px",
    "line_height": "1.75",
    "block_spacing": "1",
    "link_color": "#576b95",
    "blockquote_background": "default",
    "legend": "alt",  # legendOptions[3]
    "code_block_theme": CODE_BLOCK_THEME_OPTIONS[0]["value"],
    "is_mac_code_block": False,
    "is_show_line_number": False,
    "cite_status": False,
    "count_status": False,
    "theme_mode": "light",
    "is_use_indent": False,
    "is_use_justify": False,
}


def _load_css_file(filename: str) -> str:
    """upstream: render-article.ts:46-56（包数据资产，模块加载期读取）。"""
    return (
        files("doocs_md_py.render.assets")
        .joinpath(filename)
        .read_text(encoding="utf-8")
    )


# upstream: render-article.ts:58-63
BASE_CSS_CONTENT = _load_css_file("base.css")
THEME_MAP = {
    "default": _load_css_file("default.css"),
    "grace": _load_css_file("grace.css"),
    "simple": _load_css_file("simple.css"),
}


@dataclass(slots=True)
class RenderArticleInput:
    """upstream: render-article.ts:17-38 RenderMarkdownInput。"""

    markdown: str
    theme: str | None = None
    primary_color: str | None = None
    font_family: str | None = None
    font_size: str | None = None
    line_height: str | None = None
    block_spacing: str | None = None
    link_color: str | None = None
    blockquote_background: str | None = None
    legend: str | None = None
    is_mac_code_block: bool | None = None
    is_show_line_number: bool | None = None
    cite_status: bool | None = None
    count_status: bool | None = None
    theme_mode: str | None = None
    is_use_indent: bool | None = None
    is_use_justify: bool | None = None
    heading_styles: dict[str, str] | None = None
    code_block_theme: str | None = None
    custom_css: str | None = None


@dataclass(slots=True)
class RenderedArticle:
    """upstream: render-article.ts:166-173 返回体。"""

    html: str
    front_matter: dict
    reading_time: dict = field(default_factory=lambda: {"words": 0, "minutes": 0})


def normalize_heading_styles(
    heading_styles: dict[str, str] | None,
) -> dict[str, str] | None:
    """upstream: render-article.ts:96-106。

    逐字行为：仅排除 falsy 与 ``default``（``custom`` 保留，
    由 generate_heading_styles 内部再跳过）。
    """
    if not heading_styles:
        return None
    normalized: dict[str, str] = {}
    for level, style in heading_styles.items():
        if style and style != "default":
            normalized[level] = style
    return normalized or None


def build_rendered_output(
    input_data: RenderArticleInput,
    *,
    code_css_fetcher: Callable[[str], str] | None = None,
) -> RenderedArticle:
    """upstream: render-article.ts:108-174（Python 侧同步等价）。"""
    defaults = DEFAULT_RENDER_OPTIONS

    def opt(name: str):  # JS ``input.x ?? default``：None 才回退
        value = getattr(input_data, name)
        return defaults[name] if value is None else value

    theme = opt("theme")
    primary_color = opt("primary_color")
    font_family = opt("font_family")
    font_size = opt("font_size")
    line_height = opt("line_height")
    block_spacing = opt("block_spacing")
    link_color = opt("link_color")
    blockquote_background = opt("blockquote_background")
    legend = opt("legend")
    code_block_theme = opt("code_block_theme")
    heading_styles = normalize_heading_styles(input_data.heading_styles)

    renderer: Renderer = init_renderer(
        IOpts(
            is_mac_code_block=opt("is_mac_code_block"),
            is_show_line_number=opt("is_show_line_number"),
            cite_status=opt("cite_status"),
            count_status=opt("count_status"),
            theme_mode=opt("theme_mode"),
            legend=legend,
        )
    )

    rendered = render_markdown(input_data.markdown, renderer)
    base_html = rendered["html"]
    reading = rendered["reading_time"]
    processed_html = post_process_html(base_html, reading, renderer)
    # upstream:132 行第二次解析，专供 frontmatter（与 renderMarkdown 内部各解析一次）
    parsed = renderer.parse_front_matter_and_content(input_data.markdown)

    css_config = CSSVariableConfig(
        primary_color=primary_color,
        font_family=font_family,
        font_size=font_size,
        line_height=line_height,
        block_spacing=block_spacing,
        link_color=link_color,
        blockquote_background=blockquote_background,
        is_use_indent=opt("is_use_indent"),
        is_use_justify=opt("is_use_justify"),
        heading_styles=heading_styles,
    )

    variables_css = generate_css_variables(css_config)
    heading_styles_css = generate_heading_styles(css_config)
    # MCP 路径单取一个主题（不叠加 default；浏览器注入路径才有叠加逻辑）
    theme_css = THEME_MAP.get(theme) or THEME_MAP["default"]
    fetcher = code_css_fetcher or fetch_code_block_css
    hljs_css = fetcher(code_block_theme) if code_block_theme else ""
    raw_custom_css = input_data.custom_css
    custom_css = escape_style_content(
        raw_custom_css.strip() if raw_custom_css is not None else ""
    )

    merged_css_parts = [
        variables_css,
        BASE_CSS_CONTENT,
        theme_css,
        heading_styles_css,
        hljs_css,
        custom_css,
    ]
    merged_css = "\n\n".join(part for part in merged_css_parts if part)
    merged_css = process_css(merged_css)

    html = f"<style>\n{merged_css}\n</style>\n{processed_html}"

    return RenderedArticle(
        html=html,
        front_matter=parsed.yaml_data,
        reading_time={"words": reading.words, "minutes": reading.minutes},
    )
