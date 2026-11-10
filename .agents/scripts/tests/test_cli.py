"""lib.cli 单元测试。"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import io
import sys

import pytest

from lib import cli


class TestIsTty:
    """_is_tty 安全检测函数的边界测试。"""

    def test_tty_stream_returns_true(self, monkeypatch):
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
        assert cli._is_tty(sys.stdout) is True

    def test_non_tty_stream_returns_false(self, monkeypatch):
        monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
        assert cli._is_tty(sys.stdout) is False

    def test_stream_without_isatty_method_returns_false(self):
        class DummyStream:
            pass
        assert cli._is_tty(DummyStream()) is False

    def test_stream_with_isatty_none_returns_false(self):
        class DummyStream:
            isatty = None
        assert cli._is_tty(DummyStream()) is False

    def test_stream_with_isatty_not_callable_returns_false(self):
        class DummyStream:
            isatty = True
        assert cli._is_tty(DummyStream()) is False

    def test_isatty_raises_exception_returns_false(self):
        class DummyStream:
            def isatty(self):
                raise OSError("bad fd")
        assert cli._is_tty(DummyStream()) is False

    def test_default_uses_sys_stdout(self, monkeypatch):
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
        assert cli._is_tty() is True


class TestSupportsUnicode:
    """_supports_unicode 编码检测函数的边界测试。"""

    def _make_stream(self, *, is_tty=True, encoding="utf-8"):
        class S:
            def isatty(self):
                return is_tty
            def __getattr__(self, name):
                if name == "encoding":
                    return encoding
                raise AttributeError(name)
        return S()

    def test_tty_utf8_returns_true(self):
        assert cli._supports_unicode(self._make_stream(is_tty=True, encoding="utf-8")) is True

    def test_tty_utf8_dash_returns_true(self):
        assert cli._supports_unicode(self._make_stream(is_tty=True, encoding="UTF-8")) is True

    def test_tty_utf8_sig_returns_true(self):
        assert cli._supports_unicode(self._make_stream(is_tty=True, encoding="utf-8-sig")) is True

    def test_tty_cp65001_windows_utf8_returns_true(self):
        assert cli._supports_unicode(self._make_stream(is_tty=True, encoding="cp65001")) is True

    def test_tty_gbk_returns_false(self):
        assert cli._supports_unicode(self._make_stream(is_tty=True, encoding="gbk")) is False

    def test_tty_cp936_returns_false(self):
        assert cli._supports_unicode(self._make_stream(is_tty=True, encoding="cp936")) is False

    def test_non_tty_utf8_returns_false(self):
        assert cli._supports_unicode(self._make_stream(is_tty=False, encoding="utf-8")) is False

    def test_non_tty_gbk_returns_false(self):
        assert cli._supports_unicode(self._make_stream(is_tty=False, encoding="gbk")) is False

    def test_encoding_none_returns_false(self):
        class S:
            def isatty(self): return True
            @property
            def encoding(self): return None
        assert cli._supports_unicode(S()) is False

    def test_encoding_non_string_returns_false(self):
        class S:
            def isatty(self): return True
            @property
            def encoding(self): return 123
        assert cli._supports_unicode(S()) is False

    def test_stream_without_encoding_attr_returns_false(self):
        class S:
            def isatty(self): return True
        assert cli._supports_unicode(S()) is False

    def test_stream_without_isatty_returns_false(self):
        class S:
            @property
            def encoding(self): return "utf-8"
        assert cli._supports_unicode(S()) is False


class TestSymbol:
    """_symbol 函数边界测试。"""

    def test_pass_returns_ascii_when_no_unicode(self, monkeypatch):
        monkeypatch.setattr(cli, "_supports_unicode", lambda: False)
        assert cli._symbol("pass") == "[PASS]"

    def test_warn_returns_ascii_when_no_unicode(self, monkeypatch):
        monkeypatch.setattr(cli, "_supports_unicode", lambda: False)
        assert cli._symbol("warn") == "[WARN]"

    def test_error_returns_ascii_when_no_unicode(self, monkeypatch):
        monkeypatch.setattr(cli, "_supports_unicode", lambda: False)
        assert cli._symbol("error") == "[FAIL]"

    def test_pass_returns_unicode_checkmark(self, monkeypatch):
        monkeypatch.setattr(cli, "_supports_unicode", lambda: True)
        assert cli._symbol("pass") == "✓"

    def test_warn_returns_unicode_warning(self, monkeypatch):
        monkeypatch.setattr(cli, "_supports_unicode", lambda: True)
        assert cli._symbol("warn") == "⚠"

    def test_error_returns_unicode_ballot(self, monkeypatch):
        monkeypatch.setattr(cli, "_supports_unicode", lambda: True)
        assert cli._symbol("error") == "✗"

    def test_invalid_kind_ascii_mode_returns_fallback_not_crash(self, monkeypatch):
        monkeypatch.setattr(cli, "_supports_unicode", lambda: False)
        result = cli._symbol("invalid_kind")
        assert isinstance(result, str)
        assert "PASS" not in result

    def test_invalid_kind_unicode_mode_returns_fallback_not_crash(self, monkeypatch):
        monkeypatch.setattr(cli, "_supports_unicode", lambda: True)
        result = cli._symbol("invalid_kind")
        assert isinstance(result, str)

    def test_none_kind_does_not_crash(self, monkeypatch):
        monkeypatch.setattr(cli, "_supports_unicode", lambda: False)
        cli._symbol(None)


class TestSetupSafeOutput:
    """setup_safe_output 函数测试。"""

    def test_does_not_crash_with_normal_streams(self):
        cli.setup_safe_output()

    def test_does_not_crash_with_streams_without_reconfigure(self):
        class DummyOut:
            def write(self, s): pass
            def flush(self): pass
        class DummyErr:
            def write(self, s): pass
            def flush(self): pass
        old_out, old_err = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = DummyOut(), DummyErr()
            cli.setup_safe_output()
        finally:
            sys.stdout, sys.stderr = old_out, old_err


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

    def test_stream_without_isatty_returns_plain(self):
        class DummyStream:
            pass
        result = cli._color("hello", "\033[92m", stream=DummyStream())
        assert result == "hello"


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
        assert "[PASS]" not in out

    def test_print_warn_unicode_mode(self, capsys, monkeypatch):
        monkeypatch.setattr(cli, "_supports_unicode", lambda: True)
        cli.print_warn("be careful")
        out = capsys.readouterr().out
        assert "be careful" in out
        assert "⚠" in out
        assert "[WARN]" not in out

    def test_print_error_unicode_mode(self, capsys, monkeypatch):
        monkeypatch.setattr(cli, "_supports_unicode", lambda: True)
        cli.print_error("something wrong")
        out = capsys.readouterr().out
        assert "something wrong" in out
        assert "✗" in out
        assert "[FAIL]" not in out

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

    def test_print_summary_zero_counts(self, capsys):
        cli.print_summary(pass_count=0, warn_count=0, error_count=0, width=40)
        out = capsys.readouterr().out
        assert "检查摘要" in out


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


class TestAddKnowledgeFilterArgs:
    """add_knowledge_filter_args 参数注册测试。

    该函数内部为惰性导入，`import lib.cli` 不会触发；一旦目标模块被拆分或改名，
    只有真正调用时才抛 ModuleNotFoundError。本组用例保证调用路径始终可达。
    """

    def _build_parser(self):
        parser = argparse.ArgumentParser()
        cli.add_knowledge_filter_args(parser)
        return parser

    def _choice_action(self, parser, dest):
        return next(a for a in parser._actions if a.dest == dest)

    def test_registers_three_filters(self):
        parser = self._build_parser()
        dests = {a.dest for a in parser._actions}
        assert {"knowledge_type", "validation_status", "security_level"} <= dests

    def test_type_choices_match_knowledge_classification(self):
        from lib.knowledge_classification import VALID_KNOWLEDGE_TYPES

        action = self._choice_action(self._build_parser(), "knowledge_type")
        assert action.choices == sorted(VALID_KNOWLEDGE_TYPES)

    def test_status_choices_match_knowledge_classification(self):
        from lib.knowledge_classification import VALID_VALIDATION_STATUSES

        action = self._choice_action(self._build_parser(), "validation_status")
        assert action.choices == sorted(VALID_VALIDATION_STATUSES)

    def test_level_choices_are_security_levels(self):
        action = self._choice_action(self._build_parser(), "security_level")
        assert action.choices == ["public", "internal", "confidential"]

    def test_parses_type_and_status_values(self):
        from lib.knowledge_classification import (
            VALID_KNOWLEDGE_TYPES,
            VALID_VALIDATION_STATUSES,
        )

        knowledge_type = sorted(VALID_KNOWLEDGE_TYPES)[0]
        validation_status = sorted(VALID_VALIDATION_STATUSES)[0]
        args = self._build_parser().parse_args(
            ["--type", knowledge_type, "--status", validation_status, "--level", "public"]
        )
        assert args.knowledge_type == knowledge_type
        assert args.validation_status == validation_status
        assert args.security_level == "public"

