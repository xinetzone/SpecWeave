"""lib.checks.filename 单元测试。"""

import argparse
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from lib.checks import filename as fn


@pytest.fixture
def args_default():
    return argparse.Namespace(directory=None, fix=False, staged=False)


@pytest.fixture
def args_staged():
    return argparse.Namespace(directory=None, fix=False, staged=True)


class TestIsValid:
    """_is_valid 测试。"""

    def test_valid_filenames(self):
        """合法文件名返回 True。"""
        valid_names = [
            ("main.py", ".py"),
            ("utils.js", ".js"),
            ("my-component.tsx", ".tsx"),
            ("README.md", ".md"),
            ("config.yaml", ".yaml"),
            ("build.sh", ".sh"),
            ("test-file_name.py", ".py"),
            ("Cargo.toml", ".toml"),
            (".gitignore", ""),
        ]
        for name, ext in valid_names:
            ok, msg = fn._is_valid(name, ext)
            assert ok, f"Expected {name} to be valid, got: {msg}"

    def test_chinese_characters(self):
        assert fn._is_valid("文档.md", ".md") == (False, "包含非 ASCII 字符（中文或其他）: 文档.md")

    def test_spaces_in_name(self):
        ok, msg = fn._is_valid("my file.py", ".py")
        assert not ok
        assert "空格" in msg

    def test_starts_with_number(self):
        ok, msg = fn._is_valid("1test.py", ".py")
        assert not ok
        assert "数字开头" in msg

    def test_date_prefix_allowed(self):
        """日期前缀（YYYY-MM-DD-）允许以数字开头。"""
        ok, msg = fn._is_valid("2026-06-27-notes.md", ".md")
        assert ok, f"Date prefix should be allowed: {msg}"

    def test_two_digit_prefix_allowed(self):
        ok, msg = fn._is_valid("01-intro.md", ".md")
        assert ok, f"Two-digit prefix should be allowed: {msg}"

    def test_consecutive_hyphens(self):
        ok, msg = fn._is_valid("my--file.py", ".py")
        assert not ok
        assert "连续连字符" in msg

    def test_reserved_name(self):
        ok, msg = fn._is_valid("CON.py", ".py")
        assert not ok
        assert "保留名称" in msg
        ok2, _ = fn._is_valid("NUL.txt", ".txt")
        assert not ok2

    def test_disallowed_extension(self):
        ok, msg = fn._is_valid("archive.zip", ".zip")
        assert not ok
        assert "扩展名" in msg

    def test_none_extension_skipped(self):
        """extension 为 None 时不检查扩展名。"""
        ok, _ = fn._is_valid("Makefile", None)
        assert ok

    def test_com1_reserved(self):
        ok, _ = fn._is_valid("COM1", None)
        assert not ok


class TestGetStaged:
    """_get_staged 测试（mock subprocess）。"""

    def test_returns_staged_files(self, tmp_path):
        mock_result = MagicMock()
        mock_result.stdout = "src/main.py\ndocs/README.md\n"
        with patch.object(fn.subprocess, "run", return_value=mock_result):
            files = fn._get_staged(tmp_path)
        assert len(files) == 2
        assert files[0] == tmp_path / "src/main.py"
        assert files[1] == tmp_path / "docs/README.md"

    def test_empty_staging(self, tmp_path):
        mock_result = MagicMock()
        mock_result.stdout = ""
        with patch.object(fn.subprocess, "run", return_value=mock_result):
            files = fn._get_staged(tmp_path)
        assert files == []


class TestScan:
    """_scan 测试。"""

    def test_clean_directory(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hi')", encoding="utf-8")
        (tmp_path / "README.md").write_text("# Hi", encoding="utf-8")
        violations = fn._scan(tmp_path, staged_only=False)
        assert violations == []

    def test_detects_chinese_filename(self, tmp_path):
        (tmp_path / "文档.md").write_text("中文", encoding="utf-8")
        (tmp_path / "main.py").write_text("ok", encoding="utf-8")
        violations = fn._scan(tmp_path, staged_only=False)
        assert len(violations) == 1
        assert "文档.md" in violations[0][0].name

    def test_excludes_venv_and_temp_dirs(self, tmp_path):
        (tmp_path / ".venv").mkdir()
        (tmp_path / ".venv" / "中文.py").write_text("x", encoding="utf-8")
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "测试.pyc").write_text("x", encoding="utf-8")
        violations = fn._scan(tmp_path, staged_only=False)
        assert violations == []

    def test_excluded_files_skipped(self, tmp_path):
        """EXCLUDED_FILES 中的文件跳过检查。"""
        for fname in fn.EXCLUDED_FILES:
            (tmp_path / fname).write_text("x", encoding="utf-8")
        violations = fn._scan(tmp_path, staged_only=False)
        assert violations == []

    def test_detects_multiple_violations(self, tmp_path):
        (tmp_path / "bad file.py").write_text("x", encoding="utf-8")
        (tmp_path / "中文.txt").write_text("x", encoding="utf-8")
        (tmp_path / "good.py").write_text("x", encoding="utf-8")
        violations = fn._scan(tmp_path, staged_only=False)
        assert len(violations) == 2


class TestRun:
    """run() 集成测试。"""

    def test_all_clean(self, tmp_path, args_default, capsys):
        (tmp_path / "main.py").write_text("ok", encoding="utf-8")
        ret = fn.run(tmp_path, args_default)
        assert ret == 0
        out = capsys.readouterr().out
        assert "所有文件名符合规范" in out

    def test_violations_found(self, tmp_path, args_default, capsys):
        (tmp_path / "bad file.py").write_text("x", encoding="utf-8")
        ret = fn.run(tmp_path, args_default)
        assert ret == 1
        out = capsys.readouterr().out
        assert "发现问题" in out
        assert "bad file.py" in out

    def test_staged_mode_calls_get_staged(self, tmp_path, args_staged, capsys):
        mock_result = MagicMock()
        mock_result.stdout = ""
        with patch.object(fn.subprocess, "run", return_value=mock_result) as mock_run:
            ret = fn.run(tmp_path, args_staged)
        assert ret == 0
        mock_run.assert_called_once()
        assert "--cached" in mock_run.call_args[0][0]
