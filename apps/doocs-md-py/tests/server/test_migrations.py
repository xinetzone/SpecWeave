"""TR-3.1：8 个上游迁移的 schema/索引/CHECK/种子/幂等逐项断言。"""

import sqlite3

import pytest

from doocs_md_py.server import db

EXPECTED_TABLES = {
    "users",
    "documents",
    "settings",
    "afdian_orders",
    "sync_rate_limits",
    "shares",
    "share_rate_limits",
    "marketplace_items",
    "marketplace_rate_limits",
    "notifications",
    "emoji_packs",
    "emoji_items",
    "_migrations",
}

EXPECTED_INDEXES = {
    "idx_documents_cursor",
    "idx_settings_cursor",
    "idx_afdian_orders_user",
    "idx_shares_user_post",
    "idx_shares_expires",
    "idx_mp_type_status",
    "idx_mp_author",
    "idx_notifications_user_created",
    "idx_notifications_user_unread",
    "idx_emoji_items_pack_sort",
}


def _table_names(conn):
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return {r[0] for r in rows}


def _index_names(conn):
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return {r[0] for r in rows}


def _column_names(conn, table):
    return {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def test_all_tables_created(conn):
    assert _table_names(conn) == EXPECTED_TABLES


def test_all_explicit_indexes_created(conn):
    assert EXPECTED_INDEXES <= _index_names(conn)


def test_user_plan_columns_from_0002(conn):
    cols = {r[1]: r for r in conn.execute("PRAGMA table_info(users)").fetchall()}
    assert "plan" in cols and "plan_expires_at" in cols
    # plan 默认 free、NOT NULL
    plan_row = cols["plan"]
    assert plan_row[3] == 1  # notnull
    assert plan_row[4] == "'free'"  # dflt_value


def test_marketplace_sample_markdown_from_0005(conn):
    assert "sample_markdown" in _column_names(conn, "marketplace_items")


def test_documents_required_columns(conn):
    cols = _column_names(conn, "documents")
    assert {
        "user_id", "id", "title", "content", "parent_id", "history",
        "create_datetime", "update_datetime", "deleted", "server_updated_at",
    } <= cols


def test_system_default_pack_seeded(conn):
    row = conn.execute(
        "SELECT id, owner_user_id, kind, slug, name, created_at, updated_at"
        " FROM emoji_packs WHERE id = 'system-default'"
    ).fetchone()
    assert row is not None
    assert row["kind"] == "system"
    assert row["owner_user_id"] is None
    assert row["slug"] == "default"
    assert row["name"] == "Built-in"
    # 种子时间戳字面量必须与上游一致（0007/0008）
    assert row["created_at"] == 1785547610000
    assert row["updated_at"] == 1785547610000


def test_no_legacy_coolapk_pack(conn):
    # 0008 迁移清除旧种子
    assert conn.execute(
        "SELECT COUNT(*) FROM emoji_packs WHERE id = 'system-coolapk'"
    ).fetchone()[0] == 0


def test_migrations_idempotent(conn):
    # 再次应用：无新增、无报错
    assert db.apply_migrations(conn) == []
    registered = [r[0] for r in conn.execute("SELECT id FROM _migrations ORDER BY id")]
    assert registered == [1, 2, 3, 4, 5, 6, 7, 8]


def test_migration_0008_runs_after_0007_ordering(conn):
    # _migrations 中 0008 的时间必须晚于 0007（应用顺序证据）
    t7 = conn.execute("SELECT applied_at FROM _migrations WHERE id=7").fetchone()[0]
    t8 = conn.execute("SELECT applied_at FROM _migrations WHERE id=8").fetchone()[0]
    assert t8 >= t7


def test_check_kind_rejects_unknown(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO emoji_packs (id, owner_user_id, kind, slug, name, created_at, updated_at)"
            " VALUES ('bad', NULL, 'weird', 's1', 'N', 1, 1)"
        )


def test_check_pack_owner_exclusivity_system(conn):
    # system 包不允许 owner
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO emoji_packs (id, owner_user_id, kind, slug, name, created_at, updated_at)"
            " VALUES ('bad-sys', 'user-001', 'system', 's2', 'N', 1, 1)"
        )


def test_check_pack_owner_exclusivity_user(conn, user_id):
    # user 包必须有 owner
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO emoji_packs (id, owner_user_id, kind, slug, name, created_at, updated_at)"
            " VALUES ('bad-user', NULL, 'user', 's3', 'N', 1, 1)"
        )


def test_check_emoji_item_size_positive(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO emoji_items (id, pack_id, object_key, name, mime, size, created_at, updated_at)"
            " VALUES ('ei1', 'system-default', 'k/x.png', 'x', 'image/png', 0, 1, 1)"
        )


def test_foreign_key_cascade_enabled(conn, user_id):
    # 建一个 user pack，级联依赖 PRAGMA foreign_keys=ON
    conn.execute(
        "INSERT INTO emoji_packs (id, owner_user_id, kind, slug, name, created_at, updated_at)"
        " VALUES ('up1', ?, 'user', 'u-slug', 'U', 1, 1)",
        (user_id,),
    )
    conn.execute(
        "INSERT INTO emoji_items (id, pack_id, object_key, name, mime, size, created_at, updated_at)"
        " VALUES ('ei', 'up1', 'user/u.png', 'x', 'image/png', 10, 1, 1)"
    )
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    assert conn.execute("SELECT COUNT(*) FROM emoji_items WHERE pack_id='up1'").fetchone()[0] == 0


def test_file_based_db_migrations(tmp_path):
    path = tmp_path / "test.db"
    connection = db.connect(path)
    applied = db.apply_migrations(connection)
    assert applied == [1, 2, 3, 4, 5, 6, 7, 8]
    connection.close()
    # 重开库：迁移已持久化，无需重放
    connection2 = db.connect(path)
    assert db.apply_migrations(connection2) == []
    assert "documents" in _table_names(connection2)
    connection2.close()
