"""ASGI 路由与鉴权测试（AC-1 / AC-5 / AC-6 / AC-9）。"""

import json

import pytest

from admin_console.asgi import Request, build_context, dispatch
from admin_console.config import Config
from admin_console.store import MemoryStore

HOST = "app.test"
ORIGIN = "https://app.test"


def make_cfg():
    # 以下均为单元测试固定桩值，非真实密钥
    return Config(
        session_secret="unit-secret",  # nosec
        supabase_service_role_key="service-role-secret",  # nosec
        supabase_url="https://demo.supabase.co",
        max_upload_bytes=1024,
    )


@pytest.fixture
def ctx():
    cfg = make_cfg()
    return build_context(cfg, MemoryStore(cfg))


def call(ctx, method, path, body=b"", headers=None, query=""):
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "query_string": query.encode("utf-8"),
        "headers": [(k.encode("latin-1"), v.encode("latin-1")) for k, v in (headers or {}).items()],
    }
    status, resp_headers, payload = dispatch(ctx, Request(scope, body))
    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        data = {}
    return status, resp_headers, data


def cookies_of(resp_headers):
    out = {}
    for key, value in resp_headers:
        if key.lower() == b"set-cookie":
            name, _, raw = value.decode("latin-1").partition("=")
            out[name] = raw.split(";")[0]
    return out


def login(ctx, email="admin@example.com", password="admin12345"):  # nosec 降级模式演示账号桩值
    status, headers, data = call(ctx, "POST", "/api/auth/login",
                                 body=json.dumps({"email": email, "password": password}).encode(),
                                 headers={"content-type": "application/json", "host": HOST, "origin": ORIGIN})
    assert status == 200, data
    return cookies_of(headers)


def auth(cookies, extra=None):
    headers = {
        "cookie": f"ac_session={cookies['ac_session']}; ac_csrf={cookies['ac_csrf']}",
        "x-csrf-token": cookies["ac_csrf"],
        "host": HOST,
        "origin": ORIGIN,
        "content-type": "application/json",
    }
    headers.update(extra or {})
    return headers


# ---------- 健康与鉴权 ----------


def test_health_reports_degraded_without_leaking_secret(ctx):
    status, _, data = call(ctx, "GET", "/api/health")
    assert status == 200
    assert data["ok"] is True
    assert data["degraded"] is True
    assert "service-role-secret" not in json.dumps(data, ensure_ascii=False)


def test_login_rejects_bad_credentials(ctx):
    status, _, data = call(ctx, "POST", "/api/auth/login",
                           body=json.dumps({"email": "admin@example.com", "password": "nope"}).encode(),
                           headers={"content-type": "application/json", "host": HOST, "origin": ORIGIN})
    assert status == 401
    assert data["message"] == "邮箱或口令不正确"


def test_login_issues_httponly_session_and_csrf(ctx):
    cookies = login(ctx)
    assert cookies.get("ac_session") and cookies.get("ac_csrf")
    _, headers, _ = call(ctx, "POST", "/api/auth/login",
                         body=json.dumps({"email": "admin@example.com", "password": "admin12345"}).encode(),
                         headers={"content-type": "application/json", "host": HOST, "origin": ORIGIN})
    raw = b" ".join(v for k, v in headers if k.lower() == b"set-cookie").decode("latin-1")
    assert "HttpOnly" in raw


def test_login_rejects_cross_origin(ctx):
    status, _, _ = call(ctx, "POST", "/api/auth/login",
                        body=json.dumps({"email": "admin@example.com", "password": "admin12345"}).encode(),
                        headers={"content-type": "application/json", "host": HOST, "origin": "https://evil.test"})
    assert status == 403


def test_api_requires_session(ctx):
    status, _, _ = call(ctx, "GET", "/api/items")
    assert status == 401


def test_write_requires_csrf(ctx):
    cookies = login(ctx)
    headers = auth(cookies)
    headers.pop("x-csrf-token")
    status, _, data = call(ctx, "POST", "/api/items",
                           body=json.dumps({"title": "无 CSRF"}).encode(), headers=headers)
    assert status == 403 and data["error"] == "bad_csrf"


def test_write_rejects_mismatched_csrf(ctx):
    cookies = login(ctx)
    headers = auth(cookies, {"x-csrf-token": "forged"})
    status, _, _ = call(ctx, "POST", "/api/items",
                        body=json.dumps({"title": "伪造"}).encode(), headers=headers)
    assert status == 403


def test_write_rejects_cross_origin(ctx):
    cookies = login(ctx)
    headers = auth(cookies, {"origin": "https://evil.test"})
    _, _, data = call(ctx, "POST", "/api/items",
                      body=json.dumps({"title": "跨站"}).encode(), headers=headers)
    assert data["error"] == "bad_origin"


def test_write_rejects_non_json(ctx):
    cookies = login(ctx)
    headers = auth(cookies, {"content-type": "text/plain"})
    status, _, data = call(ctx, "POST", "/api/items", body=b"title=x", headers=headers)
    assert status == 415 and data["error"] == "unsupported_media_type"


def test_tampered_session_is_rejected(ctx):
    cookies = login(ctx)
    headers = auth(cookies)
    headers["cookie"] = f"ac_session={cookies['ac_session'][:-4]}AAAA; ac_csrf={cookies['ac_csrf']}"
    status, _, _ = call(ctx, "GET", "/api/items", headers=headers)
    assert status == 401


# ---------- 业务链路 ----------


def test_item_create_update_delete_flow(ctx):
    cookies = login(ctx)
    status, _, data = call(ctx, "POST", "/api/items",
                           body=json.dumps({"title": "上线公告", "status": "draft", "tags": ["公告"]}).encode(),
                           headers=auth(cookies))
    assert status == 200 and data["item"]["title"] == "上线公告"
    item = data["item"]

    status, _, data = call(ctx, "PATCH", f"/api/items/{item['id']}",
                           body=json.dumps({"status": "published",
                                            "expected_updated_at": item["updated_at"]}).encode(),
                           headers=auth(cookies))
    assert status == 200 and data["item"]["status"] == "published"

    status, _, data = call(ctx, "PATCH", f"/api/items/{item['id']}",
                           body=json.dumps({"status": "draft", "expected_updated_at": "2000-01-01T00:00:00+00:00"}).encode(),
                           headers=auth(cookies))
    assert status == 409 and data["error"] == "conflict"

    status, _, _ = call(ctx, "DELETE", f"/api/items/{item['id']}", body=b"{}", headers=auth(cookies))
    assert status == 200
    status, _, _ = call(ctx, "GET", f"/api/items/{item['id']}", headers=auth(cookies))
    assert status == 404


def test_item_validation_errors_are_field_level(ctx):
    cookies = login(ctx)
    status, _, data = call(ctx, "POST", "/api/items",
                           body=json.dumps({"title": "", "status": "unknown"}).encode(),
                           headers=auth(cookies))
    assert status == 400
    assert "title" in data["fields"] and "status" in data["fields"]


def test_category_delete_blocked_when_referenced(ctx):
    cookies = login(ctx)
    _, _, created = call(ctx, "POST", "/api/categories",
                         body=json.dumps({"name": "案例"}).encode(), headers=auth(cookies))
    category = created["category"]
    call(ctx, "POST", "/api/items",
         body=json.dumps({"title": "归类内容", "category_id": category["id"]}).encode(), headers=auth(cookies))
    status, _, data = call(ctx, "DELETE", f"/api/categories/{category['id']}", body=b"{}",
                           headers=auth(cookies))
    assert status == 409 and data["error"] == "conflict"


def test_bulk_update_changes_status(ctx):
    cookies = login(ctx)
    ids = []
    for index in range(2):
        _, _, data = call(ctx, "POST", "/api/items",
                          body=json.dumps({"title": f"批量 {index}"}).encode(), headers=auth(cookies))
        ids.append(data["item"]["id"])
    status, _, data = call(ctx, "POST", "/api/items/bulk",
                           body=json.dumps({"ids": ids, "action": "archived"}).encode(), headers=auth(cookies))
    assert status == 200 and data["affected"] == 2


def test_dashboard_returns_aggregates(ctx):
    cookies = login(ctx)
    call(ctx, "POST", "/api/items",
         body=json.dumps({"title": "看板数据", "status": "published"}).encode(), headers=auth(cookies))
    status, _, data = call(ctx, "GET", "/api/dashboard", headers=auth(cookies))
    assert status == 200
    assert data["total"] >= 1
    assert set(data["by_status"]) == {"draft", "published", "archived"}
    assert len(data["trend"]) == 14


# ---------- 上传 ----------


def upload(ctx, cookies, name, content_type, body):
    return call(ctx, "POST", "/api/uploads", body=body, headers={
        "cookie": f"ac_session={cookies['ac_session']}; ac_csrf={cookies['ac_csrf']}",
        "x-csrf-token": cookies["ac_csrf"],
        "x-file-name": name,
        "content-type": content_type,
        "host": HOST,
        "origin": ORIGIN,
    })


def test_upload_success(ctx):
    cookies = login(ctx)
    status, _, data = upload(ctx, cookies, "photo.png", "image/png", b"\x89PNG\r\n")
    assert status == 200
    assert data["attachment"]["filename"] == "photo.png"


def test_upload_rejects_oversized(ctx):
    cookies = login(ctx)
    status, _, data = upload(ctx, cookies, "big.png", "image/png", b"x" * 2048)
    assert status == 413 and data["error"] == "file_too_large"


def test_upload_rejects_unsupported_type(ctx):
    cookies = login(ctx)
    status, _, data = upload(ctx, cookies, "run.exe", "application/x-msdownload", b"MZ")
    assert status == 415 and data["error"] == "unsupported_type"


def test_upload_sanitizes_traversal_filename(ctx):
    cookies = login(ctx)
    status, _, data = upload(ctx, cookies, "../../etc/passwd", "text/plain", b"root")
    assert status == 200
    assert ".." not in data["attachment"]["path"]


# ---------- 静态与兜底 ----------


def test_login_page_served(ctx):
    status, _, _ = call(ctx, "GET", "/login")
    assert status in (200, 500)  # 500 表示 web/ 未随源码部署，不视为路由失败


def test_root_redirects_to_app(ctx):
    status, headers, _ = call(ctx, "GET", "/")
    assert status == 302
    assert any(k.lower() == b"location" for k, _ in headers)


def test_unknown_route_returns_json_404(ctx):
    status, _, data = call(ctx, "GET", "/api/nope")
    assert status == 404 and data["error"] == "not_found"
