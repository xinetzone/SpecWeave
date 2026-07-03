"""Jest测试场景生成器 - 成功/缺失参数/无效参数/错误码等测试用例。
STATUS: UNVERIFIED - 未经实战验证，参考pytest_gen/mdi.parser使用
"""

from __future__ import annotations

import logging
import re
from typing import Callable

from mdi.mock_data import generate_edge_value
from mdi.example_extractor import get_request_example, get_response_example, get_js_assertions
from mdi.checklist_converter import get_checklist_assertions

from .context import _TestContext
from .codegen import (
    build_url_and_args,
    request_line,
    example_to_override,
    success_code as get_success_code,
    var_name as make_var_name,
)
from .assertions import js_response_assertions, py_to_js_assertions

logger = logging.getLogger(__name__)


def test_success(
    ctx: _TestContext,
    prefix: str,
    js_repr_func: Callable[[object], str],
) -> list[str]:
    indent = "  "
    sc = get_success_code(ctx.iface)
    request_example = get_request_example(ctx.iface) if ctx.iface else None
    response_example = get_response_example(ctx.iface, sc) if ctx.iface else None
    override_req = example_to_override(request_example, ctx) if request_example else {}

    logger.debug(
        "[jest-gen] test_success %s %s: success_code=%d, has_request_example=%s, "
        "has_response_example=%s",
        ctx.method, ctx.path, sc,
        request_example is not None, response_example is not None,
    )
    logger.debug(
        "[jest-gen] test_success override: known_params=%s, extra_body=%s",
        sorted(k for k in override_req if not k.startswith("__extra_body__")),
        sorted(k[len("__extra_body__"):] for k in override_req if k.startswith("__extra_body__")),
    )

    url, qs, body = build_url_and_args(ctx, override_req, set(), js_repr_func)

    lines = [
        f"{indent}test('{prefix}_success', async () => {{",
        f"{indent}  // 正常场景：请求成功返回{sc}",
        f"{indent}  const url = '{url}';",
        request_line(ctx.method, "url", qs, body),
        f"{indent}  expect(response.status).toBe({sc});",
    ]

    need_parse = response_example is not None or (ctx.iface and bool(get_checklist_assertions(ctx.iface)))
    if need_parse:
        lines.append(f"{indent}  const data = response.data;")

    if response_example is not None:
        top_keys = list(response_example.keys()) if isinstance(response_example, dict) else None
        logger.debug(
            "[jest-gen] test_success 添加响应示例断言: top_keys=%s",
            top_keys,
        )
        lines.extend(js_response_assertions(indent + "  ", response_example, "data", js_repr_func))

    if ctx.iface:
        py_checklist = get_checklist_assertions(ctx.iface)
        if py_checklist:
            logger.debug(
                "[jest-gen] test_success 添加检查清单断言: %d条Python断言待转换",
                len(py_checklist),
            )
            lines.append(f"{indent}  // === 来自文档检查清单的断言 ===")
            lines.extend(py_to_js_assertions(indent + "  ", py_checklist, js_repr_func))

    lines.append(f"{indent}}});")
    lines.append("")
    return lines


def test_missing_required(
    ctx: _TestContext,
    prefix: str,
    js_repr_func: Callable[[object], str],
) -> list[str]:
    indent = "  "
    lines: list[str] = []
    required_body = [p for p in ctx.body_params if p.required]
    required_query = [p for p in ctx.query_params if p.required]

    for miss_p in required_body + required_query:
        safe_name = make_var_name(miss_p.name)
        loc_desc = "body" if miss_p in required_body else "query"
        url, qs, body = build_url_and_args(ctx, {}, {miss_p.name}, js_repr_func)
        lines.append(f"{indent}test('{prefix}_missing_{safe_name}', async () => {{")
        lines.append(f"{indent}  // 错误场景：缺少必填参数{miss_p.name}（{loc_desc}），期望400")
        lines.append(f"{indent}  const url = '{url}';")
        lines.append(request_line(ctx.method, "url", qs, body))
        lines.append(f"{indent}  expect(response.status).toBe(400);")
        lines.append(f"{indent}}});")
        lines.append("")

    return lines


def test_invalid_params(
    ctx: _TestContext,
    prefix: str,
    js_repr_func: Callable[[object], str],
) -> list[str]:
    indent = "  "
    lines: list[str] = []
    str_required = [p for p in ctx.all_required if (p.type or "string").lower() in ("string", "str", "")]
    int_required = [p for p in ctx.all_required if (p.type or "").lower() in ("integer", "int")]

    for p in str_required:
        safe_name = make_var_name(p.name)
        url, qs, body = build_url_and_args(ctx, {p.name: generate_edge_value(p, "empty")}, set(), js_repr_func)
        lines.append(f"{indent}test('{prefix}_empty_{safe_name}', async () => {{")
        lines.append(f"{indent}  // 边界值：{p.name}为空字符串，期望400")
        lines.append(f"{indent}  const url = '{url}';")
        lines.append(request_line(ctx.method, "url", qs, body))
        lines.append(f"{indent}  expect(response.status).toBe(400);")
        lines.append(f"{indent}}});")
        lines.append("")

    for p in int_required:
        safe_name = make_var_name(p.name)
        url, qs, body = build_url_and_args(ctx, {p.name: generate_edge_value(p, "negative")}, set(), js_repr_func)
        lines.append(f"{indent}test('{prefix}_negative_{safe_name}', async () => {{")
        lines.append(f"{indent}  // 边界值：{p.name}为负数，期望400")
        lines.append(f"{indent}  const url = '{url}';")
        lines.append(request_line(ctx.method, "url", qs, body))
        lines.append(f"{indent}  expect(response.status).toBe(400);")
        lines.append(f"{indent}}});")
        lines.append("")

    return lines


def test_error_codes(
    ctx: _TestContext,
    prefix: str,
    js_repr_func: Callable[[object], str],
) -> list[str]:
    indent = "  "
    lines: list[str] = []

    for err in ctx.iface.errors:
        err_code = int(err.code)
        if err_code == 400:
            continue
        err_msg = make_var_name(str(err.message)) if err.message else f"err_{err_code}"
        desc = err.description or err.message or f"错误码{err_code}"
        url, qs, body = build_url_and_args(ctx, {}, set(), js_repr_func)
        lines.append(f"{indent}test('{prefix}_{err_msg}', async () => {{")
        lines.append(f"{indent}  // TODO: 构造触发{err.code} {err.message}的请求数据")
        lines.append(f"{indent}  // 错误场景：{desc}（{err_code}）")
        lines.append(f"{indent}  const url = '{url}';")
        lines.append(request_line(ctx.method, "url", qs, body))
        lines.append(f"{indent}  expect(response.status).toBe({err_code});")
        lines.append(f"{indent}}});")
        lines.append("")

    return lines


def test_fallback(
    ctx: _TestContext,
    prefix: str,
    current_count: int,
    js_repr_func: Callable[[object], str],
) -> list[str]:
    """为测试用例不足3个的最小接口添加回退测试（Jest版本）。"""
    indent = "  "
    lines: list[str] = []
    needed = 3 - current_count
    sc = get_success_code(ctx.iface)

    has_boundary = False
    has_error = False
    for ln in (
        test_missing_required(ctx, prefix, js_repr_func)
        + test_invalid_params(ctx, prefix, js_repr_func)
        + test_error_codes(ctx, prefix, js_repr_func)
    ):
        m = re.match(r"\s*test\('([^']+)'", ln)
        if m:
            name = m.group(1)
            if "_empty_" in name or "_negative_" in name or "_missing_" in name:
                has_boundary = True
            elif "_err_" in name or any(f"_{c}" in name for c in ["401", "403", "404", "409", "422", "500"]):
                has_error = True

    if needed > 0 and not has_boundary:
        url, qs, body = build_url_and_args(ctx, {}, set(), js_repr_func)
        if ctx.method in ("POST", "PUT", "PATCH"):
            lines.append(f"{indent}test('{prefix}_empty_body', async () => {{")
            lines.append(f"{indent}  // 边界场景：空请求体，期望400")
            lines.append(f"{indent}  const url = '{url}';")
            lines.append(f"{indent}  const response = await apiClient.{ctx.method.lower()}(url, {{}});")
            lines.append(f"{indent}  expect([400, 422]).toContain(response.status);")
            lines.append(f"{indent}}});")
            lines.append("")
        else:
            lines.append(f"{indent}test('{prefix}_unexpected_params', async () => {{")
            lines.append(f"{indent}  // 边界场景：携带未定义的查询参数，服务端应忽略")
            lines.append(f"{indent}  const url = '{url}';")
            lines.append(f"{indent}  const response = await apiClient.{ctx.method.lower()}(url, {{ params: {{ '_unexpected': 'value' }} }});")
            lines.append(f"{indent}  expect(response.status).toBe({sc});")
            lines.append(f"{indent}}});")
            lines.append("")
        needed -= 1

    if needed > 0 and not has_error:
        url, _, _ = build_url_and_args(ctx, {}, set(), js_repr_func)
        lines.append(f"{indent}test('{prefix}_error_todo', async () => {{")
        lines.append(f"{indent}  // 错误场景：TODO 请根据API实际错误场景补充测试")
        lines.append(f"{indent}  // 例如：未认证返回401、权限不足返回403、资源不存在返回404等")
        lines.append(f"{indent}  const url = '{url}';")
        lines.append(f"{indent}  const response = await apiClient.{ctx.method.lower()}(url);")
        lines.append(f"{indent}  expect(response.status).toBeGreaterThanOrEqual(400);")
        lines.append(f"{indent}}});")
        lines.append("")
        needed -= 1

    return lines


def test_js_examples(
    ctx: _TestContext,
    prefix: str,
    js_repr_func: Callable[[object], str],
) -> list[str]:
    """从文档中的js/ts example代码块生成Jest测试用例。"""
    indent = "  "
    lines: list[str] = []
    assertions = get_js_assertions(ctx.iface) if ctx.iface else []
    logger.debug(
        "[jest-gen] test_js_examples %s %s: 找到%d个js/ts example代码块",
        ctx.method, ctx.path, len(assertions),
    )
    for i, snippet in enumerate(assertions):
        suffix = f"_example_{i + 1}" if i > 0 else "_example"
        lines.append(f"{indent}test('{prefix}{suffix}', async () => {{")
        lines.append(f"{indent}  // === 来自文档 ```js/ts example 代码块 ===")
        snippet_lines = snippet.splitlines()
        if not snippet_lines:
            logger.warning(
                "[jest-gen] test_js_examples %s %s: snippet %d为空",
                ctx.method, ctx.path, i,
            )
            lines.append(f"{indent}  // TODO: 示例代码为空")
        else:
            logger.debug(
                "[jest-gen] test_js_examples %s %s: snippet %d包含%d行代码",
                ctx.method, ctx.path, i, len(snippet_lines),
            )
            for sl in snippet_lines:
                lines.append(f"{indent}  {sl}")
        lines.append(f"{indent}}});")
        lines.append("")
    return lines
