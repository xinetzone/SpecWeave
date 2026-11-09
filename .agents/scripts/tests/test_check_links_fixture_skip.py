"""测试夹具数据跳过的红绿回归。

背景：`apps/dev-tools/zhihu-checkin-hub/tests/fixtures/tracker.md` 里 54 条链接
是喂给解析器的假路径，按实际位置解析必然断链。修复前它们进入全量扫描，
把真实断链数字淹没。本组用例锁定三条边界：

1. 被测试引用的 tests/**/fixtures/*.md 在目录扫描时跳过（修复前返回 1）；
2. 夹具目录里的 README.md / index.md 仍按真实文档检查；
3. 未被测试引用、以及 --path 显式点名的文件，一律继续检查。

修复前的行为是「全部照查」，因此第 1 条在旧代码上为红（rc=1），修复后为绿。
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

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import importlib.util

import pytest


def _import_check_links():
    spec = importlib.util.spec_from_file_location(
        "check_links_fixture", Path(__file__).parent.parent / "check-links.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cl = _import_check_links()


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def _init_repo(repo: Path) -> None:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "fixture-test@example.com")
    _git(repo, "config", "user.name", "fixture-test")
    _git(repo, "config", "core.autocrlf", "false")


def _commit_all(repo: Path) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "fixture")


@pytest.fixture
def fixture_repo(tmp_path, monkeypatch):
    """构造 tests/fixtures 结构，并把 check-links 的工程根指向临时仓库。"""
    _init_repo(tmp_path)
    monkeypatch.setattr(cl, "resolve_project_root", lambda _file: tmp_path)
    return tmp_path


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_referenced_fixture_is_skipped_in_directory_scan(fixture_repo, capsys):
    tests_dir = fixture_repo / "apps" / "demo" / "tests"
    _write(
        tests_dir / "fixtures" / "tracker.md",
        "# 夹具\n\n[假路径](../../../../docs/not-there.md)\n",
    )
    _write(tests_dir / "test_demo.py", 'FIXTURE = "tracker.md"\n')
    _commit_all(fixture_repo)

    rc = cl.main(["--path", str(tests_dir)])
    out = capsys.readouterr().out

    assert rc == 0, "被测试引用的夹具数据应在目录扫描中跳过（修复前会报断链返回 1）"
    assert "跳过测试夹具数据: 1 个 Markdown 文件" in out
    assert "tests/fixtures/tracker.md" in out


def test_fixture_readme_is_still_checked(fixture_repo):
    tests_dir = fixture_repo / "apps" / "demo" / "tests"
    _write(
        tests_dir / "fixtures" / "README.md",
        "# 夹具说明\n\n[真断链](../../../../docs/not-there.md)\n",
    )
    _write(tests_dir / "test_demo.py", 'FIXTURE = "tracker.md"\n')
    _commit_all(fixture_repo)

    rc = cl.main(["--path", str(tests_dir)])

    assert rc == 1, "夹具目录里的 README.md 是文档，不应被夹具规则豁免"


def test_unreferenced_fixture_is_still_checked(fixture_repo):
    tests_dir = fixture_repo / "apps" / "demo" / "tests"
    _write(
        tests_dir / "fixtures" / "orphan.md",
        "# 未被引用的夹具\n\n[断链](../../../../docs/not-there.md)\n",
    )
    _write(tests_dir / "test_demo.py", 'FIXTURE = "tracker.md"\n')
    _commit_all(fixture_repo)

    rc = cl.main(["--path", str(tests_dir)])

    assert rc == 1, "未被测试引用的 Markdown 不能按夹具豁免（宁可多查）"


def test_explicit_fixture_file_is_still_checked(fixture_repo):
    tests_dir = fixture_repo / "apps" / "demo" / "tests"
    fixture = tests_dir / "fixtures" / "tracker.md"
    _write(fixture, "# 夹具\n\n[假路径](../../../../docs/not-there.md)\n")
    _write(tests_dir / "test_demo.py", 'FIXTURE = "tracker.md"\n')
    _commit_all(fixture_repo)

    rc = cl.main(["--path", str(fixture)])

    assert rc == 1, "--path 点名的单个文件必须照常检查，避免零工作量假通过"
