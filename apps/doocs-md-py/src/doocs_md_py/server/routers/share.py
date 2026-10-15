"""/share 管理端点（鉴权 + pro 门）与 /s/:id 公开页（upstream: share.ts 1:1）。

- POST /share：日窗创建限流（free 2/pro 无限）、free 强制 1d、pro 四档、
  2MiB 净化后快照、同 (user,postId) 复用链接、auto 密码仅在创建响应明文返回一次；
- GET /s/:id：404/410 纯文本、密码门、授权后注入作者与阅读数、CSP 头；
- POST /s/:id/unlock：20 次/小时/IP，JSON 与表单双形态，303 回跳或 JSON。
"""

import hashlib
import re
import sqlite3
import time

from fastapi import APIRouter, Depends, Request
from starlette.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
)

from .. import db
from ..deps import get_db
from ..httputil import ApiError
from ..plan import get_effective_plan
from ..ratelimit import (
    consume_share_create_rate_limit,
    peek_share_create_rate_limit,
    sync_retry_after_sec,
)
from ..security import (
    issue_share_access_token,
    require_user,
    verify_share_access_token,
)
from .. import share_db
from ..share_gate_page import build_share_gate_html
from ..share_page import (
    ShareFooterAuthor,
    build_share_page_html,
    inject_share_footer,
)
from ..share_password import (
    generate_share_password,
    hash_share_password,
    parse_custom_password,
    parse_share_password_mode,
    share_access_cookie_name,
    share_access_cookie_path,
    verify_share_password,
)
from ..share_sanitize import (
    SHARE_PAGE_CSP,
    sanitize_html_snapshot,
    sanitize_styles_snapshot,
)

router = APIRouter(tags=["share"])

# upstream: share.ts:39-48
MAX_SNAPSHOT_BYTES = 2 * 1024 * 1024
MAX_POST_ID_LENGTH = 64
SHARE_EXPIRE_MS = 24 * 60 * 60 * 1000
SHARE_EXPIRE_MS_BY_MODE = {
    "1d": SHARE_EXPIRE_MS,
    "7d": 7 * SHARE_EXPIRE_MS,
    "30d": 30 * SHARE_EXPIRE_MS,
    "never": None,
}
UNLOCK_ATTEMPT_LIMIT = 20
MAX_TITLE_LENGTH = 200

_SHARE_ID_RE = re.compile(r"^[a-f0-9]{12}$", re.IGNORECASE)
_VALID_EXPIRES_MODES = ("1d", "7d", "30d", "never")


def _now_ms() -> int:
    return int(time.time() * 1000)


# upstream: share.ts:50-59
async def _derive_share_id(user_id: str, post_id: str) -> str:
    digest = hashlib.sha256(f"{user_id}:{post_id}".encode("utf-8")).hexdigest()
    return digest[:12]


# upstream: share.ts:61-65
def _get_client_ip(request: Request) -> str:
    cf = request.headers.get("cf-connecting-ip")
    if cf:
        return cf
    xff = request.headers.get("x-forwarded-for")
    if xff:
        first = xff.split(",")[0].strip()
        if first:
            return first
    return "unknown"


# upstream: share.ts:67-81
def _parse_html_snapshot(raw) -> dict | None:
    if not isinstance(raw, dict):
        return None
    body = raw.get("bodyHtml")
    styles = raw.get("stylesHtml")
    if not isinstance(body, str) or not isinstance(styles, str):
        return None
    if not body.strip():
        return None
    return {
        "bodyHtml": sanitize_html_snapshot(body),
        "stylesHtml": sanitize_styles_snapshot(styles),
    }


# upstream: share.ts:83-90
def _parse_post_id(value) -> str | None:
    if not isinstance(value, str):
        return None
    post_id = value.strip()
    if not post_id or len(post_id) > MAX_POST_ID_LENGTH:
        return None
    return post_id


# upstream: share.ts:92-107
def _resolve_share_expires_at(expires_mode, plan: str, now: int) -> int | None:
    requested = expires_mode if expires_mode in _VALID_EXPIRES_MODES else "1d"
    mode = requested if plan == "pro" else "1d"
    delta = SHARE_EXPIRE_MS_BY_MODE[mode]
    return None if delta is None else now + delta


def _build_share_url(request: Request, share_id: str) -> str:
    # upstream: share.ts:109-112 new URL(req.url).origin
    return f"{str(request.base_url).rstrip('/')}/s/{share_id}"


def _is_https(request: Request) -> bool:
    # upstream: share.ts:114-116
    return request.url.scheme == "https"


def _share_html_response(html: str, status: int = 200) -> HTMLResponse:
    # upstream: share.ts:118-122
    return HTMLResponse(
        html, status_code=status, headers={"Content-Security-Policy": SHARE_PAGE_CSP}
    )


def _wants_json_response(request: Request) -> bool:
    # upstream: share.ts:124-127
    accept = request.headers.get("accept") or ""
    content_type = request.headers.get("content-type") or ""
    return "application/json" in accept or "application/json" in content_type


# upstream: share.ts:129-149
def _resolve_share_password(body: dict) -> dict:
    mode = parse_share_password_mode(body.get("passwordMode")) or "none"

    if mode == "none":
        return {"ok": True, "passwordHash": None}

    if mode == "auto":
        generated = generate_share_password()
        return {
            "ok": True,
            "passwordHash": hash_share_password(generated),
            "generatedPassword": generated,
        }

    plain = parse_custom_password(body.get("password"))
    if not plain:
        return {"ok": False, "error": "invalid_password"}
    return {"ok": True, "passwordHash": hash_share_password(plain)}


def _has_share_access(request: Request, share_id: str) -> bool:
    # upstream: share.ts:151-159
    token = request.cookies.get(share_access_cookie_name(share_id))
    if not token:
        return False
    secret = request.app.state.config.jwt_secret
    return verify_share_access_token(secret, share_id, token)


# upstream: share.ts:161-182
def _set_share_access_cookie(
    response: Response,
    request: Request,
    share_id: str,
    token: str,
    share_expires_at: int | None,
) -> None:
    now_s = int(time.time())
    if share_expires_at is not None:
        share_expiry_sec = share_expires_at // 1000
    else:
        share_expiry_sec = now_s + 60 * 60 * 24
    max_age = max(60, min(60 * 60 * 24, share_expiry_sec - now_s))

    response.set_cookie(
        share_access_cookie_name(share_id),
        token,
        max_age=max_age,
        path=share_access_cookie_path(share_id),
        httponly=True,
        secure=_is_https(request),
        # Hono 逐字输出 SameSite=Lax（大小写不影响浏览器，但保 cookie 字面一致）
        samesite="Lax",
    )


# upstream: share.ts:184-204
async def _parse_unlock_password(request: Request) -> str:
    content_type = request.headers.get("content-type") or ""
    if "application/json" in content_type:
        try:
            body = await request.json()
        except Exception:
            return ""
        password = body.get("password") if isinstance(body, dict) else None
        return password if isinstance(password, str) else ""

    try:
        form = await request.form()
    except Exception:
        return ""
    password = form.get("password")
    return password if isinstance(password, str) else ""


def _resolve_share_author(
    conn: sqlite3.Connection, user_id: str
) -> ShareFooterAuthor:
    # upstream: share.ts:363-371
    user = db.get_user_by_id(conn, user_id)
    if user is None:
        return ShareFooterAuthor("未知用户")
    name = user.name.strip() if user.name else ""
    return ShareFooterAuthor(name or user.login)


def _require_pro_for_share_manage(
    conn: sqlite3.Connection, user_id: str
) -> None:
    # upstream: share.ts:210-222
    user = db.get_user_by_id(conn, user_id)
    if user is None:
        raise ApiError(404, "not_found")
    if get_effective_plan(user.plan, user.plan_expires_at) != "pro":
        raise ApiError(403, "pro_required")


# ---- 管理端点（鉴权 + pro 门）----


# upstream: share.ts:224-246
@router.get("/share")
async def list_shares(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
) -> dict:
    request.state.user_id = user_id
    _require_pro_for_share_manage(conn, user_id)

    now = _now_ms()
    items = []
    for row in share_db.list_shares_by_user_id(conn, user_id):
        items.append(
            {
                "id": row.id,
                "postId": row.post_id,
                "title": row.title,
                "url": _build_share_url(request, row.id),
                "createdAt": row.created_at,
                "expiresAt": row.expires_at,
                "viewCount": row.view_count,
                "protected": row.password_hash is not None,
                "expired": row.expires_at is not None and row.expires_at <= now,
            }
        )
    return {"shares": items}


# upstream: share.ts:248-263
@router.delete("/share/{share_id}")
async def delete_share(
    share_id: str,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
) -> dict:
    request.state.user_id = user_id
    _require_pro_for_share_manage(conn, user_id)

    if not _SHARE_ID_RE.match(share_id):
        raise ApiError(400, "invalid_id")

    if not share_db.delete_share_by_user_and_id(conn, user_id, share_id):
        raise ApiError(404, "not_found")
    return {"ok": True}


# upstream: share.ts:265-361
@router.post("/share")
async def create_share(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
) -> dict:
    request.state.user_id = user_id
    try:
        body = await request.json()
    except Exception:
        # upstream: share.ts:270-272（注意错误码是 invalid_json）
        raise ApiError(400, "invalid_json") from None
    if not isinstance(body, dict):
        raise ApiError(400, "invalid_json")

    post_id = _parse_post_id(body.get("postId"))
    if not post_id:
        raise ApiError(400, "post_id_required")

    snapshot = _parse_html_snapshot(body.get("htmlSnapshot"))
    if snapshot is None:
        raise ApiError(400, "html_snapshot_required")

    snapshot_bytes = len(
        (snapshot["bodyHtml"] + snapshot["stylesHtml"]).encode("utf-8")
    )
    if snapshot_bytes > MAX_SNAPSHOT_BYTES:
        raise ApiError(413, "snapshot_too_large")

    password_result = _resolve_share_password(body)
    if not password_result["ok"]:
        raise ApiError(400, password_result["error"])

    user = db.get_user_by_id(conn, user_id)
    if user is None:
        raise ApiError(404, "not_found")
    plan = get_effective_plan(user.plan, user.plan_expires_at)

    rate = peek_share_create_rate_limit(conn, user_id, plan)
    if not rate["allowed"]:
        # upstream: share.ts:297-308
        raise ApiError(
            429,
            "rate_limited",
            extra={
                "plan": plan,
                "period": rate["period"],
                "limit": rate["limit"],
                "retryAfterSec": rate["retry_after_sec"],
            },
        )

    existing = share_db.get_share_by_user_and_post_id(conn, user_id, post_id)
    now = _now_ms()
    expires_at = _resolve_share_expires_at(body.get("expiresMode"), plan, now)
    raw_title = body.get("title")
    # upstream: share.ts:314（JS slice 按 UTF-16 码元；Python 按码点，BMP 内一致）
    title = raw_title.strip()[:MAX_TITLE_LENGTH] if isinstance(raw_title, str) else ""
    share_id = existing.id if existing is not None else await _derive_share_id(user_id, post_id)

    try:
        html = build_share_page_html(
            title, snapshot["bodyHtml"], snapshot["stylesHtml"]
        )
    except Exception:
        # upstream: share.ts:321-324
        raise ApiError(400, "render_failed") from None

    password_hash = password_result["passwordHash"]
    if existing is not None:
        updated = share_db.update_share_content(
            conn,
            user_id=user_id,
            post_id=post_id,
            title=title,
            html=html,
            password_hash=password_hash,
            expires_at=expires_at,
        )
        if not updated:
            raise ApiError(403, "forbidden")
    else:
        share_db.insert_share(
            conn,
            share_id=share_id,
            post_id=post_id,
            user_id=user_id,
            title=title,
            html=html,
            password_hash=password_hash,
            created_at=now,
            expires_at=expires_at,
        )

    consume_share_create_rate_limit(conn, user_id, plan)

    # upstream: share.ts:353-360（password 键仅 auto 模式出现）
    response = {
        "id": share_id,
        "url": _build_share_url(request, share_id),
        "expiresAt": expires_at,
        "updated": existing is not None,
        "protected": password_hash is not None,
    }
    generated = password_result.get("generatedPassword")
    if generated:
        response["password"] = generated
    return response


# ---- 公开页面 ----


# upstream: share.ts:373-401
@router.get("/s/{share_id}")
async def view_share(
    share_id: str,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
) -> Response:
    if not _SHARE_ID_RE.match(share_id):
        return PlainTextResponse("Not Found", status_code=404)

    share = share_db.get_share_by_id(conn, share_id)
    if share is None:
        return PlainTextResponse("Not Found", status_code=404)

    if share.expires_at is not None and share.expires_at <= _now_ms():
        return PlainTextResponse("This share link has expired.", status_code=410)

    if share.password_hash is not None and not _has_share_access(request, share_id):
        error_raw = request.query_params.get("error")
        gate_error = error_raw if error_raw in ("rate_limited", "invalid") else None
        author = _resolve_share_author(conn, share.user_id)
        return _share_html_response(
            build_share_gate_html(share_id, share.title, gate_error, author)
        )

    view_count = share_db.increment_share_view_count(conn, share_id)
    author = _resolve_share_author(conn, share.user_id)
    html = inject_share_footer(share.html, author, view_count)
    return _share_html_response(html)


# upstream: share.ts:403-442
@router.post("/s/{share_id}/unlock")
async def unlock_share(
    share_id: str,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
) -> Response:
    if not _SHARE_ID_RE.match(share_id):
        return PlainTextResponse("Not Found", status_code=404)

    share = share_db.get_share_by_id(conn, share_id)
    if share is None:
        return PlainTextResponse("Not Found", status_code=404)

    if share.expires_at is not None and share.expires_at <= _now_ms():
        return PlainTextResponse("This share link has expired.", status_code=410)

    if share.password_hash is None:
        return RedirectResponse(f"/s/{share_id}", status_code=303)

    scope_key = f"unlock:{share_id}:{_get_client_ip(request)}"
    attempt_count = share_db.get_share_rate_limit_count(conn, scope_key)
    if attempt_count >= UNLOCK_ATTEMPT_LIMIT:
        if _wants_json_response(request):
            return JSONResponse(
                {"error": "rate_limited",
                 "retryAfterSec": sync_retry_after_sec()},
                status_code=429,
            )
        return RedirectResponse(
            f"/s/{share_id}?error=rate_limited", status_code=303
        )

    password = await _parse_unlock_password(request)
    valid = verify_share_password(password, share.password_hash) if password else False
    if not valid:
        share_db.increment_share_rate_limit(conn, scope_key)
        if _wants_json_response(request):
            return JSONResponse({"error": "invalid_password"}, status_code=401)
        return RedirectResponse(f"/s/{share_id}?error=invalid", status_code=303)

    secret = request.app.state.config.jwt_secret
    token = issue_share_access_token(secret, share_id, share.expires_at)

    if _wants_json_response(request):
        return JSONResponse({"ok": True, "url": f"/s/{share_id}"})

    response = RedirectResponse(f"/s/{share_id}", status_code=303)
    _set_share_access_cookie(response, request, share_id, token, share.expires_at)
    return response
