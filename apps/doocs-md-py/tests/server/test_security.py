"""TR-10.1 JWT 工具与 Bearer 依赖（upstream: auth.ts / share-password.ts）。"""

from types import SimpleNamespace

import jwt
import pytest

from doocs_md_py.server.config import Config
from doocs_md_py.server.httputil import ApiError
from doocs_md_py.server.security import (
    SHARE_ACCESS_MAX_AGE_SEC,
    TOKEN_TTL_SECONDS,
    issue_share_access_token,
    issue_token,
    require_user,
    verify_share_access_token,
    verify_token,
)

SECRET = "unit-secret-0123456789-abcdef-ghijkl"
# 固定在 2033 年（晚于测试运行的真实时间），使 exp 校验确定
NOW = 2_000_000_000
# 用于构造已过期令牌的历史时刻
PAST = 1_000_000_000


def test_issue_and_verify_roundtrip():
    token = issue_token(SECRET, "user-1", "octocat", now_s=NOW)
    payload = verify_token(SECRET, token)
    assert payload == {"sub": "user-1", "login": "octocat", "exp": NOW + TOKEN_TTL_SECONDS}
    assert TOKEN_TTL_SECONDS == 30 * 24 * 60 * 60


def test_expired_token_rejected():
    token = issue_token(SECRET, "u", "l", now_s=PAST)
    with pytest.raises(jwt.ExpiredSignatureError):
        verify_token(SECRET, token)


def test_wrong_secret_rejected():
    token = issue_token(SECRET, "u", "l", now_s=NOW)
    with pytest.raises(jwt.InvalidTokenError):
        verify_token("another-secret-0123456789-abcdef", token)


def test_garbage_token_rejected():
    with pytest.raises(jwt.InvalidTokenError):
        verify_token(SECRET, "not.a.jwt")


def test_share_token_no_expiry_uses_24h_cap():
    token = issue_share_access_token(SECRET, "share-1", None, now_s=NOW)
    payload = verify_token(SECRET, token)
    assert payload["typ"] == "share_access"
    assert payload["sub"] == "share-1"
    assert payload["exp"] == NOW + SHARE_ACCESS_MAX_AGE_SEC
    assert verify_share_access_token(SECRET, "share-1", token) is True
    assert verify_share_access_token(SECRET, "share-other", token) is False


def test_share_token_far_expiry_clamped_to_24h():
    far_ms = (NOW + 10 * SHARE_ACCESS_MAX_AGE_SEC) * 1000
    token = issue_share_access_token(SECRET, "s", far_ms, now_s=NOW)
    assert verify_token(SECRET, token)["exp"] == NOW + SHARE_ACCESS_MAX_AGE_SEC


def test_share_token_near_expiry_uses_share_expiry():
    share_exp_ms = (NOW + 60) * 1000 + 999  # 秒级 floor
    token = issue_share_access_token(SECRET, "s", share_exp_ms, now_s=NOW)
    assert verify_token(SECRET, token)["exp"] == NOW + 60


def test_share_token_verify_failures():
    token = issue_share_access_token(SECRET, "s", None, now_s=NOW)
    assert verify_share_access_token(SECRET + "x", "s", token) is False
    expired = issue_share_access_token(SECRET, "s", None, now_s=PAST)
    assert verify_share_access_token(SECRET, "s", expired) is False
    # 账户令牌不是 share_access 类型
    account = issue_token(SECRET, "s", "l", now_s=NOW)
    assert verify_share_access_token(SECRET, "s", account) is False


def _fake_request(authorization=None):
    headers = {}
    if authorization is not None:
        headers["authorization"] = authorization
    state = SimpleNamespace(config=Config(jwt_secret=SECRET))
    return SimpleNamespace(headers=headers, app=SimpleNamespace(state=state))


def test_require_user_missing_header():
    with pytest.raises(ApiError) as exc:
        require_user(_fake_request())
    assert exc.value.status_code == 401
    assert exc.value.message == "unauthorized"


def test_require_user_bad_scheme_and_bad_token():
    with pytest.raises(ApiError) as exc_info:
        require_user(_fake_request("Basic abc"))
    assert exc_info.value.message == "unauthorized"

    with pytest.raises(ApiError) as exc_info:
        require_user(_fake_request("Bearer garbage"))
    assert exc_info.value.message == "invalid_token"


def test_require_user_empty_sub_invalid():
    # 手工构造 sub 为空串的合法签名 token
    token = jwt.encode({"sub": "", "exp": NOW + 10}, SECRET, algorithm="HS256")
    with pytest.raises(ApiError) as exc_info:
        require_user(_fake_request(f"Bearer {token}"))
    assert exc_info.value.message == "invalid_token"


def test_require_user_success():
    token = issue_token(SECRET, "user-9", "octocat", now_s=NOW)
    assert require_user(_fake_request(f"Bearer {token}")) == "user-9"
