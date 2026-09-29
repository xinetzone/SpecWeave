"""TR-4：entries / drafts / records 文件存储层。"""

import shutil
from datetime import date
from pathlib import Path

import pytest
import yaml

from zhihu_checkin_hub.errors import StorageError
from zhihu_checkin_hub.storage.drafts import (
    Draft,
    list_drafts,
    load_draft,
    save_draft,
    slugify,
    transition_status,
)
from zhihu_checkin_hub.storage.entries import (
    ContentKind,
    ContentRecord,
    DayEntry,
    Interaction,
    InteractionKind,
    is_qualified_day,
    load_all_entries,
    load_entry,
    save_entry,
)
from zhihu_checkin_hub.storage.records import (
    add_earning,
    add_interruption,
    add_review,
    correct_earning,
    load_table,
    upsert_weekly,
)
from zhihu_checkin_hub.storage.workspace import open_workspace

FIXTURE = Path(__file__).parent / "fixtures" / "tracker.md"


@pytest.fixture()
def workspace(tmp_path: Path):
    ws_dir = tmp_path / "zhihu-monetization"
    ws_dir.mkdir()
    shutil.copy(FIXTURE, ws_dir / "tracker.md")
    return open_workspace(ws_dir)


# ---------------- entries ----------------


def test_entry_roundtrip_and_qualification(workspace) -> None:
    assert load_entry(workspace, date(2026, 9, 28)).contents == []

    entry = DayEntry(
        day="2026-09-28",
        contents=[ContentRecord(kind=ContentKind.ANSWER, char_count=320)],
        interactions=[
            Interaction(kind=InteractionKind.UPVOTE, target="q1"),
            Interaction(kind=InteractionKind.COMMENT, target="q2"),
            Interaction(kind=InteractionKind.FOLLOW, target="u1"),
        ],
        note="底盘完成",
    )
    save_entry(workspace, entry)
    again = load_entry(workspace, date(2026, 9, 28))
    assert again.contents[0].char_count == 320
    assert len(again.interactions) == 3
    assert is_qualified_day(again) is True


def test_entry_unqualified_thresholds(workspace) -> None:
    short_pin = DayEntry(
        day="2026-09-29",
        contents=[ContentRecord(kind=ContentKind.PIN, char_count=10)],
        interactions=[
            Interaction(kind=InteractionKind.UPVOTE),
            Interaction(kind=InteractionKind.UPVOTE),
            Interaction(kind=InteractionKind.UPVOTE),
        ],
    )
    assert is_qualified_day(short_pin) is False  # 想法不足 20 字
    short_pin.contents[0].char_count = 25
    assert is_qualified_day(short_pin) is True

    no_inter = DayEntry(day="2026-09-30", contents=[ContentRecord(kind="answer", char_count=500)])
    assert is_qualified_day(no_inter) is False


def test_gate_blob_persisted_in_entry(workspace) -> None:
    entry = DayEntry(day="2026-10-01", gates=[{"passed": True, "at": "2026-10-01T20:00"}])
    save_entry(workspace, entry)
    loaded = load_entry(workspace, date(2026, 10, 1))
    assert loaded.gates[0]["passed"] is True


def test_load_all_entries_sorted(workspace) -> None:
    for d in ("2026-10-02", "2026-09-30", "2026-10-01"):
        save_entry(workspace, DayEntry(day=d))
    assert [e.day for e in load_all_entries(workspace)] == [
        "2026-09-30",
        "2026-10-01",
        "2026-10-02",
    ]


# ---------------- drafts ----------------


def test_slugify_rejects_traversal() -> None:
    assert slugify("回答示例 标题！") == "回答示例-标题"
    assert slugify("a/b\\c") == "a-b-c"


def test_draft_frontmatter_roundtrip_and_status(workspace) -> None:
    draft = Draft(
        slug="first-answer",
        title="第一回答",
        kind=ContentKind.ANSWER,
        body="正文含特殊字符：--- 与中文。\n",
        question_url="https://www.zhihu.com/question/1/answer/2",
    )
    path = save_draft(workspace, draft)
    raw = path.read_text(encoding="utf-8")
    assert raw.startswith("---\n")
    loaded = load_draft(workspace, "first-answer")
    assert loaded.body.startswith("正文含特殊字符")
    assert loaded.kind == "answer"
    assert loaded.status == "draft"

    transition_status(loaded.status, "ready")
    loaded.status = "ready"
    save_draft(workspace, loaded)
    assert list_drafts(workspace)[0].status == "ready"


def test_draft_illegal_status_and_slug(workspace) -> None:
    with pytest.raises(StorageError):
        transition_status("published", "ready")
    with pytest.raises(StorageError):
        save_draft(workspace, Draft(slug="../escape", title="x", kind="answer"))


# ---------------- records ----------------


def test_earnings_append_and_correction(workspace) -> None:
    r1 = add_earning(workspace, day="2026-09-30", action="answer", salt_raw="120")
    assert r1["salt_raw"] == 120
    with pytest.raises(StorageError):
        add_earning(workspace, day="2026-09-30", action="answer", salt_raw="abc")
    corrected = correct_earning(workspace, row_id=r1["id"], new_salt=100, note="官方修正")
    assert corrected["salt_raw"] == 100
    assert corrected["corrections"][0]["from"] == 120
    # 原表只追加/就地修正单行，不新增
    assert len(load_table(workspace, "earnings")) == 1


def test_weekly_upsert(workspace) -> None:
    kw = dict(week_id="W1", start="2026-09-25", end="2026-10-01")
    upsert_weekly(workspace, **kw, answers=3, pins=2, confirmed=0)
    upsert_weekly(workspace, **kw, answers=4, pins=2, confirmed=1, note="全勤")
    rows = load_table(workspace, "weekly")
    assert len(rows) == 1
    assert rows[0]["answers"] == 4
    with pytest.raises(StorageError):
        upsert_weekly(workspace, **kw, answers=-1, pins=0, confirmed=0)


def test_interruptions_and_reviews(workspace) -> None:
    add_interruption(workspace, start_day="2026-10-05", days=4, reason="出差")
    assert load_table(workspace, "interruptions")[0]["days"] == 4

    review = add_review(
        workspace, day="2026-10-30", salt_total=250, decision="continue", reason="达标"
    )
    assert review["yuan_estimate"] == 2
    assert "F-059" in review["conversion_basis"]
    with pytest.raises(StorageError):
        add_review(workspace, day="2026-10-30", salt_total=1, decision="maybe", reason="")


def test_all_writes_inside_local(workspace, tmp_path: Path) -> None:
    save_entry(
        workspace,
        DayEntry(day="2026-10-03", contents=[ContentRecord(kind="pin", char_count=30)]),
    )
    save_draft(workspace, Draft(slug="p1", title="想法", kind="pin", body="x"))
    add_earning(workspace, day="2026-10-03", action="pin", salt_raw=10)
    add_review(workspace, day="2026-10-03", salt_total=100, decision="continue", reason="r")
    for path in workspace.local.rglob("*"):
        if path.is_file():
            assert workspace.local.resolve() in path.resolve().parents
