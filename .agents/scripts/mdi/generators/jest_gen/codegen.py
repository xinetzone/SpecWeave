from __future__ import annotations

import logging
from typing import Callable

from mdi.models import Interface
from mdi.generators.utils import sanitize_identifier
from mdi.mock_data import generate_mock_value

from .context import _TestContext

logger = logging.getLogger(__name__)


def js_repr(val: object) -> str:
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        escaped = val.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        return f"'{escaped}'"
    if isinstance(val, list):
        return "[" + ", ".join(js_repr(v) for v in val) + "]"
    if isinstance(val, dict):
        items = ", ".join(
            f"{js_repr(k)}: {js_repr(v)}"
            for k, v in val.items()
        )
        return "{" + items + "}"
    return repr(val)


def func_prefix(iface: Interface) -> str:
    method = iface.method.lower()
    name = sanitize_identifier(iface.name or iface.path).replace("-", "_")
    if name.startswith("_"):
        name = name[1:]
    return f"{method}_{name}"


def var_name(name: str) -> str:
    return sanitize_identifier(name).replace("-", "_")


def success_code(iface: Interface) -> int:
    for r in iface.responses:
        code = int(r.status_code)
        if 200 <= code < 300:
            return code
    m = iface.method.upper()
    if m == "POST":
        return 201
    if m == "DELETE":
        return 204
    return 200


def build_url_and_args(
    ctx: _TestContext,
    override: dict[str, object],
    skip: set[str],
    js_repr_func: Callable[[object], str] = js_repr,
) -> tuple[str, str, str]:
    path_values: dict[str, object] = {}
    query_obj: dict[str, object] = {}
    body_obj: dict[str, object] = {}

    for p in ctx.path_params:
        val = override.get(p.name, generate_mock_value(p))
        path_values[p.name] = val

    url = ctx.path
    for name, val in path_values.items():
        url = url.replace("{" + name + "}", str(val))

    for p in ctx.query_params:
        if p.name in skip:
            continue
        val = override.get(p.name, generate_mock_value(p))
        query_obj[p.name] = val

    has_body = ctx.method not in ("GET", "DELETE", "HEAD")
    extra_body_items = {k[len("__extra_body__"):]: v for k, v in override.items() if k.startswith("__extra_body__")}
    if has_body:
        for p in ctx.body_params:
            if p.name in skip:
                continue
            if not p.required and p.name not in override:
                continue
            val = override.get(p.name, generate_mock_value(p))
            body_obj[p.name] = val
        for extra_key, extra_val in extra_body_items.items():
            body_obj[extra_key] = extra_val

    query_js = js_repr_func(query_obj) if query_obj else "undefined"
    body_js = js_repr_func(body_obj) if body_obj else "undefined"
    return url, query_js, body_js


def request_line(method: str, url_expr: str, query_expr: str, body_expr: str) -> str:
    m = method.lower()
    has_query = bool(query_expr) and query_expr.strip() not in ("undefined", "null", "''", '""')
    has_body = bool(body_expr) and body_expr.strip() not in ("undefined", "null", "''", '""')
    if m in ("get", "delete", "head", "options"):
        if has_query:
            return f"    const response = await apiClient.{m}({url_expr}, {{ params: {query_expr} }});"
        else:
            return f"    const response = await apiClient.{m}({url_expr});"
    else:
        if has_query and has_body:
            return f"    const response = await apiClient.{m}({url_expr}, {body_expr}, {{ params: {query_expr} }});"
        elif has_body:
            return f"    const response = await apiClient.{m}({url_expr}, {body_expr});"
        elif has_query:
            return f"    const response = await apiClient.{m}({url_expr}, {{}}, {{ params: {query_expr} }});"
        else:
            return f"    const response = await apiClient.{m}({url_expr});"


def example_to_override(req_example: dict[str, object], ctx: _TestContext) -> dict[str, object]:
    """将request example数据转换为build_url_and_args可用的override字典。

    已知参数直接覆盖；额外字段通过__extra_body__前缀传递给body。
    值保留为Python原生类型，由js_repr统一序列化。
    """
    override: dict[str, object] = {}
    known_names = {p.name for p in ctx.path_params + ctx.query_params + ctx.body_params}
    matched: list[str] = []
    extra: list[str] = []
    for key, val in req_example.items():
        if key in known_names:
            override[key] = val
            matched.append(key)
        else:
            override[f"__extra_body__{key}"] = val
            extra.append(key)
    logger.debug(
        "[jest-gen] example_to_override %s %s: matched_known=%s, extra_body=%s, known_params=%s",
        ctx.method, ctx.path, matched, extra, sorted(known_names),
    )
    return override
