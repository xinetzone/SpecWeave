"""Web 层测试：页面流转、CSRF/Origin、导入导出、AI 生成链路、密钥零泄露。"""

import json

import pytest
from fastapi.testclient import TestClient

from travel_planner.config import AppConfig, LLMConfig
from travel_planner.web.app import create_app

from .conftest import add_item, create_trip


def test_index_redirects(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/trips"


def test_pages_render(client, csrf):
    assert "我的行程" in client.get("/trips").text
    assert "新建行程" in client.get("/trips/new").text
    assert "导入数据" in client.get("/import").text
    assert "AI 未配置" in client.get("/trips").text
    resp = client.get("/trips/does-not-exist")
    assert resp.status_code == 404
    assert "行程不存在" in resp.text
    assert client.get("/health").json() == {"status": "ok", "trips": 0}


def test_bind_address_defaults_to_loopback(tmp_path):
    config = AppConfig(data_dir=tmp_path)
    assert config.host == "127.0.0.1"


def test_create_trip_flow(client, csrf, store):
    trip_id = create_trip(client, csrf)
    detail = client.get(f"/trips/{trip_id}")
    assert detail.status_code == 200
    assert "测试行程" in detail.text
    assert "Day 1" in detail.text and "Day 3" in detail.text
    trip = store.load(trip_id)
    assert trip.name == "测试行程"
    assert trip.budget_total == 8000


def test_create_trip_invalid_date_order(client, csrf, store):
    resp = client.post(
        "/trips",
        data={
            "name": "倒序",
            "destination": "",
            "start_date": "2026-10-05",
            "end_date": "2026-10-01",
            "currency": "CNY",
            "budget_total": "",
            "status": "planning",
            "notes": "",
            "csrf_token": csrf,
        },
        follow_redirects=False,
    )
    assert resp.status_code == 422
    assert "结束日期" in resp.text
    assert store.count() == 0


def test_item_lifecycle(client, csrf, store):
    trip_id = create_trip(client, csrf)
    add_item(client, csrf, trip_id, day_index="2", type="sight", title="灵隐寺", cost="45")
    add_item(client, csrf, trip_id, day_index="2", type="meal", title="素面", cost="20")
    trip = store.load(trip_id)
    assert [i.title for i in trip.items] == ["灵隐寺", "素面"]

    first_id = trip.items[0].id
    # 勾选
    client.post(f"/trips/{trip_id}/items/{first_id}/toggle", data={"csrf_token": csrf})
    assert store.load(trip_id).items[0].done is True
    # 再勾选取消
    client.post(f"/trips/{trip_id}/items/{first_id}/toggle", data={"csrf_token": csrf})
    assert store.load(trip_id).items[0].done is False
    # 下移
    client.post(
        f"/trips/{trip_id}/items/{first_id}/move",
        data={"direction": "down", "csrf_token": csrf},
    )
    assert [i.title for i in store.load(trip_id).items] == ["素面", "灵隐寺"]
    # 上移回去
    client.post(
        f"/trips/{trip_id}/items/{first_id}/move",
        data={"direction": "up", "csrf_token": csrf},
    )
    assert [i.title for i in store.load(trip_id).items] == ["灵隐寺", "素面"]
    # 编辑
    resp = client.get(f"/trips/{trip_id}/items/{first_id}/edit")
    assert resp.status_code == 200 and "灵隐寺" in resp.text
    client.post(
        f"/trips/{trip_id}/items/{first_id}/edit",
        data={
            "day_index": "3",
            "type": "sight",
            "title": "灵隐寺（改）",
            "start_time": "08:30",
            "end_time": "11:00",
            "location": "西湖区",
            "cost": "45",
            "notes": "早去",
            "csrf_token": csrf,
        },
    )
    edited = store.load(trip_id).items[0]
    assert edited.title == "灵隐寺（改）" and edited.day_index == 3
    # 删除
    client.post(f"/trips/{trip_id}/items/{first_id}/delete", data={"csrf_token": csrf})
    assert len(store.load(trip_id).items) == 1


def test_date_shrink_rejected_no_orphans(client, csrf, store):
    trip_id = create_trip(client, csrf)
    add_item(client, csrf, trip_id, day_index="3", title="第三天条目")
    resp = client.post(
        f"/trips/{trip_id}/edit",
        data={
            "name": "测试行程",
            "destination": "杭州",
            "start_date": "2026-10-01",
            "end_date": "2026-10-02",
            "currency": "CNY",
            "budget_total": "8000",
            "status": "planning",
            "notes": "",
            "csrf_token": csrf,
        },
        follow_redirects=False,
    )
    assert resp.status_code == 422
    assert "超出行程天数" in resp.text
    assert store.load(trip_id).end_date == "2026-10-03"  # 数据未被破坏


def test_packing_lifecycle(client, csrf, store):
    trip_id = create_trip(client, csrf)
    client.post(
        f"/trips/{trip_id}/packing",
        data={"name": "身份证", "quantity": "2", "csrf_token": csrf},
    )
    trip = store.load(trip_id)
    assert trip.packing[0].name == "身份证" and trip.packing[0].quantity == 2
    pack_id = trip.packing[0].id
    client.post(f"/trips/{trip_id}/packing/{pack_id}/toggle", data={"csrf_token": csrf})
    assert store.load(trip_id).packing[0].packed is True
    client.post(f"/trips/{trip_id}/packing/{pack_id}/delete", data={"csrf_token": csrf})
    assert store.load(trip_id).packing == []


def test_budget_panel_rendered(client, csrf):
    trip_id = create_trip(client, csrf)
    add_item(client, csrf, trip_id, type="transport", title="高铁", cost="500")
    add_item(client, csrf, trip_id, type="meal", title="午餐", cost="120")
    detail = client.get(f"/trips/{trip_id}").text
    assert "已登记" in detail
    assert "620" in detail  # 500 + 120
    assert "剩余" in detail  # 8000 - 620 > 0


def test_duplicate_and_delete(client, csrf, store):
    trip_id = create_trip(client, csrf)
    add_item(client, csrf, trip_id, title="某景点")
    resp = client.post(
        f"/trips/{trip_id}/duplicate", data={"csrf_token": csrf}, follow_redirects=False
    )
    assert resp.status_code == 303
    copy_id = resp.headers["location"].rsplit("/", 1)[-1]
    assert copy_id != trip_id
    assert store.load(copy_id).name == "测试行程（副本）"
    client.post(f"/trips/{trip_id}/delete", data={"csrf_token": csrf})
    assert store.count() == 1


# ---------------------------------------------------------------- 导入导出
def test_export_import_roundtrip(client, csrf, store):
    trip_id = create_trip(client, csrf)
    add_item(client, csrf, trip_id, title="景点A", cost="45")
    exported = client.get(f"/trips/{trip_id}/export")
    assert exported.status_code == 200
    assert exported.headers["content-type"].startswith("application/json")
    payload = exported.json()
    assert payload["name"] == "测试行程"
    assert payload["items"][0]["title"] == "景点A"

    # 删除原行程后导入：id 不再冲突，原 id 保留
    client.post(f"/trips/{trip_id}/delete", data={"csrf_token": csrf})
    assert store.count() == 0
    resp = client.post(
        "/import",
        files={"upload": ("t.json", exported.content, "application/json")},
        data={"csrf_token": csrf},
    )
    assert resp.status_code == 200
    assert "导入预览" in resp.text
    assert "原 id 保留" in resp.text
    resp = client.post(
        "/import/confirm", data={"payload": exported.text, "csrf_token": csrf},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert store.count() == 1
    assert store.load(trip_id).items[0].title == "景点A"  # round-trip 等价

    # 再次导入同一文件：id 冲突 → 自动生成新 id
    resp = client.post(
        "/import",
        files={"upload": ("t.json", exported.content, "application/json")},
        data={"csrf_token": csrf},
    )
    assert "id 已存在" in resp.text
    client.post("/import/confirm", data={"payload": exported.text, "csrf_token": csrf})
    assert store.count() == 2
    ids = [t.id for t in store.list_trips()]
    assert len(set(ids)) == 2


def test_export_all_wrapper(client, csrf):
    create_trip(client, csrf, name="行程一")
    create_trip(client, csrf, name="行程二")
    exported = client.get("/export-all")
    payload = exported.json()
    assert payload["format"] == "travel-planner-export"
    assert len(payload["trips"]) == 2
    # 包装格式可再导入
    resp = client.post(
        "/import",
        files={"upload": ("all.json", exported.content, "application/json")},
        data={"csrf_token": csrf},
    )
    assert resp.status_code == 200 and "行程一" in resp.text


def test_import_malformed_rejected(client, csrf, store):
    before = store.count()
    resp = client.post(
        "/import",
        files={"upload": ("bad.json", b"{ not json", "application/json")},
        data={"csrf_token": csrf},
    )
    assert resp.status_code == 422 and "不是合法 JSON" in resp.text
    resp = client.post(
        "/import",
        files={
            "upload": (
                "bad.json",
                json.dumps({"name": "x", "hacker_field": 1}).encode(),
                "application/json",
            )
        },
        data={"csrf_token": csrf},
    )
    assert resp.status_code == 422 and "未知字段" in resp.text
    resp = client.post(
        "/import",
        files={"upload": ("bad.json", b"\xff\xfe\x00bad-utf8", "application/json")},
        data={"csrf_token": csrf},
    )
    assert resp.status_code == 422 and "UTF-8" in resp.text
    assert store.count() == before


# ---------------------------------------------------------------- 安全
def test_csrf_rejections(client):
    resp = client.post("/trips", data={"name": "无token"})
    assert resp.status_code == 403
    resp = client.post("/trips", data={"name": "错token", "csrf_token": "wrong"})
    assert resp.status_code == 403


def test_origin_rejection(client, csrf):
    resp = client.post(
        "/trips",
        data={"name": "跨源", "csrf_token": csrf},
        headers={"Origin": "http://evil.example.com"},
    )
    assert resp.status_code == 403
    assert "跨源请求" in resp.text


# ---------------------------------------------------------------- AI 链路
def _ai_client(store, factory):
    cfg = LLMConfig(base_url="http://llm.test/v1", api_key="sk-test", model="m", timeout=5)
    app = create_app(store, cfg, llm_client_factory=factory)
    with TestClient(app) as c:
        c.get("/trips")
        yield c


def test_ai_generate_preview_and_import(store, mock_llm_client):
    factory, captured, responder = mock_llm_client
    client = next(_ai_client(store, factory))
    csrf = client.cookies.get("tp_csrf")
    trip_id = create_trip(client, csrf)

    # 生成 → 预览页
    resp = client.post(
        f"/trips/{trip_id}/generate",
        data={
            "destination": "杭州",
            "start_date": "2026-10-01",
            "end_date": "2026-10-02",
            "people": "2",
            "preferences": "喜欢湖景",
            "budget_tier": "舒适",
            "csrf_token": csrf,
        },
    )
    assert resp.status_code == 200
    assert "草稿预览" in resp.text
    assert "西湖环湖" in resp.text and "灵隐寺" in resp.text
    assert len(captured) == 1
    assert store.load(trip_id).items == []  # 草稿未落盘

    # 导入：保留 2 条中的第 1 条（剔除 di_1_*）
    resp = client.post(
        f"/trips/{trip_id}/import-draft",
        data={
            "draft_count": "2",
            "di_0_keep": "1",
            "di_0_day": "1",
            "di_0_type": "sight",
            "di_0_title": "西湖环湖",
            "di_0_start_time": "09:00",
            "di_0_end_time": "11:30",
            "di_0_location": "西湖",
            "di_0_cost": "0",
            "di_0_notes": "早上人少",
            "di_1_day": "2",
            "di_1_type": "sight",
            "di_1_title": "灵隐寺",
            "di_1_cost": "45",
            "csrf_token": csrf,
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    trip = store.load(trip_id)
    assert len(trip.items) == 1
    assert trip.items[0].source == "ai"
    assert trip.items[0].title == "西湖环湖"
    assert trip.items[0].day_index == 1


def test_ai_cancel_keeps_trip_unchanged(store, mock_llm_client):
    factory, captured, responder = mock_llm_client
    client = next(_ai_client(store, factory))
    csrf = client.cookies.get("tp_csrf")
    trip_id = create_trip(client, csrf)
    before = store.load(trip_id).to_dict()
    # 预览后用户点「取消」= 仅 GET 详情页，无任何写动作
    client.post(
        f"/trips/{trip_id}/generate",
        data={
            "destination": "杭州",
            "start_date": "2026-10-01",
            "end_date": "2026-10-02",
            "people": "1",
            "csrf_token": csrf,
        },
    )
    client.get(f"/trips/{trip_id}")
    assert store.load(trip_id).to_dict() == before


def test_ai_failure_renders_chinese_error(store):
    import httpx

    from travel_planner.llm import LLMClient

    def handler(request):
        raise httpx.ConnectError("refused")

    def client_factory():
        return LLMClient(
            LLMConfig(base_url="http://llm.test/v1", api_key="sk-x", model="m", timeout=5),
            transport=httpx.MockTransport(handler),
        )

    client = next(_ai_client(store, client_factory))
    csrf = client.cookies.get("tp_csrf")
    trip_id = create_trip(client, csrf)
    resp = client.post(
        f"/trips/{trip_id}/generate",
        data={
            "destination": "杭州",
            "start_date": "2026-10-01",
            "end_date": "2026-10-02",
            "people": "1",
            "csrf_token": csrf,
        },
    )
    assert resp.status_code == 502
    assert "不可达" in resp.text
    assert store.load(trip_id).items == []


def test_ai_not_configured_degrades(client, csrf, store):
    trip_id = create_trip(client, csrf)
    form = client.get(f"/trips/{trip_id}/generate")
    assert "尚未配置" in form.text
    resp = client.post(
        f"/trips/{trip_id}/generate",
        data={
            "destination": "杭州",
            "start_date": "2026-10-01",
            "end_date": "2026-10-02",
            "people": "1",
            "csrf_token": csrf,
        },
    )
    assert resp.status_code == 502
    assert "LLM 未配置" in resp.text
    # 其余功能不受影响
    assert "我的行程" in client.get("/trips").text


def test_secret_never_leaked_in_responses(store, configured_llm_cfg):
    app = create_app(store, configured_llm_cfg)
    with TestClient(app) as c:
        c.get("/trips")
        csrf = c.cookies.get("tp_csrf")
        trip_id = create_trip(c, csrf)
        pages = [
            c.get("/trips").text,
            c.get(f"/trips/{trip_id}").text,
            c.get(f"/trips/{trip_id}/generate").text,
            c.get("/trips/none").text,
        ]
        for text in pages:
            assert "sk-test-SECRET" not in text
