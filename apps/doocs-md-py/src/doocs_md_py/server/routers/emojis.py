"""/emojis 路由（upstream: apps/api/src/emojis.ts 1:1）。

- 公开：GET /emojis/default 系统包 manifest、GET /emojis/assets/{id} 资产字节；
- 鉴权：GET/PATCH /emojis/me、POST /emojis/me/items、
  DELETE /emojis/me/items/{id}、DELETE /emojis/me。

资产字节始终经本服务读取下发（上游同样从 R2 binding 读后 Response 流出），
系统包 immutable、用户包 max-age=300。
"""

import logging
import sqlite3
import time
import uuid
from urllib.parse import quote

from fastapi import APIRouter, Depends, Request
from starlette.datastructures import UploadFile
from starlette.responses import JSONResponse, Response

from .. import emoji_db
from ..deps import get_db
from ..emoji_storage import PrefixedStorage
from ..emoji_validate import (
    EMOJI_MAX_ITEMS,
    sanitize_emoji_name,
    sanitize_pack_name,
    validate_emoji_file,
)
from ..security import require_user
from ..upload_config import UPLOAD_MAX_BYTES

router = APIRouter(prefix="/emojis", tags=["emojis"])

_logger = logging.getLogger("doocs_md_py.emojis")


def _now_ms() -> int:
    return int(time.time() * 1000)


def _origin(request: Request) -> str:
    # upstream: new URL(c.req.url).origin —— scheme://host[:port]，无尾斜杠
    return str(request.base_url).rstrip("/")


def _storage(request: Request) -> PrefixedStorage:
    return request.app.state.emoji_storage


def item_json(item, origin: str) -> dict:
    """upstream: emojis.ts:29-42。"""
    item_id = item["id"]
    return {
        "id": item_id,
        "name": item["name"],
        "mime": item["mime"],
        "size": item["size"],
        "width": item["width"],
        "height": item["height"],
        "sortOrder": item["sort_order"],
        "createdAt": item["created_at"],
        "updatedAt": item["updated_at"],
        "url": f"{origin}/emojis/assets/{quote(item_id, safe='')}",
    }


def manifest_json(pack, items, origin: str) -> dict:
    """upstream: emojis.ts:44-62。"""
    return {
        "id": pack["id"],
        "kind": pack["kind"],
        "slug": pack["slug"],
        "name": pack["name"],
        "metadata": {
            "sourceUrl": pack["source_url"],
            "sourceCommit": pack["source_commit"],
            "license": pack["license_spdx"],
            "licenseUrl": pack["license_url"],
            "attribution": pack["attribution"],
            "description": pack["description"],
        },
        "createdAt": pack["created_at"],
        "updatedAt": pack["updated_at"],
        "items": [item_json(item, origin) for item in items],
    }


def _pack_manifest(conn, pack, origin: str) -> dict:
    items = emoji_db.list_pack_items(conn, pack["id"])
    return manifest_json(pack, items, origin)


@router.get("/default")
async def default_manifest(
    request: Request, conn: sqlite3.Connection = Depends(get_db)
):
    # upstream: emojis.ts:69-74
    pack = emoji_db.get_system_pack(conn)
    if pack is None:
        return JSONResponse(status_code=404, content={"error": "not_found"})
    return _pack_manifest(conn, pack, _origin(request))


@router.get("/assets/{item_id}")
async def get_asset(
    request: Request,
    item_id: str,
    conn: sqlite3.Connection = Depends(get_db),
):
    # upstream: emojis.ts:76-101
    item = emoji_db.get_emoji_asset(conn, item_id)
    if item is None:
        return JSONResponse(status_code=404, content={"error": "not_found"})

    obj = _storage(request).get(item["object_key"])
    if obj is None:
        return JSONResponse(status_code=404, content={"error": "not_found"})

    cache_control = (
        "public, max-age=31536000, immutable"
        if item["kind"] == "system"
        else "public, max-age=300"
    )
    return Response(
        content=obj.data,
        media_type=item["mime"],
        headers={
            "Content-Type": item["mime"],
            "Content-Length": str(item["size"]),
            "ETag": obj.etag,
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": cache_control,
        },
    )


@router.get("/me")
async def get_my_manifest(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
):
    # upstream: emojis.ts:103-106
    pack = emoji_db.get_or_create_user_pack(conn, user_id, _now_ms())
    return _pack_manifest(conn, pack, _origin(request))


@router.patch("/me")
async def update_my_pack(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
):
    # upstream: emojis.ts:108-119
    try:
        body = await request.json()
    except Exception:  # noqa: BLE001 - 坏 JSON 与上游 .catch(() => null) 等价
        body = None
    name = sanitize_pack_name(body.get("name")) if isinstance(body, dict) else None
    if not name:
        return JSONResponse(status_code=400, content={"error": "invalid_name"})

    emoji_db.get_or_create_user_pack(conn, user_id, _now_ms())
    emoji_db.update_user_pack_name(conn, user_id, name, _now_ms())
    pack = emoji_db.get_or_create_user_pack(conn, user_id, _now_ms())
    return _pack_manifest(conn, pack, _origin(request))


@router.post("/me/items")
async def upload_my_item(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
):
    # upstream: emojis.ts:121-190
    try:
        form = await request.form()
    except Exception:  # noqa: BLE001 - 非法 multipart 边界
        return JSONResponse(status_code=400, content={"error": "invalid_form_data"})

    upload = form.get("file")
    if not isinstance(upload, UploadFile):
        return JSONResponse(status_code=400, content={"error": "file_required"})

    data = await upload.read()
    size = len(data)
    if size <= 0:
        return JSONResponse(status_code=400, content={"error": "empty_file"})
    if size > UPLOAD_MAX_BYTES:
        return JSONResponse(
            status_code=400,
            content={"error": "file_too_large", "maxBytes": UPLOAD_MAX_BYTES},
        )

    validation = validate_emoji_file(upload.content_type or "", size, data)
    if not validation["ok"]:
        body = {"error": validation["error"]}
        if validation["error"] == "file_too_large":
            body["maxBytes"] = UPLOAD_MAX_BYTES
        return JSONResponse(status_code=400, content=body)

    emoji_db.get_or_create_user_pack(conn, user_id, _now_ms())

    item_id = str(uuid.uuid4())
    object_key = f"user/{user_id}/{item_id}.{validation['extension']}"
    form_name = form.get("name")
    requested_name = form_name if isinstance(form_name, str) else (upload.filename or "")
    name = sanitize_emoji_name(requested_name)
    created_at = _now_ms()

    try:
        _storage(request).put(object_key, data, validation["mime"])
    except Exception:  # noqa: BLE001 - 存储失败映射 502，错误详情入日志
        _logger.exception("emoji asset put failed: %s", object_key)
        return JSONResponse(status_code=502, content={"error": "asset_upload_failed"})

    try:
        inserted = emoji_db.insert_user_emoji_item_conditional(
            conn,
            item_id=item_id,
            user_id=user_id,
            object_key=object_key,
            name=name,
            mime=validation["mime"],
            size=size,
            created_at=created_at,
        )
    except Exception:  # noqa: BLE001
        _logger.exception("emoji item insert failed: %s", object_key)
        _safe_delete(_storage(request), object_key)
        return JSONResponse(status_code=500, content={"error": "database_write_failed"})

    if not inserted:
        # 第 101 个：对象回滚后 409（upstream emojis.ts:183-186）
        _safe_delete(_storage(request), object_key)
        return JSONResponse(
            status_code=409,
            content={"error": "item_limit_reached", "limit": EMOJI_MAX_ITEMS},
        )

    pack = emoji_db.get_or_create_user_pack(conn, user_id, _now_ms())
    return JSONResponse(
        status_code=201, content=_pack_manifest(conn, pack, _origin(request))
    )


@router.delete("/me/items/{item_id}")
async def delete_my_item(
    request: Request,
    item_id: str,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
):
    # upstream: emojis.ts:192-214
    item = emoji_db.get_owned_emoji_item(conn, user_id, item_id)
    if item is None:
        return JSONResponse(status_code=404, content={"error": "not_found"})

    try:
        _storage(request).delete(item["object_key"])
    except Exception:  # noqa: BLE001
        _logger.exception("emoji asset delete failed: %s", item["object_key"])
        return JSONResponse(status_code=502, content={"error": "asset_delete_failed"})

    if not emoji_db.delete_owned_emoji_item(conn, user_id, item_id):
        return JSONResponse(status_code=404, content={"error": "not_found"})

    pack = emoji_db.get_or_create_user_pack(conn, user_id, _now_ms())
    return _pack_manifest(conn, pack, _origin(request))


@router.delete("/me")
async def delete_my_pack(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    user_id: str = Depends(require_user),
):
    # upstream: emojis.ts:216-231
    pack = emoji_db.get_or_create_user_pack(conn, user_id, _now_ms())
    items = emoji_db.list_pack_items(conn, pack["id"])

    try:
        if items:
            _storage(request).delete([item["object_key"] for item in items])
    except Exception:  # noqa: BLE001
        _logger.exception("emoji pack assets delete failed: %s", pack["id"])
        return JSONResponse(status_code=502, content={"error": "asset_delete_failed"})

    emoji_db.delete_user_pack(conn, user_id)
    return {"ok": True}


def _safe_delete(storage: PrefixedStorage, object_key: str) -> None:
    """回滚删除对象本身失败时仅记日志（upstream 同处未处理 reject）。"""
    try:
        storage.delete(object_key)
    except Exception:  # noqa: BLE001
        _logger.exception("emoji rollback delete failed: %s", object_key)
