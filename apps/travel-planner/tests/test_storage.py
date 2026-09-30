"""存储层测试：CRUD round-trip、校验、原子写、备份滚动、路径守卫（TR-2.x）。"""

import json

import pytest

from travel_planner.errors import StorageError, ValidationError
from travel_planner.models import Trip
from travel_planner.storage import TripStore


def _trip_data(**overrides):
    data = {
        "name": "杭州国庆",
        "destination": "杭州",
        "start_date": "2026-10-01",
        "end_date": "2026-10-03",
        "currency": "CNY",
        "budget_total": 8000,
        "status": "planning",
        "notes": "两人出行",
        "items": [
            {
                "id": "i-000000000001",
                "day_index": 1,
                "type": "sight",
                "title": "西湖",
                "start_time": "09:00",
                "end_time": "11:30",
                "location": "西湖",
                "cost": 0,
                "notes": "早去",
                "done": False,
                "source": "manual",
            },
            {"day_index": 2, "type": "meal", "title": "楼外楼", "cost": 120},
        ],
        "packing": [{"id": "p-000000000001", "name": "身份证", "quantity": 2, "packed": True}],
    }
    data.update(overrides)
    return data


def test_trip_crud_roundtrip(store, data_dir):
    trip = store.save(Trip.from_dict(_trip_data()))
    assert (data_dir / "trips" / f"{trip.id}.json").is_file()
    loaded = store.load(trip.id)
    assert loaded.name == "杭州国庆"
    assert loaded.budget_total == 8000
    assert len(loaded.items) == 2
    assert loaded.items[0].id == "i-000000000001"
    assert loaded.items[0].cost == 0
    assert loaded.items[1].cost == 120
    assert loaded.packing[0].packed is True
    # round-trip 等价
    assert loaded.to_dict() == store.load(trip.id).to_dict()
    store.delete(trip.id)
    with pytest.raises(StorageError, match="不存在"):
        store.load(trip.id)


def test_validation_rejections():
    with pytest.raises(ValidationError, match="结束日期"):
        Trip.from_dict(_trip_data(end_date="2026-09-30"))
    with pytest.raises(ValidationError, match="未知字段"):
        Trip.from_dict(_trip_data(foo=1))
    with pytest.raises(ValidationError, match="name：不能为空"):
        Trip.from_dict(_trip_data(name="   "))
    with pytest.raises(ValidationError, match="day_index=4 超出行程天数"):
        Trip.from_dict(_trip_data(items=[{"day_index": 4, "type": "other", "title": "x"}]))
    with pytest.raises(ValidationError, match="结束时间"):
        Trip.from_dict(
            _trip_data(
                items=[
                    {
                        "day_index": 1,
                        "type": "other",
                        "title": "x",
                        "start_time": "11:00",
                        "end_time": "09:00",
                    }
                ]
            )
        )
    with pytest.raises(ValidationError, match="type"):
        Trip.from_dict(_trip_data(items=[{"day_index": 1, "type": "hiking", "title": "x"}]))


def test_duplicate_resets_state(store):
    trip = store.save(Trip.from_dict(_trip_data()))
    copy = store.duplicate(trip.id)
    assert copy.id != trip.id
    assert copy.name == "杭州国庆（副本）"
    assert copy.status == "planning"
    assert all(item.done is False for item in copy.items)
    assert all(p.packed is False for p in copy.packing)
    assert len(copy.items) == 2
    assert len(copy.packing) == 1


def test_atomic_write_keeps_original(store, monkeypatch, data_dir):
    trip = store.save(Trip.from_dict(_trip_data()))
    path = data_dir / "trips" / f"{trip.id}.json"
    original = path.read_bytes()
    trip.name = "改名会失败"

    import travel_planner.storage as storage_mod

    def boom(*args, **kwargs):
        raise OSError("disk on fire")

    monkeypatch.setattr(storage_mod.os, "replace", boom)
    with pytest.raises(StorageError, match="写入失败"):
        store.save(trip)
    assert path.read_bytes() == original
    assert list((data_dir / "trips").glob(".*tmp*")) == []
    monkeypatch.undo()
    store.save(trip)
    assert store.load(trip.id).name == "改名会失败"


def test_backup_rolling_keep_five(store, data_dir):
    trip = Trip.from_dict(_trip_data())
    for i in range(7):
        trip.name = f"第{i}版"
        store.save(trip)
    backups = list((data_dir / "backups").glob(f"{trip.id}-*.json"))
    assert len(backups) == 5


def test_path_guard_rejects_bad_ids(store):
    for bad in ("../evil", "a/b", "UPPER", "中文名", ""):
        with pytest.raises(StorageError):
            store._trip_path(bad)
    with pytest.raises(StorageError):
        store.load("../evil")
    assert store.exists("../evil") is False


def test_list_trips_skips_corrupt_files(store, data_dir):
    good = store.save(Trip.from_dict(_trip_data()))
    bad = data_dir / "trips" / "t-badfile0001.json"
    bad.write_text("{ not json", encoding="utf-8")
    trips = store.list_trips()
    assert [t.id for t in trips] == [good.id]
    assert len(store.load_errors) == 1
    assert "t-badfile0001.json" in store.load_errors[0]


def test_import_payload_validation_roundtrip(store):
    """导出 → 导入数据等价（TR-7.1 的存储侧验证）。"""
    trip = store.save(Trip.from_dict(_trip_data()))
    exported = json.dumps(trip.to_dict(), ensure_ascii=False)
    reimported = Trip.from_dict(json.loads(exported))
    assert reimported.to_dict() == trip.to_dict()
