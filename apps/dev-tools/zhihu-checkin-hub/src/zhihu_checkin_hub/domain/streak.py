"""streak / 执行周 / 锚点 / 可勾选判定 —— 全部纯函数。

时钟一律由调用方注入 ``today``，保证测试与审计可复现。
"""

import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable

from ..models import Anchor, TrackerDoc
from ..storage.entries import ContentKind, DayEntry, is_qualified_day

DEFAULT_WEEK_START = date(2026, 9, 25)
WEEKLY_ANSWER_GOAL = 3
WEEKLY_PIN_GOAL = 2
LONG_GAP_DAYS = 3

_LABEL_ID_PREFIX = re.compile(r"^(?:W\d+-\d+|M\d+-\d+|O-\d+)\s+")


def _short_title(label: str) -> str:
    """展示用标题：去掉 label 开头的行动项编号（编号已在 UI 单独展示）。"""
    return _LABEL_ID_PREFIX.sub("", label, count=1)


@dataclass(frozen=True)
class Gap:
    start: date
    length: int

    @property
    def end(self) -> date:
        return self.start + timedelta(days=self.length - 1)


@dataclass(frozen=True)
class StreakSummary:
    current: int
    longest: int
    qualified: tuple[date, ...]
    gaps: tuple[Gap, ...]
    review_required: bool
    review_message: str


@dataclass(frozen=True)
class WeekStat:
    index: int
    start: date
    end: date
    answers: int
    pins: int
    qualified_days: int

    @property
    def meets_answer_goal(self) -> bool:
        return self.answers >= WEEKLY_ANSWER_GOAL

    @property
    def meets_pin_goal(self) -> bool:
        return self.pins >= WEEKLY_PIN_GOAL

    @property
    def meets_all(self) -> bool:
        return self.meets_answer_goal and self.meets_pin_goal


@dataclass(frozen=True)
class NextAnchor:
    anchor: Anchor
    on: date
    days_ahead: int


@dataclass(frozen=True)
class Readiness:
    item_id: str
    title: str
    can_check: bool
    gaps: tuple[str, ...]


def _qualified_set(entries: Iterable[DayEntry]) -> set[date]:
    return {e.as_date for e in entries if is_qualified_day(e)}


def _runs(days: set[date]) -> list[tuple[date, int]]:
    """把日期集合压缩为连续段 [(起点, 长度)]。"""
    if not days:
        return []
    ordered = sorted(days)
    runs: list[tuple[date, int]] = []
    start = prev = ordered[0]
    length = 1
    for d in ordered[1:]:
        if (d - prev).days == 1:
            length += 1
        else:
            runs.append((start, length))
            start = d
            length = 1
        prev = d
    runs.append((start, length))
    return runs


def streak_summary(
    entries: Iterable[DayEntry],
    *,
    today: date,
    week_start: date = DEFAULT_WEEK_START,
) -> StreakSummary:
    qualified = _qualified_set(entries)

    # 当前连续：今天未打卡时允许从昨天起算（当天尚未结束，不计断档）
    cursor = today if today in qualified else today - timedelta(days=1)
    current = 0
    while cursor in qualified:
        current += 1
        cursor -= timedelta(days=1)

    longest = max((length for _, length in _runs(qualified)), default=0)

    # 断档：起跑日（含）到今天（不含今天宽限）之间的缺卡日，聚合成段
    gap_days = [
        week_start + timedelta(days=i)
        for i in range((today - week_start).days + 1)
        if (week_start + timedelta(days=i)) not in qualified
        and week_start + timedelta(days=i) != today
    ]
    gaps = tuple(Gap(start=s, length=n) for s, n in _runs(set(gap_days)))
    long_gaps = tuple(g for g in gaps if g.length >= LONG_GAP_DAYS)
    review_required = bool(long_gaps)
    review_message = (
        "存在 ≥3 天的中断（{}）。按纪律请先回到 tracker.md §七 复核锚点核对规则与目标，再决定恢复节奏。".format(
            "、".join(f"{g.start.isoformat()} 起 {g.length} 天" for g in long_gaps)
        )
        if review_required
        else ""
    )
    return StreakSummary(
        current=current,
        longest=longest,
        qualified=tuple(sorted(qualified)),
        gaps=gaps,
        review_required=review_required,
        review_message=review_message,
    )


def weekly_stats(
    entries: Iterable[DayEntry],
    *,
    today: date,
    week_start: date = DEFAULT_WEEK_START,
) -> list[WeekStat]:
    """执行周（周五—周四）聚合，只返回到今天为止已经开始的周。"""
    entries = list(entries)
    stats: list[WeekStat] = []
    index = 1
    start = week_start
    while start <= today:
        end = start + timedelta(days=6)
        answers = pins = qualified_days = 0
        for e in entries:
            d = e.as_date
            if start <= d <= end:
                if is_qualified_day(e):
                    qualified_days += 1
                for c in e.contents:
                    if c.kind == ContentKind.ANSWER:
                        answers += 1
                    elif c.kind == ContentKind.PIN:
                        pins += 1
        stats.append(WeekStat(index, start, end, answers, pins, qualified_days))
        index += 1
        start = end + timedelta(days=1)
    return stats


def parse_anchor_date(text: str, *, default_year: int) -> date | None:
    """从锚点文本提取首个日期；支持 YYYY-MM-DD 与 M.D（取区间起点）。"""
    iso = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if iso:
        return date(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))
    md = re.search(r"(?<!\d)(\d{1,2})\.(\d{1,2})", text)
    if md:
        return date(default_year, int(md.group(1)), int(md.group(2)))
    return None


def next_anchor(
    doc: TrackerDoc, *, today: date, default_year: int = DEFAULT_WEEK_START.year
) -> NextAnchor | None:
    candidates: list[NextAnchor] = []
    for anchor in doc.anchors:
        on = parse_anchor_date(anchor.date_text, default_year=default_year)
        if on is not None and on >= today:
            candidates.append(NextAnchor(anchor, on, (on - today).days))
    return min(candidates, key=lambda c: c.days_ahead) if candidates else None


def section_progress(doc: TrackerDoc) -> dict[str, tuple[int, int]]:
    """章节 → (已勾选, 总数)。"""
    progress: dict[str, list[int]] = {}
    for item in doc.items:
        slot = progress.setdefault(item.section, [0, 0])
        slot[1] += 1
        if item.checked:
            slot[0] += 1
    return {section: (v[0], v[1]) for section, v in progress.items()}


def tracker_readiness(
    doc: TrackerDoc, entries: Iterable[DayEntry], *, today: date
) -> tuple[Readiness, ...]:
    """纯函数门槛判定：只提示「可勾选/缺口」，绝不自动勾选。"""
    entries = list(entries)
    summary = streak_summary(entries, today=today)
    out: list[Readiness] = []

    w12 = doc.get("W1-2")
    if w12 is not None:
        gaps: list[str] = []
        strong_entry = next(
            (
                e
                for e in entries
                if any(c.char_count >= 100 for c in e.contents)
                and len(e.interactions) >= 3
            ),
            None,
        )
        if strong_entry is None:
            gaps.append("尚无「≥100 字创作 + 3 个互动」同时达标的当日 entry")
        out.append(
            Readiness(
                item_id="W1-2",
                title=_short_title(w12.label),
                can_check=not gaps and not w12.checked,
                gaps=tuple(gaps),
            )
        )

    w15 = doc.get("W1-5")
    if w15 is not None:
        gaps5: list[str] = []
        has_seven_run = any(length >= 7 for _, length in _runs(set(summary.qualified)))
        if not has_seven_run:
            gaps5.append(f"最长连续合格打卡为 {summary.longest} 天，需要连续 7 天")
        out.append(
            Readiness(
                item_id="W1-5",
                title=_short_title(w15.label),
                can_check=not gaps5 and not w15.checked,
                gaps=tuple(gaps5),
            )
        )

    return tuple(out)
