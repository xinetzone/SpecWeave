"""存储层与运营服务：表 CRUD、原子写、单实例锁、广告/公告/配置/审计。"""

from pathlib import Path

import pytest

from inurl_byok_token_hub.models import User
from inurl_byok_token_hub.storage import Repository, SingleInstanceLock, atomic_write_text
from inurl_byok_token_hub.storage.store import Store

# ---------------------------------------------------------------- 表与仓库


def _user(idx: int = 0) -> User:
    return User(id=f"u{idx}", email=f"u{idx}@local", password_digest="d", password_salt="00")


def test_table_crud_roundtrip(tmp_path: Path):
    repo = Repository(tmp_path)
    table = repo.table("users", User.model_validate)
    assert table.all() == []
    table.add(_user(0))
    table.add(_user(1))
    assert len(table.all()) == 2
    assert table.find(lambda u: u.id == "u1") is not None
    assert len(table.where(lambda u: u.id.startswith("u"))) == 2
    table.replace(lambda u: u.id == "u1", _user(9))
    assert table.find(lambda u: u.id == "u9") is not None
    assert table.remove(lambda u: u.id == "u9") == 1
    assert len(table.all()) == 1


def test_table_upsert_and_clear(tmp_path: Path):
    repo = Repository(tmp_path)
    table = repo.table("users", User.model_validate)
    table.upsert(lambda u: u.id == "uX", User(id="uX", email="a@local", password_digest="d", password_salt="00"))
    table.upsert(lambda u: u.id == "uX", User(id="uX", email="b@local", password_digest="d", password_salt="00"))
    assert len(table.all()) == 1
    assert table.all()[0].email == "b@local"
    table.extend([_user(7), _user(8)])
    assert len(table.all()) == 3
    table.clear()
    assert table.all() == []


def test_table_replace_missing_raises(tmp_path: Path):
    repo = Repository(tmp_path)
    table = repo.table("users", User.model_validate)
    with pytest.raises(Exception):
        table.replace(lambda u: u.id == "nope", _user(1))


def test_table_reloads_from_disk(tmp_path: Path):
    repo = Repository(tmp_path)
    repo.table("users", User.model_validate).add(_user(0))
    fresh = Repository(tmp_path)
    assert len(fresh.table("users", User.model_validate).all()) == 1


def test_table_corrupt_json_raises(tmp_path: Path):
    (tmp_path / "users.json").write_text("{not json", encoding="utf-8")
    repo = Repository(tmp_path)
    with pytest.raises(Exception):
        repo.table("users", User.model_validate).all()


def test_atomic_write_text_is_replace_based(tmp_path: Path):
    target = tmp_path / "a.txt"
    atomic_write_text(target, "first")
    assert target.read_text(encoding="utf-8") == "first"
    atomic_write_text(target, "second")
    assert target.read_text(encoding="utf-8") == "second"
    assert list(tmp_path.glob(".*tmp")) == [], "临时文件不得残留"


def test_raw_text_concatenates_tables(tmp_path: Path):
    repo = Repository(tmp_path)
    repo.table("users", User.model_validate).add(_user(0))
    assert "u0@local" in repo.raw_text()


def test_store_exposes_data_dir_and_admin_config(tmp_path: Path):
    store = Store(tmp_path)
    assert store.data_dir == tmp_path
    config = store.ensure_admin_config()
    assert store.ensure_admin_config() == config
    updated = store.set_admin_config(config.model_copy(update={"turnstile_enabled": True}))
    assert updated.turnstile_enabled is True


def test_store_custom_catalog(tmp_path: Path):
    store = Store(tmp_path)
    assert len(store.custom_catalog()) == 1
    assert store.custom_catalog()[0].providers == ()


# ---------------------------------------------------------------- 单实例锁


def test_single_instance_lock_blocks_second_handle(tmp_path: Path):
    """锁文件与 PID 记录；同进程内二次获取的行为依赖平台实现，故分开断言。

    Windows 的文件锁以进程为单位（同进程多句柄可重复加锁），跨进程互斥仍成立；
    POSIX 的 ``fcntl.flock`` 同进程二次加锁亦会失败。本测试覆盖「已加锁则释放后可
    重新获取」与「锁文件写入 PID」两项确定行为。
    """
    import sys

    lock_path = tmp_path / "byok.pid"
    first = SingleInstanceLock(lock_path)
    first.acquire()
    assert lock_path.exists(), "加锁后锁文件应存在（Windows 下文件被占用，不读取内容）"

    second = SingleInstanceLock(lock_path)
    if sys.platform != "win32":
        with pytest.raises(Exception) as exc:
            second.acquire()
        assert "已有实例" in str(exc.value)

    first.release()
    third = SingleInstanceLock(lock_path)
    third.acquire()
    third.release()


def test_single_instance_lock_context_manager(tmp_path: Path):
    lock_path = tmp_path / "ctx.pid"
    with SingleInstanceLock(lock_path) as lock:
        assert lock._fh is not None
    assert lock._fh is None


def test_single_instance_lock_release_is_idempotent(tmp_path: Path):
    lock = SingleInstanceLock(tmp_path / "idem.pid")
    lock.release()  # 未获取时释放不应抛错
    lock.acquire()
    lock.release()


# ---------------------------------------------------------------- 运营服务


def test_ops_seed_and_public_content(hub):
    hub.ops.ensure_seed()
    assert hub.ops.ads(), "应有一条示例广告"
    news = hub.ops.news()
    assert len(news) == 5
    assert sum(1 for n in news if n.featured) == 1
    assert all(n.enabled for n in news)


def test_ops_add_ad_and_news(hub):
    ad = hub.ops.add_ad("标题", "正文", "https://example.com")
    assert ad.title == "标题"
    item = hub.ops.add_news("公告", "摘要", featured=True)
    assert item.featured is True
    assert any(n.id == item.id for n in hub.ops.news())


def test_ops_config_update_and_audit(hub):
    config = hub.ops.config()
    assert config.turnstile_enabled is False
    updated = hub.ops.set_config(turnstile_enabled=True, announcement="维护中")
    assert updated.turnstile_enabled is True
    assert updated.announcement == "维护中"
    with pytest.raises(ValueError):
        hub.ops.set_config(unknown_key=1)


def test_ops_audit_log(hub):
    hub.ops.audit(actor_user_id="u1", action="test.action", target_id="t1")
    hub.ops.audit(actor_user_id="u2", action="test.action2", target_id="t2", result="fail")
    log = hub.ops.audit_log()
    assert len(log) == 2
    assert log[0].action == "test.action2", "审计日志按时间倒序"
    assert any(e.result == "fail" for e in log)


def test_ops_modules_are_eight(hub):
    modules = hub.ops.modules()
    assert len(modules) == 8
    keys = {m["key"] for m in modules}
    assert keys == {
        "users",
        "catalog",
        "plans",
        "redemption",
        "usage",
        "content",
        "config",
        "audit",
    }


def test_public_ops_endpoints_via_api(client):
    ads = client.get("/api/ads").json()
    news = client.get("/api/news").json()
    assert ads["data"]
    assert news["data"]
    assert len(news["featured"]) == 1


def test_turnstile_default_disabled(client):
    assert client.get("/api/turnstile").json()["enabled"] is False


def test_catalog_endpoint_counts(client):
    body = client.get("/api/catalog").json()
    counts = body["counts"]
    assert counts["providers"] == 46
    assert counts["free"] == 17
    assert counts["paid"] == 29
    assert counts["hidden"] == 10
    assert counts["models"] == 133
    # ?all=1 与默认返回同一份数据（对齐 F-077 既有行为）
    assert client.get("/api/catalog", params={"all": "1"}).json()["providers"] == body["providers"]


def test_plans_endpoint_exposes_free_key_limit(client):
    body = client.get("/api/billing/plans").json()
    assert body["freeKeyLimit"] == 3
    assert [p["price_cents"] for p in body["data"]] == [0, 990, 2990]


def test_hide_hidden_providers_switch(settings, data_dir):
    """``hide_hidden_providers=True`` 时，隐藏厂商不再随公开接口下发。"""
    from inurl_byok_token_hub.config import Settings
    from inurl_byok_token_hub.services.hub import build_hub

    hidden_settings = Settings(**{**settings.__dict__, "hide_hidden_providers": True})
    hidden_hub = build_hub(hidden_settings)
    body = _client_for(hidden_settings, hidden_hub).get("/api/catalog").json()
    assert all(p["public"] for p in body["providers"]), "开启开关后隐藏厂商不得下发"
    assert len(body["providers"]) < 46


def _client_for(settings, hub):
    from fastapi.testclient import TestClient

    from inurl_byok_token_hub.api.app import create_app

    return TestClient(create_app(settings, hub=hub))
