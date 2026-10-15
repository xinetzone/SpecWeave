"""marked 自定义渲染器的 markdown-it-py 等价实现。

upstream: packages/core/src/renderer/renderer-impl.ts（RendererObject 17 规则）。
解析器差异：marked（JS）→ markdown-it-py（breaks:true、html:true、启用
table/strikethrough）；输出结构按归一化 DOM 1:1。
"""

import re
from dataclasses import dataclass

from markdown_it import MarkdownIt

from .highlight import (
    MAC_CODE_SVG,
    REGISTERED_LANGUAGES,
    highlight_and_format_code,
    render_diff_code,
)
from .html_utils import escape_html, strip_inline_html
from .options import (
    DEFAULT_COUNT_SUMMARY,
    DEFAULT_FOOTNOTE_TITLE,
    IOpts,
)
from .reading_time import ReadTimeResults, reading_time
from .frontmatter import parse_front_matter
from .extensions import (
    register_alert,
    register_component,
    register_emoji,
    register_footnotes,
    register_infographic,
    register_katex,
    register_markup,
    register_mermaid,
    register_plantuml,
    register_ruby,
    register_slider,
    register_toc,
)

_HEADING_TAG_RE = re.compile(r"^h\d$")
_PARAGRAPH_WRAPPER_RE = re.compile(r"^<p(?:\s[^>]*)?>([\s\S]*?)</p>")
_MP_WEIXIN_LINK_RE = re.compile(r"^https?://mp\.weixin\.qq\.com")
_KATEX_ONLY_RE = re.compile(r'^<section class="katex-block"[\s\S]*</section>\s*$')
_IMAGE_SIZE_RE = re.compile(r"\|(\d+)(?:x(\d+))?$")
_DOUBLE_QUOTE_RE = re.compile(r'"')

# upstream: renderer-impl.ts:50-65
ADDITION_STYLE = """
    <style>
      .preview-wrapper pre::before {
        position: absolute;
        top: 0;
        right: 0;
        color: #ccc;
        text-align: center;
        font-size: 0.8em;
        padding: 5px 10px 0;
        line-height: 15px;
        height: 15px;
        font-weight: 600;
      }
    </style>
  """


@dataclass(slots=True)
class CollectedHeading:
    """upstream: renderer-types.ts CollectedHeading。"""

    level: int
    text: str

    def as_dict(self) -> dict[str, int | str]:
        return {"level": self.level, "text": self.text}


@dataclass(slots=True)
class ParseResult:
    """upstream: renderer-impl.ts ParseResult。"""

    yaml_data: dict
    markdown_content: str
    reading_time: ReadTimeResults


@dataclass(slots=True)
class Footnote:
    index: int
    title: str
    link: str


def _extract_file_name(href: str) -> str:
    """upstream: renderer-impl.ts:77。"""
    try:
        url_path = href.split("?")[0].split("#")[0]
        file_name = url_path.split("/")[-1]
        return re.sub(r"\.[^.]*$", "", file_name)
    except Exception:
        return ""


def _transform_legend(legend: str, text: str | None, title: str | None, href: str = "") -> str:
    """upstream: renderer-impl.ts:89（legend 按 - 拆项，首个命中的 alt/title/filename）。"""
    for option in legend.split("-"):
        if option == "alt" and text:
            return text
        if option == "title" and title:
            return title
        if option == "filename" and href:
            name = _extract_file_name(href)
            if name:
                return escape_html(name)
    return ""


def _build_footnote_array(footnotes: list[Footnote]) -> str:
    """upstream: renderer-impl.ts:67。"""
    parts = []
    for fn in footnotes:
        if fn.link == fn.title:
            parts.append(
                '<code style="font-size: 90%; opacity: 0.6;">'
                f"[{fn.index}]</code>: <i style=\"word-break: break-all\">{fn.title}</i><br/>"
            )
        else:
            parts.append(
                '<code style="font-size: 90%; opacity: 0.6;">'
                f"[{fn.index}]</code> {fn.title}: "
                f'<i style="word-break: break-all">{fn.link}</i><br/>'
            )
    return "\n".join(parts)


def _link_raw_text(tokens: list, open_idx: int) -> str:
    """marked Tokens.Link.text 等价：展平链接内叶子节点的可见文本。"""
    depth = 0
    parts: list[str] = []
    i = open_idx + 1
    while i < len(tokens):
        token = tokens[i]
        if token.type == "link_open":
            depth += 1
        elif token.type == "link_close":
            if depth == 0:
                break
            depth -= 1
        elif token.type in ("text", "code_inline", "html_inline"):
            parts.append(token.content)
        elif token.type == "image":
            parts.append(token.content)
        elif token.type in ("softbreak", "hardbreak"):
            parts.append(" ")
        i += 1
    return "".join(parts)


class Renderer:
    """upstream: initRenderer 返回的 RendererAPI。"""

    def __init__(self, opts: IOpts | None = None):
        self.opts = opts or IOpts()
        self.footnotes: list[Footnote] = []
        self.footnote_index = 0
        self.headings: list[CollectedHeading] = []
        self.md = self._build_parser()

    # ---- 生命周期 ----

    def reset(self, new_opts: dict | None = None) -> None:
        self.footnotes.clear()
        self.footnote_index = 0
        self.headings.clear()
        self.opts.merge(new_opts)

    def set_options(self, new_opts: dict) -> None:
        self.opts.merge(new_opts)

    def get_opts(self) -> IOpts:
        return self.opts

    def get_headings(self) -> list[CollectedHeading]:
        return list(self.headings)

    # ---- front-matter ----

    def parse_front_matter_and_content(self, markdown_text: str) -> ParseResult:
        """upstream: renderer-impl.ts:170。"""
        try:
            parsed = parse_front_matter(markdown_text)
            return ParseResult(
                yaml_data=parsed.attributes,
                markdown_content=parsed.body,
                reading_time=reading_time(parsed.body),
            )
        except Exception:
            return ParseResult(
                yaml_data={},
                markdown_content=markdown_text,
                reading_time=reading_time(markdown_text),
            )

    def render_markdown_to_html(self, markdown: str) -> str:
        return self.md.render(markdown, {})

    # ---- HTML 拼装 ----

    def styled_content(
        self,
        style_label: str,
        content: str,
        tag_name: str | None = None,
        style: str | None = None,
    ) -> str:
        """upstream: renderer-impl.ts:210。"""
        tag = tag_name or style_label
        class_name = style_label.replace("_", "-")
        is_heading = bool(_HEADING_TAG_RE.match(tag))
        if is_heading:
            self.headings.append(
                CollectedHeading(level=int(tag[1:]), text=strip_inline_html(content))
            )
        heading_attr = ' data-heading="true"' if is_heading else ""
        style_attr = f' style="{style}"' if style else ""
        return f'<{tag} class="{class_name}"{heading_attr}{style_attr}>{content}</{tag}>'

    def _add_footnote(self, title: str, link: str) -> int:
        for fn in self.footnotes:
            if fn.link == link:
                return fn.index
        self.footnote_index += 1
        self.footnotes.append(Footnote(self.footnote_index, title, link))
        return self.footnote_index

    def _format_count_summary(self, words: int, minutes: int) -> str:
        template = (
            self.opts.count_messages.summary
            if self.opts.count_messages
            else DEFAULT_COUNT_SUMMARY
        )
        return template.replace("{words}", str(words)).replace("{minutes}", str(minutes))

    def build_reading_time(self, read: ReadTimeResults) -> str:
        """upstream: renderer-impl.ts:254。"""
        if not self.opts.count_status or not read.words:
            return ""
        import math

        minutes = math.ceil(read.minutes)
        return (
            '\n      <blockquote class="md-blockquote">\n'
            f'        <p class="md-blockquote-p">{self._format_count_summary(read.words, minutes)}</p>\n'
            "      </blockquote>\n    "
        )

    def build_footnotes(self) -> str:
        """upstream: renderer-impl.ts:269。"""
        if not self.footnotes:
            return ""
        title = (
            self.opts.render_messages.footnote_title
            if self.opts.render_messages
            else DEFAULT_FOOTNOTE_TITLE
        )
        return self.styled_content("h4", title) + self.styled_content(
            "footnotes", _build_footnote_array(self.footnotes), "p"
        )

    def build_addition(self) -> str:
        return ADDITION_STYLE

    def create_container(self, content: str) -> str:
        return self.styled_content("container", content, "section")

    # ---- 规则装配 ----

    def _build_parser(self) -> MarkdownIt:
        md = MarkdownIt("commonmark", {"breaks": True, "html": True})
        md.enable("table").enable("strikethrough")
        rules = md.renderer.rules
        r = self

        def add(name: str, fn) -> None:
            rules[name] = fn

        # heading：open 规则仅输出开标签；headings 收集在 core 预处理完成
        # （等价 marked walkTokens 先于渲染遍历全树，TOC 才能列出后文标题）
        def heading_open(tokens, idx, options, env):
            tag = tokens[idx].tag
            return f'<{tag} class="{tag}" data-heading="true">'

        add("heading_open", heading_open)
        add("heading_close", lambda t, i, o, e: f"</{t[i].tag}>")

        def paragraph_open(tokens, idx, options, env):
            token = tokens[idx]
            inline = tokens[idx + 1]
            inner = md.renderer.renderInline(inline.children or [], options, env)

            is_figure = "<figure" in inner and "<img" in inner
            is_empty = inner.strip() == ""
            is_katex_only = bool(_KATEX_ONLY_RE.match(inner.strip()))

            unwrap = False
            if token.hidden:
                # tight 列表：markdown-it 已隐藏 p 包装，仅放行 inline 内容
                unwrap = True
            elif is_figure or is_empty or is_katex_only:
                # upstream: renderer-impl.ts:290-295
                unwrap = True
            else:
                li_counts = env.get("li_counts")
                if li_counts and li_counts[-1] == 0:
                    # loose 列表项首段去 <p>（upstream: listitem catch + 正则去包装）
                    unwrap = True
                    li_counts[-1] = 1

            if unwrap:
                env.setdefault("p_stack", []).append({"unwrap": True, "inner": inner})
                # 主循环会特判 inline 类型再次渲染；改写类型跳过它，inner 在此一次性输出
                inline.type = "mdpy_skip"
                return inner
            env.setdefault("p_stack", []).append({"unwrap": False, "inner": ""})
            inline.type = "mdpy_skip"
            return f'<p class="p">{inner}'

        add("paragraph_open", paragraph_open)

        def paragraph_close(tokens, idx, options, env):
            state = env["p_stack"].pop()
            return "" if state["unwrap"] else "</p>"

        add("paragraph_close", paragraph_close)

        # blockquote
        add("blockquote_open", lambda t, i, o, e: '<blockquote class="blockquote">')
        add("blockquote_close", lambda t, i, o, e: "</blockquote>")

        # code
        def code_render(tokens, idx, options, env):
            token = tokens[idx]
            raw_lang = (token.info or "").strip()
            lang_text = raw_lang.split(" ")[0]
            # marked 的 fence/indent-code token.text 恰好去掉一个结尾换行
            # （Node 实测："x\n"→"x"、"x\n\n"→"x\n"）；markdown-it token.content
            # 保留该换行，此处对齐 marked 规范化。
            text = token.content
            if text.endswith("\n"):
                text = text[:-1]
            if lang_text.startswith("diff-"):
                return render_diff_code(text, lang_text[5:])
            registered = lang_text in REGISTERED_LANGUAGES
            language = lang_text if registered else "plaintext"
            highlighted = highlight_and_format_code(
                text, language, bool(r.opts.is_show_line_number)
            )
            span = f'<span class="mac-sign" style="padding: 10px 14px 0;">{MAC_CODE_SVG}</span>'
            pending_attr = ""
            if not registered and lang_text != "plaintext":
                escaped = _DOUBLE_QUOTE_RE.sub("&quot;", text)
                pending_attr = (
                    f' data-language-pending="{lang_text}" data-raw-code="{escaped}"'
                    f' data-show-line-number="{"true" if r.opts.is_show_line_number else "false"}"'
                )
            code = f'<code class="language-{raw_lang}"{pending_attr}>{highlighted}</code>'
            return f'<pre class="hljs code__pre">{span}{code}</pre>'

        add("fence", code_render)
        add("code_block", code_render)

        def code_inline(tokens, idx, options, env):
            return r.styled_content("codespan", escape_html(tokens[idx].content), "code")

        add("code_inline", code_inline)

        # list
        def bullet_open(tokens, idx, options, env):
            env.setdefault("list_stack", []).append((False, 1))
            return '<ul class="ul">'

        def ordered_open(tokens, idx, options, env):
            start_value = tokens[idx].attrGet("start")
            start = int(start_value or 1)
            env.setdefault("list_stack", []).append((True, start))
            if start_value is not None and int(start_value) != 1:
                return f'<ol class="ol" start="{start_value}">'
            return '<ol class="ol">'

        def list_close(tokens, idx, options, env):
            ordered, _ = env["list_stack"].pop()
            return "</ol>" if ordered else "</ul>"

        def list_item_open(tokens, idx, options, env):
            ordered, counter = env["list_stack"][-1]
            env["list_stack"][-1] = (ordered, counter + 1)
            env.setdefault("li_counts", []).append(0)
            prefix = f"{counter}. " if ordered else "• "
            return f'<li class="listitem">{prefix}'

        def list_item_close(tokens, idx, options, env):
            env["li_counts"].pop()
            return "</li>"

        add("bullet_list_open", bullet_open)
        add("ordered_list_open", ordered_open)
        add("bullet_list_close", list_close)
        add("ordered_list_close", list_close)
        add("list_item_open", list_item_open)
        add("list_item_close", list_item_close)

        # image
        def image(tokens, idx, options, env):
            token = tokens[idx]
            href = token.attrGet("src") or ""
            title = token.attrGet("title")
            text = token.content
            width_attr = ""
            height_attr = ""
            alt_text = text
            size_match = _IMAGE_SIZE_RE.search(text)
            if size_match:
                alt_text = _IMAGE_SIZE_RE.sub("", text)
                if size_match.group(1):
                    width_attr = f' width="{size_match.group(1)}"'
                if size_match.group(2):
                    height_attr = f' height="{size_match.group(2)}"'
            new_text = (
                _transform_legend(r.opts.legend, alt_text, title, href)
                if r.opts.legend
                else ""
            )
            sub_text = r.styled_content("figcaption", new_text) if new_text else ""
            title_attr = f' title="{title}"' if title else ""
            return (
                f"<figure><img src=\"{href}\"{title_attr}{width_attr}{height_attr}"
                f' alt="{alt_text}"/>{sub_text}</figure>'
            )

        add("image", image)

        # link
        def link_open(tokens, idx, options, env):
            token = tokens[idx]
            href = token.attrGet("href") or ""
            title = token.attrGet("title")
            text = _link_raw_text(tokens, idx)
            if href == text:
                env.setdefault("link_stack", []).append({"skip": True})
                return ""
            cite_ref = None
            if r.opts.cite_status:
                cite_ref = r._add_footnote(title or text, href)
            label = title or text
            env.setdefault("link_stack", []).append({"skip": False, "cite": cite_ref})
            return f'<a href="{href}" title="{label}">'

        def link_close(tokens, idx, options, env):
            state = env.get("link_stack", []).pop() if env.get("link_stack") else {"skip": False}
            if state.get("skip"):
                return ""
            sup = f'<sup>[{state["cite"]}]</sup>' if state.get("cite") else ""
            return f"{sup}</a>"

        add("link_open", link_open)
        add("link_close", link_close)

        # strong / em / del
        add("strong_open", lambda t, i, o, e: '<strong class="strong">')
        add("strong_close", lambda t, i, o, e: "</strong>")
        add("em_open", lambda t, i, o, e: '<em class="em">')
        add("em_close", lambda t, i, o, e: "</em>")
        add("s_open", lambda t, i, o, e: '<del class="del">')
        add("s_close", lambda t, i, o, e: "</del>")

        # table：open 规则预扫整表并隐藏区间内其余 token
        def table_open(tokens, idx, options, env):
            depth = 0
            end = idx
            in_head = False
            head_cells: list[str] = []
            body_rows: list[str] = []
            current_row: list[str] = []
            j = idx + 1
            while j < len(tokens):
                ttype = tokens[j].type
                if ttype == "table_open":
                    depth += 1
                elif ttype == "table_close":
                    if depth == 0:
                        end = j
                        break
                    depth -= 1
                elif ttype == "thead_open":
                    in_head = True
                elif ttype == "thead_close":
                    in_head = False
                elif ttype == "tr_open":
                    current_row = []
                elif ttype == "tr_close":
                    row_html = "".join(current_row)
                    if in_head:
                        # upstream: renderer-impl.ts table() 表头直接挂 th，无 tr 包裹
                        head_cells.append(row_html)
                    else:
                        body_rows.append(r.styled_content("tr", row_html))
                elif ttype in ("th_open", "td_open"):
                    cell_tag = "th" if ttype == "th_open" else "td"
                    style_val = "left"
                    style_attr = tokens[j].attrGet("style")
                    if style_attr and ":" in style_attr:
                        style_val = style_attr.split(":", 1)[1].strip()
                    inline = tokens[j + 1]
                    cell_text = md.renderer.renderInline(inline.children or [], options, env)
                    current_row.append(
                        r.styled_content(cell_tag, cell_text, style=f"text-align: {style_val}")
                    )
                j += 1

            for k in range(idx + 1, end + 1):
                tokens[k].type = "mdpy_skip"

            header_row = "".join(head_cells)
            body = "".join(body_rows)
            return (
                '\n        <section style="max-width: 100%; overflow: auto;'
                ' -webkit-overflow-scrolling: touch">\n'
                '          <table class="preview-table">\n'
                f"            <thead>{header_row}</thead>\n"
                f"            <tbody>{body}</tbody>\n"
                "          </table>\n"
                "        </section>\n      "
            )

        add("table_open", table_open)
        add("mdpy_skip", lambda t, i, o, e: "")

        # hr
        def hr(tokens, idx, options, env):
            raw = tokens[idx].markup
            if "*" in raw:
                variant = "star"
            elif "_" in raw:
                variant = "underscore"
            else:
                variant = "dash"
            return f'<hr class="hr hr-{variant}">'

        add("hr", hr)

        # 扩展（装配顺序对齐 renderer-impl.ts:468-497；component 最早）
        register_component(md, get_options=lambda: r.opts)

        register_markup(md)

        def resolve_emoji_url(emoji_id: str) -> str:
            resolver = r.opts.asset_resolver
            return resolver(emoji_id) if resolver is not None else "about:blank"

        register_emoji(md, resolve_url=resolve_emoji_url)
        register_toc(md)
        register_slider(md)
        register_alert(md)

        def get_katex_loading():
            messages = r.opts.render_messages
            if messages is None:
                return None
            return messages.katex_loading or None

        register_katex(md, get_loading=get_katex_loading)
        register_footnotes(md)

        def get_diagram_options():
            return r.opts

        register_mermaid(md, get_options=get_diagram_options)
        register_plantuml(md, get_options=get_diagram_options)
        register_infographic(md, get_options=get_diagram_options)
        register_ruby(md)

        # core 预处理：inline 子解析完成后、渲染前收集标题（含 TOC 目录数据）
        def collect_headings(state) -> None:
            self._collect_headings(state)

        md.core.ruler.after("text_join", "mdpy_collect_headings", collect_headings)

        return md

    def _collect_headings(self, state) -> None:
        """等价 marked walkTokens：文档序遍历 heading token，收集大纲与 TOC。

        TOC 的 text/depth/index 用原始 inline 源文（marked token.text 语义）；
        大纲 self.headings 用渲染后 stripInlineHtml 文本（styledContent 语义）。
        index 含被过滤的 h1。
        """
        toc_headings: list[dict] = []
        collected: list[CollectedHeading] = []
        tokens = state.tokens
        i = 0
        while i < len(tokens):
            if tokens[i].type == "heading_open":
                tag = tokens[i].tag
                depth = int(tag[1:])
                inline = tokens[i + 1]
                raw_text = inline.content or ""
                toc_headings.append(
                    {"text": raw_text, "depth": depth, "index": len(toc_headings)}
                )
                rendered = state.md.renderer.renderInline(
                    inline.children or [], state.md.options, state.env
                )
                collected.append(CollectedHeading(level=depth, text=strip_inline_html(rendered)))
                i += 3
                continue
            i += 1
        state.env["toc_headings"] = toc_headings
        self.headings.extend(collected)
