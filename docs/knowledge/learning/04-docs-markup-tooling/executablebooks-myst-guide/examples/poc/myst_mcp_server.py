#!/usr/bin/env python3
"""MyST → MCP Server CLI (PoC)

将包含 ``{mcp:server}`` / ``{mcp:tool}`` / ``{mcp:resource}`` / ``{mcp:prompt}``
directives 的 MyST Markdown 文档解析并运行为 MCP Server。

核心解析与构建逻辑已封装在 :mod:`mdi.mcp_domain` 和 :mod:`mdi.mcp_server` 中，
本脚本仅提供 CLI 入口。

使用方法::

    python myst_mcp_server.py <mcp-doc.md>                  # stdio 模式
    python myst_mcp_server.py <mcp-doc.md> --transport http # HTTP 模式
    python myst_mcp_server.py <mcp-doc.md> --list           # 仅列出解析结果

示例::

    python myst_mcp_server.py github-tools.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_sys_paths_to_try = [
    Path(__file__).resolve().parents[6] / ".agents" / "scripts",
    Path.cwd() / ".agents" / "scripts",
]
for _p in _sys_paths_to_try:
    _sp = str(_p)
    if _sp not in sys.path and _p.exists():
        sys.path.insert(0, _sp)

from mdi.mcp_domain import parse_file, build_input_schema
from mdi.mcp_server import build_fastmcp_server


def print_server_summary(server_def) -> None:
    """打印解析结果摘要。"""
    print("=" * 60)
    print(f"MCP Server: {server_def.name}")
    print(f"Version:    {server_def.version}")
    print(f"Transport:  {server_def.transport}")
    desc = server_def.description[:100] if server_def.description else ""
    print(f"Description: {desc}")
    print("-" * 60)
    print(f"Tools ({len(server_def.tools)}):")
    for t in server_def.tools:
        req_params = [p.name for p in t.params if p.required]
        opt_params = [p.name for p in t.params if not p.required]
        print(f"  - {t.name}")
        if t.description:
            print(f"    desc: {t.description[:80]}")
        if req_params:
            print(f"    required: {', '.join(req_params)}")
        if opt_params:
            print(f"    optional: {', '.join(opt_params)}")
    print(f"Resources ({len(server_def.resources)}):")
    for r in server_def.resources:
        print(f"  - {r.name} ({r.uri}) [{r.mime_type}]")
    print(f"Prompts ({len(server_def.prompts)}):")
    for p in server_def.prompts:
        args = [a.name for a in p.arguments]
        print(f"  - {p.name}({', '.join(args)})")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MyST → MCP Server: Parse {mcp:*} directives from MyST markdown and run as MCP server"
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

    server_def = parse_file(md_path)
    if server_def is None:
        print(f"Error: no mcp:server directive found in {md_path}", file=sys.stderr)
        sys.exit(1)

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

    mcp = build_fastmcp_server(server_def, host=args.host, port=args.port)

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
