"""TR-8.2：分享快照净化逐字对拍 apps/api/src/share-sanitize.test.ts。"""

from doocs_md_py.server.share_sanitize import (
    SHARE_PAGE_CSP,
    escape_html,
    sanitize_html_snapshot,
    sanitize_styles_snapshot,
    share_page_csp_meta,
)


# ---- 上游 share-sanitize.test.ts 三条用例逐字移植 ----

def test_ts_strips_script_tags_and_event_handlers() -> None:
    html = '<div onclick="alert(1)"><script>evil()</script><p>ok</p></div>'
    out = sanitize_html_snapshot(html)
    assert "script" not in out
    assert "onclick" not in out
    assert "<p>ok</p>" in out
    # div 外壳保留（仅危险属性/标签被移除）
    assert out.startswith("<div")


def test_ts_strips_dangerous_tags_and_javascript_urls() -> None:
    html = '<iframe src="x"></iframe><a href="javascript:alert(1)">x</a>'
    out = sanitize_html_snapshot(html)
    # 与上游 TS 测试断言一致：危险标签/协议移除，链接文本保留。
    # 注：上游正则 [^"'>\s]* 不消费闭合引号，逐字行为会残留 <a">，
    # 由 share 页 CSP 兜底；此处不断言属性闭合形态。
    assert "iframe" not in out
    assert "javascript:" not in out.lower()
    assert ">x</a>" in out


def test_ts_blocks_style_breakout_and_dangerous_imports() -> None:
    styles = 'body{}</style><script>x</script><style>@import url("javascript:alert(1)");'
    out = sanitize_styles_snapshot(styles)
    assert "</style>" not in out
    assert "script" not in out
    assert "@import" not in out  # 整条 @import 声明（到分号前）被移除


def test_ts_csp_meta_without_scripts() -> None:
    meta = share_page_csp_meta()
    assert "Content-Security-Policy" in meta
    assert "script-src 'none'" in meta


# ---- 转义 ----

def test_escape_html_four_chars() -> None:
    assert escape_html('a&b<c>d"e') == "a&amp;b&lt;c&gt;d&quot;e"


def test_csp_constant_complete() -> None:
    # upstream: share-sanitize.ts:11-22 十条指令完整
    for directive in (
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
    ):
        assert directive in SHARE_PAGE_CSP


# ---- 补充边界（规则集逐字等价） ----

def test_vbscript_and_xlink_href_stripped() -> None:
    html = (
        '<a href="vbscript:msgbox(1)">a</a>'
        '<use xlink:href="javascript:alert(1)"></use>'
    )
    out = sanitize_html_snapshot(html)
    assert "vbscript:" not in out.lower()
    assert "javascript:" not in out.lower()
    assert "xlink:href" not in out
    assert ">a</a>" in out.replace('"', "")  # 残留闭合引号为上游逐字行为
    assert "<use" in out


def test_event_handler_quote_variants() -> None:
    html = (
        "<p onmouseover='alert(1)'>a</p>"
        "<p onload=alert(2)>b</p>"
        '<img OnError="alert(3)" src=x>'
    )
    out = sanitize_html_snapshot(html)
    assert "onmouseover" not in out
    assert "onload" not in out
    assert "onerror" not in out.lower()


def test_dangerous_tag_variants_removed() -> None:
    html = (
        "<object data=x></object><embed src=x>"
        "<form action=x></form><meta charset=utf-8>"
        "<link rel=stylesheet href=x><base href=x>"
    )
    out = sanitize_html_snapshot(html).lower()
    for tag in ("object", "embed", "form", "meta", "link", "base"):
        assert f"<{tag}" not in out


def test_data_text_html_import_stripped() -> None:
    styles = '<style>@import url("data:text/html,<script>x</script>");</style>'
    out = sanitize_styles_snapshot(styles)
    assert "data:text/html" not in out
    assert "@import" not in out
    assert "<style>" in out  # 合法 style 开标签保留


def test_safe_css_import_preserved() -> None:
    styles = "@import url('https://fonts.example.com/a.css');"
    out = sanitize_styles_snapshot(styles)
    assert "@import url('https://fonts.example.com/a.css');" == out


def test_unclosed_script_not_matched_matches_upstream() -> None:
    # 与 JS 正则一致：无 </script> 闭合时 SCRIPT_TAG 不匹配（内容保留），
    # 该差异由 share 页 CSP script-src 'none' 兜底。
    html = "<script>alert(1)"
    assert sanitize_html_snapshot(html) == html
