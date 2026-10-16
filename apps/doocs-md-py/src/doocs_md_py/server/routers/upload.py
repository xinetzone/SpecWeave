"""POST /upload 图片上传（upstream: apps/api/src/upload.ts 1:1，新增 local 后端分支）。

分支顺序与错误码逐字对齐：
404 upload_disabled → 503 upload_not_configured → 400 invalid_form_data →
400 file_required → 400 invalid_file_type → 400 file_too_large{maxBytes} →
429 rate_limit_exceeded{limit,retryAfterSec,upgradeRequired} →
200 {url}（成功后才计数）/ 502 upload_failed{message}。

匿名（无/坏 Bearer）按 IP 限流（60/h），登录 free 120、pro 300。
"""

import sqlite3

import httpx
import jwt
from fastapi import APIRouter, Request
from starlette.datastructures import UploadFile
from starlette.responses import JSONResponse

from .. import db
from ..deps import get_db, get_http_client
from ..plan import get_effective_plan
from ..security import verify_token
from ..storage import LocalBackend
from ..upload_config import (
    GITHUB_BACKEND,
    LOCAL_BACKEND,
    R2_BACKEND,
    UPLOAD_MAX_BYTES,
    get_upload_backend,
    is_upload_backend_ready,
    is_upload_enabled,
    parse_github_upload_config,
)
from ..upload_filename import build_dated_object_key, dated_directory
from ..upload_github import UploadPayload, upload_to_github
from ..upload_rate import (
    get_upload_rate_limit_count,
    increment_upload_rate_limit,
    upload_rate_limit_for_plan,
    upload_rate_limit_retry_after_sec,
)
from ..upload_r2 import upload_to_r2

router = APIRouter(tags=["upload"])

DEFAULT_CONTENT_TYPE = "application/octet-stream"


# upstream: upload.ts:25-29
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


# upstream: upload.ts:31-53
def _resolve_upload_scope(
    request: Request, conn: sqlite3.Connection
) -> tuple[str, str | None]:
    ip = _get_client_ip(request)
    header = request.headers.get("authorization") or ""
    token = header[7:] if header.startswith("Bearer ") else ""
    if not token:
        return f"upload:ip:{ip}", None

    try:
        payload = verify_token(request.app.state.config.jwt_secret, token)
    except jwt.PyJWTError:
        return f"upload:ip:{ip}", None

    sub = payload.get("sub")
    if not isinstance(sub, str):
        return f"upload:ip:{ip}", None

    user = db.get_user_by_id(conn, sub)
    if user is None:
        return f"upload:ip:{ip}", None

    plan = get_effective_plan(user.plan, user.plan_expires_at)
    return f"upload:user:{sub}", plan


# upstream: upload.ts:77-122
@router.post("/upload")
async def upload_handler(request: Request):
    config = request.app.state.config
    conn = get_db(request)

    if not is_upload_enabled(config):
        return JSONResponse({"error": "upload_disabled"}, status_code=404)

    if not is_upload_backend_ready(config):
        return JSONResponse({"error": "upload_not_configured"}, status_code=503)

    try:
        form = await request.form()
    except Exception:
        return JSONResponse({"error": "invalid_form_data"}, status_code=400)

    file = form.get("file")
    if not isinstance(file, UploadFile):
        return JSONResponse({"error": "file_required"}, status_code=400)

    # upstream: upload.ts:73-75（仅 image/ 前缀，不做 magic 嗅探）
    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        return JSONResponse({"error": "invalid_file_type"}, status_code=400)

    content = await file.read()
    if len(content) <= 0 or len(content) > UPLOAD_MAX_BYTES:
        return JSONResponse(
            {"error": "file_too_large", "maxBytes": UPLOAD_MAX_BYTES}, status_code=400
        )

    scope_key, plan = _resolve_upload_scope(request, conn)
    limit = upload_rate_limit_for_plan(plan)
    count = get_upload_rate_limit_count(conn, scope_key)
    if count >= limit:
        return JSONResponse(
            {
                "error": "rate_limit_exceeded",
                "limit": limit,
                "retryAfterSec": upload_rate_limit_retry_after_sec(),
                "upgradeRequired": plan == "free",
            },
            status_code=429,
        )

    referer = (
        request.headers.get("referer")
        or request.headers.get("origin")
        or "md-api"
    )
    payload = UploadPayload(
        name=file.filename or "", content_type=content_type, content=content
    )
    http_client: httpx.Client = get_http_client(request)

    try:
        backend = get_upload_backend(config)
        if backend == R2_BACKEND:
            url = upload_to_r2(config, payload, http_client)
        elif backend == GITHUB_BACKEND:
            gh_config = parse_github_upload_config(config)
            if gh_config is None:
                # 理论不可达：ready 门已拦截；保持与上游非空断言一致
                raise RuntimeError("github upload is not configured")
            url = upload_to_github(gh_config, payload, referer, http_client)
        elif backend == LOCAL_BACKEND:
            key = f"{dated_directory()}/{build_dated_object_key(payload.name, content_type)}"
            local = LocalBackend(config.storage_local_dir, config.storage_local_base_url)
            url = local.put(key, content, content_type or DEFAULT_CONTENT_TYPE)
        else:  # pragma: no cover - get_upload_backend 已收敛枚举
            raise RuntimeError(f"unknown upload backend: {backend!r}")

        increment_upload_rate_limit(conn, scope_key)
        return JSONResponse({"url": url}, status_code=200)
    except Exception as exc:
        message = str(exc) or "upload_failed"
        return JSONResponse(
            {"error": "upload_failed", "message": message}, status_code=502
        )
