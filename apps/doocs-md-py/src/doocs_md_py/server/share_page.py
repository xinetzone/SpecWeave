"""分享正文页装配与页脚注入（upstream: apps/api/src/share-page.ts 1:1）。

- 创建分享时存库的是含 ``{{SHARE_AUTHOR}}``/``{{SHARE_VIEW_COUNT}}`` 占位符的整页；
- 每次浏览用当前作者名与阅读数替换占位符；
- 兼容旧版快照：检测到旧页脚结构时整块替换并补样式。
"""

import math
import re

from .share_head import share_page_favicon_link
from .share_sanitize import escape_html, share_page_csp_meta

# upstream: share-page.ts:4-5
SHARE_VIEW_COUNT_PLACEHOLDER = "{{SHARE_VIEW_COUNT}}"
SHARE_AUTHOR_PLACEHOLDER = "{{SHARE_AUTHOR}}"

# upstream: share-page.ts:11-44
SHARE_FOOTER_STYLES = """
    .share-footer {
      margin-top: 56px;
      padding: 24px 16px 16px;
      border-top: 1px solid #ebebeb;
      text-align: center;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    .share-footer-inner {
      margin: 0;
      display: inline-flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: center;
      gap: 6px 10px;
      max-width: 100%;
      font-size: 12px;
      line-height: 1.6;
      color: #888;
    }
    .share-footer-author {
      color: #555;
      font-weight: 500;
    }
    .share-footer-divider {
      color: #d4d4d4;
      user-select: none;
      font-weight: 300;
    }
    .share-footer-meta {
      color: #aaa;
      font-size: 11px;
      letter-spacing: 0.02em;
    }"""


class ShareFooterAuthor:
    """upstream: share-page.ts:7-9（结构类型；Python 用简单类承载 displayName）。"""

    __slots__ = ("display_name",)

    def __init__(self, display_name: str):
        self.display_name = display_name


# upstream: share-page.ts:46-49
def build_share_author_html(author: ShareFooterAuthor) -> str:
    safe_name = escape_html(author.display_name)
    return f"由 {safe_name} 分享"


# upstream: share-page.ts:51-63
def _build_share_footer_html(author_html: str, view_count: int | str) -> str:
    if isinstance(view_count, str):
        count = view_count
    else:
        count = str(max(0, math.floor(view_count)))

    return f"""<div class="share-footer">
      <p class="share-footer-inner">
        <span class="share-footer-author">{author_html}</span>
        <span class="share-footer-divider" aria-hidden="true">·</span>
        <span class="share-footer-meta">阅读 {count} 次</span>
      </p>
    </div>"""


def _build_share_footer_with_placeholders() -> str:
    # upstream: share-page.ts:65-67
    return _build_share_footer_html(
        SHARE_AUTHOR_PLACEHOLDER, SHARE_VIEW_COUNT_PLACEHOLDER
    )


# upstream: share-page.ts:69-117
def build_share_page_html(title: str, body_html: str, styles_html: str) -> str:
    safe_title = escape_html(title or "Markdown 分享")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex, nofollow" />
  {share_page_csp_meta()}
  {share_page_favicon_link()}
  <title>{safe_title}</title>
  {styles_html}
  <style>
    body {{
      margin: 0;
      background: #f5f5f5;
    }}
    .share-page {{
      max-width: 750px;
      margin: 0 auto;
      padding: 20px;
      background: #ffffff;
      box-sizing: border-box;
      min-height: 100vh;
    }}
    .share-content {{
      background: #ffffff;
    }}
    .share-page .diagram-download-bar {{
      display: none !important;
    }}
    {SHARE_FOOTER_STYLES}
  </style>
</head>
<body>
  <div class="share-page">
    <div class="share-content">
    {body_html}
    </div>
    {_build_share_footer_with_placeholders()}
  </div>
</body>
</html>"""


# upstream: share-page.ts:119
_LEGACY_FOOTER_RE = re.compile(r'<div class="share-footer">[\s\S]*?</div>')


# upstream: share-page.ts:121-125
def _ensure_share_footer_styles(html: str) -> str:
    if ".share-footer-author {" in html:
        return html
    # JS String.replace 仅替换第一处
    return html.replace("</style>", f"{SHARE_FOOTER_STYLES}\n  </style>", 1)


# upstream: share-page.ts:128-151
def inject_share_footer(
    html: str, author: ShareFooterAuthor, view_count: int
) -> str:
    author_html = build_share_author_html(author)
    count_text = str(max(0, math.floor(view_count)))

    next_html = html
    if SHARE_AUTHOR_PLACEHOLDER in next_html:
        next_html = next_html.replace(SHARE_AUTHOR_PLACEHOLDER, author_html)
    if SHARE_VIEW_COUNT_PLACEHOLDER in next_html:
        next_html = next_html.replace(SHARE_VIEW_COUNT_PLACEHOLDER, count_text)

    needs_legacy_footer = "share-footer-copy" in next_html or (
        "share-footer" in next_html and "share-footer-author" not in next_html
    )

    if needs_legacy_footer and _LEGACY_FOOTER_RE.search(next_html):
        next_html = _LEGACY_FOOTER_RE.sub(
            lambda _m: _build_share_footer_html(author_html, count_text),
            next_html,
            count=1,
        )
        next_html = _ensure_share_footer_styles(next_html)

    return next_html
