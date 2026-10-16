"""行内标记扩展：==高亮==、++下划线++、~波浪线~、^上标^。

upstream: packages/core/src/extensions/markup.ts（markedMarkup）。
marked 行内 tokenizer → markdown-it 行内规则；内容按上游 asTextTokenRenderer
语义原样插入（不做二次行内解析、不做 HTML 转义）。
"""

import re

# ASCII-only on purpose: `C++`/`x==1`/`v1~2` must stay literal, while CJK
# intraword usage like `把++重点++标出` should keep rendering.
_WORD_CHAR_RE = re.compile(r"[A-Za-z0-9]")

# upstream: markup.ts:71/96/121/148。
# 注意：Python Pattern.match(src, pos) 已锚定 pos，模式内不得再写 JS 语义的
# 行首 `^`——re 的 `^` 只认字符串真实起点，pos>0 时会导致候选全部失配。
_HIGHLIGHT_RE = re.compile(r"==(?=\S)((?:[^=]|=(?!=))*[^\s=])==")
_UNDERLINE_RE = re.compile(r"\+\+(?=\S)((?:[^+]|\+(?!\+))*[^\s+])\+\+")
_WAVY_RE = re.compile(r"~(?=\S)([^~\n]*[^\s~])~(?!~)")
_SUP_RE = re.compile(r"\^([^\s^]+)\^")

# markdown-it 的 emphasis/strikethrough 定界符在后处理（ruler2）之前被推成
# 独立的纯标记 text token，回退末字符时需跳过这些游程。
_EMPHASIS_MARKERS = "*_~"


def _deep_token_char(token) -> str:
    nested = getattr(token, "children", None)
    if nested:
        return _prev_effective_char(nested)
    return (getattr(token, "content", "") or "")[-1:]


def _prev_effective_char(tokens) -> str:
    """还原 marked prevInlineChar 在已解析 token 上看到的末字符。

    markdown-it 的 emphasis/strikethrough 在后处理（ruler2）前把定界符游程
    推送为独立的纯标记 text token，这里跳过这类尾部游程以还原上游在
    strong/em/del token 上看到的可见末字符。
    """
    i = len(tokens) - 1
    while i >= 0:
        ch = _deep_token_char(tokens[i])
        if not ch:
            return ""
        if ch in _EMPHASIS_MARKERS:
            content = getattr(tokens[i], "content", "") or ""
            if content and content.strip(_EMPHASIS_MARKERS) == "":
                i -= 1
                continue
        return ch
    return ""


def _follows_word_char(state) -> bool:
    """upstream: markup.ts:25 followsWordChar。

    普通文本先积压在 state.pending（push 时才刷成 text token），故优先取
    pending 末字符，否则沿已落盘 token 回退。
    """
    pending = getattr(state, "pending", "")
    ch = pending[-1] if pending else _prev_effective_char(state.tokens)
    return bool(ch) and bool(_WORD_CHAR_RE.fullmatch(ch))


def _make_rule(
    token_type: str, regexp: re.Pattern, opener: str, check_left_boundary: bool
):
    def rule(state, silent: bool) -> bool:
        if not state.src.startswith(opener, state.pos):
            return False
        if check_left_boundary and _follows_word_char(state):
            return False
        match = regexp.match(state.src, state.pos)
        if not match:
            return False
        if not silent:
            token = state.push(token_type, "", 0)
            token.content = match.group(1)
            token.markup = opener
        state.pos = match.end()
        return True

    return rule


markup_highlight = _make_rule("markup_highlight", _HIGHLIGHT_RE, "==", True)
markup_underline = _make_rule("markup_underline", _UNDERLINE_RE, "++", True)
markup_wavyline = _make_rule("markup_wavyline", _WAVY_RE, "~", True)
markup_superscript = _make_rule("markup_superscript", _SUP_RE, "^", False)


def render_markup_highlight(tokens, idx, options, env):
    return f'<span class="markup-highlight">{tokens[idx].content}</span>'


def render_markup_underline(tokens, idx, options, env):
    return f'<span class="markup-underline">{tokens[idx].content}</span>'


def render_markup_wavyline(tokens, idx, options, env):
    return f'<span class="markup-wavyline">{tokens[idx].content}</span>'


def render_markup_superscript(tokens, idx, options, env):
    return f'<sup class="markup-superscript">{tokens[idx].content}</sup>'


def register_markup(md) -> None:
    """装配四条行内规则；wavyline 必须先于 strikethrough 裁决 `~`/`~~`。"""
    md.inline.ruler.before("strikethrough", "markup_highlight", markup_highlight)
    md.inline.ruler.before("strikethrough", "markup_underline", markup_underline)
    md.inline.ruler.before("strikethrough", "markup_wavyline", markup_wavyline)
    md.inline.ruler.before("strikethrough", "markup_superscript", markup_superscript)
    rules = md.renderer.rules
    rules["markup_highlight"] = render_markup_highlight
    rules["markup_underline"] = render_markup_underline
    rules["markup_wavyline"] = render_markup_wavyline
    rules["markup_superscript"] = render_markup_superscript
