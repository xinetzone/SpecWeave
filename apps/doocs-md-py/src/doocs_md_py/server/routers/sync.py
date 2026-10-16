"""/sync/pull、/sync/push、/sync/activate（upstream: apps/api/src/sync.ts 1:1）。

挂载于鉴权 api 组（index.ts:53-58），所有端点经 require_user。
路由声明为 async 仅为读取 JSON body；SQLite 为本地快速同步调用，
自托管单 worker 下直接执行（与 db.connect(check_same_thread=False) 配套）。
"""

import math
import re
import sqlite3

import httpx
from fastapi import APIRouter, Depends, Request

from .. import db
from ..afdian import query_order
from ..config import Config
from ..deps import get_db, get_http_client
from ..httputil import ApiError
from ..plan import (
    activate_pro_from_order,
    get_effective_plan,
    parse_github_login_from_remark,
)
from ..ratelimit import check_sync_rate_limit
from ..security import require_user
from ..sync_limits import (
    SYNC_PUSH_LIMITS,
    SYNC_STORED_DOCUMENT_LIMIT,
    SYNC_STORED_ROW_LIMIT,
    count_new_active_documents,
    count_new_document_ids,
    exceeds_stored_document_quota,
    exceeds_stored_row_quota,
    normalize_push_documents,
    validate_push_payload,
)
from ..types import SyncDocument, SyncSetting

router = APIRouter(tags=["sync"])

_LEADING_INT_RE = re.compile(r"^\s*([+-]?\d+)")


def _parse_int_loose(raw: str | None, default: int = 0) -> int:
    """等价 JS Number.parseInt(raw, 10)：前导空白/符号+数字，无法解析得默认值。"""
    if raw is None:
        return default
    match = _LEADING_INT_RE.match(raw)
    if match is None:
        return default
    try:
        return int(match.group(1))
    except ValueError:
        return default


async def _enforce_sync_rate_limit(request: Request, conn: sqlite3.Connection) -> str:
    """upstream: sync.ts:19-41；鉴权+套餐+小时窗限流，返回有效 plan。

    用户不存在抛 404，超限抛 429。user_id 取自 request.state（require_user 写入）。
    """
    user_id = request.state.user_id
    user = db.get_user_by_id(conn, user_id)
    if user is None:
        # upstream: sync.ts:24-25
        raise ApiError(404, "not_found")

    plan = get_effective_plan(user.plan, user.plan_expires_at)
    rate = check_sync_rate_limit(conn, user_id, plan)
    if not rate["allowed"]:
        # upstream: sync.ts:29-38
        raise ApiError(
            429,
            "rate_limit_exceeded",
            extra={
                "plan": plan,
                "limit": rate["limit"],
                "retryAfterSec": rate["retry_after_sec"],
                "upgradeRequired": plan == "free",
            },
        )
    return plan


# upstream: sync.ts:43-55
@router.get("/sync/pull")
async def pull(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
) -> dict:
    request.state.user_id = user_id
    await _enforce_sync_rate_limit(request, conn)

    since = _parse_int_loose(request.query_params.get("since"), 0)
    cursor = since if math.isfinite(since) and since > 0 else 0

    result = db.pull_changes(conn, user_id, cursor)
    return {
        "documents": [doc.to_api_dict() for doc in result["documents"]],
        "settings": [setting.to_api_dict() for setting in result["settings"]],
        "cursor": result["max_cursor"],
    }


# upstream: sync.ts:57-133
@router.post("/sync/push")
async def push(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
) -> dict:
    request.state.user_id = user_id
    plan = await _enforce_sync_rate_limit(request, conn)

    # upstream: sync.ts:62-68 Content-Length 预检（无该头/非数字时跳过）
    content_length_raw = request.headers.get("content-length")
    if content_length_raw is not None:
        try:
            content_length = int(content_length_raw)
        except ValueError:
            content_length = -1
        if math.isfinite(content_length) and content_length > SYNC_PUSH_LIMITS["maxRequestBytes"]:
            raise ApiError(
                413,
                "payload_too_large",
                extra={"max": SYNC_PUSH_LIMITS["maxRequestBytes"]},
            )

    # upstream: sync.ts:72-78
    try:
        body = await request.json()
    except Exception:
        raise ApiError(400, "invalid_body") from None
    if not isinstance(body, dict):
        raise ApiError(400, "invalid_body")

    raw_documents = body.get("documents") if body.get("documents") is not None else []
    raw_settings = body.get("settings") if body.get("settings") is not None else []

    # upstream: sync.ts:83-90
    invalid = validate_push_payload(raw_documents, raw_settings)
    if invalid is not None:
        extra: dict = {}
        if "field" in invalid:
            extra["field"] = invalid["field"]
        if "max" in invalid:
            extra["max"] = invalid["max"]
        raise ApiError(invalid["status"], invalid["error"], extra=extra)

    # upstream: sync.ts:92-93（先类型化再剥墓碑）
    typed_documents = normalize_push_documents(
        [SyncDocument.from_api_dict(d) for d in raw_documents]
    )
    typed_settings = [SyncSetting.from_api_dict(s) for s in raw_settings]

    # upstream: sync.ts:95-124 存量双配额（仅在有文档时）
    if typed_documents:
        existing = db.list_existing_documents(
            conn, user_id, [doc.id for doc in typed_documents]
        )
        stored_active_count = db.count_active_documents(conn, user_id)
        stored_row_count = db.count_stored_documents(conn, user_id)
        new_active_count = count_new_active_documents(typed_documents, existing)
        new_row_count = count_new_document_ids(typed_documents, existing)

        if exceeds_stored_document_quota(plan, stored_active_count, new_active_count):
            raise ApiError(
                403,
                "document_quota_exceeded",
                extra={
                    "plan": plan,
                    "limit": SYNC_STORED_DOCUMENT_LIMIT[plan],
                    "upgradeRequired": plan == "free",
                },
            )
        if exceeds_stored_row_quota(plan, stored_row_count, new_row_count):
            raise ApiError(
                403,
                "document_quota_exceeded",
                extra={
                    "plan": plan,
                    "limit": SYNC_STORED_ROW_LIMIT[plan],
                    "upgradeRequired": plan == "free",
                },
            )

    # upstream: sync.ts:126-132
    result = db.push_changes(conn, user_id, typed_documents, typed_settings)
    return {
        "documents": [doc.to_api_dict() for doc in result["documents"]],
        "settings": [setting.to_api_dict() for setting in result["settings"]],
        "cursor": result["max_cursor"],
    }


# upstream: apps/api/src/activate.ts:9-53
@router.post("/sync/activate")
async def activate(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
    client: httpx.Client = Depends(get_http_client),
) -> dict:
    request.state.user_id = user_id
    config: Config = request.app.state.config
    # upstream: activate.ts:10-11
    if not config.is_afdian_configured():
        raise ApiError(503, "afdian_not_configured")

    # upstream: activate.ts:13-19
    try:
        body = await request.json()
    except Exception:
        raise ApiError(400, "invalid_body") from None
    raw_order_no = body.get("orderNo") if isinstance(body, dict) else None
    order_no = raw_order_no.strip() if isinstance(raw_order_no, str) else None
    if not order_no:
        # upstream: activate.ts:21-23
        raise ApiError(400, "order_no_required")

    # upstream: activate.ts:25-27
    user = db.get_user_by_id(conn, user_id)
    if user is None:
        raise ApiError(404, "not_found")

    # upstream: activate.ts:29-31 订单事实回查爱发电
    order = query_order(client, config, order_no)
    if order is None:
        raise ApiError(404, "order_not_found")

    # upstream: activate.ts:33-34
    if order.status != 2:
        raise ApiError(400, "order_not_paid")

    # upstream: activate.ts:36-40 备注有登录名但与当前用户不符才拒绝；
    # 备注无登录名时不拦截，按当前登录用户激活
    remark_login = parse_github_login_from_remark(order.remark)
    current_login = user.login.lower()
    if remark_login and remark_login != current_login:
        raise ApiError(403, "remark_mismatch")

    # upstream: activate.ts:42-46
    result = activate_pro_from_order(conn, config, order, user.login)
    if not result["ok"]:
        status = 404 if result["reason"] == "user_not_found" else 400
        raise ApiError(status, result["reason"])

    # upstream: activate.ts:48-52
    plan = get_effective_plan("pro", result["expires_at"])
    return {"plan": plan, "planExpiresAt": result["expires_at"]}
