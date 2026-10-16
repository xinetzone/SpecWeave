"""表情扩展：GitHub shortcode、系统贴纸 <Emoji>、legacy 兼容语法。

upstream: packages/core/src/extensions/emoji.ts（markedEmoji）。

- 行内 emoji：`:smile:` → 😄；`<Emoji id=... />`；`{{emoji:<id>}}`
- 行内 asset_emoji：`![name](asset://<id>){N%}`（必须先于内建 image 裁决）
- 块 emoji_block：独占一行的 `<Emoji …/>`，包 <p>（可带 align）
- 贴纸 URL 经 opts.assetResolver 解析，缺省 about:blank，并做 SAFE_SRC 收敛

编辑器侧的 formatEmojiSnippet/padEmojiBlock 是面板插入助手，渲染链路不涉及，
不移植。JS ``\\w`` 为 ASCII 语义，统一显式写成 ASCII 字符类。
扩展元数据挂在 token.attrs 的 mdpy-* 键上（自定义 token 类型，attrs 不会被
默认规则渲染成 HTML 属性）。
"""

import re
from dataclasses import dataclass

from .emoji_data import EMOJI_SHORTCODES
from ..html_utils import escape_html

# upstream: emoji.ts:9/11/13（去 JS 行首 ^，Python match 已锚定 pos）
SHORTCODE_RE = re.compile(r":([a-z0-9_+-]+):")
LEGACY_EMOJI_RE = re.compile(r"\{\{emoji:([A-Za-z0-9_-]+)\}\}")
ASSET_EMOJI_RE = re.compile(r"!\[([^\]]*)\]\(\s*asset:/*([^\s/)]+)\s*\)\{(\d+)%?\}")

EMOJI_TAG_OPEN = "<Emoji"
SAFE_SRC_RE = re.compile(r"^(?:https?:|blob:|data:image/|about:blank)", re.IGNORECASE)
EMOJI_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_NAME_CHAR_RE = re.compile(r"[A-Za-z0-9_-]")
_WS_RE = re.compile(r"\s")

_ASSET_EMOJI_WINDOW = 256

# token.attrs 键
_A_ID = "mdpy-emoji-id"
_A_NAME = "mdpy-emoji-name"
_A_WIDTH = "mdpy-emoji-width"
_A_ALIGN = "mdpy-emoji-align"


@dataclass(slots=True)
class EmojiTag:
    """upstream: parseEmojiTag 返回值。"""

    raw: str
    id: str
    alt: str | None = None
    width_percent: int | None = None
    align: str | None = None


def parse_width_percent(raw: str | None) -> int | None:
    """upstream: emoji.ts:88（clamp 1-100）。"""
    if not raw:
        return None
    m = re.match(r"^(\d+)%?$", raw.strip())
    if not m:
        return None
    value = int(m.group(1))
    return max(1, min(100, value))


def parse_align(raw: str | None) -> str | None:
    """upstream: emoji.ts:100。"""
    if raw is None:
        return None
    value = raw.strip().lower()
    if value in ("left", "center", "right"):
        return value
    return None


def _is_name_boundary(ch: str | None) -> bool:
    return not ch or not _NAME_CHAR_RE.fullmatch(ch)


def _skip_ws(src: str, i: int) -> int:
    while i < len(src) and _WS_RE.fullmatch(src[i]):
        i += 1
    return i


def _read_quoted(src: str, i: int) -> tuple[str, int] | None:
    quote = src[i] if i < len(src) else ""
    if quote not in ('"', "'"):
        return None
    j = i + 1
    while j < len(src) and src[j] != quote:
        j += 1
    if j >= len(src):
        return None
    return src[i + 1 : j], j + 1


def parse_emoji_tag(src: str) -> EmojiTag | None:
    """upstream: emoji.ts:134（属性序自由，id 必填，自闭合或空标签）。"""
    if not src.startswith(EMOJI_TAG_OPEN) or not _is_name_boundary(
        src[len(EMOJI_TAG_OPEN)] if len(src) > len(EMOJI_TAG_OPEN) else None
    ):
        return None

    attrs: dict[str, str] = {}
    i = _skip_ws(src, len(EMOJI_TAG_OPEN))
    closed = False

    while i < len(src):
        i = _skip_ws(src, i)
        if src.startswith("/>", i):
            i += 2
            closed = True
            break
        if src[i] == ">":
            i = _skip_ws(src, i + 1)
            close = "</Emoji>"
            if not src.startswith(close, i):
                return None
            i += len(close)
            closed = True
            break

        name_start = i
        while i < len(src) and _NAME_CHAR_RE.fullmatch(src[i]):
            i += 1
        if i == name_start:
            return None
        name = src[name_start:i]
        i = _skip_ws(src, i)
        if i >= len(src) or src[i] != "=":
            return None
        i = _skip_ws(src, i + 1)
        quoted = _read_quoted(src, i)
        if quoted is None:
            return None
        attrs[name] = quoted[0]
        i = quoted[1]

    if not closed:
        return None

    tag_id = attrs.get("id", "").strip()
    if not tag_id or not EMOJI_ID_RE.fullmatch(tag_id):
        return None

    return EmojiTag(
        raw=src[:i],
        id=tag_id,
        alt=attrs.get("alt", "").strip() or None,
        width_percent=parse_width_percent(attrs.get("width")),
        align=parse_align(attrs.get("align")),
    )


def _safe_src(url: str) -> str:
    """upstream: emoji.ts:49。"""
    trimmed = url.strip()
    if not SAFE_SRC_RE.match(trimmed):
        return "about:blank"
    return escape_html(trimmed)


def _sticker_alt(emoji_id: str, name: str | None) -> str:
    r"""upstream: renderSticker 内 name ?? `:${id}:`。"""
    return name if name else f":{emoji_id}:"


def render_sticker(resolve_url, emoji_id: str, alt: str, width_percent: int | None) -> str:
    """upstream: emoji.ts:245。"""
    safe_id = escape_html(emoji_id)
    safe_alt = escape_html(alt)
    url = _safe_src(resolve_url(emoji_id))
    width = (
        parse_width_percent(str(width_percent)) if width_percent is not None else None
    )
    if width is not None:
        return (
            f'<img class="md-asset-img" data-emoji-id="{safe_id}" '
            f'data-asset-id="{safe_id}" src="{url}" alt="{safe_alt}" '
            f'style="width:{width}%" />'
        )
    return (
        f'<img class="md-emoji" data-emoji-id="{safe_id}" '
        f'src="{url}" alt="{safe_alt}" />'
    )


def _set_sticker_attrs(token, tag_or_id, *, name=None, width=None, align=None) -> None:
    emoji_id = tag_or_id.id if isinstance(tag_or_id, EmojiTag) else tag_or_id
    if isinstance(tag_or_id, EmojiTag):
        name = tag_or_id.alt
        width = tag_or_id.width_percent
        align = tag_or_id.align
    token.attrs[_A_ID] = emoji_id
    token.attrs[_A_NAME] = name or ""
    if width is not None:
        token.attrs[_A_WIDTH] = width
    if align:
        token.attrs[_A_ALIGN] = align


# ---- 行内规则 ----

def asset_emoji_inline(state, silent: bool) -> bool:
    """upstream: emoji.ts:371-407（先于内建 image 裁决）。"""
    pos = state.pos
    if not state.src.startswith("![", pos):
        return False
    window_end = min(len(state.src), pos + _ASSET_EMOJI_WINDOW)
    if "](asset:" not in state.src[pos:window_end]:
        return False
    match = ASSET_EMOJI_RE.match(state.src, pos)
    if not match:
        return False
    emoji_id = match.group(2)
    if not EMOJI_ID_RE.fullmatch(emoji_id):
        return False
    width_percent = parse_width_percent(match.group(3))
    if width_percent is None:
        return False
    if not silent:
        token = state.push("asset_emoji", "", 0)
        token.content = match.group(0)
        _set_sticker_attrs(
            token, emoji_id, name=match.group(1), width=width_percent
        )
    state.pos = match.end()
    return True


def emoji_inline(state, silent: bool) -> bool:
    """upstream: emoji.ts:409-449（tag → legacy → shortcode）。"""
    pos = state.pos
    src = state.src
    tag = parse_emoji_tag(src[pos:])
    if tag is not None:
        if not silent:
            token = state.push("emoji", "", 0)
            token.content = tag.raw
            _set_sticker_attrs(token, tag)
        state.pos = pos + len(tag.raw)
        return True

    legacy = LEGACY_EMOJI_RE.match(src, pos)
    if legacy is not None:
        if not silent:
            token = state.push("emoji", "", 0)
            token.content = legacy.group(0)
            _set_sticker_attrs(token, legacy.group(1))
        state.pos = legacy.end()
        return True

    match = SHORTCODE_RE.match(src, pos)
    if match is not None:
        char = EMOJI_SHORTCODES.get(match.group(1))
        if char is not None:
            if not silent:
                token = state.push("emoji", "", 0)
                token.content = char
            state.pos = match.end()
            return True
    return False


def render_emoji(tokens, idx, options, env):
    token = tokens[idx]
    emoji_id = token.attrs.get(_A_ID)
    if emoji_id:
        return render_sticker(
            options_get_resolver(options),
            emoji_id,
            _sticker_alt(emoji_id, token.attrs.get(_A_NAME) or None),
            token.attrs.get(_A_WIDTH),
        )
    return token.content


def render_asset_emoji(tokens, idx, options, env):
    token = tokens[idx]
    return render_sticker(
        options_get_resolver(options),
        token.attrs[_A_ID],
        _sticker_alt(token.attrs[_A_ID], token.attrs.get(_A_NAME) or None),
        token.attrs[_A_WIDTH],
    )


# ---- 块规则 ----

def emoji_block(state, startLine: int, endLine: int, silent: bool) -> bool:
    """upstream: emoji.ts:339-369 + findLineStartEmojiTag/consumeFullLineTag。

    围栏（```/~~~）由 markdown-it fence 规则先行消费，无需手工跳过；
    上游要求标签位于行首（零缩进），这里以 bMarks 原始行起点判定。
    """
    if state.is_code_block(startLine):
        return False
    line_start = state.bMarks[startLine]
    if not state.src.startswith(EMOJI_TAG_OPEN, line_start) or not _is_name_boundary(
        state.src[line_start + len(EMOJI_TAG_OPEN)]
        if line_start + len(EMOJI_TAG_OPEN) < len(state.src)
        else None
    ):
        return False
    tag = parse_emoji_tag(state.src[line_start : state.eMarks[startLine]])
    if tag is None:
        return False
    # consumeFullLineTag：标签后该行只能剩空白
    if state.src[line_start + len(tag.raw) : state.eMarks[startLine]].strip():
        return False
    if silent:
        return True
    state.line = startLine + 1
    token = state.push("emoji_block", "", 0)
    token.map = [startLine, state.line]
    token.content = tag.raw
    _set_sticker_attrs(token, tag)
    return True


def render_emoji_block(tokens, idx, options, env):
    token = tokens[idx]
    sticker = render_sticker(
        options_get_resolver(options),
        token.attrs[_A_ID],
        _sticker_alt(token.attrs[_A_ID], token.attrs.get(_A_NAME) or None),
        token.attrs.get(_A_WIDTH),
    )
    align = token.attrs.get(_A_ALIGN)
    if align:
        return f'<p style="text-align:{align}">{sticker}</p>\n'
    return f"<p>{sticker}</p>\n"


# resolveUrl 通过 md.options 注入（register_emoji 时挂接，动态读取 opts）

_RESOLVER_KEY = "mdpy_emoji_resolve_url"


def options_get_resolver(options):
    return options.get(_RESOLVER_KEY, _default_resolve_url) if options else _default_resolve_url


def _default_resolve_url(emoji_id: str) -> str:
    return "about:blank"


def register_emoji(md, resolve_url=None) -> None:
    """装配 emoji 三规则。行内两条均须先于 image/html_inline。"""
    md.options[_RESOLVER_KEY] = (
        resolve_url if resolve_url is not None else _default_resolve_url
    )
    md.block.ruler.before("html_block", "emoji_block", emoji_block)
    md.inline.ruler.before("strikethrough", "asset_emoji", asset_emoji_inline)
    md.inline.ruler.before("strikethrough", "emoji", emoji_inline)
    rules = md.renderer.rules
    rules["emoji"] = render_emoji
    rules["asset_emoji"] = render_asset_emoji
    rules["emoji_block"] = render_emoji_block
