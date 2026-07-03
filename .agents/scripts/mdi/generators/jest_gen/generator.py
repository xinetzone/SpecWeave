"""Jest测试骨架生成器。
STATUS: UNVERIFIED - 未经实战验证，参考pytest_gen/mdi.parser使用

为Web API Profile生成Jest测试文件（JavaScript/TypeScript），
使用axios作为HTTP客户端，包含正常场景、边界值和错误场景三类测试用例。
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from mdi.models import MDIDocument, Interface
from mdi.generators.base import BaseGenerator
from mdi.generators.utils import sanitize_identifier

from .context import _TestContext
from .codegen import (
    js_repr,
    func_prefix,
    var_name,
    success_code,
    build_url_and_args,
    request_line,
    example_to_override,
)
from .assertions import js_response_assertions, py_to_js_assertions
from .templates import generate_jest_config, generate_test_header, generate_placeholder_tests
from .test_scenarios import (
    test_success,
    test_missing_required,
    test_invalid_params,
    test_error_codes,
    test_fallback,
    test_js_examples,
)

logger = logging.getLogger(__name__)


class JestGenerator(BaseGenerator):
    """Jest测试骨架生成器。"""

    _js_repr = staticmethod(js_repr)
    _func_prefix = staticmethod(func_prefix)
    _var_name = staticmethod(var_name)
    _success_code = staticmethod(success_code)

    def _generate(self, doc: MDIDocument, output_dir: Path) -> list[Path]:
        generated_files: list[Path] = []
        module_name = sanitize_identifier(
            doc.frontmatter.get("name", "test_api")
        ).replace("-", "_")
        test_filename = f"{module_name}.test.js"

        logger.info(
            "[jest-gen] 开始生成测试文件: doc=%s, interfaces=%d, output=%s",
            doc.title or module_name, len(doc.interfaces), output_dir,
        )

        content = self._generate_test_module(doc)
        test_path = output_dir / test_filename
        generated_files.append(self._write_file(test_path, content))
        logger.debug("[jest-gen] 测试文件已写入: %s (%d行)", test_path, content.count("\n") + 1)

        config_path = output_dir / "jest.config.js"
        if not config_path.exists():
            generated_files.append(self._write_file(config_path, self._generate_jest_config()))
            logger.debug("[jest-gen] jest.config.js已写入: %s", config_path)

        logger.info("[jest-gen] 生成完成: %d个文件", len(generated_files))
        return generated_files

    def _generate_test_module(self, doc: MDIDocument) -> str:
        title = doc.title or doc.frontmatter.get("name", "API")
        base_url = doc.frontmatter.get("baseUrl", doc.frontmatter.get("baseurl", "https://api.example.com"))

        lines = generate_test_header(title, base_url)

        if not doc.interfaces:
            lines.extend(generate_placeholder_tests())
            return "\n".join(lines)

        for iface in doc.interfaces:
            lines.extend(self._generate_interface_tests(iface))

        return "\n".join(lines)

    def _generate_interface_tests(self, iface: Interface) -> list[str]:
        lines: list[str] = []
        method = iface.method.upper()
        desc_name = iface.summary or f"{method} {iface.path}"

        path_params = [p for p in iface.parameters if p.location == "path"]
        query_params = [p for p in iface.parameters if p.location == "query"]
        body_params = [p for p in iface.parameters if p.location not in ("path", "query", "header", "cookie")]
        func_prefix_val = self._func_prefix(iface)

        logger.debug(
            "[jest-gen] 接口 %s %s: path_params=%d, query_params=%d, body_params=%d, "
            "examples=%d, check_items=%d, errors=%d, prefix=%s",
            method, iface.path,
            len(path_params), len(query_params), len(body_params),
            len(iface.examples), len(iface.check_items), len(iface.errors),
            func_prefix_val,
        )

        ctx = _TestContext(iface.path, method, path_params, query_params, body_params, iface=iface)

        lines.append(f"// Tests for {method} {iface.path} - {desc_name}")
        lines.append(f"describe('{method} {iface.path}', () => {{")

        lines.extend(self._test_success(ctx, func_prefix_val))
        lines.extend(self._test_missing_required(ctx, func_prefix_val))
        lines.extend(self._test_invalid_params(ctx, func_prefix_val))
        lines.extend(self._test_error_codes(ctx, func_prefix_val))
        lines.extend(self._test_js_examples(ctx, func_prefix_val))

        test_count = sum(1 for ln in lines if re.match(r"\s*test\(", ln))
        if test_count < 3:
            logger.debug(
                "[jest-gen] 接口 %s %s 仅生成%d个测试用例，添加回退测试以满足≥3要求",
                method, iface.path, test_count,
            )
            lines.extend(self._test_fallback(ctx, func_prefix_val, test_count))

        lines.append("});")
        lines.append("")
        return lines

    def _build_url_and_args(self, ctx: _TestContext, override: dict[str, object], skip: set[str]) -> tuple[str, str, str]:
        return build_url_and_args(ctx, override, skip, self._js_repr)

    def _request_line(self, method: str, url_expr: str, query_expr: str, body_expr: str) -> str:
        return request_line(method, url_expr, query_expr, body_expr)

    def _test_success(self, ctx: _TestContext, prefix: str) -> list[str]:
        return test_success(ctx, prefix, self._js_repr)

    def _test_missing_required(self, ctx: _TestContext, prefix: str) -> list[str]:
        return test_missing_required(ctx, prefix, self._js_repr)

    def _test_invalid_params(self, ctx: _TestContext, prefix: str) -> list[str]:
        return test_invalid_params(ctx, prefix, self._js_repr)

    def _test_error_codes(self, ctx: _TestContext, prefix: str) -> list[str]:
        return test_error_codes(ctx, prefix, self._js_repr)

    def _test_js_examples(self, ctx: _TestContext, prefix: str) -> list[str]:
        return test_js_examples(ctx, prefix, self._js_repr)

    def _test_fallback(self, ctx: _TestContext, prefix: str, current_count: int) -> list[str]:
        return test_fallback(ctx, prefix, current_count, self._js_repr)

    def _example_to_override(self, req_example: dict[str, object], ctx: _TestContext) -> dict[str, object]:
        return example_to_override(req_example, ctx)

    def _js_response_assertions(self, indent: str, expected: object, actual_expr: str, depth: int = 0) -> list[str]:
        return js_response_assertions(indent, expected, actual_expr, self._js_repr, depth)

    def _py_to_js_assertions(self, indent: str, py_lines: list[str]) -> list[str]:
        return py_to_js_assertions(indent, py_lines, self._js_repr)

    def _generate_jest_config(self) -> str:
        return generate_jest_config()
