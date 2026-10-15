"""TR-16.2：/notifications 五端点分支（upstream: notifications.ts + notifications-db.ts）。

覆盖：鉴权、分页默认/归一化、created_at DESC、属主隔离（他人通知 404）、
未读计数、单条已读幂等且不覆盖 read_at、全部已读、清空、payload 损坏兜底
与非字符串 rejectReason 透传。
"""

import json
import time

import pytest
from fastapi.testclient import TestClient

from doocs_md_py.server import db
from doocs_md_py.server.app import create_app
from doocs_md_py.server.config import Config
from doocs_md_py.server.security import issue_token

SECRET = "notif-secret-0123456789-abcdef-ghijkl"


@pytest.fixture
def ctx(conn):
    db.upsert_user(conn, {
        "id": "u1", "github_id": 1, "login": "octocat",
        "name": "Octo", "avatar": None,
    })
    db.upsert_user(conn, {
        "id": "u2", "github_id": 2, "login": "procat",
        "name": "Pro", "avatar": None,
    })
    app = create_app(Config(jwt_secret=SECRET), conn=conn)
    client = TestClient(app)

    def headers(uid, login):
        return {"Authorization": f"Bearer {issue_token(SECRET, uid, login, now_s=2_000_000_000)}"}

    return {"client": client, "conn": conn, "h1": headers("u1", "octocat"),
            "h2": headers("u2", "procat")}


def _seed(conn, user_id, nid, ntype, created_at, *, payload=None, read_at=None):
    payload = payload or {
        "itemId": "m1", "itemType": "theme", "name": "N", "slug": "s", "rejectReason": None,
    }
    conn.execute(
        "INSERT INTO notifications (id, user_id, type, payload, read_at, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (nid, user_id, ntype, json.dumps(payload, ensure_ascii=False), read_at, created_at),
    )
    conn.commit()


# ---- 鉴权 ----


@pytest.mark.parametrize(("method", "path"), [
    ("GET", "/notifications"),
    ("GET", "/notifications/unread-count"),
    ("POST", "/notifications/read-all"),
    ("POST", "/notifications/n1/read"),
    ("DELETE", "/notifications"),
])
def test_auth_required(ctx, method, path):
    resp = ctx["client"].request(method, path)
    assert resp.status_code == 401
    assert resp.json() == {"error": "unauthorized"}


def test_invalid_token_rejected(ctx):
    resp = ctx["client"].get(
        "/notifications", headers={"Authorization": "Bearer not-a-jwt"}
    )
    assert resp.status_code == 401
    assert resp.json() == {"error": "invalid_token"}


# ---- 列表与分页 ----


def test_empty_list_default_paging(ctx):
    resp = ctx["client"].get("/notifications", headers=ctx["h1"])
    assert resp.status_code == 200
    assert resp.json() == {"items": [], "total": 0, "page": 1, "pageSize": 30}


def test_list_desc_order_shape_and_owner_isolation(ctx):
    _seed(ctx["conn"], "u1", "a1", "marketplace_pending", 1000)
    _seed(ctx["conn"], "u1", "a2", "marketplace_approved", 2000)
    _seed(ctx["conn"], "u2", "b1", "marketplace_rejected", 3000)

    resp = ctx["client"].get("/notifications", headers=ctx["h1"])
    body = resp.json()
    assert body["total"] == 2
    assert [i["id"] for i in body["items"]] == ["a2", "a1"]
    first = body["items"][0]
    assert set(first) == {"id", "type", "payload", "readAt", "createdAt"}
    assert first["readAt"] is None
    assert first["payload"] == {
        "itemId": "m1", "itemType": "theme", "name": "N", "slug": "s",
        "rejectReason": None,
    }

    # u2 只见自己
    other = ctx["client"].get("/notifications", headers=ctx["h2"]).json()
    assert [i["id"] for i in other["items"]] == ["b1"]


def test_pagination_normalization(ctx):
    for i in range(3):
        _seed(ctx["conn"], "u1", f"n{i}", "marketplace_pending", 1000 + i)

    # page=0 → 1；pageSize=2
    body = ctx["client"].get(
        "/notifications?page=0&pageSize=2", headers=ctx["h1"]
    ).json()
    assert body["page"] == 1 and body["pageSize"] == 2
    assert [i["id"] for i in body["items"]] == ["n2", "n1"]

    # 第二页
    body = ctx["client"].get(
        "/notifications?page=2&pageSize=2", headers=ctx["h1"]
    ).json()
    assert [i["id"] for i in body["items"]] == ["n0"]

    # pageSize 非数字 → 30；过大 → 50
    bad_size = ctx["client"].get(
        "/notifications?pageSize=abc", headers=ctx["h1"]
    ).json()
    assert bad_size["pageSize"] == 30
    capped = ctx["client"].get(
        "/notifications?pageSize=10000", headers=ctx["h1"]
    ).json()
    assert capped["pageSize"] == 50

    # page 非数字 → 1
    assert ctx["client"].get(
        "/notifications?page=xyz", headers=ctx["h1"]
    ).json()["page"] == 1


# ---- 未读计数 ----


def test_unread_count(ctx):
    _seed(ctx["conn"], "u1", "a1", "marketplace_pending", 1)
    _seed(ctx["conn"], "u1", "a2", "marketplace_pending", 2, read_at=999)
    _seed(ctx["conn"], "u2", "b1", "marketplace_pending", 3)
    count = ctx["client"].get(
        "/notifications/unread-count", headers=ctx["h1"]
    ).json()["count"]
    assert count == 1


# ---- 单条已读 ----


def test_mark_read_404_for_missing_and_others(ctx):
    _seed(ctx["conn"], "u2", "b1", "marketplace_pending", 1)
    assert ctx["client"].post(
        "/notifications/ghost/read", headers=ctx["h1"]
    ).status_code == 404
    # 他人通知 → 属主条件不命中，同样 404
    assert ctx["client"].post(
        "/notifications/b1/read", headers=ctx["h1"]
    ).status_code == 404
    # u2 自己可以读
    assert ctx["client"].post(
        "/notifications/b1/read", headers=ctx["h2"]
    ).json() == {"ok": True}


def test_mark_read_idempotent_keeps_first_read_at(ctx):
    _seed(ctx["conn"], "u1", "a1", "marketplace_pending", 1)
    first = ctx["client"].post("/notifications/a1/read", headers=ctx["h1"])
    assert first.status_code == 200 and first.json() == {"ok": True}
    read_at_1 = ctx["conn"].execute(
        "SELECT read_at FROM notifications WHERE id = 'a1'"
    ).fetchone()["read_at"]
    assert read_at_1 is not None

    time.sleep(0.02)
    second = ctx["client"].post("/notifications/a1/read", headers=ctx["h1"])
    assert second.status_code == 200
    read_at_2 = ctx["conn"].execute(
        "SELECT read_at FROM notifications WHERE id = 'a1'"
    ).fetchone()["read_at"]
    # 幂等：已读不重复盖时间戳
    assert read_at_2 == read_at_1
    assert ctx["client"].get(
        "/notifications/unread-count", headers=ctx["h1"]
    ).json()["count"] == 0


# ---- 全部已读 ----


def test_read_all_only_affects_own_unread(ctx):
    _seed(ctx["conn"], "u1", "a1", "marketplace_pending", 1)
    _seed(ctx["conn"], "u1", "a2", "marketplace_pending", 2, read_at=500)
    _seed(ctx["conn"], "u2", "b1", "marketplace_pending", 3)

    resp = ctx["client"].post("/notifications/read-all", headers=ctx["h1"])
    assert resp.status_code == 200 and resp.json() == {"ok": True}

    rows = ctx["conn"].execute(
        "SELECT id, read_at FROM notifications ORDER BY id"
    ).fetchall()
    by_id = {r["id"]: r["read_at"] for r in rows}
    assert by_id["a1"] is not None
    assert by_id["a2"] == 500  # 已读不被覆盖
    assert by_id["b1"] is None  # 他人未读保持


def test_read_all_static_path_not_swallowed_by_id_route(ctx):
    # /read-all 不能被 /{id}/read 路由吞掉（注册顺序回归）
    _seed(ctx["conn"], "u1", "a1", "marketplace_pending", 1)
    assert ctx["client"].post(
        "/notifications/read-all", headers=ctx["h1"]
    ).status_code == 200
    assert ctx["conn"].execute(
        "SELECT read_at FROM notifications WHERE id = 'a1'"
    ).fetchone()["read_at"] is not None


# ---- 清空 ----


def test_clear_all_only_own(ctx):
    _seed(ctx["conn"], "u1", "a1", "marketplace_pending", 1)
    _seed(ctx["conn"], "u2", "b1", "marketplace_pending", 2)

    resp = ctx["client"].delete("/notifications", headers=ctx["h1"])
    assert resp.status_code == 200 and resp.json() == {"ok": True}

    assert ctx["conn"].execute(
        "SELECT COUNT(*) AS c FROM notifications WHERE user_id = 'u1'"
    ).fetchone()["c"] == 0
    assert ctx["conn"].execute(
        "SELECT COUNT(*) AS c FROM notifications WHERE user_id = 'u2'"
    ).fetchone()["c"] == 1
    # 幂等：再删仍 200
    assert ctx["client"].delete("/notifications", headers=ctx["h1"]).status_code == 200


# ---- payload 兜底 ----


def test_payload_fallbacks(ctx):
    # 损坏 JSON → 全兜底
    _seed(ctx["conn"], "u1", "bad", "marketplace_pending", 1)
    ctx["conn"].execute(
        "UPDATE notifications SET payload = ? WHERE id = 'bad'", ("{broken",)
    )
    ctx["conn"].commit()
    # 数字 rejectReason 逐字上游 ?? 语义：非 nullish 原样保留
    _seed(
        ctx["conn"], "u1", "num", "marketplace_rejected", 2,
        payload={"itemId": "x", "itemType": "component", "name": "N",
                 "slug": "s", "rejectReason": 42},
    )

    items = ctx["client"].get("/notifications", headers=ctx["h1"]).json()["items"]
    by_id = {i["id"]: i for i in items}
    assert by_id["bad"]["payload"] == {
        "itemId": "", "itemType": "theme", "name": "", "slug": "", "rejectReason": None,
    }
    assert by_id["num"]["payload"]["itemType"] == "component"
    assert by_id["num"]["payload"]["rejectReason"] == 42
