"""表情包数据层（upstream: apps/api/src/emoji-db.ts 1:1）。

- 系统包单例（kind='system' 最早一条）；每用户至多一个用户包
  （emoji_packs.owner_user_id UNIQUE），slug 形如 ``user-<id>``；
- 表情项上限在单条条件 INSERT...HAVING COUNT 中判定（并发安全），
  sort_order 取当前最大 + 1（COALESCE(MAX,-1)+1，首项为 0）；
- 删包显式先删子项再删包（不依赖外键级联）。
"""

import sqlite3
import uuid

from .emoji_validate import EMOJI_MAX_ITEMS

USER_PACK_NAME = "My Emojis"
USER_SLUG_PREFIX = "user-"


def get_pack_by_slug(conn: sqlite3.Connection, slug: str) -> sqlite3.Row | None:
    """upstream: emoji-db.ts:38-43。"""
    return conn.execute("SELECT * FROM emoji_packs WHERE slug = ?", (slug,)).fetchone()


def get_system_pack(conn: sqlite3.Connection) -> sqlite3.Row | None:
    """upstream: emoji-db.ts:45-49。"""
    return conn.execute(
        "SELECT * FROM emoji_packs WHERE kind = 'system' ORDER BY created_at ASC LIMIT 1"
    ).fetchone()


def get_or_create_user_pack(
    conn: sqlite3.Connection, user_id: str, now: int
) -> sqlite3.Row:
    """upstream: emoji-db.ts:51-73；ON CONFLICT DO NOTHING 后回读。"""
    conn.execute(
        """INSERT INTO emoji_packs (
             id, owner_user_id, kind, slug, name, created_at, updated_at
           ) VALUES (?, ?, 'user', ?, ?, ?, ?)
           ON CONFLICT(owner_user_id) DO NOTHING""",
        (str(uuid.uuid4()), user_id, f"{USER_SLUG_PREFIX}{user_id}", USER_PACK_NAME, now, now),
    )
    conn.commit()
    pack = conn.execute(
        "SELECT * FROM emoji_packs WHERE owner_user_id = ?", (user_id,)
    ).fetchone()
    if pack is None:
        raise RuntimeError("emoji_pack_create_failed")
    return pack


def list_pack_items(conn: sqlite3.Connection, pack_id: str) -> list[sqlite3.Row]:
    """upstream: emoji-db.ts:75-85；sort_order ASC, id ASC。"""
    rows = conn.execute(
        """SELECT * FROM emoji_items
           WHERE pack_id = ?
           ORDER BY sort_order ASC, id ASC""",
        (pack_id,),
    ).fetchall()
    return list(rows)


def update_user_pack_name(
    conn: sqlite3.Connection, user_id: str, name: str, updated_at: int
) -> None:
    """upstream: emoji-db.ts:87-97。"""
    conn.execute(
        "UPDATE emoji_packs SET name = ?, updated_at = ? WHERE owner_user_id = ?",
        (name, updated_at, user_id),
    )
    conn.commit()


def insert_user_emoji_item_conditional(
    conn: sqlite3.Connection,
    *,
    item_id: str,
    user_id: str,
    object_key: str,
    name: str,
    mime: str,
    size: int,
    created_at: int,
) -> bool:
    """upstream: emoji-db.ts:99-139；单条条件 INSERT 串行化上限判定。

    用户包不存在或已达 EMOJI_MAX_ITEMS 时插入 0 行，返回 False。
    """
    cursor = conn.execute(
        """INSERT INTO emoji_items (
             id, pack_id, object_key, name, mime, size, width, height,
             sort_order, created_at, updated_at
           )
           SELECT ?, p.id, ?, ?, ?, ?, NULL, NULL,
                  COALESCE(MAX(i.sort_order), -1) + 1, ?, ?
           FROM emoji_packs p
           LEFT JOIN emoji_items i ON i.pack_id = p.id
           WHERE p.owner_user_id = ?
           GROUP BY p.id
           HAVING COUNT(i.id) < ?""",
        (
            item_id,
            object_key,
            name,
            mime,
            size,
            created_at,
            created_at,
            user_id,
            EMOJI_MAX_ITEMS,
        ),
    )
    conn.commit()
    return cursor.rowcount == 1


def get_emoji_asset(conn: sqlite3.Connection, item_id: str) -> sqlite3.Row | None:
    """upstream: emoji-db.ts:141-151；JOIN 带出 pack kind（缓存策略用）。"""
    return conn.execute(
        """SELECT i.*, p.kind
           FROM emoji_items i
           JOIN emoji_packs p ON p.id = i.pack_id
           WHERE i.id = ?""",
        (item_id,),
    ).fetchone()


def get_owned_emoji_item(
    conn: sqlite3.Connection, user_id: str, item_id: str
) -> sqlite3.Row | None:
    """upstream: emoji-db.ts:153-167。"""
    return conn.execute(
        """SELECT i.*
           FROM emoji_items i
           JOIN emoji_packs p ON p.id = i.pack_id
           WHERE i.id = ? AND p.owner_user_id = ?""",
        (item_id, user_id),
    ).fetchone()


def delete_owned_emoji_item(
    conn: sqlite3.Connection, user_id: str, item_id: str
) -> bool:
    """upstream: emoji-db.ts:169-184。"""
    cursor = conn.execute(
        """DELETE FROM emoji_items
           WHERE id = ? AND pack_id = (
             SELECT id FROM emoji_packs WHERE owner_user_id = ?
           )""",
        (item_id, user_id),
    )
    conn.commit()
    return cursor.rowcount == 1


def delete_user_pack(conn: sqlite3.Connection, user_id: str) -> None:
    """upstream: emoji-db.ts:186-198；无包静默返回，有包原子删子项+包。"""
    pack = conn.execute(
        "SELECT id FROM emoji_packs WHERE owner_user_id = ?", (user_id,)
    ).fetchone()
    if pack is None:
        return
    with conn:
        conn.execute("DELETE FROM emoji_items WHERE pack_id = ?", (pack["id"],))
        conn.execute(
            "DELETE FROM emoji_packs WHERE id = ? AND owner_user_id = ?",
            (pack["id"], user_id),
        )
