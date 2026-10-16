"""JWT（HS256）签发校验与 Bearer 鉴权依赖。

upstream:
- apps/api/src/auth.ts:14,29-51（账户令牌 TOKEN_TTL_SECONDS=30 天）
- apps/api/src/share-password.ts:9,133-161（share_access 令牌，最长 24 小时）

hono/jwt 与 PyJWT 均实现 RFC 7519 HS256（HMAC-SHA256 + base64url、exp 校验），
双向互认向量见 tests/golden/jwt_interop.json（scripts/jwt_interop_regen.py 生成）。
"""

import time

import jwt
from fastapi import Request

from .httputil import ApiError

# upstream: auth.ts:14
TOKEN_TTL_SECONDS = 60 * 60 * 24 * 30
# upstream: share-password.ts:9
SHARE_ACCESS_MAX_AGE_SEC = 60 * 60 * 24

ALGORITHM = "HS256"
_SHARE_ACCESS_TYP = "share_access"


def _now_sec(now_s: int | None) -> int:
    return int(time.time()) if now_s is None else now_s


# ---- 账户令牌（upstream: auth.ts:29-51）----


def issue_token(secret: str, sub: str, login: str, *, now_s: int | None = None) -> str:
    """upstream: auth.ts:29-32 issueToken，payload {sub, login, exp}。"""
    exp = _now_sec(now_s) + TOKEN_TTL_SECONDS
    return jwt.encode({"sub": sub, "login": login, "exp": exp}, secret, algorithm=ALGORITHM)


def verify_token(secret: str, token: str) -> dict:
    """upstream: auth.ts:42 verify；签名/过期非法时抛 jwt.PyJWTError 子类。"""
    return jwt.decode(token, secret, algorithms=[ALGORITHM])


# ---- 分享访问令牌（upstream: share-password.ts:133-161；T12 共用）----


def issue_share_access_token(
    secret: str,
    share_id: str,
    share_expires_at_ms: int | None,
    *,
    now_s: int | None = None,
) -> str:
    """upstream: share-password.ts:133-147 issueShareAccessToken。

    exp = min(分享到期秒, now+24h)；分享无到期时仅取 24 小时上限。
    """
    now = _now_sec(now_s)
    share_expiry_sec = (
        share_expires_at_ms // 1000
        if share_expires_at_ms is not None
        else now + SHARE_ACCESS_MAX_AGE_SEC
    )
    exp = min(share_expiry_sec, now + SHARE_ACCESS_MAX_AGE_SEC)
    return jwt.encode(
        {"sub": share_id, "typ": _SHARE_ACCESS_TYP, "exp": exp},
        secret,
        algorithm=ALGORITHM,
    )


def verify_share_access_token(secret: str, share_id: str, token: str) -> bool:
    """upstream: share-password.ts:149-161；任何异常或 typ/sub 不符均返回 False。"""
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return False
    return payload.get("typ") == _SHARE_ACCESS_TYP and payload.get("sub") == share_id


# ---- FastAPI 鉴权依赖（upstream: auth.ts:35-51 authMiddleware）----


def require_user(request: Request) -> str:
    """Bearer 令牌校验，通过返回内部 user id，否则 401（unauthorized/invalid_token）。"""
    header = request.headers.get("authorization") or ""
    token = header[7:] if header.startswith("Bearer ") else ""
    if not token:
        # upstream: auth.ts:38-39
        raise ApiError(401, "unauthorized")

    try:
        payload = verify_token(request.app.state.config.jwt_secret, token)
    except jwt.PyJWTError:
        # upstream: auth.ts:48-49
        raise ApiError(401, "invalid_token") from None

    sub = payload.get("sub")
    # upstream: auth.ts:43-44
    if not isinstance(sub, str) or not sub:
        raise ApiError(401, "invalid_token")
    return sub
