"""CLI测试生成器（基于Click CliRunner）。"""

from __future__ import annotations

import logging
from pathlib import Path

from mdi.models import MDIDocument, Interface
from mdi.generators.base import BaseGenerator
from mdi.generators.utils import sanitize_identifier

from .context import _CLITestContext
from . import test_builders

logger = logging.getLogger(__name__)

CONFTEST_TEMPLATE = '''"""pytest fixtures for CLI testing."""

import pytest
from click.testing import CliRunner


@pytest.fixture
def cli_runner():
    """提供Click CliRunner实例。"""
    return CliRunner()
'''


class CLITestGenerator(BaseGenerator):
    """Click CLI测试骨架生成器，使用CliRunner进行命令行集成测试。"""

    def _generate(self, doc: MDIDocument, output_dir: Path) -> list[Path]:
        generated_files: list[Path] = []
        module_name = sanitize_identifier(
            doc.frontmatter.get("name", "cli")
        ).replace("-", "_")
        test_filename = f"test_{module_name}_cli.py"

        logger.info(
            "[cli-test-gen] 开始生成CLI测试文件: doc=%s, commands=%d, output=%s",
            doc.title or module_name, len(doc.interfaces), output_dir,
        )

        cli_interfaces = [
            iface for iface in doc.interfaces
            if iface.method.upper() in ("CMD", "CLI", "COMMAND")
        ]

        content = self._generate_test_module(doc, cli_interfaces, module_name)
        test_path = output_dir / test_filename
        generated_files.append(self._write_file(test_path, content))
        logger.debug("[cli-test-gen] 测试文件已写入: %s (%d行)", test_path, content.count("\n") + 1)

        conftest_path = output_dir / "conftest.py"
        if not conftest_path.exists():
            generated_files.append(self._write_file(conftest_path, CONFTEST_TEMPLATE))
            logger.debug("[cli-test-gen] conftest.py已写入: %s", conftest_path)

        logger.info("[cli-test-gen] 生成完成: %d个文件", len(generated_files))
        return generated_files

    def _generate_test_module(
        self, doc: MDIDocument, interfaces: list[Interface], module_name: str
    ) -> str:
        lines: list[str] = []
        title = doc.title or doc.frontmatter.get("name", "CLI Tool")

        lines.append(f'"""Click CLI integration tests for {title}."""')
        lines.append("")
        lines.append("import pytest")
        lines.append("from click.testing import CliRunner")
        lines.append("")
        lines.append(f"# TODO: 替换为实际CLI入口导入路径")
        lines.append(f"# from {module_name}.cli import main")
        lines.append(f"def main(*args, **kwargs):")
        lines.append(f'    """占位入口，请替换为实际CLI main函数。"""')
        lines.append(f"    raise NotImplementedError('请替换为实际CLI入口')")
        lines.append("")
        lines.append("")

        if not interfaces:
            lines.append("# TODO: 未发现CLI命令定义（{endpoint} CMD），请检查MDI文档")
            lines.append("def test_cli_placeholder(cli_runner):")
            lines.append('    """占位测试，待命令定义后实现。"""')
            lines.append("    pass")
            lines.append("")
            return "\n".join(lines)

        for iface in interfaces:
            lines.extend(self._generate_command_tests(iface))

        return "\n".join(lines)

    def _generate_command_tests(self, iface: Interface) -> list[str]:
        lines: list[str] = []
        cmd_name = sanitize_identifier(iface.path or iface.name).replace("-", "_")
        if cmd_name.startswith("_"):
            cmd_name = cmd_name[1:]

        ctx = _CLITestContext(cmd_name, iface.method, iface=iface)

        logger.debug(
            "[cli-test-gen] 命令 %s: arguments=%d, options=%d, flags=%d, "
            "examples=%d, errors=%d",
            cmd_name,
            len(ctx.arguments), len(ctx.options), len(ctx.flags),
            len(iface.examples), len(iface.errors),
        )

        lines.append(f"class Test{cmd_name.title()}:")
        lines.append(f'    """Tests for `{cmd_name}` command - {iface.summary}."""')
        lines.append("")

        lines.extend(test_builders.test_help(ctx))
        lines.extend(test_builders.test_success(ctx))
        lines.extend(test_builders.test_missing_required(ctx))
        lines.extend(test_builders.test_invalid_values(ctx))
        lines.extend(test_builders.test_error_codes(ctx))
        lines.extend(test_builders.test_shell_examples(ctx))

        test_count = sum(1 for ln in lines if ln.strip().startswith("def test_"))
        if test_count < 3:
            logger.debug(
                "[cli-test-gen] 命令 %s 仅生成%d个测试用例，添加回退测试以满足≥3要求",
                cmd_name, test_count,
            )
            lines.extend(test_builders.test_fallback(ctx, test_count))

        lines.append("")
        return lines
