"""动态 CSS 变量与 CSS 后处理。

upstream:
- packages/core/src/theme/cssVariables.ts（generateCSSVariables/generateHeadingStyles）
- packages/core/src/theme/cssProcessor.ts（processCSS：var() 与 calc() 解析）
"""

import math
import re
from dataclasses import dataclass

# upstream: cssVariables.ts:23-26
DEFAULT_LINE_HEIGHT = "1.75"
DEFAULT_BLOCK_SPACING = "1"
DEFAULT_LINK_COLOR = "#576b95"
THEME_BLOCKQUOTE_BACKGROUND = "default"

_HEADING_LEVELS = ("h1", "h2", "h3", "h4", "h5", "h6")


@dataclass(slots=True)
class CSSVariableConfig:
    """upstream: cssVariables.ts CSSVariableConfig。"""

    primary_color: str
    font_family: str
    font_size: str
    line_height: str | None = None
    block_spacing: str | None = None
    link_color: str | None = None
    blockquote_background: str | None = None
    is_use_indent: bool | None = None
    is_use_justify: bool | None = None
    # {"h1": "color-only", ...}；值为 default/custom 时跳过
    heading_styles: dict[str, str] | None = None


def generate_css_variables(config: CSSVariableConfig) -> str:
    """upstream: cssVariables.ts:28-53。"""
    # default 主题留空不声明，让各主题的 var() fallback 生效：
    # default 保留模式感知灰底，grace/simple 无背景。
    if config.blockquote_background and (
        config.blockquote_background != THEME_BLOCKQUOTE_BACKGROUND
    ):
        blockquote_bg = (
            "\n  --md-blockquote-background: "
            f"{config.blockquote_background};"
        )
    else:
        blockquote_bg = ""

    indent = "text-indent: 2em;" if config.is_use_indent else ""
    justify = "text-align: justify;" if config.is_use_justify else ""

    return f"""
:root {{
  /* Theme config */
  --md-primary-color: {config.primary_color};
  --md-font-family: {config.font_family};
  --md-font-size: {config.font_size};
  --md-line-height: {config.line_height or DEFAULT_LINE_HEIGHT};
  --md-block-spacing: {config.block_spacing or DEFAULT_BLOCK_SPACING};
  --md-link-color: {config.link_color or DEFAULT_LINK_COLOR};{blockquote_bg}
}}

/* Paragraph indent & justify */
#output p {{
  {indent}
  {justify}
}}
  """.strip()


def generate_heading_styles(config: CSSVariableConfig) -> str:
    """upstream: cssVariables.ts:56-76。"""
    heading_styles = config.heading_styles
    if not heading_styles:
        return ""

    rules: list[str] = []
    for level in _HEADING_LEVELS:
        style = heading_styles.get(level)
        # 自定义样式在 CSS 编辑器处理；此处仅预设类型
        if style and style != "default" and style != "custom":
            rules.append(_generate_heading_css(level, style))
    return "\n\n".join(rules)


def _generate_heading_css(level: str, style: str) -> str:
    """upstream: cssVariables.ts:78-108。"""
    base_styles = """
  display: block;
  text-align: left;
  background: transparent;"""

    if style == "color-only":
        return f"""#output {level} {{
  color: var(--md-primary-color);
  background: transparent;
}}"""

    if style == "border-bottom":
        return f"""#output {level} {{{base_styles}
  padding-bottom: 0.3em;
  border-bottom: 2px solid var(--md-primary-color);
  color: var(--md-primary-color);
}}"""

    if style == "border-left":
        return f"""#output {level} {{{base_styles}
  margin-left: 0;
  padding-left: 10px;
  border-left: 4px solid var(--md-primary-color);
  color: var(--md-primary-color);
}}"""

    return ""


# ---- processCSS（upstream: cssProcessor.ts） ----

_VAR_DECL_RE = re.compile(r"--([\w-]+)\s*:\s*([^;}\n]+)")
# 第二层 fallback 捕获支持至多一层嵌套括号：[^()]*(?:\([^()]*\)[^()]*)*
_VAR_USE_RE = re.compile(
    r"var\(\s*(--[\w-]+)\s*(?:,([^()]*(?:\([^()]*\)[^()]*)*))?\)"
)
_CALC_RE = re.compile(r"calc\(([^()]+)\)")

_UNITS = r"px|em|rem|vw|vh|vmin|vmax|%|pt|pc|cm|mm|in|ex|ch"
_NUM = r"(-?[\d.]+)"
# UNIT_VAL = (-?[\d.]+)(units)?：数字 + 可选单位两个捕获组
_UNIT_VAL_GROUPED = rf"(-?[\d.]+)((?:{_UNITS}))?"
_MUL_RE = re.compile(rf"^{_UNIT_VAL_GROUPED}\s*\*\s*{_UNIT_VAL_GROUPED}$")
_DIV_RE = re.compile(rf"^{_UNIT_VAL_GROUPED}\s*/\s*{_NUM}$")
_ADD_SUB_RE = re.compile(rf"^{_UNIT_VAL_GROUPED}\s*([+-])\s*{_UNIT_VAL_GROUPED}$")


def _js_round(n: float) -> float:
    """Math.round(n*10000)/10000（JS 为 +∞ 方向半入，非 Python 银行家舍入）。"""
    return math.floor(n * 10000 + 0.5) / 10000


def _evaluate_calc_inner(expr: str) -> str:
    """upstream: cssProcessor.ts:52-80。"""
    mul = _MUL_RE.match(expr)
    if mul:
        a, ua, b, ub = mul.group(1), mul.group(2), mul.group(3), mul.group(4)
        # JS: !ua !== !ub —— 恰一个带单位
        if (ua is None) != (ub is None):
            unit = ua or ub
            result = _js_round(float(a) * float(b))
            return f"{_format_number(result)}{unit}"

    div = _DIV_RE.match(expr)
    if div:
        unit = div.group(2)
        # upstream: cssProcessor.ts:65 解构写作 `const [, a, unit,, b] = div`，
        # 多一个 elision 使 b 恒为 undefined（Node 实测 parseFloat(undefined)=NaN）。
        # 此处逐字等价复现该上游行为，差异登记 contract-differences；
        # group(1)/group(3)（被除数/除数）刻意不参与计算。
        return f"NaN{unit or ''}"

    add_sub = _ADD_SUB_RE.match(expr)
    if add_sub:
        a, ua, op, b, ub = (
            add_sub.group(1),
            add_sub.group(2),
            add_sub.group(3),
            add_sub.group(4),
            add_sub.group(5),
        )
        if ua == ub:
            value = float(a) + float(b) if op == "+" else float(a) - float(b)
            result = _js_round(value)
            return f"{_format_number(result)}{ua or ''}"

    return f"calc({expr})"


def _format_number(n: float) -> str:
    """JS 数字字符串化：整数不带 .0。"""
    if n == int(n):
        return str(int(n))
    return str(n)


def process_css(css: str) -> str:
    """upstream: cssProcessor.ts:16-45。

    先迭代替换 var()（≤10 轮，支持 fallback 与嵌套自定义属性），
    再迭代求值 calc()（同单位加减、无单位乘除，四位小数）。
    """
    # 后声明覆盖先声明（同 JS Map.set）
    variables: dict[str, str] = {}
    for match in _VAR_DECL_RE.finditer(css):
        variables[f"--{match.group(1)}"] = match.group(2).strip()

    def _replace_var(match: re.Match[str]) -> str:
        var_name = match.group(1)
        fallback = match.group(2)
        if var_name in variables:
            return variables[var_name]
        if fallback is not None:
            return fallback.strip()
        return f"var({var_name})"

    result = css
    prev = ""
    iterations = 0
    while result != prev and iterations < 10:
        prev = result
        result = _VAR_USE_RE.sub(_replace_var, result)
        iterations += 1

    iterations = 0
    prev = ""
    while result != prev and iterations < 10:
        prev = result
        result = _CALC_RE.sub(
            lambda m: _evaluate_calc_inner(m.group(1).strip()), result
        )
        iterations += 1

    return result


def escape_style_content(css: str) -> str:
    """upstream: render-article.ts:42-44（防止 </style> 闭合逃逸）。"""
    return re.sub(r"</style", r"<\\/style", css, flags=re.IGNORECASE)
