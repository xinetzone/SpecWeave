"""KaTeX 数学公式扩展（服务端仅产占位容器，不引 MathJax）。

upstream: packages/core/src/extensions/katex.ts + utils/mathDetection.ts。

四种语法（renderer-impl.ts:479 以 nonStandard=True 装配）：
- 行内 ``$...$`` / ``$$...$$``（后者 displayMode=True，产出块容器）
- 块级 ``$$\\n...\\n$$`` 多行与 ``$$...$$`` 独占行
- LaTeX 行内 ``\\(...\\)``；LaTeX 块 ``\\[...\\]``

服务端等价于上游 ``typeof window === 'undefined'`` 分支：只渲染
katex-pending 占位（块 <section> / 行内 <span>），data-math-raw 携带
escapeHtml(raw)。该占位在 T8 净化白名单中必须受保护。

已知偏差（登记 contract-differences）：marked 块词法器可用 start() 把
段中 ``\\[x\\]`` 抽成块 token；markdown-it 块规则只能按行工作，段中
``\\[...\\]`` 由行内规则兜底，容器嵌在段落内。
"""

import re

from ..html_utils import escape_html

# upstream: katex.ts:24
DEFAULT_KATEX_LOADING = "Loading formula…"

# upstream: mathDetection.ts:1-6/50-51（Python match(src,pos) 已锚定 pos，去 JS 行首 ^）
INLINE_RE = re.compile(
    r"(\${1,2})(?!\$)((?:\\.|[^\\\n])*?(?:\\.|[^\\\n$]))\1(?=[\s?!.,:？！。，：]|$)"
)
INLINE_NONSTD_RE = re.compile(r"(\${1,2})(?!\$)((?:\\.|[^\\\n])*?(?:\\.|[^\\\n$]))\1")
BLOCK_MULTILINE_RE = re.compile(r"[ \t]{0,3}(\${1,2})[ \t]*\n([\s\S]+?)\n[ \t]{0,3}\1[ \t]*(?:\n|$)")
BLOCK_SINGLE_RE = re.compile(r"[ \t]{0,3}(\$\$)([^\n]+)\1[ \t]*(?:\n|$)")
INLINE_LATEX_RE = re.compile(r"\\\(([^\\]*(?:\\.[^\\]*)*?)\\\)")
BLOCK_LATEX_RE = re.compile(r"\\\[([^\\]*(?:\\.[^\\]*)*?)\\\]")

_AMOUNT_PREV_RE = re.compile(r"[0-9,.]")

# token.attrs 键
_A_DISPLAY = "mdpy-katex-display"
_A_RAW = "mdpy-katex-raw"

_LOADING_KEY = "mdpy_katex_loading"


# ---- upstream: mathDetection.ts:63-97（nonStandard 分支）----
def _is_amount_dollar(src: str, index: int) -> bool:
    """upstream: isAmountDollarSign（offset 固定为 inline state 起点 0）。"""
    if index <= 0:
        return False
    prev = src[index - 1]
    if _AMOUNT_PREV_RE.fullmatch(prev):
        return True
    return prev == " " and index >= 2 and "0" <= src[index - 2] <= "9"


def render_pending(raw: str, display: bool, get_loading=None) -> str:
    """upstream: katex.ts:71-80（window 未定义 / MathJax 未就绪分支）。"""
    raw_attr = escape_html(raw)
    if display:
        loading = ""
        if get_loading is not None:
            loading = get_loading() or ""
        if not loading:
            loading = DEFAULT_KATEX_LOADING
        return (
            f'<section class="katex-block katex-pending" data-math-display="true"'
            f' data-math-raw="{raw_attr}"><span>{escape_html(loading)}</span></section>'
        )
    return (
        f'<span class="katex-inline katex-pending" data-math-display="false"'
        f' data-math-raw="{raw_attr}"><span>…</span></span>'
    )


def _set_attrs(token, raw: str, display: bool) -> None:
    token.attrs[_A_RAW] = raw
    token.attrs[_A_DISPLAY] = display
    token.content = ""


# ---- 行内规则 ----
def inline_katex(state, silent: bool) -> bool:
    """upstream: inlineKatex（findInlineKatexStart + inlineRuleNonStandard）。"""
    src = state.src
    pos = state.pos
    if pos >= len(src) or src[pos] != "$":
        return False
    if _is_amount_dollar(src, pos):
        return False
    match = INLINE_NONSTD_RE.match(src, pos)
    if match is None:
        return False
    if not silent:
        token = state.push("katex_inline", "", 0)
        _set_attrs(token, match.group(0), len(match.group(1)) == 2)
    state.pos = match.end()
    return True


def inline_latex(state, silent: bool) -> bool:
    """upstream: inlineLatexKatex（``\\(``），兼作段中 ``\\[`` 兜底。"""
    src = state.src
    pos = state.pos
    if pos >= len(src) or src[pos] != "\\":
        return False
    match = INLINE_LATEX_RE.match(src, pos)
    display = False
    if match is None:
        match = BLOCK_LATEX_RE.match(src, pos)
        display = True
        if match is None:
            return False
    if not silent:
        token = state.push("katex_inline", "", 0)
        _set_attrs(token, match.group(0), display)
    state.pos = match.end()
    return True


# ---- 块规则 ----
def _line_match(state, start_line: int):
    pos = state.bMarks[start_line]
    match = BLOCK_MULTILINE_RE.match(state.src, pos)
    if match is None:
        match = BLOCK_SINGLE_RE.match(state.src, pos)
    return match


def block_katex(state, startLine: int, endLine: int, silent: bool) -> bool:
    """upstream: blockKatex（matchBlockKatex，findIndentedLineStart 见扫描守卫）。

    围栏（```/~~~）由 markdown-it fence 先行消费；规则仅在物理行首触发，
    缩进已由正则 ``[ \\t]{0,3}`` 表达。
    """
    if state.is_code_block(startLine):
        return False
    match = _line_match(state, startLine)
    if match is None:
        return False
    # 独占行：闭合后该行只能剩空白（正则已强制 (?:\n|$)，此处防御性复核）
    end = match.end()
    if end < state.eMarks[startLine]:
        return False
    if silent:
        return True
    next_line = startLine
    line_count = len(state.bMarks)
    while next_line < min(endLine, line_count) and state.bMarks[next_line] < end:
        next_line += 1
    state.line = next_line
    token = state.push("katex_block", "", 0)
    token.map = [startLine, next_line]
    _set_attrs(token, match.group(0), True)
    return True


def block_latex(state, startLine: int, endLine: int, silent: bool) -> bool:
    """upstream: blockLatexKatex（仅行首形态；段中形态走行内兜底）。"""
    if state.is_code_block(startLine):
        return False
    pos = state.bMarks[startLine]
    # 行首至多 3 个空白（对齐 marked 块边界）
    indent = 0
    while indent < 3 and pos + indent < len(state.src) and state.src[pos + indent] in " \t":
        indent += 1
    match = BLOCK_LATEX_RE.match(state.src, pos + indent)
    if match is None:
        return False
    # 匹配必须延伸到本行尾（段中 \\[ 交给行内兜底，避免吞掉同行残余文本）
    line_end = state.eMarks[startLine]
    if match.end() < line_end or state.src[match.end():line_end].strip():
        return False
    if silent:
        return True
    end = match.end()
    next_line = startLine
    line_count = len(state.bMarks)
    while next_line < min(endLine, line_count) and state.bMarks[next_line] < end:
        next_line += 1
    state.line = next_line
    token = state.push("katex_block", "", 0)
    token.map = [startLine, next_line]
    _set_attrs(token, match.group(0), True)
    return True


# ---- 渲染 ----
def render_katex(tokens, idx, options, env):
    token = tokens[idx]
    get_loading = options.get(_LOADING_KEY) if options else None
    return render_pending(token.attrs[_A_RAW], token.attrs[_A_DISPLAY], get_loading)


# ---- upstream: mathDetection.ts:114-116 ----
_STRIP_BREAK_RE = re.compile(r'<br\s*/?>\s*(?=<span class="katex-inline)', re.IGNORECASE)


def strip_break_before_inline_katex(html: str) -> str:
    """upstream: stripBreakBeforeInlineKatex（marked 软/硬换行在段内行首公式前残留 <br>）。"""
    return _STRIP_BREAK_RE.sub("", html)


def register_katex(md, get_loading=None) -> None:
    """装配四条规则（对齐 MDKatex({nonStandard: True}, True)）。

    行内规则必须先于内建 escape，否则 ``\\(`` 会被转义规则吃掉。
    """
    md.options[_LOADING_KEY] = get_loading
    # alt 对齐 markdown-it 内建 fence：块公式需能中断段落/引用/列表
    # （上游 marked 块扩展的 start() 可在任意行重新起块）。
    block_alt = {"alt": ["paragraph", "reference", "blockquote", "list"]}
    md.block.ruler.before("paragraph", "katex_block", block_katex, block_alt)
    md.block.ruler.before("paragraph", "katex_block_latex", block_latex, block_alt)
    md.inline.ruler.before("escape", "katex_inline", inline_katex)
    md.inline.ruler.before("escape", "katex_latex_inline", inline_latex)
    rules = md.renderer.rules
    rules["katex_inline"] = render_katex
    rules["katex_block"] = render_katex
