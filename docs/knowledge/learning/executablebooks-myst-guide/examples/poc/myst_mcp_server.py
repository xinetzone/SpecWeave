#!/usr/bin/env python3
"""MyST → MCP Server PoC (Proof of Concept).

解析包含 ``{mcp:server}`` / ``{mcp:tool}`` / ``{mcp:param}`` / ``{mcp:resource}`` /
``{mcp:prompt}`` MyST directives 的 Markdown 文档，动态生成可运行的 MCP Server。

这验证了报告第9.5节提出的"文档即MCP Server"构想——MyST文档本身既是人类可读的
文档，也是机器可解析的MCP Server描述，消除了文档与实现之间的中间转换层。

使用方法::

    python myst_mcp_server.py <mcp-doc.md>                  # stdio 模式（供MCP客户端连接）
    python myst_mcp_server.py <mcp-doc.md> --transport http # HTTP 模式（:8000/mcp）
    python myst_mcp_server.py <mcp-doc.md> --list           # 仅列出解析出的工具/资源/提示

示例::

    python myst_mcp_server.py github-tools.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# MyST Directive 解析器（轻量级PoC实现）
# ---------------------------------------------------------------------------

_DIRECTIVE_HEADER_RE = re.compile(
    r"^```\{(\w[\w:_-]*)\}\s*(.*)$"
)
_OPTION_RE = re.compile(
    r"^:([\w][\w\s\-]*?)(\??)\s*:\s*(.*)$"
)
_FENCE_CLOSE_RE = re.compile(r"^```\s*$")


@dataclass
class ParamDef:
    """参数定义（对应 {mcp:param} 指令）。"""
    name: str
    type: str = "string"
    required: bool = True
    description: str = ""
    default: Any = None
    enum: list[str] = field(default_factory=list)


@dataclass
class ToolDef:
    """工具定义（对应 {mcp:tool} 指令）。"""
    name: str
    description: str = ""
    params: list[ParamDef] = field(default_factory=list)
    body: str = ""


@dataclass
class ResourceDef:
    """资源定义（对应 {mcp:resource} 指令）。"""
    uri: str = ""
    name: str = ""
    mime_type: str = "text/plain"
    description: str = ""
    body: str = ""


@dataclass
class PromptDef:
    """提示模板定义（对应 {mcp:prompt} 指令）。"""
    name: str = ""
    description: str = ""
    template: str = ""
    arguments: list[ParamDef] = field(default_factory=list)


@dataclass
class ServerDef:
    """MCP Server 定义（对应 {mcp:server} 指令）。"""
    name: str = "myst-mcp-server"
    version: str = "0.1.0"
    transport: str = "stdio"
    description: str = ""
    tools: list[ToolDef] = field(default_factory=list)
    resources: list[ResourceDef] = field(default_factory=list)
    prompts: list[PromptDef] = field(default_factory=list)


_TYPE_MAP = {
    "string": {"type": "string"},
    "str": {"type": "string"},
    "integer": {"type": "integer"},
    "int": {"type": "integer"},
    "number": {"type": "number"},
    "float": {"type": "number"},
    "boolean": {"type": "boolean"},
    "bool": {"type": "boolean"},
    "array": {"type": "array", "items": {"type": "string"}},
    "object": {"type": "object"},
}


def _parse_type(type_str: str) -> dict:
    """将类型字符串映射为 JSON Schema（返回新字典，避免污染_TYPE_MAP）。"""
    type_str = type_str.strip().lower()
    if type_str.startswith("array<"):
        inner = type_str[6:-1] if type_str.endswith(">") else "string"
        return {"type": "array", "items": _parse_type(inner)}
    base = _TYPE_MAP.get(type_str, {"type": "string"})
    return dict(base)


def parse_myst_mcp(md_content: str) -> ServerDef:
    """解析包含 mcp:* 指令的 MyST Markdown 内容，返回 ServerDef。

    这是一个轻量级递归下降解析器，支持：
    - 反引号围栏中的 ``{mcp:server}`` / ``{mcp:tool}`` / ``{mcp:param}`` /
      ``{mcp:resource}`` / ``{mcp:prompt}`` 指令
    - ``:key: value`` 格式的选项
    - 嵌套指令（``{mcp:tool}`` 内含 ``{mcp:param}``）
    """
    lines = md_content.splitlines()
    server = ServerDef()
    i = 0
    n = len(lines)

    def parse_options(start: int) -> tuple[dict[str, str], int]:
        """从 start 行开始解析连续的 :key: value 选项行。"""
        opts: dict[str, str] = {}
        idx = start
        while idx < n:
            line = lines[idx]
            m = _OPTION_RE.match(line)
            if m:
                key = m.group(1).strip().replace("-", "_").replace(" ", "_")
                optional = bool(m.group(2))
                value = m.group(3).strip()
                opts[key] = value
                opts[f"{key}_optional"] = optional
                idx += 1
            else:
                break
        return opts, idx

    def parse_directive_body(start: int, end_directives: set[str] | None = None) -> tuple[str, int]:
        """解析指令体，直到遇到闭合 ``` 或同级指令。"""
        body_lines: list[str] = []
        idx = start
        depth = 1
        while idx < n:
            line = lines[idx]
            if _FENCE_CLOSE_RE.match(line):
                depth -= 1
                if depth == 0:
                    idx += 1
                    break
                body_lines.append(line)
                idx += 1
            elif _DIRECTIVE_HEADER_RE.match(line):
                m = _DIRECTIVE_HEADER_RE.match(line)
                name = m.group(1)
                if end_directives and name in end_directives:
                    break
                depth += 1
                body_lines.append(line)
                idx += 1
            else:
                body_lines.append(line)
                idx += 1
        return "\n".join(body_lines), idx

    while i < n:
        line = lines[i]
        dm = _DIRECTIVE_HEADER_RE.match(line)
        if dm:
            directive_name = dm.group(1)
            args_str = dm.group(2).strip()
            i += 1

            if directive_name == "mcp:server":
                server.name = args_str or server.name
                opts, i = parse_options(i)
                server.version = opts.get("version", server.version)
                server.transport = opts.get("transport", server.transport)
                desc, i = parse_directive_body(i, {"mcp:tool", "mcp:resource", "mcp:prompt"})
                server.description = desc.strip()

            elif directive_name == "mcp:tool":
                tool = ToolDef(name=args_str)
                opts, i = parse_options(i)
                tool.description = opts.get("description", "")

                nested_body_lines: list[str] = []
                while i < n:
                    nested_line = lines[i]
                    pm = _DIRECTIVE_HEADER_RE.match(nested_line)
                    if pm and pm.group(1) == "mcp:param":
                        i += 1
                        param_args = pm.group(2).strip()
                        popts, i = parse_options(i)
                        p = ParamDef(
                            name=param_args,
                            type=popts.get("type", "string"),
                            required=not popts.get("required", "true").lower() == "false",
                            description=popts.get("description", ""),
                            default=popts.get("default", None),
                        )
                        if popts.get("enum"):
                            p.enum = [e.strip() for e in popts["enum"].split(",")]
                        pbody, i = parse_directive_body(i)
                        if not p.description:
                            p.description = pbody.strip()
                        tool.params.append(p)
                    elif _FENCE_CLOSE_RE.match(nested_line):
                        i += 1
                        break
                    else:
                        nested_body_lines.append(nested_line)
                        i += 1

                tool.body = "\n".join(nested_body_lines).strip()
                server.tools.append(tool)

            elif directive_name == "mcp:resource":
                res = ResourceDef(name=args_str)
                opts, i = parse_options(i)
                res.uri = opts.get("uri", f"resource://{server.name}/{args_str}")
                res.mime_type = opts.get("mime_type", opts.get("mimetype", "text/plain"))
                res.description = opts.get("description", "")
                body, i = parse_directive_body(i)
                res.body = body.strip()
                server.resources.append(res)

            elif directive_name == "mcp:prompt":
                prompt = PromptDef(name=args_str)
                opts, i = parse_options(i)
                prompt.description = opts.get("description", "")
                # parse nested args if any
                while i < n:
                    nested_line = lines[i]
                    am = _DIRECTIVE_HEADER_RE.match(nested_line)
                    if am and am.group(1) == "mcp:arg":
                        i += 1
                        arg_args = am.group(2).strip()
                        aopts, i = parse_options(i)
                        ap = ParamDef(
                            name=arg_args,
                            type=aopts.get("type", "string"),
                            required=not aopts.get("required", "true").lower() == "false",
                            description=aopts.get("description", ""),
                            default=aopts.get("default", None),
                        )
                        abody, i = parse_directive_body(i)
                        if not ap.description:
                            ap.description = abody.strip()
                        prompt.arguments.append(ap)
                    elif _FENCE_CLOSE_RE.match(nested_line):
                        i += 1
                        break
                    else:
                        prompt.template += nested_line + "\n"
                        i += 1
                prompt.template = prompt.template.strip()
                server.prompts.append(prompt)
            else:
                _, i = parse_directive_body(i)
        else:
            i += 1

    return server


# ---------------------------------------------------------------------------
# 动态 MCP Server 构建
# ---------------------------------------------------------------------------

def _cast_value(val: Any, type_str: str) -> Any:
    """将字符串值转换为对应Python类型。"""
    if val is None:
        return None
    if isinstance(val, str):
        t = _py_type(type_str) if isinstance(type_str, str) else type_str
        try:
            if t is bool:
                return val.lower() in ("true", "1", "yes")
            if t is list:
                return json.loads(val) if val.startswith("[") else [x.strip() for x in val.split(",")]
            return t(val)
        except (ValueError, TypeError, json.JSONDecodeError):
            return val
    return val


_PY_TYPE_MAP = {
    "string": str, "str": str,
    "integer": int, "int": int,
    "number": float, "float": float,
    "boolean": bool, "bool": bool,
    "array": list,
    "object": dict,
}


def _py_type(type_str: str):
    type_str = type_str.strip().lower()
    if type_str.startswith("array<"):
        return list
    return _PY_TYPE_MAP.get(type_str, str)


def build_input_schema(tool: ToolDef) -> dict[str, Any]:
    """将 ToolDef.params 转换为 MCP JSON Schema。"""
    properties: dict[str, Any] = {}
    required: list[str] = []

    for p in tool.params:
        prop = _parse_type(p.type)
        if p.description:
            prop["description"] = p.description
        if p.default is not None:
            prop["default"] = _cast_value(p.default, p.type)
        if p.enum:
            prop["enum"] = p.enum
        properties[p.name] = prop
        if p.required:
            required.append(p.name)

    schema: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema


def _build_annotated_type(p: ParamDef) -> str:
    """为参数生成带Annotated/Field/Literal的类型注解字符串，确保JSON Schema完整。"""
    py_t = _py_type(p.type)
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
    else:
        return base_type


def build_mcp_server(server_def: ServerDef, *, host: str = "127.0.0.1", port: int = 8000) -> Any:
    """根据 ServerDef 构建 FastMCP 实例。

    使用 exec() 动态生成带具名参数的 handler 函数，确保 FastMCP 通过函数签名
    内省生成正确的 JSON Schema（而非 **kwargs 导致的单字段问题）。
    使用 Annotated+Field 保留描述信息，Literal 保留枚举约束。
    """
    from mcp.server import FastMCP
    from typing import Annotated, Literal
    from pydantic import Field

    instructions_parts = [server_def.description] if server_def.description else []
    instructions_parts.append(f"Server version: {server_def.version}")
    instructions_parts.append(
        "This server was generated from a MyST Markdown document. "
        "Tool implementations in this PoC return mock responses."
    )

    mcp = FastMCP(
        name=server_def.name,
        instructions="\n\n".join(instructions_parts),
        host=host,
        port=port,
    )

    for tool in server_def.tools:
        tool_name_safe = tool.name.replace("-", "_")
        tool_desc = tool.description or tool.body[:200] or tool_name_safe

        param_parts: list[str] = []
        param_dict_parts: list[str] = []
        for p in tool.params:
            annotated_type = _build_annotated_type(p)
            if p.required:
                param_parts.append(f"{p.name}: {annotated_type}")
            else:
                default_val = _cast_value(p.default, p.type) if p.default is not None else None
                param_parts.append(f"{p.name}: {annotated_type} | None = {repr(default_val)}")
            param_dict_parts.append(f"'{p.name}': {p.name}")

        param_sig = ", ".join(param_parts) if param_parts else ""
        args_dict = "{" + ", ".join(param_dict_parts) + "}"

        func_code = f"""
async def {tool_name_safe}({param_sig}):
    import json, mcp.types as types
    args = {args_dict}
    args_repr = json.dumps(args, ensure_ascii=False, indent=2, default=str)
    result = (
        f"[MyST-MCP PoC] Called tool '{tool.name}'\\n"
        f"Description: {tool_desc}\\n"
        f"Arguments:\\n{{args_repr}}\\n\\n"
        f"---\\n"
        f"Note: This is a PoC mock response. In production, "
        f"this handler would be replaced by actual business logic "
        f"or mapped to a backend implementation."
    )
    return [types.TextContent(type="text", text=result)]
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

    for res in server_def.resources:
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
        else:
            text_expr = (
                f'f"[MyST-MCP PoC] Resource \'{res.name}\' (URI: {uri_template})'
                f'\\nArgs: {{json.dumps({kwargs_dict}, ensure_ascii=False)}}"'
            )

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
        namespace = {}
        exec(func_code, namespace)
        handler_fn = namespace[func_name]
        handler_fn.__doc__ = res.description

        mcp.resource(uri=res.uri, name=res.name, description=res.description)(handler_fn)

    for prompt in server_def.prompts:
        func_name = prompt.name.replace("-", "_")
        prompt_desc = prompt.description or prompt.name
        template_str = prompt.template
        arg_names = [a.name for a in prompt.arguments]

        param_parts: list[str] = []
        for a in prompt.arguments:
            py_t = _py_type(a.type)
            type_name = py_t.__name__
            if a.required:
                param_parts.append(f"{a.name}: {type_name}")
            else:
                default_val = _cast_value(a.default, a.type) if a.default is not None else None
                param_parts.append(f"{a.name}: {type_name} | None = {repr(default_val)}")

        param_sig = ", ".join(param_parts) if param_parts else ""

        replacement_code_lines = []
        for an in arg_names:
            replacement_code_lines.append(f"    text = text.replace('{{{an}}}', str({an}) if {an} is not None else '')")
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
        namespace = {}
        exec(func_code, namespace)
        handler_fn = namespace[func_name]
        handler_fn.__name__ = func_name
        handler_fn.__doc__ = prompt_desc

        mcp.prompt(name=prompt.name, description=prompt_desc)(handler_fn)

    return mcp


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_server_summary(server: ServerDef) -> None:
    """打印解析结果摘要。"""
    print("=" * 60)
    print(f"MCP Server: {server.name}")
    print(f"Version:    {server.version}")
    print(f"Transport:  {server.transport}")
    print(f"Description: {server.description[:100]}")
    print("-" * 60)
    print(f"Tools ({len(server.tools)}):")
    for t in server.tools:
        req_params = [p.name for p in t.params if p.required]
        opt_params = [p.name for p in t.params if not p.required]
        print(f"  - {t.name}")
        if t.description:
            print(f"    desc: {t.description[:80]}")
        if req_params:
            print(f"    required: {', '.join(req_params)}")
        if opt_params:
            print(f"    optional: {', '.join(opt_params)}")
    print(f"Resources ({len(server.resources)}):")
    for r in server.resources:
        print(f"  - {r.name} ({r.uri})")
    print(f"Prompts ({len(server.prompts)}):")
    for p in server.prompts:
        print(f"  - {p.name}")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MyST → MCP Server PoC: Parse {mcp:*} directives from MyST markdown and run as MCP server"
    )
    parser.add_argument("md_file", help="Path to MyST markdown file with mcp: directives")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default=None,
        help="Transport mode (overrides :transport: option in document)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Only list parsed tools/resources/prompts, don't start server",
    )
    parser.add_argument("--host", default="127.0.0.1", help="HTTP host")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port")
    args = parser.parse_args()

    md_path = Path(args.md_file)
    if not md_path.exists():
        print(f"Error: file not found: {md_path}", file=sys.stderr)
        sys.exit(1)

    content = md_path.read_text(encoding="utf-8")
    server_def = parse_myst_mcp(content)

    if args.list:
        print_server_summary(server_def)
        print()
        print("JSON Schema Preview (first tool):")
        if server_def.tools:
            print(json.dumps(
                build_input_schema(server_def.tools[0]),
                ensure_ascii=False, indent=2
            ))
        return

    mcp = build_mcp_server(server_def, host=args.host, port=args.port)

    transport = args.transport or server_def.transport
    print(f"Starting MCP Server '{server_def.name}' via {transport}...", file=sys.stderr)

    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "http":
        mcp.run(transport="streamable-http")
    elif transport == "sse":
        mcp.run(transport="sse")


if __name__ == "__main__":
    main()
