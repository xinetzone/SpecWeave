"""Mock 数据生成器。

根据 Parameter 类型/名称推断并生成符合 Schema 的随机测试数据，
供 pytest/jest 等测试生成器使用，替换硬编码占位值。

设计原则：
- 确定性：同一输入多次调用返回相同值（基于参数名hash），方便测试复现
- 语义化：根据参数名（email/id/name/url等）生成符合语义的数据，提高可读性
- 类型安全：严格按照 type 字段生成对应类型的值
"""

from __future__ import annotations

import hashlib
import random
from typing import Any

from .models import Parameter

_NAME_PATTERNS: dict[str, Any] = {
    "email": "user_{seed}@example.com",
    "email_address": "user_{seed}@example.com",
    "mail": "user_{seed}@example.com",
    "user_id": "usr_{seed}",
    "id": "data_{seed}",
    "uuid": "550e8400-e29b-41d4-a716-{seed:012d}",
    "name": "Test Name {seed}",
    "username": "testuser_{seed}",
    "first_name": "First{seed}",
    "last_name": "Last{seed}",
    "full_name": "Test User {seed}",
    "phone": "138{seed:08d}",
    "mobile": "139{seed:08d}",
    "tel": "010-{seed:08d}",
    "address": "No.{seed} Test Street",
    "city": "City{seed}",
    "country": "CN",
    "url": "https://example.com/resource/{seed}",
    "website": "https://example{seed}.com",
    "avatar": "https://example.com/avatar/{seed}.png",
    "password": "TestPass{seed}!@",
    "title": "Title {seed}",
    "description": "This is a test description item {seed} for automated testing.",
    "content": "Sample content body {seed} with enough length to look realistic.",
    "keyword": "test{seed}",
    "query": "search term {seed}",
    "token": "tok_{seed:024x}",
    "api_key": "ak_{seed:024x}",
    "page": 1,
    "page_size": 20,
    "limit": 10,
    "offset": 0,
    "status": "active",
    "role": "user",
    "locale": "zh-CN",
    "language": "zh-CN",
    "timezone": "Asia/Shanghai",
    "version": "v1.0.0",
    "sort": "created_at",
    "order": "desc",
    "format": "json",
}


def _seed_for(name: str) -> int:
    """根据参数名生成确定性seed（0~99999范围）。"""
    h = hashlib.md5(name.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % 100000


def generate_mock_value(param: Parameter) -> Any:
    """为单个参数生成符合其类型/名称语义的 mock 值。

    规则：
    1. 如果有 default 值，优先使用 default（按类型转换）
    2. 根据参数名匹配语义模式（email/id/name等）生成更真实的数据
    3. 兜底按类型生成默认值
    """
    tl = (param.type or "string").lower().strip()
    name_lower = param.name.lower().strip()

    if param.default is not None:
        return _convert_default(param.default, tl)

    seed = _seed_for(param.name)

    if tl in ("boolean", "bool"):
        for k in ("is_", "has_", "enable", "active", "deleted", "verified"):
            if k in name_lower:
                return True
        return bool(seed % 2)

    if tl in ("integer", "int"):
        if "page" == name_lower:
            return 1
        if "page_size" in name_lower or "pagesize" in name_lower or "per_page" in name_lower:
            return 20
        if "limit" in name_lower:
            return 10
        if "offset" in name_lower or "skip" in name_lower:
            return 0
        if "age" in name_lower:
            return 20 + (seed % 40)
        if "port" in name_lower:
            return 8000 + (seed % 1000)
        if "status" in name_lower or "state" in name_lower:
            return seed % 3
        return (seed % 100) + 1

    if tl in ("number", "float", "double"):
        if "price" in name_lower or "amount" in name_lower or "cost" in name_lower:
            return round((seed % 10000) / 100.0 + 0.99, 2)
        if "rate" in name_lower or "ratio" in name_lower:
            return round((seed % 100) / 100.0, 2)
        if "score" in name_lower or "rating" in name_lower:
            return round((seed % 50) / 10.0, 1)
        return round(seed / 100.0, 2)

    if tl in ("string", "str", ""):
        for pattern_name, template in _NAME_PATTERNS.items():
            if name_lower == pattern_name or name_lower.endswith("_" + pattern_name):
                if isinstance(template, str):
                    try:
                        return template.format(seed=seed)
                    except (ValueError, IndexError, KeyError):
                        return template.replace("{seed}", str(seed))
                return template

        if "date" in name_lower or "time" in name_lower and "timestamp" not in name_lower:
            return f"2024-0{(seed % 9) + 1}-{10 + (seed % 20):02d}T08:00:00Z"
        if "timestamp" in name_lower:
            return 1700000000 + seed

        if name_lower.endswith("_id") or name_lower == "id":
            prefix = name_lower.replace("_id", "") or "item"
            prefix = prefix[:3] if len(prefix) > 3 else prefix
            return f"{prefix}_{seed:05d}"

        return f"test_{param.name}_{seed}"

    if tl in ("array", "list"):
        return []

    if tl in ("object", "dict", "map"):
        return {}

    if tl in ("null",):
        return None

    return f"test_{param.name}_{seed}"


def generate_mock_values(params: list[Parameter]) -> dict[str, Any]:
    """批量生成参数mock值，返回 {param_name: value} 字典。"""
    return {p.name: generate_mock_value(p) for p in params}


def generate_mock_body(params: list[Parameter]) -> dict[str, Any]:
    """生成 body 参数的 mock 对象（仅包含 body location 的参数）。"""
    return {
        p.name: generate_mock_value(p)
        for p in params
        if p.location == "body"
    }


def generate_mock_query(params: list[Parameter]) -> dict[str, Any]:
    """生成 query 参数的 mock 对象（仅包含 query location 的参数）。"""
    return {
        p.name: generate_mock_value(p)
        for p in params
        if p.location == "query"
    }


def generate_mock_path(params: list[Parameter]) -> dict[str, Any]:
    """生成 path 参数的 mock 值映射。"""
    return {
        p.name: generate_mock_value(p)
        for p in params
        if p.location == "path"
    }


def generate_edge_value(param: Parameter, edge_type: str) -> Any:
    """为边界值测试生成特定边界值。

    edge_type:
      - "empty": 空字符串 / 0 / 空数组
      - "too_long": 超长字符串（1000字符）
      - "negative": 负数（int/float）
      - "null": None值
      - "invalid_type": 类型错误的值（如int字段传string）
    """
    tl = (param.type or "string").lower().strip()

    if edge_type == "empty":
        if tl in ("string", "str", ""):
            return ""
        if tl in ("integer", "int", "number", "float"):
            return 0
        if tl in ("boolean", "bool"):
            return False
        if tl in ("array", "list"):
            return []
        if tl in ("object", "dict"):
            return {}
        return None

    if edge_type == "too_long":
        return "a" * 1000

    if edge_type == "negative":
        if tl in ("integer", "int"):
            return -1
        if tl in ("number", "float"):
            return -1.0
        return "-1"

    if edge_type == "null":
        return None

    if edge_type == "invalid_type":
        if tl in ("integer", "int", "number", "float"):
            return "not_a_number"
        if tl in ("boolean", "bool"):
            return "not_a_bool"
        if tl in ("array", "list"):
            return "not_an_array"
        return 12345

    return generate_mock_value(param)


def _convert_default(default: str, tl: str) -> Any:
    """将字符串形式的default值转换为对应Python类型。"""
    d = default.strip().strip('"\'')
    if tl in ("boolean", "bool"):
        return d.lower() in ("true", "yes", "1", "on")
    if tl in ("integer", "int"):
        try:
            return int(d)
        except ValueError:
            return d
    if tl in ("number", "float"):
        try:
            return float(d)
        except ValueError:
            return d
    if tl in ("null",):
        return None
    return d
