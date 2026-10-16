"""TR-15.1 市场端点契约矩阵（upstream: apps/api/src/marketplace.ts + marketplace-db.ts）。

鉴权门 → 发布（校验/409/日限 5/30/管理员豁免）→ 可见性 → 管理员审批状态机 →
作者更新/删除 → install 原子计数 → 公开列表 q/sort/分页。
"""

import time

import pytest
from fastapi.testclient import TestClient

from doocs_md_py.server import db
from doocs_md_py.server.app import create_app
from doocs_md_py.server.config import Config
from doocs_md_py.server.security import issue_token

SECRET = "marketplace-secret-0123456789-abcdef-ghijkl"
DAY_MS = 24 * 60 * 60 * 1000


@pytest.fixture
def ctx(conn):
    db.upsert_user(conn, {
        "id": "u1", "github_id": 1, "login": "octocat",
        "name": "Octo Cat", "avatar": None,
    })
    db.upsert_user(conn, {
        "id": "u2", "github_id": 2, "login": "procat",
        "name": "Pro Cat", "avatar": None,
    })
    db.upsert_user(conn, {
        "id": "u3", "github_id": 3, "login": "adminroot",
        "name": "Admin Root", "avatar": None,
    })
    future_ms = (int(time.time()) + 365 * DAY_MS // 1000) * 1000
    conn.execute(
        "UPDATE users SET plan = 'pro', plan_expires_at = ? WHERE id = 'u2'",
        (future_ms,),
    )
    conn.commit()
    app = create_app(
        Config(jwt_secret=SECRET, admin_github_logins=("adminroot",)), conn=conn
    )
    client = TestClient(app)

    def headers(uid, login):
        return {"Authorization": f"Bearer {issue_token(SECRET, uid, login, now_s=2_000_000_000)}"}

    ctx_obj = {
        "client": client,
        "conn": conn,
        "h1": headers("u1", "octocat"),
        "h2": headers("u2", "procat"),
        "hadmin": headers("u3", "adminroot"),
        "ghost": headers("ghost", "ghost"),
        "headers": headers,
    }
    return ctx_obj


def theme_body(slug="my-theme", **over):
    body = {"slug": slug, "name": "My Theme", "css": "h1 { color: red; }"}
    body.update(over)
    return body


def component_body(slug="tip-block", **over):
    body = {
        "slug": slug,
        "name": "Tip",
        "component": {"name": "TipBlock", "template": "<section>{{x}}</section>", "props": []},
    }
    body.update(over)
    return body


def seed_item(conn, *, item_id="m1", item_type="theme", author="u1", slug=None,
              status="approved", version="1.0.0", download=0,
              created=1000, updated=2000, published=2000, reject_reason=None,
              name="Item Name", description="desc", sample=None, payload="h1{}"):
    if slug is None:
        slug = f"slug-{item_id}"
    conn.execute(
        """INSERT INTO marketplace_items (
             id, type, author_id, slug, name, description, version,
             cover_url, primary_color, sample_markdown, payload, status, reject_reason,
             download_count, created_at, updated_at, published_at
           ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (item_id, item_type, author, slug, name, description, version,
         sample, payload, status, reject_reason, download, created, updated,
         published if status == "approved" else None),
    )
    conn.commit()
    return item_id


# ---- 鉴权门（8 端点）----


@pytest.mark.parametrize("method,path", [
    ("GET", "/marketplace/me"),
    ("POST", "/marketplace/themes"),
    ("POST", "/marketplace/components"),
    ("PATCH", "/marketplace/item-id"),
    ("DELETE", "/marketplace/item-id"),
    ("GET", "/marketplace/admin/pending"),
    ("POST", "/marketplace/admin/item-id/approve"),
    ("POST", "/marketplace/admin/item-id/reject"),
])
def test_manage_endpoints_require_auth(ctx, method, path):
    resp = ctx["client"].request(method, path)
    assert resp.status_code == 401
    assert resp.json() == {"error": "unauthorized"}


def test_invalid_token_401(ctx):
    resp = ctx["client"].get("/marketplace/me", headers={"Authorization": "Bearer garbage"})
    assert resp.status_code == 401
    assert resp.json() == {"error": "invalid_token"}


# ---- 公开浏览 ----


def test_empty_catalog_shape(ctx):
    for path in ("/marketplace/themes", "/marketplace/components"):
        resp = ctx["client"].get(path)
        assert resp.status_code == 200
        assert resp.json() == {"items": [], "total": 0, "page": 1, "pageSize": 20}


def test_pagination_param_normalization(ctx):
    resp = ctx["client"].get("/marketplace/themes?page=0&pageSize=10000")
    assert resp.json()["page"] == 1
    assert resp.json()["pageSize"] == 50
    resp = ctx["client"].get("/marketplace/themes?page=abc&pageSize=0")
    assert resp.json()["page"] == 1
    assert resp.json()["pageSize"] == 20


def test_public_list_filters_and_orders(ctx):
    conn = ctx["conn"]
    # popular：a 下载多但 published 早；newest 顺序相反
    seed_item(conn, item_id="a", slug="alpha", name="Alpha Theme",
              download=5, published=1000, updated=1000)
    seed_item(conn, item_id="b", slug="beta", name="Beta Theme",
              download=0, published=2000, updated=2000)
    seed_item(conn, item_id="p1", item_type="component", slug="c1",
             status="pending", published=None, updated=3000)
    seed_item(conn, item_id="r1", slug="rejected", status="rejected",
             published=None, updated=4000, reject_reason="bad")

    popular = ctx["client"].get("/marketplace/themes?sort=popular").json()
    assert [i["id"] for i in popular["items"]] == ["a", "b"]
    assert popular["total"] == 2
    newest = ctx["client"].get("/marketplace/themes?sort=newest").json()
    assert [i["id"] for i in newest["items"]] == ["b", "a"]
    # 非 popular 值一律回退 newest
    default = ctx["client"].get("/marketplace/themes?sort=weird").json()
    assert [i["id"] for i in default["items"]] == ["b", "a"]

    found = ctx["client"].get("/marketplace/themes?q=alp").json()
    assert [i["id"] for i in found["items"]] == ["a"]
    assert found["total"] == 1
    # 公开 summary 不含 rejectReason
    assert "rejectReason" not in found["items"][0]
    assert ctx["client"].get("/marketplace/components").json()["total"] == 0


def test_public_detail_visibility(ctx):
    seed_item(ctx["conn"], item_id="pub1", status="approved", sample="# Sample")
    seed_item(ctx["conn"], item_id="pend1", status="pending")

    anon = ctx["client"].get("/marketplace/pub1")
    assert anon.status_code == 200
    detail = anon.json()
    assert detail["payload"] == "h1{}"
    assert detail["sampleMarkdown"] == "# Sample"
    assert "rejectReason" not in detail
    assert detail["author"]["login"] == "octocat"

    # 坏 token 等同匿名，不 401
    anon_bad_token = ctx["client"].get(
        "/marketplace/pub1", headers={"Authorization": "Bearer garbage"}
    )
    assert anon_bad_token.status_code == 200

    assert ctx["client"].get("/marketplace/pend1").status_code == 404
    assert ctx["client"].get("/marketplace/missing").status_code == 404
    # 其他普通用户看不到他人的待审条目
    assert ctx["client"].get("/marketplace/pend1", headers=ctx["h2"]).status_code == 404
    # 作者与管理员可见
    assert ctx["client"].get("/marketplace/pend1", headers=ctx["h1"]).status_code == 200
    admin_view = ctx["client"].get("/marketplace/pend1", headers=ctx["hadmin"])
    assert admin_view.status_code == 200
    assert admin_view.json()["rejectReason"] is None


# ---- 发布 ----


def test_publish_theme_success_shape(ctx):
    resp = ctx["client"].post(
        "/marketplace/themes", headers=ctx["h1"],
        json=theme_body(primaryColor="#0F4C81", version="9.9.9", sampleMarkdown="# Hi"),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "pending"
    assert body["version"] == "1.0.0"
    assert body["type"] == "theme"
    assert body["slug"] == "my-theme"
    assert body["primaryColor"] == "#0F4C81"
    assert body["sampleMarkdown"] == "# Hi"
    assert body["payload"] == "h1 { color: red; }"
    assert body["rejectReason"] is None
    assert body["publishedAt"] is None
    assert isinstance(body["createdAt"], int) and body["createdAt"] > 0
    assert body["author"]["id"] == "u1"
    assert body["downloadCount"] == 0


def test_publish_component_success(ctx):
    resp = ctx["client"].post(
        "/marketplace/components", headers=ctx["h1"], json=component_body()
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["type"] == "component"
    payload = __import__("json").loads(body["payload"])
    assert payload["name"] == "TipBlock"
    assert body["sampleMarkdown"] is None
    assert body["primaryColor"] is None


def test_publish_bad_json_and_validation(ctx):
    malformed = ctx["client"].post(
        "/marketplace/themes",
        headers={**ctx["h1"], "content-type": "application/json"},
        content="not-json",
    )
    assert malformed.status_code == 400
    assert malformed.json() == {"error": "invalid_body"}

    bad_slug = ctx["client"].post(
        "/marketplace/themes", headers=ctx["h1"], json=theme_body(slug="Bad Slug")
    )
    assert bad_slug.status_code == 400
    assert bad_slug.json() == {"error": "invalid_slug"}

    # ghost 是签名合法但用户不存在的令牌：/me 不加载用户，上游同样 200 空列表
    ghost_me = ctx["client"].get("/marketplace/me", headers=ctx["ghost"])
    assert ghost_me.status_code == 200 and ghost_me.json()["items"] == []
    # publish 加载用户 → 404
    ghost_pub = ctx["client"].post(
        "/marketplace/themes", headers=ctx["ghost"], json=theme_body()
    )
    assert ghost_pub.status_code == 404


def test_publish_slug_unique_per_type(ctx):
    first = ctx["client"].post("/marketplace/themes", headers=ctx["h1"], json=theme_body(slug="dup"))
    assert first.status_code == 201
    second = ctx["client"].post("/marketplace/themes", headers=ctx["h1"], json=theme_body(slug="dup"))
    assert second.status_code == 409
    assert second.json() == {"error": "slug_taken"}
    # 唯一键含 type：同 slug 的 component 允许
    other_type = ctx["client"].post(
        "/marketplace/components", headers=ctx["h1"], json=component_body(slug="dup")
    )
    assert other_type.status_code == 201


def test_free_publish_rate_limited_after_five(ctx):
    for i in range(5):
        ok = ctx["client"].post(
            "/marketplace/themes", headers=ctx["h1"], json=theme_body(slug=f"free-{i}")
        )
        assert ok.status_code == 201
    # 第 6 次：限流先于校验，坏 body 同样 429
    limited = ctx["client"].post(
        "/marketplace/themes", headers=ctx["h1"], json={"slug": "free-6"}
    )
    assert limited.status_code == 429
    body = limited.json()
    assert body["error"] == "rate_limited"
    assert body["limit"] == 5
    assert 1 <= body["retryAfterSec"] <= 24 * 60 * 60


def test_pro_and_admin_publish_limits(ctx):
    for i in range(6):
        assert ctx["client"].post(
            "/marketplace/themes", headers=ctx["h2"], json=theme_body(slug=f"pro-{i}")
        ).status_code == 201
    for i in range(6):
        assert ctx["client"].post(
            "/marketplace/themes", headers=ctx["hadmin"], json=theme_body(slug=f"adm-{i}")
        ).status_code == 201


# ---- 管理员队列与审批状态机 ----


def test_admin_pending_guard_and_list(ctx):
    assert ctx["client"].get("/marketplace/admin/pending", headers=ctx["h1"]).status_code == 403
    assert ctx["client"].get("/marketplace/admin/pending", headers=ctx["ghost"]).status_code == 404

    seed_item(ctx["conn"], item_id="t1", item_type="theme", status="pending",
              published=None, updated=1000)
    seed_item(ctx["conn"], item_id="c1", item_type="component", status="pending",
              published=None, updated=2000)
    seed_item(ctx["conn"], item_id="ap1", status="approved", updated=3000)

    resp = ctx["client"].get("/marketplace/admin/pending", headers=ctx["hadmin"])
    assert resp.status_code == 200
    assert [i["id"] for i in resp.json()["items"]] == ["t1", "c1"]  # updated_at ASC
    assert resp.json()["total"] == 2
    assert "payload" in resp.json()["items"][0]

    only_theme = ctx["client"].get(
        "/marketplace/admin/pending?type=theme", headers=ctx["hadmin"]
    ).json()
    assert [i["id"] for i in only_theme["items"]] == ["t1"]
    # type 非法值等同不过滤参数？上游 parseType 返回 null → undefined → 全量
    bad_type = ctx["client"].get(
        "/marketplace/admin/pending?type=nope", headers=ctx["hadmin"]
    ).json()
    assert bad_type["total"] == 2


def test_approve_flow(ctx):
    seed_item(ctx["conn"], item_id="t1", status="pending", published=None,
              reject_reason="fix css", updated=1000)

    # 非管理员 403
    assert ctx["client"].post(
        "/marketplace/admin/t1/approve", headers=ctx["h1"]
    ).status_code == 403

    resp = ctx["client"].post("/marketplace/admin/t1/approve", headers=ctx["hadmin"])
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "approved"
    assert body["rejectReason"] is None
    assert body["publishedAt"] == body["updatedAt"] and body["publishedAt"] > 1000

    assert ctx["client"].get("/marketplace/t1").status_code == 200
    # 仅 pending 可审批：重复审批 404
    assert ctx["client"].post(
        "/marketplace/admin/t1/approve", headers=ctx["hadmin"]
    ).status_code == 404
    assert ctx["client"].post(
        "/marketplace/admin/missing/approve", headers=ctx["hadmin"]
    ).status_code == 404


def test_reject_flow(ctx):
    seed_item(ctx["conn"], item_id="t1", status="pending", published=None, updated=1000)

    resp = ctx["client"].post(
        "/marketplace/admin/t1/reject", headers=ctx["hadmin"], json={"reason": "  bad css  "}
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "rejected"
    assert resp.json()["rejectReason"] == "bad css"

    # 公开不可见
    assert ctx["client"].get("/marketplace/t1").status_code == 404
    # 作者 /me 与详情可见驳回原因
    mine = ctx["client"].get("/marketplace/me", headers=ctx["h1"]).json()["items"]
    assert mine[0]["status"] == "rejected"
    assert mine[0]["rejectReason"] == "bad css"
    author_detail = ctx["client"].get("/marketplace/t1", headers=ctx["h1"]).json()
    assert author_detail["rejectReason"] == "bad css"
    # 重复驳回 404
    assert ctx["client"].post(
        "/marketplace/admin/t1/reject", headers=ctx["hadmin"]
    ).status_code == 404


# ---- 作者更新/删除 ----


def test_update_by_author(ctx):
    seed_item(ctx["conn"], item_id="t1", status="rejected", published=None,
              reject_reason="old reason", updated=1000)

    # 他人 403、不存在 404
    assert ctx["client"].patch(
        "/marketplace/t1", headers=ctx["h2"], json={"css": "p{}"}
    ).status_code == 403
    assert ctx["client"].patch(
        "/marketplace/missing", headers=ctx["h1"], json={"css": "p{}"}
    ).status_code == 404
    # 空更新 400；坏 CSS 400
    assert ctx["client"].patch("/marketplace/t1", headers=ctx["h1"], json={}).status_code == 400
    assert ctx["client"].patch(
        "/marketplace/t1", headers=ctx["h1"], json={"css": "  "}
    ).status_code == 400

    resp = ctx["client"].patch(
        "/marketplace/t1", headers=ctx["h1"],
        json={"css": "p { color: blue; }", "version": "9.9.9", "name": "New Name"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["version"] == "1.0.1"  # 服务端自增，客户端 9.9.9 被忽略
    assert body["name"] == "New Name"
    assert body["payload"] == "p { color: blue; }"
    assert body["status"] == "pending"
    assert body["rejectReason"] is None
    assert body["publishedAt"] is None


def test_update_component_payload(ctx):
    seed_item(ctx["conn"], item_id="c1", item_type="component", status="pending",
             published=None, updated=1000, payload='{"name":"Old"}')
    resp = ctx["client"].patch(
        "/marketplace/c1", headers=ctx["h1"],
        json={"component": {"name": "NewBlock", "template": "<p>n</p>", "props": []}},
    )
    assert resp.status_code == 200
    import json
    assert json.loads(resp.json()["payload"])["name"] == "NewBlock"


def test_delete_by_author(ctx):
    seed_item(ctx["conn"], item_id="t1", status="pending", published=None)
    # 他人删除：upstream 按 author 条件 DELETE，统一 404（而非 403）
    assert ctx["client"].delete(
        "/marketplace/t1", headers=ctx["h2"]
    ).status_code == 404
    assert ctx["client"].delete(
        "/marketplace/missing", headers=ctx["h1"]
    ).status_code == 404
    resp = ctx["client"].delete("/marketplace/t1", headers=ctx["h1"])
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    assert ctx["client"].get("/marketplace/t1", headers=ctx["h1"]).status_code == 404


# ---- install 计数 ----


def test_install_atomic_count(ctx):
    seed_item(ctx["conn"], item_id="pend", status="pending", published=None)
    assert ctx["client"].post("/marketplace/pend/install").status_code == 404

    seed_item(ctx["conn"], item_id="ok1", status="approved", download=3)
    first = ctx["client"].post("/marketplace/ok1/install")
    assert first.status_code == 200
    assert first.json()["downloadCount"] == 4
    assert "payload" in first.json()
    second = ctx["client"].post("/marketplace/ok1/install")
    assert second.json()["downloadCount"] == 5
    assert ctx["client"].post("/marketplace/missing/install").status_code == 404


# ---- /me 列表 ----


def test_my_items_all_statuses(ctx):
    seed_item(ctx["conn"], item_id="older", slug="older", status="approved", updated=1000)
    seed_item(ctx["conn"], item_id="newer", slug="newer", status="rejected",
             published=None, updated=2000, reject_reason="why")
    seed_item(ctx["conn"], item_id="other", slug="other", author="u2", status="pending",
             published=None, updated=3000)

    resp = ctx["client"].get("/marketplace/me", headers=ctx["h1"])
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert [i["id"] for i in items] == ["newer", "older"]  # updated_at DESC
    assert items[0]["rejectReason"] == "why"
