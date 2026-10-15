"""stdio MCP Server 包（upstream: packages/mcp-server/src）。

四个模块：``options``（字面值资产）、``schema``（render_markdown 入参）、
``tools``（13 工具注册表）、``stdio``（换行分隔 JSON-RPC 2.0 传输层）。
"""

from .schema import RENDER_MARKDOWN_INPUT_SCHEMA, parse_render_input
from .stdio import McpStdioServer, json_dumps, main
from .tools import (
    RENDER_INPUT_FIELDS,
    SERVER_NAME,
    SERVER_VERSION,
    TOOLS,
    TOOLS_BY_NAME,
    ToolInputError,
    ToolSpec,
    call_tool,
    list_tools_payload,
)

__all__ = [
    "main",
    "McpStdioServer",
    "json_dumps",
    "parse_render_input",
    "RENDER_INPUT_FIELDS",
    "RENDER_MARKDOWN_INPUT_SCHEMA",
    "SERVER_NAME",
    "SERVER_VERSION",
    "ToolSpec",
    "ToolInputError",
    "TOOLS",
    "TOOLS_BY_NAME",
    "call_tool",
    "list_tools_payload",
]
