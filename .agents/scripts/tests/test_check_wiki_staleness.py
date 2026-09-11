"""check-wiki-staleness.py 单元测试。

覆盖场景：
- parse_frontmatter: 正常字段/无 frontmatter/非法日期
- iter_markdown: 递归扫描与排除规则（生成目录/模板/入口页）
- check_wiki: fresh/stale/missing 三态与阈值边界
- mark_needs_update: 改写 status/新增 status/deprecated 跳过/无 FM 跳过/幂等
- apply_marks: --mark-stale 与 --mark-missing 的目标集合
- main: --knowledge 与 --path 端到端退出码
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
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "check_wiki_staleness", _SCRIPTS_DIR / "check-wiki-staleness.py"
)
cws = importlib.util.module_from_spec(_spec)
sys.modules["check_wiki_staleness"] = cws
_spec.loader.exec_module(cws)


# ---- 夹具 ----

def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _fm(title: str, *, status: str = "stable", last_verified: str | None = None) -> str:
    lines = ["---", f"title: {title}", f"status: {status}"]
    if last_verified is not None:
        lines.append(f"last_verified: {last_verified}")
    lines += ["---", "", f"# {title}", ""]
    return "\n".join(lines)


@pytest.fixture
def wiki_tree(tmp_path: Path) -> Path:
    """构造一棵含 fresh/stale/missing/递归子目录/排除项的知识树。"""
    today = date.today().isoformat()
    old = (date.today() - timedelta(days=100)).isoformat()
    boundary = (date.today() - timedelta(days=90)).isoformat()

    _write(tmp_path / "fresh.md", _fm("Fresh", last_verified=today))
    _write(tmp_path / "stale.md", _fm("Stale", last_verified=old))
    _write(tmp_path / "missing.md", _fm("Missing"))
    _write(tmp_path / "boundary.md", _fm("Boundary", last_verified=boundary))
    _write(tmp_path / "sub" / "deep" / "stale-deep.md",
           _fm("Deep", last_verified=old))
    # 排除项
    _write(tmp_path / "README.md", _fm("README", last_verified=old))
    _write(tmp_path / "template.md", _fm("Template", last_verified=old))
    _write(tmp_path / "scripts" / "generated.md", _fm("Gen", last_verified=old))
    _write(tmp_path / "categories" / "x.md", _fm("Cat", last_verified=old))
    return tmp_path


# ---- parse_frontmatter ----

def test_parse_frontmatter_fields(tmp_path: Path):
    today = date.today().isoformat()
    f = _write(tmp_path / "a.md", _fm("A", status="reviewed", last_verified=today))
    fields, body = cws.parse_frontmatter(f)
    assert fields["title"] == "A"
    assert fields["status"] == "reviewed"
    assert fields["last_verified"] == today
    assert "# A" in body


def test_parse_frontmatter_missing(tmp_path: Path):
    f = _write(tmp_path / "a.md", "# 无 frontmatter\n正文\n")
    fields, _ = cws.parse_frontmatter(f)
    assert fields == {}


def test_parse_frontmatter_invalid_date_counts_as_missing(tmp_path: Path):
    content = "---\ntitle: X\nlast_verified: 2026/01/01\n---\n\n# X\n"
    f = _write(tmp_path / "a.md", content)
    results = cws.check_wiki(tmp_path, 90)
    assert results[0].status == "missing"


# ---- iter_markdown ----

def test_iter_markdown_recursion_and_excludes(wiki_tree: Path):
    files = list(cws.iter_markdown(
        wiki_tree, recursive=True,
        exclude_dirs=cws.KNOWLEDGE_EXCLUDE_DIRS,
        exclude_files=cws.KNOWLEDGE_EXCLUDE_FILES,
    ))
    names = sorted(f.name for f in files)
    assert names == ["boundary.md", "fresh.md", "missing.md", "stale-deep.md", "stale.md"]


def test_iter_markdown_flat_mode(wiki_tree: Path):
    files = list(cws.iter_markdown(wiki_tree, recursive=False))
    names = sorted(f.name for f in files)
    # 非递归：仅顶层，且无排除
    assert "stale-deep.md" not in names
    assert "README.md" in names
    assert "scripts" not in names


# ---- check_wiki ----

def test_check_wiki_states_and_boundary(wiki_tree: Path):
    results = cws.check_wiki(
        wiki_tree, 90,
        exclude_dirs=cws.KNOWLEDGE_EXCLUDE_DIRS,
        exclude_files=cws.KNOWLEDGE_EXCLUDE_FILES,
    )
    by_name = {r.path.name: r for r in results}
    assert by_name["fresh.md"].status == "fresh"
    assert by_name["stale.md"].status == "stale"
    assert by_name["stale.md"].days_since == 100
    assert by_name["missing.md"].status == "missing"
    # 阈值边界：恰好 90 天不算过期（> threshold 才 stale）
    assert by_name["boundary.md"].status == "fresh"
    # 子目录递归命中
    assert by_name["stale-deep.md"].status == "stale"


def test_check_wiki_custom_threshold(wiki_tree: Path):
    results = cws.check_wiki(
        wiki_tree, 200,
        exclude_dirs=cws.KNOWLEDGE_EXCLUDE_DIRS,
        exclude_files=cws.KNOWLEDGE_EXCLUDE_FILES,
    )
    assert all(r.status != "stale" for r in results)


def test_check_wiki_nonexistent_dir(tmp_path: Path):
    with pytest.raises(SystemExit) as exc:
        cws.check_wiki(tmp_path / "nope", 90)
    assert exc.value.code == 2


# ---- mark_needs_update ----

def test_mark_updates_existing_status(tmp_path: Path):
    old = (date.today() - timedelta(days=100)).isoformat()
    f = _write(tmp_path / "a.md", _fm("A", status="stable", last_verified=old))
    assert cws.mark_needs_update(f) == "updated"
    text = f.read_text(encoding="utf-8")
    assert "status: needs-update" in text
    assert "last_verified:" in text  # 其他字段保留
    assert "# A" in text
    # 幂等
    assert cws.mark_needs_update(f) == "already"


def test_mark_inserts_status_when_absent(tmp_path: Path):
    f = _write(tmp_path / "a.md",
               "---\ntitle: X\nlast_verified: 2020-01-01\n---\n\n# X\n")
    assert cws.mark_needs_update(f) == "updated"
    text = f.read_text(encoding="utf-8")
    assert "status: needs-update" in text
    assert "title: X" in text


def test_mark_skips_deprecated(tmp_path: Path):
    f = _write(tmp_path / "a.md",
               _fm("A", status="deprecated",
                   last_verified=(date.today() - timedelta(days=300)).isoformat()))
    assert cws.mark_needs_update(f) == "skipped-deprecated"
    assert "status: deprecated" in f.read_text(encoding="utf-8")


def test_mark_skips_without_frontmatter(tmp_path: Path):
    f = _write(tmp_path / "a.md", "# 无 FM\n")
    assert cws.mark_needs_update(f) == "no-frontmatter"
    assert f.read_text(encoding="utf-8") == "# 无 FM\n"


# ---- apply_marks ----

def test_apply_marks_stale_only(wiki_tree: Path):
    results = cws.check_wiki(
        wiki_tree, 90,
        exclude_dirs=cws.KNOWLEDGE_EXCLUDE_DIRS,
        exclude_files=cws.KNOWLEDGE_EXCLUDE_FILES,
    )
    changed = cws.apply_marks(results, mark_stale=True, mark_missing=False)
    assert changed == 2  # stale + stale-deep
    by_name = {r.path.name: r for r in results}
    assert by_name["stale.md"].mark_note == "updated"
    assert by_name["missing.md"].mark_note == ""
    assert "status: needs-update" in (wiki_tree / "stale.md").read_text(encoding="utf-8")


def test_apply_marks_missing_only(wiki_tree: Path):
    results = cws.check_wiki(
        wiki_tree, 90,
        exclude_dirs=cws.KNOWLEDGE_EXCLUDE_DIRS,
        exclude_files=cws.KNOWLEDGE_EXCLUDE_FILES,
    )
    changed = cws.apply_marks(results, mark_stale=False, mark_missing=True)
    assert changed == 1  # 仅 missing（有 frontmatter）
    by_name = {r.path.name: r for r in results}
    assert by_name["missing.md"].mark_note == "updated"
    assert by_name["stale.md"].mark_note == ""


# ---- main 端到端 ----

def test_main_path_exit_codes(wiki_tree: Path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", [
        "check-wiki-staleness.py", "--path", str(wiki_tree),
        "--threshold", "90",
    ])
    assert cws.main() == 1  # 存在 stale + missing
    out = capsys.readouterr().out
    assert "Wiki Freshness Report" in out

    # 全部新鲜的小树 -> exit 0
    fresh_root = wiki_tree / "fresh-only"
    fresh_root.mkdir()
    _write(fresh_root / "ok.md",
           _fm("OK", last_verified=date.today().isoformat()))
    monkeypatch.setattr(sys, "argv", [
        "check-wiki-staleness.py", "--path", str(fresh_root),
    ])
    assert cws.main() == 0


def test_main_knowledge_preset_runs(monkeypatch, capsys):
    # 真实仓库当前 249 条存量均无 last_verified，预期 exit 1 且能跑通
    monkeypatch.setattr(sys, "argv", ["check-wiki-staleness.py", "--knowledge"])
    rc = cws.main()
    assert rc == 1
    out = capsys.readouterr().out
    assert "docs/knowledge" in out
    assert "total files" in out


def test_main_mark_batch_guard(tmp_path: Path, monkeypatch):
    # 21 个无基线文件超过护栏上限：不带 --force 拒绝执行且不写文件
    for i in range(21):
        _write(tmp_path / f"m{i:02d}.md", _fm(f"M{i}"))
    target = tmp_path / "m00.md"
    original = target.read_text(encoding="utf-8")

    monkeypatch.setattr(sys, "argv", [
        "check-wiki-staleness.py", "--path", str(tmp_path), "--mark-missing",
    ])
    with pytest.raises(SystemExit) as exc:
        cws.main()
    assert exc.value.code == 2
    assert target.read_text(encoding="utf-8") == original  # 护栏拦截，零写入

    # --force 放行
    monkeypatch.setattr(sys, "argv", [
        "check-wiki-staleness.py", "--path", str(tmp_path),
        "--mark-missing", "--force",
    ])
    assert cws.main() == 1
    assert "status: needs-update" in target.read_text(encoding="utf-8")


def test_main_mark_within_batch_limit_runs(tmp_path: Path, monkeypatch):
    for i in range(3):
        _write(tmp_path / f"s{i}.md",
               _fm(f"S{i}", last_verified=(date.today() - timedelta(days=120)).isoformat()))
    monkeypatch.setattr(sys, "argv", [
        "check-wiki-staleness.py", "--path", str(tmp_path), "--mark-stale",
    ])
    assert cws.main() == 1
    assert "status: needs-update" in (tmp_path / "s0.md").read_text(encoding="utf-8")
