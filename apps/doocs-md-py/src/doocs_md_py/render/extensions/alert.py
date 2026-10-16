"""Alert 扩展：GFM blockquote 提醒与 Obsidian ::: 容器。

upstream: packages/core/src/extensions/alert.ts（markedAlert）。

两种语法：
1. ``> [!NAME] 自定义标题``（GFM）：上游在 marked walkTokens 中把
   blockquote token 改造成 alert；markdown-it 里用 block 与 inline 两条
   core 规则之间的 core ruler 完成等价改造（此时块树已成型、inline 未解析，
   可直接截断首段 inline.content，等价于上游按 br/text-\\n 裁剪 inline tokens）。
2. ``:::name 标题\\n正文\\n:::``（Obsidian 容器）：block ruler before paragraph，
   正文 trim 后重新 block.parse。

主渲染器固定 markedAlert({})：className=markdown-alert、withoutStyle=False、
无用户自定义变体；变体表与 octicon 图标见 alert_data.py。
"""

import re
from dataclasses import dataclass

from markdown_it.token import Token

from ..html_utils import escape_html
from .alert_data import VARIANTS

CLASS_NAME = "markdown-alert"

# upstream: alert.ts:68
_HEADER_RE = re.compile(r"^\[!([^\]\n]+)\][ \t]*([^\n]*)")
# upstream: alert.ts:129（去 ^，Python match 已锚定 pos）
_CONTAINER_RE = re.compile(r":::[ \t]*(\S+)[ \t]*([^\n]*)\n([\s\S]*?)\n:::")

# token.attrs 键
_A_VARIANT = "mdpy-alert-variant"
_A_TITLE = "mdpy-alert-title"
_A_ICON = "mdpy-alert-icon"
_A_FROM_CONTAINER = "mdpy-alert-container"


def _ucfirst(text: str) -> str:
    """upstream: utils/basicHelpers.ts ucfirst。"""
    return text[:1].upper() + text[1:].lower()


@dataclass(slots=True)
class AlertMeta:
    variant: str
    icon: str
    title: str  # 已 HTML 转义
    from_container: bool = False


def _resolve_variant(name: str) -> tuple[str, str | None, str] | None:
    """upstream: resolveVariant + defaultAlertVariant（大小写不敏感）。"""
    lower = name.lower()
    for vtype, vtitle, icon in VARIANTS:
        if vtype.lower() == lower:
            return vtype, vtitle, icon
    return None


def _build_meta(name: str, custom_title: str | None, from_container: bool) -> AlertMeta:
    """upstream: alert.ts:25-41 buildMeta。"""
    matched = _resolve_variant(name)
    if matched is not None:
        vtype, vtitle, icon = matched
        default_title = vtitle if vtitle is not None else _ucfirst(vtype)
    else:
        vtype, icon = "custom", ""
        default_title = name
    title = custom_title.strip() if custom_title and custom_title.strip() else default_title
    return AlertMeta(
        variant=vtype,
        icon=icon,
        title=escape_html(title),
        from_container=from_container,
    )


def _meta_attrs(token_open: Token, meta: AlertMeta) -> None:
    token_open.attrs[_A_VARIANT] = meta.variant
    token_open.attrs[_A_TITLE] = meta.title
    token_open.attrs[_A_ICON] = meta.icon
    token_open.attrs[_A_FROM_CONTAINER] = "1" if meta.from_container else ""


# ---- 语法一：GFM blockquote（core ruler，block 之后、inline 之前）----

def _transform_blockquotes(state) -> None:
    tokens = state.tokens
    out: list[Token] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.type != "blockquote_open":
            out.append(token)
            i += 1
            continue

        depth = 1
        j = i + 1
        while j < len(tokens) and depth:
            if tokens[j].type == "blockquote_open":
                depth += 1
            elif tokens[j].type == "blockquote_close":
                depth -= 1
            j += 1
        close_idx = j - 1

        meta = _match_blockquote_alert(state, tokens, i, close_idx)
        if meta is None:
            out.extend(tokens[i:j])
            i = j
            continue

        body = list(tokens[i + 1 : close_idx])
        _strip_first_paragraph(body)
        out.append(_open_token(token, meta))
        out.append(_title_token(token.level, meta))
        out.extend(body)
        out.append(Token("alert_close", "blockquote", -1))
        i = j

    state.tokens = out


def _match_blockquote_alert(state, tokens, open_idx: int, close_idx: int):
    """首个直接子块必须是起始于 blockquote 首物理行的段落。"""
    open_tok = tokens[open_idx]
    first_idx = open_idx + 1
    if first_idx >= close_idx:
        return None
    first = tokens[first_idx]
    if (
        first.type != "paragraph_open"
        or first.level != open_tok.level + 1
        or not first.map
        or not open_tok.map
        or first.map[0] != open_tok.map[0]
    ):
        return None
    inline_tok = tokens[first_idx + 1]
    if inline_tok.type != "inline":
        return None
    content = inline_tok.content
    nl = content.find("\n")
    first_line = content if nl < 0 else content[:nl]
    match = _HEADER_RE.match(first_line)
    if match is None:
        return None
    return _build_meta(match.group(1).strip(), match.group(2), False)


def _strip_first_paragraph(body: list[Token]) -> None:
    """等价上游 alert.ts:85-112：裁掉首行；首段为空则整段移除。"""
    if not body or body[0].type != "paragraph_open":
        return
    inline_tok = body[1]
    content = inline_tok.content
    nl = content.find("\n")
    if nl < 0:
        del body[0:3]
        return
    remainder = content[nl + 1 :]
    if remainder == "":
        del body[0:3]
        return
    inline_tok.content = remainder
    if inline_tok.map:
        inline_tok.map = [inline_tok.map[0] + 1, inline_tok.map[1]]


def _open_token(open_tok: Token, meta: AlertMeta) -> Token:
    token = Token("alert_open", "blockquote", 1)
    token.level = open_tok.level
    token.map = open_tok.map
    token.attrs["class"] = f"{CLASS_NAME} {CLASS_NAME}-{meta.variant}"
    _meta_attrs(token, meta)
    return token


def _title_token(base_level: int, meta: AlertMeta) -> Token:
    token = Token("alert_title", "p", 0)
    token.level = base_level + 1
    token.attrs["class"] = f"{CLASS_NAME}-title alert-title-{meta.variant}"
    token.attrs[_A_VARIANT] = meta.variant
    token.attrs[_A_TITLE] = meta.title
    token.attrs[_A_ICON] = meta.icon
    return token


# ---- 语法二：::: 容器（block ruler）----

def alert_container(state, startLine: int, endLine: int, silent: bool) -> bool:
    if state.is_code_block(startLine):
        return False
    pos = state.bMarks[startLine]
    match = _CONTAINER_RE.match(state.src, pos)
    if match is None:
        return False
    if silent:
        return True

    meta = _build_meta(match.group(1), match.group(2), True)
    content = match.group(3).strip()

    state.line = startLine + 1

    open_tok = state.push("alert_open", "blockquote", 1)
    open_tok.map = [startLine, 0]
    open_tok.attrs["class"] = f"{CLASS_NAME} {CLASS_NAME}-{meta.variant}"
    _meta_attrs(open_tok, meta)

    title_tok = state.push("alert_title", "p", 0)
    title_tok.attrs["class"] = f"{CLASS_NAME}-title alert-title-{meta.variant}"
    title_tok.attrs[_A_VARIANT] = meta.variant
    title_tok.attrs[_A_TITLE] = meta.title
    title_tok.attrs[_A_ICON] = meta.icon

    if content:
        child_tokens: list[Token] = []
        state.md.block.parse(content, state.md, state.env, child_tokens)
        for child in child_tokens:
            child.level += state.level
            state.tokens.append(child)

    state.push("alert_close", "blockquote", -1)

    # match.end() 落在闭合行；行尾若有残余字符（":::junk"），按上游语义
    # 剩余源文继续块解析；干净闭合则直接推进到下一物理行。
    end = match.end()
    nxt = startLine + 1
    while nxt < endLine and state.bMarks[nxt] < end:
        nxt += 1
    closing_eol = state.eMarks[nxt - 1] if nxt - 1 < endLine else end
    tail = state.src[end:closing_eol]
    if tail.strip():
        tail_src = state.src[end : state.eMarks[endLine - 1]]
        tail_tokens: list[Token] = []
        state.md.block.parse(tail_src, state.md, state.env, tail_tokens)
        state.tokens.extend(tail_tokens)
        state.line = endLine
    else:
        state.line = nxt
    return True


# ---- 渲染 ----

def _injected_icon(icon: str, variant: str, without_style: bool) -> str:
    if without_style or not icon:
        return ""
    return icon.replace("<svg", f'<svg class="alert-icon-{variant}"', 1)


def render_alert_open(tokens, idx, options, env) -> str:
    token = tokens[idx]
    cls = token.attrs.get("class", CLASS_NAME)
    return f'<blockquote class="{cls}">\n'


def render_alert_title(tokens, idx, options, env) -> str:
    token = tokens[idx]
    variant = token.attrs.get(_A_VARIANT, "custom")
    title = token.attrs.get(_A_TITLE, "")
    icon = token.attrs.get(_A_ICON, "")
    without_style = bool(options.get(_OPTION_WITHOUT_STYLE)) if options else False
    cls = token.attrs.get("class", f"{CLASS_NAME}-title alert-title-{variant}")
    return f'<p class="{cls}">{_injected_icon(icon, variant, without_style)}{title}</p>\n'


def render_alert_close(tokens, idx, options, env) -> str:
    return "</blockquote>\n"


_OPTION_WITHOUT_STYLE = "mdpy_alert_without_style"


def register_alert(md, without_style: bool = False) -> None:
    """装配 alert：容器块规则 + blockquote 改造 core ruler。"""
    md.options[_OPTION_WITHOUT_STYLE] = without_style
    md.block.ruler.before("paragraph", "alert_container", alert_container)
    md.core.ruler.after("block", "mdpy_alert_blockquote", _transform_blockquotes)
    rules = md.renderer.rules
    rules["alert_open"] = render_alert_open
    rules["alert_title"] = render_alert_title
    rules["alert_close"] = render_alert_close
