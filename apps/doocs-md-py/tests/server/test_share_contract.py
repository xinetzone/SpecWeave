"""TR-12.1 分享端点契约矩阵（upstream: apps/api/src/share.ts）。

鉴权门/pro 门 → 创建（校验/限流/套餐/净化/幂等/派生 id/标题截断）→
公开页（404/410 文本、密码门、页脚计数、CSP、作者）→ unlock（双形态、
20/h/IP、cookie 属性、错误透传）。
"""

import hashlib
import time

import pytest
from fastapi.testclient import TestClient

from doocs_md_py.server import db, share_db
from doocs_md_py.server.app import create_app
from doocs_md_py.server.config import Config
from doocs_md_py.server.security import issue_token
from doocs_md_py.server.share_page import build_share_page_html
from doocs_md_py.server.share_sanitize import SHARE_PAGE_CSP

JWT_SECRET = "share-secret-0123456789-abcdef-ghijkl"
DAY_MS = 24 * 60 * 60 * 1000
SNAPSHOT = {"bodyHtml": "<p>你好</p>", "stylesHtml": "<style>a{color:red}</style>"}


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
    future_ms = (int(time.time()) + 365 * DAY_MS // 1000) * 1000
    conn.execute(
        "UPDATE users SET plan = 'pro', plan_expires_at = ? WHERE id = 'u2'",
        (future_ms,),
    )
    conn.commit()
    app = create_app(Config(jwt_secret=JWT_SECRET), conn=conn)
    client = TestClient(app)
    h1 = {"Authorization": f"Bearer {issue_token(JWT_SECRET, 'u1', 'octocat', now_s=2_000_000_000)}"}
    h2 = {"Authorization": f"Bearer {issue_token(JWT_SECRET, 'u2', 'procat', now_s=2_000_000_000)}"}
    return {"client": client, "conn": conn, "h1": h1, "h2": h2, "pro_h": h2, "free_h": h1}


def create(client, headers, **over):
    body = {"postId": "p1", "htmlSnapshot": SNAPSHOT}
    body.update(over)
    return client.post("/share", headers=headers, json=body)


def seed_share(conn, share_id, *, user_id="u1", password_hash=None,
               expires_at=None, title="T", html=None, created_at=None):
    if html is None:
        html = build_share_page_html(title, "<p>x</p>", "")
    share_db.insert_share(
        conn,
        share_id=share_id, post_id=f"post-{share_id}", user_id=user_id,
        title=title, html=html, password_hash=password_hash,
        created_at=created_at or 1_000,
        expires_at=expires_at,
    )
    return share_id


# ---- 鉴权（3）----


def test_manage_endpoints_require_auth(ctx):
    client = ctx["client"]
    assert client.get("/share").status_code == 401
    assert client.post("/share", json={}).status_code == 401
    assert client.delete("/share/aaaaaaaaaaaa").status_code == 401
    assert client.get("/share").json() == {"error": "unauthorized"}


def test_unknown_user_404(ctx):
    ghost = {"Authorization": f"Bearer {issue_token(JWT_SECRET, 'ghost', 'g', now_s=2_000_000_000)}"}
    assert ctx["client"].get("/share", headers=ghost).status_code == 404


def test_free_user_blocked_from_manage(ctx):
    assert ctx["client"].get("/share", headers=ctx["free_h"]).status_code == 403
    assert ctx["client"].get("/share", headers=ctx["free_h"]).json() == {
        "error": "pro_required"
    }
    assert ctx["client"].delete(
        "/share/aaaaaaaaaaaa", headers=ctx["free_h"]
    ).status_code == 403


# ---- pro 列表/删除（4）----


def test_pro_list_empty_and_shape(ctx):
    resp = ctx["client"].get("/share", headers=ctx["pro_h"])
    assert resp.status_code == 200
    assert resp.json() == {"shares": []}


def test_pro_list_items_and_expired_flag(ctx):
    now = int(time.time() * 1000)
    seed_share(ctx["conn"], "a" * 12, user_id="u2", expires_at=now - 1000)
    seed_share(ctx["conn"], "b" * 12, user_id="u2", expires_at=now + DAY_MS,
               password_hash="pbkdf2:1:x:x", title="活的")
    resp = ctx["client"].get("/share", headers=ctx["pro_h"])
    items = {s["id"]: s for s in resp.json()["shares"]}
    # created_at DESC：b 后插入（同 created_at=1000 时顺序不定，逐项断言）
    assert items["a" * 12]["expired"] is True
    assert items["a" * 12]["protected"] is False
    live = items["b" * 12]
    assert live["expired"] is False
    assert live["protected"] is True
    assert live["url"] == f"http://testserver/s/{'b' * 12}"
    assert live["postId"] == f"post-{'b' * 12}"
    assert live["title"] == "活的"
    assert live["viewCount"] == 0
    assert live["expiresAt"] == now + DAY_MS
    assert isinstance(live["createdAt"], int)


def test_pro_delete_lifecycle(ctx):
    client = ctx["client"]
    sid = seed_share(ctx["conn"], "c" * 12, user_id="u2")
    # 非法 id
    assert client.delete("/share/zzz", headers=ctx["pro_h"]).status_code == 400
    # 他人的（不存在于自己命名空间）
    other = seed_share(ctx["conn"], "d" * 12, user_id="u1")
    resp = client.delete(f"/share/{other}", headers=ctx["pro_h"])
    assert resp.status_code == 404
    # 成功
    assert client.delete(f"/share/{sid}", headers=ctx["pro_h"]).json() == {"ok": True}
    assert client.delete(f"/share/{sid}", headers=ctx["pro_h"]).status_code == 404


def test_pro_list_scoped_per_user(ctx):
    seed_share(ctx["conn"], "e" * 12, user_id="u1")
    items = ctx["client"].get("/share", headers=ctx["pro_h"]).json()["shares"]
    assert items == []


# ---- 创建校验（7）----


def test_create_invalid_json(ctx):
    resp = ctx["client"].post(
        "/share", headers={**ctx["free_h"], "Content-Type": "application/json"},
        content=b"{bad",
    )
    assert resp.status_code == 400
    assert resp.json() == {"error": "invalid_json"}


def test_create_post_id_required(ctx):
    assert create(ctx["client"], ctx["free_h"], postId="  ").status_code == 400
    assert create(ctx["client"], ctx["free_h"], postId=None).status_code == 400
    long_id = create(ctx["client"], ctx["free_h"], postId="x" * 65)
    assert long_id.status_code == 400
    assert long_id.json() == {"error": "post_id_required"}


def test_create_html_snapshot_required(ctx):
    assert create(ctx["client"], ctx["free_h"], htmlSnapshot=None).status_code == 400
    assert create(
        ctx["client"], ctx["free_h"],
        htmlSnapshot={"bodyHtml": "  ", "stylesHtml": ""},
    ).status_code == 400
    assert create(
        ctx["client"], ctx["free_h"],
        htmlSnapshot={"bodyHtml": 1, "stylesHtml": ""},
    ).status_code == 400
    assert create(
        ctx["client"], ctx["free_h"],
        htmlSnapshot={"bodyHtml": "<p>x</p>", "stylesHtml": 0},
    ).status_code == 400


def test_create_snapshot_too_large(ctx):
    big = "x" * (2 * 1024 * 1024 + 1)
    resp = create(ctx["client"], ctx["free_h"], htmlSnapshot={
        "bodyHtml": big, "stylesHtml": "",
    })
    assert resp.status_code == 413
    assert resp.json() == {"error": "snapshot_too_large"}


def test_create_custom_password_invalid(ctx):
    # 4–64
    resp = create(
        ctx["client"], ctx["free_h"], postId="pw1",
        passwordMode="custom", password="abc",
    )
    assert resp.status_code == 400
    assert resp.json() == {"error": "invalid_password"}
    # 非字符串
    resp = create(
        ctx["client"], ctx["free_h"], postId="pw1",
        passwordMode="custom", password=1234,
    )
    assert resp.status_code == 400


def test_create_free_success_shape_and_id_derivation(ctx):
    before = int(time.time() * 1000)
    resp = create(ctx["client"], ctx["free_h"], postId="my-post")
    after = int(time.time() * 1000)
    assert resp.status_code == 200
    body = resp.json()
    expected_id = hashlib.sha256(b"u1:my-post").hexdigest()[:12]
    assert body["id"] == expected_id
    assert body["url"] == f"http://testserver/s/{expected_id}"
    assert body["updated"] is False
    assert body["protected"] is False
    assert "password" not in body
    # free 强制 1d
    assert before + DAY_MS - 1000 <= body["expiresAt"] <= after + DAY_MS + 1000


def test_create_free_forced_one_day_ignores_mode(ctx):
    resp = create(
        ctx["client"], ctx["free_h"], postId="p-30d", expiresMode="30d"
    )
    expires = resp.json()["expiresAt"]
    now = int(time.time() * 1000)
    assert abs(expires - (now + DAY_MS)) < 5000
    # 非法 mode 兜底 1d（pro 同样兜底）
    resp2 = create(
        ctx["client"], ctx["pro_h"], postId="p-bad", expiresMode="nonsense"
    )
    assert abs(resp2.json()["expiresAt"] - (now + DAY_MS)) < 5000


# ---- 限流与套餐（3）----


def test_create_free_rate_limit_two_per_day(ctx):
    first = create(ctx["client"], ctx["free_h"], postId="a1")
    second = create(ctx["client"], ctx["free_h"], postId="a2")
    third = create(ctx["client"], ctx["free_h"], postId="a3")
    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    body = third.json()
    assert body == {
        "error": "rate_limited",
        "plan": "free",
        "period": "day",
        "limit": 2,
        "retryAfterSec": body["retryAfterSec"],
    }
    assert 1 <= body["retryAfterSec"] <= 86_400


def test_create_pro_unlimited_and_expiry_modes(ctx):
    client = ctx["client"]
    for i in range(5):
        assert create(client, ctx["pro_h"], postId=f"m{i}").status_code == 200
    never = create(client, ctx["pro_h"], postId="m-never", expiresMode="never")
    assert never.json()["expiresAt"] is None
    week = create(client, ctx["pro_h"], postId="m-7d", expiresMode="7d")
    now = int(time.time() * 1000)
    assert abs(week.json()["expiresAt"] - (now + 7 * DAY_MS)) < 5000


def test_create_update_reuses_id_and_consumes_quota(ctx):
    first = create(ctx["client"], ctx["free_h"], postId="dup", title="v1")
    second = create(
        ctx["client"], ctx["free_h"], postId="dup",
        title="v2", passwordMode="custom", password="abcd1234",
    )
    assert first.json()["id"] == second.json()["id"]
    assert second.json()["updated"] is True
    assert second.json()["protected"] is True
    # 更新同样消耗日配额（上游 consume 在 upsert 之后无条件执行）
    third = create(ctx["client"], ctx["free_h"], postId="other")
    assert third.status_code == 429


# ---- 密码模式（2）----


def test_create_auto_password_returned_once(ctx):
    resp = create(
        ctx["client"], ctx["pro_h"], postId="auto1", passwordMode="auto"
    )
    body = resp.json()
    assert body["protected"] is True
    assert len(body["password"]) == 8
    assert all(c.isalnum() for c in body["password"])
    # 存库 hash 非明文
    row = ctx["conn"].execute(
        "SELECT password_hash FROM shares WHERE id = ?", (body["id"],)
    ).fetchone()
    assert row["password_hash"].startswith("pbkdf2:100000:")
    assert body["password"] not in row["password_hash"]
    # 门可以用明文密码解开
    sid = body["id"]
    assert ctx["client"].get(f"/s/{sid}").status_code == 200  # gate
    unlocked = ctx["client"].post(
        f"/s/{sid}/unlock", json={"password": body["password"]}
    )
    assert unlocked.status_code == 200
    assert unlocked.json() == {"ok": True, "url": f"/s/{sid}"}


def test_create_title_trim_and_truncate(ctx):
    long_title = "  " + "字" * 250 + "  "
    resp = create(ctx["client"], ctx["pro_h"], postId="tt", title=long_title)
    row = ctx["conn"].execute(
        "SELECT title FROM shares WHERE id = ?", (resp.json()["id"],)
    ).fetchone()
    assert row["title"] == "字" * 200
    # 非字符串 title → 空串
    resp2 = create(ctx["client"], ctx["pro_h"], postId="tt2", title=123)
    assert resp2.status_code == 200


# ---- 净化（1）----


def test_create_sanitizes_snapshot(ctx):
    resp = create(
        ctx["client"], ctx["pro_h"], postId="evil",
        htmlSnapshot={
            "bodyHtml": '<p>ok</p><script>alert(1)</script>'
                        '<img src=x onerror=alert(1)>',
            "stylesHtml": "<style></style><iframe src='jav\tascript:x'></iframe>",
        },
    )
    row = ctx["conn"].execute(
        "SELECT html FROM shares WHERE id = ?", (resp.json()["id"],)
    ).fetchone()
    assert "<script>" not in row["html"].lower()
    assert "onerror" not in row["html"].lower()
    assert "<iframe" not in row["html"].lower()
    assert "<p>ok</p>" in row["html"]


# ---- 公开页：404/410（3）----


def test_public_malformed_id_404_text(ctx):
    client = ctx["client"]
    for method, path in (("GET", "/s/not-an-id"), ("POST", "/s/not-an-id/unlock")):
        resp = client.request(method, path)
        assert resp.status_code == 404
        assert resp.text == "Not Found"
        assert resp.headers["content-type"].startswith("text/plain")


def test_public_wellformed_missing_404(ctx):
    resp = ctx["client"].get("/s/aaaaaaaaaaaa")
    assert resp.status_code == 404
    assert resp.text == "Not Found"


def test_public_expired_410_text(ctx):
    past = int(time.time() * 1000) - 1000
    sid = seed_share(ctx["conn"], "1" * 12, expires_at=past)
    resp = ctx["client"].get(f"/s/{sid}")
    assert resp.status_code == 410
    assert resp.text == "This share link has expired."
    # unlock 同样 410
    assert ctx["client"].post(f"/s/{sid}/unlock", json={"password": "x"}).status_code == 410


# ---- 公开页：正文与计数（3）----


def test_public_view_renders_footer_and_increments(ctx):
    sid = seed_share(ctx["conn"], "2" * 12)
    resp = ctx["client"].get(f"/s/{sid}")
    assert resp.status_code == 200
    assert resp.headers["content-security-policy"] == SHARE_PAGE_CSP
    assert "由 Octo Cat 分享" in resp.text
    assert "阅读 1 次" in resp.text
    ctx["client"].get(f"/s/{sid}")
    third = ctx["client"].get(f"/s/{sid}")
    assert "阅读 3 次" in third.text


def test_public_view_unknown_author(ctx):
    sid = seed_share(ctx["conn"], "3" * 12, user_id="ghost-user")
    resp = ctx["client"].get(f"/s/{sid}")
    assert "由 未知用户 分享" in resp.text


def test_public_view_csp_on_gate_too(ctx):
    from doocs_md_py.server.share_password import hash_share_password

    sid = seed_share(ctx["conn"], "4" * 12, password_hash=hash_share_password("abcd1234"))
    resp = ctx["client"].get(f"/s/{sid}")
    assert resp.status_code == 200
    assert resp.headers["content-security-policy"] == SHARE_PAGE_CSP
    assert 'action="/s/' in resp.text


# ---- 密码门与 unlock（8）----


def test_gate_blocks_content_without_cookie(ctx):
    from doocs_md_py.server.share_password import hash_share_password

    sid = seed_share(
        ctx["conn"], "5" * 12,
        html=build_share_page_html("机密", "<p>SECRET-BODY</p>", ""),
        password_hash=hash_share_password("abcd1234"),
    )
    resp = ctx["client"].get(f"/s/{sid}")
    assert "SECRET-BODY" not in resp.text
    assert "此分享链接已设置访问密码" in resp.text


def test_gate_error_query_passthrough(ctx):
    from doocs_md_py.server.share_password import hash_share_password

    sid = seed_share(ctx["conn"], "6" * 12, password_hash=hash_share_password("abcd1234"))
    invalid = ctx["client"].get(f"/s/{sid}", params={"error": "invalid"})
    assert "密码错误，请重试。" in invalid.text
    limited = ctx["client"].get(f"/s/{sid}", params={"error": "rate_limited"})
    assert "尝试次数过多，请稍后再试。" in limited.text
    other = ctx["client"].get(f"/s/{sid}", params={"error": "weird"})
    assert 'class="error"' not in other.text


def test_unlock_no_password_redirects(ctx):
    sid = seed_share(ctx["conn"], "7" * 12)
    resp = ctx["client"].post(
        f"/s/{sid}/unlock", data={"password": "x"}, follow_redirects=False
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == f"/s/{sid}"
    assert "set-cookie" not in resp.headers


def test_unlock_wrong_password_form_and_json(ctx):
    from doocs_md_py.server.share_password import hash_share_password

    sid = seed_share(ctx["conn"], "8" * 12, password_hash=hash_share_password("abcd1234"))
    # 表单：303 回门带 error=invalid
    resp = ctx["client"].post(
        f"/s/{sid}/unlock", data={"password": "wrong"}, follow_redirects=False
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == f"/s/{sid}?error=invalid"
    # JSON：401
    resp = ctx["client"].post(f"/s/{sid}/unlock", json={"password": "wrong"})
    assert resp.status_code == 401
    assert resp.json() == {"error": "invalid_password"}


def test_unlock_empty_password_counts_as_failure(ctx):
    from doocs_md_py.server.share_password import hash_share_password

    sid = seed_share(ctx["conn"], "9" * 12, password_hash=hash_share_password("abcd1234"))
    resp = ctx["client"].post(f"/s/{sid}/unlock", json={})
    assert resp.status_code == 401
    resp = ctx["client"].post(f"/s/{sid}/unlock", json={"password": 123})
    assert resp.status_code == 401


def test_unlock_success_form_sets_cookie_and_unlocks(ctx):
    from doocs_md_py.server.share_password import (
        hash_share_password,
        share_access_cookie_name,
        share_access_cookie_path,
    )

    sid = seed_share(ctx["conn"], "a0" * 6, password_hash=hash_share_password("abcd1234"))
    resp = ctx["client"].post(
        f"/s/{sid}/unlock", data={"password": "abcd1234"}, follow_redirects=False
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == f"/s/{sid}"
    cookie = resp.headers["set-cookie"]
    name = share_access_cookie_name(sid)
    assert cookie.startswith(f"{name}=eyJ")  # JWT header base64
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie
    assert f"Path={share_access_cookie_path(sid)}" in cookie.replace(" ", "")
    assert "Secure" not in cookie  # http 测试环境
    # Max-Age 夹在 [60, 86400]
    import re
    max_age = int(re.search(r"Max-Age=(\d+)", cookie).group(1))
    assert 60 <= max_age <= 86_400
    # TestClient 自动带 cookie 回该 path → 见正文
    view = ctx["client"].get(f"/s/{sid}")
    assert "此分享链接已设置访问密码" not in view.text
    assert "<p>x</p>" in view.text


def test_unlock_success_json_has_no_cookie(ctx):
    from doocs_md_py.server.share_password import hash_share_password

    sid = seed_share(ctx["conn"], "b0" * 6, password_hash=hash_share_password("abcd1234"))
    resp = ctx["client"].post(f"/s/{sid}/unlock", json={"password": "abcd1234"})
    assert resp.status_code == 200
    assert "set-cookie" not in resp.headers
    # JSON 客户端需自行带 token；此处仍见门
    assert "此分享链接已设置访问密码" in ctx["client"].get(f"/s/{sid}").text


def test_unlock_rate_limit_20_per_hour_per_ip(ctx):
    from doocs_md_py.server.share_password import hash_share_password

    sid = seed_share(ctx["conn"], "c0" * 6, password_hash=hash_share_password("abcd1234"))
    client = ctx["client"]
    for _ in range(20):
        assert client.post(
            f"/s/{sid}/unlock", json={"password": "wrong"}
        ).status_code == 401
    # 第 21 次：JSON 429
    resp = client.post(f"/s/{sid}/unlock", json={"password": "wrong"})
    assert resp.status_code == 429
    assert resp.json()["error"] == "rate_limited"
    assert 1 <= resp.json()["retryAfterSec"] <= 3600
    # 表单：303 rate_limited
    resp = client.post(
        f"/s/{sid}/unlock", data={"password": "x"}, follow_redirects=False
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == f"/s/{sid}?error=rate_limited"
    # 即使密码正确也被拦
    resp = client.post(f"/s/{sid}/unlock", json={"password": "abcd1234"})
    assert resp.status_code == 429


def test_unlock_rate_limit_isolated_per_ip(ctx):
    from doocs_md_py.server.share_password import hash_share_password

    sid = seed_share(ctx["conn"], "d0" * 6, password_hash=hash_share_password("abcd1234"))
    client = ctx["client"]
    for _ in range(20):
        client.post(
            f"/s/{sid}/unlock",
            json={"password": "wrong"},
            headers={"X-Forwarded-For": "1.1.1.1"},
        )
    # 同 share 不同 IP：独立计数，密码正确直接成功
    resp = client.post(
        f"/s/{sid}/unlock",
        json={"password": "abcd1234"},
        headers={"X-Forwarded-For": "2.2.2.2"},
    )
    assert resp.status_code == 200
    # CF-Connecting-IP 优先于 XFF
    resp = client.post(
        f"/s/{sid}/unlock",
        json={"password": "abcd1234"},
        headers={"CF-Connecting-IP": "3.3.3.3", "X-Forwarded-For": "1.1.1.1"},
    )
    assert resp.status_code == 200


# ---- 篡改 cookie（1）----


def test_tampered_cookie_shows_gate(ctx):
    from doocs_md_py.server.share_password import hash_share_password

    sid = seed_share(ctx["conn"], "e0" * 6, password_hash=hash_share_password("abcd1234"))
    client = ctx["client"]
    client.cookies.set(f"md_share_{sid}", "garbage.token.here")
    resp = client.get(f"/s/{sid}")
    assert "此分享链接已设置访问密码" in resp.text
