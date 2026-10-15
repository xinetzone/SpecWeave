"""T1 骨架：CLI 占位行为测试。"""

import pytest

from doocs_md_py.cli import _SUBCOMMANDS, build_parser, main


def test_help_lists_all_subcommands(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    for name in _SUBCOMMANDS:
        assert name in out


def test_no_args_prints_help_exit_zero(capsys):
    assert main([]) == 0
    assert "mdpy" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("name", "argv"),
    [
        ("render", ["render", "-i", "x.md"]),
        ("serve", ["serve"]),
        ("upload", ["upload", "--provider", "local", "--file", "x.png"]),
    ],
)
def test_placeholder_subcommands_exit_two(name, argv, capsys):
    assert main(argv) == 2
    err = capsys.readouterr().err
    assert name in err


def test_migrate_creates_and_updates_db(tmp_path, capsys):
    db_file = tmp_path / "nested" / "test.db"
    assert main(["migrate", "--db", str(db_file)]) == 0
    assert db_file.exists()
    out = capsys.readouterr().out
    assert "已应用迁移" in out
    # 幂等：第二次无新增
    assert main(["migrate", "--db", str(db_file)]) == 0
    out2 = capsys.readouterr().out
    assert "已是最新" in out2


def test_missing_required_args_exits_two(capsys):
    # argparse 标准行为：缺必需参数时 SystemExit(2) 并输出 usage
    with pytest.raises(SystemExit) as exc:
        main(["upload"])
    assert exc.value.code == 2
    assert "required" in capsys.readouterr().err


def test_parser_structure():
    parser = build_parser()
    # 无额外必需参数的子命令可直接解析
    for name in ("mcp", "migrate"):
        args = parser.parse_args([name])
        assert args.command == name


def test_serve_defaults():
    parser = build_parser()
    args = parser.parse_args(["serve"])
    assert args.host == "127.0.0.1"
    assert args.port == 8800
