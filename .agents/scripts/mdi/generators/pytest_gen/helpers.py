from __future__ import annotations

import logging
from typing import Any

from mdi.models import Interface, Parameter
from mdi.generators.utils import sanitize_identifier
from mdi.mock_data import generate_mock_value, generate_edge_value

logger = logging.getLogger(__name__)


def py_repr(val: object) -> str:
    if val is None:
        return "None"
    if isinstance(val, bool):
        return "True" if val else "False"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        escaped = val.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        return f'"{escaped}"'
    if isinstance(val, list):
        return "[" + ", ".join(py_repr(v) for v in val) + "]"
    if isinstance(val, dict):
        items = ", ".join(
            f"{py_repr(k)}: {py_repr(v)}"
            for k, v in val.items()
        )
        return "{" + items + "}"
    return repr(val)


def var_name(name: str) -> str:
    return sanitize_identifier(name).replace("-", "_")


def func_prefix(iface: Interface) -> str:
    method = iface.method.lower()
    name = sanitize_identifier(iface.name or iface.path).replace("-", "_")
    if name.startswith("_"):
        name = name[1:]
    return f"{method}_{name}"


def code_for_method(method: str) -> int:
    m = method.upper()
    if m == "POST":
        return 201
    if m == "DELETE":
        return 204
    return 200


def success_code(iface: Interface) -> int:
    for r in iface.responses:
        code = int(r.status_code)
        if 200 <= code < 300:
            return code
    return code_for_method(iface.method)


def sample_value(param: Parameter) -> str:
    val = generate_mock_value(param)
    return py_repr(val)


def edge_value(param: Parameter, edge_type: str) -> str:
    val = generate_edge_value(param, edge_type)
    return py_repr(val)


def build_fstring_url(path: str, path_params: list[Parameter], override: dict[str, str]) -> str:
    result = path
    for p in path_params:
        var = var_name(p.name)
        placeholder = "{" + p.name + "}"
        if p.name in override:
            val = override[p.name]
            raw = val.strip('"') if val.startswith('"') and val.endswith('"') else val
            result = result.replace(placeholder, raw)
        else:
            result = result.replace(placeholder, "{" + var + "}")
    return result


def example_to_override(req_example: dict[str, Any], ctx, known_names: set[str]) -> dict[str, str]:
    override: dict[str, str] = {}
    matched: list[str] = []
    extra: list[str] = []
    for key, val in req_example.items():
        if key in known_names:
            override[key] = py_repr(val)
            matched.append(key)
        else:
            override[f"__extra_body__{key}"] = py_repr(val)
            extra.append(key)
    logger.debug(
        "[pytest-gen] _example_to_override %s %s: matched_known=%s, extra_body=%s, known_params=%s",
        ctx.method, ctx.path, matched, extra, sorted(known_names),
    )
    return override


def response_assertions(indent: str, expected: Any, actual_expr: str, depth: int = 0) -> list[str]:
    lines: list[str] = []
    prefix = indent
    if isinstance(expected, dict):
        keys = list(expected.keys())
        logger.debug(
            "[pytest-gen] _response_assertions depth=%d expr=%s type=dict keys=%s",
            depth, actual_expr, keys,
        )
        for key in expected.keys():
            if depth == 0:
                lines.append(f"{prefix}assert {repr(key)} in {actual_expr}")
            elif depth <= 2:
                child_key = f"{actual_expr}[{repr(key)}]"
                child_val = expected[key]
                if isinstance(child_val, dict):
                    lines.append(f"{prefix}assert isinstance({child_key}, dict)")
                elif isinstance(child_val, list):
                    lines.append(f"{prefix}assert isinstance({child_key}, list)")
                elif isinstance(child_val, (str, int, float, bool)) or child_val is None:
                    pass
    elif isinstance(expected, list):
        logger.debug(
            "[pytest-gen] _response_assertions depth=%d expr=%s type=list len=%d",
            depth, actual_expr, len(expected),
        )
        lines.append(f"{prefix}assert isinstance({actual_expr}, list)")
    else:
        logger.debug(
            "[pytest-gen] _response_assertions depth=%d expr=%s type=%s value=%r",
            depth, actual_expr, type(expected).__name__, expected,
        )
    return lines
