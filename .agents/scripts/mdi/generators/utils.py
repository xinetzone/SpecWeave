"""MDI代码生成工具函数。

提供类型映射、命名转换等通用工具函数。
"""

from __future__ import annotations

import re
from typing import Any


def snake_to_pascal(name: str) -> str:
    """将snake_case转换为PascalCase。

    Examples:
        >>> snake_to_pascal("user_id")
        'UserId'
        >>> snake_to_pascal("create_user")
        'CreateUser'
        >>> snake_to_pascal("hello_world_test")
        'HelloWorldTest'
    """
    if not name:
        return name
    parts = re.split(r"[_\-\s]+", name)
    return "".join(p.capitalize() for p in parts if p)


def snake_to_camel(name: str) -> str:
    """将snake_case转换为camelCase。

    Examples:
        >>> snake_to_camel("user_id")
        'userId'
        >>> snake_to_camel("create_user")
        'createUser'
    """
    if not name:
        return name
    pascal = snake_to_pascal(name)
    return pascal[0].lower() + pascal[1:] if pascal else ""


def kebab_to_snake(name: str) -> str:
    """将kebab-case转换为snake_case。

    Examples:
        >>> kebab_to_snake("link-check-cmd")
        'link_check_cmd'
    """
    return name.replace("-", "_")


def sanitize_identifier(name: str) -> str:
    """将名称转换为有效的Python标识符。

    Examples:
        >>> sanitize_identifier("user-id")
        'user_id'
        >>> sanitize_identifier("123abc")
        '_123abc'
    """
    result = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if result and result[0].isdigit():
        result = "_" + result
    return result


PYTHON_TYPE_MAP: dict[str, str] = {
    "string": "str",
    "str": "str",
    "integer": "int",
    "int": "int",
    "number": "float",
    "float": "float",
    "boolean": "bool",
    "bool": "bool",
    "array": "list",
    "list": "list",
    "object": "dict",
    "dict": "dict",
    "any": "Any",
    "": "Any",
}

TYPESCRIPT_TYPE_MAP: dict[str, str] = {
    "string": "string",
    "str": "string",
    "integer": "number",
    "int": "number",
    "number": "number",
    "float": "number",
    "boolean": "boolean",
    "bool": "boolean",
    "array": "any[]",
    "list": "any[]",
    "object": "Record<string, any>",
    "dict": "Record<string, any>",
    "any": "any",
    "": "any",
}

JSON_SCHEMA_TYPE_MAP: dict[str, str] = {
    "string": "string",
    "str": "string",
    "integer": "integer",
    "int": "integer",
    "number": "number",
    "float": "number",
    "boolean": "boolean",
    "bool": "boolean",
    "array": "array",
    "list": "array",
    "object": "object",
    "dict": "object",
    "any": "object",
    "": "object",
}


def map_python_type(type_str: str | None) -> str:
    """将MDI类型映射为Python类型。"""
    if not type_str:
        return "Any"
    type_lower = type_str.lower().strip()

    if "|" in type_lower or "union" in type_lower:
        parts = re.split(r"\s*\|\s*|,\s*", type_lower)
        mapped = [map_python_type(p) for p in parts if p.strip()]
        return f"Union[{', '.join(mapped)}]"

    if "optional" in type_lower or "?" in type_str:
        inner = type_lower.replace("optional", "").replace("?", "").strip()
        return f"Optional[{map_python_type(inner)}]"

    if type_lower.startswith("array[") or type_lower.startswith("list["):
        match = re.search(r"[\[<](.+)[\]>]", type_str)
        if match:
            inner = map_python_type(match.group(1))
            return f"list[{inner}]"
        return "list"

    if type_lower.startswith("dict[") or type_lower.startswith("object["):
        return "dict"

    if type_lower in ("literal",) or "literal[" in type_lower:
        match = re.search(r"literal\[(.+)\]", type_lower)
        if match:
            values = match.group(1)
            return f"Literal[{values}]"
        return "str"

    return PYTHON_TYPE_MAP.get(type_lower, "Any")


def map_typescript_type(type_str: str | None) -> str:
    """将MDI类型映射为TypeScript类型。"""
    if not type_str:
        return "any"
    type_lower = type_str.lower().strip()

    if "|" in type_lower or "union" in type_lower:
        parts = re.split(r"\s*\|\s*|,\s*", type_lower)
        mapped = [map_typescript_type(p) for p in parts if p.strip()]
        return " | ".join(mapped)

    if "optional" in type_lower or "?" in type_str:
        inner = type_lower.replace("optional", "").replace("?", "").strip()
        return f"{map_typescript_type(inner)} | undefined"

    if type_lower.startswith("array[") or type_lower.startswith("list["):
        match = re.search(r"[\[<](.+)[\]>]", type_str)
        if match:
            inner = map_typescript_type(match.group(1))
            return f"{inner}[]"
        return "any[]"

    if type_lower.startswith("dict[") or type_lower.startswith("object["):
        return "Record<string, any>"

    return TYPESCRIPT_TYPE_MAP.get(type_lower, "any")


def map_json_schema_type(type_str: str | None) -> dict[str, Any]:
    """将MDI类型映射为JSON Schema类型定义。"""
    if not type_str:
        return {"type": "object"}
    type_lower = type_str.lower().strip()

    if "|" in type_lower or "union" in type_lower:
        parts = re.split(r"\s*\|\s*|,\s*", type_lower)
        mapped = [map_json_schema_type(p) for p in parts if p.strip()]
        types = []
        for m in mapped:
            if "type" in m:
                types.append(m["type"])
        return {"type": types} if types else {"type": "object"}

    if "optional" in type_lower or "?" in type_str:
        inner = type_lower.replace("optional", "").replace("?", "").strip()
        schema = map_json_schema_type(inner)
        return schema

    if type_lower.startswith("array[") or type_lower.startswith("list["):
        match = re.search(r"[\[<](.+)[\]>]", type_str)
        if match:
            items_schema = map_json_schema_type(match.group(1))
            return {"type": "array", "items": items_schema}
        return {"type": "array"}

    if type_lower.startswith("dict[") or type_lower.startswith("object["):
        return {"type": "object"}

    base_type = JSON_SCHEMA_TYPE_MAP.get(type_lower, "object")
    return {"type": base_type}


def escape_docstring(text: str, indent: str = "    ") -> str:
    """转义并格式化docstring文本。"""
    if not text:
        return ""
    lines = text.strip().split("\n")
    return f"\n{indent}".join(lines)


def to_jsdoc_comment(text: str, indent: str = "    ") -> str:
    """将文本转换为JSDoc注释格式。"""
    if not text:
        return ""
    lines = text.strip().split("\n")
    if len(lines) == 1:
        return f"{indent}/** {lines[0]} */"
    result = [f"{indent}/**"]
    for line in lines:
        result.append(f"{indent} * {line}")
    result.append(f"{indent} */")
    return "\n".join(result)


def make_interface_name(name: str) -> str:
    """从接口名生成类型名（PascalCase）。"""
    cleaned = re.sub(r"[^a-zA-Z0-9_\-\s]", "", name)
    cleaned = cleaned.replace("/", "_")
    return snake_to_pascal(cleaned)
