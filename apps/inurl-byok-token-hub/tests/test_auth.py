"""AC-1：统一令牌与鉴权语义逐字成立。

鉴权口径（源文档 F-085 / F-099）：
- 用户类接口未授权 → 401 裸 JSON ``{"error": "unauthorized"}``；
- 管理员类接口越权 → 403 裸 JSON ``{"error": "forbidden"}``；
- 未匹配路由 → 401；
- ``/api/ads``、``/api/news``、``/api/catalog``、``/api/billing/plans``、
  ``/api/turnstile`` 无鉴权公开。
"""

import pytest

from inurl_byok_token_hub.crypto import digest
from inurl_byok_token_hub.errors import AuthError, ErrorCode
from inurl_byok_token_hub.models import TOKEN_PREFIX

PUBLIC_ENDPOINTS = (
    "/api/ads",
    "/api/news",
    "/api/catalog",
    "/api/billing/plans",
    "/api/turnstile",
)


def test_token_prefix_and_digest_only(hub, registered):
    result, _master = registered
    assert result.token.startswith(TOKEN_PREFIX)
    records = hub.store.tokens.all()
    assert records, "应至少签发一条令牌记录"
    assert all(r.digest == digest(result.token) for r in records if r.user_id == result.user.id)
    dumped = hub.store.raw_text()
    assert result.token not in dumped, "明文令牌不得落盘"
    assert result.recovery_secret not in dumped, "明文恢复密语不得落盘"


def test_no_token_is_401_bare_json(client):
    resp = client.get("/v1/models")
    assert resp.status_code == 401
    assert resp.json() == {"error": "unauthorized"}


def test_invalid_token_is_401_bare_json(client):
    resp = client.get("/v1/models", headers={"Authorization": "Bearer byok_live_invalid"})
    assert resp.status_code == 401
    assert resp.json() == {"error": "unauthorized"}


def test_non_admin_is_403_bare_json(client, registered):
    result, _master = registered
    resp = client.get(
        "/api/admin/modules", headers={"Authorization": f"Bearer {result.token}"}
    )
    assert resp.status_code == 403
    assert resp.json() == {"error": "forbidden"}


def test_unmatched_route_is_401(client):
    for path in ("/api/definitely-not-exist", "/nope", "/v1/unknown/route"):
        resp = client.get(path)
        assert resp.status_code == 401, path
        assert resp.json() == {"error": "unauthorized"}


def test_public_endpoints_need_no_token(client):
    for path in PUBLIC_ENDPOINTS:
        resp = client.get(path)
        assert resp.status_code == 200, path


def test_admin_can_access_backend(client, hub):
    token = hub.admin_token()
    assert token is not None and token.startswith(TOKEN_PREFIX)
    resp = client.get("/api/admin/modules", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 8, "后台应为八模块"


def test_rotated_token_grace_then_401(client, hub, registered):
    result, _master = registered
    old = result.token
    new = hub.tokens.rotate(result.user.id, grace_seconds=60)
    assert new != old
    # 宽限期内旧令牌仍可用
    assert client.get("/v1/models", headers={"Authorization": f"Bearer {old}"}).status_code == 200
    # 宽限期外（0 秒）立刻失效
    newer = hub.tokens.rotate(result.user.id, grace_seconds=0)
    assert newer != new
    assert client.get("/v1/models", headers={"Authorization": f"Bearer {new}"}).status_code == 401


def test_revoked_token_is_401(client, hub, registered):
    result, _master = registered
    record = hub.store.tokens.find(lambda r: r.user_id == result.user.id)
    hub.tokens.revoke(record.id)
    resp = client.get("/v1/models", headers={"Authorization": f"Bearer {result.token}"})
    assert resp.status_code == 401


def test_login_roundtrip_and_bad_password(hub, registered):
    result, _master = registered
    again = hub.tokens.login("user@local", "user-password")
    assert again.startswith(TOKEN_PREFIX)
    assert hub.tokens.verify(again) is not None
    with pytest.raises(AuthError):
        hub.tokens.login("user@local", "wrong-password")


def test_require_user_and_require_admin(hub, registered):
    result, _master = registered
    assert hub.tokens.require_user(result.token).id == result.user.id
    with pytest.raises(AuthError) as none_exc:
        hub.tokens.require_user(None)
    assert none_exc.value.error_code is ErrorCode.UNAUTHORIZED
    with pytest.raises(AuthError) as admin_exc:
        hub.tokens.require_admin(result.token)
    assert admin_exc.value.error_code is ErrorCode.FORBIDDEN
    admin_token = hub.admin_token()
    assert hub.tokens.require_admin(admin_token).role.value == "admin"


def test_x_api_key_header_is_accepted(client, registered):
    """:class:`deps.extract_token` 的 ``X-API-Key`` 分支（Anthropic 客户端常用）。"""
    result, _master = registered
    resp = client.get("/v1/models", headers={"X-API-Key": result.token})
    assert resp.status_code == 200


def test_password_change_and_recovery_roundtrip(hub, registered):
    result, _master = registered
    hub.tokens.change_password(result.user.id, "user-password", "another-password")
    with pytest.raises(AuthError):
        hub.tokens.login("user@local", "user-password")
    assert hub.tokens.login("user@local", "another-password") is not None
    user = hub.tokens.verify_recovery(result.recovery_secret)
    assert user is not None and user.id == result.user.id
    hub.tokens.reset_password_with_recovery(result.recovery_secret, "third-password")
    assert hub.tokens.login("user@local", "third-password") is not None
    assert hub.tokens.verify_recovery("not-a-real-recovery-secret") is None
