"""MDI代码生成器子包。

提供多语言代码生成和文档导出能力。
"""

from .base import BaseGenerator
from .python_gen import PythonGenerator
from .typescript_gen import TypeScriptGenerator
from .openapi_gen import OpenAPIGenerator
from .mcp_gen import MCPGenerator
from .markdown_gen import MarkdownGenerator
from .cli_gen import CLIGenerator

__all__ = [
    "BaseGenerator",
    "PythonGenerator",
    "TypeScriptGenerator",
    "OpenAPIGenerator",
    "MCPGenerator",
    "MarkdownGenerator",
    "CLIGenerator",
]

GENERATOR_MAP: dict[str, type[BaseGenerator]] = {
    "python": PythonGenerator,
    "typescript": TypeScriptGenerator,
    "ts": TypeScriptGenerator,
    "openapi": OpenAPIGenerator,
    "mcp": MCPGenerator,
    "markdown": MarkdownGenerator,
    "md": MarkdownGenerator,
    "cli": CLIGenerator,
}
