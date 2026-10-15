"""TR-11.1 sync-limits 纯函数（upstream: sync-limits.test.ts 全用例 + Python 边界）。"""

import math

from doocs_md_py.server.sync_limits import (
    SYNC_PUSH_LIMITS as L,
    SYNC_STORED_DOCUMENT_LIMIT,
    SYNC_STORED_ROW_LIMIT,
    count_new_active_documents,
    count_new_document_ids,
    estimate_document_row_bytes,
    exceeds_stored_document_quota,
    exceeds_stored_row_quota,
    normalize_push_documents,
    utf8_bytes,
    validate_push_payload,
)
from doocs_md_py.server.types import SyncDocument


def doc(overrides=None) -> dict:
    base = {
        "id": "doc-1",
        "title": "Hello",
        "content": "# hi",
        "parentId": None,
        "history": [],
        "createDatetime": 1,
        "updateDatetime": 2,
        "deleted": False,
    }
    if overrides:
        base.update(overrides)
    return base


def setting(overrides=None) -> dict:
    base = {"key": "theme", "value": "default", "updatedAt": 1}
    if overrides:
        base.update(overrides)
    return base


def _typed(d: dict) -> SyncDocument:
    return SyncDocument.from_api_dict(d)


# ---- 基本通过 ----


def test_empty_push_accepted():
    assert validate_push_payload([], []) is None


def test_valid_payload_accepted():
    assert validate_push_payload([doc()], [setting()]) is None


def test_utf8_bytes_multibyte():
    assert utf8_bytes("你好") == 6
    assert utf8_bytes("abc") == 3


# ---- 批次数量 ----


def test_too_many_documents():
    documents = [doc({"id": f"d-{i}"}) for i in range(L["maxDocumentsPerPush"] + 1)]
    result = validate_push_payload(documents, [])
    assert result == {"error": "too_many_documents", "status": 413,
                      "field": "documents", "max": 100}


def test_too_many_settings():
    settings = [setting({"key": f"k-{i}"}) for i in range(L["maxSettingsPerPush"] + 1)]
    result = validate_push_payload([], settings)
    assert result["error"] == "too_many_settings"
    assert result["status"] == 413
    assert result["max"] == 80


# ---- 尺寸 ----


def test_oversize_content():
    content = "x" * (L["maxContentBytes"] + 1)
    result = validate_push_payload([doc({"content": content})], [])
    assert result == {"error": "content_too_large", "status": 413,
                      "field": "documents.content", "max": L["maxContentBytes"]}


def test_oversize_title_by_utf8_bytes():
    title = "你" * L["maxTitleBytes"]  # 500 字符但 1500 字节
    result = validate_push_payload([doc({"title": title})], [])
    assert result["error"] == "title_too_large"
    assert utf8_bytes(title) > L["maxTitleBytes"]


def test_document_row_cap():
    block = "x" * L["maxHistoryContentBytes"]
    history = [{"datetime": i, "content": block} for i in range(4)]
    result = validate_push_payload([doc({"content": block, "history": history})], [])
    assert result == {"error": "document_too_large", "status": 413,
                      "field": "documents", "max": L["maxDocumentRowBytes"]}


# ---- 结构非法 ----


def test_malformed_documents():
    assert validate_push_payload([{"id": "x"}], [])["error"] == "invalid_document"
    assert validate_push_payload([doc({"id": ""})], [])["error"] == "invalid_document_id"
    assert validate_push_payload([doc({"deleted": "no"})], [])["error"] == "invalid_document"
    # 墓碑是合法文档（内容可为空）
    tombstone = doc({"deleted": True, "title": "", "content": ""})
    assert validate_push_payload([tombstone], []) is None
    assert validate_push_payload([doc({"history": "oops"})], [])["error"] == "invalid_history"
    long_parent = "x" * (L["maxIdChars"] + 1)
    assert (
        validate_push_payload([doc({"parentId": long_parent})], [])["error"]
        == "invalid_document_parent_id"
    )
    assert validate_push_payload([doc({"parentId": ""})], [])["error"] == \
        "invalid_document_parent_id"
    assert (
        validate_push_payload([doc({"createDatetime": "nope"})], [])["field"]
        == "documents.createDatetime"
    )
    assert (
        validate_push_payload([doc({"updateDatetime": float("nan")})], [])["field"]
        == "documents.updateDatetime"
    )
    assert validate_push_payload({}, [])["error"] == "invalid_body"
    assert validate_push_payload([], {})["error"] == "invalid_body"


def test_boolean_is_not_finite_number():
    # Python bool 是 int 子类；JS typeof boolean !== number，必须拒绝
    assert validate_push_payload([doc({"createDatetime": True})], [])["field"] == \
        "documents.createDatetime"
    assert validate_push_payload([], [setting({"updatedAt": False})])["field"] == \
        "settings.updatedAt"


def test_float_timestamps_accepted():
    assert validate_push_payload([doc({"createDatetime": 1.5})], []) is None


def test_null_history_accepted():
    assert validate_push_payload([doc({"history": None})], []) is None


def test_history_item_must_be_object():
    result = validate_push_payload([doc({"history": [5]})], [])
    assert result["error"] == "invalid_history"
    result = validate_push_payload([doc({"history": [None]})], [])
    assert result["error"] == "invalid_history"


def test_history_string_datetime_accepted():
    payload = doc({"history": [{"datetime": "2026-01-01", "content": "x"}]})
    assert validate_push_payload([payload], []) is None


# ---- history ----


def test_history_too_long():
    history = [{"datetime": i, "content": f"n{i}"}
               for i in range(L["maxHistoryItems"] + 1)]
    assert validate_push_payload([doc({"history": history})], [])["error"] == \
        "history_too_long"


def test_history_content_too_large():
    huge = {"datetime": 1, "content": "y" * (L["maxHistoryContentBytes"] + 1)}
    result = validate_push_payload([doc({"history": [huge]})], [])
    assert result["error"] == "history_content_too_large"


# ---- settings ----


def test_invalid_settings():
    assert validate_push_payload([], [setting({"key": ""})])["error"] == \
        "invalid_setting_key"
    long_key = "k" * (L["maxSettingKeyChars"] + 1)
    assert validate_push_payload([], [setting({"key": long_key})])["error"] == \
        "invalid_setting_key"
    assert validate_push_payload([], [setting({"value": 1})])["error"] == \
        "invalid_setting"
    value = "z" * (L["maxSettingValueBytes"] + 1)
    result = validate_push_payload([], [setting({"value": value})])
    assert result["error"] == "setting_value_too_large"
    assert result["max"] == L["maxSettingValueBytes"]


def test_null_setting_value_accepted():
    assert validate_push_payload([], [setting({"value": None})]) is None


# ---- 整包字节 ----


def test_payload_too_large_aggregate():
    # 单文档均未超 content(512KiB)/row(1.8MB) 上限，但整包超过 8MiB：
    # 17 × 500000 = 8.5MB
    big = "x" * 500_000
    documents = [doc({"id": f"d-{i}", "content": big}) for i in range(17)]
    result = validate_push_payload(documents, [])
    assert result == {"error": "payload_too_large", "status": 413,
                      "field": "body", "max": L["maxRequestBytes"]}


def test_estimate_row_bytes_non_string_fields_count_zero():
    size = estimate_document_row_bytes(
        {"id": "ab", "title": None, "content": 1, "parentId": ["x"], "history": "no"}
    )
    # id=2 + 空 history 序列化 "[]"=2
    assert size == utf8_bytes("ab") + utf8_bytes("[]")


# ---- 存量配额计数 ----


def test_quota_allows_updates_at_cap():
    assert exceeds_stored_document_quota(
        "free", SYNC_STORED_DOCUMENT_LIMIT["free"], 0
    ) is False
    assert count_new_active_documents([_typed(doc({"id": "existing"}))],
                                      {"existing": False}) == 0


def test_quota_blocks_past_cap():
    assert exceeds_stored_document_quota(
        "free", SYNC_STORED_DOCUMENT_LIMIT["free"], 1
    ) is True
    assert exceeds_stored_document_quota(
        "pro", SYNC_STORED_DOCUMENT_LIMIT["pro"] - 1, 1
    ) is False
    assert count_new_active_documents(
        [_typed(doc({"id": "new-1"})), _typed(doc({"id": "new-2", "deleted": True}))],
        {},
    ) == 1


def test_resurrected_tombstone_counts_as_new_active():
    assert count_new_active_documents(
        [_typed(doc({"id": "was-deleted"}))], {"was-deleted": True}
    ) == 1
    assert count_new_active_documents(
        [_typed(doc({"id": "was-deleted"})), _typed(doc({"id": "was-deleted"}))],
        {"was-deleted": True},
    ) == 1


def test_unknown_tombstone_counts_toward_row_cap():
    assert exceeds_stored_row_quota("free", SYNC_STORED_ROW_LIMIT["free"], 0) is False
    assert exceeds_stored_row_quota("free", SYNC_STORED_ROW_LIMIT["free"], 1) is True
    assert count_new_document_ids(
        [_typed(doc({"id": "existing"})), _typed(doc({"id": "tomb", "deleted": True}))],
        {"existing": False},
    ) == 1


def test_new_counts_zero_never_blocks():
    assert exceeds_stored_document_quota("free", 999_999, 0) is False
    assert exceeds_stored_row_quota("free", 999_999, 0) is False


# ---- normalize ----


def test_normalize_strips_tombstones():
    tomb, live = normalize_push_documents([
        _typed(doc({"id": "gone", "deleted": True, "title": "x", "content": "huge",
                    "history": [{"datetime": 1, "content": "h"}]})),
        _typed(doc({"id": "live", "content": "keep"})),
    ])
    assert tomb.id == "gone"
    assert tomb.deleted is True
    assert tomb.title == ""
    assert tomb.content == ""
    assert tomb.history == []
    assert live.content == "keep"


def test_plan_limit_constants():
    assert SYNC_STORED_DOCUMENT_LIMIT == {"free": 200, "pro": 2000}
    assert SYNC_STORED_ROW_LIMIT == {"free": 400, "pro": 4000}
    assert L["maxContentBytes"] == 512 * 1024
    assert math.isfinite(L["maxRequestBytes"])
