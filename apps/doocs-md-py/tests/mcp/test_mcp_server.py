"""T18 / TR-18.1：MCP stdio Server 契约测试。

对拍对象：上游 ``packages/mcp-server/src/index.ts``（13 工具注册序、``render_markdown``
的 20 个 zod 入参、zod 自定义报错文案）与 MCP 规范的 JSON-RPC 2.0 信封。

说明：上游用官方 TS SDK（``McpServer`` + ``StdioServerTransport``）；本仓按 spec A6
回退条款手写传输层，故 ``initialize`` 的 result 形状、入参校验错误文案的承载方式属
既定契约差异（T21 登记），断言针对本仓实现而非 SDK 内部格式。
"""

import dataclasses
import io
import json
import sys
from types import SimpleNamespace

import pytest

from doocs_md_py import cli
from doocs_md_py.mcp_server import (
    RENDER_MARKDOWN_INPUT_SCHEMA,
    TOOLS,
    TOOLS_BY_NAME,
    McpStdioServer,
    parse_render_input,
)
from doocs_md_py.mcp_server.stdio import (
    DEFAULT_PROTOCOL_VERSION,
    FATAL_PREFIX,
    INVALID_PARAMS,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    PARSE_ERROR,
    STARTUP_LINE,
    json_dumps,
)
from doocs_md_py.mcp_server.tools import NO_INPUT_SCHEMA, SERVER_NAME, SERVER_VERSION

EXPECTED_TOOL_ORDER = (
    "render_markdown",
    "list_themes",
    "list_colors",
    "list_fonts",
    "list_font_sizes",
    "list_legend_formats",
    "list_heading_styles",
    "list_spacing_options",
    "list_color_options",
    "list_code_block_themes",
    "list_ai_services",
    "explain_extensions",
    "get_renderer_options",
)

# upstream: index.ts:26-137（20 个 zod 顶层字段，声明序即 properties 键序）
EXPECTED_SCHEMA_FIELDS = (
    "markdown",
    "theme",
    "primaryColor",
    "fontFamily",
    "fontSize",
    "lineHeight",
    "blockSpacing",
    "linkColor",
    "blockquoteBackground",
    "legend",
    "isMacCodeBlock",
    "isShowLineNumber",
    "citeStatus",
    "countStatus",
    "themeMode",
    "isUseIndent",
    "isUseJustify",
    "headingStyles",
    "codeBlockTheme",
    "customCSS",
)

# upstream: index.ts:31-114（10 个 .optional().default(...)）
EXPECTED_DEFAULTS = {
    "theme": "default",
    "primaryColor": "#0F4C81",
    "legend": "alt",
    "isMacCodeBlock": False,
    "isShowLineNumber": False,
    "citeStatus": False,
    "countStatus": False,
    "themeMode": "light",
    "isUseIndent": False,
    "isUseJustify": False,
}


def _request(message_id, method, params=None):
    message = {"jsonrpc": "2.0", "id": message_id, "method": method}
    if params is not None:
        message["params"] = params
    return message


def _call(server, name, arguments=None):
    """tools/call 帧的便捷构造（返回值即完整 JSON-RPC 响应）。"""
    params = {"name": name}
    if arguments is not None:
        params["arguments"] = arguments
    return server.handle_message(_request(9, "tools/call", params))


def _call_text(server, name, arguments=None):
    response = _call(server, name, arguments)
    assert "error" not in response, response
    result = response["result"]
    return result["content"][0]["text"], result.get("isError", False)


def _call_ok(server, name, arguments=None):
    text, is_error = _call_text(server, name, arguments)
    assert is_error is False
    return json.loads(text)


# --------------------------------------------------------------------------- #
# 工具名册与入参 schema
# --------------------------------------------------------------------------- #


def test_registry_has_thirteen_tools_in_upstream_order():
    assert tuple(tool.name for tool in TOOLS) == EXPECTED_TOOL_ORDER
    assert len(TOOLS) == 13
    assert len(TOOLS_BY_NAME) == 13


def test_tools_list_payload_matches_registry_order():
    payload = McpStdioServer().handle_message(_request(1, "tools/list"))
    assert "error" not in payload
    tools = payload["result"]["tools"]
    assert [tool["name"] for tool in tools] == list(EXPECTED_TOOL_ORDER)


def test_every_tool_metadata_has_description_and_input_schema():
    for tool in TOOLS:
        metadata = tool.metadata()
        assert list(metadata) == ["name", "description", "inputSchema"]
        assert metadata["description"].strip()
        assert metadata["inputSchema"]["type"] == "object"


def test_only_render_markdown_declares_input_schema():
    for tool in TOOLS:
        if tool.name == "render_markdown":
            assert tool.input_schema is RENDER_MARKDOWN_INPUT_SCHEMA
        else:
            assert tool.input_schema == NO_INPUT_SCHEMA


def test_render_markdown_schema_field_order_and_required():
    schema = RENDER_MARKDOWN_INPUT_SCHEMA
    assert tuple(schema["properties"]) == EXPECTED_SCHEMA_FIELDS
    assert len(schema["properties"]) == 20
    assert schema["required"] == ["markdown"]


def test_render_markdown_schema_defaults():
    properties = RENDER_MARKDOWN_INPUT_SCHEMA["properties"]
    found = {name: prop["default"] for name, prop in properties.items() if "default" in prop}
    assert found == EXPECTED_DEFAULTS


def test_render_markdown_schema_declared_types():
    properties = RENDER_MARKDOWN_INPUT_SCHEMA["properties"]
    assert properties["markdown"]["type"] == "string"
    assert properties["headingStyles"]["type"] == "object"
    boolean_fields = (
        "isMacCodeBlock",
        "isShowLineNumber",
        "citeStatus",
        "countStatus",
        "isUseIndent",
        "isUseJustify",
    )
    for field in boolean_fields:
        assert properties[field]["type"] == "boolean"


def test_render_input_field_mapping_is_total():
    """JSON 键 → dataclass 字段的映射必须双向全覆盖（防 camelCase/snake_case 漂移）。"""
    from doocs_md_py.mcp_server import RENDER_INPUT_FIELDS
    from doocs_md_py.render.article import RenderArticleInput

    assert set(RENDER_INPUT_FIELDS) == set(RENDER_MARKDOWN_INPUT_SCHEMA["properties"])
    assert set(RENDER_INPUT_FIELDS.values()) == {field.name for field in dataclasses.fields(RenderArticleInput)}


# --------------------------------------------------------------------------- #
# zod 语义等价（.parse）
# --------------------------------------------------------------------------- #


def test_parse_fills_zod_defaults_only():
    parsed, errors = parse_render_input({"markdown": "# 标题"})
    assert errors == []
    assert parsed == {"markdown": "# 标题", **EXPECTED_DEFAULTS}


def test_parse_strips_unknown_keys():
    parsed, errors = parse_render_input({"markdown": "x", "bogus": 1})
    assert errors == []
    assert "bogus" not in parsed


def test_parse_reports_missing_required_first():
    _, errors = parse_render_input({})
    assert errors == ["markdown: Required"]


def test_parse_rejects_null_as_type_error():
    # zod .optional() 只放宽 undefined，不放宽显式 null
    _, errors = parse_render_input({"markdown": None})
    assert errors == ["markdown: Expected string, received null"]


# --------------------------------------------------------------------------- #
# 非法入参拒绝（isError 结果 + 上游自定义文案）
# --------------------------------------------------------------------------- #

INVALID_CASES = (
    ("hex", {"markdown": "x", "primaryColor": "#12345"}, "primaryColor: Must be a valid 6-digit hex color"),
    ("hex-no-hash", {"markdown": "x", "primaryColor": "0F4C81"}, "primaryColor: Must be a valid 6-digit hex color"),
    ("font-size-unitless", {"markdown": "x", "fontSize": "16"}, "fontSize: Must be a pixel size like 16px"),
    ("font-size-fraction", {"markdown": "x", "fontSize": "16.5px"}, "fontSize: Must be a pixel size like 16px"),
    ("line-height-unit", {"markdown": "x", "lineHeight": "1.75px"}, "lineHeight: Must be a unitless number like 1.75"),
    ("block-spacing-unit", {"markdown": "x", "blockSpacing": "1.15em"}, "blockSpacing: Must be a unitless number like 1"),
    (
        "enum-theme",
        {"markdown": "x", "theme": "fancy"},
        "theme: Invalid enum value. Expected 'default' | 'grace' | 'simple', received 'fancy'",
    ),
    (
        "enum-legend",
        {"markdown": "x", "legend": "caption"},
        "legend: Invalid enum value. Expected 'title-alt' | 'alt-title' | 'title' | 'alt' | 'filename' | 'none', "
        "received 'caption'",
    ),
    (
        "enum-theme-mode",
        {"markdown": "x", "themeMode": "auto"},
        "themeMode: Invalid enum value. Expected 'light' | 'dark', received 'auto'",
    ),
    (
        "enum-heading-style",
        {"markdown": "x", "headingStyles": {"h1": "fancy"}},
        "headingStyles.h1: Invalid enum value. Expected 'default' | 'color-only' | 'border-bottom' | "
        "'border-left' | 'custom', received 'fancy'",
    ),
    ("bool-string", {"markdown": "x", "isMacCodeBlock": "true"}, "isMacCodeBlock: Expected boolean, received string"),
    ("string-number", {"markdown": "x", "fontSize": 16}, "fontSize: Expected string, received number"),
    ("object-string", {"markdown": "x", "headingStyles": "h1"}, "headingStyles: Expected object, received string"),
    ("json-null", {"markdown": "x", "fontFamily": None}, "fontFamily: Expected string, received null"),
    ("json-array", {"markdown": "x", "headingStyles": ["h1"]}, "headingStyles: Expected object, received array"),
)


@pytest.mark.parametrize(
    ("arguments", "expected"),
    [case[1:] for case in INVALID_CASES],
    ids=[case[0] for case in INVALID_CASES],
)
def test_render_markdown_rejects_invalid_inputs(arguments, expected):
    text, is_error = _call_text(McpStdioServer(), "render_markdown", arguments)
    assert is_error is True
    assert text == expected


def test_render_markdown_strips_unknown_keys_and_succeeds():
    payload = _call_ok(McpStdioServer(), "render_markdown", {"markdown": "# 标题", "unknownKey": 1})
    assert list(payload) == ["html", "frontMatter", "readingTime"]


def test_render_markdown_reports_all_errors_joined_by_newline():
    text, is_error = _call_text(
        McpStdioServer(),
        "render_markdown",
        {"primaryColor": "#12345", "fontSize": "16"},
    )
    assert is_error is True
    assert text.split("\n") == [
        "markdown: Required",
        "primaryColor: Must be a valid 6-digit hex color",
        "fontSize: Must be a pixel size like 16px",
    ]


def test_code_block_theme_enum_lists_ten_urls_in_message():
    text, is_error = _call_text(McpStdioServer(), "render_markdown", {"markdown": "x", "codeBlockTheme": "nope"})
    assert is_error is True
    assert text.startswith("codeBlockTheme: Invalid enum value. Expected ")
    assert text.endswith(", received 'nope'")
    assert text.count(" | ") == 9  # 10 个候选 URL
    assert ".min.css'" in text


# --------------------------------------------------------------------------- #
# tools/call 往返
# --------------------------------------------------------------------------- #


def test_render_markdown_round_trip_shape():
    payload = _call_ok(McpStdioServer(), "render_markdown", {"markdown": "# 标题\n\n正文。"})
    assert payload["html"].startswith("<style>")
    assert "<h1" in payload["html"]
    assert isinstance(payload["frontMatter"], dict)
    assert set(payload["readingTime"]) == {"words", "minutes"}


def test_render_markdown_uses_injected_code_css_fetcher():
    fetched = []

    def fetcher(url):
        fetched.append(url)
        return "/* injected */"

    server = McpStdioServer(code_css_fetcher=fetcher)
    from doocs_md_py.render.code_themes import CODE_BLOCK_THEME_OPTIONS

    url = CODE_BLOCK_THEME_OPTIONS[0]["value"]
    payload = _call_ok(server, "render_markdown", {"markdown": "```js\n1\n```", "codeBlockTheme": url})
    assert fetched == [url]
    assert "/* injected */" in payload["html"]


def test_list_tools_payload_returned_as_json_text():
    text, is_error = _call_text(McpStdioServer(), "list_themes")
    assert is_error is False
    assert json.loads(text)["themes"][0] == {"value": "default", "label": "经典", "author": "official"}


def test_call_tool_accepts_omitted_arguments():
    server = McpStdioServer()
    text, is_error = _call_text(server, "list_heading_styles")
    assert is_error is False
    assert json.loads(text)["levels"] == ["h1", "h2", "h3", "h4", "h5", "h6"]


def test_handler_exception_becomes_is_error_result(monkeypatch):
    class Boom(Exception):
        pass

    def raiser(*_args, **_kwargs):
        raise Boom("炸了")

    monkeypatch.setitem(TOOLS_BY_NAME, "list_colors", dataclasses.replace(TOOLS_BY_NAME["list_colors"], handler=raiser))
    text, is_error = _call_text(McpStdioServer(), "list_colors")
    assert is_error is True
    assert text == "Boom: 炸了"


# --------------------------------------------------------------------------- #
# JSON-RPC 协议边界
# --------------------------------------------------------------------------- #


def test_initialize_echoes_supported_protocol_version():
    response = McpStdioServer().handle_message(
        _request(1, "initialize", {"protocolVersion": "2025-03-26", "clientInfo": {"name": "c", "version": "1"}})
    )
    assert response == {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "protocolVersion": "2025-03-26",
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        },
    }


def test_initialize_falls_back_to_newest_supported_version():
    response = McpStdioServer().handle_message(_request(1, "initialize", {"protocolVersion": "1999-01-01"}))
    assert response["result"]["protocolVersion"] == DEFAULT_PROTOCOL_VERSION


def test_initialize_without_params_uses_default_version():
    response = McpStdioServer().handle_message(_request(1, "initialize"))
    assert response["result"]["protocolVersion"] == DEFAULT_PROTOCOL_VERSION


def test_ping_returns_empty_result():
    assert McpStdioServer().handle_message(_request(2, "ping")) == {"jsonrpc": "2.0", "id": 2, "result": {}}


def test_notifications_are_silent():
    server = McpStdioServer()
    assert server.handle_message({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    assert server.handle_message({"jsonrpc": "2.0", "method": "notifications/cancelled"}) is None


def test_unknown_method_with_id_returns_method_not_found():
    response = McpStdioServer().handle_message(_request(3, "resources/list"))
    assert response["error"] == {"code": METHOD_NOT_FOUND, "message": "Method not found: resources/list"}


def test_unknown_notification_is_silently_dropped():
    assert McpStdioServer().handle_message({"jsonrpc": "2.0", "method": "nope"}) is None


def test_invalid_request_shape_returns_minus_32600():
    server = McpStdioServer()
    for message in ([1, 2], "text", {"jsonrpc": "2.0", "id": 1}):
        response = server.handle_message(message)
        assert response == {"jsonrpc": "2.0", "id": None, "error": {"code": INVALID_REQUEST, "message": "Invalid Request"}}


@pytest.mark.parametrize("raw", [b"{not json", b"", b"\xff\xfe"], ids=["broken", "empty", "non-utf8"])
def test_bad_frame_returns_parse_error(raw):
    assert McpStdioServer().handle_line(raw) == {
        "jsonrpc": "2.0",
        "id": None,
        "error": {"code": PARSE_ERROR, "message": "Parse error"},
    }


def test_call_tool_without_name_returns_minus_32602():
    response = McpStdioServer().handle_message(_request(4, "tools/call", {"arguments": {}}))
    assert response["error"] == {"code": INVALID_PARAMS, "message": "Invalid params"}


def test_call_tool_unknown_name_returns_minus_32602():
    response = _call(McpStdioServer(), "not_a_tool", {})
    assert response["error"] == {"code": INVALID_PARAMS, "message": "Unknown tool: not_a_tool"}


def test_call_tool_non_object_arguments_returns_minus_32602():
    response = _call(McpStdioServer(), "list_themes", "themes")
    assert response["error"] == {
        "code": INVALID_PARAMS,
        "message": "Invalid params: arguments must be an object",
    }


# --------------------------------------------------------------------------- #
# stdio 主循环与 CLI 接线
# --------------------------------------------------------------------------- #


def test_serve_writes_startup_line_and_skips_blank_frames():
    frames = b"\n".join(
        [
            json_dumps(_request(1, "initialize")).encode("utf-8"),
            b"",
            b"   ",
            json_dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}).encode("utf-8"),
            json_dumps(_request(2, "tools/list")).encode("utf-8"),
        ]
    )
    writer = io.BytesIO()
    stderr = io.StringIO()
    code = McpStdioServer().serve(io.BytesIO(frames + b"\n"), writer, stderr=stderr)

    assert code == 0
    assert stderr.getvalue() == STARTUP_LINE + "\n"
    out = writer.getvalue().decode("utf-8")
    assert out.endswith("\n")
    lines = [line for line in out.split("\n") if line]
    assert len(lines) == 2  # 通知与空行均无应答
    ids = [json.loads(line)["id"] for line in lines]
    assert ids == [1, 2]


def test_serve_returns_zero_on_empty_stdin():
    writer = io.BytesIO()
    assert McpStdioServer().serve(io.BytesIO(b""), writer, stderr=io.StringIO()) == 0
    assert writer.getvalue() == b""


class _RaisingStdin:
    """模拟 stdin 不可读（pytest 捕获态），驱动 fatal 分支。"""

    @property
    def buffer(self):
        raise OSError("stdin is closed")


def test_main_returns_one_and_logs_fatal(monkeypatch):
    stderr = io.StringIO()
    monkeypatch.setattr(sys, "stdin", _RaisingStdin())
    monkeypatch.setattr(sys, "stderr", stderr)

    from doocs_md_py.mcp_server import main as mcp_main

    assert mcp_main() == 1
    assert stderr.getvalue() == f"{FATAL_PREFIX} stdin is closed\n"


def test_cli_mcp_wires_stdio_server(monkeypatch):
    frames = (json_dumps(_request(1, "ping")) + "\n").encode("utf-8")
    stdout = SimpleNamespace(buffer=io.BytesIO())
    stderr = io.StringIO()
    monkeypatch.setattr(sys, "stdin", SimpleNamespace(buffer=io.BytesIO(frames)))
    monkeypatch.setattr(sys, "stdout", stdout)
    monkeypatch.setattr(sys, "stderr", stderr)

    assert cli.main(["mcp"]) == 0
    assert stderr.getvalue() == STARTUP_LINE + "\n"
    assert json.loads(stdout.buffer.getvalue().decode("utf-8"))["result"] == {}


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__]))
