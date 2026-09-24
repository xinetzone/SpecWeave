"""纯文本提取与保守清洗测试（Task 10 / AC-18）。"""

import pytest

from mp_archiver.core.text_extract import clean_plain_text, html_to_plain_text


def _page(body_inner: str) -> str:
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>导航标题</title>"
        "</head><body><header>网站导航 首页 关于</header>"
        f"<div id='js_content'>{body_inner}</div>"
        "<footer>版权所有</footer></body></html>"
    )


def test_extracts_block_structure_and_excludes_navigation():
    html = _page(
        "<section><p>第一段。</p><p>第二段。</p></section>"
        "<h2>小标题</h2><ul><li>要点一</li><li>要点二</li></ul>"
    )
    text = html_to_plain_text(html)
    lines = text.splitlines()
    # 正文容器外的导航/版权不得进入语料
    assert "网站导航" not in text and "版权所有" not in text
    assert "第一段。" in lines and "第二段。" in lines
    assert "小标题" in lines
    assert "- 要点一" in lines and "- 要点二" in lines
    # 段落间存在空行分隔（结构保留），无连续多空行
    assert "\n\n" in text
    assert "\n\n\n" not in text


def test_lazy_images_removed_but_text_kept():
    html = _page(
        "<p>前文说明</p>"
        "<p><img data-src='images/001.jpg' src='data:image/gif;base64,xxx'></p>"
        "<p><img data-src='http://x/2.jpg' alt='广告二维码'></p>"
        "<p>后文结论</p>"
    )
    text = html_to_plain_text(html)
    assert "广告二维码" not in text
    assert "data:image" not in text and "001.jpg" not in text
    assert "前文说明" in text and "后文结论" in text


def test_rich_media_placeholder_preserves_semantics():
    html = _page(
        "<p>先听这段语音：</p>"
        "<mpvoice data-name='开场问候'></mpvoice>"
        "<mpvideosnap data-name='演示视频'></mpvideosnap>"
        "<p>正文继续。</p>"
    )
    text = html_to_plain_text(html)
    assert "［音频：开场问候］" in text
    assert "［视频：演示视频］" in text


def test_pre_block_preserves_code_indentation():
    html = _page("<p>代码如下：</p><pre><code>def f():\n    return 1\n</code></pre>")
    text = html_to_plain_text(html)
    assert "def f():" in text
    assert "    return 1" in text  # 四空格缩进保留


def test_fallback_to_body_when_content_container_missing():
    html = "<html><body><p>没有 js_content 容器</p></body></html>"
    assert html_to_plain_text(html).strip() == "没有 js_content 容器"


def test_normalizes_non_breaking_space_and_blank_lines():
    html = _page("<p>行\xa0一</p><p><br></p><p></p><p>行\u3000二</p>")
    text = html_to_plain_text(html)
    assert "\xa0" not in text and "\u3000" not in text
    assert "行 一" in text and "行 二" in text
    assert "\n\n\n" not in text


def test_empty_and_script_only_html_returns_empty_string():
    assert html_to_plain_text("") == ""
    html = _page("<script>var a = 1;</script><style>.x{}</style>")
    assert html_to_plain_text(html) == ""


# ---- 清洗 ---------------------------------------------------------------


def test_clean_remolves_guide_and_decoration_lines():
    text = "\n".join([
        "正文第一段，讨论今天的主题。",
        "长按识别二维码关注我们",
        "正文第二段，内容与关注无关。",
        "点个在看你最好看",
        "▲",
        "———",
    ])
    cleaned, stats = clean_plain_text(text)
    assert "二维码" not in cleaned
    assert "在看" not in cleaned
    assert "▲" not in cleaned and "———" not in cleaned
    assert "正文第一段" in cleaned and "正文第二段" in cleaned
    assert stats.removed_noise_lines >= 4


def test_clean_does_not_mutilate_body_discussing_qrcode():
    body_line = "二维码的技术原理并不复杂，它本质上是一种用黑白模块编码数据的矩阵"
    text = "\n".join([
        body_line,
        "我们扫描二维码时，摄像头先完成定位与纠偏，再逐模块读取比特。",
        "这一段超过四十字的引导语即使提到点击上方蓝字关注公众号也不应被误删，因为它很长。",
    ])
    cleaned, stats = clean_plain_text(text)
    assert body_line in cleaned
    assert "摄像头先完成定位与纠偏" in cleaned
    assert "点击上方蓝字关注公众号" in cleaned  # 长行不强匹配
    assert stats.removed_noise_lines == 0


def test_clean_trims_platform_recommendation_block_at_tail():
    lines = ["正文段落一。", "正文段落二。", "正文段落三。"]
    lines += ["喜欢此内容的人还喜欢", "推荐文章甲", "推荐文章乙"]
    cleaned, stats = clean_plain_text("\n".join(lines))
    assert "喜欢此内容的人还喜欢" not in cleaned
    assert "推荐文章甲" not in cleaned
    assert "正文段落三" in cleaned
    assert stats.trimmed_tail_lines == 3


def test_clean_keeps_anchor_in_first_half():
    # 锚点出现在文章前半部时保守保留（可能是正文引用）
    lines = ["喜欢此内容的人还喜欢", "正文一", "正文二", "正文三", "正文四", "正文五"]
    cleaned, stats = clean_plain_text("\n".join(lines))
    assert "喜欢此内容的人还喜欢" in cleaned
    assert stats.trimmed_tail_lines == 0


def test_clean_collapses_adjacent_duplicate_lines():
    text = "\n".join(["首段。", "同一段声明", "同一段声明", "末段。"])
    cleaned, stats = clean_plain_text(text)
    assert cleaned.count("同一段声明") == 1
    assert stats.collapsed_duplicates == 1
    assert "首段。" in cleaned and "末段。" in cleaned


def test_clean_empty_text_is_stable():
    cleaned, stats = clean_plain_text("")
    assert cleaned == ""
    assert not stats.touched


def test_extract_then_clean_keeps_code_indentation():
    html = _page(
        "<p>正文。</p>"
        "<pre><code>for x in xs:\n    print(x)\n</code></pre>"
        "<p>点个在看你最好看</p>"
    )
    text = html_to_plain_text(html)
    cleaned, _ = clean_plain_text(text)
    assert "    print(x)" in cleaned  # 清洗后缩进仍保留
    assert "在看" not in cleaned
