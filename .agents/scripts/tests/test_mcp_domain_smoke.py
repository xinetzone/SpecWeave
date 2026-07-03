"""mcp_domain 烟雾测试——验证UNVERIFIED模块可导入、模型可创建、解析器可运行。

这些测试不追求覆盖率，而是作为"已实现未验证"代码的基本安全网，
防止模块级别的回归（语法错误、导入失败、核心数据结构不可用）。
"""
from __future__ import annotations

import pytest


class TestMcpDomainImports:
    """验证所有公开API可正常导入。"""

    def test_constants_import(self):
        from mdi.mcp_domain import HAS_MDIT
        assert isinstance(HAS_MDIT, bool)

    def test_models_import(self):
        from mdi.mcp_domain import McpParam, McpTool, McpResource, McpPrompt, McpServer
        assert McpParam is not None
        assert McpTool is not None
        assert McpResource is not None
        assert McpPrompt is not None
        assert McpServer is not None

    def test_parser_import(self):
        from mdi.mcp_domain import parse_myst_mcp, parse_string, parse_file
        assert callable(parse_myst_mcp)
        assert callable(parse_string)
        assert callable(parse_file)

    def test_utils_import(self):
        from mdi.mcp_domain import py_type, json_schema_type, cast_value, build_input_schema
        assert callable(py_type)
        assert callable(json_schema_type)
        assert callable(cast_value)
        assert callable(build_input_schema)


class TestMcpModels:
    """验证数据模型可正常实例化。"""

    def test_param_creation(self):
        from mdi.mcp_domain import McpParam
        p = McpParam(name="query", type="string", required=True, description="Search query")
        assert p.name == "query"
        assert p.type == "string"
        assert p.required is True
        assert p.description == "Search query"

    def test_tool_creation(self):
        from mdi.mcp_domain import McpParam, McpTool
        p = McpParam(name="x", type="integer", required=True, description="X value")
        t = McpTool(name="add", description="Add numbers", params=[p])
        assert t.name == "add"
        assert len(t.params) == 1
        assert t.params[0].name == "x"

    def test_server_creation(self):
        from mdi.mcp_domain import McpServer
        s = McpServer(
            name="math-server",
            version="1.0.0",
            transport="stdio",
            tools=[],
            resources=[],
            prompts=[],
        )
        assert s.name == "math-server"
        assert s.version == "1.0.0"
        assert s.tools == []

    def test_resource_creation(self):
        from mdi.mcp_domain import McpResource
        r = McpResource(uri="file:///test", name="test", mime_type="text/plain", description="Test resource", body="hello")
        assert r.uri == "file:///test"
        assert r.mime_type == "text/plain"
        assert r.body == "hello"

    def test_prompt_creation(self):
        from mdi.mcp_domain import McpPrompt
        p = McpPrompt(name="greet", description="Greeting template", template="Hello {name}!", arguments=[])
        assert p.name == "greet"
        assert p.template == "Hello {name}!"
        assert p.arguments == []


class TestMcpUtils:
    """验证工具函数基本功能。"""

    def test_py_type_mapping(self):
        from mdi.mcp_domain import py_type
        assert py_type("string") is str
        assert py_type("integer") is int
        assert py_type("number") is float
        assert py_type("boolean") is bool

    def test_json_schema_type(self):
        from mdi.mcp_domain import json_schema_type
        assert json_schema_type("string") == {"type": "string"}
        assert json_schema_type("integer") == {"type": "integer"}

    def test_cast_value_string(self):
        from mdi.mcp_domain import cast_value
        assert cast_value("hello", "string") == "hello"
        assert cast_value("42", "integer") == 42
        assert cast_value("true", "boolean") is True

    def test_build_input_schema(self):
        from mdi.mcp_domain import McpParam, McpTool, build_input_schema
        p1 = McpParam(name="name", type="string", required=True, description="Name")
        p2 = McpParam(name="age", type="integer", required=False, description="Age", default="18")
        tool = McpTool(name="create_user", description="Create user", params=[p1, p2])
        schema = build_input_schema(tool)
        assert "properties" in schema
        assert "name" in schema["properties"]
        assert "age" in schema["properties"]
        assert "name" in schema.get("required", [])


class TestMcpParser:
    """验证解析器可处理基本的MCP directive格式。"""

    def test_parse_string_no_mcp_returns_none(self):
        from mdi.mcp_domain import parse_string
        result = parse_string("# No MCP here\n\nJust regular markdown.")
        assert result is None

    def test_parse_string_with_backtick_server(self):
        from mdi.mcp_domain import parse_string
        content = """
# Test MCP Server

```{mcp:server} test-server
:version: 1.0.0
:transport: stdio

A test MCP server.
```
"""
        server = parse_string(content)
        assert server is not None
        assert server.name == "test-server"
        assert server.version == "1.0.0"
