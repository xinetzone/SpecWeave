"""HTML 净化层（upstream: packages/core/src/utils/markdownHelpers.ts:17 sanitizeHtml）。

上游用 isomorphic-dompurify（DOMPurify v3.1.7），本仓以 nh3（ammonia 绑定）复刻：
- 默认标签/属性白名单 + 渲染器所需补充（section/nav/svg 系列/mp-common-profile）；
- URL 协议集合对齐 DOMPurify 默认 ALLOWED_URI_REGEXP
  （(f|ht)tps?/mailto/tel/callto/sms/cid/xmpp；拒绝 about:/data:/blob:）；
- 不插入 link rel（DOMPurify 默认不插；nh3 默认的 noopener noreferrer 关闭）；
- data-*/aria-* 前缀通配；style 属性原值保留（DOMPurify 默认不解析 CSS 声明）；
- mermaid/infographic 占位含 HTML 注释，净化前以 data-md-protected span 保护、净化后还原
  （DOMPurify 会剥注释导致占位结构坍塌；v3.1.7+ 还会剥 foreignObject）。
"""

import re

import nh3

# upstream: markdownHelpers.ts:6-8
_INFOGRAPHIC_RE = re.compile(
    r"<!--infographic-start-->[\s\S]*?<!--infographic-end-->"
)
_MERMAID_RE = re.compile(r"<!--mermaid-start-->[\s\S]*?<!--mermaid-end-->")
_PROTECTED_SPAN_RE = re.compile(r'<span data-md-protected="(\d+)"></span>')

# nh3 默认 HTML 白名单（jsoup/ammonia 基线，已含 ruby/rp/rt、table 全套、
# details/summary、figure/figcaption 等），补齐渲染器与 DOMPurify 默认 HTML5 集
# 中额外涉及的标签。
_EXTRA_TAGS = frozenset(
    {
        # 组件/排版骨架（ammonia 默认缺，渲染器大量使用 section）
        "section",
        "nav",
        # alert 图标与 mac-sign 内联 SVG
        "svg",
        "path",
        "ellipse",
        # 微信公众号自定义元素（DOMPurify ADD_TAGS）
        "mp-common-profile",
        # DOMPurify 默认允许的表单/媒体元素
        "form",
        "button",
        "input",
        "select",
        "option",
        "optgroup",
        "textarea",
        "label",
        "fieldset",
        "legend",
        "video",
        "audio",
        "source",
        "track",
    }
)

# 通用属性：渲染器模板产出 + DOMPurify 默认 HTML5 常见属性。
# 事件处理器 on* 不在列（nh3 对未列属性一律剥离）。
_GENERIC_ATTRS = frozenset(
    {
        # 全局
        "class",
        "id",
        "style",
        "title",
        "lang",
        "dir",
        "align",
        "hidden",
        "tabindex",
        "role",
        # 链接/图片
        "target",
        "rel",
        "href",
        "src",
        "alt",
        "width",
        "height",
        "srcset",
        "sizes",
        # 表格/列表
        "colspan",
        "rowspan",
        "start",
        "span",
        "scope",
        "headers",
        # 引用/时间
        "cite",
        "datetime",
        "hreflang",
        # 表单
        "action",
        "method",
        "enctype",
        "name",
        "value",
        "type",
        "placeholder",
        "checked",
        "disabled",
        "readonly",
        "required",
        "for",
        "media",
        # 媒体
        "controls",
        "autoplay",
        "loop",
        "muted",
        "poster",
        "preload",
        "playsinline",
        "label",
        "kind",
        "default",
        # 内联 SVG（mac-sign / octicon）
        "xmlns",
        "version",
        "x",
        "y",
        "viewBox",
        "d",
        "cx",
        "cy",
        "rx",
        "ry",
        "fill",
        "stroke",
        "stroke-width",
        "aria-hidden",
    }
)

# DOMPurify 默认 ALLOWED_URI_REGEXP 允许的协议集（nh3 默认多出
# bitcoin/geo/irc/magnet/ssh/webcal 等，此处收窄对齐）。相对/锚点/协议相对 URL
# 由 url_relative=pass_through 放行。
_URL_SCHEMES = frozenset(
    {
        "http",
        "https",
        "ftp",
        "ftps",
        "mailto",
        "tel",
        "callto",
        "sms",
        "cid",
        "xmpp",
    }
)

_cleaner = nh3.Cleaner(
    tags=set(nh3.ALLOWED_TAGS) | set(_EXTRA_TAGS),
    attributes={"*": set(_GENERIC_ATTRS)},
    generic_attribute_prefixes={"data-", "aria-"},
    url_schemes=set(_URL_SCHEMES),
    link_rel=None,
    # script/style 默认即在 CLEAN_CONTENT_TAGS（连内容一并移除），注释默认剥除。
)


def sanitize_html(html: str) -> str:
    """upstream: markdownHelpers.ts:17-46。"""
    protected: list[str] = []

    def _protect(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f'<span data-md-protected="{len(protected) - 1}"></span>'

    html = _INFOGRAPHIC_RE.sub(_protect, html)
    html = _MERMAID_RE.sub(_protect, html)
    html = _cleaner.clean(html)
    html = _PROTECTED_SPAN_RE.sub(lambda m: protected[int(m.group(1))], html)
    return html
