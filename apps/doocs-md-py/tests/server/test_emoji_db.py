"""TR-16.1 之二：emoji_db 条件插入上限、排序与级联删除（对齐 emoji-db.test.ts）。"""

import pytest

from doocs_md_py.server import emoji_db
from doocs_md_py.server.emoji_validate import EMOJI_MAX_ITEMS


def test_system_pack_seeded(conn):
    pack = emoji_db.get_system_pack(conn)
    assert pack is not None
    assert pack["slug"] == "default"
    assert pack["kind"] == "system"
    assert pack["owner_user_id"] is None
    assert emoji_db.get_pack_by_slug(conn, "default")["id"] == pack["id"]


def test_get_or_create_user_pack_idempotent(conn, user_id):
    first = emoji_db.get_or_create_user_pack(conn, user_id, 1000)
    assert first["slug"] == f"user-{user_id}"
    assert first["name"] == "My Emojis"
    second = emoji_db.get_or_create_user_pack(conn, user_id, 2000)
    assert second["id"] == first["id"]
    assert second["created_at"] == 1000  # 已存在不覆盖


def _insert(conn, user_id, seq, *, item_id=None, name="e"):
    item_id = item_id or f"item-{seq}"
    return emoji_db.insert_user_emoji_item_conditional(
        conn,
        item_id=item_id,
        user_id=user_id,
        object_key=f"user/{user_id}/{item_id}.png",
        name=name,
        mime="image/png",
        size=10 + seq,
        created_at=1000 + seq,
    )


def test_conditional_insert_sort_order(conn, user_id):
    emoji_db.get_or_create_user_pack(conn, user_id, 1)
    assert _insert(conn, user_id, 1) is True
    assert _insert(conn, user_id, 2) is True
    pack = emoji_db.get_or_create_user_pack(conn, user_id, 1)
    items = emoji_db.list_pack_items(conn, pack["id"])
    assert [i["sort_order"] for i in items] == [0, 1]
    assert [i["id"] for i in items] == ["item-1", "item-2"]
    # created_at 与 updated_at 同值
    assert items[0]["created_at"] == items[0]["updated_at"] == 1001


def test_insert_without_pack_returns_false(conn, user_id):
    # 用户包不存在（无 SELECT 行）→ 插入 0 行
    assert _insert(conn, user_id, 1) is False


def test_item_cap_rejects_101st_and_rolls_back_nothing(conn, user_id):
    emoji_db.get_or_create_user_pack(conn, user_id, 1)
    for seq in range(1, EMOJI_MAX_ITEMS + 1):
        assert _insert(conn, user_id, seq) is True
    rejected = _insert(conn, user_id, EMOJI_MAX_ITEMS + 1, item_id="overflow")
    assert rejected is False
    pack = emoji_db.get_or_create_user_pack(conn, user_id, 1)
    items = emoji_db.list_pack_items(conn, pack["id"])
    assert len(items) == EMOJI_MAX_ITEMS
    assert emoji_db.get_emoji_asset(conn, "overflow") is None
    # JOIN 带出 system/user kind
    assert emoji_db.get_emoji_asset(conn, "item-1")["kind"] == "user"


def test_owned_lookup_and_delete(conn, user_id):
    emoji_db.get_or_create_user_pack(conn, user_id, 1)
    _insert(conn, user_id, 1)
    item = emoji_db.get_owned_emoji_item(conn, user_id, "item-1")
    assert item is not None and item["object_key"].endswith("item-1.png")
    assert emoji_db.get_owned_emoji_item(conn, "someone-else", "item-1") is None
    assert emoji_db.delete_owned_emoji_item(conn, "someone-else", "item-1") is False
    assert emoji_db.delete_owned_emoji_item(conn, user_id, "item-1") is True
    assert emoji_db.delete_owned_emoji_item(conn, user_id, "item-1") is False


def test_update_pack_name(conn, user_id):
    emoji_db.get_or_create_user_pack(conn, user_id, 1)
    emoji_db.update_user_pack_name(conn, user_id, "Custom", 9999)
    pack = emoji_db.get_or_create_user_pack(conn, user_id, 1)
    assert pack["name"] == "Custom"
    assert pack["updated_at"] == 9999


def test_delete_user_pack_removes_items(conn, user_id):
    emoji_db.get_or_create_user_pack(conn, user_id, 1)
    _insert(conn, user_id, 1)
    _insert(conn, user_id, 2)
    emoji_db.delete_user_pack(conn, user_id)
    # 无包时静默
    emoji_db.delete_user_pack(conn, user_id)
    new_pack = emoji_db.get_or_create_user_pack(conn, user_id, 2)
    assert emoji_db.list_pack_items(conn, new_pack["id"]) == []
    assert new_pack["slug"] == f"user-{user_id}"  # slug 复用，行重新创建


def test_insert_requires_real_pack_foreign_key(conn):
    # 直插伪造的 pack_id 受外键约束（PRAGMA foreign_keys=ON）
    with pytest.raises(Exception):  # noqa: PT011, B017
        conn.execute(
            "INSERT INTO emoji_items (id, pack_id, object_key, name, mime, size,"
            " created_at, updated_at) VALUES ('x', 'no-such-pack', 'k', 'n',"
            " 'image/png', 1, 1, 1)"
        )
