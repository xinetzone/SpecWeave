"""数据模型校验分支测试（补齐 models.py 覆盖率）。"""

import pytest

from travel_planner.errors import ValidationError
from travel_planner.models import Item, PackingItem, Trip


def _base_item(**overrides):
    data = {"day_index": 1, "type": "sight", "title": "标题"}
    data.update(overrides)
    return data


def _base_trip(**overrides):
    data = {
        "name": "行程",
        "start_date": "2026-10-01",
        "end_date": "2026-10-02",
        "items": [],
        "packing": [],
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------------- Item 校验
def test_item_id_generated_and_validated():
    item = Item.from_dict(_base_item())
    assert item.id.startswith("i-")
    with pytest.raises(ValidationError, match="id 格式不合法"):
        Item.from_dict(_base_item(id="BAD!"))
    with pytest.raises(ValidationError, match="id 格式不合法"):
        Item.from_dict(_base_item(id=123))


def test_item_day_index_branches():
    with pytest.raises(ValidationError, match="day_index"):
        Item.from_dict(_base_item(day_index=None))
    for bad in (0, 366, "1", True):
        with pytest.raises(ValidationError, match="day_index"):
            Item.from_dict(_base_item(day_index=bad))


def test_item_type_and_source_enums():
    with pytest.raises(ValidationError, match="type"):
        Item.from_dict(_base_item(type="hiking"))
    with pytest.raises(ValidationError, match="source"):
        Item.from_dict(_base_item(source="robot"))


def test_item_title_rules():
    with pytest.raises(ValidationError, match="title"):
        Item.from_dict(_base_item(title=""))
    with pytest.raises(ValidationError, match="title"):
        Item.from_dict(_base_item(title="x" * 121))
    with pytest.raises(ValidationError, match="title"):
        Item.from_dict(_base_item(title=42))


def test_item_time_rules():
    with pytest.raises(ValidationError, match="时间格式"):
        Item.from_dict(_base_item(start_time="9:00"))
    with pytest.raises(ValidationError, match="必须是字符串"):
        Item.from_dict(_base_item(start_time=930))
    with pytest.raises(ValidationError, match="结束时间"):
        Item.from_dict(_base_item(start_time="14:00", end_time="09:00"))


def test_item_cost_rules():
    assert Item.from_dict(_base_item(cost="")).cost is None
    with pytest.raises(ValidationError, match="数字"):
        Item.from_dict(_base_item(cost="45"))
    with pytest.raises(ValidationError, match="数字"):
        Item.from_dict(_base_item(cost=True))
    with pytest.raises(ValidationError, match="之间"):
        Item.from_dict(_base_item(cost=-1))
    with pytest.raises(ValidationError, match="之间"):
        Item.from_dict(_base_item(cost=10_000_001))


def test_item_misc_fields():
    with pytest.raises(ValidationError, match="未知字段"):
        Item.from_dict(_base_item(foo=1))
    with pytest.raises(ValidationError, match="布尔值"):
        Item.from_dict(_base_item(done="yes"))
    with pytest.raises(ValidationError, match="location"):
        Item.from_dict(_base_item(location="x" * 201))
    with pytest.raises(ValidationError, match="notes"):
        Item.from_dict(_base_item(notes="x" * 2001))
    assert Item.from_dict(_base_item(done=None)).done is False
    assert Item.from_dict(_base_item(notes=None)).notes == ""


def test_item_non_dict_rejected():
    with pytest.raises(ValidationError, match="必须是对象"):
        Item.from_dict("not-a-dict")


# ---------------------------------------------------------------- Packing 校验
def test_packing_rules():
    pack = PackingItem.from_dict({"name": "身份证"})
    assert pack.id.startswith("p-") and pack.quantity == 1 and pack.packed is False
    with pytest.raises(ValidationError, match="name"):
        PackingItem.from_dict({"name": " "})
    with pytest.raises(ValidationError, match="quantity"):
        PackingItem.from_dict({"name": "x", "quantity": 0})
    with pytest.raises(ValidationError, match="quantity"):
        PackingItem.from_dict({"name": "x", "quantity": "2"})
    with pytest.raises(ValidationError, match="未知字段"):
        PackingItem.from_dict({"name": "x", "weight": 1})
    with pytest.raises(ValidationError, match="必须是对象"):
        PackingItem.from_dict([1])


# ---------------------------------------------------------------- Trip 校验
def test_trip_id_and_defaults():
    trip = Trip.from_dict({"name": "无日期行程"})
    assert trip.id.startswith("t-")
    assert trip.start_date == "" and trip.end_date == ""
    assert trip.currency == "CNY"
    assert trip.status == "planning"
    assert trip.created_at and trip.updated_at


def test_trip_currency_empty_falls_back():
    assert Trip.from_dict(_base_trip(currency="")).currency == "CNY"
    assert Trip.from_dict(_base_trip(currency=None)).currency == "CNY"


def test_trip_date_rules():
    with pytest.raises(ValidationError, match="日期格式"):
        Trip.from_dict(_base_trip(start_date="2026/10/01"))
    with pytest.raises(ValidationError, match="不是合法日期"):
        Trip.from_dict(_base_trip(start_date="2026-02-30"))
    with pytest.raises(ValidationError, match="必须是字符串"):
        Trip.from_dict(_base_trip(start_date=20261001))


def test_trip_container_rules():
    with pytest.raises(ValidationError, match="items"):
        Trip.from_dict(_base_trip(items="nope"))
    with pytest.raises(ValidationError, match="packing"):
        Trip.from_dict(_base_trip(packing={"a": 1}))
    with pytest.raises(ValidationError, match="未知字段"):
        Trip.from_dict(_base_trip(hacker=1))
    with pytest.raises(ValidationError, match="必须是对象"):
        Trip.from_dict(_base_trip(items=["nope"]))


def test_trip_budget_and_status():
    with pytest.raises(ValidationError, match="budget_total"):
        Trip.from_dict(_base_trip(budget_total=True))
    with pytest.raises(ValidationError, match="budget_total"):
        Trip.from_dict(_base_trip(budget_total="8000"))
    with pytest.raises(ValidationError, match="status"):
        Trip.from_dict(_base_trip(status="flying"))


def test_trip_keeps_created_at_when_given():
    trip = Trip.from_dict(_base_trip(created_at="2026-01-01T00:00:00"))
    assert trip.created_at == "2026-01-01T00:00:00"
    assert trip.updated_at == "2026-01-01T00:00:00"


def test_trip_date_shrink_overflow_message():
    trip = Trip.from_dict(
        _base_trip(items=[_base_item(day_index=2, title="第二天")])
    )
    data = trip.to_dict()
    data["end_date"] = "2026-10-01"
    with pytest.raises(ValidationError, match="超出行程天数"):
        Trip.from_dict(data)
