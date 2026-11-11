"""repo-brief.py 的单元测试。

全部在临时仓库夹具上执行，不读取本仓实时状态——本仓的分支、提交数、
工作树每天都在变，断言它等于钉死错误的东西。
"""

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "repo-brief.py"

_spec = importlib.util.spec_from_file_location("repo_brief", SCRIPT_PATH)
repo_brief = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(repo_brief)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def _init_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-q")
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test")
    _git(path, "config", "commit.gpgsign", "false")
    (path / "a.txt").write_text("a", encoding="utf-8")
    _git(path, "add", "a.txt")
    _git(path, "commit", "-q", "-m", "init")
    return path


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return _init_repo(tmp_path / "repo")


def test_worktree_clean_then_dirty(repo: Path):
    clean = repo_brief.collect(repo)
    assert clean["worktree"]["clean"] is True
    assert clean["worktree"]["untracked"] == 0
    assert clean["worktree"]["modified"] == 0
    assert clean["worktree"]["staged"] == 0

    (repo / "untracked.txt").write_text("u", encoding="utf-8")
    (repo / "a.txt").write_text("changed", encoding="utf-8")
    (repo / "staged.txt").write_text("s", encoding="utf-8")
    _git(repo, "add", "staged.txt")

    dirty = repo_brief.collect(repo)
    assert dirty["worktree"]["clean"] is False
    assert dirty["worktree"]["untracked"] == 1
    assert dirty["worktree"]["modified"] == 1
    assert dirty["worktree"]["staged"] == 1


def test_collect_is_read_only(repo: Path):
    def snapshot() -> set:
        return {
            str(path.relative_to(repo))
            for path in repo.rglob("*")
            if ".git" not in path.relative_to(repo).parts
        }

    before = snapshot()
    repo_brief.collect(repo)
    assert snapshot() == before


def test_unpushed_commit_count(tmp_path: Path):
    origin = tmp_path / "origin.git"
    origin.mkdir()
    _git(origin, "init", "--bare", "-q")

    repo = _init_repo(tmp_path / "repo")
    _git(repo, "remote", "add", "origin", str(origin))
    _git(repo, "push", "-q", "-u", "origin", "HEAD")

    (repo / "b.txt").write_text("b", encoding="utf-8")
    _git(repo, "add", "b.txt")
    _git(repo, "commit", "-q", "-m", "second")
    (repo / "c.txt").write_text("c", encoding="utf-8")
    _git(repo, "add", "c.txt")
    _git(repo, "commit", "-q", "-m", "third")

    data = repo_brief.collect(repo)
    assert data["branch"]["upstream"] == "origin/" + data["branch"]["name"]
    assert data["branch"]["ahead"] == 2
    assert data["commits"]["unpushed"]["count"] == 2
    assert data["commits"]["unpushed"]["by_area"], "未推送提交应按目录聚合"

    recent = data["commits"]["recent"]
    assert [item["pushed"] for item in recent] == [False, False, True]


def test_unknown_when_no_remote_cache(repo: Path):
    data = repo_brief.collect(repo)

    assert data["branch"]["upstream"] is None
    assert data["commits"]["unpushed"]["value"] == "unknown"
    assert data["commits"]["unpushed"]["reason"]
    assert all(item["pushed"] == "unknown" for item in data["commits"]["recent"])

    freshness = data["commits"]["remote_freshness"]
    assert freshness["value"] == "unknown"
    assert "FETCH_HEAD" in freshness["reason"]
    assert freshness["last_fetch_at"] is None

    fields = {item["field"] for item in data["unknowns"]}
    assert "commits.remote_freshness" in fields
    assert "unpushed" in fields


def test_remote_configured_but_never_fetched(tmp_path: Path):
    origin = tmp_path / "origin.git"
    origin.mkdir()
    _git(origin, "init", "--bare", "-q")

    repo = _init_repo(tmp_path / "repo")
    _git(repo, "remote", "add", "origin", str(origin))

    freshness = repo_brief.collect(repo)["commits"]["remote_freshness"]
    assert freshness["value"] == "unknown"
    assert freshness["last_fetch_at"] is None


def test_json_structure_completeness(repo: Path):
    data = repo_brief.collect(repo)

    for key in ("schema_version", "generated_at", "repo", "branch", "worktree",
                "commits", "specs", "artifacts_7d", "known_exceptions",
                "known_debt", "unknowns", "timings_ms"):
        assert key in data, f"缺少顶层字段: {key}"
    assert data["schema_version"] == 1
    assert data["timings_ms"]["total"] > 0

    # 五个强制未知面必须显式出现，且每条都带原因
    fields = {item["field"] for item in data["unknowns"]}
    expected = {
        "worktree.submodules",
        "commits.remote_freshness",
        "worktree.other_sessions",
        "artifacts.sensitivity",
        "worktree.ignored_dirs",
    }
    assert expected <= fields
    for item in data["unknowns"]:
        assert item["reason"].strip(), f"{item['field']} 的 unknown 缺少原因"
    assert data["worktree"]["submodules"]["value"] == "unknown"

    # 序列化必须无损
    assert json.loads(json.dumps(data, ensure_ascii=False))["schema_version"] == 1


def test_with_links_disabled_by_default(repo: Path):
    assert repo_brief.build_parser().parse_args([]).with_links is False

    data = repo_brief.collect(repo)
    assert data["known_debt"]["status"] == "unknown"
    assert "--with-links" in data["known_debt"]["value"]["reason"]
    assert "check_links" not in data["timings_ms"], "默认不应执行链接检查"


def test_with_links_missing_script_is_unknown(repo: Path):
    data = repo_brief.collect(repo, with_links=True)
    assert data["known_debt"]["status"] == "unknown"
    assert "检查脚本不存在" in data["known_debt"]["value"]["reason"]


def test_known_exceptions_missing_source_is_unknown(repo: Path):
    exceptions = repo_brief.collect(repo)["known_exceptions"]
    assert exceptions["status"] == "unknown"
    assert "来源文件不存在" in exceptions["value"]["reason"]


def test_known_exceptions_reads_section(repo: Path):
    source = repo / repo_brief.EXCEPTIONS_SOURCE
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(
        "# 报告\n\n## 已知例外（示例）\n\n第一行事实\n第二行事实\n\n## 附录\n\n不相关\n",
        encoding="utf-8",
    )

    exceptions = repo_brief.collect(repo)["known_exceptions"]
    assert exceptions["status"] == "ok"
    assert exceptions["value"]["line"] == 3
    assert "第一行事实" in exceptions["value"]["lines"]
    assert "不相关" not in exceptions["value"]["lines"]


def test_cli_json_output(repo: Path, capsys):
    assert repo_brief.main(["--repo", str(repo), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["repo"]["path"] == str(repo.resolve())


def test_cli_rejects_non_repo(tmp_path: Path, capsys):
    plain = tmp_path / "plain"
    plain.mkdir()
    assert repo_brief.main(["--repo", str(plain)]) == 2
    assert "不是 git 仓库" in capsys.readouterr().err
