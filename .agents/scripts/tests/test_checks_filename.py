"""lib.checks.filename 单元测试。"""


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
            ("xmnn_bootstrap.pth", ".pth"),
            ("product.env", ".env"),
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

    def test_two_digit_appendix_prefix_allowed(self):
        ok, msg = fn._is_valid("08b-codex-examples.md", ".md")
        assert ok, f"Two-digit appendix prefix should be allowed: {msg}"

    def test_three_digit_prefix_allowed(self):
        ok, msg = fn._is_valid("001-overview-architecture.md", ".md")
        assert ok, f"Three-digit prefix should be allowed: {msg}"

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

    def test_containerfile_variant_names_allowed(self):
        """容器构建文件的形态后缀（如 Containerfile.xmnn-dev）不按扩展名拦截。"""
        for name, ext in [
            ("Containerfile.xmnn-dev", ".xmnn-dev"),
            ("Containerfile.xmnn-runtime", ".xmnn-runtime"),
            ("Containerfile.client", ".client"),
            ("Dockerfile.dev", ".dev"),
        ]:
            ok, msg = fn._is_valid(name, ext)
            assert ok, f"Expected {name} to be valid, got: {msg}"

    def test_containerfile_exemption_keeps_name_checks(self):
        """约定名豁免仅限扩展名检查，名称合法性检查仍然生效。"""
        ok, msg = fn._is_valid("CON.xmnn-dev", ".xmnn-dev")
        assert not ok
        assert "保留名称" in msg

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
        mock_result.stdout = (
            ":100644 100644 00000000 11111111 A\tsrc/main.py\n"
            ":100644 100644 22222222 33333333 M\tdocs/README.md\n"
        )
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

    def test_skips_submodule_gitlink(self, tmp_path):
        """子模块 gitlink（mode=160000）不按文件命名规范检查。

        回归：daoapps.github.io 指针 bump 曾被误判为「扩展名 .io 不允许」，
        导致 chore(submodules) 提交被 pre-commit 拦下。
        """
        mock_result = MagicMock()
        mock_result.stdout = (
            ":160000 160000 f3095a80e f7726e067 M\tprojects/daoapps.github.io\n"
            ":100644 100644 22222222 33333333 M\tdocs/index.md\n"
        )
        with patch.object(fn.subprocess, "run", return_value=mock_result):
            files = fn._get_staged(tmp_path)
        assert files == [tmp_path / "docs/index.md"]

    def test_skips_newly_added_gitlink(self, tmp_path):
        """新增子模块（旧 mode=000000、新 mode=160000）同样跳过。"""
        mock_result = MagicMock()
        mock_result.stdout = ":000000 160000 00000000 aabbccddee A\tprojects/new-repo.io\n"
        with patch.object(fn.subprocess, "run", return_value=mock_result):
            assert fn._get_staged(tmp_path) == []

    def test_ignores_malformed_raw_lines(self, tmp_path):
        """缺制表符或空路径的行不产生结果，也不抛异常。"""
        mock_result = MagicMock()
        mock_result.stdout = ":100644 100644 0 0 A\n\n:no-tab-line\n"
        with patch.object(fn.subprocess, "run", return_value=mock_result):
            assert fn._get_staged(tmp_path) == []

    def test_uses_raw_diff_format(self, tmp_path):
        """必须走 --raw：只有 raw 输出携带 mode，才能识别 gitlink。"""
        mock_result = MagicMock()
        mock_result.stdout = ""
        with patch.object(fn.subprocess, "run", return_value=mock_result) as mock_run:
            fn._get_staged(tmp_path)
        argv = mock_run.call_args[0][0]
        assert "--raw" in argv
        assert "--name-only" not in argv


class TestScanStagedGitlink:
    """_scan(staged_only=True) 对 gitlink 的端到端行为。"""

    def test_gitlink_pointer_bump_has_no_violation(self, tmp_path):
        raw = ":160000 160000 f3095a80e f7726e067 M\tprojects/daoapps.github.io\n"
        mock_result = MagicMock()
        mock_result.stdout = raw
        with patch.object(fn.subprocess, "run", return_value=mock_result):
            violations = fn._scan(tmp_path, staged_only=True)
        assert violations == []

    def test_real_violation_still_caught_in_staged_mode(self, tmp_path):
        """跳过 gitlink 不影响对真实违规文件名的拦截。"""
        mock_result = MagicMock()
        mock_result.stdout = ":100644 100644 0 1 A\tprojects/归档.zip\n"
        with patch.object(fn.subprocess, "run", return_value=mock_result):
            violations = fn._scan(tmp_path, staged_only=True)
        assert len(violations) == 1
        assert "扩展名" in violations[0][1] or "非 ASCII" in violations[0][1]


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

    def test_excludes_non_worktree_prefixes(self, tmp_path):
        (tmp_path / "external" / "bad file.py").parent.mkdir(parents=True)
        (tmp_path / "external" / "bad file.py").write_text("x", encoding="utf-8")
        backup_file = tmp_path / ".meta" / "backup" / "docs" / "中文.md"
        backup_file.parent.mkdir(parents=True)
        backup_file.write_text("x", encoding="utf-8")
        playground_file = tmp_path / "playground" / "reports" / "bad file.c"
        playground_file.parent.mkdir(parents=True)
        playground_file.write_text("x", encoding="utf-8")

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

