"""同步推送载荷校验与存量配额（upstream: apps/api/src/sync-limits.ts 1:1）。

- 校验全部针对 JSON 反序列化后的原生 dict/list（写入前校验，不修改输入）；
- 错误码：400 结构类（invalid_*）、413 尺寸类（*_too_large/too_many_*）；
- 存量配额在路由层判定（403 document_quota_exceeded），本模块只提供计数与判定；
- 墓碑（deleted=true）落库前剥除 title/content/history，防止借删除行存储 DoS。
"""

import dataclasses
import json
import math
from typing import TypedDict

from .types import SyncDocument

# upstream: sync-limits.ts:4-17
SYNC_PUSH_LIMITS = {
    "maxDocumentsPerPush": 100,
    "maxSettingsPerPush": 80,
    "maxIdChars": 128,
    "maxTitleBytes": 500,
    "maxContentBytes": 512 * 1024,
    "maxHistoryItems": 20,
    "maxHistoryContentBytes": 512 * 1024,
    "maxSettingKeyChars": 256,
    "maxSettingValueBytes": 1024 * 1024,
    "maxRequestBytes": 8 * 1024 * 1024,
    # D1 行/字符串上限 2MB；为其他列与 JSON 转义留余量
    "maxDocumentRowBytes": 1_800_000,
}

# upstream: sync-limits.ts:19-28
SYNC_STORED_DOCUMENT_LIMIT = {"free": 200, "pro": 2000}
# 含墓碑的总行数：删除后新建不应消耗活跃额度
SYNC_STORED_ROW_LIMIT = {"free": 400, "pro": 4000}


def utf8_bytes(value: str) -> int:
    """upstream: sync-limits.ts:32-34 TextEncoder().encode(value).length。"""
    return len(value.encode("utf-8"))


class PayloadRejection(TypedDict, total=False):
    """upstream: SyncPayloadRejection（field/max 可选）。"""

    error: str
    status: int
    field: str
    max: int


def _reject(
    error: str, status: int, *, field: str | None = None, max_value: int | None = None
) -> PayloadRejection:
    result: PayloadRejection = {"error": error, "status": status}
    if field is not None:
        result["field"] = field
    if max_value is not None:
        result["max"] = max_value
    return result


def _is_finite_number(value) -> bool:
    """upstream: sync-limits.ts:47-49 typeof number && isFinite。

    Python 的 bool 是 int 子类，必须显式排除（JS 中 true/false 不是 number）。
    """
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _validate_history(history) -> PayloadRejection | None:
    """upstream: sync-limits.ts:51-83。"""
    if history is None:
        return None
    if not isinstance(history, list):
        return _reject("invalid_history", 400, field="documents.history")
    if len(history) > SYNC_PUSH_LIMITS["maxHistoryItems"]:
        return _reject(
            "history_too_long",
            413,
            field="documents.history",
            max_value=SYNC_PUSH_LIMITS["maxHistoryItems"],
        )

    for item in history:
        if not isinstance(item, dict):
            return _reject("invalid_history", 400, field="documents.history")

        datetime_value = item.get("datetime")
        datetime_ok = _is_finite_number(datetime_value) or isinstance(datetime_value, str)
        if not datetime_ok or not isinstance(item.get("content"), str):
            return _reject("invalid_history", 400, field="documents.history")

        if utf8_bytes(item["content"]) > SYNC_PUSH_LIMITS["maxHistoryContentBytes"]:
            return _reject(
                "history_content_too_large",
                413,
                field="documents.history.content",
                max_value=SYNC_PUSH_LIMITS["maxHistoryContentBytes"],
            )
    return None


def estimate_document_row_bytes(record: dict) -> int:
    """upstream: sync-limits.ts:133-140。

    JSON.stringify(history) 等价紧凑序列化（不转义非 ASCII）；history 非数组按 0。
    """
    id_value = record.get("id") if isinstance(record.get("id"), str) else ""
    title = record.get("title") if isinstance(record.get("title"), str) else ""
    content = record.get("content") if isinstance(record.get("content"), str) else ""
    parent_id = record.get("parentId") if isinstance(record.get("parentId"), str) else ""
    history = record.get("history") if isinstance(record.get("history"), list) else []
    history_json = json.dumps(history, ensure_ascii=False, separators=(",", ":"))
    return (
        utf8_bytes(id_value)
        + utf8_bytes(title)
        + utf8_bytes(content)
        + utf8_bytes(parent_id)
        + utf8_bytes(history_json)
    )


def _validate_document(doc) -> PayloadRejection | None:
    """upstream: sync-limits.ts:85-131。"""
    if not isinstance(doc, dict):
        return _reject("invalid_document", 400, field="documents")

    record = doc
    doc_id = record.get("id")
    if (
        not isinstance(doc_id, str)
        or len(doc_id) == 0
        or len(doc_id) > SYNC_PUSH_LIMITS["maxIdChars"]
    ):
        return _reject(
            "invalid_document_id", 400, field="documents.id",
            max_value=SYNC_PUSH_LIMITS["maxIdChars"],
        )
    if not isinstance(record.get("title"), str):
        return _reject("invalid_document", 400, field="documents.title")
    if utf8_bytes(record["title"]) > SYNC_PUSH_LIMITS["maxTitleBytes"]:
        return _reject(
            "title_too_large", 413, field="documents.title",
            max_value=SYNC_PUSH_LIMITS["maxTitleBytes"],
        )
    if not isinstance(record.get("content"), str):
        return _reject("invalid_document", 400, field="documents.content")
    if utf8_bytes(record["content"]) > SYNC_PUSH_LIMITS["maxContentBytes"]:
        return _reject(
            "content_too_large", 413, field="documents.content",
            max_value=SYNC_PUSH_LIMITS["maxContentBytes"],
        )

    parent_id = record.get("parentId")
    if parent_id is not None:
        if (
            not isinstance(parent_id, str)
            or len(parent_id) == 0
            or len(parent_id) > SYNC_PUSH_LIMITS["maxIdChars"]
        ):
            return _reject(
                "invalid_document_parent_id", 400, field="documents.parentId",
                max_value=SYNC_PUSH_LIMITS["maxIdChars"],
            )
    if not _is_finite_number(record.get("createDatetime")):
        return _reject("invalid_document", 400, field="documents.createDatetime")
    if not _is_finite_number(record.get("updateDatetime")):
        return _reject("invalid_document", 400, field="documents.updateDatetime")
    if not isinstance(record.get("deleted"), bool):
        return _reject("invalid_document", 400, field="documents.deleted")

    history_error = _validate_history(record.get("history"))
    if history_error is not None:
        return history_error

    if estimate_document_row_bytes(record) > SYNC_PUSH_LIMITS["maxDocumentRowBytes"]:
        return _reject(
            "document_too_large", 413, field="documents",
            max_value=SYNC_PUSH_LIMITS["maxDocumentRowBytes"],
        )
    return None


def _validate_setting(setting) -> PayloadRejection | None:
    """upstream: sync-limits.ts:142-165。"""
    if not isinstance(setting, dict):
        return _reject("invalid_setting", 400, field="settings")

    record = setting
    key = record.get("key")
    if (
        not isinstance(key, str)
        or len(key) == 0
        or len(key) > SYNC_PUSH_LIMITS["maxSettingKeyChars"]
    ):
        return _reject(
            "invalid_setting_key", 400, field="settings.key",
            max_value=SYNC_PUSH_LIMITS["maxSettingKeyChars"],
        )
    value = record.get("value")
    if value is not None and not isinstance(value, str):
        return _reject("invalid_setting", 400, field="settings.value")
    if isinstance(value, str) and utf8_bytes(value) > SYNC_PUSH_LIMITS["maxSettingValueBytes"]:
        return _reject(
            "setting_value_too_large", 413, field="settings.value",
            max_value=SYNC_PUSH_LIMITS["maxSettingValueBytes"],
        )
    if not _is_finite_number(record.get("updatedAt")):
        return _reject("invalid_setting", 400, field="settings.updatedAt")
    return None


def validate_push_payload(documents, settings) -> PayloadRejection | None:
    """upstream: sync-limits.ts:168-220；写入前校验，不修改输入。"""
    if not isinstance(documents, list):
        return _reject("invalid_body", 400, field="documents")
    if not isinstance(settings, list):
        return _reject("invalid_body", 400, field="settings")

    if len(documents) > SYNC_PUSH_LIMITS["maxDocumentsPerPush"]:
        return _reject(
            "too_many_documents", 413, field="documents",
            max_value=SYNC_PUSH_LIMITS["maxDocumentsPerPush"],
        )
    if len(settings) > SYNC_PUSH_LIMITS["maxSettingsPerPush"]:
        return _reject(
            "too_many_settings", 413, field="settings",
            max_value=SYNC_PUSH_LIMITS["maxSettingsPerPush"],
        )

    for doc in documents:
        failed = _validate_document(doc)
        if failed is not None:
            return failed
    for setting in settings:
        failed = _validate_setting(setting)
        if failed is not None:
            return failed

    payload_bytes = 0
    for doc in documents:
        payload_bytes += estimate_document_row_bytes(doc)
    for setting in settings:
        key = setting.get("key")
        value = setting.get("value")
        if isinstance(key, str):
            payload_bytes += utf8_bytes(key)
        if isinstance(value, str):
            payload_bytes += utf8_bytes(value)
    if payload_bytes > SYNC_PUSH_LIMITS["maxRequestBytes"]:
        return _reject(
            "payload_too_large", 413, field="body",
            max_value=SYNC_PUSH_LIMITS["maxRequestBytes"],
        )
    return None


def normalize_push_documents(documents: list[SyncDocument]) -> list[SyncDocument]:
    """upstream: sync-limits.ts:223-234；墓碑剥 title/content/history。

    Python dataclass slots 仍允许 replace 造新对象，非墓碑原样返回
    （与上游同一对象引用语义等价）。
    """
    normalized: list[SyncDocument] = []
    for doc in documents:
        if not doc.deleted:
            normalized.append(doc)
        else:
            normalized.append(
                dataclasses.replace(doc, title="", content="", history=[])
            )
    return normalized


def count_new_document_ids(
    documents: list[SyncDocument], existing: dict[str, bool]
) -> int:
    """upstream: sync-limits.ts:236-250；本批去重后，服务端不存在的 id 数（含墓碑）。"""
    seen: set[str] = set()
    added = 0
    for doc in documents:
        if doc.id in seen:
            continue
        seen.add(doc.id)
        if doc.id not in existing:
            added += 1
    return added


def count_new_active_documents(
    documents: list[SyncDocument], existing: dict[str, bool]
) -> int:
    """upstream: sync-limits.ts:256-271。

    新活跃行 = 活跃文档的插入 + 墓碑复活；同批重复 id 只计一次。
    existing[id] 为该 id 当前是否已删除（listExistingDocuments 语义）。
    """
    seen: set[str] = set()
    added = 0
    for doc in documents:
        if doc.deleted or doc.id in seen:
            continue
        seen.add(doc.id)
        deleted = existing.get(doc.id)
        if deleted is None or deleted:
            added += 1
    return added


def exceeds_stored_document_quota(
    plan: str, stored_active_count: int, new_active_count: int
) -> bool:
    """upstream: sync-limits.ts:273-281。"""
    if new_active_count <= 0:
        return False
    return stored_active_count + new_active_count > SYNC_STORED_DOCUMENT_LIMIT[plan]


def exceeds_stored_row_quota(
    plan: str, stored_row_count: int, new_row_count: int
) -> bool:
    """upstream: sync-limits.ts:283-291。"""
    if new_row_count <= 0:
        return False
    return stored_row_count + new_row_count > SYNC_STORED_ROW_LIMIT[plan]
