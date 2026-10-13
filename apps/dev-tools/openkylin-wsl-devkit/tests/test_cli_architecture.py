"""cli/ 分层架构门禁。

覆盖：parser 命令面与注册表键集交叉校验、子组空命令帮助闭包、
main 单点错误收口（OkwError 收口 / 非受控异常不吞）、
parser/main 职责纯度静态断言与行数预算。
"""

import ast
import importlib
from pathlib import Path

import pytest

from okw import cli
from okw.cli.parser import build_parser
from okw.commands import COMMAND_HANDLERS
from okw.distro import WslError
from okw.scaffold import ScaffoldError

from cli_surface_lib import collect_leaf_commands

# 注意：okw.cli.__init__ 重导出的 main 函数会遮蔽同名子模块，
# 要拿到子模块（及其模块级 COMMAND_HANDLERS 绑定）必须经 importlib。
main_mod = importlib.import_module("okw.cli.main")

SRC_ROOT = Path(__file__).resolve().parents[1] / "src" / "okw"
PARSER_SOURCE = (SRC_ROOT / "cli" / "parser.py").read_text(encoding="utf-8")
MAIN_SOURCE = (SRC_ROOT / "cli" / "main.py").read_text(encoding="utf-8")


def test_parser_leaves_match_registry_keys_exactly():
    assert sorted(collect_leaf_commands(build_parser())) == sorted(COMMAND_HANDLERS)


@pytest.mark.parametrize("group", ["ai", "podman", "compose", "image"])
def test_group_without_subcommand_prints_help_and_returns_2(group, capsys):
    ret = cli.main([group])
    captured = capsys.readouterr()
    assert ret == 2
    assert f"okw {group}" in captured.out


def test_main_central_catches_wsl_error(monkeypatch, capsys):
    def boom(_args):
        raise WslError("受控失败清单")

    monkeypatch.setitem(COMMAND_HANDLERS, "list", boom)
    rc = main_mod.main(["list"])
    captured = capsys.readouterr()
    assert rc == 1
    assert captured.err == "错误：受控失败清单\n"
    assert captured.out == ""


def test_main_central_catches_scaffold_error(monkeypatch, capsys):
    def boom(_args):
        raise ScaffoldError("脚手架受控失败")

    monkeypatch.setitem(COMMAND_HANDLERS, "list", boom)
    rc = main_mod.main(["list"])
    captured = capsys.readouterr()
    assert rc == 1
    assert captured.err == "错误：脚手架受控失败\n"


def test_main_does_not_swallow_unexpected_exception(monkeypatch):
    def boom(_args):
        raise ValueError("程序缺陷不应被伪装")

    monkeypatch.setitem(COMMAND_HANDLERS, "list", boom)
    with pytest.raises(ValueError, match="程序缺陷"):
        main_mod.main(["list"])


def _except_handlers(source):
    tree = ast.parse(source)
    handlers = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            handlers.append(node.type)
    return handlers


def test_main_has_no_broad_exception_catch():
    for handler_type in _except_handlers(MAIN_SOURCE):
        # 仅允许具名捕获；且唯一具名类型必须是 OkwError。
        assert handler_type is not None, "禁止裸 except"
        assert ast.unparse(handler_type) == "OkwError", ast.unparse(handler_type)


def test_parser_module_does_not_read_argv_or_run_subprocess():
    forbidden = ("sys.argv", "subprocess", "os.system", "run_wsl", "exec_distro")
    for token in forbidden:
        assert token not in PARSER_SOURCE, f"parser 层出现 IO/执行耦合：{token}"


def test_main_module_does_not_assemble_parser():
    tree = ast.parse(MAIN_SOURCE)
    assembly_methods = ("add_parser", "add_argument", "add_subparsers")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in assembly_methods:
                pytest.fail(f"main 层出现装配调用：{func.attr}")


def test_parser_and_main_line_budget():
    parser_lines = len(PARSER_SOURCE.splitlines())
    main_lines = len(MAIN_SOURCE.splitlines())
    assert parser_lines <= 400, f"parser.py {parser_lines} 行超预算"
    assert main_lines <= 300, f"main.py {main_lines} 行超预算"
