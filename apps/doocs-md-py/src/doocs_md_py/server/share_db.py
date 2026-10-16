"""分享存储与解锁失败计数（upstream: apps/api/src/share-db.ts 1:1）。

- 分享 CRUD：同一 (user_id, post_id) 复用链接（唯一索引 + sha256 派生 id）；
- 解锁限流：scope ``unlock:<shareId>:<ip>`` 存 share_rate_limits 表，
  按 UTC 小时窗（20 次/小时，重试到小时末）；发布限流（日窗）在 ratelimit.py。
"""

import sqlite3
from dataclasses import dataclass

from .ratelimit import utc_hour_key


@dataclass(slots=True)
class ShareRow:
    """upstream: share-types.ts:1-11 ShareRow。"""

    id: str
    post_id: str
    user_id: str
    title: str
    html: str
    password_hash: str | None
    created_at: int
    expires_at: int | None
    view_count: int


@dataclass(slots=True)
class ShareListRow:
    """upstream: share-db.ts:18-26 ShareListRow（不含 html）。"""

    id: str
    post_id: str
    title: str
    password_hash: str | None
    created_at: int
    expires_at: int | None
    view_count: int


def _row_to_share(row: sqlite3.Row) -> ShareRow:
    return ShareRow(
        id=row["id"],
        post_id=row["post_id"],
        user_id=row["user_id"],
        title=row["title"],
        html=row["html"],
        password_hash=row["password_hash"],
        created_at=row["created_at"],
        expires_at=row["expires_at"],
        view_count=row["view_count"],
    )


def _row_to_list(row: sqlite3.Row) -> ShareListRow:
    return ShareListRow(
        id=row["id"],
        post_id=row["post_id"],
        title=row["title"],
        password_hash=row["password_hash"],
        created_at=row["created_at"],
        expires_at=row["expires_at"],
        view_count=row["view_count"],
    )


# upstream: share-db.ts:3-16
def get_share_by_user_and_post_id(
    conn: sqlite3.Connection, user_id: str, post_id: str
) -> ShareRow | None:
    row = conn.execute(
        "SELECT * FROM shares WHERE user_id = ? AND post_id = ?",
        (user_id, post_id),
    ).fetchone()
    return _row_to_share(row) if row is not None else None


def get_share_by_id(conn: sqlite3.Connection, share_id: str) -> ShareRow | None:
    row = conn.execute(
        "SELECT * FROM shares WHERE id = ?", (share_id,)
    ).fetchone()
    return _row_to_share(row) if row is not None else None


# upstream: share-db.ts:28-40
def list_shares_by_user_id(
    conn: sqlite3.Connection, user_id: str
) -> list[ShareListRow]:
    rows = conn.execute(
        """SELECT id, post_id, title, password_hash, created_at, expires_at, view_count
           FROM shares WHERE user_id = ?
           ORDER BY created_at DESC""",
        (user_id,),
    ).fetchall()
    return [_row_to_list(row) for row in rows]


# upstream: share-db.ts:42-53
def delete_share_by_user_and_id(
    conn: sqlite3.Connection, user_id: str, share_id: str
) -> bool:
    cursor = conn.execute(
        "DELETE FROM shares WHERE user_id = ? AND id = ?", (user_id, share_id)
    )
    conn.commit()
    return cursor.rowcount > 0


# upstream: share-db.ts:55-75
def insert_share(
    conn: sqlite3.Connection,
    *,
    share_id: str,
    post_id: str,
    user_id: str,
    title: str,
    html: str,
    password_hash: str | None,
    created_at: int,
    expires_at: int | None,
) -> None:
    conn.execute(
        """INSERT INTO shares
             (id, post_id, user_id, title, html, password_hash,
              created_at, expires_at, view_count)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)""",
        (
            share_id, post_id, user_id, title, html, password_hash,
            created_at, expires_at,
        ),
    )
    conn.commit()


# upstream: share-db.ts:77-98
def update_share_content(
    conn: sqlite3.Connection,
    *,
    user_id: str,
    post_id: str,
    title: str,
    html: str,
    password_hash: str | None,
    expires_at: int | None,
) -> bool:
    cursor = conn.execute(
        """UPDATE shares
           SET title = ?, html = ?, password_hash = ?, expires_at = ?
           WHERE user_id = ? AND post_id = ?""",
        (title, html, password_hash, expires_at, user_id, post_id),
    )
    conn.commit()
    return cursor.rowcount > 0


# upstream: share-db.ts:100-107
def increment_share_view_count(conn: sqlite3.Connection, share_id: str) -> int:
    conn.execute(
        "UPDATE shares SET view_count = view_count + 1 WHERE id = ?",
        (share_id,),
    )
    conn.commit()
    row = conn.execute(
        "SELECT view_count FROM shares WHERE id = ?", (share_id,)
    ).fetchone()
    return int(row["view_count"]) if row is not None else 1


# ---- 解锁失败小时窗（upstream: share-db.ts:109-144）----


def get_share_rate_limit_count(
    conn: sqlite3.Connection, scope_key: str, *, now=None
) -> int:
    """upstream: share-db.ts:109-120；当前 UTC 小时窗内失败次数。"""
    row = conn.execute(
        "SELECT count FROM share_rate_limits WHERE scope_key = ? AND hour_key = ?",
        (scope_key, utc_hour_key(now)),
    ).fetchone()
    return int(row["count"]) if row is not None else 0


def increment_share_rate_limit(
    conn: sqlite3.Connection, scope_key: str, *, now=None
) -> None:
    """upstream: share-db.ts:122-134。"""
    conn.execute(
        """INSERT INTO share_rate_limits (scope_key, hour_key, count)
           VALUES (?, ?, 1)
           ON CONFLICT(scope_key, hour_key) DO UPDATE SET count = count + 1""",
        (scope_key, utc_hour_key(now)),
    )
    conn.commit()
