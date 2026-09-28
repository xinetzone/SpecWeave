"""TR-5.1 / TR-5.2：streak、周聚合、锚点、可勾选判定。"""

from datetime import date
from pathlib import Path

from zhihu_checkin_hub.domain.streak import (
    DEFAULT_WEEK_START,
    next_anchor,
    parse_anchor_date,
    section_progress,
    streak_summary,
    tracker_readiness,
    weekly_stats,
)
from zhihu_checkin_hub.storage.entries import (
    ContentKind,
    ContentRecord,
    DayEntry,
    Interaction,
)
from zhihu_checkin_hub.storage.tracker import parse_tracker

FIXTURE = Path(__file__).parent / "fixtures" / "tracker.md"


def q_entry(day: str, kind: str = ContentKind.ANSWER, chars: int = 200) -> DayEntry:
    return DayEntry(
        day=day,
        contents=[ContentRecord(kind=kind, char_count=chars)],
        interactions=[Interaction(kind="upvote"), Interaction(kind="comment"), Interaction(kind="follow")],
    )


def test_current_streak_today_grace_and_longest() -> None:
    entries = [q_entry(f"2026-09-{d:02d}") for d in (25, 26, 27)]
    s = streak_summary(entries, today=date(2026, 9, 28))
    assert s.current == 3  # 今天未打卡从昨天起算
    assert s.longest == 3
    assert s.gaps == ()

    entries.append(q_entry("2026-09-28"))
    s2 = streak_summary(entries, today=date(2026, 9, 28))
    assert s2.current == 4


def test_single_day_gap_no_review() -> None:
    entries = [q_entry("2026-09-25"), q_entry("2026-09-26"), q_entry("2026-09-28")]
    s = streak_summary(entries, today=date(2026, 9, 28))
    assert s.current == 1
    assert s.longest == 2
    assert len(s.gaps) == 1
    assert s.gaps[0].length == 1
    assert s.review_required is False


def test_three_day_gap_triggers_review() -> None:
    entries = [q_entry("2026-09-25"), q_entry("2026-09-26"), q_entry("2026-09-27")]
    s = streak_summary(entries, today=date(2026, 10, 1))
    assert s.current == 0
    assert any(g.length >= 3 for g in s.gaps)
    assert s.review_required is True
    assert "复核锚点" in s.review_message


def test_weekly_aggregation_goals() -> None:
    entries = [
        DayEntry(
            day="2026-09-26",
            contents=[
                ContentRecord(kind=ContentKind.ANSWER, char_count=200),
                ContentRecord(kind=ContentKind.ANSWER, char_count=200),
                ContentRecord(kind=ContentKind.PIN, char_count=30),
            ],
            interactions=[Interaction(kind="upvote")] * 3,
        ),
        DayEntry(
            day="2026-09-27",
            contents=[
                ContentRecord(kind=ContentKind.ANSWER, char_count=200),
                ContentRecord(kind=ContentKind.PIN, char_count=30),
            ],
            interactions=[Interaction(kind="upvote")] * 3,
        ),
    ]
    stats = weekly_stats(entries, today=date(2026, 9, 28))
    assert len(stats) == 1
    w1 = stats[0]
    assert (w1.start, w1.end) == (date(2026, 9, 25), date(2026, 10, 1))
    assert w1.answers == 3 and w1.pins == 2
    assert w1.meets_all is True
    assert w1.qualified_days == 2

    stats2 = weekly_stats(entries, today=date(2026, 10, 2))
    assert [w.index for w in stats2] == [1, 2]
    assert stats2[1].meets_all is False


def test_next_anchor_fixed_clock() -> None:
    doc = parse_tracker(FIXTURE)
    nxt = next_anchor(doc, today=date(2026, 9, 28))
    assert nxt is not None
    assert nxt.on == date(2026, 9, 29)
    assert nxt.days_ahead == 1
    assert "Go/No-Go" in nxt.anchor.event
    assert parse_anchor_date("10.01~10.08 长假", default_year=2026) == date(2026, 10, 1)


def test_section_progress() -> None:
    doc = parse_tracker(FIXTURE)
    progress = section_progress(doc)
    week1 = next(v for k, v in progress.items() if k.startswith("二、"))
    assert week1 == (0, 8)


def test_readiness_w12_and_w15() -> None:
    doc = parse_tracker(FIXTURE)
    # 只有 6 天合格，且无 ≥100 字创作（想法 25 字）
    weak = [
        DayEntry(
            day=f"2026-09-{25 + i:02d}",
            contents=[ContentRecord(kind=ContentKind.PIN, char_count=25)],
            interactions=[Interaction(kind="upvote")] * 3,
        )
        for i in range(6)
    ]
    r = {x.item_id: x for x in tracker_readiness(doc, weak, today=date(2026, 9, 30))}
    assert r["W1-2"].can_check is False
    assert r["W1-5"].can_check is False
    assert any("7 天" in g for g in r["W1-5"].gaps)

    strong = weak + [q_entry(f"2026-10-{d:02d}") for d in (1, 2)]
    # 6 天到 9/30，10/1、10/2 连续合格但与前段之间无断档 → 连续 8 天
    r2 = {x.item_id: x for x in tracker_readiness(doc, strong, today=date(2026, 10, 2))}
    assert r2["W1-2"].can_check is True
    assert r2["W1-5"].can_check is True
    # 展示标题不重复携带编号（编号在 UI 单独渲染）
    assert not r2["W1-2"].title.startswith("W1-2")
    assert r2["W1-2"].title == "首日打卡"
    assert r2["W1-5"].title == "连续 7 天打卡"
