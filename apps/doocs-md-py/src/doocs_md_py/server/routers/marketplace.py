"""/marketplace 路由全集（upstream: apps/api/src/marketplace.ts 1:1）。

三组端点：
- 公开浏览：GET /themes|/components、GET /:id、POST /:id/install；
- 作者：GET /me、POST /themes|/components、PATCH/DELETE /:id；
- 管理员：GET /admin/pending、POST /admin/:id/approve|reject。

静态路径先于 /:id 注册；通知联动失败仅记日志，不阻断主流程。
"""

import logging
import sqlite3
import time
import uuid

import jwt
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from .. import db
from ..config import Config
from ..deps import get_db
from ..httputil import ApiError
from ..marketplace_admin import is_admin
from ..marketplace_db import (
    approve_marketplace_item,
    delete_marketplace_item_by_author,
    get_marketplace_item_by_id,
    increment_download_count,
    insert_marketplace_item,
    list_approved_items,
    list_items_by_author,
    list_pending_items,
    reject_marketplace_item,
    row_to_detail,
    row_to_summary,
    update_marketplace_item_by_author,
)
from ..marketplace_validate import (
    parse_reject_reason,
    validate_publish_component,
    validate_publish_theme,
    validate_update,
)
from ..notifications_db import notify_users, resolve_admin_user_ids
from ..plan import get_effective_plan
from ..ratelimit import consume_marketplace_publish_rate_limit
from ..security import require_user, verify_token

router = APIRouter(prefix="/marketplace", tags=["marketplace"])

_logger = logging.getLogger("doocs_md_py.marketplace")

# upstream: marketplace.ts:38-41
MARKETPLACE_PUBLISH_LIMIT = {"free": 5, "pro": 30}
# upstream: marketplace.ts:43-44
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 50


def _now_ms() -> int:
    return int(time.time() * 1000)


def _json_error(status_code: int, error: str, extra: dict | None = None) -> JSONResponse:
    body = {"error": error}
    if extra:
        body.update(extra)
    return JSONResponse(status_code=status_code, content=body)


# upstream: marketplace.ts:54-58
def _parse_type(value: str | None) -> str | None:
    if value in ("theme", "component"):
        return value
    return None


# upstream: marketplace.ts:60-62
def _parse_sort(value: str | None) -> str:
    return "popular" if value == "popular" else "newest"


# upstream: marketplace.ts:64-69
def _parse_page(value: str | None) -> int:
    try:
        n = int(value) if value is not None else 1
    except (TypeError, ValueError):
        return 1
    return n if n >= 1 else 1


# upstream: marketplace.ts:71-76
def _parse_page_size(value: str | None) -> int:
    try:
        n = int(value) if value is not None else DEFAULT_PAGE_SIZE
    except (TypeError, ValueError):
        return DEFAULT_PAGE_SIZE
    if n < 1:
        return DEFAULT_PAGE_SIZE
    return min(n, MAX_PAGE_SIZE)


async def _try_get_user_id(request: Request) -> str | None:
    """upstream: marketplace.ts:78-92；可选 Bearer，任何失败均返回 None 而非 401。"""
    header = request.headers.get("authorization") or ""
    token = header[7:] if header.startswith("Bearer ") else ""
    if not token:
        return None
    try:
        payload = verify_token(request.app.state.config.jwt_secret, token)
    except jwt.PyJWTError:
        return None
    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        return None
    return sub


def _require_admin(request: Request, conn: sqlite3.Connection, user_id: str) -> None:
    """upstream: marketplace.ts:94-103；用户不存在 404，非管理员 403。"""
    user = db.get_user_by_id(conn, user_id)
    if user is None:
        raise ApiError(404, "not_found")
    if not is_admin(request.app.state.config, user.login):
        raise ApiError(403, "forbidden")


def _notification_payload(row: sqlite3.Row) -> dict:
    # upstream: marketplace.ts:105-119
    return {
        "itemId": row["id"],
        "itemType": row["type"],
        "name": row["name"],
        "slug": row["slug"],
        "rejectReason": row["reject_reason"],
    }


async def _notify_admins_pending(
    request: Request, conn: sqlite3.Connection, row: sqlite3.Row, created_at: int
) -> None:
    """upstream: marketplace.ts:121-138；通知全部已登录过的管理员（含作者本人）。"""
    try:
        config: Config = request.app.state.config
        admin_ids = resolve_admin_user_ids(conn, config)
        notify_users(
            conn,
            admin_ids,
            notification_type="marketplace_pending",
            payload=_notification_payload(row),
            created_at=created_at,
        )
    except Exception:  # noqa: BLE001 —— 上游 console.error 后吞掉，通知不阻断发布
        _logger.exception("[marketplace] notifyAdminsPending failed")


async def _notify_author_review_result(
    conn: sqlite3.Connection,
    row: sqlite3.Row,
    notification_type: str,
    created_at: int,
) -> None:
    """upstream: marketplace.ts:140-156。"""
    try:
        notify_users(
            conn,
            [row["author_id"]],
            notification_type=notification_type,
            payload=_notification_payload(row),
            created_at=created_at,
        )
    except Exception:  # noqa: BLE001 —— 通知失败不阻断审批
        _logger.exception("[marketplace] notifyAuthorReviewResult failed")


async def _list_public(request: Request, conn: sqlite3.Connection, item_type: str):
    # upstream: marketplace.ts:158-181
    q_raw = request.query_params.get("q")
    q = q_raw.strip()[:64] if q_raw is not None else ""
    q_value = q or None
    sort = _parse_sort(request.query_params.get("sort"))
    page = _parse_page(request.query_params.get("page"))
    page_size = _parse_page_size(request.query_params.get("pageSize"))

    rows, total = list_approved_items(
        conn,
        item_type=item_type,
        q=q_value,
        sort=sort,
        page=page,
        page_size=page_size,
    )
    return {
        "items": [row_to_summary(r) for r in rows],
        "total": total,
        "page": page,
        "pageSize": page_size,
    }


# ---- 公开浏览 ----


# upstream: marketplace.ts:404-405
@router.get("/themes")
async def list_public_themes(
    request: Request, conn: sqlite3.Connection = Depends(get_db)
) -> dict:
    return await _list_public(request, conn, "theme")


@router.get("/components")
async def list_public_components(
    request: Request, conn: sqlite3.Connection = Depends(get_db)
) -> dict:
    return await _list_public(request, conn, "component")


# ---- 作者端点（须先于 /{item_id} 注册）----


# upstream: marketplace.ts:407
@router.get("/me")
async def list_my_items(
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
) -> dict:
    # upstream: marketplace.ts:278-283
    rows = list_items_by_author(conn, user_id)
    return {"items": [row_to_summary(r, include_reject_reason=True) for r in rows]}


# upstream: marketplace.ts:408-409
@router.post("/themes")
async def publish_theme(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
):
    return await _publish(request, conn, user_id, "theme")


@router.post("/components")
async def publish_component(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
):
    return await _publish(request, conn, user_id, "component")


# ---- 管理员端点 ----


# upstream: marketplace.ts:411
@router.get("/admin/pending")
async def list_pending(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
) -> dict:
    # upstream: marketplace.ts:332-348
    _require_admin(request, conn, user_id)
    item_type = _parse_type(request.query_params.get("type"))
    page = _parse_page(request.query_params.get("page"))
    page_size = _parse_page_size(request.query_params.get("pageSize"))
    rows, total = list_pending_items(
        conn, page=page, page_size=page_size, item_type=item_type
    )
    return {
        "items": [row_to_detail(r, include_reject_reason=True) for r in rows],
        "total": total,
        "page": page,
        "pageSize": page_size,
    }


# upstream: marketplace.ts:412
@router.post("/admin/{item_id}/approve")
async def approve_item(
    item_id: str,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
):
    # upstream: marketplace.ts:350-371
    _require_admin(request, conn, user_id)
    now = _now_ms()
    if not approve_marketplace_item(conn, item_id, now):
        raise ApiError(404, "not_found")
    row = get_marketplace_item_by_id(conn, item_id)
    if row is None:
        raise ApiError(404, "not_found")
    await _notify_author_review_result(conn, row, "marketplace_approved", now)
    return row_to_detail(row, include_reject_reason=True)


# upstream: marketplace.ts:413
@router.post("/admin/{item_id}/reject")
async def reject_item(
    item_id: str,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
):
    # upstream: marketplace.ts:373-396
    _require_admin(request, conn, user_id)
    try:
        body = await request.json()
    except Exception:
        body = {}
    reason = parse_reject_reason(body.get("reason") if isinstance(body, dict) else None)
    now = _now_ms()
    if not reject_marketplace_item(conn, item_id, reason, now):
        raise ApiError(404, "not_found")
    row = get_marketplace_item_by_id(conn, item_id)
    if row is None:
        raise ApiError(404, "not_found")
    await _notify_author_review_result(conn, row, "marketplace_rejected", now)
    return row_to_detail(row, include_reject_reason=True)


# ---- 单条目动态路由（静态路径之后注册）----


# upstream: marketplace.ts:415
@router.get("/{item_id}")
async def get_item(
    item_id: str,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
):
    # upstream: marketplace.ts:183-201
    row = get_marketplace_item_by_id(conn, item_id)
    if row is None:
        raise ApiError(404, "not_found")

    user_id = await _try_get_user_id(request)
    user = db.get_user_by_id(conn, user_id) if user_id else None
    is_author = user_id == row["author_id"]
    admin = is_admin(request.app.state.config, user.login) if user else False

    if row["status"] != "approved" and not is_author and not admin:
        raise ApiError(404, "not_found")
    return row_to_detail(row, include_reject_reason=is_author or admin)


# upstream: marketplace.ts:416
@router.post("/{item_id}/install")
async def install_item(
    item_id: str, conn: sqlite3.Connection = Depends(get_db)
):
    # upstream: marketplace.ts:203-218
    row = get_marketplace_item_by_id(conn, item_id)
    if row is None or row["status"] != "approved":
        raise ApiError(404, "not_found")
    download_count = increment_download_count(conn, item_id)
    result = row_to_detail(row)
    result["downloadCount"] = download_count
    return result


# upstream: marketplace.ts:417
@router.patch("/{item_id}")
async def update_item(
    item_id: str,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
):
    # upstream: marketplace.ts:285-319
    existing = get_marketplace_item_by_id(conn, item_id)
    if existing is None:
        raise ApiError(404, "not_found")
    if existing["author_id"] != user_id:
        raise ApiError(403, "forbidden")

    try:
        body = await request.json()
    except Exception:
        body = None
    validated = validate_update(
        existing["type"], body, current_version=existing["version"]
    )
    if not validated.ok:
        raise ApiError(400, validated.error)

    now = _now_ms()
    updated = update_marketplace_item_by_author(
        conn,
        item_id=item_id,
        author_id=user_id,
        patch=validated.value,
        status="pending",
        updated_at=now,
    )
    if not updated:
        raise ApiError(404, "not_found")

    row = get_marketplace_item_by_id(conn, item_id)
    if row is None:
        raise ApiError(404, "not_found")
    await _notify_admins_pending(request, conn, row, now)
    return row_to_detail(row, include_reject_reason=True)


# upstream: marketplace.ts:418
@router.delete("/{item_id}")
async def delete_item(
    item_id: str,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
):
    # upstream: marketplace.ts:321-330
    if not delete_marketplace_item_by_author(conn, user_id, item_id):
        raise ApiError(404, "not_found")
    return {"ok": True}


# ---- 发布处理器（公共逻辑，upstream: marketplace.ts:220-276）----


async def _publish(
    request: Request,
    conn: sqlite3.Connection,
    user_id: str,
    item_type: str,
):
    user = db.get_user_by_id(conn, user_id)
    if user is None:
        raise ApiError(404, "not_found")

    config: Config = request.app.state.config

    # upstream: marketplace.ts:229-240 管理员豁免日发布上限
    if not is_admin(config, user.login):
        plan = get_effective_plan(user.plan, user.plan_expires_at)
        limit = MARKETPLACE_PUBLISH_LIMIT[plan]
        rate = consume_marketplace_publish_rate_limit(conn, user_id, limit)
        if not rate["allowed"]:
            return _json_error(
                429,
                "rate_limited",
                extra={"limit": rate["limit"], "retryAfterSec": rate["retry_after_sec"]},
            )

    # upstream: marketplace.ts:242-248 坏 JSON → null → invalid_body
    try:
        body = await request.json()
    except Exception:
        body = None
    validated = (
        validate_publish_theme(body)
        if item_type == "theme"
        else validate_publish_component(body)
    )
    if not validated.ok:
        raise ApiError(400, validated.error)

    now = _now_ms()
    item_id = str(uuid.uuid4())

    # upstream: marketplace.ts:253-267 UNIQUE 冲突（author_id,type,slug）→ 409
    try:
        insert_marketplace_item(
            conn,
            item_id=item_id,
            author_id=user_id,
            data=validated.value,
            status="pending",
            created_at=now,
        )
    except sqlite3.IntegrityError as exc:
        if "UNIQUE" in str(exc) or "unique" in str(exc):
            return _json_error(409, "slug_taken")
        raise

    row = get_marketplace_item_by_id(conn, item_id)
    if row is None:
        raise ApiError(404, "not_found")

    await _notify_admins_pending(request, conn, row, now)
    return JSONResponse(status_code=201, content=row_to_detail(row, include_reject_reason=True))
