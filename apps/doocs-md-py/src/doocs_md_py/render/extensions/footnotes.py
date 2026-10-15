"""显式脚注扩展（``[^id]`` 引用 + ``[^id]: text`` 定义）。

upstream: packages/core/src/extensions/footnotes.ts（markedFootnotes）。

- 块定义 ``[^id]: 文本`` 独占一行（零缩进），在原位渲染；首条开 <p>、
  最后一条闭 </p>（编号按定义首次出现顺序，重复 id 复用编号）。
- 行内引用 ``[^id]`` 解析失败（无定义）时保持原文字面。
- 文本/标识均原样插入（上游不做转义），XSS 由 T8 净化层兜底。

fnMap 上游是每次 parse 新建；markdown-it 解析器单例复用，这里改挂 env
（每次 render 全新 env，语义等价）。输出空白/换行严格对齐上游模板。
"""

import re

# upstream: footnotes.ts:34/74（match 锚定 bMarks，去 ^）
DEF_RE = re.compile(r"\[\^(.*)\]:(.*)")
REF_RE = re.compile(r"\[\^(.*?)\]")

_FN_MAP_KEY = "mdpy_footnotes"

# token.attrs 键
_A_FN_ID = "mdpy-fn-id"
_A_FN_INDEX = "mdpy-fn-index"

# upstream: footnotes.ts:51-55（模板内空白逐字保留）
_FN_INNER = (
    "\n                <code>{index}.</code> "
    "\n                <span>{text}</span> "
    '\n                    <a id="fnDef-{fn_id}" href="#fnRef-{fn_id}" '
    'style="color: var(--md-primary-color);">↩︎</a>'
    "\n                <br>"
)
_FN_FIRST = '\n            <p style="font-size: 80%;margin: 0.5em 8px;word-break:break-all;">'
_FN_REF = (
    '<sup style="color: var(--md-primary-color);">'
    '\n                    <a href="#fnDef-{fn_id}" id="fnRef-{fn_id}">[{index}]</a>'
    "\n                </sup>"
)


def _get_map(env) -> dict[str, int]:
    fn_map = env.get(_FN_MAP_KEY)
    if fn_map is None:
        fn_map = {}
        env[_FN_MAP_KEY] = fn_map
    return fn_map


# ---- 块规则 ----
def footnote_def(state, startLine: int, endLine: int, silent: bool) -> bool:
    if state.is_code_block(startLine):
        return False
    pos = state.bMarks[startLine]
    # marked start：src.startsWith('[^')，零缩进
    if not state.src.startswith("[^", pos):
        return False
    match = DEF_RE.match(state.src, pos, state.eMarks[startLine])
    if match is None:
        return False
    if silent:
        return True
    fn_id = match.group(1)
    fn_map = _get_map(state.env)
    if fn_id not in fn_map:
        fn_map[fn_id] = len(fn_map) + 1
    token = state.push("footnote_def", "", 0)
    token.map = [startLine, startLine + 1]
    token.content = match.group(2)
    token.attrs[_A_FN_ID] = fn_id
    token.attrs[_A_FN_INDEX] = fn_map[fn_id]
    state.line = startLine + 1
    return True


def render_footnote_def(tokens, idx, options, env):
    token = tokens[idx]
    fn_id = token.attrs[_A_FN_ID]
    index = token.attrs[_A_FN_INDEX]
    total = len(_get_map(env))
    inner = _FN_INNER.format(index=index, text=token.content, fn_id=fn_id)
    if index == 1:
        return _FN_FIRST + inner
    if index == total:
        return inner + "</p>"
    return inner


# ---- 行内规则 ----
def footnote_ref(state, silent: bool) -> bool:
    match = REF_RE.match(state.src, state.pos)
    if match is None:
        return False
    if not silent:
        token = state.push("footnote_ref", "", 0)
        token.content = match.group(0)
        token.attrs[_A_FN_ID] = match.group(1)
    state.pos = match.end()
    return True


def render_footnote_ref(tokens, idx, options, env):
    token = tokens[idx]
    fn_id = token.attrs[_A_FN_ID]
    reference = _get_map(env).get(fn_id)
    if reference is None:
        # upstream: 未定义引用保持字面
        return token.content
    return _FN_REF.format(fn_id=fn_id, index=reference)


def register_footnotes(md) -> None:
    """装配脚注两规则；行内引用须先于内建 link。"""
    md.block.ruler.before("reference", "footnote_def", footnote_def)
    md.inline.ruler.before("link", "footnote_ref", footnote_ref)
    rules = md.renderer.rules
    rules["footnote_def"] = render_footnote_def
    rules["footnote_ref"] = render_footnote_ref
