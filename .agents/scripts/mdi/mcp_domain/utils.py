"""MCP Domain 工具函数和公共API。
STATUS: UNVERIFIED - 未经实战验证，参考pytest_gen/mdi.parser使用
"""

from __future__ import annotations

import json as _json
from pathlib import Path
from typing import Any

from .constants import _JSON_SCHEMA_TYPE_MAP, _PY_TYPE_MAP
from .models import McpTool
from .parser import parse_myst_mcp


def _parse_array_type(type_str: str) -> tuple[str, str | None]:
    """解析 array[...] / array<...> 语法，返回 (base_type, inner_type)。"""
    type_str = type_str.strip().lower()
    for open_ch, close_ch in (("[", "]"), ("<", ">")):
        if open_ch in type_str and type_str.endswith(close_ch):
            idx = type_str.index(open_ch)
            base = type_str[:idx].strip()
            inner = type_str[idx + 1:-1].strip()
            return base, inner
    return type_str, None


def _json_schema_type(type_str: str) -> dict[str, Any]:
    """内部：将类型字符串映射为 JSON Schema 片段（返回副本避免污染）。"""
    base, inner = _parse_array_type(type_str)
    if base == "array" or base.startswith("list"):
        inner_schema = _json_schema_type(inner or "string")
        return {"type": "array", "items": inner_schema}
    return dict(_JSON_SCHEMA_TYPE_MAP.get(base, {"type": "string"}))


def py_type(type_str: str) -> type:
    """将 MCP 类型字符串映射为 Python 类型。"""
    base, _ = _parse_array_type(type_str)
    if base == "array" or base.startswith("list"):
        return list
    return _PY_TYPE_MAP.get(base, str)


def json_schema_type(type_str: str) -> dict[str, Any]:
    """将类型字符串映射为 JSON Schema 片段。"""
    return _json_schema_type(type_str)


def cast_value(val: Any, type_str: str) -> Any:
    """将字符串值转换为对应 Python 类型。"""
    if val is None:
        return None
    base, inner = _parse_array_type(type_str)
    if isinstance(val, str):
        t = py_type(base)
        try:
            if t is bool:
                return val.lower() in ("true", "1", "yes")
            if t is list:
                if val.startswith("["):
                    return _json.loads(val)
                return [x.strip() for x in val.split(",")]
            return t(val)
        except (ValueError, TypeError, _json.JSONDecodeError):
            return val
    return val


def build_input_schema(tool: McpTool) -> dict[str, Any]:
    """将 McpTool.params 转换为 MCP JSON Schema。"""
    properties: dict[str, Any] = {}
    required: list[str] = []

    for p in tool.params:
        prop = _json_schema_type(p.type)
        if p.description:
            prop["description"] = p.description
        if p.default is not None:
            prop["default"] = cast_value(p.default, p.type)
        if p.enum:
            prop["enum"] = list(p.enum)
        properties[p.name] = prop
        if p.required:
            required.append(p.name)

    schema: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema


def parse_file(path: str | Path):
    """从 MyST 文件解析 MCP Server 定义。"""
    p = Path(path)
    content = p.read_text(encoding="utf-8")
    return parse_myst_mcp(content, p)


def parse_string(text: str, source: str | Path | None = None):
    """从 MyST 文本字符串解析 MCP Server 定义。"""
    src = Path(source) if source else None
    return parse_myst_mcp(text, src)
