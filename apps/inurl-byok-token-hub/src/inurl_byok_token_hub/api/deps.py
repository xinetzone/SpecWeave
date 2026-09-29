"""鉴权依赖：统一令牌提取与角色校验。

鉴权语义（源文档 F-085 / F-099）：
- 用户类接口未授权 → **401**，裸 JSON ``{"error": "unauthorized"}``；
- 管理员类接口越权 → **403**，裸 JSON ``{"error": "forbidden"}``；
- 未匹配路由 → **401**。
"""

from fastapi import Request

from ..errors import AuthError, ErrorCode
from ..models import Role, User


def extract_token(request: Request) -> str | None:
    """从 ``Authorization: Bearer`` 或 ``X-API-Key`` 中提取令牌。"""
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    api_key = request.headers.get("x-api-key")
    if api_key:
        return api_key.strip()
    return None


def hub_of(request: Request):
    return request.app.state.hub


def current_user(request: Request) -> User:
    token = extract_token(request)
    user = hub_of(request).tokens.verify(token)
    if user is None:
        raise AuthError(ErrorCode.UNAUTHORIZED)
    return user


def require_admin(request: Request) -> User:
    user = current_user(request)
    if user.role is not Role.ADMIN:
        raise AuthError(ErrorCode.FORBIDDEN)
    return user


def require_turnstile(request: Request) -> None:
    """人机校验（默认关闭，与原产品 ``enabled:false`` 一致）。"""
    if not hub_of(request).settings.turnstile_enabled:
        return
    if not request.headers.get("x-turnstile-token"):
        raise AuthError(ErrorCode.TURNSTILE_REQUIRED)
