"""注音（ruby）扩展：``[汉字]{注音}`` 与 ``[汉字]^(注音)``。

upstream: packages/core/src/extensions/ruby.ts（markedRuby）。

- 注音部分隔符：``・`` ``．`` ``。`` ``-``；多段注音按字数分配：
  字数 >= 段数时每段一字、末段吞掉所有剩余字；字数 < 段数时逐字配对、
  多余注音段丢弃。
- data-text/data-ruby 原样插入（上游不转义），XSS 由 T8 净化层兜底。
- JS ``str.split('')`` 按 UTF-16 码元切分；注音/汉字均在 BMP，list(str) 等价。
"""

import re

# upstream: ruby.ts:24/36（去行首 ^）
RULE1_RE = re.compile(r"\[([^\]]+)\]\{([^}]+)\}")
RULE2_RE = re.compile(r"\[([^\]]+)\]\^\(([^)]+)\)")
# upstream: ruby.ts:53（- 在字符类末尾为字面量）
SEP_RE = re.compile(r"[・．。-]")

_A_TEXT = "mdpy-ruby-text"
_A_RUBY = "mdpy-ruby-annotation"
_A_FORMAT = "mdpy-ruby-format"


def _ruby_tag(text: str, annotation: str, fmt: str) -> str:
    """upstream: ruby.ts:77/92/103（逐字模板）。"""
    return (
        f'<ruby data-text="{text}" data-ruby="{annotation}" data-format="{fmt}">'
        f"{text}<rp>(</rp><rt>{annotation}</rt><rp>)</rp></ruby>"
    )


def render_ruby_html(text: str, annotation: str, fmt: str) -> str:
    """upstream: ruby.ts:50-104。"""
    parts = [part for part in SEP_RE.split(annotation) if part.strip() != ""]
    if not parts:
        # 无分隔符（或注音全为分隔符/空白）：单元素整体注音
        return _ruby_tag(text, annotation, fmt)

    chars = list(text)
    result: list[str] = []

    if len(chars) >= len(parts):
        current = 0
        for i, part in enumerate(parts):
            remaining_chars = len(chars) - current
            remaining_parts = len(parts) - i
            char_count = remaining_chars if remaining_parts == 1 else 1
            current_text = "".join(chars[current : current + char_count])
            result.append(_ruby_tag(current_text, part, fmt))
            current += char_count
        if current < len(chars):
            result.append("".join(chars[current:]))
    else:
        for i, char in enumerate(chars):
            part = parts[i] if i < len(parts) else ""
            if part:
                result.append(_ruby_tag(char, part, fmt))
            else:
                result.append(char)

    return "".join(result)


def ruby_inline(state, silent: bool) -> bool:
    if state.pos >= len(state.src) or state.src[state.pos] != "[":
        return False
    match = RULE1_RE.match(state.src, state.pos)
    fmt = "basic"
    if match is None:
        match = RULE2_RE.match(state.src, state.pos)
        fmt = "basic-hat"
        if match is None:
            return False
    if not silent:
        token = state.push("ruby", "", 0)
        token.attrs[_A_TEXT] = match.group(1).strip()
        token.attrs[_A_RUBY] = match.group(2).strip()
        token.attrs[_A_FORMAT] = fmt
        token.content = match.group(0)
    state.pos = match.end()
    return True


def render_ruby(tokens, idx, options, env):
    token = tokens[idx]
    return render_ruby_html(
        token.attrs[_A_TEXT], token.attrs[_A_RUBY], token.attrs[_A_FORMAT]
    )


def register_ruby(md) -> None:
    """装配行内 ruby；须先于内建 link（同以 ``[`` 起始）。"""
    md.inline.ruler.before("link", "ruby", ruby_inline)
    md.renderer.rules["ruby"] = render_ruby
