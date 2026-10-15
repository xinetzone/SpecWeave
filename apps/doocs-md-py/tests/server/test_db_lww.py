"""TR-3.2：db.ts LWW / 游标 / 回拉 / 墓碑 / 设置编解码怪癖的场景化测试。"""

from doocs_md_py.server import db
from doocs_md_py.server.types import SyncDocument, SyncSetting


def doc(
    doc_id="d1",
    title="标题",
    content="正文",
    parent_id=None,
    history=None,
    created=100,
    updated=100,
    deleted=False,
):
    return SyncDocument(
        id=doc_id,
        title=title,
        content=content,
        parent_id=parent_id,
        history=history or [],
        create_datetime=created,
        update_datetime=updated,
        deleted=deleted,
    )


def setting(key, value, updated_at):
    return SyncSetting(key=key, value=value, updated_at=updated_at)


# ---- 用户 upsert（upstream: db.ts:59-78）----


def test_upsert_user_inserts_then_updates(conn):
    db.upsert_user(conn, {
        "id": "u1", "github_id": 42, "login": "old", "name": "Old", "avatar": None,
    })
    row = db.get_user_by_id(conn, "u1")
    assert row is not None and row.login == "old" and row.plan == "free"
    created_at = row.created_at

    # github_id 冲突：更新资料但保留 id 与 created_at
    db.upsert_user(conn, {
        "id": "u1", "github_id": 42, "login": "new", "name": "New", "avatar": "a.png",
    })
    assert db.get_user_by_id(conn, "u1").login == "new"
    assert db.get_user_by_id(conn, "u1").created_at == created_at
    # 只有一个用户行
    assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1


def test_get_user_missing_returns_none(conn):
    assert db.get_user_by_id(conn, "nope") is None


# ---- 分块（upstream: db.ts:96-105）----


def test_chunk_ids_dedup_preserve_order():
    ids = ["a", "b", "a", "c", "b"]
    assert db.chunk_document_ids(ids) == [["a", "b", "c"]]


def test_chunk_ids_99_boundary():
    ids = [f"id{i}" for i in range(200)]
    chunks = db.chunk_document_ids(ids)
    assert [len(c) for c in chunks] == [99, 99, 2]
    assert chunks[0][0] == "id0"
    assert chunks[2][-1] == "id199"


def test_list_existing_empty(conn, user_id):
    assert db.list_existing_documents(conn, user_id, []) == {}
    assert db.list_existing_documents(conn, user_id, ["x"]) == {}


def test_list_existing_reports_deleted(conn, user_id):
    result = db.push_changes(
        conn, user_id, [doc("a"), doc("b", updated=50, deleted=True)], [], clock=lambda: 1000
    )
    assert result["max_cursor"] == 1000
    existing = db.list_existing_documents(conn, user_id, ["a", "b", "c"])
    assert existing == {"a": False, "b": True}


# ---- push/pull 与游标（upstream: db.ts:131-246）----


def test_push_then_pull_roundtrip(conn, user_id):
    result = db.push_changes(conn, user_id, [doc()], [], clock=lambda: 1000)
    docs = result["documents"]
    assert len(docs) == 1
    assert docs[0].id == "d1"
    assert docs[0].to_api_dict()["parentId"] is None
    # 用新游标再拉为空（严格 >）
    pulled = db.pull_changes(conn, user_id, result["max_cursor"])
    assert pulled["documents"] == []
    assert pulled["max_cursor"] == 1000


def test_pull_from_zero_returns_all(conn, user_id):
    db.push_changes(conn, user_id, [doc("a"), doc("b")], [], clock=lambda: 2000)
    pulled = db.pull_changes(conn, user_id, 0)
    assert {d.id for d in pulled["documents"]} == {"a", "b"}
    assert pulled["max_cursor"] == 2000


def test_lww_rejects_older_client_version(conn, user_id):
    db.push_changes(conn, user_id, [doc(updated=100, title="new")], [], clock=lambda: 1000)
    # 更旧的客户端版本：整行被跳过 → 本批无写入 → 回拉为空（服务端既有值
    # 由同步协议 push 前的 pull 获得，见 db.ts:243 注释）
    result = db.push_changes(
        conn, user_id, [doc(updated=90, title="old-stale")], [], clock=lambda: 2000
    )
    assert result["documents"] == []
    assert result["max_cursor"] == 2000
    # 库内未被污染
    row = conn.execute("SELECT title, server_updated_at FROM documents WHERE id='d1'").fetchone()
    assert row["title"] == "new"
    assert row["server_updated_at"] == 1000


def test_lww_equal_timestamp_rejected(conn, user_id):
    # upstream: existing.update_datetime >= client（相等也拒绝）
    db.push_changes(conn, user_id, [doc(updated=100, title="first")], [], clock=lambda: 1000)
    result = db.push_changes(
        conn, user_id, [doc(updated=100, title="equal")], [], clock=lambda: 2000
    )
    assert result["documents"] == []
    assert conn.execute("SELECT title FROM documents WHERE id='d1'").fetchone()["title"] == "first"


def test_newer_client_version_overwrites(conn, user_id):
    db.push_changes(conn, user_id, [doc(updated=100, title="v1")], [], clock=lambda: 1000)
    result = db.push_changes(
        conn, user_id, [doc(updated=200, title="v2", content="新正文")], [], clock=lambda: 3000
    )
    assert result["documents"][0].title == "v2"
    pulled = db.pull_changes(conn, user_id, 1000)
    assert len(pulled["documents"]) == 1
    assert pulled["documents"][0].content == "新正文"


def test_sync_protocol_pull_before_push_protects_stale_client(conn, user_id):
    # 设备 A 推 t=100
    db.push_changes(conn, user_id, [doc(updated=100, title="A100")], [], clock=lambda: 1000)
    # 设备 B（同账号另一设备）推 t=200
    db.push_changes(conn, user_id, [doc(updated=200, title="B200")], [], clock=lambda: 2000)
    # 设备 A 同步：协议先 pull（cursor=1000）→ 拿到 B200
    pre_pull = db.pull_changes(conn, user_id, 1000)
    assert pre_pull["documents"][0].title == "B200"
    # A 仍持陈旧 t=150 推送 → LWW 拒绝，本批无写入
    result = db.push_changes(
        conn, user_id, [doc(updated=150, title="A150")], [], clock=lambda: 3000
    )
    assert result["documents"] == []
    # 库内稳定为 B200
    assert conn.execute("SELECT title FROM documents WHERE id='d1'").fetchone()["title"] == "B200"


def test_pullback_includes_just_written_rows(conn, user_id):
    # 回拉 now-1 的意义：本批落库行 server_updated_at=now 必被 pull(now-1) 带回，
    # 且不依赖客户端传入游标
    result = db.push_changes(
        conn, user_id, [doc(updated=100)], [setting("k", "v", 50)], clock=lambda: 2000
    )
    assert result["max_cursor"] == 2000
    assert {d.id for d in result["documents"]} == {"d1"}
    assert result["settings"][0].value == "v"


# ---- 墓碑 ----


def test_tombstone_counts_and_pulls(conn, user_id):
    db.push_changes(
        conn, user_id, [doc("live"), doc("dead", updated=10, deleted=True)], [],
        clock=lambda: 1000,
    )
    assert db.count_active_documents(conn, user_id) == 1
    assert db.count_stored_documents(conn, user_id) == 2
    pulled = db.pull_changes(conn, user_id, 0)
    dead = next(d for d in pulled["documents"] if d.id == "dead")
    assert dead.deleted is True


def test_tombstone_recreation_uses_active_count(conn, user_id):
    db.push_changes(conn, user_id, [doc("x", deleted=True)], [], clock=lambda: 1000)
    # 重新创建（同 id 更新时间更大，deleted=False）
    db.push_changes(conn, user_id, [doc("x", updated=200, deleted=False, title="back")], [],
                    clock=lambda: 2000)
    assert db.count_active_documents(conn, user_id) == 1
    assert db.count_stored_documents(conn, user_id) == 1


# ---- 设置编解码怪癖（upstream: db.ts:42-57, 220-240）----


def test_setting_string_roundtrip(conn, user_id):
    db.push_changes(conn, user_id, [], [setting("MD__theme", "default", 10)], clock=lambda: 1000)
    pulled = db.pull_changes(conn, user_id, 0)
    assert pulled["settings"][0].to_api_dict() == {
        "key": "MD__theme", "value": "default", "updatedAt": 10,
    }


def test_setting_null_roundtrip(conn, user_id):
    db.push_changes(conn, user_id, [], [setting("legend", None, 20)], clock=lambda: 1000)
    raw = conn.execute("SELECT value FROM settings WHERE key='legend'").fetchone()[0]
    assert raw == "null"
    assert db.pull_changes(conn, user_id, 0)["settings"][0].value is None


def test_setting_lww(conn, user_id):
    db.push_changes(conn, user_id, [], [setting("k", "v1", 100)], clock=lambda: 1000)
    result = db.push_changes(conn, user_id, [], [setting("k", "v0", 90)], clock=lambda: 2000)
    # 旧值被拒：本批无写入；库内仍是 v1
    assert result["settings"] == []
    row = conn.execute("SELECT value, updated_at FROM settings WHERE key='k'").fetchone()
    assert row["updated_at"] == 100
    assert db.decode_setting_value(row["value"]) == "v1"


def test_decode_setting_value_quirks():
    # 非字符串 JSON 标量/对象 → 重新序列化字符串
    assert db.decode_setting_value("5") == "5"
    assert db.decode_setting_value("true") == "true"
    assert db.decode_setting_value('{"a":1}') == '{"a":1}'
    assert db.decode_setting_value('["x",2]') == '["x",2]'
    assert db.decode_setting_value('"hello"') == "hello"
    assert db.decode_setting_value("null") is None
    # 坏 JSON → None（等价 catch 分支）
    assert db.decode_setting_value("not-json") is None
    # 非 ASCII 不转义（等价 JS JSON.stringify）
    assert db.decode_setting_value('"中文"') == "中文"


def test_setting_corrupt_db_value_pulls_as_null(conn, user_id):
    db.push_changes(conn, user_id, [], [setting("k", "ok", 10)], clock=lambda: 1000)
    conn.execute("UPDATE settings SET value='broken-json' WHERE user_id=? AND key='k'", (user_id,))
    assert db.pull_changes(conn, user_id, 0)["settings"][0].value is None


# ---- history 怪癖 ----


def test_history_roundtrip_and_corrupt_fallback(conn, user_id):
    from doocs_md_py.server.types import SyncHistoryEntry

    d = doc("h", history=[SyncHistoryEntry(datetime=123, content="v1")])
    db.push_changes(conn, user_id, [d], [], clock=lambda: 1000)
    pulled = db.pull_changes(conn, user_id, 0)
    hist = pulled["documents"][0].history
    assert len(hist) == 1
    assert hist[0].datetime == 123 and hist[0].content == "v1"

    # 损坏的 history JSON 回退 []（直接改库不推进 server_updated_at，故从 0 拉）
    conn.execute("UPDATE documents SET history='not-json' WHERE id='h'")
    corrupt = db.pull_changes(conn, user_id, 0)["documents"][0]
    assert corrupt.history == []


def test_history_legacy_string_datetime_preserved():
    api = {
        "id": "x", "title": "", "content": "", "parentId": None,
        "history": [{"datetime": "2024-01-01", "content": "old"}],
        "createDatetime": 1, "updateDatetime": 1, "deleted": False,
    }
    d = SyncDocument.from_api_dict(api)
    assert d.history[0].datetime == "2024-01-01"
    assert d.to_api_dict()["history"][0]["datetime"] == "2024-01-01"


# ---- 多用户隔离 ----


def test_user_isolation(conn):
    db.upsert_user(conn, {"id": "u2", "github_id": 99, "login": "two", "name": None, "avatar": None})
    db.push_changes(conn, "user-001", [doc("shared-id", title="one")], [], clock=lambda: 1000)
    db.push_changes(conn, "u2", [doc("shared-id", title="two")], [], clock=lambda: 1000)
    p1 = db.pull_changes(conn, "user-001", 0)
    p2 = db.pull_changes(conn, "u2", 0)
    assert p1["documents"][0].title == "one"
    assert p2["documents"][0].title == "two"
