"""lib.checks.gitignore 单元测试。"""

import argparse
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from lib.checks import gitignore as gi
from constants import REQUIRED_RULES


@pytest.fixture
def args_ns():
    return argparse.Namespace()


class TestCheckRules:
    """_check_rules 内部函数测试。"""

    def test_missing_gitignore_file(self, tmp_path):
        """gitignore 文件不存在时返回错误。"""
        missing = tmp_path / ".gitignore"
        result = gi._check_rules(missing)
        assert len(result) == 1
        assert "文件不存在" in result[0]

    def test_all_rules_present(self, tmp_path):
        """所有规则都存在时返回空列表。"""
        gi_path = tmp_path / ".gitignore"
        gi_path.write_text("\n".join(REQUIRED_RULES), encoding="utf-8")
        result = gi._check_rules(gi_path)
        assert result == []

    def test_some_rules_missing(self, tmp_path):
        """部分规则缺失时返回缺失的规则列表。"""
        gi_path = tmp_path / ".gitignore"
        gi_path.write_text("vendor/\n.temp/\n", encoding="utf-8")
        result = gi._check_rules(gi_path)
        assert "__pycache__/" in result
        assert "vendor/" not in result

    def test_empty_gitignore(self, tmp_path):
        """空 gitignore 文件返回所有规则为缺失。"""
        gi_path = tmp_path / ".gitignore"
        gi_path.write_text("", encoding="utf-8")
        result = gi._check_rules(gi_path)
        assert len(result) == len(REQUIRED_RULES)


class TestCheckGitStatus:
    """_check_git_status 内部函数测试。"""

    def test_clean_status(self, tmp_path):
        """git status 干净时返回空列表。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        with patch.object(gi.subprocess, "run", return_value=mock_result):
            result = gi._check_git_status(tmp_path)
        assert result == []

    def test_status_with_violations(self, tmp_path):
        """git status 包含临时路径时返回违规列表。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "?? vendor/something.py\n?? .temp/cache.tmp\n M src/main.py\n"
        mock_result.stderr = ""
        with patch.object(gi.subprocess, "run", return_value=mock_result):
            result = gi._check_git_status(tmp_path)
        assert len(result) == 2
        assert any("vendor/" in v for v in result)
        assert any(".temp/" in v for v in result)
        assert not any("src/main.py" in v for v in result)

    def test_git_command_failure(self, tmp_path):
        """git 命令返回非零退出码时报告错误。"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "fatal: not a git repository"
        with patch.object(gi.subprocess, "run", return_value=mock_result):
            result = gi._check_git_status(tmp_path)
        assert len(result) == 1
        assert "执行失败" in result[0]

    def test_git_not_found(self, tmp_path):
        """git 命令不存在时捕获 FileNotFoundError。"""
        with patch.object(gi.subprocess, "run", side_effect=FileNotFoundError):
            result = gi._check_git_status(tmp_path)
        assert len(result) == 1
        assert "git 命令未找到" in result[0]

    def test_deduplicates_violations(self, tmp_path):
        """同一行匹配多个临时路径时只记录一次（break 逻辑）。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "?? vendor/__pycache__/test.cpython-313.pyc\n"
        mock_result.stderr = ""
        with patch.object(gi.subprocess, "run", return_value=mock_result):
            result = gi._check_git_status(tmp_path)
        assert len(result) == 1


class TestRun:
    """run() 集成测试（mock subprocess 和 print）。"""

    def test_all_passes(self, tmp_path, args_ns, capsys):
        """所有检查通过返回 0。"""
        gi_path = tmp_path / ".gitignore"
        gi_path.write_text("\n".join(REQUIRED_RULES), encoding="utf-8")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        with patch.object(gi.subprocess, "run", return_value=mock_result):
            ret = gi.run(tmp_path, args_ns)
        assert ret == 0
        out = capsys.readouterr().out
        assert "通过" in out
        assert "验证通过" in out

    def test_missing_rules_returns_1(self, tmp_path, args_ns, capsys):
        """.gitignore 缺少规则时返回 1 且不执行 git status 检查。"""
        gi_path = tmp_path / ".gitignore"
        gi_path.write_text("vendor/\n", encoding="utf-8")
        ret = gi.run(tmp_path, args_ns)
        assert ret == 1
        out = capsys.readouterr().out
        assert "失败: 缺少以下规则" in out
        assert "git status" not in out

    def test_git_violations_returns_1(self, tmp_path, args_ns, capsys):
        """规则齐全但 git status 有违规时返回 1。"""
        gi_path = tmp_path / ".gitignore"
        gi_path.write_text("\n".join(REQUIRED_RULES), encoding="utf-8")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "?? .temp/test.txt\n"
        mock_result.stderr = ""
        with patch.object(gi.subprocess, "run", return_value=mock_result):
            ret = gi.run(tmp_path, args_ns)
        assert ret == 1
        out = capsys.readouterr().out
        assert "通过: 所有" in out
        assert "失败: git status" in out
