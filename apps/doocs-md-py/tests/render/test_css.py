"""render/css.py 单元测试（upstream: cssVariables.ts/cssProcessor.ts）。"""

import json
from pathlib import Path

import pytest

from doocs_md_py.render.css import (
    CSSVariableConfig,
    escape_style_content,
    generate_css_variables,
    generate_heading_styles,
    process_css,
)

SNAPSHOT_PATH = Path(__file__).parent.parent / "golden" / "css_snapshot.json"


def _config_from_json(data: dict) -> CSSVariableConfig:
    mapping = {
        "primaryColor": "primary_color",
        "fontFamily": "font_family",
        "fontSize": "font_size",
        "lineHeight": "line_height",
        "blockSpacing": "block_spacing",
        "linkColor": "link_color",
        "blockquoteBackground": "blockquote_background",
        "isUseIndent": "is_use_indent",
        "isUseJustify": "is_use_justify",
    }
    kwargs = {py_key: data.get(js_key) for js_key, py_key in mapping.items()}
    return CSSVariableConfig(**kwargs)


# ---- golden 对拍（上游 Node 22 输出固化于 css_snapshot.json） ----


def test_css_golden_snapshot_exists():
    assert SNAPSHOT_PATH.exists()


def test_golden_css_variables():
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    for case in snapshot["variables"]:
        config = _config_from_json(case["input"])
        assert generate_css_variables(config) == case["expected"], case["name"]


def test_golden_heading_styles():
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    for case in snapshot["headings"]:
        config = CSSVariableConfig(
            primary_color="#000",
            font_family="x",
            font_size="16px",
            heading_styles=case.get("input"),
        )
        assert generate_heading_styles(config) == case["expected"], case["name"]


def test_golden_process_css():
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    for case in snapshot["process"]:
        assert process_css(case["input"]) == case["expected"], case["name"]


# ---- generate_css_variables 分支 ----


def test_default_blockquote_bg_not_declared():
    css = generate_css_variables(
        CSSVariableConfig(
            primary_color="#000",
            font_family="x",
            font_size="16px",
            blockquote_background="default",
        )
    )
    assert "--md-blockquote-background" not in css


def test_empty_blockquote_bg_not_declared():
    css = generate_css_variables(
        CSSVariableConfig(
            primary_color="#000",
            font_family="x",
            font_size="16px",
            blockquote_background="",
        )
    )
    assert "--md-blockquote-background" not in css


def test_custom_blockquote_bg_declared():
    css = generate_css_variables(
        CSSVariableConfig(
            primary_color="#000",
            font_family="x",
            font_size="16px",
            blockquote_background="#f5f5f5",
        )
    )
    assert "--md-blockquote-background: #f5f5f5;" in css


def test_indent_and_justify_lines():
    css = generate_css_variables(
        CSSVariableConfig(
            primary_color="#000",
            font_family="x",
            font_size="16px",
            is_use_indent=True,
            is_use_justify=True,
        )
    )
    assert "text-indent: 2em;" in css
    assert "text-align: justify;" in css


def test_default_line_height_block_spacing_link_color():
    css = generate_css_variables(
        CSSVariableConfig(primary_color="#000", font_family="x", font_size="16px")
    )
    assert "--md-line-height: 1.75;" in css
    assert "--md-block-spacing: 1;" in css
    assert "--md-link-color: #576b95;" in css


# ---- heading 样式 ----


def test_heading_three_presets():
    css = generate_heading_styles(
        CSSVariableConfig(
            primary_color="#000",
            font_family="x",
            font_size="16px",
            heading_styles={
                "h1": "color-only",
                "h2": "border-bottom",
                "h3": "border-left",
            },
        )
    )
    assert "#output h1" in css
    assert "padding-bottom: 0.3em;" in css
    assert "border-bottom: 2px solid var(--md-primary-color);" in css
    assert "padding-left: 10px;" in css
    assert "border-left: 4px solid var(--md-primary-color);" in css
    # 规则间空行分隔
    assert "\n\n" in css


def test_heading_empty_and_none():
    config = CSSVariableConfig(
        primary_color="#000", font_family="x", font_size="16px"
    )
    assert generate_heading_styles(config) == ""
    config.heading_styles = {}
    assert generate_heading_styles(config) == ""


def test_heading_unknown_style_ignored():
    css = generate_heading_styles(
        CSSVariableConfig(
            primary_color="#000",
            font_family="x",
            font_size="16px",
            heading_styles={"h9": "color-only", "h1": "mystery"},
        )
    )
    assert css == ""


# ---- process_css 补充用例（舍入/边界） ----


def test_process_css_round_four_decimals_half_up():
    # 0.33335 * 10000 = 3333.5 → JS Math.round 向 +∞ 半入 → 0.3334
    assert process_css("x{width:calc(1px * 0.33335)}") == "x{width:0.3334px}"


def test_process_css_negative_round():
    assert process_css("x{width:calc(-1px * 0.5)}") == "x{width:-0.5px}"


def test_process_css_integer_without_dot_zero():
    assert process_css("x{width:calc(1.5px * 2)}") == "x{width:3px}"


def test_process_css_division_replicates_upstream_nan():
    # 上游 cssProcessor.ts:65 解构跳槽导致除法恒为 NaN（契约差异已登记）
    assert process_css("x{width:calc(8px / 2)}") == "x{width:NaNpx}"
    assert process_css("x{width:calc(1px / 3)}") == "x{width:NaNpx}"


def test_process_css_iteration_cap():
    # 10 轮后仍有未解析嵌套则保留原样，不无限循环
    css = ":root{--a:var(--b)} x{color:var(--a)}"
    result = process_css(css)
    assert "var(" in result  # --b 未定义，声明与引用回退形态保留


def test_process_css_no_calc_without_match():
    assert process_css("x{color:red}") == "x{color:red}"


# ---- escape_style_content ----


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("</style>", "<\\/style>"),
        # JS 替换串为固定小写，匹配任意大小写后统一输出小写 style
        ("</STYLE>", "<\\/style>"),
        ("</Style ", "<\\/style "),
        ("a </style> b </style>", "a <\\/style> b <\\/style>"),
        ("normal css", "normal css"),
    ],
)
def test_escape_style_content(raw, expected):
    assert escape_style_content(raw) == expected
