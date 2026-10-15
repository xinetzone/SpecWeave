"""emoji 扩展对拍（upstream: extensions/emoji.test.ts）。

覆盖 parseEmojiTag 标签解析、shortcode 表、legacy/asset 兼容语法、
块/行内两级渲染、安全收敛与围栏隔离。
"""

import re

import pytest

from doocs_md_py.render import init_renderer
from doocs_md_py.render.extensions.emoji import parse_emoji_tag, parse_width_percent
from doocs_md_py.render.extensions.emoji_data import EMOJI_SHORTCODES
from doocs_md_py.render.options import IOpts

TAG = '<Emoji id="liulei" />'
SMALL_IMG = (
    '<img class="md-emoji" data-emoji-id="liulei" '
    'src="about:blank" alt=":liulei:" />'
)
SIZED_IMG = (
    '<img class="md-asset-img" data-emoji-id="liulei" data-asset-id="liulei" '
    'src="about:blank" alt="流泪" style="width:20%" />'
)


@pytest.fixture()
def render():
    renderer = init_renderer(IOpts(asset_resolver=lambda _id: "about:blank"))

    def _render(md: str) -> str:
        return renderer.render_markdown_to_html(md)

    return _render


@pytest.fixture()
def render_js_url():
    renderer = init_renderer(IOpts(asset_resolver=lambda _id: "javascript:alert(1)"))
    return renderer.render_markdown_to_html


class TestParseEmojiTag:
    def test_attrs_any_order(self):
        tag = parse_emoji_tag('<Emoji width="20%" id="aida" alt="挨打" />')
        assert tag is not None
        assert tag.id == "aida"
        assert tag.alt == "挨打"
        assert tag.width_percent == 20
        assert tag.align is None
        assert tag.raw == '<Emoji width="20%" id="aida" alt="挨打" />'

    def test_align_whitelist(self):
        assert parse_emoji_tag('<Emoji id="aida" align="center" />').align == "center"
        assert parse_emoji_tag('<Emoji id="aida" align="middle" />').align is None

    def test_empty_paired_tag(self):
        assert parse_emoji_tag("<Emoji id=\"aida\"></Emoji>").id == "aida"

    def test_missing_id(self):
        assert parse_emoji_tag('<Emoji alt="流泪" />') is None

    def test_unclosed(self):
        assert parse_emoji_tag('<Emoji id="aida"') is None

    def test_name_boundary(self):
        assert parse_emoji_tag('<EmojiFoo id="x" />') is None


class TestParseWidth:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [("20%", 20), ("30", 30), ("999%", 100), ("0", 1), (None, None), ("abc", None)],
    )
    def test_clamp(self, raw, expected):
        assert parse_width_percent(raw) == expected


class TestEmojiTagRender:
    def test_single_inline(self, render):
        out = render(TAG)
        assert SMALL_IMG in out
        assert "<Emoji" not in out
        assert len(re.findall(r"<img\b", out)) == 1

    def test_mid_paragraph(self, render):
        out = render(f"Markdown test 既简单又强大。{TAG} ")
        assert SMALL_IMG in out
        assert "<Emoji" not in out

    def test_sized(self, render):
        out = render('<Emoji id="liulei" alt="流泪" width="20%" />')
        assert SIZED_IMG in out
        assert 'width="20%"' not in out

    def test_width_without_percent(self, render):
        assert 'style="width:30%"' in render('<Emoji id="liulei" width="30" />')

    def test_multiple_stickers(self, render):
        assert len(re.findall(r"<img\b", render(TAG * 3))) == 3

    def test_emoji_foo_not_sticker(self, render):
        assert "md-emoji" not in render('<EmojiFoo id="liulei" />')

    def test_fenced_left_as_code(self, render):
        out = render("```\n<Emoji id=\"liulei\" />\n```")
        assert "<pre" in out
        assert "md-emoji" not in out

    def test_clamp_oversized(self, render):
        assert 'style="width:100%"' in render('<Emoji id="liulei" width="999%" />')

    def test_drop_javascript_url(self, render_js_url):
        out = render_js_url(TAG)
        assert 'src="about:blank"' in out
        assert "javascript:" not in out

    def test_own_line_center(self, render):
        out = render('<Emoji id="liulei" width="20%" align="center" />')
        assert '<p style="text-align:center">' in out
        assert 'style="width:20%"' in out
        assert 'align="center"' not in out

    def test_mid_paragraph_align_ignored(self, render):
        out = render("hello <Emoji id=\"liulei\" align=\"center\" /> world")
        assert SMALL_IMG in out
        assert "text-align:center" not in out

    def test_indented_tag_is_raw_html_block(self, render):
        # 上游 findLineStartEmojiTag 要求标签位于行首零缩进；0-3 空格的
        # <Emoji> 行由通用 HTML 块规则接管并原样透传（marked/markdown-it 一致）
        out = render('   <Emoji id="liulei" align="center" />')
        assert "md-emoji" not in out
        assert "<Emoji" in out


class TestLegacy:
    def test_legacy_token(self, render):
        out = render("{{emoji:liulei}}")
        assert SMALL_IMG in out
        assert "{{emoji:liulei}}" not in out

    def test_asset_syntax(self, render):
        out = render("![流泪](asset://liulei){20%}")
        assert 'data-asset-id="liulei"' in out
        assert 'style="width:20%"' in out
        assert "{20%}" not in out
        assert len(re.findall(r"<img\b", out)) == 1

    def test_asset_without_width_falls_back(self, render):
        out = render("![10001.gif](asset:liulei)")
        assert "md-asset-img" not in out
        assert "asset:liulei" in out

    def test_asset_bad_id_no_breakout(self, render):
        out = render('![x](asset://foo"onclick=alert(1)){20%}')
        assert "md-asset-img" not in out
        assert re.search(r"\sonclick\s*=", out) is None


class TestShortcodes:
    def test_required_aliases(self, render):
        assert "👍" in render(":+1:")
        out = render(":-1: :rocket: :tada:")
        assert "👎" in out and "🚀" in out and "🎉" in out

    def test_unknown_kept_literal(self, render):
        assert ":zzz_no_such:" in render("hi :zzz_no_such: there")

    @pytest.mark.parametrize(
        "name",
        sorted(EMOJI_SHORTCODES)[:50],
    )
    def test_sample_50_of_table(self, render, name):
        # 从上游表确定性抽样 50 条（排序后前 50），逐一对拍替换
        out = render(f":{name}:")
        assert EMOJI_SHORTCODES[name] in out
        assert f":{name}:" not in out

    def test_table_has_at_least_500(self):
        assert len(EMOJI_SHORTCODES) >= 500

    def test_time_ratio_literal(self, render):
        out = render("3:4:5 12:30:45 key: value")
        assert "3:4:5" in out and "12:30:45" in out and "key: value" in out

    def test_after_url_and_time(self, render):
        out = render("see http://example.com/a:b at 12:30 :smile:")
        assert "😄" in out
        assert ":smile:" not in out

    def test_inline_code_not_replaced(self, render):
        out = render("`:smile:`")
        assert ":smile:" in out and "😄" not in out

    def test_container_marker_not_swallowed(self, render):
        # alert（:::tip）尚未接入，冒号容器标记必须保持字面
        assert ":::tip" in render(":::tip")


class TestBlockScanning:
    def test_after_blank_line(self, render):
        out = render(f"hello\n\n{TAG}")
        assert SMALL_IMG in out
        assert len(re.findall(r"<img\b", out)) == 1
