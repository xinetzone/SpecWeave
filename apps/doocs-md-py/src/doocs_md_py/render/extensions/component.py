"""JSX 风格自定义组件扩展（upstream: extensions/component.ts）。

- 块级自闭合：``<Component prop="value" />``
- 成对（同行/多行）：``<Component prop="value">children</Component>``
- 名字必须 PascalCase（``<`` 后紧跟 A-Z，ASCII ``\\w`` 续名）
- 行内系统组件（Emoji）与注册表中 ``inline=True`` 的组件不走块解析
- 未知名渲染红色提示段；模板引擎支持 ``{{#each}}``/``{{#if}}``/``{{#else}}``/
  ``{{#unless}}``/``{{prop}}``（转义）/``{{children}}``（原样）

marked 的 start() 廉价候选扫描在 markdown-it 中由块规则逐行守卫天然替代
（围栏由内建 fence 规则先行消费，规则内 is_code_block 守卫兜底）。
"""

import json
import math
import re
from dataclasses import dataclass, field

from ..html_utils import escape_html, unescape_html

DEFAULT_UNKNOWN_COMPONENT = "Unknown component: {name}"

_INLINE_SYSTEM_NAMES = frozenset({"Emoji"})
_OPTS_KEY = "mdpy_component_opts"
_A_NAME = "mdpy-component-name"
_A_PROPS = "mdpy-component-props"
_A_CHILDREN = "mdpy-component-children"

_WORD_CH = re.compile(r"[A-Za-z0-9_]")
_PROP_RE = re.compile(r"([A-Za-z0-9_][A-Za-z0-9_-]*)=(?:\"([^\"]*)\"|'([^']*)')")
_FENCE_LINE_RE = re.compile(r"^ {0,3}([`~]{3,})")
_LEADING_WS_RE = re.compile(r"^\s*")

_EACH_RE = re.compile(r"\{\{#each\s+([\w-]+)\}\}([\s\S]*?)\{\{/each\}\}")
_IF_RE = re.compile(r"\{\{#if\s+([\w-]+)\}\}([\s\S]*?)\{\{/if\}\}")
_UNLESS_RE = re.compile(r"\{\{#unless\s+([\w-]+)\}\}([\s\S]*?)\{\{/unless\}\}")
_VAR_RE = re.compile(r"\{\{([\w-]+)\}\}")
_ITEM_KEY_RE = re.compile(r"\{\{item\.([\w-]+)\}\}")


@dataclass(slots=True)
class PropDef:
    """upstream: CustomComponentProp。"""

    name: str
    required: bool = False
    default: str | None = None
    type: str | None = None


@dataclass(slots=True)
class ComponentDef:
    """upstream: CustomComponentDef（example/description 等仅编辑器元数据不参与渲染）。"""

    name: str
    template: str = ""
    inline: bool = False
    props: tuple[PropDef, ...] = field(default_factory=tuple)


# ---- upstream: component.ts:153-160 ----
def parse_props(props_str: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for m in _PROP_RE.finditer(props_str):
        value = m.group(2) if m.group(2) is not None else (m.group(3) or "")
        result[m.group(1)] = unescape_html(value)
    return result


# ---- upstream: component.ts:165-189 ----
def _palette_vars() -> dict[str, str]:
    return {
        "_bgPrimary_": "var(--md-comp-bg, #fff)",
        "_bgSecondary_": "var(--md-comp-bg-secondary, #f5f5f5)",
        "_bgStripe_": "var(--md-comp-bg-stripe, #fafafa)",
        "_textPrimary_": "var(--md-comp-text-primary, #333)",
        "_textSecondary_": "var(--md-comp-text-secondary, #666)",
        "_textTertiary_": "var(--md-comp-text-tertiary, #999)",
        "_borderDefault_": "var(--md-comp-border-default, #e0e0e0)",
        "_borderLight_": "var(--md-comp-border-light, #eee)",
    }


_CV = {
    "bg": "var(--md-comp-bg, #fff)",
    "bgSec": "var(--md-comp-bg-secondary, #f5f5f5)",
    "bgStripe": "var(--md-comp-bg-stripe, #fafafa)",
    "txtP": "var(--md-comp-text-primary, #333)",
    "txtS": "var(--md-comp-text-secondary, #666)",
    "txtT": "var(--md-comp-text-tertiary, #999)",
    "border": "var(--md-comp-border-default, #e0e0e0)",
    "borderL": "var(--md-comp-border-light, #eee)",
}


def _js_string(value) -> str:
    """等价 JS String(value)（JSON 解析结果域）：null→'null'，布尔小写，整值浮点去 .0。"""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


# ---- upstream: component.ts:193-234 ----
def render_table_block(props: dict[str, str]) -> str:
    try:
        headers = json.loads(props.get("headers") or "[]")
    except (json.JSONDecodeError, TypeError):
        headers = []
    try:
        raw_rows = json.loads(props.get("rows") or "[]")
        rows = raw_rows if isinstance(raw_rows, list) else []
    except (json.JSONDecodeError, TypeError):
        rows = []

    striped = props.get("striped") != "false"
    caption = props.get("caption") or ""

    th_style = (
        f"padding: 8px 12px; text-align: left; font-weight: 600; font-size: 13px; "
        f"color: {_CV['txtS']}; background: {_CV['bgSec']}; "
        f"border-bottom: 2px solid {_CV['border']};"
    )
    td_style = (
        f"padding: 8px 12px; font-size: 13px; color: {_CV['txtP']}; "
        f"border-bottom: 1px solid {_CV['borderL']};"
    )

    html = '<section style="overflow-x: auto; margin: 16px 0;">\n'
    html += '  <table style="width: 100%; border-collapse: collapse; font-size: 13px;">\n'
    if caption:
        html += (
            f'    <caption style="font-size: 13px; color: {_CV["txtS"]}; '
            'margin-bottom: 8px; text-align: left; caption-side: top;">'
            f"{escape_html(caption)}</caption>\n"
        )
    if len(headers) > 0:
        html += "    <thead>\n      <tr>\n"
        for h in headers:
            html += f'        <th style="{th_style}">{escape_html(_js_string(h))}</th>\n'
        html += "      </tr>\n    </thead>\n"
    html += "    <tbody>\n"
    for i, raw_row in enumerate(rows):
        row = raw_row if isinstance(raw_row, list) else []
        row_style = f' style="background: {_CV["bgStripe"]};"' if striped and i % 2 == 1 else ""
        html += f"      <tr{row_style}>\n"
        for cell in row:
            html += f'        <td style="{td_style}">{escape_html(_js_string(cell))}</td>\n'
        html += "      </tr>\n"
    html += "    </tbody>\n  </table>\n</section>"
    return html


# ---- upstream: component.ts:236-262 ----
def render_info_grid(props: dict[str, str]) -> str:
    try:
        items = json.loads(props.get("items") or "[]")
    except (json.JSONDecodeError, TypeError):
        items = []
    if not isinstance(items, list):
        items = []
    try:
        cols_num = float(props.get("cols", ""))
        if math.isnan(cols_num):
            raise ValueError
        cols_f = cols_num
    except (ValueError, TypeError):
        cols_f = 2.0
    cols = int(min(max(cols_f, 1), 3))
    col_width = f"{math.floor(100 / cols)}%"

    html = (
        f'<section style="margin: 16px 0; border: 1px solid {_CV["borderL"]}; '
        f'border-radius: 8px; overflow: hidden; background: {_CV["bg"]};">\n'
    )
    html += '  <section style="display: table; width: 100%; border-collapse: collapse;">\n'
    r = 0
    while r < len(items):
        html += '    <section style="display: table-row;">\n'
        for c in range(cols):
            item = items[r + c] if r + c < len(items) else None
            border_bottom = (
                f"1px solid {_CV['borderL']}" if r + cols < len(items) else "none"
            )
            border_right = f"1px solid {_CV['borderL']}" if c < cols - 1 else "none"
            html += (
                '      <section style="display: table-cell; '
                f"width: {col_width}; padding: 10px 14px; border-bottom: {border_bottom}; "
                f"border-right: {border_right}; vertical-align: top; box-sizing: border-box;\">\n"
            )
            if item is not None:
                label = item.get("label") or "" if isinstance(item, dict) else ""
                value = item.get("value") or "" if isinstance(item, dict) else ""
                html += (
                    f'        <p style="margin: 0 0 2px; font-size: 11px; color: {_CV["txtT"]}; '
                    'text-transform: uppercase; letter-spacing: 0.5px;">'
                    f"{escape_html(str(label))}</p>\n"
                )
                html += (
                    f'        <p style="margin: 0; font-size: 14px; font-weight: 500; '
                    f'color: {_CV["txtP"]};">{escape_html(str(value))}</p>\n'
                )
            html += "      </section>\n"
        html += "    </section>\n"
        r += cols
    html += "  </section>\n</section>"
    return html


_SPECIAL_RENDERERS = {
    "TableBlock": render_table_block,
    "InfoGrid": render_info_grid,
}

# ---- upstream: component.ts:271-282 ----
_TIP_COLORS = {
    "info": {"borderColor": "#1890ff", "bgColor": "#e6f7ff", "textColor": "#0050b3"},
    "success": {"borderColor": "#52c41a", "bgColor": "#f6ffed", "textColor": "#135200"},
    "warning": {"borderColor": "#faad14", "bgColor": "#fffbe6", "textColor": "#874d00"},
    "danger": {"borderColor": "#ff4d4f", "bgColor": "#fff2f0", "textColor": "#a8071a"},
}


# ---- upstream: component.ts:289-333 ----
def process_template(template: str, props: dict[str, str]) -> str:
    def _each_sub(m: re.Match) -> str:
        prop_key, body = m.group(1), m.group(2)
        try:
            parsed = json.loads(props.get(prop_key) or "[]")
        except (json.JSONDecodeError, TypeError):
            parsed = []
        if not isinstance(parsed, list):
            return ""
        parts = []
        for index, item in enumerate(parsed):
            item_body = body.replace("{{@index}}", str(index))
            if isinstance(item, dict):
                def _key_sub(km: re.Match) -> str:
                    key = km.group(1)
                    return escape_html(str(item[key])) if key in item else ""

                item_body = _ITEM_KEY_RE.sub(_key_sub, item_body)
            else:
                item_body = item_body.replace("{{item}}", escape_html(_js_string(item)))
            parts.append(process_template(item_body, props))
        return "".join(parts)

    html = _EACH_RE.sub(_each_sub, template)

    def _if_sub(m: re.Match) -> str:
        key, content = m.group(1), m.group(2)
        else_idx = content.find("{{#else}}")
        if else_idx >= 0:
            return content[:else_idx] if props.get(key) else content[else_idx + 9 :]
        return content if props.get(key) else ""

    html = _IF_RE.sub(_if_sub, html)

    def _unless_sub(m: re.Match) -> str:
        return m.group(2) if not props.get(m.group(1)) else ""

    html = _UNLESS_RE.sub(_unless_sub, html)

    def _var_sub(m: re.Match) -> str:
        key = m.group(1)
        if key == "children":
            return props.get(key, "")
        return escape_html(props[key]) if key in props else ""

    html = _VAR_RE.sub(_var_sub, html)
    return html


# ---- upstream: component.ts:336-355 ----
def render_template(defn: ComponentDef, raw_props: dict[str, str]) -> str:
    props: dict[str, str] = {}
    for prop_def in defn.props:
        if prop_def.default is not None:
            props[prop_def.name] = prop_def.default
    props.update(raw_props)

    special = _SPECIAL_RENDERERS.get(defn.name)
    if special is not None:
        return special(props)

    if defn.name == "TipBlock":
        colors = _TIP_COLORS.get(props.get("type") or "info", _TIP_COLORS["info"])
        merged = {**colors, **props}
    else:
        merged = props
    props_with_palette = {**_palette_vars(), **merged}
    return process_template(defn.template, props_with_palette)


def preview_component(defn: ComponentDef, props_override: dict[str, str] | None = None) -> str:
    """upstream: previewComponent（编辑器预览 API）。"""
    return render_template(defn, props_override or {})


def get_built_in_registry() -> dict[str, ComponentDef]:
    """upstream: getBuiltInRegistry。数据模块在文件尾部导入以打破循环引用。"""
    from .component_data import BUILT_IN_COMPONENTS

    return {c.name: c for c in BUILT_IN_COMPONENTS}


# ---- 标签扫描器（upstream: component.ts:401-588）----
def _read_component_name(src: str, i: int) -> str:
    j = i
    while j < len(src) and _WORD_CH.fullmatch(src[j]):
        j += 1
    return src[i:j]


def _is_inline_component(name: str, registry: dict[str, ComponentDef]) -> bool:
    if name in _INLINE_SYSTEM_NAMES:
        return True
    defn = registry.get(name)
    return defn is not None and defn.inline


def _find_line_end(src: str, i: int) -> int:
    nl = src.find("\n", i)
    return nl if nl >= 0 else len(src)


def _only_ws_to_line_end(src: str, i: int) -> bool:
    return src[i : _find_line_end(src, i)].strip() == ""


def _find_closing_tag(src: str, name: str, start_from: int) -> int:
    close_tag = f"</{name}>"
    line_start = start_from
    fence_char = ""
    fence_length = 0
    while line_start <= len(src):
        line_end = _find_line_end(src, line_start)
        line = src[line_start:line_end]
        fm = _FENCE_LINE_RE.match(line)
        if fence_char:
            if fm and fm.group(1)[0] == fence_char and len(fm.group(1)) >= fence_length:
                fence_char = ""
                fence_length = 0
        elif fm:
            fence_char = fm.group(1)[0]
            fence_length = len(fm.group(1))
        else:
            ws = _LEADING_WS_RE.match(line)
            lws = ws.end() - ws.start()
            stripped = line[lws:]
            if stripped.startswith(close_tag) and stripped[len(close_tag) :].strip() == "":
                return line_start + lws
        if line_end == len(src):
            break
        line_start = line_end + 1
    return -1


@dataclass(slots=True)
class _ParsedTag:
    raw: str
    name: str
    props_str: str
    children: str


def parse_tag(src: str) -> _ParsedTag | None:
    """upstream: parseTag（非正则标签解析，引号内 '>' 不误闭合）。src 必须以 '<' 起始。"""
    if len(src) < 2 or src[0] != "<" or not ("A" <= src[1] <= "Z"):
        return None
    name = _read_component_name(src, 1)
    if not name:
        return None
    i = 1 + len(name)
    in_quote = ""
    j = i
    while j < len(src):
        ch = src[j]
        if in_quote:
            if ch == in_quote:
                in_quote = ""
        elif ch in ('"', "'"):
            in_quote = ch
        elif ch == "/" and j + 1 < len(src) and src[j + 1] == ">":
            if not _only_ws_to_line_end(src, j + 2):
                return None
            return _ParsedTag(src[: j + 2], name, src[i:j].strip(), "")
        elif ch == ">":
            line_end = _find_line_end(src, j + 1)
            close_tag = f"</{name}>"
            inline_close = src.find(close_tag, j + 1)
            if 0 <= inline_close < line_end:
                if src[inline_close + len(close_tag) : line_end].strip() != "":
                    return None
                children = src[j + 1 : inline_close]
                return _ParsedTag(src[: inline_close + len(close_tag)], name, src[i:j].strip(), children)
            if not _only_ws_to_line_end(src, j + 1):
                return None
            scan_from = line_end if line_end == len(src) else line_end + 1
            close_idx = _find_closing_tag(src, name, scan_from)
            if close_idx < 0:
                return None
            children = src[j + 1 : close_idx]
            return _ParsedTag(src[: close_idx + len(close_tag)], name, src[i:j].strip(), children)
        j += 1
    return None


# ---- markdown-it 装配 ----
def component_block(state, start_line: int, end_line: int, silent: bool) -> bool:
    """upstream: mdComponent block tokenizer（start 候选守卫由逐行调用天然承载）。"""
    if state.is_code_block(start_line):
        return False
    bm = state.bMarks[start_line]
    src = state.src
    if bm >= len(src) or bm + 1 >= len(src) or src[bm] != "<":
        return False
    if not ("A" <= src[bm + 1] <= "Z"):
        return False
    name = _read_component_name(src, bm + 1)
    get_options = state.md.options.get(_OPTS_KEY)
    opts = get_options() if get_options is not None else None
    registry = opts.components if opts is not None and opts.components is not None else get_built_in_registry()
    if _is_inline_component(name, registry):
        return False
    tag = parse_tag(src[bm:])
    if tag is None:
        return False
    if silent:
        return True
    consumed = tag.raw.count("\n") + 1
    state.line = start_line + consumed
    token = state.push("md_component", "", 0)
    token.map = [start_line, start_line + consumed]
    token.attrs[_A_NAME] = tag.name
    token.attrs[_A_PROPS] = tag.props_str
    token.attrs[_A_CHILDREN] = tag.children
    return True


def render_component(tokens, idx, options, env):
    token = tokens[idx]
    name = token.attrs[_A_NAME]
    props_str = token.attrs[_A_PROPS]
    children = token.attrs[_A_CHILDREN]
    get_options = options.get(_OPTS_KEY)
    opts = get_options() if get_options is not None else None
    registry = (
        opts.components if opts is not None and opts.components is not None else get_built_in_registry()
    )
    defn = registry.get(name)
    if defn is None:
        tpl = ""
        if opts.render_messages is not None:
            tpl = opts.render_messages.unknown_component or ""
        if not tpl:
            tpl = DEFAULT_UNKNOWN_COMPONENT
        text = name.join(tpl.split("{name}"))
        return f'<p style="color:#f00;font-size:12px;">[{text}]</p>\n'
    props = parse_props(props_str)
    if children and props.get("children") is None:
        props["children"] = children
    return render_template(defn, props) + "\n"


def register_component(md, get_options=None) -> None:
    """upstream: markedComponent(() => opts.components ?? getBuiltInRegistry(),
    () => opts.renderMessages)，装配位 renderer-impl.ts:468（扩展链最早）。
    """
    md.options[_OPTS_KEY] = get_options
    # 必须先于 emoji_block/html_block 注册（before 同锚点按注册顺序排前）。
    # alt=['paragraph','reference'] 对齐 html_block：marked 的 start() 可在任意行
    # 重新起块，markdown-it 中则需显式获得段落/引用定义中断权。
    md.block.ruler.before(
        "html_block",
        "md_component",
        component_block,
        {"alt": ["paragraph", "reference"]},
    )
    md.renderer.rules["md_component"] = render_component
