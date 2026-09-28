"""html_transform 纯函数层测试（TR-5.2：标题/列表/代码块/引用四类结构）。"""

import pytest

from mp_archiver.core.html_transform import (
    PageUnavailableError,
    classify_page,
    collect_image_urls,
    content_to_markdown,
    drop_placeholder_images,
    extract_content_soup,
    guess_image_ext,
    localize_image,
    preserve_remote_image,
)

WECHAT_PAGE = """
<html><head><title>测试文章</title></head><body>
<div id="page-content"><div id="js_content" class="rich_media_content">
  <h2>小标题</h2>
  <p>正文段落</p>
  <ul><li>项目一</li><li>项目二</li></ul>
  <ol><li>有序项</li></ol>
  <blockquote><p>引用文字</p></blockquote>
  <pre><code class="language-python">print("hi")</code></pre>
  <img data-src="https://mmbiz.qpic.cn/mmbiz_png/aaa?wx_fmt=png"
       src="data:image/svg+xml;base64,PLACEHOLDER"/>
  <img data-src="https://mmbiz.qpic.cn/mmbiz_jpg/bbb?wx_fmt=jpeg"/>
  <img data-src="https://mmbiz.qpic.cn/mmbiz_png/aaa?wx_fmt=png"/>
  <img src="https://example.com/ext.gif"/>
  <img src="data:image/gif;base64,xx"/>
</div></div>
</body></html>
"""


def test_classify_page():
    assert classify_page(WECHAT_PAGE) == "ok"
    assert classify_page("<html>该内容已被发布者删除</html>") == "deleted"
    assert classify_page("<html>此内容因违规无法查看</html>") == "violation"
    assert classify_page("<html>环境异常，去验证</html>") == "risk"


def test_extract_content_soup_present_and_missing():
    content = extract_content_soup(WECHAT_PAGE)
    assert content.get("id") == "js_content"
    assert content.find("h2") is not None

    with pytest.raises(PageUnavailableError) as exc_info:
        extract_content_soup("<html><body><p>无正文容器</p></body></html>")
    assert exc_info.value.kind == "risk"


def test_collect_image_urls_dedup_and_filter():
    content = extract_content_soup(WECHAT_PAGE)
    urls = collect_image_urls(content)
    assert urls == [
        "https://mmbiz.qpic.cn/mmbiz_png/aaa?wx_fmt=png",
        "https://mmbiz.qpic.cn/mmbiz_jpg/bbb?wx_fmt=jpeg",
        "https://example.com/ext.gif",
    ]


def test_localize_and_preserve_and_drop_placeholders():
    content = extract_content_soup(WECHAT_PAGE)
    url = "https://mmbiz.qpic.cn/mmbiz_png/aaa?wx_fmt=png"
    localize_image(content, url, "images/001.png")
    localized = [
        img for img in content.find_all("img")
        if img.get("data-src") == "images/001.png"
    ]
    assert len(localized) == 2  # 重复 URL 两处引用都被改写
    assert all(img.get("src") == "images/001.png" for img in localized)

    # 下载失败的图片：src 兜底对齐远程真实地址
    failed = "https://mmbiz.qpic.cn/mmbiz_jpg/bbb?wx_fmt=jpeg"
    preserve_remote_image(content, failed)
    failed_img = next(
        img for img in content.find_all("img") if img.get("data-src") == failed
    )
    assert failed_img.get("src") == failed

    # 仅剩 1 张纯 data: 占位（aaa 已本地化、bbb 已兜底、外链图有真实 src）
    assert drop_placeholder_images(content) == 1
    remaining_src = [img.get("src") for img in content.find_all("img")]
    assert "images/001.png" in remaining_src
    assert failed in remaining_src
    assert not any((src or "").startswith("data:") for src in remaining_src)


def test_markdown_preserves_four_structures():
    markdown = content_to_markdown(extract_content_soup(WECHAT_PAGE))
    assert "## 小标题" in markdown
    assert "- 项目一" in markdown and "- 项目二" in markdown
    assert "1. 有序项" in markdown
    assert "> 引用文字" in markdown
    assert "```python" in markdown
    assert 'print("hi")' in markdown


def test_markdown_collapses_excess_blank_lines():
    html = '<div id="js_content"><p>一段</p><p>二段</p></div>'
    markdown = content_to_markdown(extract_content_soup(html))
    assert "\n\n\n" not in markdown
    assert markdown.endswith("\n")


@pytest.mark.parametrize(
    ("url", "content_type", "expected"),
    [
        ("https://mmbiz.qpic.cn/a?wx_fmt=png", "image/jpeg", ".png"),
        ("https://mmbiz.qpic.cn/a?wx_fmt=jpeg", None, ".jpg"),
        ("https://mmbiz.qpic.cn/a", "image/gif; charset=x", ".gif"),
        ("https://mmbiz.qpic.cn/a", "application/octet-stream", ".jpg"),
        ("https://mmbiz.qpic.cn/a", None, ".jpg"),
    ],
)
def test_guess_image_ext(url, content_type, expected):
    assert guess_image_ext(url, content_type) == expected
