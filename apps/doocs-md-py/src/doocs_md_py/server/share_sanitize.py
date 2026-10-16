"""只读分享页快照净化（upstream: apps/api/src/share-sanitize.ts）。

比渲染主净化（DOMPurify/nh3）更严格的纯正则规则集，用于分享页 HTML/样式快照：
移除 script 与危险容器标签、事件处理器、javascript:/vbscript: 协议属性；
样式快照额外移除 </style> 闭合逃逸与危险 @import。
"""

import re

# upstream: share-sanitize.ts:2-8
def escape_html(text: str) -> str:
    """转义文本以插值进分享页 HTML（文本或双引号属性）。"""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# upstream: share-sanitize.ts:11-22
SHARE_PAGE_CSP = "; ".join(
    [
        "default-src 'self'",
        "script-src 'none'",
        "style-src 'unsafe-inline'",
        "img-src 'self' https: data: blob:",
        "font-src https: data:",
        "connect-src 'none'",
        "frame-src 'none'",
        "object-src 'none'",
        "base-uri 'none'",
        "form-action 'self'",
    ]
)


def share_page_csp_meta() -> str:
    """upstream: share-sanitize.ts:24-26。"""
    return f'<meta http-equiv="Content-Security-Policy" content="{SHARE_PAGE_CSP}" />'


_SCRIPT_TAG = re.compile(
    r"<script\b[^<]*(?:(?!</script>)<[^<]*)*</script>", re.IGNORECASE
)
_DANGEROUS_TAGS = re.compile(
    r"</?(?:iframe|object|embed|form|meta|link|base)\b[^>]*>", re.IGNORECASE
)
_EVENT_HANDLERS = re.compile(
    r"""\son\w+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)""", re.IGNORECASE
)
_DANGEROUS_URL_ATTRS = re.compile(
    r"""\s(href|src|xlink:href)\s*=\s*(?:("|')\s*)?"""
    r"(?:javascript|vbscript):[^\"'>\s]*",
    re.IGNORECASE,
)
_STYLE_BREAKOUT = re.compile(r"</style>", re.IGNORECASE)
_DANGEROUS_CSS_IMPORT = re.compile(
    r"@import\s[^;]*(?:javascript|data:text/html)", re.IGNORECASE
)


def sanitize_html_snapshot(html: str) -> str:
    """upstream: share-sanitize.ts:35-41。"""
    html = _SCRIPT_TAG.sub("", html)
    html = _DANGEROUS_TAGS.sub("", html)
    html = _EVENT_HANDLERS.sub("", html)
    html = _DANGEROUS_URL_ATTRS.sub("", html)
    return html


def sanitize_styles_snapshot(styles_html: str) -> str:
    """upstream: share-sanitize.ts:43-46。"""
    html = sanitize_html_snapshot(styles_html)
    html = _STYLE_BREAKOUT.sub("", html)
    html = _DANGEROUS_CSS_IMPORT.sub("", html)
    return html
