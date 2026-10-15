"""GitHub OAuth 路由与 /me（upstream: apps/api/src/auth.ts 1:1）。"""

import sqlite3
import uuid
from urllib.parse import urlencode, urlsplit, urlunsplit

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from .. import db
from ..config import Config
from ..deps import get_db, get_http_client
from ..httputil import ApiError
from ..github_oauth import (
    build_authorize_url,
    exchange_code_for_token,
    fetch_github_user,
)
from ..origin import default_origin, resolve_redirect
from ..plan import get_effective_plan
from ..security import issue_token, require_user

# upstream: auth.ts:12-13
STATE_COOKIE = "md_oauth_state"
REDIRECT_COOKIE = "md_oauth_redirect"

# upstream: index.ts:37 app.route('/auth', authRoutes)
router = APIRouter(prefix="/auth", tags=["auth"])
# upstream: index.ts:53-64：/me 属于挂在根的鉴权 api 子路由（api.get('/me')）
me_router = APIRouter(tags=["auth"])


def _callback_url(request: Request) -> str:
    """upstream: auth.ts:16-19 `${url.origin}/auth/github/callback`。"""
    url = request.url
    return f"{url.scheme}://{url.netloc}/auth/github/callback"


def _redirect_to_app(
    config: Config, saved_redirect: str | None, fragment: dict[str, str]
) -> RedirectResponse:
    """upstream: auth.ts:22-27 带 hash 载荷 302 回前端。"""
    target = resolve_redirect(config.app_url, saved_redirect) or default_origin(config.app_url)
    parts = urlsplit(target)
    location = urlunsplit(
        (parts.scheme, parts.netloc, parts.path, parts.query, urlencode(fragment))
    )
    return RedirectResponse(url=location, status_code=302)


# upstream: auth.ts:56-79
@router.get("/github", status_code=302)
def github_authorize(request: Request) -> RedirectResponse:
    config: Config = request.app.state.config
    state = str(uuid.uuid4())
    is_https = request.url.scheme == "https"

    # upstream: auth.ts:70 先校验回跳来源，再写入 cookie
    redirect = resolve_redirect(config.app_url, request.query_params.get("redirect"))

    authorize_url = build_authorize_url(
        config.github_client_id, _callback_url(request), state
    )
    response = RedirectResponse(url=authorize_url, status_code=302)

    cookie_kwargs = {
        "max_age": 600,
        "httponly": True,
        "secure": is_https,
        # Hono setCookie 逐字输出 SameSite=Lax
        "samesite": "Lax",
        "path": "/",
    }
    response.set_cookie(STATE_COOKIE, state, **cookie_kwargs)
    response.set_cookie(REDIRECT_COOKIE, redirect, **cookie_kwargs)
    return response


# upstream: auth.ts:82-144
@router.get("/github/callback", status_code=302)
def github_callback(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    client: httpx.Client = Depends(get_http_client),
) -> RedirectResponse:
    config: Config = request.app.state.config
    oauth_error = request.query_params.get("error")
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    saved_state = request.cookies.get(STATE_COOKIE)
    saved_redirect = request.cookies.get(REDIRECT_COOKIE)

    def finish(fragment: dict[str, str]) -> RedirectResponse:
        response = _redirect_to_app(config, saved_redirect, fragment)
        # upstream: auth.ts:88-89 无论成败先清两枚 state cookie
        response.delete_cookie(STATE_COOKIE, path="/")
        response.delete_cookie(REDIRECT_COOKIE, path="/")
        return response

    # upstream: auth.ts:92-93 取消/拒绝必须回到编辑器而非 JSON 错误页
    if oauth_error:
        return finish({"oauth_error": oauth_error})

    # upstream: auth.ts:95-96
    if not code or not state or state != saved_state:
        return finish({"oauth_error": "invalid_oauth_state"})

    access_token = exchange_code_for_token(
        client,
        client_id=config.github_client_id,
        client_secret=config.github_client_secret,
        code=code,
        redirect_uri=_callback_url(request),
    )
    # upstream: auth.ts:110-111
    if not access_token:
        return finish({"oauth_error": "oauth_exchange_failed"})

    ok, gh = fetch_github_user(client, access_token)
    # upstream: auth.ts:121-122
    if not ok:
        return finish({"oauth_error": "github_user_fetch_failed"})

    github_id = int(gh["id"])
    login = gh["login"]
    name = gh.get("name")
    avatar = gh.get("avatar_url")

    # upstream: auth.ts:126-138
    existing = conn.execute(
        "SELECT id FROM users WHERE github_id = ?", (github_id,)
    ).fetchone()
    user_id = existing["id"] if existing is not None else str(uuid.uuid4())
    db.upsert_user(
        conn,
        {
            "id": user_id,
            "github_id": github_id,
            "login": login,
            "name": name,
            "avatar": avatar,
        },
    )

    token = issue_token(config.jwt_secret, user_id, login)
    # upstream: auth.ts:143 token 放 URL fragment，不进服务端日志
    return finish({"account_token": token})


# upstream: auth.ts:146-160（挂载点 index.ts:55 → /me）
@me_router.get("/me")
def me(
    request: Request,
    user_id: str = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict:
    config: Config = request.app.state.config
    user = db.get_user_by_id(conn, user_id)
    if user is None:
        raise ApiError(404, "not_found")
    plan = get_effective_plan(user.plan, user.plan_expires_at)
    return {
        "id": user.id,
        "login": user.login,
        "name": user.name,
        "avatar": user.avatar,
        "plan": plan,
        "planExpiresAt": user.plan_expires_at,
        "isAdmin": config.is_admin_login(user.login),
    }
