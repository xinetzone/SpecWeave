"""MyST MCP Server Builder — 将 McpServer 定义构建为可运行的 FastMCP 实例。

核心函数 :func:`build_fastmcp_server` 接收由 :func:`mdi.mcp_domain.parse_myst_mcp`
或 :func:`mdi.mcp_domain.parse_file` 返回的 :class:`McpServer` 对象，动态生成带正确
类型签名的 handler 函数，并注册到 FastMCP 实例。

使用 ``exec()`` 动态生成带具名参数的 handler，确保 FastMCP 通过函数签名内省
生成正确的 JSON Schema（而非 ``**kwargs`` 导致的单字段 schema 问题）。
使用 ``Annotated`` + ``Field`` 保留参数描述，``Literal`` 保留枚举约束。

用法::

    from mdi.mcp_domain import parse_file
    from mdi.mcp_server import build_fastmcp_server

    server_def = parse_file("github-tools.md")
    mcp = build_fastmcp_server(server_def, host="127.0.0.1", port=8000)
    mcp.run(transport="stdio")          # 或 "streamable-http" / "sse"
"""

from __future__ import annotations

import re
from typing import Any

from mdi.mcp_domain import (
    McpServer,
    McpTool,
    McpResource,
    McpPrompt,
    McpParam,
    py_type,
    cast_value,
)


def _build_annotated_type(p: McpParam) -> str:
    """为参数生成带 Annotated/Field/Literal 的类型注解字符串，确保 JSON Schema 完整。"""
    py_t = py_type(p.type)
    type_name = py_t.__name__

    if p.enum:
        literal_values = ", ".join(repr(e) for e in p.enum)
        base_type = f"Literal[{literal_values}]"
    else:
        base_type = type_name

    field_args: list[str] = []
    if p.description:
        field_args.append(f"description={repr(p.description)}")

    if field_args:
        return f"Annotated[{base_type}, Field({', '.join(field_args)})]"
    return base_type


def build_fastmcp_server(
    server_def: McpServer,
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
    mock_response: bool = True,
) -> Any:
    """根据 McpServer 定义构建 FastMCP 实例。

    Parameters
    ----------
    server_def:
        由 ``parse_myst_mcp()`` 或 ``parse_file()`` 返回的 McpServer 对象。
    host, port:
        HTTP/SSE 监听地址，传入 FastMCP 构造函数。
    mock_response:
        若为 True（默认），工具/资源/提示 handler 返回 PoC mock 响应；
        若为 False，则生成的 handler 仅返回参数 echo，由调用方后续替换。

    Returns
    -------
    FastMCP
        已注册所有 tools / resources / prompts 的 FastMCP 实例，
        可直接调用 ``.run(transport=...)`` 启动。
    """
    from mcp.server import FastMCP
    from typing import Annotated, Literal
    from pydantic import Field

    instructions_parts: list[str] = []
    if server_def.description:
        instructions_parts.append(server_def.description)
    instructions_parts.append(f"Server version: {server_def.version}")
    if mock_response:
        instructions_parts.append(
            "This server was generated from a MyST Markdown document. "
            "Tool implementations return mock responses (PoC mode)."
        )

    mcp = FastMCP(
        name=server_def.name,
        instructions="\n\n".join(instructions_parts),
        host=host,
        port=port,
    )

    for tool in server_def.tools:
        _register_tool(mcp, tool, Annotated=Annotated, Literal=Literal, Field=Field, mock=mock_response)

    for res in server_def.resources:
        _register_resource(mcp, res, mock=mock_response)

    for prompt in server_def.prompts:
        _register_prompt(mcp, prompt, mock=mock_response)

    return mcp


# ---------------------------------------------------------------------------
# Tool 注册
# ---------------------------------------------------------------------------

def _register_tool(
    mcp: Any,
    tool: McpTool,
    *,
    Annotated: Any,
    Literal: Any,
    Field: Any,
    mock: bool,
) -> None:
    tool_name_safe = tool.name.replace("-", "_")
    tool_desc = tool.description or tool.body[:200] or tool_name_safe

    param_parts: list[str] = []
    param_dict_parts: list[str] = []
    for p in tool.params:
        annotated_type = _build_annotated_type(p)
        if p.required:
            param_parts.append(f"{p.name}: {annotated_type}")
        else:
            default_val = cast_value(p.default, p.type) if p.default is not None else None
            param_parts.append(f"{p.name}: {annotated_type} | None = {repr(default_val)}")
        param_dict_parts.append(f"'{p.name}': {p.name}")

    param_sig = ", ".join(param_parts) if param_parts else ""
    args_dict = "{" + ", ".join(param_dict_parts) + "}"

    if mock:
        func_code = f"""
async def {tool_name_safe}({param_sig}):
    import json, mcp.types as types
    args = {args_dict}
    args_repr = json.dumps(args, ensure_ascii=False, indent=2, default=str)
    result = (
        f"[MyST-MCP] Called tool '{tool.name}'\\n"
        f"Description: {tool_desc}\\n"
        f"Arguments:\\n{{args_repr}}\\n\\n"
        f"---\\n"
        f"Note: This is a mock response from a MyST-defined MCP server. "
        f"Replace this handler with actual business logic in production."
    )
    return [types.TextContent(type="text", text=result)]
"""
    else:
        func_code = f"""
async def {tool_name_safe}({param_sig}):
    import json, mcp.types as types
    args = {args_dict}
    return [types.TextContent(
        type="text",
        text=json.dumps({{"tool": "{tool.name}", "args": args}}, ensure_ascii=False)
    )]
"""

    namespace: dict[str, Any] = {
        "Annotated": Annotated,
        "Literal": Literal,
        "Field": Field,
    }
    exec(func_code, namespace)
    handler_fn = namespace[tool_name_safe]
    handler_fn.__name__ = tool_name_safe
    handler_fn.__doc__ = tool_desc

    mcp.add_tool(handler_fn)


# ---------------------------------------------------------------------------
# Resource 注册
# ---------------------------------------------------------------------------

def _register_resource(mcp: Any, res: McpResource, *, mock: bool) -> None:
    uri_template = res.uri
    uri_params = re.findall(r'\{(\w+)\}', uri_template)
    func_name = res.name.replace("-", "_")

    param_sig = ", ".join(uri_params) if uri_params else ""
    kwargs_dict = "{" + ", ".join(f"'{p}': {p}" for p in uri_params) + "}"

    has_body = bool(res.body)
    body_repr = repr(res.body) if res.body else '""'
    mime_type_repr = repr(res.mime_type)

    if has_body:
        text_expr = body_repr
    elif mock:
        text_expr = (
            f'f"[MyST-MCP] Resource \'{res.name}\' (URI: {uri_template})'
            f'\\nArgs: {{json.dumps({kwargs_dict}, ensure_ascii=False)}}"'
        )
    else:
        text_expr = '""'

    text_replacement_lines = []
    for up in uri_params:
        text_replacement_lines.append(
            f"    text = text.replace('{{{up}}}', str({up}))"
        )
    text_replacement_block = "\n".join(text_replacement_lines)

    func_code = f"""
async def {func_name}({param_sig}):
    import json, mcp.types as types
    kwargs = {kwargs_dict}
    text = {text_expr}
{text_replacement_block}
    resolved_uri = {repr(uri_template)}
    for k, v in kwargs.items():
        resolved_uri = resolved_uri.replace('{{' + k + '}}', str(v))
    return types.ReadResourceResult(
        contents=[
            types.TextResourceContents(
                uri=resolved_uri,
                mimeType={mime_type_repr},
                text=text,
            )
        ]
    )
"""
    namespace: dict[str, Any] = {}
    exec(func_code, namespace)
    handler_fn = namespace[func_name]
    handler_fn.__doc__ = res.description

    mcp.resource(uri=res.uri, name=res.name, description=res.description)(handler_fn)


# ---------------------------------------------------------------------------
# Prompt 注册
# ---------------------------------------------------------------------------

def _register_prompt(mcp: Any, prompt: McpPrompt, *, mock: bool) -> None:
    func_name = prompt.name.replace("-", "_")
    prompt_desc = prompt.description or prompt.name
    template_str = prompt.template
    arg_names = [a.name for a in prompt.arguments]

    param_parts: list[str] = []
    for a in prompt.arguments:
        py_t = py_type(a.type)
        type_name = py_t.__name__
        if a.required:
            param_parts.append(f"{a.name}: {type_name}")
        else:
            default_val = cast_value(a.default, a.type) if a.default is not None else None
            param_parts.append(f"{a.name}: {type_name} | None = {repr(default_val)}")

    param_sig = ", ".join(param_parts) if param_parts else ""

    replacement_code_lines = []
    for an in arg_names:
        replacement_code_lines.append(
            f"    text = text.replace('{{{an}}}', str({an}) if {an} is not None else '')"
        )
    replacement_block = "\n".join(replacement_code_lines)

    func_code = f"""
async def {func_name}({param_sig}):
    import mcp.types as types
    text = {repr(template_str)}
{replacement_block if replacement_block else ''}
    return types.GetPromptResult(
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=text),
            )
        ]
    )
"""
    namespace: dict[str, Any] = {}
    exec(func_code, namespace)
    handler_fn = namespace[func_name]
    handler_fn.__name__ = func_name
    handler_fn.__doc__ = prompt_desc

    mcp.prompt(name=prompt.name, description=prompt_desc)(handler_fn)
