"""自定义组件扩展测试（与上游 marked 18.1.0 + component.ts 对拍锁定）。

对拍脚本（含 27 例逐字比对）位于 .temp-node-comp/，属临时验证资产；
本文件固化关键行为与解析守卫。
"""

import pytest

from doocs_md_py.render import IOpts, RenderMessages, init_renderer
from doocs_md_py.render.extensions.component import (
    ComponentDef,
    PropDef,
    get_built_in_registry,
    parse_props,
    parse_tag,
    preview_component,
)


def render(md: str, opts=None) -> str:
    return init_renderer(opts).render_markdown_to_html(md)


# ---- 注册表数据 ----
def test_builtin_registry_contains_eight_components():
    reg = get_built_in_registry()
    assert set(reg) == {
        "MpProfile", "QRCodeBlock", "AuthorBlock", "TipBlock",
        "TableBlock", "InfoGrid", "BadgeGroup", "Emoji",
    }
    assert reg["Emoji"].inline is True
    assert all(not c.inline for n, c in reg.items() if n != "Emoji")


# ---- MpProfile ----
def test_mpprofile_template_substitution():
    out = render(
        '<MpProfile mpId="abc==" nickname="Doocs" headimg="https://x/l.png" '
        'signature="GitHub" serviceType="2" verifyStatus="1" />\n'
    )
    assert '<mp-common-profile' in out
    assert 'data-id="abc=="' in out
    assert 'data-nickname="Doocs"' in out
    assert 'data-service_type="2"' in out


def test_mpprofile_defaults():
    out = render('<MpProfile mpId="x" nickname="y" />\n')
    assert 'data-service_type="1"' in out
    assert 'data-verify_status="0"' in out


# ---- QRCodeBlock ----
def test_qr_defaults_and_raw_placeholder():
    out = render('<QRCodeBlock url="https://md.doocs.org" />\n')
    assert "size=150x150&data=https://md.doocs.org" in out
    assert "width: 150px" in out
    assert ">扫码访问</p>" in out


def test_qr_gt_inside_quoted_attr():
    out = render('<QRCodeBlock url="a>b" size="96" />\n')
    assert "size=96x96&data=a&gt;b" in out  # 模板变量统一 escapeHtml


# ---- AuthorBlock ----
def test_author_block_escapes_values():
    out = render('<AuthorBlock name="A &amp; B <x>" avatar="a.png" />\n')
    assert "A &amp; B &lt;x&gt;" in out
    assert 'src="a.png"' in out


# ---- TipBlock ----
def test_tip_with_title_and_danger_palette():
    out = render('<TipBlock type="danger" title="危险" content="不可为" />\n')
    assert "border-left: 4px solid #ff4d4f" in out
    assert "background: #fff2f0" in out
    assert "#a8071a" in out
    assert ">危险</p>" in out
    assert ">不可为</p>" in out


def test_tip_without_title_emits_no_title_paragraph():
    out = render('<TipBlock content="仅内容" />\n')
    assert "#1890ff" in out  # 默认 info
    assert out.count("<p ") == 1


def test_tip_unknown_type_falls_back_info():
    out = render('<TipBlock type="weird" content="x" />\n')
    assert "border-left: 4px solid #1890ff" in out


# ---- TableBlock ----
def test_table_block_structure_and_zebra():
    out = render(
        "<TableBlock headers='[\"名称\",\"版本\"]' "
        "rows='[[\"Vue\",\"3.x\"],[\"Vite\",\"8.x\"]]' caption=\"清单\" />\n"
    )
    assert "<caption" in out and ">清单</caption>" in out
    assert out.count("<th ") == 2
    assert out.count("<td ") == 4
    assert 'style="background: var(--md-comp-bg-stripe, #fafafa);"' in out  # 第二行斑马纹


def test_table_block_striped_false():
    out = render(
        "<TableBlock headers='[\"a\"]' rows='[[\"1\"],[\"2\"]]' striped=\"false\" />"
    )
    assert "bgStripe" not in out and "background" not in out.split("<tbody>")[1]


def test_table_block_bad_json_and_scalar_cells():
    out = render("<TableBlock headers='broken' rows='nope' />\n")
    assert "<thead>" not in out
    assert "<tbody>" in out
    out2 = render(
        "<TableBlock headers='[1,true,null]' rows='[[\"x\",2,false,null]]' />"
    )
    assert ">1</th>" in out2
    assert ">true</th>" in out2
    assert ">null</th>" in out2
    assert ">false</td>" in out2


def test_table_block_escapes_cells():
    out = render("<TableBlock headers='[\"a\"]' rows='[[\"<script>x</script>\"]]' />")
    assert "<script>" not in out
    assert "&lt;script&gt;" in out


# ---- InfoGrid ----
def test_info_grid_two_cols_borders():
    out = render(
        "<InfoGrid items='[{\"label\":\"作者\",\"value\":\"me\"},{\"label\":\"版本\",\"value\":\"v1\"}]' />"
    )
    assert "width: 50%" in out
    assert ">作者</p>" in out and ">me</p>" in out


def test_info_grid_cols_clamped_three():
    out = render(
        "<InfoGrid items='[{\"label\":\"a\",\"value\":\"1\"}]' cols=\"9\" />"
    )
    assert "width: 33%" in out  # floor(100/3)


def test_info_grid_bad_cols_and_items():
    out_empty = render("<InfoGrid items='[]' cols=\"abc\" />")
    assert "table-cell" not in out_empty
    out = render(
        "<InfoGrid items='[{\"label\":\"a\",\"value\":\"1\"}]' cols=\"abc\" />"
    )
    assert "width: 50%" in out  # 回退 2


# ---- BadgeGroup ----
def test_badge_group_each_loop_and_default_color():
    out = render("""<BadgeGroup tags='["Vue 3","TypeScript"]' />""")
    assert out.count("<span ") == 2
    assert "background: #07c1601a" in out
    assert "border: 1px solid #07c16040" in out
    assert ">Vue 3</span>" in out and ">TypeScript</span>" in out


def test_badge_group_non_array_tags_renders_empty_body():
    out = render("<BadgeGroup tags='notarray' />")
    assert "<span " not in out


# ---- 未知名 ----
def test_unknown_component_default_message():
    out = render('<NoSuchComp x="1" />\n')
    assert out == '<p style="color:#f00;font-size:12px;">[Unknown component: NoSuchComp]</p>\n'


def test_unknown_component_custom_template():
    opts = IOpts(render_messages=RenderMessages(unknown_component="不明组件 {name}？"))
    out = render('<Foo />', opts)
    assert "[不明组件 Foo？]" in out


# ---- 解析守卫 ----
def test_lowercase_tag_is_not_component():
    out = render('<qrcodeblock url="x" />\n')
    assert "<section" not in out


def test_trailing_junk_rejects_self_closing():
    out = render('<QRCodeBlock url="x" /> trailing junk\n')
    assert "api.qrserver.com" not in out


def test_same_line_paired_unknown_still_recognized():
    out = render("<NoSuch>child</NoSuch>\n")
    assert "[Unknown component: NoSuch]" in out


def test_multiline_paired_unknown_recognized():
    out = render("<NoSuch a=\"1\">\ninner text\n</NoSuch>\n")
    assert "[Unknown component: NoSuch]" in out
    assert "inner text" not in out  # 未知名不渲染 children


def test_single_quote_props_and_entity_unescape():
    assert parse_props("name='a &amp; b' x=\"y&lt;z\"") == {
        "name": "a & b",
        "x": "y<z",
    }


def test_parse_tag_helpers():
    tag = parse_tag('<X a="1" />')
    assert tag is not None and tag.name == "X" and tag.props_str == 'a="1"'
    assert parse_tag("<x />") is None
    # 自闭合后行尾有残余 → 拒绝
    assert parse_tag('<X a="1" />junk\n') is None


# ---- 段落中断 ----
def test_component_interrupts_paragraph():
    out = render("前缀文字\n<QRCodeBlock url=\"x\" />\n")
    assert ">前缀文字</p>" in out
    assert "<section" in out


def test_component_inside_fence_is_literal():
    out = render("```\n<QRCodeBlock url=\"x\" />\n```\n")
    assert "api.qrserver.com" not in out
    assert "&lt;QRCodeBlock" in out


# ---- 自定义注册表 ----
def test_custom_registry_template_engine():
    defn = ComponentDef(
        name="Card",
        template=(
            '<div class="card" data-k="{{k}}">{{#if k}}K={{k}}{{/if}}'
            "{{#unless k}}no-k{{/unless}}"
            '{{#each rows}}<i>{{@index}}:{{item}}</i>{{/each}}'
            "<span>{{children}}</span></div>"
        ),
        props=(PropDef(name="k"), PropDef(name="rows")),
    )
    opts = IOpts(components={"Card": defn})
    out = render("<Card k=\"v\" rows='[\"a\",\"b\"]'>raw<b>x</b></Card>", opts)
    assert 'data-k="v"' in out
    assert "K=v" in out and "no-k" not in out
    assert "<i>0:a</i><i>1:b</i>" in out
    assert "<span>raw<b>x</b></span>" in out  # children 原样不转义


def test_preview_component_applies_defaults():
    defn = get_built_in_registry()["QRCodeBlock"]
    html = preview_component(defn, {"url": "u"})
    assert "size=150x150&data=u" in html


def test_unknown_registry_replaces_builtins():
    # 上游语义：opts.components 非空时整体替换内置表
    defn = ComponentDef(name="Only", template="<b>only</b>")
    opts = IOpts(components={"Only": defn})
    out = render("<Only />", opts)
    assert "<b>only</b>" in out
    out2 = render('<QRCodeBlock url="x" />', opts)
    assert "[Unknown component: QRCodeBlock]" in out2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
