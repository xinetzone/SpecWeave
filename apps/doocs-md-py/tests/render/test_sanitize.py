"""TR-8.1：nh3 净化层 XSS 回归（对齐上游 DOMPurify 配置语义）。"""

import pytest

from doocs_md_py.render.sanitize import sanitize_html

# (名称, 恶意输入)：净化后不得包含可执行向量。
XSS_CASES = [
    ("script-basic", "<script>alert(1)</script>"),
    ("script-src", '<script src="https://evil.example/x.js"></script>'),
    ("script-split-nest", "<scr<script>ipt>alert(1)</scr</script>ipt>"),
    ("img-onerror", '<img src="x" onerror="alert(1)">'),
    ("img-onerror-unquoted", "<img src=x onerror=alert(1)>"),
    ("a-javascript", '<a href="javascript:alert(1)">x</a>'),
    ("a-javascript-mixedcase", '<a href="JaVaScRiPt:alert(1)">x</a>'),
    ("a-javascript-entity", '<a href="&#106;avascript:alert(1)">x</a>'),
    ("a-javascript-colon-entity", '<a href="javascript&colon;alert(1)">x</a>'),
    ("a-javascript-tab", '<a href="\tjavascript:alert(1)">x</a>'),
    ("a-vbscript", '<a href="vbscript:msgbox(1)">x</a>'),
    ("a-data-html", '<a href="data:text/html,<script>alert(1)</script>">x</a>'),
    ("svg-onload", '<svg onload="alert(1)"></svg>'),
    ("svg-script", "<svg><script>alert(1)</script></svg>"),
    ("iframe-js", '<iframe src="javascript:alert(1)"></iframe>'),
    ("object-data", '<object data="javascript:alert(1)"></object>'),
    ("embed-src", '<embed src="x" />'),
    ("input-onfocus", "<input onfocus=\"alert(1)\" autofocus />"),
    ("details-ontoggle", '<details open ontoggle="alert(1)"></details>'),
    ("marquee-onstart", '<marquee onstart="alert(1)">x</marquee>'),
    ("div-onmouseover", '<div onmouseover="alert(1)">x</div>'),
    ("form-action-js", '<form action="javascript:alert(1)"><button>x</button></form>'),
    ("base-hijack", '<base href="https://evil.example/" />'),
    ("link-import", '<link rel="import" href="https://evil.example/x.html" />'),
    ("meta-refresh", '<meta http-equiv="refresh" content="0;url=javascript:alert(1)" />'),
    ("comment-breakout", "<!--><script>alert(1)</script>-->"),
    ("body-onload", '<body onload="alert(1)">'),
    ("style-expression-tag", "<style>body{background:url(x)}</style>"),
]


@pytest.mark.parametrize("name,payload", XSS_CASES, ids=[c[0] for c in XSS_CASES])
def test_xss_vectors_neutralized(name: str, payload: str) -> None:
    out = sanitize_html(payload)
    lowered = out.lower()
    # 无脚本标签、事件处理器、危险容器/劫持标签
    assert "<script" not in lowered
    assert "onerror" not in lowered
    assert "onload" not in lowered
    assert "onfocus" not in lowered
    assert "ontoggle" not in lowered
    assert "onstart" not in lowered
    assert "onmouseover" not in lowered
    assert "<iframe" not in lowered
    assert "<object" not in lowered
    assert "<embed" not in lowered
    assert "<base" not in lowered
    assert "<meta" not in lowered
    assert "<link" not in lowered
    # 不得残留可执行协议（实体解码后仍需拦截）
    assert "javascript:" not in lowered.replace(" ", "")
    assert "vbscript:" not in lowered


def test_script_content_removed_entirely() -> None:
    # script 为 CLEAN_CONTENT_TAGS：连内部文本一并移除
    out = sanitize_html("<p>keep</p><script>secret = 'SHOWN'</script>")  # example: 脚本内容应被整体移除
    assert "SHOWN" not in out
    assert "keep" in out


def test_normal_content_preserved() -> None:
    html = (
        '<p class="p" style="text-align: center;">你好 <strong class="strong">加粗</strong>'
        '<a href="https://md.doocs.org" title="t" target="_blank">链接</a></p>'
    )
    out = sanitize_html(html)
    assert 'class="p"' in out
    assert 'style="text-align: center;"' in out
    assert '<strong class="strong">加粗</strong>' in out
    assert 'href="https://md.doocs.org"' in out
    assert 'target="_blank"' in out
    # DOMPurify 默认不插入 rel；nh3 link_rel=None
    assert "noopener" not in out


def test_allowed_schemes_and_relative_urls() -> None:
    out = sanitize_html(
        '<a href="mailto:a@b.com">m</a><a href="tel:+123">t</a>'
        '<a href="/path/rel">r</a><a href="#anchor">#</a>'
        '<a href="//cdn.example.com/x">p</a>'
    )
    assert 'href="mailto:a@b.com"' in out
    assert 'href="tel:+123"' in out
    assert 'href="/path/rel"' in out
    assert 'href="#anchor"' in out
    assert 'href="//cdn.example.com/x"' in out


def test_about_blank_data_blob_stripped_like_dompurify() -> None:
    # DOMPurify 默认 ALLOWED_URI_REGEXP 拒绝 about:/data:/blob:
    out = sanitize_html(
        '<img src="about:blank" data-emoji-id="smile">'
        '<img src="data:image/png;base64,AAA=">'
        '<img src="blob:https://x/y">'
    )
    assert "about:blank" not in out
    assert "data:image" not in out
    assert "blob:" not in out
    # data-* 属性保留（前端 hydrate 真实 src）
    assert 'data-emoji-id="smile"' in out


def test_mp_common_profile_kept() -> None:
    html = (
        '<mp-common-profile class="profile-box" data-pluginname="MpCommonProfile"'
        ' data-id="MzIx" data-headimg="https://cdn.example.com/a.png"'
        ' data-nickname="Doocs" data-signature="hi" data-service_type="1"'
        ' data-verify_status="1"></mp-common-profile>'
    )
    out = sanitize_html(html)
    assert "<mp-common-profile" in out
    assert 'data-id="MzIx"' in out
    assert 'data-nickname="Doocs"' in out
    assert 'data-headimg="https://cdn.example.com/a.png"' in out
    assert 'class="profile-box"' in out


def test_mermaid_placeholder_protected_and_restored() -> None:
    html = (
        '<div><p>前</p><!--mermaid-start-->\n<div data-placeholder="p1" '
        'data-md-diagram-state="0">\n<svg><foreignObject>x</foreignObject></svg>\n</div>'
        "\n<!--mermaid-end--><p>后</p></div>"
    )
    out = sanitize_html(html)
    assert "<!--mermaid-start-->" in out
    assert "<!--mermaid-end-->" in out
    assert 'data-md-diagram-state="0"' in out
    assert "foreignObject" in out  # 受保护内容原样还原，不经白名单剥离
    assert "data-md-protected" not in out
    assert "<p>前</p>" in out and "<p>后</p>" in out


def test_infographic_placeholder_protected() -> None:
    html = (
        '<!--infographic-start--><div data-placeholder="ig1">{json}</div>'
        "<!--infographic-end-->"
    )
    out = sanitize_html(html)
    assert "<!--infographic-start-->" in out
    assert 'data-placeholder="ig1"' in out
    assert "{json}" in out


def test_multiple_placeholders_restored_in_order() -> None:
    html = (
        "<!--mermaid-start-->M0<!--mermaid-end-->"
        "<p>x</p>"
        "<!--infographic-start-->I0<!--infographic-end-->"
        "<!--mermaid-start-->M1<!--mermaid-end-->"
    )
    out = sanitize_html(html)
    assert out.index("M0") < out.index("<p>x</p>") < out.index("I0") < out.index("M1")


def test_svg_icons_kept() -> None:
    html = (
        '<svg class="octicon" viewBox="0 0 16 16" width="16" height="16" '
        'aria-hidden="true"><path d="M1 2z" fill="#576b95"></path>'
        '<ellipse cx="8" cy="8" rx="2" ry="3"></ellipse></svg>'
    )
    out = sanitize_html(html)
    assert "<svg" in out and "<path" in out and "<ellipse" in out
    assert 'viewBox="0 0 16 16"' in out
    assert 'd="M1 2z"' in out
    assert 'fill="#576b95"' in out
    assert 'aria-hidden="true"' in out


def test_comments_stripped_outside_placeholders() -> None:
    out = sanitize_html("<p>a</p><!-- ordinary comment --><p>b</p>")
    assert "ordinary comment" not in out
    assert "<p>a</p>" in out and "<p>b</p>" in out
