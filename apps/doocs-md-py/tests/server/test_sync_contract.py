"""TR-11.1 同步端点契约矩阵（upstream: apps/api/src/sync.ts）。

覆盖：鉴权门、pull 游标/since 解析、push 往返/LWW/墓碑/设置、400/413/403/429
全部分支、Content-Length 预检、配额双计数（预置存量）、activate 占位、
响应 camelCase 形态。共 30+ 场景。
"""

import pytest
from fastapi.testclient import TestClient

from doocs_md_py.server import db
from doocs_md_py.server.app import create_app
from doocs_md_py.server.config import Config
from doocs_md_py.server.security import issue_token

JWT_SECRET = "sync-secret-0123456789-abcdef-ghijkl"


@pytest.fixture
def ctx(conn):
    db.upsert_user(
        conn,
        {"id": "u1", "github_id": 1, "login": "octocat", "name": None, "avatar": None},
    )
    db.upsert_user(
        conn,
        {"id": "u2", "github_id": 2, "login": "other", "name": None, "avatar": None},
    )
    app = create_app(Config(jwt_secret=JWT_SECRET), conn=conn)
    client = TestClient(app)
    token = issue_token(JWT_SECRET, "u1", "octocat", now_s=2_000_000_000)
    return {
        "client": client,
        "conn": conn,
        "h": {"Authorization": f"Bearer {token}"},
    }


def doc(doc_id="d1", **over):
    base = {
        "id": doc_id,
        "title": "T",
        "content": "# hi",
        "parentId": None,
        "history": [],
        "createDatetime": 1,
        "updateDatetime": over.pop("_update", 100),
        "deleted": False,
    }
    base.update(over)
    return base


def setting(key="theme", value="default", updated_at=10):
    return {"key": key, "value": value, "updatedAt": updated_at}


def seed_document(conn, user_id, doc_id, deleted=0, server_ts=1000, update_ts=100):
    conn.execute(
        """INSERT INTO documents
             (user_id, id, title, content, parent_id, history,
              create_datetime, update_datetime, deleted, server_updated_at)
           VALUES (?, ?, 'seed', '', NULL, '[]', 1, ?, ?, ?)""",
        (user_id, doc_id, update_ts, deleted, server_ts),
    )
    conn.commit()


# ---- 鉴权门（3）----


def test_pull_requires_auth(ctx):
    assert ctx["client"].get("/sync/pull").status_code == 401
    assert ctx["client"].get(
        "/sync/pull", headers={"Authorization": "Bearer junk"}
    ).status_code == 401


def test_push_requires_auth(ctx):
    assert ctx["client"].post("/sync/push", json={}).status_code == 401


def test_sync_unknown_user_404(ctx):
    ghost = issue_token(JWT_SECRET, "ghost", "ghost", now_s=2_000_000_000)
    resp = ctx["client"].get("/sync/pull", headers={"Authorization": f"Bearer {ghost}"})
    assert resp.status_code == 404
    assert resp.json() == {"error": "not_found"}


# ---- pull（5）----


def test_pull_empty_shape(ctx):
    resp = ctx["client"].get("/sync/pull", headers=ctx["h"])
    assert resp.status_code == 200
    assert resp.json() == {"documents": [], "settings": [], "cursor": 0}


def test_pull_since_parsing_variants(ctx):
    # since 非法/负数/0/缺省 → 从 0 起
    for raw in ("abc", "-5", "0"):
        resp = ctx["client"].get(
            "/sync/pull", params={"since": raw}, headers=ctx["h"]
        )
        assert resp.status_code == 200
        assert resp.json()["cursor"] == 0
    # 无 since 参数同样 200
    assert ctx["client"].get("/sync/pull", headers=ctx["h"]).json()["cursor"] == 0
    # 等价 JS parseInt("12abc",10)=12：空变更时 cursor 原样回显
    resp = ctx["client"].get(
        "/sync/pull", params={"since": "12abc"}, headers=ctx["h"]
    )
    assert resp.json()["cursor"] == 12
    assert resp.json()["documents"] == []


def test_pull_incremental_cursor(ctx, conn):
    seed_document(conn, "u1", "old", server_ts=100)
    seed_document(conn, "u1", "new", server_ts=200)
    # since=100：严格大于，只回 200
    resp = ctx["client"].get("/sync/pull", params={"since": 100}, headers=ctx["h"])
    body = resp.json()
    assert [d["id"] for d in body["documents"]] == ["new"]
    assert body["cursor"] == 200
    # since=200：空
    assert ctx["client"].get(
        "/sync/pull", params={"since": 200}, headers=ctx["h"]
    ).json()["documents"] == []


def test_pull_is_scoped_per_user(ctx, conn):
    seed_document(conn, "u1", "mine", server_ts=100)
    seed_document(conn, "u2", "theirs", server_ts=100)
    ids = [d["id"] for d in ctx["client"].get(
        "/sync/pull", headers=ctx["h"]).json()["documents"]]
    assert ids == ["mine"]


def test_pull_returns_camel_case_and_deleted(ctx, conn):
    seed_document(conn, "u1", "gone", deleted=1, server_ts=100)
    body = ctx["client"].get("/sync/pull", headers=ctx["h"]).json()
    item = body["documents"][0]
    assert item["id"] == "gone"
    assert item["deleted"] is True
    assert item["parentId"] is None
    assert "createDatetime" in item and "updateDatetime" in item


# ---- push 基本往返/LWW/墓碑（8）----


def test_push_empty_is_noop(ctx):
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"], json={"documents": [], "settings": []}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["documents"] == []
    assert body["settings"] == []
    assert isinstance(body["cursor"], int)


def test_push_defaults_missing_arrays(ctx):
    # 上游 body.documents ?? [] / settings ?? []
    assert ctx["client"].post("/sync/push", headers=ctx["h"], json={}).status_code == 200


def test_push_invalid_json_body(ctx):
    resp = ctx["client"].post(
        "/sync/push",
        headers={**ctx["h"], "Content-Type": "application/json"},
        content=b"{not json",
    )
    assert resp.status_code == 400
    assert resp.json() == {"error": "invalid_body"}


def test_push_document_roundtrip(ctx):
    payload = doc("d1", title="标题", content="# Hello",
                  history=[{"datetime": 1, "content": "v1"}])
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [payload], "settings": []},
    )
    assert resp.status_code == 200
    merged = resp.json()["documents"]
    assert len(merged) == 1
    assert merged[0]["title"] == "标题"
    assert merged[0]["history"][0]["content"] == "v1"


def test_push_setting_roundtrip_and_value_decode(ctx):
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [], "settings": [setting("k", "v", updated_at=50)]},
    )
    assert resp.json()["settings"][0] == {"key": "k", "value": "v", "updatedAt": 50}
    # pull 回拉一致
    pulled = ctx["client"].get("/sync/pull", headers=ctx["h"]).json()
    assert pulled["settings"][0]["value"] == "v"


def test_push_lww_rejects_stale_document(ctx):
    ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [doc("d1", content="newer", _update=200)], "settings": []},
    )
    # 旧 updateDatetime 被 LWW 拒绝：被拒行不在 push 响应内（上游 D1
    # ON CONFLICT...WHERE + RETURNING 语义），pull 回拉仍为服务端版本
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [doc("d1", content="older", _update=100)], "settings": []},
    )
    assert resp.status_code == 200
    assert resp.json()["documents"] == []
    pulled = {d["id"]: d for d in ctx["client"].get(
        "/sync/pull", headers=ctx["h"]).json()["documents"]}
    assert pulled["d1"]["content"] == "newer"


def test_push_lww_equal_timestamp_keeps_server(ctx):
    ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [doc("d1", content="first", _update=100)], "settings": []},
    )
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [doc("d1", content="second", _update=100)], "settings": []},
    )
    # existing.ts >= client → 跳过（上游 db.ts:188），无行回写
    assert resp.json()["documents"] == []
    pulled = {d["id"]: d for d in ctx["client"].get(
        "/sync/pull", headers=ctx["h"]).json()["documents"]}
    assert pulled["d1"]["content"] == "first"


def test_push_tombstone_strips_body(ctx, conn):
    ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [
            doc("d1", content="alive", title="T", _update=100),
        ], "settings": []},
    )
    ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [
            doc("d1", content="SHOULD-BE-STRIPPED", title="STRIPPED",
                history=[{"datetime": 1, "content": "x"}],
                deleted=True, _update=200),
        ], "settings": []},
    )
    row = conn.execute(
        "SELECT title, content, history, deleted FROM documents WHERE id = 'd1'"
    ).fetchone()
    assert row["deleted"] == 1
    assert row["title"] == ""
    assert row["content"] == ""
    assert row["history"] == "[]"


def test_push_resurrect_tombstone_is_new_active(ctx, conn):
    seed_document(conn, "u1", "d1", deleted=1, server_ts=10, update_ts=10)
    # 复活：deleted=false 推送，应成功且计入活跃
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [doc("d1", content="back", _update=20)], "settings": []},
    )
    assert resp.status_code == 200
    row = conn.execute(
        "SELECT deleted, content FROM documents WHERE id = 'd1'"
    ).fetchone()
    assert row["deleted"] == 0
    assert row["content"] == "back"


# ---- 400 结构类（4）----


def test_push_rejects_non_array_documents(ctx):
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"], json={"documents": {}, "settings": []}
    )
    assert resp.status_code == 400
    assert resp.json() == {"error": "invalid_body", "field": "documents"}


def test_push_rejects_malformed_document(ctx):
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [{"id": "x"}], "settings": []},
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "invalid_document"
    assert resp.json()["field"] == "documents.title"


def test_push_rejects_empty_id(ctx):
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [doc("")], "settings": []},
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "invalid_document_id"
    assert resp.json()["max"] == 128


def test_push_rejects_bad_setting(ctx):
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [], "settings": [setting(value=123)]},
    )
    assert resp.status_code == 400
    assert resp.json() == {"error": "invalid_setting", "field": "settings.value"}


# ---- 413 尺寸类（4）----


def test_push_too_many_documents_413(ctx):
    docs = [doc(f"d-{i}") for i in range(101)]
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"], json={"documents": docs, "settings": []}
    )
    assert resp.status_code == 413
    assert resp.json() == {"error": "too_many_documents", "field": "documents", "max": 100}


def test_push_content_too_large_413(ctx):
    big = "x" * (512 * 1024 + 1)
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [doc("big", content=big)], "settings": []},
    )
    assert resp.status_code == 413
    assert resp.json()["error"] == "content_too_large"
    assert resp.json()["max"] == 512 * 1024


def test_push_content_length_precheck_413(ctx):
    # 体极小但 Content-Length 谎报超限：预检先于 JSON 解析
    resp = ctx["client"].post(
        "/sync/push",
        headers={**ctx["h"], "Content-Length": str(9 * 1024 * 1024)},
        json={"documents": [], "settings": []},
    )
    assert resp.status_code == 413
    body = resp.json()
    assert body["error"] == "payload_too_large"
    assert body["max"] == 8 * 1024 * 1024


def test_push_row_cap_document_too_large_413(ctx):
    block = "x" * (512 * 1024)
    history = [{"datetime": i, "content": block} for i in range(4)]
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [doc("big", content=block, history=history)],
              "settings": []},
    )
    assert resp.status_code == 413
    assert resp.json()["error"] == "document_too_large"
    assert resp.json()["max"] == 1_800_000


# ---- 403 存量配额（4）----


def test_push_active_quota_free_403(ctx, conn):
    for i in range(200):
        seed_document(conn, "u1", f"cap-{i}", deleted=0, server_ts=i + 1)
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [doc("brand-new", _update=999)], "settings": []},
    )
    assert resp.status_code == 403
    body = resp.json()
    assert body == {"error": "document_quota_exceeded", "plan": "free",
                    "limit": 200, "upgradeRequired": True}


def test_push_row_quota_free_403(ctx, conn):
    # 400 行存量（含墓碑）；未知 id 新行（即使是墓碑）触发行配额
    for i in range(400):
        seed_document(conn, "u1", f"row-{i}", deleted=(i % 2), server_ts=i + 1)
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [doc("unknown-row", deleted=True, _update=999)],
              "settings": []},
    )
    assert resp.status_code == 403
    assert resp.json()["limit"] == 400


def test_push_updates_existing_allowed_at_cap(ctx, conn):
    for i in range(200):
        seed_document(conn, "u1", f"cap-{i}", server_ts=i + 1)
    # 更新已有行：newActive=0，不拦
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [doc("cap-0", content="u", _update=999_999)],
              "settings": []},
    )
    assert resp.status_code == 200


def test_push_settings_do_not_trigger_document_quota(ctx, conn):
    for i in range(200):
        seed_document(conn, "u1", f"cap-{i}", server_ts=i + 1)
    resp = ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [], "settings": [setting("k", "v")]},
    )
    assert resp.status_code == 200


# ---- 429 限流（2）----


def test_sync_rate_limit_429_body(ctx):
    client = ctx["client"]
    for _ in range(30):
        assert client.get("/sync/pull", headers=ctx["h"]).status_code == 200
    resp = client.get("/sync/pull", headers=ctx["h"])
    assert resp.status_code == 429
    body = resp.json()
    assert body["error"] == "rate_limit_exceeded"
    assert body["plan"] == "free"
    assert body["limit"] == 30
    assert body["upgradeRequired"] is True
    assert 1 <= body["retryAfterSec"] <= 3600


def test_sync_rate_limit_shared_by_pull_and_push(ctx):
    client = ctx["client"]
    for _ in range(29):
        client.get("/sync/pull", headers=ctx["h"])
    # 第 30 次给 push（仍在窗口内），通过；第 31 次 push 被拦
    assert client.post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [], "settings": []},
    ).status_code == 200
    resp = client.post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [], "settings": []},
    )
    assert resp.status_code == 429


# ---- activate 占位（1）----


def test_activate_503_placeholder(ctx):
    resp = ctx["client"].post(
        "/sync/activate", headers=ctx["h"], json={"orderNo": "x"}
    )
    assert resp.status_code == 503
    assert resp.json() == {"error": "afdian_not_configured"}


# ---- 配额不消耗于校验失败（1）----


def test_failed_validation_does_not_write_documents(ctx, conn):
    ctx["client"].post(
        "/sync/push", headers=ctx["h"],
        json={"documents": [{"id": "bad"}], "settings": []},
    )
    count = conn.execute("SELECT COUNT(*) AS c FROM documents").fetchone()["c"]
    assert count == 0
