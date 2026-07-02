"""pytest测试骨架生成器。

为Web API Profile生成pytest测试文件，包含正常场景、边界值和错误场景三类测试用例。
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mdi.models import MDIDocument, Interface, Parameter
from mdi.generators.base import BaseGenerator
from mdi.generators.utils import (
    make_interface_name,
    sanitize_identifier,
)
from mdi.mock_data import generate_mock_value, generate_edge_value
from mdi.example_extractor import (
    extract_examples,
    get_request_example,
    get_response_example,
    get_python_assertions,
)


class PytestGenerator(BaseGenerator):
    """pytest测试骨架生成器。"""

    def _generate(self, doc: MDIDocument, output_dir: Path) -> list[Path]:
        generated_files: list[Path] = []
        module_name = sanitize_identifier(
            doc.frontmatter.get("name", "test_api")
        ).replace("-", "_")
        test_filename = f"test_{module_name}.py"

        content = self._generate_test_module(doc)
        test_path = output_dir / test_filename
        generated_files.append(self._write_file(test_path, content))

        conftest_path = output_dir / "conftest.py"
        if not conftest_path.exists():
            conftest_content = self._generate_conftest(doc)
            generated_files.append(self._write_file(conftest_path, conftest_content))

        return generated_files

    def _generate_test_module(self, doc: MDIDocument) -> str:
        lines: list[str] = []
        title = doc.title or doc.frontmatter.get("name", "API")

        lines.append(f'"""pytest tests for {title}."""')
        lines.append("")
        lines.append("import pytest")
        lines.append("import requests")
        lines.append("")
        lines.append("")

        if not doc.interfaces:
            lines.append("# TODO: 未发现接口定义，请检查MDI文档")
            lines.append("def test_placeholder():")
            lines.append('    """占位测试，待接口定义后实现。"""')
            lines.append("    pass")
            lines.append("")
            return "\n".join(lines)

        for iface in doc.interfaces:
            lines.extend(self._generate_interface_tests(iface))

        return "\n".join(lines)

    def _generate_interface_tests(self, iface: Interface) -> list[str]:
        lines: list[str] = []
        method = iface.method.upper()
        class_name = method.title() + make_interface_name(iface.name or iface.path)
        lines.append(f"class Test{class_name}:")
        lines.append(f'    """Tests for {method} {iface.path} - {iface.summary}."""')
        lines.append("")

        path_params = [p for p in iface.parameters if p.location == "path"]
        query_params = [p for p in iface.parameters if p.location == "query"]
        body_params = [p for p in iface.parameters if p.location not in ("path", "query", "header", "cookie")]
        func_prefix = self._func_prefix(iface)

        ctx = _TestContext(iface.path, method, path_params, query_params, body_params, iface=iface)

        lines.extend(self._test_success(ctx, func_prefix))
        lines.extend(self._test_missing_required(ctx, func_prefix))
        lines.extend(self._test_invalid_params(ctx, func_prefix))
        lines.extend(self._test_error_codes(ctx, func_prefix))
        if ctx.iface:
            lines.extend(self._test_python_examples(ctx, func_prefix))
        lines.append("")

        return lines

    def _test_success(self, ctx: "_TestContext", prefix: str) -> list[str]:
        indent = "    "
        success_code = self._success_code(ctx.iface)
        request_example = get_request_example(ctx.iface) if ctx.iface else None
        response_example = get_response_example(ctx.iface, success_code) if ctx.iface else None

        lines = [
            f"{indent}def test_{prefix}_success(self, api_client, base_url):",
            f'{indent}    """{ctx.summary} - 正常场景：请求成功返回{success_code}。"""',
        ]

        override_req = self._example_to_override(request_example, ctx) if request_example else {}
        lines.extend(self._setup_params(indent * 2, ctx, override=override_req, skip=set()))
        lines.append(f"{indent}    ")
        lines.append(f"{indent}    response = api_client.{ctx.method.lower()}(url, params=params, json=json_body)")
        lines.append(f"{indent}    assert response.status_code == {success_code}")

        if response_example is not None:
            lines.append(f"{indent}    data = response.json()")
            lines.extend(self._response_assertions(indent + "    ", response_example, "data"))

        lines.append("")
        return lines

    def _test_missing_required(self, ctx: "_TestContext", prefix: str) -> list[str]:
        indent = "    "
        lines: list[str] = []
        required_body = [p for p in ctx.body_params if p.required]
        required_query = [p for p in ctx.query_params if p.required]

        for miss_p in required_body + required_query:
            safe_name = self._var_name(miss_p.name)
            loc_desc = "body" if miss_p in required_body else "query"
            lines.append(f"{indent}def test_{prefix}_missing_{safe_name}(self, api_client, base_url):")
            lines.append(f'{indent}    """{ctx.summary} - 错误场景：缺少必填参数{miss_p.name}（{loc_desc}），期望400。"""')
            lines.extend(self._setup_params(indent * 2, ctx, override={}, skip={miss_p.name}))
            lines.append(f"{indent}    ")
            lines.append(f"{indent}    response = api_client.{ctx.method.lower()}(url, params=params, json=json_body)")
            lines.append(f"{indent}    assert response.status_code == 400")
            lines.append("")

        return lines

    def _test_invalid_params(self, ctx: "_TestContext", prefix: str) -> list[str]:
        indent = "    "
        lines: list[str] = []
        str_required = [p for p in ctx.all_required if p.type in ("string", "str", "")]
        int_required = [p for p in ctx.all_required if p.type in ("integer", "int")]

        for p in str_required:
            safe_name = self._var_name(p.name)
            lines.append(f"{indent}def test_{prefix}_empty_{safe_name}(self, api_client, base_url):")
            lines.append(f'{indent}    """{ctx.summary} - 边界值：{p.name}为空字符串，期望400。"""')
            lines.extend(self._setup_params(indent * 2, ctx, override={p.name: self._edge_value(p, "empty")}, skip=set()))
            lines.append(f"{indent}    ")
            lines.append(f"{indent}    response = api_client.{ctx.method.lower()}(url, params=params, json=json_body)")
            lines.append(f"{indent}    assert response.status_code == 400")
            lines.append("")

        for p in int_required:
            safe_name = self._var_name(p.name)
            lines.append(f"{indent}def test_{prefix}_negative_{safe_name}(self, api_client, base_url):")
            lines.append(f'{indent}    """{ctx.summary} - 边界值：{p.name}为负数，期望400。"""')
            lines.extend(self._setup_params(indent * 2, ctx, override={p.name: self._edge_value(p, "negative")}, skip=set()))
            lines.append(f"{indent}    ")
            lines.append(f"{indent}    response = api_client.{ctx.method.lower()}(url, params=params, json=json_body)")
            lines.append(f"{indent}    assert response.status_code == 400")
            lines.append("")

        return lines

    def _test_error_codes(self, ctx: "_TestContext", prefix: str) -> list[str]:
        indent = "    "
        lines: list[str] = []

        for err in ctx.iface.errors:
            err_code = int(err.code)
            if err_code == 400:
                continue
            err_msg = self._var_name(str(err.message)) if err.message else f"err_{err_code}"
            desc = err.description or err.message or f"错误码{err_code}"
            lines.append(f"{indent}def test_{prefix}_{err_msg}(self, api_client, base_url):")
            lines.append(f'{indent}    """{ctx.summary} - 错误场景：{desc}（{err_code}）。"""')
            lines.append(f"{indent}    # TODO: 构造触发{err.code} {err.message}的请求数据")
            lines.extend(self._setup_params(indent * 2, ctx, override={}, skip=set()))
            lines.append(f"{indent}    ")
            lines.append(f"{indent}    response = api_client.{ctx.method.lower()}(url, params=params, json=json_body)")
            lines.append(f"{indent}    assert response.status_code == {err_code}")
            lines.append("")

        return lines

    def _setup_params(
        self,
        indent: str,
        ctx: "_TestContext",
        override: dict[str, str],
        skip: set[str],
    ) -> list[str]:
        lines: list[str] = []

        for p in ctx.path_params:
            var = self._var_name(p.name)
            val = override.get(p.name, self._sample_value(p))
            lines.append(f"{indent}{var} = {val}")

        url = self._build_fstring_url(ctx.path, ctx.path_params, override)
        lines.append(f"{indent}url = f'{{base_url}}{url}'")

        if ctx.query_params:
            lines.append(f"{indent}params = {{")
            for p in ctx.query_params:
                if p.name in skip:
                    continue
                val = override.get(p.name, self._sample_value(p))
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
                val = override.get(p.name, self._sample_value(p))
                lines.append(f"{indent}    {repr(p.name)}: {val},")
            for extra_key, extra_val in extra_body_items.items():
                lines.append(f"{indent}    {repr(extra_key)}: {extra_val},")
            lines.append(f"{indent}}}")
        else:
            lines.append(f"{indent}json_body = None")

        return lines

    def _build_fstring_url(self, path: str, path_params: list[Parameter], override: dict[str, str]) -> str:
        result = path
        for p in path_params:
            var = self._var_name(p.name)
            placeholder = "{" + p.name + "}"
            if p.name in override:
                val = override[p.name]
                raw = val.strip('"') if val.startswith('"') and val.endswith('"') else val
                result = result.replace(placeholder, raw)
            else:
                result = result.replace(placeholder, "{" + var + "}")
        return result

    def _func_prefix(self, iface: Interface) -> str:
        method = iface.method.lower()
        name = sanitize_identifier(iface.name or iface.path).replace("-", "_")
        if name.startswith("_"):
            name = name[1:]
        return f"{method}_{name}"

    def _var_name(self, name: str) -> str:
        return sanitize_identifier(name).replace("-", "_")

    def _code_for_method(self, method: str) -> int:
        m = method.upper()
        if m == "POST":
            return 201
        if m == "DELETE":
            return 204
        return 200

    def _success_code(self, iface: Interface) -> int:
        for r in iface.responses:
            code = int(r.status_code)
            if 200 <= code < 300:
                return code
        return self._code_for_method(iface.method)

    def _sample_value(self, param: Parameter) -> str:
        val = generate_mock_value(param)
        return self._py_repr(val)

    def _edge_value(self, param: Parameter, edge_type: str) -> str:
        val = generate_edge_value(param, edge_type)
        return self._py_repr(val)

    @staticmethod
    def _py_repr(val: object) -> str:
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
            return "[" + ", ".join(PytestGenerator._py_repr(v) for v in val) + "]"
        if isinstance(val, dict):
            items = ", ".join(
                f"{PytestGenerator._py_repr(k)}: {PytestGenerator._py_repr(v)}"
                for k, v in val.items()
            )
            return "{" + items + "}"
        return repr(val)

    def _example_to_override(self, req_example: dict[str, Any], ctx: "_TestContext") -> dict[str, str]:
        """将request example数据转换为_setup_params可用的override字典。

        只覆盖example中与已知参数名匹配的字段。example中未定义的参数仍用mock数据。
        若example中有额外字段（非参数表定义但在请求体中），通过__extra_body__前缀传递，
        由_setup_params追加到json_body末尾。
        """
        override: dict[str, str] = {}
        known_names = {p.name for p in ctx.path_params + ctx.query_params + ctx.body_params}
        for key, val in req_example.items():
            if key in known_names:
                override[key] = self._py_repr(val)
            else:
                override[f"__extra_body__{key}"] = self._py_repr(val)
        return override

    def _response_assertions(self, indent: str, expected: Any, actual_expr: str, depth: int = 0) -> list[str]:
        """从响应示例数据生成字段级断言。

        对顶层字段（depth=0）只断言存在性和类型；对嵌套结构递归断言关键字段存在。
        """
        lines: list[str] = []
        prefix = indent
        if isinstance(expected, dict):
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
            lines.append(f"{prefix}assert isinstance({actual_expr}, list)")
        return lines

    def _test_python_examples(self, ctx: "_TestContext", prefix: str) -> list[str]:
        """将```python example代码块作为自定义测试方法嵌入。"""
        indent = "    "
        lines: list[str] = []
        assertions = get_python_assertions(ctx.iface)
        for i, snippet in enumerate(assertions):
            suffix = f"_example_{i + 1}" if i > 0 else "_example"
            lines.append(f"{indent}def test_{prefix}{suffix}(self, api_client, base_url):")
            lines.append(f'{indent}    """{ctx.summary} - 文档示例断言。"""')
            snippet_lines = snippet.splitlines()
            if not snippet_lines:
                lines.append(f"{indent}    pass")
            else:
                lines.append(f"{indent}    # === 来自文档 ```python example 代码块 ===")
                for sl in snippet_lines:
                    lines.append(f"{indent}    {sl}")
            lines.append("")
        return lines

    def _generate_conftest(self, doc: MDIDocument) -> str:
        default_base_url = doc.frontmatter.get("baseUrl", doc.frontmatter.get("baseurl", "https://api.example.com"))
        return (
            '"""pytest配置和共享fixture。\n'
            '\n'
            'base_url 覆盖优先级：命令行 --base-url > 环境变量 API_BASE_URL > frontmatter 默认值\n'
            'api_token 覆盖优先级：命令行 --api-token > 环境变量 API_TOKEN > 无token\n'
            '"""\n'
            '\n'
            'import os\n'
            'import pytest\n'
            'import requests\n'
            '\n'
            '\n'
            'def pytest_addoption(parser):\n'
            '    """注册自定义命令行参数（幂等：重复调用不报错）。"""\n'
            '    def _safe_addoption(*args, **kwargs):\n'
            '        try:\n'
            '            parser.addoption(*args, **kwargs)\n'
            '        except ValueError:\n'
            '            pass\n'
            '    _safe_addoption(\n'
            '        "--base-url",\n'
            '        action="store",\n'
            '        default=None,\n'
            '        help="API基础URL，覆盖默认配置（也可通过API_BASE_URL环境变量设置）",\n'
            '    )\n'
            '    _safe_addoption(\n'
            '        "--api-token",\n'
            '        action="store",\n'
            '        default=None,\n'
            '        help="API认证Token，设置后自动加入Authorization头（也可通过API_TOKEN环境变量设置）",\n'
            '    )\n'
            '\n'
            '\n'
            '@pytest.fixture(scope="session")\n'
            'def base_url(request):\n'
            '    """API基础URL。优先级：命令行 > 环境变量 > 默认值。"""\n'
            '    cli_url = request.config.getoption("--base-url")\n'
            '    if cli_url:\n'
            '        return cli_url.rstrip("/")\n'
            '    env_url = os.environ.get("API_BASE_URL")\n'
            '    if env_url:\n'
            '        return env_url.rstrip("/")\n'
            f'    return "{default_base_url}"\n'
            '\n'
            '\n'
            '@pytest.fixture(scope="session")\n'
            'def api_client(request):\n'
            '    """共享requests session，自动配置Content-Type和认证头。"""\n'
            '    session = requests.Session()\n'
            '    session.headers.update({"Content-Type": "application/json"})\n'
            '    cli_token = request.config.getoption("--api-token")\n'
            '    token = cli_token or os.environ.get("API_TOKEN")\n'
            '    if token:\n'
            '        session.headers.update({"Authorization": f"Bearer {token}"})\n'
            '    yield session\n'
            '    session.close()\n'
        )


class _TestContext:
    """测试生成上下文，封装单个接口的参数信息。"""

    def __init__(
        self,
        path: str,
        method: str,
        path_params: list[Parameter],
        query_params: list[Parameter],
        body_params: list[Parameter],
        iface: Interface | None = None,
    ) -> None:
        self.path = path
        self.method = method
        self.path_params = path_params
        self.query_params = query_params
        self.body_params = body_params
        self.iface = iface

    @property
    def summary(self) -> str:
        return self.iface.summary if self.iface else ""

    @property
    def all_required(self) -> list[Parameter]:
        return [p for p in self.path_params + self.query_params + self.body_params if p.required]
