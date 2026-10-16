"""注音 ruby 扩展对拍测试（转录 ruby.ts 的分配规则）。"""

import pytest

from doocs_md_py.render import init_renderer
from doocs_md_py.render.extensions.ruby import render_ruby_html


def render(md: str) -> str:
    return init_renderer().render_markdown_to_html(md)


# ---- 渲染层 ----
def test_basic_brace_syntax():
    out = render("[漢字]{かんじ}")
    assert (
        '<ruby data-text="漢字" data-ruby="かんじ" data-format="basic">'
        "漢字<rp>(</rp><rt>かんじ</rt><rp>)</rp></ruby>"
    ) in out


def test_hat_syntax_format_attribute():
    out = render("[拼音]^(pin-yin)")
    assert 'data-format="basic-hat"' in out
    # 连字符分隔 → 两字两段
    assert out.count("<ruby ") == 2
    assert 'data-text="拼" data-ruby="pin"' in out
    assert 'data-text="音" data-ruby="yin"' in out


def test_shanghai_split_two_rubies():
    out = render("[上海]{shang-hai}")
    assert out.count("<ruby ") == 2
    assert 'data-text="上" data-ruby="shang"' in out
    assert 'data-text="海" data-ruby="hai"' in out


def test_last_part_consumes_all_remaining_chars():
    # 2 段注音、4 个字：首段 1 字，末段吞剩余 3 字
    out = render_ruby_html("上海城市", "shang-hai", "basic")
    assert out == (
        '<ruby data-text="上" data-ruby="shang" data-format="basic">'
        "上<rp>(</rp><rt>shang</rt><rp>)</rp></ruby>"
        '<ruby data-text="海城市" data-ruby="hai" data-format="basic">'
        "海城市<rp>(</rp><rt>hai</rt><rp>)</rp></ruby>"
    )


def test_more_parts_than_chars_extra_parts_dropped():
    # 2 字 3 段：逐字配对，第 3 段丢弃
    out = render_ruby_html("ab", "x-y-z", "basic")
    assert out.count("<ruby ") == 2
    assert 'data-ruby="x"' in out
    assert 'data-ruby="y"' in out
    assert "z<" not in out
    assert 'data-ruby="z"' not in out


@pytest.mark.parametrize("sep", ["・", "．", "。"])
def test_fullwidth_separators(sep):
    out = render(f"[甲乙]{{甲{sep}乙}}")
    assert out.count("<ruby ") == 2
    assert 'data-ruby="甲"' in out
    assert 'data-ruby="乙"' in out


def test_empty_parts_filtered():
    # x--y 切出空段，过滤后仍为两段
    out = render_ruby_html("拼音", "pin--yin", "basic")
    assert out.count("<ruby ") == 2


def test_no_separator_single_element():
    out = render_ruby_html("漢字", "かんじ", "basic")
    assert out.count("<ruby ") == 1


def test_trim_text_and_ruby():
    out = render("[ 漢字 ]{ かんじ }")
    assert 'data-text="漢字"' in out
    assert 'data-ruby="かんじ"' in out


# ---- 优先级与守卫 ----
def test_normal_link_still_works():
    out = render("[Doocs](https://github.com/doocs)")
    assert '<ruby' not in out
    assert 'href="https://github.com/doocs"' in out


def test_ruby_inside_inline_code_is_literal():
    out = render("`[漢字]{かんじ}`")
    assert "<ruby" not in out
    assert "かんじ" in out  # code 内原文可见但无标签


def test_unmatched_brackets_stay_literal():
    assert "<ruby" not in render("[a]")
    assert "<ruby" not in render("[a]{")
    assert "<ruby" not in render("普通文本")


def test_ruby_and_footnote_coexist():
    out = render("[^1] 与 [漢字]{かんじ}\n\n[^1]: 注")
    assert 'id="fnRef-1"' in out
    assert 'data-ruby="かんじ"' in out


def test_basic_vs_hat_format_distinct():
    assert 'data-format="basic"' in render("[a]{b}")
    assert 'data-format="basic-hat"' in render("[a]^(b)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
