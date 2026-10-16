"""支持 ``python -m doocs_md_py.mcp_server`` 直接启动 stdio MCP Server。"""

from doocs_md_py.mcp_server import main

if __name__ == "__main__":
    raise SystemExit(main())
