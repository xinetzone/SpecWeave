"""[TOC] 块扩展：独占一行的文档目录。

upstream: packages/core/src/extensions/toc.ts（markedToc）。
标题收集在 core 预处理阶段完成（等价 marked walkTokens 先于渲染遍历全树），
见 renderer.py 的 _collect_toc_headings；标题 index 为含 h1 在内的文档序。
"""

_TOC_LINE = "[TOC]"


def toc_block(state, startLine: int, endLine: int, silent: bool) -> bool:
    if state.is_code_block(startLine):
        return False
    # 缩进 >=4 视为缩进代码行（blockquote 嵌套时扣除 blkIndent）
    if state.sCount[startLine] - state.blkIndent >= 4:
        return False
    pos = state.bMarks[startLine] + state.tShift[startLine]
    maximum = state.eMarks[startLine]
    line_text = state.src[pos:maximum].strip()
    if line_text != _TOC_LINE:
        return False
    if silent:
        return True
    state.line = startLine + 1
    token = state.push("toc", "", 0)
    token.map = [startLine, state.line]
    return True


def render_toc(tokens, idx, options, env) -> str:
    """upstream: toc.ts:40-69。"""
    all_headings = env.get("toc_headings") or []
    toc_headings = [h for h in all_headings if h["depth"] != 1]
    if not toc_headings:
        return ""

    min_depth = min(h["depth"] for h in toc_headings)
    html = (
        '<nav class="markdown-toc">'
        f'<ul class="toc-ul toc-level-{min_depth} pl-4 border-l ml-2">'
    )
    last_depth = min_depth
    for h in toc_headings:
        depth = h["depth"]
        if depth > last_depth:
            for i in range(last_depth + 1, depth + 1):
                html += f'<ul class="toc-ul toc-level-{i} pl-4 border-l ml-2">'
        elif depth < last_depth:
            for _ in range(last_depth - depth):
                html += "</ul>"
        html += (
            f'<li class="toc-li toc-level-{depth} mb-1">'
            '<a class="text-gray-700 hover:text-blue-600 underline transition-colors" '
            f'href="#{h["index"]}">{h["text"]}</a></li>'
        )
        last_depth = depth

    for _ in range(last_depth - 1):
        html += "</ul>"

    html += "</ul></nav>"
    return html


def register_toc(md) -> None:
    md.block.ruler.before("paragraph", "toc", toc_block)
    md.renderer.rules["toc"] = render_toc
