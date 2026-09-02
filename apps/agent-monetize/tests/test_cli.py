"""CLI 入口冒烟测试：--help / --version / 无子命令。"""

from __future__ import annotations

import pytest

from agent_monetize.cli import build_parser, main


def test_help_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "demo" in capsys.readouterr().out


def test_version_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "0.1.0" in capsys.readouterr().out


def test_no_command_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert "demo" in capsys.readouterr().out


def test_parser_has_rounds_override() -> None:
    args = build_parser().parse_args(["--rounds", "5", "demo"])
    assert args.command == "demo"
    assert args.rounds == 5
