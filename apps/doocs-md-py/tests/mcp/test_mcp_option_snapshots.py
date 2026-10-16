"""T18 / TR-18.2：与上游 TS 源树的离线黄金快照对拍。

快照 ``tests/golden/mcp_options_snapshot.json`` 由 ``scripts/mcp_options_snapshot_regen.py``
机械提取上游 ``packages/mcp-server/src`` 与 ``packages/shared/src`` 的字面值生成，
不导入本包，因此它是独立的上游期望值；本模块只做只读比对（离线、无网络）。

比对维度：工具注册序/描述、``render_markdown`` schema、15 组字面值表、12 个清单工具
的完整 JSON 文本（经 ``json_dumps`` 锁定键序）。
"""

import json
from pathlib import Path

import pytest

from doocs_md_py.mcp_server import RENDER_MARKDOWN_INPUT_SCHEMA, TOOLS, call_tool
from doocs_md_py.mcp_server import options as mcp_options
from doocs_md_py.mcp_server.stdio import json_dumps
from doocs_md_py.render import code_themes

GOLDEN_PATH = Path(__file__).resolve().parents[1] / "golden" / "mcp_options_snapshot.json"

# 快照 raw 段 → 本仓常量（全部为 tuple[dict, ...]，元素键为 value/label/desc）
OPTION_TABLES = (
    ("color_options", "COLOR_OPTIONS"),
    ("theme_options", "THEME_OPTIONS"),
    ("font_family_options", "FONT_FAMILY_OPTIONS"),
    ("font_size_options", "FONT_SIZE_OPTIONS"),
    ("line_height_options", "LINE_HEIGHT_OPTIONS"),
    ("block_spacing_options", "BLOCK_SPACING_OPTIONS"),
    ("link_color_options", "LINK_COLOR_OPTIONS"),
    ("blockquote_background_options", "BLOCKQUOTE_BACKGROUND_OPTIONS"),
    ("legend_options", "LEGEND_OPTIONS"),
    ("heading_style_options", "HEADING_STYLE_OPTIONS"),
)


@pytest.fixture(scope="module")
def golden():
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def _as_json(value):
    """归一化嵌套 tuple → list（本仓常量用 tuple 保不可变，快照为 JSON 数组）。"""
    return json.loads(json_dumps(value))


def test_snapshot_records_upstream_provenance(golden):
    assert golden["generated_by"] == "scripts/mcp_options_snapshot_regen.py"
    assert set(golden["sources"]) == {
        "packages/mcp-server/src/config-options.ts",
        "packages/mcp-server/src/index.ts",
        "packages/shared/src/configs/ai-service-options.ts",
        "packages/shared/src/constants/ai-config.ts",
    }
    for digest in golden["sources"].values():
        assert digest.startswith("sha256:") and len(digest) == len("sha256:") + 64


def test_tool_order_matches_upstream_registration(golden):
    assert golden["tool_order"] == [tool.name for tool in TOOLS]
    assert len(golden["tool_order"]) == 13


def test_tool_descriptions_match_upstream(golden):
    assert golden["tool_descriptions"] == {tool.name: tool.description for tool in TOOLS}


def test_input_schema_matches_upstream_zod(golden):
    schema = RENDER_MARKDOWN_INPUT_SCHEMA
    upstream = golden["schema"]
    assert upstream["fields"] == list(schema["properties"])
    assert upstream["required"] == schema["required"]
    assert {
        name: prop["default"] for name, prop in schema["properties"].items() if "default" in prop
    } == upstream["defaults"]
    assert {
        name: prop["pattern"] for name, prop in schema["properties"].items() if "pattern" in prop
    } == upstream["patterns"]
    assert {
        name: prop["enum"] for name, prop in schema["properties"].items() if "enum" in prop
    } == upstream["enums"]


@pytest.mark.parametrize(
    ("raw_key", "constant_name"),
    OPTION_TABLES,
    ids=[key for key, _ in OPTION_TABLES],
)
def test_option_tables_match_upstream(golden, raw_key, constant_name):
    constant = getattr(mcp_options, constant_name)
    assert _as_json(constant) == golden["raw"][raw_key]


def test_code_block_theme_table_and_prefix_match_upstream(golden):
    assert _as_json(code_themes.CODE_BLOCK_THEME_OPTIONS) == golden["raw"]["code_block_theme_options"]
    assert code_themes.CODE_BLOCK_URL_PREFIX == golden["raw"]["code_block_url_prefix"]


def test_scalar_facts_match_upstream(golden):
    assert mcp_options.DEFAULT_SERVICE_ENDPOINT == golden["raw"]["default_service_endpoint"]
    assert list(mcp_options.HEADING_LEVELS) == golden["raw"]["heading_levels"]


def test_service_extension_and_renderer_tables_match_upstream(golden):
    assert _as_json(mcp_options.AI_SERVICE_OPTIONS) == golden["raw"]["service_options"]
    assert _as_json(mcp_options.EXTENSION_DOCS) == golden["raw"]["extensions"]
    assert _as_json(mcp_options.RENDERER_OPTION_DOCS) == golden["raw"]["renderer_options"]


def test_table_sizes_are_locked(golden):
    sizes = {
        "color_options": 11,
        "theme_options": 3,
        "font_family_options": 3,
        "font_size_options": 5,
        "line_height_options": 5,
        "block_spacing_options": 5,
        "link_color_options": 3,
        "blockquote_background_options": 3,
        "legend_options": 6,
        "heading_style_options": 5,
        "code_block_theme_options": 10,
        "service_options": 21,
        "extensions": 11,
        "renderer_options": 19,
    }
    for key, expected in sizes.items():
        assert len(golden["raw"][key]) == expected, key
    assert len(golden["schema"]["fields"]) == 20


def test_list_tool_payloads_match_upstream_byte_for_byte(golden):
    """清单工具的 payload 必须与上游逐字节一致（json_dumps 锁定键序与转义）。"""
    expected = golden["tools"]
    assert set(expected) == {tool.name for tool in TOOLS} - {"render_markdown"}
    for name, payload in expected.items():
        assert json_dumps(call_tool(name)) == json_dumps(payload), name
