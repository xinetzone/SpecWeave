"""TR-15.2 市场通知联动（upstream: marketplace.ts:121-156 + notifications-db.ts）。

收件人规则：
- 新提交/更新：全部已登录过的管理员（含管理员作者本人），未注册的管理员配置不收；
- 批准/驳回：仅作者；
- 通知失败不阻断主流程。
"""

import json

import pytest
from fastapi.testclient import TestClient

from doocs_md_py.server import db
from doocs_md_py.server.app import create_app
from doocs_md_py.server.config import Config
from doocs_md_py.server.routers import marketplace as marketplace_router
from doocs_md_py.server.security import issue_token

SECRET = "notify-secret-0123456789-abcdef-ghijklmn"


@pytest.fixture
def ctx(conn):
    db.upsert_user(conn, {
        "id": "u1", "github_id": 1, "login": "octocat",
        "name": "Octo", "avatar": None,
    })
    db.upsert_user(conn, {
        "id": "u3", "github_id": 3, "login": "adminroot",
        "name": "Admin Root", "avatar": None,
    })
    db.upsert_user(conn, {
        "id": "u4", "github_id": 4, "login": "admintwo",
        "name": "Admin Two", "avatar": None,
    })
    # ghostadmin 出现在配置但从未登录（users 表无记录）
    app = create_app(
        Config(
            jwt_secret=SECRET,
            admin_github_logins=("adminroot", "admintwo", "ghostadmin"),
        ),
        conn=conn,
    )
    client = TestClient(app)

    def headers(uid, login):
        return {"Authorization": f"Bearer {issue_token(SECRET, uid, login, now_s=2_000_000_000)}"}

    return {
        "client": client,
        "conn": conn,
        "h1": headers("u1", "octocat"),
        "hadmin": headers("u3", "adminroot"),
        "hadmin2": headers("u4", "admintwo"),
    }


def theme_body(slug, **over):
    body = {"slug": slug, "name": "My Theme", "css": "h1 { color: red; }"}
    body.update(over)
    return body


def list_notifications(conn):
    rows = conn.execute(
        "SELECT user_id, type, payload, created_at FROM notifications ORDER BY user_id"
    ).fetchall()
    return [(r["user_id"], r["type"], json.loads(r["payload"]), r["created_at"]) for r in rows]


def test_publish_notifies_all_registered_admins(ctx):
    resp = ctx["client"].post(
        "/marketplace/themes", headers=ctx["h1"], json=theme_body("note-1")
    )
    assert resp.status_code == 201
    item_id = resp.json()["id"]

    notes = list_notifications(ctx["conn"])
    recipients = {n[0] for n in notes}
    assert recipients == {"u3", "u4"}  # 作者 u1 不收；未注册 ghostadmin 不收
    for user_id, ntype, payload, created_at in notes:
        assert ntype == "marketplace_pending"
        assert payload == {
            "itemId": item_id,
            "itemType": "theme",
            "name": "My Theme",
            "slug": "note-1",
            "rejectReason": None,
        }
        assert created_at == resp.json()["createdAt"]


def test_admin_author_gets_self_notification(ctx):
    # upstream marketplace.ts:127 注释：管理员作者提交时通知其本人
    resp = ctx["client"].post(
        "/marketplace/themes", headers=ctx["hadmin"], json=theme_body("adm-self")
    )
    assert resp.status_code == 201
    recipients = {n[0] for n in list_notifications(ctx["conn"])}
    assert recipients == {"u3", "u4"}  # u3 自发也收到


def test_approve_notifies_author_only(ctx):
    published = ctx["client"].post(
        "/marketplace/themes", headers=ctx["h1"], json=theme_body("note-2")
    )
    item_id = published.json()["id"]
    ctx["conn"].execute("DELETE FROM notifications")
    ctx["conn"].commit()

    resp = ctx["client"].post(
        f"/marketplace/admin/{item_id}/approve", headers=ctx["hadmin2"]
    )
    assert resp.status_code == 200
    notes = list_notifications(ctx["conn"])
    assert len(notes) == 1
    user_id, ntype, payload, _ = notes[0]
    assert user_id == "u1"
    assert ntype == "marketplace_approved"
    assert payload["itemId"] == item_id
    assert payload["rejectReason"] is None


def test_reject_notifies_author_with_reason(ctx):
    published = ctx["client"].post(
        "/marketplace/themes", headers=ctx["h1"], json=theme_body("note-3")
    )
    item_id = published.json()["id"]
    ctx["conn"].execute("DELETE FROM notifications")
    ctx["conn"].commit()

    resp = ctx["client"].post(
        f"/marketplace/admin/{item_id}/reject",
        headers=ctx["hadmin"],
        json={"reason": "unsafe css"},
    )
    assert resp.status_code == 200
    notes = list_notifications(ctx["conn"])
    assert len(notes) == 1
    user_id, ntype, payload, _ = notes[0]
    assert (user_id, ntype) == ("u1", "marketplace_rejected")
    assert payload["rejectReason"] == "unsafe css"


def test_resubmit_notifies_admins_again(ctx):
    published = ctx["client"].post(
        "/marketplace/themes", headers=ctx["h1"], json=theme_body("note-4")
    )
    item_id = published.json()["id"]
    # 驳回后作者更新 → 重新进入 pending，再次通知管理员
    ctx["conn"].execute(
        "UPDATE marketplace_items SET status = 'rejected', reject_reason = 'x'",
    )
    ctx["conn"].commit()
    ctx["conn"].execute("DELETE FROM notifications")
    ctx["conn"].commit()

    resp = ctx["client"].patch(
        f"/marketplace/{item_id}", headers=ctx["h1"], json={"css": "p { color: red; }"}
    )
    assert resp.status_code == 200
    assert {n[0] for n in list_notifications(ctx["conn"])} == {"u3", "u4"}


def test_notification_failure_does_not_block_publish(ctx, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("notification storage down")

    # notify_users 在路由模块中以名字导入，patch 路由模块的引用
    monkeypatch.setattr(marketplace_router, "notify_users", boom)
    resp = ctx["client"].post(
        "/marketplace/themes", headers=ctx["h1"], json=theme_body("note-5")
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "pending"
