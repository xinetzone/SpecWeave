"""MCP Domain 数据模型定义。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class McpParam:
    """MCP 工具/提示的参数定义。"""
    name: str
    type: str = "string"
    required: bool = True
    description: str = ""
    default: str | None = None
    enum: list[str] = field(default_factory=list)


@dataclass
class McpTool:
    """MCP Tool 定义。"""
    name: str
    description: str = ""
    params: list[McpParam] = field(default_factory=list)
    body: str = ""


@dataclass
class McpResource:
    """MCP Resource 定义。"""
    uri: str = ""
    name: str = ""
    description: str = ""
    mime_type: str = "text/plain"
    body: str = ""


@dataclass
class McpPrompt:
    """MCP Prompt 定义。"""
    name: str = ""
    description: str = ""
    arguments: list[McpParam] = field(default_factory=list)
    template: str = ""


@dataclass
class McpServer:
    """MCP Server 定义，从 MyST 文档解析的根对象。"""
    name: str = "myst-mcp-server"
    version: str = "0.1.0"
    description: str = ""
    transport: str = "stdio"
    tools: list[McpTool] = field(default_factory=list)
    resources: list[McpResource] = field(default_factory=list)
    prompts: list[McpPrompt] = field(default_factory=list)
    source_path: Path | None = None
