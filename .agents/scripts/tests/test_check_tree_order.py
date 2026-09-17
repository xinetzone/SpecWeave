"""check-tree-order.py 单元测试。

测试覆盖：
- 排序键等价性（git base_name_compare：目录名等价于 name + "/"）
- tree 原始字节解析与相邻越序判定
- 端到端：临时仓库中手工写入非规范序 tree 必须被拦下，规范序 tree 必须放行
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

import importlib.util
import hashlib
import subprocess
import sys
import zlib
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent
_SPEC_PATH = SCRIPTS_DIR / "check-tree-order.py"
_spec = importlib.util.spec_from_file_location("check_tree_order", _SPEC_PATH)
cto = importlib.util.module_from_spec(_spec)
sys.modules["check_tree_order"] = cto
_spec.loader.exec_module(cto)


def _entry(mode: bytes, name: bytes, sha_byte: int) -> bytes:
    """构造一个 tree 条目（sha 用固定字节填充，测试不关心真实对象）。"""
    return mode + b" " + name + b"\x00" + bytes([sha_byte]) * 20


class TestSortKey:
    """排序键等价性测试。"""

    def test_file_order_is_plain_byte_order(self):
        assert cto.sort_key(b"100644", b"README.md") < cto.sort_key(b"100644", b"index.md")

    def test_directory_sorts_after_same_prefix_file(self):
        # base_name_compare：目录 "a" 视作 "a/"，而 "/" (0x2F) > "." (0x2E)
        assert cto.sort_key(b"40000", b"a") > cto.sort_key(b"100644", b"a.txt")

    def test_directory_sorts_before_longer_name(self):
        assert cto.sort_key(b"40000", b"a") < cto.sort_key(b"100644", b"ab")

    def test_six_digit_directory_mode_supported(self):
        assert cto.sort_key(b"040000", b"a") == cto.sort_key(b"40000", b"a")


class TestFindViolations:
    """tree 原始字节解析与越序判定测试。"""

    def test_canonical_order_passes(self):
        content = _entry(b"100644", b"README.md", 1) + _entry(b"100644", b"index.md", 2)
        assert cto.find_violations(content) == []

    def test_directory_after_file_with_same_prefix_is_canonical(self):
        # 规范序：a.txt 在目录 a 之前
        content = _entry(b"100644", b"a.txt", 1) + _entry(b"40000", b"a", 2)
        assert cto.find_violations(content) == []

    def test_swapped_entries_detected(self):
        content = _entry(b"100644", b"index.md", 1) + _entry(b"100644", b"README.md", 2)
        violations = cto.find_violations(content)
        assert len(violations) == 1
        assert violations[0]["left"] == "index.md"
        assert violations[0]["right"] == "README.md"
        assert violations[0]["duplicate"] is False

    def test_duplicate_entries_flagged(self):
        content = _entry(b"100644", b"a.txt", 1) + _entry(b"100644", b"a.txt", 2)
        violations = cto.find_violations(content)
        assert len(violations) == 1
        assert violations[0]["duplicate"] is True


def _run_git(repo: Path, *args: str, input_bytes: bytes | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "--no-optional-locks", *args],
        cwd=str(repo),
        input=input_bytes,
        capture_output=True,
    )


def _init_repo(repo: Path) -> None:
    _run_git(repo, "init", "-q")
    _run_git(repo, "config", "user.name", "tree-order-test")
    _run_git(repo, "config", "user.email", "tree-order-test@example.com")


def _write_tree_object(repo: Path, content: bytes) -> str:
    """手工写入松散 tree 对象，复现非规范序 tree 的产生方式。

    不能走 `git hash-object -w`：现代 git 会对写入对象做 fsck 并直接拒绝
    （``treeNotSorted: not properly sorted`` + ``refusing to create malformed
    object``）。历史事故中的坏对象正是由绕过 git 的手写脚本直接压缩落盘产生的，
    这里用同样方式复现。
    """
    payload = b"tree " + str(len(content)).encode() + b"\x00" + content
    sha = hashlib.sha1(payload).hexdigest()
    obj_dir = repo / ".git" / "objects" / sha[:2]
    obj_dir.mkdir(parents=True, exist_ok=True)
    (obj_dir / sha[2:]).write_bytes(zlib.compress(payload))
    return sha


def _commit_tree(repo: Path, tree_sha: str) -> str:
    result = _run_git(repo, "commit-tree", tree_sha, "-m", "test: synthetic tree")
    assert result.returncode == 0, result.stderr
    commit_sha = result.stdout.decode().strip()
    _run_git(repo, "update-ref", "refs/heads/main", commit_sha)
    return commit_sha


def _run_check(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_SPEC_PATH), "--range", "HEAD"],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


class TestEndToEnd:
    """端到端：在临时仓库中真实写入 tree 对象后校验退出码。"""

    def test_non_canonical_tree_is_blocked(self, tmp_path):
        repo = tmp_path / "bad"
        repo.mkdir()
        _init_repo(repo)

        blob = _run_git(repo, "hash-object", "-w", "--stdin", input_bytes=b"content\n")
        blob_sha = blob.stdout.decode().strip()
        blob_bytes = bytes.fromhex(blob_sha)

        # 人为构造越序 tree：index.md 排在 README.md 之前
        content = (
            b"100644 index.md\x00" + blob_bytes
            + b"100644 README.md\x00" + blob_bytes
        )
        _commit_tree(repo, _write_tree_object(repo, content))

        result = _run_check(repo)
        assert result.returncode == 1
        assert "index.md" in result.stdout
        assert "越序" in result.stdout

    def test_canonical_tree_passes(self, tmp_path):
        repo = tmp_path / "good"
        repo.mkdir()
        _init_repo(repo)
        (repo / "README.md").write_text("readme\n", encoding="utf-8")
        _run_git(repo, "add", "README.md")
        _run_git(repo, "commit", "-q", "-m", "test: canonical tree")

        result = _run_check(repo)
        assert result.returncode == 0
        assert "通过" in result.stdout

    def test_empty_repo_does_not_block(self, tmp_path):
        repo = tmp_path / "empty"
        repo.mkdir()
        _init_repo(repo)

        result = _run_check(repo)
        assert result.returncode == 0

    def test_non_repo_does_not_block(self, tmp_path):
        plain = tmp_path / "plain"
        plain.mkdir()

        result = subprocess.run(
            [sys.executable, str(_SPEC_PATH)],
            cwd=str(plain),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0


@pytest.mark.parametrize(
    "left,right,expected",
    [
        (b"README.md", b"index.md", True),
        (b"index.md", b"README.md", False),
    ],
)
def test_byte_order_matches_git(left, right, expected):
    """交叉验证：与 git 自身的 tree 排序结果一致。"""
    assert (cto.sort_key(b"100644", left) < cto.sort_key(b"100644", right)) is expected