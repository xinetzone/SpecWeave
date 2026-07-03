"""CLI测试生成辅助函数。"""

from __future__ import annotations

import logging
from typing import Any

from mdi.models import Interface, Parameter
from mdi.generators.utils import sanitize_identifier
from mdi.mock_data import generate_mock_value, generate_edge_value

logger = logging.getLogger(__name__)


def cli_var_name(name: str) -> str:
    return sanitize_identifier(name).replace("-", "_")


def cli_option_name(name: str) -> str:
    return "--" + name.replace("_", "-")


def cli_sample_value(param: Parameter) -> str:
    val = generate_mock_value(param)
    return _cli_repr(val)


def cli_flag_default(param: Parameter) -> bool:
    if param.default is None:
        return False
    return str(param.default).lower() in ("true", "yes", "1")


def build_command_args(
    ctx,
    override: dict[str, str] | None = None,
    skip: set[str] | None = None,
    include_all_options: bool = False,
) -> tuple[list[str], list[str]]:
    """构建CliRunner.invoke的args列表代码行。

    Args:
        ctx: CLI测试上下文。
        override: 参数覆盖值字典。
        skip: 要跳过的参数名集合。
        include_all_options: 是否在success场景包含所有options（含带默认值的）。

    Returns:
        (args_lines, opt_lines) - 位置参数行和选项行的代码片段列表，已含8空格缩进。
    """
    override = override or {}
    skip = skip or set()
    indent = "        "

    args_lines: list[str] = []
    opt_lines: list[str] = []

    for p in ctx.arguments:
        if p.name in skip:
            continue
        val = override.get(p.name, cli_sample_value(p))
        args_lines.append(f"{indent}{val},")

    for p in ctx.options:
        if p.name in skip:
            continue
        if not include_all_options and not p.required and p.name not in override and p.default is not None:
            continue
        if not include_all_options and not p.required and p.name not in override:
            continue
        val = override.get(p.name, cli_sample_value(p))
        opt_lines.append(f"{indent}{repr(cli_option_name(p.name))},")
        opt_lines.append(f"{indent}{val},")

    for p in ctx.flags:
        flag_val = override.get(p.name)
        if flag_val is not None:
            if _is_truthy_flag(flag_val):
                opt_lines.append(f"{indent}{repr(cli_option_name(p.name))},")
        else:
            if p.required or cli_flag_default(p) or include_all_options:
                opt_lines.append(f"{indent}{repr(cli_option_name(p.name))},")

    return args_lines, opt_lines


def build_exit_code_check(ctx) -> int:
    """推断CLI命令成功时的退出码。"""
    if ctx.iface:
        for r in ctx.iface.responses:
            code = int(r.status_code) if not isinstance(r.status_code, int) else r.status_code
            if code == 0:
                return 0
    return 0


def _cli_repr(val: object) -> str:
    if val is None:
        return "None"
    if isinstance(val, bool):
        return "True" if val else "False"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        escaped = val.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        return f"'{escaped}'"
    if isinstance(val, list):
        return "[" + ", ".join(_cli_repr(v) for v in val) + "]"
    return repr(val)


def _is_truthy_flag(val: str) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        v = val.strip("'\"")
        return v.lower() in ("true", "yes", "1")
    return bool(val)
