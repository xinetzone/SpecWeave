r"""显式脚注扩展对拍测试。

转录自 packages/core/src/extensions/footnotes.ts 的模板契约：
- 引用：<sup>…<a id="fnRef-id" href="#fnDef-id">\[N\]</a></sup>
- 定义：首条开 <p style="font-size:80%;…">，末条闭 </p>，编号按定义首次出现顺序
- 未定义引用保持原文字面
"""

import pytest

from doocs_md_py.render import init_renderer
from doocs_md_py.render.extensions.footnotes import _FN_INNER, _FN_FIRST, _FN_REF


def render(md: str) -> str:
    return init_renderer().render_markdown_to_html(md)


# ---- 引用渲染 ----
def test_defined_reference_renders_sup_anchor():
    html = render("段落[^1]。\n\n[^1]: 第一条")
    expected = _FN_REF.format(fn_id="1", index=1)
    assert expected in html
    assert 'id="fnRef-1"' in html
    assert 'href="#fnDef-1"' in html
    # upstream: footnotes.ts 模板字符串 \[1\] 求值为字面 [1]
    assert ">[1]<" in html


def test_undefined_reference_stays_literal():
    html = render("段落[^x]。")
    assert "[^x]" in html
    assert "fnRef-x" not in html


def test_multiple_references_share_number():
    html = render("a[^1] b[^1]\n\n[^1]: note")
    assert html.count('id="fnRef-1"') == 2
    assert html.count(">[1]<") == 2


# ---- 定义渲染 ----
def test_single_definition_opens_and_closes_paragraph():
    html = render("正文[^1]。\n\n[^1]: 唯一注释")
    assert _FN_FIRST in html
    # 唯一一条既是首条也是末条
    assert "</p>" in html
    assert "<code>1.</code>" in html
    assert '<span> 唯一注释</span>' in html
    assert 'id="fnDef-1"' in html
    assert 'href="#fnRef-1"' in html
    assert "↩︎" in html


def test_two_definitions_first_and_last_wrappers():
    html = render("a[^1][^2]\n\n[^1]: 注释甲\n[^2]: 注释乙")
    assert _FN_FIRST in html
    # 中间不应出现多余的 <p 开标签；末条后恰好收尾
    assert html.count('style="font-size: 80%;margin: 0.5em 8px;word-break:break-all;"') == 1
    assert "<code>1.</code>" in html
    assert "<code>2.</code>" in html
    assert '<span> 注释甲</span>' in html
    assert '<span> 注释乙</span>' in html
    # 末条闭合
    assert "<br></p>" in html


def test_definition_numbering_by_definition_encounter_order():
    # 上游编号在定义词法化时按 fnMap.size+1 分配（定义序，非引用序）
    html = render("x[^b] y[^a]\n\n[^a]: A\n[^b]: B")
    assert _FN_REF.format(fn_id="a", index=1) in html
    assert _FN_REF.format(fn_id="b", index=2) in html


def test_duplicate_definition_id_reuses_number():
    # 上游：fnMap.set 覆盖，编号复用，总数不增
    html = render("[^1]\n\n[^1]: 第一次\n[^1]: 第二次")
    assert html.count("<code>1.</code>") == 2
    assert html.count("<code>2.</code>") == 0


# ---- 守卫与边界 ----
def test_reference_inside_inline_code_is_literal():
    html = render("`[^1]`\n\n[^1]: note")
    # 行内 code 中的文本不产出 sup（code 段内无 fnRef）
    code_part = html.split("<code")[0]
    assert "fnRef-1" not in code_part


def test_definition_with_empty_id_matches_upstream():
    # 上游 .*? 允许空 id：[^] 与 [^]: 文本 以空 id 配对
    html = render("[^]\n\n[^]: 空标识")
    assert 'id="fnRef-"' in html
    assert 'id="fnDef-"' in html
    assert "<span> 空标识</span>" in html


def test_definition_text_is_raw_no_escape():
    # 上游原样插入（净化是 T8 的职责）
    html = render("[^1]\n\n[^1]: <b>bold</b> & amp")
    assert "<b>bold</b>" in html
    assert "& amp" in html


def test_fn_inner_template_exact_shape():
    inner = _FN_INNER.format(index=7, text=" txt", fn_id="id2")
    assert inner == (
        "\n                <code>7.</code> "
        "\n                <span> txt</span> "
        '\n                    <a id="fnDef-id2" href="#fnRef-id2" '
        'style="color: var(--md-primary-color);">↩︎</a>'
        "\n                <br>"
    )


def test_renders_independent_across_documents():
    renderer = init_renderer()
    first = renderer.render_markdown_to_html("[^1]\n\n[^1]: 甲")
    second = renderer.render_markdown_to_html("[^1]\n\n[^1]: 乙")
    # 两次渲染编号都从 1 开始（env 不串台）
    assert first.count("<code>1.</code>") == 1
    assert second.count("<code>1.</code>") == 1
    assert "甲" in first and "乙" in second


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
