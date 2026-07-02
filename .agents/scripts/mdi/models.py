"""MDI (Markdown Interface) 核心数据模型。

定义 MDI 文档解析过程中使用的所有数据类。
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CodeBlock:
    """代码块数据结构。"""
    language: str
    meta: str
    content: str
    purpose: str


@dataclass
class Warning:
    """警告信息。"""
    message: str
    line: int
    severity: str


@dataclass
class CheckItem:
    """检查清单项。"""
    text: str
    checked: bool
    line: int


@dataclass
class DecisionNode:
    """决策节点（用于流程图）。"""
    id: str
    label: str
    edges: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class Section:
    """文档章节。"""
    level: int
    title: str
    content: str = ""
    subsections: list["Section"] = field(default_factory=list)
    tables: list[dict[str, Any]] = field(default_factory=list)
    code_blocks: list[CodeBlock] = field(default_factory=list)
    lists: list[Any] = field(default_factory=list)


@dataclass
class Parameter:
    """接口参数。"""
    name: str
    type: str
    required: bool
    description: str
    default: str | None = None
    location: str = "body"


@dataclass
class Response:
    """接口响应。"""
    status_code: str | int
    description: str
    schema: dict[str, Any] | None = None
    example: CodeBlock | None = None


@dataclass
class ErrorCode:
    """错误码定义。"""
    code: str | int
    description: str
    message: str


@dataclass
class Interface:
    """API 接口定义。"""
    name: str
    method: str
    path: str
    summary: str = ""
    description: str = ""
    parameters: list[Parameter] = field(default_factory=list)
    request_body: Parameter | None = None
    responses: list[Response] = field(default_factory=list)
    errors: list[ErrorCode] = field(default_factory=list)
    examples: list[CodeBlock] = field(default_factory=list)
    check_items: list[CheckItem] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class MDIDocument:
    """MDI 文档根对象。"""
    frontmatter: dict[str, Any] = field(default_factory=dict)
    title: str = ""
    description: str = ""
    sections: list[Section] = field(default_factory=list)
    interfaces: list[Interface] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_path: Path | None = None
