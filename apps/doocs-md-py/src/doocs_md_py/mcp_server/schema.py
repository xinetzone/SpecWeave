"""render_markdown 入参 schema（upstream: packages/mcp-server/src/index.ts:24-137）。

zod 等价：``.optional().default(x)`` → JSON Schema ``default: x`` 且不入 ``required``；
``.regex(re, msg)`` → ``pattern`` + 上游自定义报错文案；``z.enum`` → ``enum``。
两条与 JS 语义的去偏（不改变接受集）：
① JS ``\\d`` 仅 ASCII，Python ``re`` 默认 Unicode → 一律写 ``[0-9]``；
② JSON Schema 无 ``/i`` 标志，hex 正则展开为 ``[0-9A-Fa-f]``。
"""

import re
from typing import Any

from ..render.code_themes import CODE_BLOCK_THEME_OPTIONS

# upstream: index.ts:24
HEADING_STYLE_ENUM = (
    "default",
    "color-only",
    "border-bottom",
    "border-left",
    "custom",
)

# upstream: index.ts:127（codeBlockThemeOptions.map(option => option.value)）
CODE_BLOCK_THEME_URLS = tuple(option["value"] for option in CODE_BLOCK_THEME_OPTIONS)

_HEADING_STYLE_PROPS = {
    level: {"type": "string", "enum": list(HEADING_STYLE_ENUM)}
    for level in ("h1", "h2", "h3", "h4", "h5", "h6")
}

# upstream: index.ts:26-137（键序即 zod 声明序；JSON.stringify 保序，故键序参与对拍）
RENDER_MARKDOWN_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "markdown": {
            "type": "string",
            "description": "The Markdown source text to render.",
        },
        "theme": {
            "type": "string",
            "enum": ["default", "grace", "simple"],
            "default": "default",
            "description": (
                "Visual theme to apply. One of: default (经典), grace (优雅), simple (简洁)."
            ),
        },
        "primaryColor": {
            "type": "string",
            "pattern": "^#[0-9A-Fa-f]{6}$",
            "default": "#0F4C81",
            "description": (
                "Primary accent color (hex). Use list_colors to see presets. Default: #0F4C81 "
                "(经典蓝). This color is applied via CSS variable --md-primary-color and "
                "affects headings, links, alerts, etc."
            ),
        },
        "fontFamily": {
            "type": "string",
            "description": (
                "Font family stack. Use list_fonts for presets or pass any CSS font-family value."
            ),
        },
        "fontSize": {
            "type": "string",
            "pattern": "^[0-9]+px$",
            "description": "Base font size (e.g. 16px). Use list_font_sizes for presets.",
        },
        "lineHeight": {
            "type": "string",
            "pattern": "^[0-9]+(?:\\.[0-9]+)?$",
            "description": "Body line height, unitless (e.g. 1.75). Use list_spacing_options for presets.",
        },
        "blockSpacing": {
            "type": "string",
            "pattern": "^[0-9]+(?:\\.[0-9]+)?$",
            "description": (
                "Multiplier for the theme's vertical block margins (e.g. 1.15 loosens by 15%). "
                "Use list_spacing_options for presets."
            ),
        },
        "linkColor": {
            "type": "string",
            "description": (
                "Link colour. Use list_color_options for presets, including var(--md-primary-color)."
            ),
        },
        "blockquoteBackground": {
            "type": "string",
            "description": (
                "Blockquote background. Use list_color_options for presets; "
                '"default" keeps each theme\'s own background.'
            ),
        },
        "legend": {
            "type": "string",
            "enum": ["title-alt", "alt-title", "title", "alt", "filename", "none"],
            "default": "alt",
            "description": "Image caption format. Use list_legend_formats for options.",
        },
        "isMacCodeBlock": {
            "type": "boolean",
            "default": False,
            "description": "Whether to render code blocks with a macOS-style title bar.",
        },
        "isShowLineNumber": {
            "type": "boolean",
            "default": False,
            "description": "Whether to show line numbers in code blocks.",
        },
        "citeStatus": {
            "type": "boolean",
            "default": False,
            "description": "Whether to render links as bottom citations (footnote style).",
        },
        "countStatus": {
            "type": "boolean",
            "default": False,
            "description": "Whether to prepend a reading-time estimate to the document.",
        },
        "themeMode": {
            "type": "string",
            "enum": ["light", "dark"],
            "default": "light",
            "description": "Colour mode used by diagram extensions (e.g. Mermaid, infographic).",
        },
        "isUseIndent": {
            "type": "boolean",
            "default": False,
            "description": "Whether to indent paragraph first lines (text-indent: 2em).",
        },
        "isUseJustify": {
            "type": "boolean",
            "default": False,
            "description": "Whether to justify paragraph text (text-align: justify).",
        },
        "headingStyles": {
            "type": "object",
            "properties": _HEADING_STYLE_PROPS,
            "description": "Per-level heading style presets. Use list_heading_styles for options.",
        },
        "codeBlockTheme": {
            "type": "string",
            "enum": list(CODE_BLOCK_THEME_URLS),
            "description": (
                "Preset highlight.js theme URL for code blocks. Use list_code_block_themes for "
                "allowed values. Defaults to the GitHub theme."
            ),
        },
        "customCSS": {
            "type": "string",
            "description": "Additional custom CSS appended after theme styles (highest priority).",
        },
    },
    "required": ["markdown"],
}

# upstream: index.ts:35/48/53/58（zod regex 的第二实参即自定义文案，逐字保留）
_PATTERN_MESSAGES = {
    "primaryColor": "Must be a valid 6-digit hex color",
    "fontSize": "Must be a pixel size like 16px",
    "lineHeight": "Must be a unitless number like 1.75",
    "blockSpacing": "Must be a unitless number like 1",
}


def _js_type(value: Any) -> str:
    """JS ``typeof`` 语义的类型名（zod 报错文案使用同一词汇）。"""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int | float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, dict):
        return "object"
    return "array"


def _enum_message(enum: list[Any], received: Any) -> str:
    """upstream: zod v3 枚举报错文案 ``Invalid enum value. Expected 'a' | 'b', received 'x'``。"""
    expected = " | ".join(
        f"'{item}'" if isinstance(item, str) else f"{item}" for item in enum
    )
    shown = f"'{received}'" if isinstance(received, str) else f"{received}"
    return f"Invalid enum value. Expected {expected}, received {shown}"


def _check(prop: dict[str, Any], field: str, value: Any) -> str | None:
    schema_type = prop["type"]
    if schema_type == "boolean":
        if not isinstance(value, bool):
            return f"Expected boolean, received {_js_type(value)}"
        return None
    if schema_type == "string":
        if not isinstance(value, str):
            return f"Expected string, received {_js_type(value)}"
        pattern = prop.get("pattern")
        if pattern and not re.fullmatch(pattern, value):
            return _PATTERN_MESSAGES[field]
        enum = prop.get("enum")
        if enum and value not in enum:
            return _enum_message(enum, value)
        return None
    if schema_type == "object":
        if not isinstance(value, dict):
            return f"Expected object, received {_js_type(value)}"
        return None
    raise AssertionError(f"unsupported schema type: {schema_type}")  # pragma: no cover


def parse_render_input(args: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """zod ``.parse`` 等价：返回（已填默认值的入参, 错误文案列表）。

    - 未知键按 zod 默认 strip 语义丢弃；
    - 缺省且带 ``default`` 的字段填默认值，其余可选字段保持缺省（``undefined``/``None`` 等价）；
    - 显式 ``null`` 视为类型错误（zod ``.optional()`` 只放宽 ``undefined``，不放宽 ``null``）。
    """
    schema = RENDER_MARKDOWN_INPUT_SCHEMA
    properties: dict[str, Any] = schema["properties"]
    errors: list[str] = []

    for field in schema["required"]:
        if field not in args:
            errors.append(f"{field}: Required")

    parsed: dict[str, Any] = {}
    for field, prop in properties.items():
        if field not in args:
            if "default" in prop:
                parsed[field] = prop["default"]
            continue
        value = args[field]
        message = _check(prop, field, value)
        if message is not None:
            errors.append(f"{field}: {message}")
            continue
        if prop["type"] == "object":
            nested: dict[str, Any] = {}
            for level, level_prop in prop["properties"].items():
                if level not in value:
                    continue
                level_message = _check(level_prop, level, value[level])
                if level_message is not None:
                    errors.append(f"headingStyles.{level}: {level_message}")
                    continue
                nested[level] = value[level]
            parsed[field] = nested
        else:
            parsed[field] = value

    return parsed, errors
