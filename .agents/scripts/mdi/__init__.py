"""mdi — Markdown Interface 文档解析与代码生成工具包。

提供 MDI 文档的解析、验证、代码生成能力。
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mdi.models import (
    MDIDocument,
    Interface,
    Parameter,
    Response,
    ErrorCode,
    CodeBlock,
    CheckItem,
    DecisionNode,
    Section,
    Warning,
)
from mdi.parser import MDIParser
from mdi.validator import MDIValidator, ValidationReport
from mdi.generator import MDIGenerator
from mdi.generators import (
    BaseGenerator,
    PythonGenerator,
    TypeScriptGenerator,
    OpenAPIGenerator,
    MCPGenerator,
    MarkdownGenerator,
    CLIGenerator,
)

__all__ = [
    "MDIDocument",
    "Interface",
    "Parameter",
    "Response",
    "ErrorCode",
    "CodeBlock",
    "CheckItem",
    "DecisionNode",
    "Section",
    "Warning",
    "MDIParser",
    "MDIValidator",
    "ValidationReport",
    "MDIGenerator",
    "BaseGenerator",
    "PythonGenerator",
    "TypeScriptGenerator",
    "OpenAPIGenerator",
    "MCPGenerator",
    "MarkdownGenerator",
    "CLIGenerator",
]
