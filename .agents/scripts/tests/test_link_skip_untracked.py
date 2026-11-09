"""链接检查跳过集测试：未跟踪目录跳过 + 免除资格硬约束。

背景：本地语料库（.corpus/）、AI 工具目录（.workbuddy/）、本地缓存（.cache/）
曾贡献 1.4 万条假断链，把真实问题淹没。修复方向是「只跳过未被 git 跟踪的内容」，
并强制校验免除资格——被跳过的路径必须未被 git 跟踪，或是指向已跟踪目录的
联接别名。

覆盖：
- S-1: 未跟踪目录下的 Markdown 被跳过；
- S-2: 同一目录里受 git 跟踪的文件必须照常检查（不许前缀硬挡）；
- S-3: 审计函数对违规跳过抛错（硬约束可执行）；
- S-4: 去重优先保留字面路径，避免联接别名视图挤掉真实路径。
"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from lib.markdown import (
    JUNCTION_ALIAS_REASON,
    UNTRACKED_REASON,
    audit_skipped_paths,
    filter_untracked_paths,
    is_literal_path,
)

GIT = shutil.which("git")

pytestmark = pytest.mark.skipif(GIT is None, reason="需要 git 可执行文件")


def _init_repo(root: Path) -> None:
    """初始化临时 git 仓库（无需提交，git add 后即可被 ls-files 收录）。"""
    subprocess.run([GIT, "-C", str(root), "init", "-q"], check=True)


def _stage(root: Path, rel: str) -> None:
    subprocess.run([GIT, "-C", str(root), "add", rel], check=True)


class TestUntrackedSkip:
    """未跟踪目录的跳过决策。"""

    def test_untracked_file_in_skip_dir_is_skipped(self, tmp_path):
        """未跟踪的本地语料必须被跳过——修复前它贡献了大量假断链。"""
        _init_repo(tmp_path)
        loose = tmp_path / ".corpus" / "loose.md"
        loose.parent.mkdir()
        loose.write_text("# 本地语料\n\n[断链](records.md)\n", encoding="utf-8")

        kept, stats = filter_untracked_paths([loose], tmp_path, {".corpus"})

        assert kept == []
        assert stats["total"] == 1
        assert stats[UNTRACKED_REASON] == 1

    def test_tracked_file_in_skip_dir_is_kept(self, tmp_path):
        """同一目录里受 git 跟踪的文件必须照常检查，禁止前缀硬挡。"""
        _init_repo(tmp_path)
        tracked = tmp_path / ".corpus" / "tracked.md"
        tracked.parent.mkdir()
        tracked.write_text("# 受跟踪\n\n[断链](missing.md)\n", encoding="utf-8")
        _stage(tmp_path, ".corpus/tracked.md")

        kept, stats = filter_untracked_paths([tracked], tmp_path, {".corpus"})

        assert kept == [tracked]
        assert stats.get("total", 0) == 0

    def test_file_outside_skip_dirs_is_kept(self, tmp_path):
        """普通文档目录不受跳过集影响。"""
        _init_repo(tmp_path)
        doc = tmp_path / "docs" / "guide.md"
        doc.parent.mkdir()
        doc.write_text("# 指南\n", encoding="utf-8")

        kept, stats = filter_untracked_paths([doc], tmp_path, {".corpus"})

        assert kept == [doc]
        assert stats == {}

    def test_file_outside_repo_is_kept(self, tmp_path):
        """扫描根之外的文件无法验证跟踪状态，必须保留而不是跳过。"""
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        outside = tmp_path / "other" / ".corpus" / "x.md"
        outside.parent.mkdir(parents=True)
        outside.write_text("# 仓外\n", encoding="utf-8")

        kept, stats = filter_untracked_paths([outside], repo, {".corpus"})

        assert kept == [outside]
        assert stats.get("total", 0) == 0


class TestSkipAudit:
    """硬约束：被跳过的路径必须具备免除资格。"""

    def test_audit_rejects_tracked_file(self, tmp_path):
        """被跳过却受 git 跟踪 → 抛错，不允许静默藏起真断链。"""
        _init_repo(tmp_path)
        doc = tmp_path / "docs" / "ok.md"
        doc.parent.mkdir()
        doc.write_text("# ok\n", encoding="utf-8")
        _stage(tmp_path, "docs/ok.md")

        with pytest.raises(RuntimeError, match="已被 git 跟踪"):
            audit_skipped_paths({doc: UNTRACKED_REASON}, {"docs/ok.md"}, tmp_path)

    def test_audit_rejects_skip_without_index(self, tmp_path):
        """git 索引不可用时拒绝跳过，宁可不跳过也不能误挡。"""
        with pytest.raises(RuntimeError, match="缺少 git 索引"):
            audit_skipped_paths({tmp_path / "x.md": UNTRACKED_REASON}, None, tmp_path)

    def test_audit_rejects_fake_alias_claim(self, tmp_path):
        """声明为联接别名但实际不是别名 → 抛错。"""
        _init_repo(tmp_path)
        doc = tmp_path / ".workbuddy" / "x.md"
        doc.parent.mkdir()
        doc.write_text("x", encoding="utf-8")

        with pytest.raises(RuntimeError, match="联接别名"):
            audit_skipped_paths({doc: JUNCTION_ALIAS_REASON}, set(), tmp_path)

    def test_audit_accepts_untracked_file(self, tmp_path):
        """未跟踪文件具备免除资格，审计通过。"""
        _init_repo(tmp_path)
        doc = tmp_path / ".cache" / "x.md"
        doc.parent.mkdir()
        doc.write_text("x", encoding="utf-8")

        audit_skipped_paths({doc: UNTRACKED_REASON}, set(), tmp_path)


def _make_dir_link(link: Path, target: Path) -> bool:
    """创建目录联接/符号链接，失败返回 False（权限不足时整类跳过）。"""
    try:
        if sys.platform == "win32":
            rc = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(link), str(target)],
                capture_output=True,
            )
            return rc.returncode == 0 and link.exists()
        link.symlink_to(target, target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        return False


class TestLiteralPathPreference:
    """去重必须优先保留字面路径，否则别名视图会挤掉真实路径。

    实测背景：`.workbuddy/skills` 是指向 `.agents/skills` 的目录联接，
    而 check-links 的既有去重按 resolve() 只留「先到者」。别名若先到，
    跳过集就会连同真实路径的断链一起吞掉——这正是硬约束要防的误伤。
    """

    def test_plain_path_is_literal(self, tmp_path):
        doc = tmp_path / "docs" / "guide.md"
        doc.parent.mkdir()
        doc.write_text("# x\n", encoding="utf-8")
        assert is_literal_path(doc) is True

    def test_alias_path_is_not_literal(self, tmp_path):
        real = tmp_path / ".agents" / "skills"
        real.mkdir(parents=True)
        (real / "SKILL.md").write_text("# x\n", encoding="utf-8")
        alias = tmp_path / ".workbuddy" / "skills"
        alias.parent.mkdir()
        if not _make_dir_link(alias, real):
            pytest.skip("当前环境无法创建目录联接/符号链接")

        assert is_literal_path(alias / "SKILL.md") is False
        assert is_literal_path(real / "SKILL.md") is True
