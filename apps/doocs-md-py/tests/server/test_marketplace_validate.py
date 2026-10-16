"""TR-15.1 市场校验拒绝条件全集（upstream: marketplace-validate.test.ts 超集）。

覆盖：发布主题/组件 ≥25 条拒绝分支、版本十进制进位与非法段兜底、
update 归一化与 empty_update、reject reason 截断。
"""

import json

import pytest

from doocs_md_py.server.config import Config
from doocs_md_py.server.marketplace_admin import get_admin_logins, is_admin
from doocs_md_py.server.marketplace_validate import (
    MAX_COMPONENT_JSON_BYTES,
    MAX_REJECT_REASON_LENGTH,
    MAX_SAMPLE_MARKDOWN_BYTES,
    MAX_THEME_CSS_BYTES,
    _UNSET,
    bump_marketplace_version,
    compare_marketplace_versions,
    parse_reject_reason,
    parse_sample_markdown,
    validate_component_payload,
    validate_publish_component,
    validate_publish_theme,
    validate_theme_css,
    validate_update,
)


def theme_body(**over):
    body = {"slug": "my-theme", "name": "My Theme", "css": "h1 { color: red; }"}
    body.update(over)
    return body


def component_body(**over):
    body = {
        "slug": "tip-block",
        "name": "Tip",
        "component": {
            "name": "TipBlock",
            "template": "<section>{{text}}</section>",
            "props": [{"name": "text", "type": "string"}],
        },
    }
    body.update(over)
    return body


# ---- 主题发布拒绝分支（16）----


def test_theme_rejects_non_object_body():
    assert validate_publish_theme(None).error == "invalid_body"
    assert validate_publish_theme("x").error == "invalid_body"
    assert validate_publish_theme([]).error == "invalid_body"


def test_theme_slug_rules():
    assert validate_publish_theme(theme_body(slug="My Theme")).error == "invalid_slug"
    assert validate_publish_theme(theme_body(slug="-abc")).error == "invalid_slug"
    assert validate_publish_theme(theme_body(slug="abc-")).error == "invalid_slug"
    assert validate_publish_theme(theme_body(slug="a" * 49)).error == "invalid_slug"
    assert validate_publish_theme(theme_body(slug="")).error == "invalid_slug"
    assert validate_publish_theme(theme_body(slug=123)).error == "invalid_slug"


def test_theme_name_rules():
    assert validate_publish_theme(theme_body(name="")).error == "invalid_name"
    assert validate_publish_theme(theme_body(name="   ")).error == "invalid_name"
    assert validate_publish_theme(theme_body(name="x" * 65)).error == "invalid_name"
    assert validate_publish_theme(theme_body(name=12)).error == "invalid_name"


def test_theme_cover_url_rules():
    assert validate_publish_theme(
        theme_body(coverUrl="ftp://x.com/a")
    ).error == "invalid_cover_url"
    assert validate_publish_theme(
        theme_body(coverUrl="not-a-url")
    ).error == "invalid_cover_url"
    assert validate_publish_theme(
        theme_body(coverUrl="//x.com/a.png")
    ).error == "invalid_cover_url"
    assert validate_publish_theme(
        theme_body(coverUrl="javascript:alert(1)")
    ).error == "invalid_cover_url"
    ok = validate_publish_theme(theme_body(coverUrl="http://localhost:8800/a.png"))
    assert ok.ok and ok.value["coverUrl"] == "http://localhost:8800/a.png"
    nullish = validate_publish_theme(theme_body(coverUrl=None))
    assert nullish.ok and nullish.value["coverUrl"] is None


def test_theme_primary_color_rules():
    for bad in ("red", "#abcd", "abc", "#gggggg", 123):
        assert validate_publish_theme(
            theme_body(primaryColor=bad)
        ).error == "invalid_primary_color", bad
    for good in ("#abc", "#aabbcc", "#AABBCCFF"):
        ok = validate_publish_theme(theme_body(primaryColor=good))
        assert ok.ok and ok.value["primaryColor"] == good


def test_theme_sample_markdown_rules():
    assert validate_publish_theme(
        theme_body(sampleMarkdown=123)
    ).error == "invalid_sample_markdown"
    big = "x" * (MAX_SAMPLE_MARKDOWN_BYTES + 1)
    assert validate_publish_theme(
        theme_body(sampleMarkdown=big)
    ).error == "payload_too_large"
    whitespace = validate_publish_theme(theme_body(sampleMarkdown="   "))
    assert whitespace.ok and whitespace.value["sampleMarkdown"] is None
    omitted = validate_publish_theme(theme_body())
    assert omitted.ok and omitted.value["sampleMarkdown"] is None
    custom = validate_publish_theme(theme_body(sampleMarkdown="# Hi"))
    assert custom.ok and custom.value["sampleMarkdown"] == "# Hi"


def test_theme_css_rules():
    assert validate_publish_theme(theme_body(css="")).error == "invalid_css"
    assert validate_publish_theme(theme_body(css="   ")).error == "invalid_css"
    assert validate_publish_theme(theme_body(css=123)).error == "invalid_css"
    assert validate_publish_theme(
        theme_body(css='@import url("x.css");')
    ).error == "css_import_forbidden"
    assert validate_publish_theme(
        theme_body(css="body { background: url(https://evil.test/x.png); }")
    ).error == "css_external_url_forbidden"
    boundary = "a" * MAX_THEME_CSS_BYTES
    assert validate_theme_css(boundary).ok
    assert validate_theme_css(boundary + "a").error == "payload_too_large"


def test_theme_success_shape():
    ok = validate_publish_theme(
        theme_body(primaryColor="#0F4C81", version="9.9.9", description="  Desc  ")
    )
    assert ok.ok
    value = ok.value
    assert value["type"] == "theme"
    assert value["version"] == "1.0.0"  # 客户端版本被忽略，服务端写死
    assert value["description"] == "Desc"
    assert value["primaryColor"] == "#0F4C81"
    assert value["payload"] == "h1 { color: red; }"
    # description 截断 2000
    long_desc = validate_publish_theme(theme_body(description="d" * 2001))
    assert long_desc.ok and len(long_desc.value["description"]) == 2000


# ---- 组件发布拒绝分支（10）----


def test_component_object_rules():
    assert validate_publish_component(component_body(component=None)).error == "invalid_component"
    assert validate_publish_component(component_body(component="x")).error == "invalid_component"


def test_component_name_and_template_rules():
    bad_name = component_body(component={"name": "bad-name", "template": "<div>x</div>", "props": []})
    assert validate_publish_component(bad_name).error == "invalid_component_name"
    no_template = component_body(component={"name": "TipBlock", "template": "   ", "props": []})
    assert validate_publish_component(no_template).error == "invalid_component_template"
    for template, expected in (
        ("<script>alert(1)</script>", "unsafe_component_template"),
        ("<div onclick='x()'>y</div>", "unsafe_component_template"),
        ('<a href="javascript:alert(1)">x</a>', "unsafe_component_template"),
    ):
        body = component_body(component={"name": "TipBlock", "template": template, "props": []})
        assert validate_publish_component(body).error == expected


def test_component_props_rules():
    bad_props = component_body(component={"name": "TipBlock", "template": "<div/>", "props": {}})
    assert validate_publish_component(bad_props).error == "invalid_component_props"
    bad_type = component_body(
        component={"name": "TipBlock", "template": "<div/>", "props": [{"name": "x", "type": "object"}]}
    )
    assert validate_publish_component(bad_type).error == "invalid_component_props"
    no_name = component_body(
        component={"name": "TipBlock", "template": "<div/>", "props": [{"type": "string"}]}
    )
    assert validate_publish_component(no_name).error == "invalid_component_props"
    non_object = component_body(
        component={"name": "TipBlock", "template": "<div/>", "props": ["x"]}
    )
    assert validate_publish_component(non_object).error == "invalid_component_props"
    # type 缺省合法
    default_type = component_body(
        component={"name": "TipBlock", "template": "<div/>", "props": [{"name": "x"}]}
    )
    assert validate_publish_component(default_type).ok


def test_component_payload_shape_and_size():
    ok = validate_publish_component(
        component_body(
            component={
                "name": "TipBlock",
                "description": "  d  ",
                "template": "<div>{{x}}</div>",
                "props": [],
                "example": "usage",
            }
        )
    )
    assert ok.ok
    payload = json.loads(ok.value["payload"])
    assert list(payload) == ["name", "description", "template", "props", "example"]
    assert payload["description"] == "d"

    omitted = validate_component_payload(
        {"name": "TipBlock", "template": "<div/>", "props": []}
    )
    assert omitted.ok
    assert list(json.loads(omitted.value)) == ["name", "description", "template", "props"]

    # description 先截 2000，需靠不截断的 template 撑大 payload
    huge = validate_component_payload(
        {
            "name": "TipBlock",
            "template": "x" * (MAX_COMPONENT_JSON_BYTES + 10),
            "props": [],
        }
    )
    assert huge.error == "payload_too_large"


# ---- update 归一化（含 empty_update）----


def test_update_rejects_empty():
    assert validate_update("theme", None).error == "invalid_body"
    assert validate_update("theme", {}).error == "empty_update"
    # 仅客户端版本号：无 currentVersion 与有 currentVersion 均 empty_update
    assert validate_update("theme", {"version": "9.9.9"}).error == "empty_update"
    assert (
        validate_update("theme", {"version": "9.9.9"}, current_version="1.0.0").error
        == "empty_update"
    )


def test_update_theme_fields():
    ok = validate_update("theme", {"css": "p { color: red; }"}, current_version="1.0.0")
    assert ok.ok
    assert ok.value["payload"] == "p { color: red; }"
    assert ok.value["version"] == "1.0.1"  # 客户端版本被忽略

    assert validate_update("theme", {"name": ""}).error == "invalid_name"
    assert validate_update("theme", {"description": 1}).error == "invalid_description"
    assert validate_update("theme", {"css": ""}).error == "invalid_css"
    assert validate_update("theme", {"coverUrl": "bad"}).error == "invalid_cover_url"
    assert validate_update(
        "theme", {"primaryColor": "nope"}
    ).error == "invalid_primary_color"
    assert validate_update(
        "theme", {"sampleMarkdown": 1}
    ).error == "invalid_sample_markdown"
    assert validate_update(
        "theme", {"css": "@import 'x';"}
    ).error == "css_import_forbidden"

    # 显式清空封面/主色/样例
    cleared = validate_update(
        "theme", {"coverUrl": None, "primaryColor": None, "sampleMarkdown": None},
        current_version="2.0.0",
    )
    assert cleared.ok
    assert cleared.value["coverUrl"] is None
    assert cleared.value["primaryColor"] is None
    assert cleared.value["sampleMarkdown"] is None
    assert cleared.value["version"] == "2.0.1"


def test_update_component_payload():
    ok = validate_update(
        "component",
        {"component": {"name": "NewBlock", "template": "<p>hi</p>", "props": []}},
        current_version="1.5.9",
    )
    assert ok.ok and ok.value["version"] == "1.6.0"
    bad = validate_update(
        "component",
        {"component": {"name": "TipBlock", "template": "<iframe src='x'></iframe>", "props": []}},
    )
    assert bad.error == "unsafe_component_template"
    assert validate_update("component", {"component": None}).error == "invalid_component"


# ---- 版本号十进制进位 ----


@pytest.mark.parametrize(
    "current,expected",
    [
        (None, "1.0.0"),
        ("", "1.0.0"),
        ("   ", "1.0.0"),
        ("1.0.0", "1.0.1"),
        ("1.0.9", "1.1.0"),
        ("1.9.9", "2.0.0"),
        ("v1.2.3", "1.2.4"),
        ("V2.0.0", "2.0.1"),
        ("1.2.9", "1.3.0"),
        ("9", "9.0.1"),
        ("x", "1.0.1"),
        ("1.0.-1", "1.0.1"),
        ("2.x.9", "2.1.0"),
    ],
)
def test_bump_version_carry(current, expected):
    assert bump_marketplace_version(current) == expected


def test_compare_versions():
    assert compare_marketplace_versions("1.1.0", "1.0.9") > 0
    assert compare_marketplace_versions("1.0.0", "1.0.0") == 0
    assert compare_marketplace_versions("1.0.0", "2.0.0") < 0


# ---- reject reason 与 sample markdown 三态 ----


def test_parse_reject_reason():
    assert parse_reject_reason(_UNSET) is None
    assert parse_reject_reason(None) is None
    assert parse_reject_reason("") is None
    assert parse_reject_reason(123) is None
    assert parse_reject_reason("  ok  ") == "ok"
    long_reason = parse_reject_reason("r" * (MAX_REJECT_REASON_LENGTH + 1))
    assert long_reason is not None and len(long_reason) == MAX_REJECT_REASON_LENGTH
    assert parse_reject_reason("   ") is None


def test_parse_sample_markdown_tri_state():
    assert parse_sample_markdown(_UNSET).value is _UNSET
    assert parse_sample_markdown(None).value is None
    assert parse_sample_markdown("   ").value is None
    assert parse_sample_markdown(" a ").value == "a"


# ---- 管理员白名单（upstream: marketplace-admin.ts）----


def test_admin_logins_normalized_and_blanks_dropped():
    cfg = Config(admin_github_logins=(" OctoCat ", "", "   ", "HUBber"))
    assert get_admin_logins(cfg) == {"octocat", "hubber"}


def test_admin_logins_empty_when_unconfigured():
    assert get_admin_logins(Config()) == set()


def test_is_admin_normalizes_login_and_rejects_falsy():
    cfg = Config(admin_github_logins=("octocat",))
    assert is_admin(cfg, "OCTOCAT") is True
    assert is_admin(cfg, " someone ") is False
    # 空 / None 一律非管理员；未配置白名单时任何登录名均非管理员
    assert is_admin(cfg, None) is False
    assert is_admin(cfg, "") is False
    assert is_admin(Config(), "octocat") is False
