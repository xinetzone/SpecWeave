"""仓储测试：内存降级全链路 + Supabase 注入防护与聚合（AC-3 / AC-4 / AC-7 / AC-8）。"""

import pytest

from admin_console.config import Config
from admin_console.store import Conflict, MemoryStore, SupabaseStore

from conftest import FakeResponse


def make_cfg(**kwargs):
    return Config(session_secret="unit-secret", **kwargs)  # nosec 单元测试固定桩值


# ---------- 内存降级 ----------


def test_memory_store_seeds_demo_admin():
    store = MemoryStore(make_cfg())
    assert store.admin_by_email("admin@example.com") is not None
    assert store.verify_credentials("admin@example.com", "admin12345")  # nosec 降级模式演示账号桩值
    assert store.verify_credentials("admin@example.com", "wrong") is None


def test_demo_admin_is_disabled_in_production(monkeypatch):
    """Vercel 生产环境 fail-closed：不得启用口令已知的演示账号。"""
    monkeypatch.setenv("VERCEL", "1")
    cfg = Config.from_env()
    assert cfg.demo_admin_enabled is False
    store = MemoryStore(cfg)
    assert store.admin_by_email("admin@example.com") is None
    assert store.count_admins() == 0


def test_memory_store_unknown_email_has_constant_behaviour():
    store = MemoryStore(make_cfg())
    assert store.verify_credentials("nobody@example.com", "whatever") is None


def test_memory_store_item_crud_roundtrip():
    store = MemoryStore(make_cfg())
    created = store.create_item({"title": "测试内容", "status": "draft", "tags": ["产品"]})
    assert created["status"] == "draft"
    assert created["tags"] == ["产品"]

    fetched = store.get_item(created["id"])
    assert fetched["title"] == "测试内容"

    updated = store.update_item(created["id"], {"status": "published"}, actor="tester")
    assert updated["status"] == "published"
    assert updated["published_at"]

    assert store.delete_item(created["id"]) is True
    assert store.get_item(created["id"]) is None


def test_memory_store_optimistic_concurrency():
    store = MemoryStore(make_cfg())
    item = store.create_item({"title": "并发测试"})
    with pytest.raises(Conflict):
        store.update_item(item["id"], {"title": "他人修改"}, expected_updated_at="1999-01-01T00:00:00+00:00")
    assert store.update_item(item["id"], {"title": "我的修改"},
                             expected_updated_at=item["updated_at"])["title"] == "我的修改"


def test_memory_store_blocks_deleting_used_category():
    store = MemoryStore(make_cfg())
    category = store.create_category({"name": "资讯", "slug": "news"})
    store.create_item({"title": "某条内容", "category_id": category["id"]})
    with pytest.raises(Conflict):
        store.delete_category(category["id"])


def test_memory_store_blocks_deleting_used_tag():
    store = MemoryStore(make_cfg())
    store.create_item({"title": "带标签", "tags": ["热点"]})
    tag = [t for t in store.list_tags() if t["name"] == "热点"][0]
    with pytest.raises(Conflict):
        store.delete_tag(tag["id"])


def test_memory_store_dashboard_aggregation_matches_manual_count():
    store = MemoryStore(make_cfg())
    before = store.dashboard()
    for index in range(7):
        store.create_item({"title": f"内容 {index}", "status": "published" if index % 2 else "draft"})
    data = store.dashboard()
    assert data["total"] == before["total"] + 7 == len(store.items)
    assert data["by_status"]["draft"] == before["by_status"]["draft"] + 4
    assert data["by_status"]["published"] == before["by_status"]["published"] + 3
    assert len(data["trend"]) == 14


def test_memory_store_pagination_and_search():
    store = MemoryStore(make_cfg())
    for index in range(12):
        store.create_item({"title": f"条目 {index}", "summary": "通用"})
    rows, total = store.list_items({"page": "2", "page_size": "5"})
    assert total == len(store.items)
    assert len(rows) <= 5
    rows, _ = store.list_items({"q": "条目 11"})
    assert len(rows) == 1


def test_memory_store_bulk_actions():
    store = MemoryStore(make_cfg())
    ids = [store.create_item({"title": f"批量 {i}"})["id"] for i in range(3)]
    assert store.bulk_update(ids, "archived") == 3
    assert all(store.get_item(i)["status"] == "archived" for i in ids)
    store.bulk_update(ids, "delete")
    assert all(store.get_item(i) is None for i in ids)


# ---------- Supabase：注入防护与聚合 ----------


def test_supabase_store_encodes_filter_values(http):
    cfg = make_cfg(supabase_url="https://demo.supabase.co", supabase_service_role_key="k")
    http.set_response(FakeResponse(200, b"[]", {"content-range": "0-0/0"}))
    SupabaseStore(cfg).list_items({"q": "a' or 1=1--; drop table ac_items"})
    url = http.last_url()
    assert "'" not in url
    assert "; drop" not in url
    assert "%27" in url or "or+1%3D1" in url or "1%3D1" in url


def test_supabase_store_whitelists_sort_fields(http):
    cfg = make_cfg(supabase_url="https://demo.supabase.co", supabase_service_role_key="k")
    http.set_response(FakeResponse(200, b"[]", {"content-range": "0-0/0"}))
    SupabaseStore(cfg).list_items({"sort": "id; drop", "order": "asc"})
    assert "updated_at" in http.last_url() or "created_at" in http.last_url()


def test_supabase_store_rejects_unknown_table():
    cfg = make_cfg(supabase_url="https://demo.supabase.co", supabase_service_role_key="k")
    with pytest.raises(ValueError):
        SupabaseStore(cfg)._rows("pg_tables; drop", [("select", "*")])


def test_supabase_store_parses_total_from_content_range(http):
    cfg = make_cfg(supabase_url="https://demo.supabase.co", supabase_service_role_key="k")
    http.set_response(FakeResponse(200, b"[]", {"content-range": "0-19/137"}))
    _, total = SupabaseStore(cfg)._rows("ac_items", [("select", "*")], with_count=True)
    assert total == 137


def test_supabase_store_degrades_on_network_failure(http):
    cfg = make_cfg(supabase_url="https://demo.supabase.co", supabase_service_role_key="k")
    http.set_response(FakeResponse(0, b""))
    store = SupabaseStore(cfg)
    store._rows("ac_items", [("select", "id")])
    assert store.degraded is True


def test_build_store_falls_back_to_memory_without_cloud():
    from admin_console.store import build_store

    assert isinstance(build_store(make_cfg()), MemoryStore)
