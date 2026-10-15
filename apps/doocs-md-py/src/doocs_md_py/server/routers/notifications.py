"""/notifications 路由（upstream: apps/api/src/notifications.ts 1:1）。

五端点全部强制 Bearer 鉴权（上游挂在 authMiddleware api 组内）：
列表分页（默认 30、上限 50）、未读计数、单条已读（幂等）、全部已读、清空。
所有查询都带 user_id 属主条件——他人通知对当前用户等价不存在（404）。
"""

import sqlite3
import time

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from .. import notifications_db
from ..deps import get_db
from ..security import require_user

router = APIRouter(prefix="/notifications", tags=["notifications"])

# upstream: notifications.ts:14-15
DEFAULT_PAGE_SIZE = 30
MAX_PAGE_SIZE = 50


def _now_ms() -> int:
    return int(time.time() * 1000)


# upstream: notifications.ts:20-25
def _parse_page(value: str | None) -> int:
    try:
        n = int(value) if value is not None else 1
    except (TypeError, ValueError):
        return 1
    return n if n >= 1 else 1


# upstream: notifications.ts:27-32
def _parse_page_size(value: str | None) -> int:
    try:
        n = int(value) if value is not None else DEFAULT_PAGE_SIZE
    except (TypeError, ValueError):
        return DEFAULT_PAGE_SIZE
    if n < 1:
        return DEFAULT_PAGE_SIZE
    return min(n, MAX_PAGE_SIZE)


@router.get("")
@router.get("/")
async def list_notifications(
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
    page: str | None = None,
    pageSize: str | None = None,  # noqa: N803 - 查询参数逐字上游 camelCase
):
    # upstream: notifications.ts:34-45
    page_n = _parse_page(page)
    page_size_n = _parse_page_size(pageSize)
    rows, total = notifications_db.list_notifications(
        conn, user_id, page=page_n, page_size=page_size_n
    )
    return {
        "items": [notifications_db.row_to_notification(row) for row in rows],
        "total": total,
        "page": page_n,
        "pageSize": page_size_n,
    }


@router.get("/unread-count")
async def unread_count(
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
):
    # upstream: notifications.ts:47-50
    count = notifications_db.count_unread_notifications(conn, user_id)
    return {"count": count}


@router.post("/read-all")
async def mark_all_read(
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
):
    # upstream: notifications.ts:67-70；静态路径必须先于 /{id}/read 注册
    notifications_db.mark_all_notifications_read(conn, user_id, _now_ms())
    return {"ok": True}


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
):
    # upstream: notifications.ts:52-65
    if not notification_id:
        return JSONResponse(status_code=404, content={"error": "not_found"})
    existing = notifications_db.get_notification_by_id(conn, user_id, notification_id)
    if existing is None:
        return JSONResponse(status_code=404, content={"error": "not_found"})
    if existing["read_at"] is None:
        notifications_db.mark_notification_read(
            conn, user_id, notification_id, _now_ms()
        )
    return {"ok": True}


@router.delete("")
@router.delete("/")
async def clear_all(
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
):
    # upstream: notifications.ts:72-75
    notifications_db.clear_all_notifications(conn, user_id)
    return {"ok": True}
