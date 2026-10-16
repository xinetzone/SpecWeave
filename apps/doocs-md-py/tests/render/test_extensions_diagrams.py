"""图表围栏占位扩展对拍测试。

转录自 mermaid.ts / plantuml.ts / infographic.ts 的 SSR 占位分支：
- 服务端仅输出 data-md-diagram-state="loading" 占位，不产生 SVG/网络请求
- 容器 id / data-placeholder 由 simpleHash(code-theme[-v2]) 决定
- walkTokens 兜底：~~~ 围栏、四反引号、info 残余同样转图表
"""

import re

import pytest

from doocs_md_py.render import init_renderer
from doocs_md_py.render.extensions.diagrams import DEFAULT_MESSAGES
from doocs_md_py.render.html_utils import simple_hash
from doocs_md_py.render.options import DiagramMessages, IOpts


def render(md: str, opts=None) -> str:
    renderer = init_renderer(opts)
    return renderer.render_markdown_to_html(md)


MERMAID_FENCE = "```mermaid\ngraph TD;\n    A-->B\n```"
PLANTUML_FENCE = "```plantuml\n@startuml\nA->B\n@enduml\n```"
INFO_FENCE = '```infographic\n{"type": "chart"}\n```'


# ---- simpleHash 基准（与 Node djb2-int32-base36 对拍锁定）----
@pytest.mark.parametrize(
    "text,expected",
    [
        ("graph TD; A-->B-light", "w0enk7"),
        ("@startuml-light", "w1qwat"),
        ("x-dark-v2", "6tkwri"),
        ("", "0"),
    ],
)
def test_simple_hash_matches_node(text, expected):
    assert simple_hash(text) == expected


# ---- mermaid ----
def test_mermaid_placeholder_shape():
    html = render(MERMAID_FENCE)
    code = "graph TD;\n    A-->B"
    key = simple_hash(f"{code}-light")
    assert "<!--mermaid-start-->" in html
    assert "<!--mermaid-end-->" in html
    assert f'id="mermaid-{key}"' in html
    assert 'class="mermaid-diagram"' in html
    assert 'data-md-diagram-state="loading"' in html
    assert DEFAULT_MESSAGES["mermaid_loading"] in html
    # 不产出代码围栏
    assert "<pre" not in html


def test_mermaid_dark_mode_changes_cache_key():
    light = render(MERMAID_FENCE)
    dark = render(MERMAID_FENCE, IOpts(theme_mode="dark"))
    code = "graph TD;\n    A-->B"
    assert f'id="mermaid-{simple_hash(code + "-light")}"' in light
    assert f'id="mermaid-{simple_hash(code + "-dark")}"' in dark


def test_mermaid_code_is_trimmed():
    html = render("```mermaid\n\n  graph LR; X-->Y  \n```")
    key = simple_hash("graph LR; X-->Y-light")
    assert f'id="mermaid-{key}"' in html


def test_mermaid_does_not_swallow_following_paragraph():
    html = render(MERMAID_FENCE + "\n\n后续段落")
    assert "<!--mermaid-end-->" in html
    assert "后续段落" in html


def test_mermaid_tilde_fence_fallback():
    # ~~~ 围栏经内建 fence → walkTokens 等价兜底转图表
    html = render("~~~mermaid\ngraph TD; A-->B\n~~~")
    assert 'class="mermaid-diagram"' in html
    assert "<pre" not in html


def test_mermaid_four_backticks_with_info_extra():
    # 四反引号 + info 残余：扩展正则不匹配，内建 fence 按 lang 首词兜底
    html = render("````mermaid extra\ngraph TD; A-->B\n````")
    assert 'class="mermaid-diagram"' in html


def test_normal_code_fence_untouched():
    html = render("```python\nprint(1)\n```")
    assert "mermaid-diagram" not in html
    assert "<pre" in html


# ---- plantuml ----
def test_plantuml_placeholder_shape():
    html = render(PLANTUML_FENCE)
    code = "@startuml\nA->B\n@enduml"
    key = simple_hash(f"{code}-light")
    assert f'data-placeholder="plantuml-{key}"' in html
    assert 'class="plantuml-diagram"' in html
    assert 'style="text-align: center; margin: 16px 8px; overflow-x: auto"' in html
    assert 'data-md-diagram-state="loading"' in html
    assert 'color: #666; font-style: italic;' in html
    assert DEFAULT_MESSAGES["plantuml_loading"] in html
    # plantuml 无注释标记
    assert "plantuml-start" not in html
    # 不携带服务端 imageUrl（纯占位）
    assert "www.plantuml.com" not in html


def test_plantuml_dark_mode_key():
    html = render(PLANTUML_FENCE, IOpts(theme_mode="dark"))
    code = "@startuml\nA->B\n@enduml"
    assert f'data-placeholder="plantuml-{simple_hash(code + "-dark")}"' in html


# ---- infographic ----
def test_infographic_placeholder_shape():
    html = render(INFO_FENCE)
    code = '{"type": "chart"}'
    key = simple_hash(f"{code}-light-v2")
    assert "<!--infographic-start-->" in html
    assert f'id="infographic-{key}"' in html
    assert 'class="infographic-diagram"' in html
    assert 'style="width: 100%;"' in html
    assert 'data-md-diagram-state="loading"' in html
    assert DEFAULT_MESSAGES["infographic_loading"] in html


def test_infographic_dark_key_v2_suffix():
    html = render(INFO_FENCE, IOpts(theme_mode="dark"))
    code = '{"type": "chart"}'
    assert f'id="infographic-{simple_hash(code + "-dark-v2")}"' in html


# ---- 文案注入 ----
def test_custom_diagram_messages():
    messages = DiagramMessages(
        mermaid_loading="Mermaid 加载中",
        plantuml_loading="PlantUML 加载中",
        infographic_loading="信息图加载中",
    )
    opts = IOpts(diagram_messages=messages)
    assert "Mermaid 加载中" in render(MERMAID_FENCE, opts)
    assert "PlantUML 加载中" in render(PLANTUML_FENCE, opts)
    assert "信息图加载中" in render(INFO_FENCE, opts)


def test_empty_messages_object_falls_back_to_defaults():
    # 空串字段回退英文默认（与 resolveDiagramMessages 后的或兜底一致）
    opts = IOpts(diagram_messages=DiagramMessages())
    html = render(MERMAID_FENCE, opts)
    assert DEFAULT_MESSAGES["mermaid_loading"] in html


# ---- 独立场景 ----
def test_unknown_lang_fence_still_code():
    html = render("```yaml\na: 1\n```")
    assert re.search(r'class="language-yaml', html)


def test_independent_renders_no_state_leak():
    renderer = init_renderer()
    first = renderer.render_markdown_to_html(MERMAID_FENCE)
    second = renderer.render_markdown_to_html(PLANTUML_FENCE)
    assert "mermaid-diagram" in first
    assert "plantuml-diagram" in second
    assert "mermaid-diagram" not in second


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
