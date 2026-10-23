"""lib.checks.gitignore 单元测试。"""


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
from unittest.mock import patch, MagicMock

import pytest

from lib.checks import gitignore as gi
from constants import REQUIRED_RULES


@pytest.fixture
def args_ns():
    return argparse.Namespace()


def _index_payload(records) -> bytes:
    """构造 git ls-files -s -z 的字节输出。

    records: [(mode, path), ...]，mode 取自索引（"100644" 普通文件 / "160000" gitlink）。
    """
    blob = "".join(
        f"{mode} 0000000000000000000000000000000000000000 0\t{path}\0"
        for mode, path in records
    )
    return blob.encode("utf-8")


def _make_mock_run(index_records=(), ignored=(), ls_files_rc=0, ls_files_stderr=b"",
                   check_ignore_rc=None, calls=None):
    """创建区分 git ls-files 与 git check-ignore 调用的 mock。

    ignored —— 会被 .gitignore 规则命中的路径集合（模拟 check-ignore --no-index 的输出）。
    calls  —— 可选列表，用于记录实际发生的 git 调用命令。
    """
    def mock_run(cmd, **kwargs):
        if calls is not None:
            calls.append(list(cmd))
        if "ls-files" in cmd:
            r = MagicMock()
            r.returncode = ls_files_rc
            r.stdout = _index_payload(index_records)
            r.stderr = ls_files_stderr
            return r
        if "check-ignore" in cmd:
            paths = [
                p for p in kwargs["input"].decode("utf-8").split("\0")
                if p
            ]
            matched = [p for p in paths if p in ignored]
            r = MagicMock()
            r.returncode = (check_ignore_rc if check_ignore_rc is not None
                            else (0 if matched else 1))
            r.stdout = ("".join(f"{p}\0" for p in matched)).encode("utf-8")
            r.stderr = b""
            return r
        return MagicMock(returncode=0)

    return mock_run


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


class TestPickTempCandidates:
    """_pick_temp_candidates 内部函数测试。"""

    def test_gitlink_excluded(self):
        """gitlink（mode 160000）不参与临时依赖判定。"""
        entries = [("160000", "vendor/flexloop"), ("100644", "vendor/README.md")]
        assert gi._pick_temp_candidates(entries) == ["vendor/README.md"]

    def test_plain_path_excluded(self):
        """不命中临时依赖路径的条目被排除。"""
        entries = [("100644", "src/main.py"), ("100644", "docs/README.md")]
        assert gi._pick_temp_candidates(entries) == []

    def test_temp_path_picked(self):
        """命中临时依赖路径的普通文件被选中。"""
        entries = [("100644", ".temp/x.txt"), ("100644", "a/__pycache__/b.pyc")]
        assert gi._pick_temp_candidates(entries) == [".temp/x.txt", "a/__pycache__/b.pyc"]


class TestCheckTrackedTempDeps:
    """_check_tracked_temp_deps 内部函数测试。"""

    def test_clean_index(self, tmp_path):
        """索引中无临时依赖时返回空列表，且不调用 check-ignore。"""
        calls = []
        mock = _make_mock_run(index_records=[("100644", "src/main.py")], calls=calls)
        with patch.object(gi.subprocess, "run", side_effect=mock):
            result = gi._check_tracked_temp_deps(tmp_path)
        assert result == []
        assert not any("check-ignore" in " ".join(c) for c in calls)

    def test_gitlink_only(self, tmp_path):
        """仅有子模块 gitlink 时不产生违规。"""
        mock = _make_mock_run(index_records=[("160000", "vendor/flexloop")])
        with patch.object(gi.subprocess, "run", side_effect=mock):
            result = gi._check_tracked_temp_deps(tmp_path)
        assert result == []

    def test_tracked_and_ignored_temp_dep_is_violation(self, tmp_path):
        """已跟踪且被忽略规则覆盖的临时依赖判为违规。"""
        mock = _make_mock_run(
            index_records=[("100644", ".temp/cache.bin"), ("100644", "src/main.py")],
            ignored={".temp/cache.bin"},
        )
        with patch.object(gi.subprocess, "run", side_effect=mock):
            result = gi._check_tracked_temp_deps(tmp_path)
        assert len(result) == 1
        assert ".temp/cache.bin" in result[0]

    def test_tracked_but_not_ignored_path_not_violation(self, tmp_path):
        """已跟踪但未被忽略规则覆盖的路径（如 vendor/README.md）不判违规。"""
        mock = _make_mock_run(index_records=[("100644", "vendor/README.md")])
        with patch.object(gi.subprocess, "run", side_effect=mock):
            result = gi._check_tracked_temp_deps(tmp_path)
        assert result == []

    def test_ls_files_failure(self, tmp_path):
        """git ls-files 返回非零退出码时报告错误。"""
        mock = _make_mock_run(ls_files_rc=128, ls_files_stderr=b"fatal: not a git repository")
        with patch.object(gi.subprocess, "run", side_effect=mock):
            result = gi._check_tracked_temp_deps(tmp_path)
        assert len(result) == 1
        assert "执行失败" in result[0]

    def test_ls_files_timeout(self, tmp_path):
        """git ls-files 超时时报告错误而非无限期挂起。"""
        def mock_run(cmd, **kwargs):
            raise subprocess.TimeoutExpired(cmd, gi.GIT_TIMEOUT)
        with patch.object(gi.subprocess, "run", side_effect=mock_run):
            result = gi._check_tracked_temp_deps(tmp_path)
        assert len(result) == 1
        assert "超时" in result[0]

    def test_check_ignore_failure(self, tmp_path):
        """git check-ignore 返回异常退出码时报告错误。"""
        mock = _make_mock_run(
            index_records=[("100644", ".temp/cache.bin")],
            check_ignore_rc=128,
        )
        with patch.object(gi.subprocess, "run", side_effect=mock):
            result = gi._check_tracked_temp_deps(tmp_path)
        assert len(result) == 1
        assert "执行失败" in result[0]

    def test_git_not_found(self, tmp_path):
        """git 命令不存在时捕获 FileNotFoundError。"""
        with patch.object(gi.subprocess, "run", side_effect=FileNotFoundError):
            result = gi._check_tracked_temp_deps(tmp_path)
        assert len(result) == 1
        assert "git 命令未找到" in result[0]


class TestRun:
    """run() 集成测试（mock subprocess 和 print）。"""

    def test_all_passes(self, tmp_path, args_ns, capsys):
        """所有检查通过返回 0。"""
        gi_path = tmp_path / ".gitignore"
        gi_path.write_text("\n".join(REQUIRED_RULES), encoding="utf-8")

        mock = _make_mock_run(index_records=[("100644", "src/main.py")])
        with patch.object(gi.subprocess, "run", side_effect=mock):
            ret = gi.run(tmp_path, args_ns)
        assert ret == 0
        out = capsys.readouterr().out
        assert "通过" in out
        assert "验证通过" in out

    def test_missing_rules_returns_1(self, tmp_path, args_ns, capsys):
        """.gitignore 缺少规则时返回 1 且不执行索引检查。"""
        gi_path = tmp_path / ".gitignore"
        gi_path.write_text("vendor/\n", encoding="utf-8")
        calls = []
        mock = _make_mock_run(calls=calls)
        with patch.object(gi.subprocess, "run", side_effect=mock):
            ret = gi.run(tmp_path, args_ns)
        assert ret == 1
        out = capsys.readouterr().out
        assert "失败: 缺少以下规则" in out
        assert calls == []

    def test_violation_returns_1(self, tmp_path, args_ns, capsys):
        """规则齐全但索引中存在临时依赖时返回 1。"""
        gi_path = tmp_path / ".gitignore"
        gi_path.write_text("\n".join(REQUIRED_RULES), encoding="utf-8")

        mock = _make_mock_run(
            index_records=[("100644", ".temp/test.txt")],
            ignored={".temp/test.txt"},
        )
        with patch.object(gi.subprocess, "run", side_effect=mock):
            ret = gi.run(tmp_path, args_ns)
        assert ret == 1
        out = capsys.readouterr().out
        assert "通过: 所有" in out
        assert "失败: 版本控制索引中存在本应被忽略的临时依赖" in out
