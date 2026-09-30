"""领域聚合测试：预算汇总、天数视图、今天映射、计数（TR-3.x）。"""

from datetime import date

from travel_planner.domain import (
    budget_summary,
    day_count,
    day_views,
    packing_progress,
    today_day_index,
    unfinished_count,
)
from travel_planner.models import Item, PackingItem, Trip


def make_trip(**overrides) -> Trip:
    trip = Trip(
        id="t-test00000001",
        name="测试",
        destination="杭州",
        start_date="2026-10-01",
        end_date="2026-10-03",
        currency="CNY",
        budget_total=8000,
    )
    trip.items = [
        Item(id="i-1", day_index=1, type="transport", title="高铁", cost=500),
        Item(id="i-2", day_index=1, type="sight", title="西湖", cost=0),
        Item(id="i-3", day_index=1, type="meal", title="午餐", cost=None),
        Item(id="i-4", day_index=2, type="lodging", title="住宿", cost=400),
        Item(id="i-5", day_index=3, type="shopping", title="特产", cost=300),
        Item(id="i-6", day_index=3, type="sight", title="已完成的景点", cost=45, done=True),
    ]
    trip.packing = [
        PackingItem(id="p-1", name="身份证", quantity=2, packed=True),
        PackingItem(id="p-2", name="充电宝", quantity=1, packed=False),
    ]
    for key, value in overrides.items():
        setattr(trip, key, value)
    return trip


def test_day_count_and_views():
    trip = make_trip()
    assert day_count(trip) == 3
    views = day_views(trip)
    assert [v.day_index for v in views] == [1, 2, 3]
    assert views[0].date_iso == "2026-10-01"
    assert views[0].weekday == "周四"  # 2026-10-01 是周四
    assert len(views[0].items) == 3
    assert len(views[1].items) == 1
    assert views[0].cost == 500
    assert views[1].cost == 400
    assert views[2].cost == 345


def test_budget_summary_matches_hand_computed():
    trip = make_trip()
    summary = budget_summary(trip)
    # 手算：500 + 0 + 400 + 300 + 45 = 1245
    assert summary.planned == 1245
    assert summary.total == 8000
    assert summary.diff == 8000 - 1245
    assert summary.over_budget is False
    assert summary.by_type["transport"] == 500
    assert summary.by_type["lodging"] == 400
    assert summary.by_type["shopping"] == 300
    assert summary.by_type["sight"] == 45
    assert summary.by_type["meal"] == 0
    assert summary.by_day == {1: 500, 2: 400, 3: 345}


def test_budget_over_budget_flag():
    trip = make_trip(budget_total=1000)
    summary = budget_summary(trip)
    assert summary.over_budget is True
    assert summary.diff == 1000 - 1245


def test_budget_without_total():
    trip = make_trip(budget_total=None)
    summary = budget_summary(trip)
    assert summary.total is None
    assert summary.diff is None
    assert summary.over_budget is False


def test_today_day_index():
    trip = make_trip()  # 10-01 ~ 10-03
    assert today_day_index(trip, date(2026, 10, 1)) == 1
    assert today_day_index(trip, date(2026, 10, 2)) == 2
    assert today_day_index(trip, date(2026, 10, 3)) == 3
    assert today_day_index(trip, date(2026, 9, 30)) is None
    assert today_day_index(trip, date(2026, 10, 4)) is None


def test_unfinished_and_packing_progress():
    trip = make_trip()
    assert unfinished_count(trip) == 5  # 6 条中 1 条 done
    assert packing_progress(trip) == (1, 2)


def test_no_dates_degrades_gracefully():
    trip = make_trip(start_date="", end_date="")
    assert day_count(trip) == 0
    views = day_views(trip)
    assert len(views) == 1  # 全部条目归入 Day 1
    assert len(views[0].items) == 6
    assert today_day_index(trip, date(2026, 10, 1)) is None
