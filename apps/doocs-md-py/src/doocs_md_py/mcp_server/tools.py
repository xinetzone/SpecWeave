"""13 个 MCP 工具注册表（upstream: packages/mcp-server/src/index.ts:150-431）。

上游 SDK 的 ``registerTool(name, {description, inputSchema}, handler)`` 在此映射为
``ToolSpec``；handler 返回 payload，由 stdio 层包成
``{content:[{type:'text', text: JSON.stringify(payload)}]}``。
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..render.article import RenderArticleInput, build_rendered_output
from ..render.code_themes import CODE_BLOCK_THEME_OPTIONS
from .options import (
    AI_SERVICE_OPTIONS,
    BLOCK_SPACING_OPTIONS,
    BLOCKQUOTE_BACKGROUND_OPTIONS,
    COLOR_OPTIONS,
    EXTENSION_DOCS,
    FONT_FAMILY_OPTIONS,
    FONT_SIZE_OPTIONS,
    HEADING_LEVELS,
    HEADING_STYLE_OPTIONS,
    LEGEND_OPTIONS,
    LINE_HEIGHT_OPTIONS,
    LINK_COLOR_OPTIONS,
    RENDERER_OPTION_DOCS,
    THEME_OPTIONS,
)
from .schema import RENDER_MARKDOWN_INPUT_SCHEMA, parse_render_input

# upstream: index.ts:145-148
SERVER_NAME = "md-mcp-server"
SERVER_VERSION = "2.1.1"

# 无入参工具的 inputSchema（MCP 规范要求 tools/list 恒有 inputSchema 字段）
NO_INPUT_SCHEMA: dict[str, Any] = {"type": "object", "properties": {}}


class ToolInputError(Exception):
    """入参校验失败（zod ``.parse`` 等价）；stdio 层转为 ``isError: true`` 结果。"""

    def __init__(self, messages: list[str]) -> None:
        super().__init__("\n".join(messages))
        self.messages = tuple(messages)


def _label_value_desc(options: tuple[dict[str, Any], ...]) -> list[dict[str, Any]]:
    """``options.map(o => ({label, value, description}))`` 的统一投影。"""
    return [
        {"label": option["label"], "value": option["value"], "description": option["desc"]}
        for option in options
    ]


# JSON 入参键名（camelCase）→ RenderArticleInput 字段名（snake_case）；
# upstream: index.ts:26-137 的 20 个 zod 字段与 schema.py 的 properties 一一对应，
# 由 tests/mcp/test_mcp_server.py::test_render_input_field_mapping_is_total 双向锁定。
RENDER_INPUT_FIELDS: dict[str, str] = {
    "markdown": "markdown",
    "theme": "theme",
    "primaryColor": "primary_color",
    "fontFamily": "font_family",
    "fontSize": "font_size",
    "lineHeight": "line_height",
    "blockSpacing": "block_spacing",
    "linkColor": "link_color",
    "blockquoteBackground": "blockquote_background",
    "legend": "legend",
    "isMacCodeBlock": "is_mac_code_block",
    "isShowLineNumber": "is_show_line_number",
    "citeStatus": "cite_status",
    "countStatus": "count_status",
    "themeMode": "theme_mode",
    "isUseIndent": "is_use_indent",
    "isUseJustify": "is_use_justify",
    "headingStyles": "heading_styles",
    "codeBlockTheme": "code_block_theme",
    "customCSS": "custom_css",
}


def _render_markdown(args: dict[str, Any], *, code_css_fetcher: Callable[[str], str] | None = None):
    """upstream: index.ts:160-163（buildRenderedOutput(args) → jsonText）。"""
    parsed, errors = parse_render_input(args)
    if errors:
        raise ToolInputError(errors)
    input_data = RenderArticleInput(**{RENDER_INPUT_FIELDS[key]: value for key, value in parsed.items()})
    article = build_rendered_output(input_data, code_css_fetcher=code_css_fetcher)
    return {
        "html": article.html,
        "frontMatter": article.front_matter,
        "readingTime": article.reading_time,
    }


# upstream: index.ts:173-179
def _list_themes(_args: dict[str, Any], **_: Any):
    return {
        "themes": [
            {"value": theme["value"], "label": theme["label"], "author": theme["desc"] or "official"}
            for theme in THEME_OPTIONS
        ]
    }


# upstream: index.ts:190-196
def _list_colors(_args: dict[str, Any], **_: Any):
    return {
        "colors": [
            {"value": color["value"], "label": color["label"], "description": color["desc"]}
            for color in COLOR_OPTIONS
        ]
    }


# upstream: index.ts:204-210
def _list_fonts(_args: dict[str, Any], **_: Any):
    return {"fonts": _label_value_desc(FONT_FAMILY_OPTIONS)}


# upstream: index.ts:218-224
def _list_font_sizes(_args: dict[str, Any], **_: Any):
    return {"fontSizes": _label_value_desc(FONT_SIZE_OPTIONS)}


# upstream: index.ts:232-238
def _list_legend_formats(_args: dict[str, Any], **_: Any):
    return {"legendFormats": _label_value_desc(LEGEND_OPTIONS)}


# upstream: index.ts:246-254
def _list_heading_styles(_args: dict[str, Any], **_: Any):
    return {
        "headingStyles": _label_value_desc(HEADING_STYLE_OPTIONS),
        "levels": list(HEADING_LEVELS),
    }


# upstream: index.ts:261-273
def _list_spacing_options(_args: dict[str, Any], **_: Any):
    return {
        "lineHeights": _label_value_desc(LINE_HEIGHT_OPTIONS),
        "blockSpacings": _label_value_desc(BLOCK_SPACING_OPTIONS),
    }


# upstream: index.ts:280-292
def _list_color_options(_args: dict[str, Any], **_: Any):
    return {
        "linkColors": _label_value_desc(LINK_COLOR_OPTIONS),
        "blockquoteBackgrounds": _label_value_desc(BLOCKQUOTE_BACKGROUND_OPTIONS),
    }


# upstream: index.ts:299-306
def _list_code_block_themes(_args: dict[str, Any], **_: Any):
    return {"codeBlockThemes": _label_value_desc(CODE_BLOCK_THEME_OPTIONS)}


# upstream: index.ts:316-323
def _list_ai_services(_args: dict[str, Any], **_: Any):
    return {
        "services": [
            {
                "value": service["value"],
                "label": service["label"],
                "endpoint": service["endpoint"],
                "models": list(service["models"]),
            }
            for service in AI_SERVICE_OPTIONS
        ]
    }


# upstream: index.ts:333-398
def _explain_extensions(_args: dict[str, Any], **_: Any):
    return {"extensions": [dict(extension) for extension in EXTENSION_DOCS]}


# upstream: index.ts:408-430
def _get_renderer_options(_args: dict[str, Any], **_: Any):
    return {"options": [dict(option) for option in RENDERER_OPTION_DOCS]}


@dataclass(frozen=True, slots=True)
class ToolSpec:
    """``registerTool`` 等价条目（键序 name → description → inputSchema 与上游一致）。"""

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., dict[str, Any]]

    def metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


# upstream: index.ts:150-431（注册顺序即 tools/list 顺序）
TOOLS: tuple[ToolSpec, ...] = (
    ToolSpec(
        name="render_markdown",
        description=(
            "Render Markdown text to styled HTML using the doocs/md rendering engine. "
            "The output is ready to be used in WeChat Official Accounts (公众号) and other platforms. "
            "Supports standard Markdown plus: KaTeX math, Mermaid diagrams, PlantUML, footnotes, alerts, "
            "ruby annotations, sliders, and table-of-contents."
        ),
        input_schema=RENDER_MARKDOWN_INPUT_SCHEMA,
        handler=_render_markdown,
    ),
    ToolSpec(
        name="list_themes",
        description=(
            "List all available visual themes for the doocs/md Markdown editor. "
            "Each theme changes colours, typography, and spacing of the rendered output."
        ),
        input_schema=NO_INPUT_SCHEMA,
        handler=_list_themes,
    ),
    ToolSpec(
        name="list_colors",
        description=(
            "List all available primary accent colors for the doocs/md Markdown editor. "
            "Each color is applied via CSS variable --md-primary-color and affects headings, links, alerts, etc. "
            "You can also pass any custom hex color string directly to render_markdown."
        ),
        input_schema=NO_INPUT_SCHEMA,
        handler=_list_colors,
    ),
    ToolSpec(
        name="list_fonts",
        description="List preset font family options for render_markdown.",
        input_schema=NO_INPUT_SCHEMA,
        handler=_list_fonts,
    ),
    ToolSpec(
        name="list_font_sizes",
        description="List preset font size options for render_markdown.",
        input_schema=NO_INPUT_SCHEMA,
        handler=_list_font_sizes,
    ),
    ToolSpec(
        name="list_legend_formats",
        description="List image caption (legend) format options for render_markdown.",
        input_schema=NO_INPUT_SCHEMA,
        handler=_list_legend_formats,
    ),
    ToolSpec(
        name="list_heading_styles",
        description="List heading style presets usable in render_markdown headingStyles.",
        input_schema=NO_INPUT_SCHEMA,
        handler=_list_heading_styles,
    ),
    ToolSpec(
        name="list_spacing_options",
        description="List preset line height and block spacing options for render_markdown.",
        input_schema=NO_INPUT_SCHEMA,
        handler=_list_spacing_options,
    ),
    ToolSpec(
        name="list_color_options",
        description="List preset link colour and blockquote background options for render_markdown.",
        input_schema=NO_INPUT_SCHEMA,
        handler=_list_color_options,
    ),
    ToolSpec(
        name="list_code_block_themes",
        description="List highlight.js code block theme URLs for render_markdown.",
        input_schema=NO_INPUT_SCHEMA,
        handler=_list_code_block_themes,
    ),
    ToolSpec(
        name="list_ai_services",
        description=(
            "List all built-in AI service providers supported by doocs/md. "
            "Each entry includes the provider name, OpenAI-compatible endpoint URL, and available models. "
            "Use this to help users pick the right AI service and model."
        ),
        input_schema=NO_INPUT_SCHEMA,
        handler=_list_ai_services,
    ),
    ToolSpec(
        name="explain_extensions",
        description=(
            "Describe all Markdown extensions supported by doocs/md beyond standard CommonMark. "
            "Returns the extension name, a description, and a usage example for each."
        ),
        input_schema=NO_INPUT_SCHEMA,
        handler=_explain_extensions,
    ),
    ToolSpec(
        name="get_renderer_options",
        description=(
            "Describe every configuration option accepted by the doocs/md renderer. "
            "Use this to understand what parameters are available when calling render_markdown."
        ),
        input_schema=NO_INPUT_SCHEMA,
        handler=_get_renderer_options,
    ),
)

TOOLS_BY_NAME: dict[str, ToolSpec] = {tool.name: tool for tool in TOOLS}


def list_tools_payload() -> list[dict[str, Any]]:
    """tools/list 的 ``tools`` 数组。"""
    return [tool.metadata() for tool in TOOLS]


def call_tool(
    name: str, args: dict[str, Any] | None = None, *, code_css_fetcher: Callable[[str], str] | None = None
) -> dict[str, Any]:
    """调用工具并返回 payload；未知工具抛 ``KeyError``（stdio 层转 -32602）。"""
    tool = TOOLS_BY_NAME[name]
    return tool.handler(args or {}, code_css_fetcher=code_css_fetcher)
