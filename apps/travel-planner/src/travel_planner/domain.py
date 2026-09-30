"""领域聚合：预算汇总、天数视图、行中状态。纯函数、零 IO。"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta

from .models import ITEM_TYPES, Item, Trip

WEEKDAYS = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")


def day_count(trip: Trip) -> int:
    """行程天数（日期不全时为 0）。"""
    if not trip.start_date or not trip.end_date:
        return 0
    return (date.fromisoformat(trip.end_date) - date.fromisoformat(trip.start_date)).days + 1


def day_date(trip: Trip, day_index: int) -> date | None:
    if not trip.start_date:
        return None
    return date.fromisoformat(trip.start_date) + timedelta(days=day_index - 1)


@dataclass(frozen=True)
class DayView:
    """一天的渲染视图。"""

    day_index: int
    date_iso: str
    weekday: str
    items: list[Item] = field(default_factory=list)
    cost: float = 0.0


def day_views(trip: Trip) -> list[DayView]:
    """按天分组条目；无日期时全部条目归入 Day 1。"""
    total = max(1, day_count(trip))
    grouped: dict[int, list[Item]] = defaultdict(list)
    for item in trip.items:
        grouped[item.day_index].append(item)
    views: list[DayView] = []
    for index in range(1, total + 1):
        d = day_date(trip, index)
        items = grouped.get(index, [])
        cost = sum(i.cost for i in items if i.cost is not None)
        views.append(
            DayView(
                day_index=index,
                date_iso=d.isoformat() if d else "",
                weekday=WEEKDAYS[d.weekday()] if d else "",
                items=items,
                cost=cost,
            )
        )
    # 日期为空但 day_index 超界的条目（不应出现，防御性归组）
    for index in sorted(k for k in grouped if k > total):
        views[-1].items.extend(grouped[index]) if views else None
    return views


@dataclass(frozen=True)
class BudgetSummary:
    """预算汇总。"""

    currency: str
    total: float | None
    planned: float
    diff: float | None
    over_budget: bool
    by_type: dict[str, float]
    by_day: dict[int, float]


def budget_summary(trip: Trip) -> BudgetSummary:
    """按类型/按天汇总费用；纯加法，无费用条目不计入。"""
    by_type: dict[str, float] = {key: 0.0 for key in ITEM_TYPES}
    by_day: dict[int, float] = defaultdict(float)
    planned = 0.0
    for item in trip.items:
        if item.cost is None:
            continue
        by_type[item.type] += item.cost
        by_day[item.day_index] += item.cost
        planned += item.cost
    total = trip.budget_total
    return BudgetSummary(
        currency=trip.currency,
        total=total,
        planned=planned,
        diff=(total - planned) if total is not None else None,
        over_budget=total is not None and planned > total,
        by_type=by_type,
        by_day=dict(by_day),
    )


def today_day_index(trip: Trip, today: date) -> int | None:
    """「今天」对应的 day_index；不在行程期内返回 None。"""
    if not trip.start_date:
        return None
    start = date.fromisoformat(trip.start_date)
    index = (today - start).days + 1
    if 1 <= index <= max(1, day_count(trip)):
        return index
    return None


def unfinished_count(trip: Trip) -> int:
    return sum(1 for item in trip.items if not item.done)


def packing_progress(trip: Trip) -> tuple[int, int]:
    """返回（已打包数, 总数）。"""
    return sum(1 for p in trip.packing if p.packed), len(trip.packing)
