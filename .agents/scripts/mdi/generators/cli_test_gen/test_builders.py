"""CLI测试场景构建器。"""

from __future__ import annotations

import logging
import re

from mdi.example_extractor import get_shell_examples

from .context import _CLITestContext
from . import helpers

logger = logging.getLogger(__name__)


def _args_block(indent: str, cmd_name: str, args_lines: list[str], opt_lines: list[str]) -> list[str]:
    """生成统一格式的args列表代码块。"""
    lines = [f"{indent}args = ["]
    lines.append(f"{indent}    '{cmd_name}',")
    lines.extend(args_lines)
    lines.extend(opt_lines)
    lines.append(f"{indent}]")
    return lines


def test_help(ctx: _CLITestContext) -> list[str]:
    """测试 --help 标志。"""
    indent = "    "
    cmd = ctx.command_name
    return [
        f"{indent}def test_{cmd}_help(self, cli_runner):",
        f'{indent}    """{ctx.summary or cmd} - --help 显示帮助信息，退出码0。"""',
        f"{indent}    result = cli_runner.invoke(main, ['{cmd}', '--help'])",
        f"{indent}    assert result.exit_code == 0",
        f"{indent}    assert '{cmd}' in result.output",
        "",
    ]


def test_success(ctx: _CLITestContext) -> list[str]:
    """测试命令正常执行成功。"""
    indent = "    "
    cmd = ctx.command_name
    success_code = helpers.build_exit_code_check(ctx)
    lines = [
        f"{indent}def test_{cmd}_success(self, cli_runner):",
        f'{indent}    """{ctx.summary or cmd} - 正常场景：所有必填参数提供，执行成功退出码{success_code}。"""',
    ]

    args_lines, opt_lines = helpers.build_command_args(ctx, include_all_options=True)
    lines.extend(_args_block(indent, cmd, args_lines, opt_lines))
    lines.append(f"{indent}    result = cli_runner.invoke(main, args)")
    lines.append(f"{indent}    assert result.exit_code == {success_code}")
    lines.append("")
    return lines


def test_missing_required(ctx: _CLITestContext) -> list[str]:
    """测试缺少必填参数时退出码非0。"""
    indent = "    "
    cmd = ctx.command_name
    lines: list[str] = []

    for miss_p in ctx.all_required:
        safe_name = helpers.cli_var_name(miss_p.name)
        loc_desc = "位置参数" if miss_p in ctx.arguments else "必填选项"
        lines.append(f"{indent}def test_{cmd}_missing_{safe_name}(self, cli_runner):")
        lines.append(f'{indent}    """{ctx.summary or cmd} - 错误场景：缺少{loc_desc}{miss_p.name}，期望非0退出码。"""')
        args_lines, opt_lines = helpers.build_command_args(ctx, skip={miss_p.name})
        lines.extend(_args_block(indent, cmd, args_lines, opt_lines))
        lines.append(f"{indent}    result = cli_runner.invoke(main, args)")
        lines.append(f"{indent}    assert result.exit_code != 0")
        lines.append("")

    return lines


def test_invalid_values(ctx: _CLITestContext) -> list[str]:
    """测试无效参数值（如空字符串、负数）。"""
    indent = "    "
    cmd = ctx.command_name
    lines: list[str] = []

    for p in ctx.all_required:
        if p.type in ("string", "str", ""):
            safe_name = helpers.cli_var_name(p.name)
            lines.append(f"{indent}def test_{cmd}_empty_{safe_name}(self, cli_runner):")
            lines.append(f'{indent}    """{ctx.summary or cmd} - 边界值：{p.name}为空字符串，期望非0退出码。"""')
            args_lines, opt_lines = helpers.build_command_args(
                ctx, override={p.name: "''"}, include_all_options=False
            )
            lines.extend(_args_block(indent, cmd, args_lines, opt_lines))
            lines.append(f"{indent}    result = cli_runner.invoke(main, args)")
            lines.append(f"{indent}    assert result.exit_code != 0")
            lines.append("")

    return lines


def test_error_codes(ctx: _CLITestContext) -> list[str]:
    """测试文档中声明的错误码。"""
    indent = "    "
    cmd = ctx.command_name
    lines: list[str] = []

    if not ctx.iface:
        return lines

    for err in ctx.iface.errors:
        err_code_val = int(err.code) if not isinstance(err.code, int) else err.code
        if err_code_val == 0:
            continue
        err_id = helpers.cli_var_name(str(err.message or f"err_{err_code_val}"))
        desc = err.description or err.message or f"错误码{err_code_val}"
        lines.append(f"{indent}def test_{cmd}_{err_id}(self, cli_runner):")
        lines.append(f'{indent}    """{ctx.summary or cmd} - 错误场景：{desc}（退出码{err_code_val}）。"""')
        lines.append(f"{indent}    # TODO: 构造触发{err_code_val} {err.message}的命令参数")
        args_lines, opt_lines = helpers.build_command_args(ctx)
        lines.extend(_args_block(indent, cmd, args_lines, opt_lines))
        lines.append(f"{indent}    result = cli_runner.invoke(main, args)")
        lines.append(f"{indent}    # assert result.exit_code == {err_code_val}")
        lines.append("")

    return lines


def test_shell_examples(ctx: _CLITestContext) -> list[str]:
    """从文档 ```shell example / ```bash example 代码块提取CLI示例测试。"""
    indent = "    "
    cmd = ctx.command_name
    lines: list[str] = []

    if not ctx.iface:
        return lines

    examples = get_shell_examples(ctx.iface)
    logger.debug(
        "[cli-test-gen] test_shell_examples %s: 找到%d个shell example代码块",
        cmd, len(examples),
    )

    for i, snippet in enumerate(examples):
        suffix = f"_example_{i + 1}" if i > 0 else "_example"
        lines.append(f"{indent}def test_{cmd}{suffix}(self, cli_runner):")
        lines.append(f'{indent}    """{ctx.summary or cmd} - 文档Shell示例。"""')
        snippet_lines = snippet.strip().splitlines()
        if not snippet_lines:
            logger.warning("[cli-test-gen] test_shell_examples %s: snippet %d为空", cmd, i)
            lines.append(f"{indent}    pass")
        else:
            first_line = snippet_lines[0].strip()
            invoke_args = _parse_shell_to_invoke_args(first_line, cmd)
            lines.append(f"{indent}    # === 来自文档 ```shell example 代码块 ===")
            if invoke_args:
                lines.append(f"{indent}    result = cli_runner.invoke(main, {invoke_args})")
                lines.append(f"{indent}    assert result.exit_code == 0")
            else:
                for sl in snippet_lines:
                    lines.append(f"{indent}    # {sl}")
                lines.append(f"{indent}    pass  # TODO: 手动转换为cli_runner.invoke调用")
        lines.append("")

    return lines


def _parse_shell_to_invoke_args(shell_line: str, expected_cmd: str) -> str | None:
    """尝试将shell命令行解析为Python args列表。"""
    import shlex
    try:
        tokens = shlex.split(shell_line)
    except ValueError:
        return None

    if not tokens:
        return None

    args_tokens = tokens[1:]

    if expected_cmd in args_tokens:
        idx = args_tokens.index(expected_cmd)
        cmd_args = args_tokens[idx:]
    elif tokens[0].endswith(expected_cmd) or tokens[0] == expected_cmd:
        cmd_args = args_tokens
    else:
        cmd_args = args_tokens

    arg_reprs = [repr(a) for a in cmd_args]
    return "[" + ", ".join(arg_reprs) + "]"


def test_fallback(ctx: _CLITestContext, current_count: int) -> list[str]:
    """回退测试：确保每个命令至少3个测试用例。"""
    indent = "    "
    cmd = ctx.command_name
    lines: list[str] = []
    needed = 3 - current_count

    if needed <= 0:
        return lines

    has_invalid = any(
        ln.strip().startswith(f"def test_{cmd}_empty_")
        for ln in test_invalid_values(ctx)
    )
    has_missing = any(
        ln.strip().startswith(f"def test_{cmd}_missing_")
        for ln in test_missing_required(ctx)
    )

    if needed > 0 and not has_invalid:
        lines.append(f"{indent}def test_{cmd}_invalid_flag(self, cli_runner):")
        lines.append(f'{indent}    """{ctx.summary or cmd} - 边界场景：传入无效选项，期望非0退出码。"""')
        lines.append(f"{indent}    result = cli_runner.invoke(main, ['{cmd}', '--nonexistent-option'])")
        lines.append(f"{indent}    assert result.exit_code != 0")
        lines.append("")
        needed -= 1

    if needed > 0 and not has_missing:
        lines.append(f"{indent}def test_{cmd}_no_args(self, cli_runner):")
        lines.append(f'{indent}    """{ctx.summary or cmd} - 边界场景：无参数调用，根据命令期望验证行为。"""')
        lines.append(f"{indent}    result = cli_runner.invoke(main, ['{cmd}'])")
        if ctx.all_required:
            lines.append(f"{indent}    assert result.exit_code != 0")
        else:
            lines.append(f"{indent}    assert result.exit_code == 0")
        lines.append("")
        needed -= 1

    if needed > 0:
        lines.append(f"{indent}def test_{cmd}_todo(self, cli_runner):")
        lines.append(f'{indent}    """{ctx.summary or cmd} - TODO 请根据CLI实际行为补充测试。"""')
        lines.append(f"{indent}    # TODO: 补充实际测试场景")
        lines.append(f"{indent}    result = cli_runner.invoke(main, ['{cmd}', '--help'])")
        lines.append(f"{indent}    assert result.exit_code == 0")
        lines.append("")

    return lines
