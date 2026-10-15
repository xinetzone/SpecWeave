"""分享页/密码门模板逐字契约（upstream: share-page.ts/share-gate-page.ts/share-head.ts）。"""

from doocs_md_py.server import share_gate_page
from doocs_md_py.server.share_head import SHARE_FAVICON_PATH, share_page_favicon_link
from doocs_md_py.server.share_page import (
    SHARE_AUTHOR_PLACEHOLDER,
    SHARE_FOOTER_STYLES,
    SHARE_VIEW_COUNT_PLACEHOLDER,
    ShareFooterAuthor,
    build_share_author_html,
    build_share_page_html,
    inject_share_footer,
)
from doocs_md_py.server.share_sanitize import SHARE_PAGE_CSP

AUTHOR = ShareFooterAuthor("张三")


# ---- head ----


def test_favicon_link_literal():
    assert SHARE_FAVICON_PATH == "/images/favicon-32x32.png"
    assert share_page_favicon_link() == (
        '<link rel="icon" type="image/png" sizes="32x32" '
        'href="/images/favicon-32x32.png" />'
    )


# ---- 正文页骨架 ----


def test_share_page_skeleton_literals():
    html = build_share_page_html("标题", "<p>正文</p>", "<style>a{}</style>")
    assert "<!DOCTYPE html>" in html
    assert '<html lang="zh-CN">' in html
    assert '<meta name="robots" content="noindex, nofollow" />' in html
    assert 'http-equiv="Content-Security-Policy"' in html
    assert SHARE_PAGE_CSP in html
    assert "<title>标题</title>" in html
    assert "max-width: 750px" in html
    assert ".diagram-download-bar" in html
    assert "<p>正文</p>" in html
    # 存库版本含占位符（浏览时才替换）
    assert SHARE_AUTHOR_PLACEHOLDER in html
    assert SHARE_VIEW_COUNT_PLACEHOLDER in html


def test_share_page_default_title_and_escape():
    html = build_share_page_html("", "<p>x</p>", "")
    assert "<title>Markdown 分享</title>" in html
    evil = build_share_page_html("<script>x</script>", "<p>x</p>", "")
    assert "<title>&lt;script&gt;x&lt;/script&gt;</title>" in evil


def test_author_html_escape():
    assert build_share_author_html(ShareFooterAuthor("a<b>")) == "由 a&lt;b&gt; 分享"
    assert build_share_author_html(AUTHOR) == "由 张三 分享"


# ---- 页脚注入 ----


def test_inject_placeholders():
    html = build_share_page_html("t", "<p>x</p>", "")
    injected = inject_share_footer(html, AUTHOR, 3)
    assert SHARE_AUTHOR_PLACEHOLDER not in injected
    assert SHARE_VIEW_COUNT_PLACEHOLDER not in injected
    assert "由 张三 分享" in injected
    assert "阅读 3 次" in injected


def test_inject_floors_negative_and_floats():
    html = build_share_page_html("t", "<p>x</p>", "")
    injected = inject_share_footer(html, AUTHOR, -5)
    assert "阅读 0 次" in injected


def test_inject_without_placeholders_is_passthrough():
    plain = "<html><body>nothing</body></html>"
    assert inject_share_footer(plain, AUTHOR, 1) == plain


# ---- legacy 页脚兼容 ----


def test_legacy_footer_replaced_and_styles_injected():
    # 旧快照：有 share-footer-copy 触发 legacy 分支，无新页脚样式
    legacy = (
        "<html><head><style>body{color:red}</style></head>"
        "<body><div class=\"share-footer\">旧脚注 share-footer-copy</div>"
        "</body></html>"
    )
    injected = inject_share_footer(legacy, AUTHOR, 7)
    assert "share-footer-copy" not in injected
    assert "由 张三 分享" in injected
    assert "阅读 7 次" in injected
    assert ".share-footer-author {" in injected
    # 样式插在 </style> 之前
    assert injected.index(".share-footer-author {") < injected.index("</style>")


def test_legacy_footer_kept_when_new_styles_present():
    # 含新样式标记时不重复注入
    legacy = (
        "<html><head><style>.share-footer-author { color:#000 }</style></head>"
        "<body><div class=\"share-footer\">share-footer-copy</div></body></html>"
    )
    injected = inject_share_footer(legacy, AUTHOR, 2)
    assert "阅读 2 次" in injected
    # SHARE_FOOTER_STYLES 整块未再插入（只可能出现页面既有的短标记一次）
    assert injected.count(".share-footer-meta") == 0


# ---- 密码门 ----


def test_gate_page_skeleton():
    html = share_gate_page.build_share_gate_html("abc123def456", "机密文档")
    assert "<title>机密文档 - 需要密码</title>" in html
    assert 'action="/s/abc123def456/unlock"' in html
    assert 'method="POST"' in html
    assert 'name="password" type="password"' in html
    assert "autocomplete=\"current-password\"" in html
    assert "required autofocus" in html
    # 主色 #07c160（focus 边框 + 按钮）与 hover 色
    assert "#07c160" in html
    assert "#06ad56" in html
    assert "noindex, nofollow" in html
    assert SHARE_PAGE_CSP in html
    # 无错误时不渲染错误条
    assert 'class="error"' not in html
    # 无作者时默认署名
    assert "由 doocs/md 分享" in html


def test_gate_page_error_variants():
    invalid = share_gate_page.build_share_gate_html(
        "a" * 12, "t", error="invalid"
    )
    assert "密码错误，请重试。" in invalid
    limited = share_gate_page.build_share_gate_html(
        "a" * 12, "t", error="rate_limited"
    )
    assert "尝试次数过多，请稍后再试。" in limited
    assert 'class="error"' in limited


def test_gate_page_author_and_escape():
    html = share_gate_page.build_share_gate_html(
        "a" * 12, "<b>", author=ShareFooterAuthor("李<四")
    )
    assert "<h1>&lt;b&gt;</h1>" in html
    assert "由 李&lt;四 分享" in html
    assert "由 doocs/md 分享" not in html


def test_footer_styles_block_is_upstream_literal():
    # 关键样式锚点
    for anchor in (
        "margin-top: 56px",
        "border-top: 1px solid #ebebeb",
        ".share-footer-divider",
        "letter-spacing: 0.02em",
    ):
        assert anchor in SHARE_FOOTER_STYLES
