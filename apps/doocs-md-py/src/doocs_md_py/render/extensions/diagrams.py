"""图表围栏占位扩展（mermaid / plantuml / infographic）。

upstream: packages/core/src/extensions/{mermaid,plantuml,infographic}.ts
+ utils/asyncDiagramState.ts + extensions/diagram-theme.ts。

服务端等价上游 ``typeof window === 'undefined'``：只产出 data-md-diagram-state
="loading" 占位容器（浏览器端再异步渲染 SVG）。NG 约束：不引入 mermaid /
@antv/infographic / PlantUML 编码与网络请求（fflate/deflate/encode64 均不移植，
inlineSvg 占位不需要 imageUrl）。占位容器在 T8 净化白名单中受保护。
"""

import re

from ..html_utils import simple_hash

# upstream: asyncDiagramState.ts:3/14-21
DIAGRAM_STATE_ATTR = "data-md-diagram-state"
STATE_LOADING = "loading"
DEFAULT_MESSAGES = {
    "mermaid_loading": "Loading Mermaid…",
    "mermaid_error": "Mermaid render failed: {detail}",
    "plantuml_loading": "Loading PlantUML diagram…",
    "plantuml_error": "Failed to load PlantUML diagram",
    "infographic_loading": "Loading infographic…",
    "infographic_error": "Infographic render failed: {detail}",
}

_FENCE_RE_TEMPLATE = r"```%s\r?\n([\s\S]*?)\r?\n```"
_PLANTUML_CONTAINER_STYLE = "text-align: center; margin: 16px 8px; overflow-x: auto"

_OPTS_KEY = "mdpy_diagram_opts"


def _resolve_theme_mode(opts) -> str:
    """upstream: diagram-theme.ts:20（非 dark 一律 light）。"""
    return "dark" if opts is not None and opts.theme_mode == "dark" else "light"


def _loading_text(opts, field: str) -> str:
    """upstream: resolveDiagramMessages（messages 缺省才回退英文默认）。"""
    messages = getattr(opts, "diagram_messages", None) if opts is not None else None
    if messages is None:
        return DEFAULT_MESSAGES[field]
    value = getattr(messages, field, "")
    return value if value else DEFAULT_MESSAGES[field]


def _make_fence_rule(lang: str):
    pattern = re.compile(_FENCE_RE_TEMPLATE % lang)

    def fence_diagram(state, startLine: int, endLine: int, silent: bool) -> bool:
        pos = state.bMarks[startLine]
        match = pattern.match(state.src, pos)
        if match is None:
            return False
        # 闭合 ``` 后允许行尾残余空白；非空白残余属畸形输入，仍按上游消费整段
        if silent:
            return True
        token = state.push(f"mdpy_{lang}", "", 0)
        consumed_lines = match.group(0).count("\n") + 1
        next_line = min(startLine + consumed_lines, endLine)
        token.map = [startLine, next_line]
        token.content = match.group(1).strip()
        state.line = next_line
        return True

    fence_diagram.__name__ = f"fence_{lang}"
    return fence_diagram


# ---- mermaid（mermaid.ts:122-138 占位分支）----
def render_mermaid(tokens, idx, options, env):
    code = tokens[idx].content
    opts = options.get(_OPTS_KEY) if options else None
    cache_key = simple_hash(f"{code}-{_resolve_theme_mode(opts)}")
    loading = _loading_text(opts, "mermaid_loading")
    return (
        "<!--mermaid-start-->"
        f'<div id="mermaid-{cache_key}" class="mermaid-diagram"'
        f' {DIAGRAM_STATE_ATTR}="{STATE_LOADING}">{loading}</div>'
        "<!--mermaid-end-->"
    )


# ---- plantuml（plantuml.ts:187-189 inlineSvg 占位分支）----
def render_plantuml(tokens, idx, options, env):
    code = tokens[idx].content
    opts = options.get(_OPTS_KEY) if options else None
    cache_key = simple_hash(f"{code}-{_resolve_theme_mode(opts)}")
    loading = _loading_text(opts, "plantuml_loading")
    return (
        f'<div class="plantuml-diagram" style="{_PLANTUML_CONTAINER_STYLE}"'
        f' data-placeholder="plantuml-{cache_key}"'
        f' {DIAGRAM_STATE_ATTR}="{STATE_LOADING}">\n'
        '      <div style="color: #666; font-style: italic;">'
        f"{loading}</div>\n"
        "    </div>"
    )


# ---- infographic（infographic.ts:266 占位分支，key 带 -v2 后缀）----
def render_infographic(tokens, idx, options, env):
    code = tokens[idx].content
    opts = options.get(_OPTS_KEY) if options else None
    cache_key = simple_hash(f"{code}-{_resolve_theme_mode(opts)}-v2")
    loading = _loading_text(opts, "infographic_loading")
    return (
        "<!--infographic-start-->"
        f'<div id="infographic-{cache_key}" class="infographic-diagram"'
        ' style="width: 100%;"'
        f' {DIAGRAM_STATE_ATTR}="{STATE_LOADING}">{loading}</div>'
        "<!--infographic-end-->"
    )


_DIAGRAM_LANGS = ("mermaid", "plantuml", "infographic")


def convert_diagram_fences(state) -> None:
    """upstream: walkTokens + asDiagramToken 兜底。

    扩展块正则只认恰好三反引号的围栏；~~~ 围栏、四反引号、info 带残余等
    落到内建 fence 的，按 lang 首词改型为图表 token。
    """
    for token in state.tokens:
        if token.type != "fence" or not token.info:
            continue
        lang = token.info.split()[0]
        if lang in _DIAGRAM_LANGS:
            token.type = f"mdpy_{lang}"
            token.content = token.content.strip()


def _ensure_core(md) -> None:
    if md.options.get("mdpy_diagram_core"):
        return
    md.core.ruler.after("block", "mdpy_diagram_fences", convert_diagram_fences)
    md.options["mdpy_diagram_core"] = True


def _register(md, lang: str, rule, render_fn) -> None:
    md.block.ruler.before("fence", f"mdpy_fence_{lang}", rule)
    _ensure_core(md)
    md.renderer.rules[f"mdpy_{lang}"] = render_fn


def register_mermaid(md, get_options=None) -> None:
    md.options[_OPTS_KEY] = get_options() if get_options is not None else None
    _register(md, "mermaid", _make_fence_rule("mermaid"), render_mermaid)


def register_plantuml(md, get_options=None) -> None:
    md.options[_OPTS_KEY] = get_options() if get_options is not None else None
    _register(md, "plantuml", _make_fence_rule("plantuml"), render_plantuml)


def register_infographic(md, get_options=None) -> None:
    md.options[_OPTS_KEY] = get_options() if get_options is not None else None
    _register(md, "infographic", _make_fence_rule("infographic"), render_infographic)
