from __future__ import annotations

import logging

from mdi.example_extractor import (
    get_request_example,
    get_response_example,
    get_python_assertions,
)
from mdi.checklist_converter import get_checklist_assertions

from .context import _TestContext
from . import helpers

logger = logging.getLogger(__name__)


def setup_params(
    indent: str,
    ctx: _TestContext,
    override: dict[str, str],
    skip: set[str],
) -> list[str]:
    lines: list[str] = []

    for p in ctx.path_params:
        var = helpers.var_name(p.name)
        val = override.get(p.name, helpers.sample_value(p))
        lines.append(f"{indent}{var} = {val}")

    url = helpers.build_fstring_url(ctx.path, ctx.path_params, override)
    lines.append(f"{indent}url = f'{{base_url}}{url}'")

    if ctx.query_params:
        lines.append(f"{indent}params = {{")
        for p in ctx.query_params:
            if p.name in skip:
                continue
            val = override.get(p.name, helpers.sample_value(p))
            lines.append(f"{indent}    {repr(p.name)}: {val},")
        lines.append(f"{indent}}}")
    else:
        lines.append(f"{indent}params = None")

    has_body = ctx.method not in ("GET", "DELETE", "HEAD")
    extra_body_items = {k[len("__extra_body__"):]: v for k, v in override.items() if k.startswith("__extra_body__")}
    if has_body and (ctx.body_params or extra_body_items):
        lines.append(f"{indent}json_body = {{")
        for p in ctx.body_params:
            if p.name in skip:
                continue
            if not p.required and p.name not in override:
                continue
            val = override.get(p.name, helpers.sample_value(p))
            lines.append(f"{indent}    {repr(p.name)}: {val},")
        for extra_key, extra_val in extra_body_items.items():
            lines.append(f"{indent}    {repr(extra_key)}: {extra_val},")
        lines.append(f"{indent}}}")
    else:
        lines.append(f"{indent}json_body = None")

    return lines


def test_success(ctx: _TestContext, prefix: str) -> list[str]:
    indent = "    "
    success_code_val = helpers.success_code(ctx.iface)
    request_example = get_request_example(ctx.iface) if ctx.iface else None
    response_example = get_response_example(ctx.iface, success_code_val) if ctx.iface else None

    logger.debug(
        "[pytest-gen] _test_success %s %s: success_code=%d, has_request_example=%s, "
        "has_response_example=%s",
        ctx.method, ctx.path, success_code_val,
        request_example is not None, response_example is not None,
    )

    lines = [
        f"{indent}def test_{prefix}_success(self, api_client, base_url):",
        f'{indent}    """{ctx.summary} - 正常场景：请求成功返回{success_code_val}。"""',
    ]

    known_names = {p.name for p in ctx.path_params + ctx.query_params + ctx.body_params}
    override_req = helpers.example_to_override(request_example, ctx, known_names) if request_example else {}
    logger.debug(
        "[pytest-gen] _test_success override: known_params=%s, extra_body=%s",
        sorted(k for k in override_req if not k.startswith("__extra_body__")),
        sorted(k[len("__extra_body__"):] for k in override_req if k.startswith("__extra_body__")),
    )
    lines.extend(setup_params(indent * 2, ctx, override=override_req, skip=set()))
    lines.append(f"{indent}    ")
    lines.append(f"{indent}    response = api_client.{ctx.method.lower()}(url, params=params, json=json_body)")
    lines.append(f"{indent}    assert response.status_code == {success_code_val}")

    if response_example is not None:
        logger.debug(
            "[pytest-gen] _test_success 添加响应示例断言: %d个顶层字段",
            len(response_example) if isinstance(response_example, dict) else 1,
        )
        lines.append(f"{indent}    data = response.json()")
        lines.extend(helpers.response_assertions(indent + "    ", response_example, "data"))

    if ctx.iface:
        checklist_asserts = get_checklist_assertions(ctx.iface)
        if checklist_asserts:
            logger.debug(
                "[pytest-gen] _test_success 添加检查清单断言: %d条", len(checklist_asserts),
            )
            if response_example is None:
                lines.append(f"{indent}    data = response.json()")
            lines.append(f"{indent}    # === 来自文档检查清单的断言 ===")
            for cl in checklist_asserts:
                lines.append(f"{indent}    {cl}")

    lines.append("")
    return lines


def test_missing_required(ctx: _TestContext, prefix: str) -> list[str]:
    indent = "    "
    lines: list[str] = []
    required_body = [p for p in ctx.body_params if p.required]
    required_query = [p for p in ctx.query_params if p.required]

    for miss_p in required_body + required_query:
        safe_name = helpers.var_name(miss_p.name)
        loc_desc = "body" if miss_p in required_body else "query"
        lines.append(f"{indent}def test_{prefix}_missing_{safe_name}(self, api_client, base_url):")
        lines.append(f'{indent}    """{ctx.summary} - 错误场景：缺少必填参数{miss_p.name}（{loc_desc}），期望400。"""')
        lines.extend(setup_params(indent * 2, ctx, override={}, skip={miss_p.name}))
        lines.append(f"{indent}    ")
        lines.append(f"{indent}    response = api_client.{ctx.method.lower()}(url, params=params, json=json_body)")
        lines.append(f"{indent}    assert response.status_code == 400")
        lines.append("")

    return lines


def test_invalid_params(ctx: _TestContext, prefix: str) -> list[str]:
    indent = "    "
    lines: list[str] = []
    str_required = [p for p in ctx.all_required if p.type in ("string", "str", "")]
    int_required = [p for p in ctx.all_required if p.type in ("integer", "int")]

    for p in str_required:
        safe_name = helpers.var_name(p.name)
        lines.append(f"{indent}def test_{prefix}_empty_{safe_name}(self, api_client, base_url):")
        lines.append(f'{indent}    """{ctx.summary} - 边界值：{p.name}为空字符串，期望400。"""')
        lines.extend(setup_params(indent * 2, ctx, override={p.name: helpers.edge_value(p, "empty")}, skip=set()))
        lines.append(f"{indent}    ")
        lines.append(f"{indent}    response = api_client.{ctx.method.lower()}(url, params=params, json=json_body)")
        lines.append(f"{indent}    assert response.status_code == 400")
        lines.append("")

    for p in int_required:
        safe_name = helpers.var_name(p.name)
        lines.append(f"{indent}def test_{prefix}_negative_{safe_name}(self, api_client, base_url):")
        lines.append(f'{indent}    """{ctx.summary} - 边界值：{p.name}为负数，期望400。"""')
        lines.extend(setup_params(indent * 2, ctx, override={p.name: helpers.edge_value(p, "negative")}, skip=set()))
        lines.append(f"{indent}    ")
        lines.append(f"{indent}    response = api_client.{ctx.method.lower()}(url, params=params, json=json_body)")
        lines.append(f"{indent}    assert response.status_code == 400")
        lines.append("")

    return lines


def test_error_codes(ctx: _TestContext, prefix: str) -> list[str]:
    indent = "    "
    lines: list[str] = []

    for err in ctx.iface.errors:
        err_code = int(err.code)
        if err_code == 400:
            continue
        err_msg = helpers.var_name(str(err.message)) if err.message else f"err_{err_code}"
        desc = err.description or err.message or f"错误码{err_code}"
        lines.append(f"{indent}def test_{prefix}_{err_msg}(self, api_client, base_url):")
        lines.append(f'{indent}    """{ctx.summary} - 错误场景：{desc}（{err_code}）。"""')
        lines.append(f"{indent}    # TODO: 构造触发{err.code} {err.message}的请求数据")
        lines.extend(setup_params(indent * 2, ctx, override={}, skip=set()))
        lines.append(f"{indent}    ")
        lines.append(f"{indent}    response = api_client.{ctx.method.lower()}(url, params=params, json=json_body)")
        lines.append(f"{indent}    assert response.status_code == {err_code}")
        lines.append("")

    return lines


def test_fallback(ctx: _TestContext, prefix: str, current_count: int) -> list[str]:
    indent = "    "
    lines: list[str] = []
    needed = 3 - current_count

    has_boundary = False
    has_error = False
    for ln in test_missing_required(ctx, prefix) + test_invalid_params(ctx, prefix) + test_error_codes(ctx, prefix):
        stripped = ln.strip()
        if stripped.startswith("def test_"):
            name = stripped.split("(")[0].replace("def ", "")
            if "_empty_" in name or "_negative_" in name or "_missing_" in name:
                has_boundary = True
            elif "_err_" in name or any(f"_{c}" in name for c in ["401", "403", "404", "409", "422", "500"]):
                has_error = True

    if needed > 0 and not has_boundary:
        if ctx.method in ("POST", "PUT", "PATCH"):
            lines.append(f"{indent}def test_{prefix}_empty_body(self, api_client, base_url):")
            lines.append(f'{indent}    """{ctx.summary} - 边界场景：空请求体，期望400。"""')
            lines.append(f"{indent}    url = f'{{base_url}}{ctx.path}'")
            lines.append(f"{indent}    response = api_client.{ctx.method.lower()}(url, json={{}})")
            lines.append(f"{indent}    # 空请求体应返回400（根据API实际行为调整断言）")
            lines.append(f"{indent}    assert response.status_code in (400, 422)")
            lines.append("")
        else:
            lines.append(f"{indent}def test_{prefix}_unexpected_params(self, api_client, base_url):")
            lines.append(f'{indent}    """{ctx.summary} - 边界场景：携带未定义的查询参数，服务端应忽略。"""')
            lines.extend(setup_params(indent * 2, ctx, override={}, skip=set()))
            lines.append(f"{indent}    # 添加未预期参数，验证服务端忽略未知参数")
            lines.append(f"{indent}    if params is not None:")
            lines.append(f"{indent}        params['_unexpected'] = 'value'")
            lines.append(f"{indent}    else:")
            lines.append(f"{indent}        params = {{'_unexpected': 'value'}}")
            lines.append(f"{indent}    response = api_client.{ctx.method.lower()}(url, params=params, json=json_body)")
            lines.append(f"{indent}    # 未预期的查询参数应被忽略，请求仍然成功")
            lines.append(f"{indent}    assert response.status_code == {helpers.success_code(ctx.iface)}")
            lines.append("")
        needed -= 1

    if needed > 0 and not has_error:
        lines.append(f"{indent}def test_{prefix}_error_todo(self, api_client, base_url):")
        lines.append(f'{indent}    """{ctx.summary} - 错误场景：TODO 请根据API实际错误场景补充测试。"""')
        lines.append(f"{indent}    # TODO: 根据API文档补充实际错误场景测试")
        lines.append(f"{indent}    # 例如：未认证返回401、权限不足返回403、资源不存在返回404等")
        lines.append(f"{indent}    url = f'{{base_url}}{ctx.path}'")
        lines.append(f"{indent}    response = api_client.{ctx.method.lower()}(url)")
        lines.append(f"{indent}    assert response.status_code >= 400")
        lines.append("")
        needed -= 1

    return lines


def test_python_examples(ctx: _TestContext, prefix: str) -> list[str]:
    indent = "    "
    lines: list[str] = []
    assertions = get_python_assertions(ctx.iface)
    logger.debug(
        "[pytest-gen] _test_python_examples %s %s: 找到%d个python example代码块",
        ctx.method, ctx.path, len(assertions),
    )
    for i, snippet in enumerate(assertions):
        suffix = f"_example_{i + 1}" if i > 0 else "_example"
        lines.append(f"{indent}def test_{prefix}{suffix}(self, api_client, base_url):")
        lines.append(f'{indent}    """{ctx.summary} - 文档示例断言。"""')
        snippet_lines = snippet.splitlines()
        if not snippet_lines:
            logger.warning(
                "[pytest-gen] _test_python_examples %s %s: snippet %d为空",
                ctx.method, ctx.path, i,
            )
            lines.append(f"{indent}    pass")
        else:
            logger.debug(
                "[pytest-gen] _test_python_examples %s %s: snippet %d包含%d行代码",
                ctx.method, ctx.path, i, len(snippet_lines),
            )
            lines.append(f"{indent}    # === 来自文档 ```python example 代码块 ===")
            for sl in snippet_lines:
                lines.append(f"{indent}    {sl}")
        lines.append("")
    return lines
