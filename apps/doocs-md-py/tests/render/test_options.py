"""render/options.py 测试（upstream: packages/shared/src/types/common.ts IOpts）。

本轮聚焦 ``IOpts.merge`` 的浅合并契约（upstream ``setOptions`` 的
``{ ...opts, ...newOpts }``）：仅覆盖显式给出的键，falsy 值同样生效。
"""

import pytest

from doocs_md_py.render.options import (
    DEFAULT_COUNT_SUMMARY,
    DEFAULT_FOOTNOTE_TITLE,
    CountMessages,
    DiagramMessages,
    IOpts,
    RenderMessages,
)


def test_default_field_values():
    opts = IOpts()
    assert opts.legend is None
    assert opts.cite_status is False
    assert opts.count_status is False
    assert opts.is_mac_code_block is False
    assert opts.is_show_line_number is False
    assert opts.theme_mode == "light"
    assert opts.components is None
    assert opts.diagram_messages is None
    assert opts.count_messages is None
    assert opts.render_messages is None
    assert opts.asset_resolver is None


def test_message_dataclass_defaults():
    assert CountMessages().summary == DEFAULT_COUNT_SUMMARY
    assert RenderMessages().footnote_title == DEFAULT_FOOTNOTE_TITLE
    assert RenderMessages().unknown_component == ""
    assert RenderMessages().katex_loading == ""
    assert DiagramMessages().mermaid_error == ""
    assert DiagramMessages().infographic_error == ""


def test_merge_applies_every_explicit_key():
    opts = IOpts(legend="legend", theme_mode="light")
    merged = opts.merge(
        {"legend": "new-legend", "is_show_line_number": True, "theme_mode": "dark"}
    )
    assert merged is opts
    assert opts.legend == "new-legend"
    assert opts.is_show_line_number is True
    assert opts.theme_mode == "dark"


def test_merge_overrides_with_falsy_values():
    opts = IOpts(legend="legend", is_mac_code_block=True, theme_mode="dark")
    opts.merge({"legend": "", "is_mac_code_block": False, "theme_mode": ""})
    assert opts.legend == ""
    assert opts.is_mac_code_block is False
    assert opts.theme_mode == ""


def test_merge_accepts_nested_message_objects():
    messages = RenderMessages(katex_loading="加载中")
    opts = IOpts()
    opts.merge({"render_messages": messages})
    assert opts.render_messages is messages
    assert opts.render_messages.katex_loading == "加载中"


@pytest.mark.parametrize("patch", [None, {}, {"legend": None}])
def test_merge_without_effective_keys_returns_self(patch):
    opts = IOpts(legend="legend")
    result = opts.merge(patch)
    assert result is opts
    if isinstance(patch, dict) and "legend" in patch:
        assert opts.legend is None
    else:
        assert opts.legend == "legend"


def test_merge_rejects_unknown_key():
    # slots=True：未声明字段无法注入（浅合并只覆盖 IOpts 已声明键）
    with pytest.raises(AttributeError):
        IOpts().merge({"unknown_option": 1})
