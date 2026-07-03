"""MCP Domain for MyST Markdown - 数据模型与解析器。
STATUS: UNVERIFIED - 未经实战验证，参考pytest_gen/mdi.parser使用

实现报告第9章中提出的"文档即MCP Server"原型：
从使用 mcp: 前缀 directive 的 MyST 文档中解析 MCP Server 定义。

支持两种围栏语法：
1. 冒号围栏（MyST 标准），内层使用更多冒号::
    :::{mcp:server} server-name      <- 3 colons (outermost)
    :version: 1.0.0
    :transport: stdio

    服务器描述文本。

    ::::{mcp:tool} tool-name        <- 4 colons (nested)
    :description: 工具描述
    ::::
    :::

2. 反引号围栏（通用 Markdown 兼容），内层通过围栏深度计数嵌套:
    ```{mcp:server} server-name
    :version: 1.0.0

    服务器描述文本。

    ```{mcp:tool} tool-name
    :description: 工具描述
    ```
    ```

Directive 类型：
- mcp:server  — 服务器根定义，内含 tool/resource/prompt
- mcp:tool    — 工具定义，内含 mcp:param/mcp:arg
- mcp:resource — 资源定义，支持 :uri: :mime-type: 选项，body 为资源内容
- mcp:prompt  — 提示模板定义，内含 mcp:param/mcp:arg，body 为模板文本
- mcp:param   — 工具/提示的参数定义
- mcp:arg     — mcp:param 的别名（提示参数语义更清晰）
"""

from .constants import HAS_MDIT
from .models import (
    McpParam,
    McpTool,
    McpResource,
    McpPrompt,
    McpServer,
)
from .parser import parse_myst_mcp
from .utils import (
    parse_file,
    parse_string,
    py_type,
    json_schema_type,
    cast_value,
    build_input_schema,
)

__all__ = [
    "HAS_MDIT",
    "McpParam",
    "McpTool",
    "McpResource",
    "McpPrompt",
    "McpServer",
    "parse_myst_mcp",
    "parse_file",
    "parse_string",
    "py_type",
    "json_schema_type",
    "cast_value",
    "build_input_schema",
]
