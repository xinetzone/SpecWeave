"""TR-9 端到端文章渲染 golden 对拍。

期望 HTML 由 scripts/article_golden_regen.py 用上游真实 Node 模块
（initRenderer + isomorphic-dompurify + 真实 highlight.js/plaintext +
cssVariables/cssProcessor/config-options）生成并入库；普通 pytest 不依赖 Node。
"""

import json
from pathlib import Path

import pytest

from doocs_md_py.render.article import (
    RenderArticleInput,
    build_rendered_output,
)
from doocs_md_py.render.domcompare import assert_dom_equal

GOLDEN_DIR = Path(__file__).parent
CASES_JSON = GOLDEN_DIR / "article_cases.json"

CAMEL_TO_SNAKE = {
    "theme": "theme",
    "primaryColor": "primary_color",
    "fontFamily": "font_family",
    "fontSize": "font_size",
    "lineHeight": "line_height",
    "blockSpacing": "block_spacing",
    "linkColor": "link_color",
    "blockquoteBackground": "blockquote_background",
    "legend": "legend",
    "isMacCodeBlock": "is_mac_code_block",
    "isShowLineNumber": "is_show_line_number",
    "citeStatus": "cite_status",
    "countStatus": "count_status",
    "themeMode": "theme_mode",
    "isUseIndent": "is_use_indent",
    "isUseJustify": "is_use_justify",
    "headingStyles": "heading_styles",
    "codeBlockTheme": "code_block_theme",
    "customCSS": "custom_css",
}


def _load_spec() -> dict:
    return json.loads(CASES_JSON.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", _load_spec()["cases"], ids=lambda c: c["name"])
def test_article_matches_upstream(case):
    markdown = case.get("markdown")
    if markdown is None:
        markdown = (GOLDEN_DIR / case["file"]).read_text(encoding="utf-8")
    options = {
        CAMEL_TO_SNAKE[key]: value
        for key, value in case.get("options", {}).items()
    }
    spec = _load_spec()
    actual = build_rendered_output(
        RenderArticleInput(markdown=markdown, **options),
        code_css_fetcher=lambda url: spec["hljs_fixture"],
    ).html
    expected = (
        GOLDEN_DIR / f"article_expected_{case['name']}.html"
    ).read_text(encoding="utf-8")
    assert_dom_equal(expected, actual)
