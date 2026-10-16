"""TR-20.1 错误体字段一致性全表（cross-cutting，upstream: apps/api/src/*.ts）。

上游各 handler 统一以 ``c.json({error}, status)`` 返回错误；仅少量场景附带额外
字段（``maxBytes``/``limit``/``retryAfterSec``/``upgradeRequired``/``plan``/``period``/
``field``/``max``/``message``）。本文件把**可端到端触发**的错误位点汇总成一张全表，
逐条断言：① HTTP 状态码；② ``Content-Type`` 为 JSON；③ body 键集合与上游逐字一致
（多一个键、少一个键都算契约违约）。

完整 103 处错误位点清单、无法端到端触发的位点及其差异说明见
``apps/doocs-md-py/docs/contract-mapping.md``（TR-20.2）。
"""

import json

import httpx
import pytest
from fastapi.testclient import TestClient

from doocs_md_py.server.app import create_app
from doocs_md_py.server.config import Config
from doocs_md_py.server.emoji_validate import EMOJI_MAX_ITEMS
from doocs_md_py.server.httputil import ApiError, error_response
from doocs_md_py.server.plan import SYNC_RATE_LIMIT
from doocs_md_py.server.routers.marketplace import MARKETPLACE_PUBLISH_LIMIT
from doocs_md_py.server.routers.share import MAX_SNAPSHOT_BYTES
from doocs_md_py.server.security import issue_token
from doocs_md_py.server.sync_limits import SYNC_PUSH_LIMITS
from doocs_md_py.server.upload_config import UPLOAD_MAX_BYTES
from doocs_md_py.server.upload_rate import (
    increment_upload_rate_limit,
    upload_rate_limit_for_plan,
)

JWT_SECRET = "jwt-secret-0123456789-abcdef-ghijkl"

# 全仓错误体允许出现的键（超集白名单）；任何新键都必须先在此登记并核对上游。
ERROR_BODY_ALLOWED_KEYS = frozenset(
    {
        "error",
        "message",
        "max",
        "maxBytes",
        "limit",
        "plan",
        "period",
        "retryAfterSec",
        "upgradeRequired",
        "field",
        "ok",
        "error_description",
        "detail",
    }
)


def _client(conn, **overrides) -> TestClient:
    cfg = Config(**{"jwt_secret": JWT_SECRET, "upload_backend": "local", **overrides})
    return TestClient(create_app(cfg, conn=conn))


def _auth(user_id: str = "user-001", login: str = "octocat") -> dict[str, str]:
    return {"Authorization": f"Bearer {issue_token(JWT_SECRET, user_id, login)}"}


def _expect(resp, status: int, body: dict) -> None:
    """状态码 + JSON Content-Type + body 逐字相等。"""
    assert resp.status_code == status, (resp.status_code, resp.text)
    assert resp.headers["content-type"].startswith("application/json"), resp.headers
    assert resp.json() == body


def _expect_shape(resp, status: int, keys: set[str]) -> dict:
    """状态码 + JSON + 键集合逐字相等（值含时间派生量时用）。"""
    assert resp.status_code == status, (resp.status_code, resp.text)
    assert resp.headers["content-type"].startswith("application/json"), resp.headers
    payload = resp.json()
    assert set(payload) == keys, payload
    assert set(payload) <= ERROR_BODY_ALLOWED_KEYS, payload
    return payload


# ---- 白名单与构造器单元断言（httputil.error_response / ApiError）----


def test_error_response_single_key():
    resp = error_response(418, "teapot")
    assert json.loads(resp.body) == {"error": "teapot"}
    assert resp.status_code == 418


def test_error_response_extra_can_override_error_key():
    resp = error_response(400, "invalid_request", extra={"error": "invalid_request", "error_description": "bad"})
    assert json.loads(resp.body) == {"error": "invalid_request", "error_description": "bad"}


def test_api_error_carries_extra_and_headers():
    exc = ApiError(429, "rate_limited", extra={"limit": 5}, headers={"retry-after": "60"})
    assert (exc.status_code, exc.message, exc.extra, exc.headers) == (
        429,
        "rate_limited",
        {"limit": 5},
        {"retry-after": "60"},
    )


# ---- 鉴权（upstream: auth.ts:35-51 authMiddleware）----


def test_auth_unauthorized_and_invalid_token(conn):
    client = _client(conn)
    _expect(client.get("/me"), 401, {"error": "unauthorized"})
    _expect(
        client.get("/me", headers={"Authorization": "Bearer not-a-jwt"}),
        401,
        {"error": "invalid_token"},
    )


# ---- 同步（upstream: sync.ts 43-132）----


def test_sync_pull_ghost_user_not_found(conn):
    client = _client(conn)
    headers = {"Authorization": f"Bearer {issue_token(JWT_SECRET, 'ghost', 'ghost')}"}
    _expect(client.get("/sync/pull", headers=headers), 404, {"error": "not_found"})


def test_sync_push_invalid_body(conn, user_id):
    client = _client(conn)
    headers = _auth(user_id)
    _expect(client.post("/sync/push", headers=headers, content=b"{"), 400, {"error": "invalid_body"})
    _expect(client.post("/sync/push", headers=headers, content=b"[]"), 400, {"error": "invalid_body"})


def test_sync_push_payload_too_large(conn, user_id):
    client = _client(conn)
    oversized = b"x" * (SYNC_PUSH_LIMITS["maxRequestBytes"] + 1)
    _expect(
        client.post("/sync/push", headers=_auth(user_id), content=oversized),
        413,
        {"error": "payload_too_large", "max": SYNC_PUSH_LIMITS["maxRequestBytes"]},
    )


def test_sync_push_too_many_documents(conn, user_id):
    client = _client(conn)
    documents = [
        {"id": f"d-{i}", "title": "t", "content": "c", "updateDatetime": 1}
        for i in range(SYNC_PUSH_LIMITS["maxDocumentsPerPush"] + 1)
    ]
    _expect(
        client.post("/sync/push", headers=_auth(user_id), json={"documents": documents, "settings": []}),
        413,
        {
            "error": "too_many_documents",
            "field": "documents",
            "max": SYNC_PUSH_LIMITS["maxDocumentsPerPush"],
        },
    )


def test_sync_rate_limit_exceeded_shape(conn, user_id):
    client = _client(conn)
    headers = _auth(user_id)
    limit = SYNC_RATE_LIMIT["free"]
    for _ in range(limit):
        assert client.get("/sync/pull", headers=headers).status_code == 200
    payload = _expect_shape(
        client.get("/sync/pull", headers=headers),
        429,
        {"error", "plan", "limit", "retryAfterSec", "upgradeRequired"},
    )
    assert payload["error"] == "rate_limit_exceeded"
    assert payload["plan"] == "free"
    assert payload["limit"] == limit
    assert payload["upgradeRequired"] is True
    assert 1 <= payload["retryAfterSec"] <= 3600


# ---- 图片上传（upstream: upload.ts:77-122；分支顺序逐字对齐）----


def test_upload_disabled(conn):
    client = _client(conn, upload_enabled=False)
    _expect(client.post("/upload"), 404, {"error": "upload_disabled"})


def test_upload_not_configured(conn):
    client = _client(conn, upload_backend="github", upload_github_tokens=())
    _expect(client.post("/upload"), 503, {"error": "upload_not_configured"})


def test_upload_file_required_and_invalid_type(conn, tmp_path):
    client = _client(conn, storage_local_dir=str(tmp_path))
    _expect(client.post("/upload", files={}), 400, {"error": "file_required"})
    _expect(
        client.post("/upload", files={"file": ("a.txt", b"hello", "text/plain")}),
        400,
        {"error": "invalid_file_type"},
    )


def test_upload_file_too_large(conn, tmp_path):
    client = _client(conn, storage_local_dir=str(tmp_path))
    oversized = b"x" * (UPLOAD_MAX_BYTES + 1)
    _expect(
        client.post("/upload", files={"file": ("a.png", oversized, "image/png")}),
        400,
        {"error": "file_too_large", "maxBytes": UPLOAD_MAX_BYTES},
    )


def test_upload_rate_limit_exceeded_shape(conn, tmp_path):
    client = _client(conn, storage_local_dir=str(tmp_path))
    limit = upload_rate_limit_for_plan(None)
    # 匿名（无 cf-connecting-ip / x-forwarded-for 头）的 scope key 为 upload:ip:unknown
    for _ in range(limit):
        increment_upload_rate_limit(conn, "upload:ip:unknown")
    payload = _expect_shape(
        client.post("/upload", files={"file": ("a.png", b"png", "image/png")}),
        429,
        {"error", "limit", "retryAfterSec", "upgradeRequired"},
    )
    assert payload["error"] == "rate_limit_exceeded"
    assert payload["limit"] == limit
    # upstream upload.ts:67：plan === 'free' 才置 True，匿名（plan=null）为 False
    assert payload["upgradeRequired"] is False


def test_upload_backend_failure_is_502(conn, user_id):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"message": "boom"})

    cfg = Config(
        jwt_secret=JWT_SECRET,
        upload_backend="s3",
        upload_s3_bucket="bucket",
        upload_s3_access_key_id="ak",
        upload_s3_secret_access_key="sk",
        upload_s3_public_url="https://cdn.example.com",
    )
    app = create_app(cfg, conn=conn, http_client=httpx.Client(transport=httpx.MockTransport(handler)))
    resp = TestClient(app).post("/upload", files={"file": ("a.png", b"png", "image/png")})
    payload = _expect_shape(resp, 502, {"error", "message"})
    assert payload["error"] == "upload_failed"
    assert isinstance(payload["message"], str) and payload["message"]


# ---- 分享（upstream: share.ts）----


def test_share_list_requires_pro(conn, user_id):
    client = _client(conn)
    _expect(client.get("/share", headers=_auth(user_id)), 403, {"error": "pro_required"})


def test_share_create_validation_chain(conn, user_id):
    client = _client(conn)
    headers = _auth(user_id)
    _expect(client.post("/share", headers=headers, content=b"{"), 400, {"error": "invalid_json"})
    _expect(client.post("/share", headers=headers, json={}), 400, {"error": "post_id_required"})
    _expect(client.post("/share", headers=headers, json={"postId": "p1"}), 400, {"error": "html_snapshot_required"})


def test_share_snapshot_too_large(conn, user_id):
    client = _client(conn)
    blob = "x" * (MAX_SNAPSHOT_BYTES + 1)
    resp = client.post(
        "/share",
        headers=_auth(user_id),
        json={
            "postId": "p1",
            "htmlSnapshot": {"bodyHtml": blob, "stylesHtml": ""},
            "passwordMode": "none",
        },
    )
    _expect(resp, 413, {"error": "snapshot_too_large"})


# ---- 市场（upstream: marketplace.ts）----


def test_marketplace_publish_rate_limited_shape(conn, user_id):
    client = _client(conn)
    headers = _auth(user_id)
    limit = MARKETPLACE_PUBLISH_LIMIT["free"]
    for _ in range(limit):
        client.post("/marketplace/themes", headers=headers, json={})
    payload = _expect_shape(
        client.post("/marketplace/themes", headers=headers, json={}),
        429,
        {"error", "limit", "retryAfterSec"},
    )
    assert payload["error"] == "rate_limited"
    assert payload["limit"] == limit


@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_marketplace_unknown_item_not_found(conn, user_id, method):
    client = _client(conn)
    call = getattr(client, method)
    kwargs = {"headers": _auth(user_id)}
    if method == "patch":
        kwargs["json"] = {}
    _expect(call("/marketplace/nope", **kwargs), 404, {"error": "not_found"})


def test_marketplace_install_unknown_item_not_found(conn, user_id):
    client = _client(conn)
    _expect(
        client.post("/marketplace/nope/install", headers=_auth(user_id)),
        404,
        {"error": "not_found"},
    )


# ---- 表情（upstream: emojis.ts）----


def test_emojis_item_errors(conn, user_id):
    client = _client(conn)
    headers = _auth(user_id)
    _expect(client.post("/emojis/me/items", headers=headers), 400, {"error": "file_required"})
    _expect(
        client.delete("/emojis/me/items/nope", headers=headers), 404, {"error": "not_found"}
    )
    assert EMOJI_MAX_ITEMS == 100


# ---- 通知（upstream: notifications.ts）----


def test_notifications_read_unknown_not_found(conn, user_id):
    client = _client(conn)
    _expect(
        client.post("/notifications/nope/read", headers=_auth(user_id)),
        404,
        {"error": "not_found"},
    )


# ---- 框架级兜底：登记为契约差异（upstream Hono 无 notFound/onError 自定义）----


def test_framework_unknown_route_body_is_documented_difference(conn):
    """FastAPI 未命中路由返回 ``{"detail": "Not Found"}``。

    上游 Hono 未注册 ``notFound``/``onError``，未命中路径返回 ``404 Not Found``
    纯文本，因此两侧都不是 ``{"error": ...}``；Python 侧的 ``detail`` 键已登记在
    ``ERROR_BODY_ALLOWED_KEYS`` 白名单与 ``docs/contract-mapping.md`` 差异表中。
    """
    client = _client(conn)
    _expect(client.get("/definitely-not-a-route"), 404, {"detail": "Not Found"})
