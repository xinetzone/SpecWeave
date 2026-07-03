from __future__ import annotations

import logging
from pathlib import Path

from mdi.models import MDIDocument, Interface
from mdi.generators.base import BaseGenerator
from mdi.generators.utils import (
    make_interface_name,
    sanitize_identifier,
)

from .context import _TestContext
from .templates import CONFTEST_TEMPLATE
from . import helpers
from . import test_builders

logger = logging.getLogger(__name__)


class PytestGenerator(BaseGenerator):
    """pytest测试骨架生成器。"""

    def _generate(self, doc: MDIDocument, output_dir: Path) -> list[Path]:
        generated_files: list[Path] = []
        module_name = sanitize_identifier(
            doc.frontmatter.get("name", "test_api")
        ).replace("-", "_")
        test_filename = f"test_{module_name}.py"

        logger.info(
            "[pytest-gen] 开始生成测试文件: doc=%s, interfaces=%d, output=%s",
            doc.title or module_name, len(doc.interfaces), output_dir,
        )

        content = self._generate_test_module(doc)
        test_path = output_dir / test_filename
        generated_files.append(self._write_file(test_path, content))
        logger.debug("[pytest-gen] 测试文件已写入: %s (%d行)", test_path, content.count("\n") + 1)

        conftest_path = output_dir / "conftest.py"
        if not conftest_path.exists():
            conftest_content = self._generate_conftest(doc)
            generated_files.append(self._write_file(conftest_path, conftest_content))
            logger.debug("[pytest-gen] conftest.py已写入: %s", conftest_path)

        logger.info("[pytest-gen] 生成完成: %d个文件", len(generated_files))
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

        path_params = [p for p in iface.parameters if p.location == "path"]
        query_params = [p for p in iface.parameters if p.location == "query"]
        body_params = [p for p in iface.parameters if p.location not in ("path", "query", "header", "cookie")]
        func_prefix_val = helpers.func_prefix(iface)

        logger.debug(
            "[pytest-gen] 接口 %s %s: path_params=%d, query_params=%d, body_params=%d, "
            "examples=%d, check_items=%d, errors=%d, prefix=%s",
            method, iface.path,
            len(path_params), len(query_params), len(body_params),
            len(iface.examples), len(iface.check_items), len(iface.errors),
            func_prefix_val,
        )

        ctx = _TestContext(iface.path, method, path_params, query_params, body_params, iface=iface)

        lines.append(f"class Test{class_name}:")
        lines.append(f'    """Tests for {method} {iface.path} - {iface.summary}."""')
        lines.append("")

        lines.extend(test_builders.test_success(ctx, func_prefix_val))
        lines.extend(test_builders.test_missing_required(ctx, func_prefix_val))
        lines.extend(test_builders.test_invalid_params(ctx, func_prefix_val))
        lines.extend(test_builders.test_error_codes(ctx, func_prefix_val))
        if ctx.iface:
            lines.extend(test_builders.test_python_examples(ctx, func_prefix_val))

        test_count = sum(1 for ln in lines if ln.strip().startswith("def test_"))
        if test_count < 3:
            logger.debug(
                "[pytest-gen] 接口 %s %s 仅生成%d个测试用例，添加回退测试以满足≥3要求",
                method, iface.path, test_count,
            )
            lines.extend(test_builders.test_fallback(ctx, func_prefix_val, test_count))

        lines.append("")

        return lines

    def _generate_conftest(self, doc: MDIDocument) -> str:
        default_base_url = doc.frontmatter.get("baseUrl", doc.frontmatter.get("baseurl", "https://api.example.com"))
        return CONFTEST_TEMPLATE.format(default_base_url=default_base_url)
