"""链接基线（--baseline / --update-baseline）的回归与验收。

核心验收（test_baseline_reports_three_kinds_of_new_breakage）在一个临时 git
仓库里制造三种新增断链——新文件带断链、老文件新增断链、删除目标文件导致
别处断裂——断言三种都被报出，且基线内的存量断链不打印。
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
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

import pytest

from lib import link_baseline


def _import_check_links():
    spec = importlib.util.spec_from_file_location(
        "check_links_baseline", Path(__file__).parent.parent / "check-links.py"
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


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _init_repo(repo: Path) -> None:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "baseline-test@example.com")
    _git(repo, "config", "user.name", "baseline-test")
    _git(repo, "config", "core.autocrlf", "false")


def _commit_all(repo: Path) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "baseline fixture")


@pytest.fixture
def repo(tmp_path, monkeypatch):
    _init_repo(tmp_path)
    monkeypatch.setattr(cl, "resolve_project_root", lambda _file: tmp_path)
    return tmp_path


def _baseline_path(repo: Path) -> Path:
    return repo / ".agents" / "config" / "link-baseline.json"


def test_update_baseline_without_reason_is_refused(repo, capsys):
    _write(repo / "docs" / "a.md", "[断链](missing.md)\n")
    _commit_all(repo)

    rc = cl.main(["--update-baseline"])

    assert rc == 1
    assert "缺少 reason" in capsys.readouterr().err
    assert not _baseline_path(repo).exists(), "缺少 reason 时不得写入基线"


def test_invalid_reason_is_rejected(repo):
    with pytest.raises(SystemExit):
        cl.main(["--update-baseline", "--reason", "guess"])

    with pytest.raises(link_baseline.BaselineError):
        link_baseline.build_updated_entries(
            {("docs/a.md", "missing.md"): 1},
            {},
            reason="guess",
            reason_map=None,
            since="2026-11-09",
            review_by=None,
        )


def test_update_then_baseline_reports_zero_new(repo, capsys):
    _write(repo / "docs" / "a.md", "[断链](missing.md)\n")
    _commit_all(repo)

    assert cl.main(["--update-baseline", "--reason", "deleted"]) == 0
    capsys.readouterr()

    rc = cl.main(["--baseline"])
    out = capsys.readouterr().out

    assert rc == 0
    assert "新增 0 条" in out
    assert "missing.md" not in out.split("[基线]")[-1]


def test_baseline_reports_three_kinds_of_new_breakage(repo, capsys):
    docs = repo / "docs"
    _write(docs / "a.md", "# A\n\n[好链](target.md)\n")
    _write(docs / "target.md", "# Target\n")
    _write(docs / "old.md", "[老断链](missing-old.md)\n")
    _commit_all(repo)

    assert cl.main(["--update-baseline", "--reason", "deleted"]) == 0
    capsys.readouterr()

    # 三种新增：新文件带断链 / 老文件加断链 / 删目标导致别处断裂
    _write(docs / "new.md", "[新文件断链](missing-new.md)\n")
    _write(docs / "a.md", "# A\n\n[好链](target.md)\n\n[新增断链](missing-added.md)\n")
    (docs / "target.md").unlink()
    _git(repo, "add", "-A")

    rc = cl.main(["--baseline"])
    out = capsys.readouterr().out

    assert rc == 1
    assert "失败: 3 个断链" in out
    assert "missing-new.md" in out
    assert "missing-added.md" in out
    assert "target.md" in out
    assert "missing-old.md" not in out, "基线内存量不应打印"


def test_baseline_self_check_rejects_corrupt_entries(tmp_path):
    tracked = {"docs/a.md"}
    base = {
        "version": 1,
        "entries": [
            {
                "source": "docs/a.md",
                "target": "missing.md",
                "count": 1,
                "since": "2026-11-09",
                "reason": "deleted",
                "review_by": "2027-02-07",
            }
        ],
    }

    def load(entries):
        path = tmp_path / "baseline.json"
        path.write_text(json.dumps({"version": 1, "entries": entries}), encoding="utf-8")
        return link_baseline.load_baseline(path, tracked)

    assert ("docs/a.md", "missing.md") in load(base["entries"])

    for broken in (
        {**base["entries"][0], "source": "projects/x/a.md"},
        {**base["entries"][0], "target": "vendor/x.md"},
        {**base["entries"][0], "reason": "guess"},
        {**base["entries"][0], "source": "docs/untracked.md"},
    ):
        with pytest.raises(link_baseline.BaselineError):
            load([broken])
