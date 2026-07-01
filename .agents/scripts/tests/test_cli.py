"""lib.cli 单元测试。"""

import argparse
import sys

import pytest

from lib import cli


class TestColor:
    """_color 内部函数测试（在非 TTY 环境下不添加 ANSI 码）。"""

    def test_non_tty_returns_plain(self, monkeypatch):
        monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
        assert cli._color("hello", "\033[92m") == "hello"

    def test_tty_wraps_ansi(self, monkeypatch):
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
        result = cli._color("hello", "\033[92m")
        assert "\033[92m" in result
        assert "hello" in result
        assert "\033[0m" in result


class TestPrintFunctions:
    """打印函数测试（使用 capsys 捕获输出）。"""

    def test_print_pass_ascii_mode(self, capsys):
        cli.print_pass("all good")
        out = capsys.readouterr().out
        assert "all good" in out
        assert "[PASS]" in out

    def test_print_warn_ascii_mode(self, capsys):
        cli.print_warn("be careful")
        out = capsys.readouterr().out
        assert "be careful" in out
        assert "[WARN]" in out

    def test_print_error_ascii_mode(self, capsys):
        cli.print_error("something wrong")
        out = capsys.readouterr().out
        assert "something wrong" in out
        assert "[FAIL]" in out

    def test_print_pass_unicode_mode(self, capsys, monkeypatch):
        monkeypatch.setattr(cli, "_supports_unicode", lambda: True)
        cli.print_pass("all good")
        out = capsys.readouterr().out
        assert "all good" in out
        assert "✓" in out

    def test_print_warn_unicode_mode(self, capsys, monkeypatch):
        monkeypatch.setattr(cli, "_supports_unicode", lambda: True)
        cli.print_warn("be careful")
        out = capsys.readouterr().out
        assert "be careful" in out
        assert "⚠" in out

    def test_print_error_unicode_mode(self, capsys, monkeypatch):
        monkeypatch.setattr(cli, "_supports_unicode", lambda: True)
        cli.print_error("something wrong")
        out = capsys.readouterr().out
        assert "something wrong" in out
        assert "✗" in out

    def test_gbk_terminal_falls_back_to_ascii(self, capsys, monkeypatch):
        monkeypatch.setattr(cli, "_supports_unicode", lambda: False)
        cli.print_pass("ok")
        out = capsys.readouterr().out
        assert "[PASS]" in out
        assert "✓" not in out

    def test_print_header(self, capsys):
        cli.print_header("Title", width=40)
        out = capsys.readouterr().out
        assert "Title" in out
        assert "=" * 40 in out

    def test_print_header_default_width(self, capsys):
        cli.print_header("Test")
        out = capsys.readouterr().out
        assert "=" * 60 in out

    def test_print_summary_all_counts(self, capsys):
        cli.print_summary(pass_count=5, warn_count=2, error_count=1, width=40)
        out = capsys.readouterr().out
        assert "通过 5 项" in out
        assert "警告 2 项" in out
        assert "错误 1 项" in out
        assert "检查摘要" in out

    def test_print_summary_only_pass(self, capsys):
        cli.print_summary(pass_count=3, warn_count=0, error_count=0, width=40)
        out = capsys.readouterr().out
        assert "通过 3 项" in out
        assert "警告" not in out
        assert "错误" not in out

    def test_print_summary_only_errors(self, capsys):
        cli.print_summary(pass_count=0, warn_count=0, error_count=2, width=40)
        out = capsys.readouterr().out
        assert "错误 2 项" in out
        assert "通过" not in out


class TestAddCommonArgs:

    def test_adds_path_and_json_args(self):
        parser = argparse.ArgumentParser()
        cli.add_common_args(parser)
        args = parser.parse_args([])
        assert args.path is None
        assert args.json is False

    def test_parses_path(self, tmp_path):
        parser = argparse.ArgumentParser()
        cli.add_common_args(parser)
        args = parser.parse_args(["--path", str(tmp_path)])
        assert args.path == tmp_path

    def test_parses_json_flag(self):
        parser = argparse.ArgumentParser()
        cli.add_common_args(parser)
        args = parser.parse_args(["--json"])
        assert args.json is True

    def test_allows_additional_args(self):
        parser = argparse.ArgumentParser()
        cli.add_common_args(parser)
        parser.add_argument("--fix", action="store_true")
        args = parser.parse_args(["--json", "--fix", "--path", "."])
        assert args.json is True
        assert args.fix is True
