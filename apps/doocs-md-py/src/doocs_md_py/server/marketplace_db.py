"""市场条目数据层（upstream: apps/api/src/marketplace-db.ts 1:1）。

行存储 snake_case，输出 summary/detail 转 camelCase；发布限流复用
``ratelimit.consume_marketplace_publish_rate_limit``（T11 脚手架，不重复实现）。
"""

import sqlite3
from typing import Any

# upstream: marketplace-db.ts:53-60
AUTHOR_JOIN = """
  SELECT m.*,
         u.login AS author_login,
         u.name AS author_name,
         u.avatar AS author_avatar
  FROM marketplace_items m
  JOIN users u ON u.id = m.author_id
"""


def _author_from_row(row: sqlite3.Row) -> dict:
    # upstream: marketplace-db.ts:16-23
    return {
        "id": row["author_id"],
        "login": row["author_login"],
        "name": row["author_name"],
        "avatar": row["author_avatar"],
    }


def row_to_summary(row: sqlite3.Row, include_reject_reason: bool = False) -> dict:
    """upstream: marketplace-db.ts:25-43；rejectReason 仅作者/管理员视角出现。"""
    result: dict[str, Any] = {
        "id": row["id"],
        "type": row["type"],
        "slug": row["slug"],
        "name": row["name"],
        "description": row["description"],
        "version": row["version"],
        "coverUrl": row["cover_url"],
        "primaryColor": row["primary_color"],
        "status": row["status"],
        "downloadCount": row["download_count"],
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
        "publishedAt": row["published_at"],
        "author": _author_from_row(row),
    }
    if include_reject_reason:
        result["rejectReason"] = row["reject_reason"]
    return result


def row_to_detail(row: sqlite3.Row, include_reject_reason: bool = False) -> dict:
    """upstream: marketplace-db.ts:45-51。"""
    result = row_to_summary(row, include_reject_reason)
    result["payload"] = row["payload"]
    result["sampleMarkdown"] = row["sample_markdown"] if row["sample_markdown"] is not None else None
    return result


def get_marketplace_item_by_id(
    conn: sqlite3.Connection, item_id: str
) -> sqlite3.Row | None:
    """upstream: marketplace-db.ts:62-70。"""
    return conn.execute(f"{AUTHOR_JOIN} WHERE m.id = ?", (item_id,)).fetchone()


def list_approved_items(
    conn: sqlite3.Connection,
    *,
    item_type: str,
    q: str | None,
    sort: str,
    page: int,
    page_size: int,
) -> tuple[list[sqlite3.Row], int]:
    """upstream: marketplace-db.ts:72-131；popular/newest 双排序 + q LIKE。"""
    offset = (page - 1) * page_size
    order_by = (
        "m.download_count DESC, m.published_at DESC"
        if sort == "popular"
        else "m.published_at DESC, m.updated_at DESC"
    )

    if q:
        like = f"%{q}%"
        total_row = conn.execute(
            """SELECT COUNT(*) AS total FROM marketplace_items m
               WHERE m.type = ? AND m.status = 'approved'
                 AND (m.name LIKE ? OR m.description LIKE ? OR m.slug LIKE ?)""",
            (item_type, like, like, like),
        ).fetchone()
        rows = conn.execute(
            f"""{AUTHOR_JOIN}
               WHERE m.type = ? AND m.status = 'approved'
                 AND (m.name LIKE ? OR m.description LIKE ? OR m.slug LIKE ?)
               ORDER BY {order_by}
               LIMIT ? OFFSET ?""",
            (item_type, like, like, like, page_size, offset),
        ).fetchall()
    else:
        total_row = conn.execute(
            "SELECT COUNT(*) AS total FROM marketplace_items WHERE type = ? AND status = 'approved'",
            (item_type,),
        ).fetchone()
        rows = conn.execute(
            f"""{AUTHOR_JOIN}
               WHERE m.type = ? AND m.status = 'approved'
               ORDER BY {order_by}
               LIMIT ? OFFSET ?""",
            (item_type, page_size, offset),
        ).fetchall()

    total = int(total_row["total"]) if total_row is not None else 0
    return list(rows), total


def list_items_by_author(
    conn: sqlite3.Connection, author_id: str
) -> list[sqlite3.Row]:
    """upstream: marketplace-db.ts:133-147；作者可见全部状态，updated_at DESC。"""
    rows = conn.execute(
        f"{AUTHOR_JOIN} WHERE m.author_id = ? ORDER BY m.updated_at DESC",
        (author_id,),
    ).fetchall()
    return list(rows)


def list_pending_items(
    conn: sqlite3.Connection,
    *,
    page: int,
    page_size: int,
    item_type: str | None = None,
) -> tuple[list[sqlite3.Row], int]:
    """upstream: marketplace-db.ts:149-192；pending 队列 updated_at ASC（FIFO）。"""
    offset = (page - 1) * page_size

    if item_type:
        total_row = conn.execute(
            "SELECT COUNT(*) AS total FROM marketplace_items WHERE status = 'pending' AND type = ?",
            (item_type,),
        ).fetchone()
        rows = conn.execute(
            f"""{AUTHOR_JOIN}
               WHERE m.status = 'pending' AND m.type = ?
               ORDER BY m.updated_at ASC
               LIMIT ? OFFSET ?""",
            (item_type, page_size, offset),
        ).fetchall()
    else:
        total_row = conn.execute(
            "SELECT COUNT(*) AS total FROM marketplace_items WHERE status = 'pending'"
        ).fetchone()
        rows = conn.execute(
            f"""{AUTHOR_JOIN}
               WHERE m.status = 'pending'
               ORDER BY m.updated_at ASC
               LIMIT ? OFFSET ?""",
            (page_size, offset),
        ).fetchall()

    total = int(total_row["total"]) if total_row is not None else 0
    return list(rows), total


def insert_marketplace_item(
    conn: sqlite3.Connection,
    *,
    item_id: str,
    author_id: str,
    data: dict,
    status: str,
    created_at: int,
) -> None:
    """upstream: marketplace-db.ts:194-229；reject_reason=NULL/download=0/published=NULL。"""
    conn.execute(
        """INSERT INTO marketplace_items (
             id, type, author_id, slug, name, description, version,
             cover_url, primary_color, sample_markdown, payload, status, reject_reason,
             download_count, created_at, updated_at, published_at
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, 0, ?, ?, NULL)""",
        (
            item_id,
            data["type"],
            author_id,
            data["slug"],
            data["name"],
            data["description"],
            data["version"],
            data["coverUrl"],
            data["primaryColor"],
            data["sampleMarkdown"],
            data["payload"],
            status,
            created_at,
            created_at,
        ),
    )
    conn.commit()


def update_marketplace_item_by_author(
    conn: sqlite3.Connection,
    *,
    item_id: str,
    author_id: str,
    patch: dict,
    status: str,
    updated_at: int,
) -> bool:
    """upstream: marketplace-db.ts:231-284；重新提交流转 pending 并清空驳回原因。"""
    existing = conn.execute(
        "SELECT * FROM marketplace_items WHERE id = ? AND author_id = ?",
        (item_id, author_id),
    ).fetchone()
    if existing is None:
        return False

    name = patch.get("name", existing["name"])
    description = patch.get("description", existing["description"])
    version = patch.get("version", existing["version"])
    cover_url = (
        patch["coverUrl"] if "coverUrl" in patch else existing["cover_url"]
    )
    primary_color = (
        patch["primaryColor"] if "primaryColor" in patch else existing["primary_color"]
    )
    sample_markdown = (
        patch["sampleMarkdown"]
        if "sampleMarkdown" in patch
        else existing["sample_markdown"]
    )
    payload = patch.get("payload", existing["payload"])

    cursor = conn.execute(
        """UPDATE marketplace_items
           SET name = ?, description = ?, version = ?, cover_url = ?, primary_color = ?,
               sample_markdown = ?, payload = ?, status = ?, reject_reason = NULL,
               updated_at = ?, published_at = NULL
           WHERE id = ? AND author_id = ?""",
        (
            name,
            description,
            version,
            cover_url,
            primary_color,
            sample_markdown,
            payload,
            status,
            updated_at,
            item_id,
            author_id,
        ),
    )
    conn.commit()
    return cursor.rowcount > 0


def delete_marketplace_item_by_author(
    conn: sqlite3.Connection, author_id: str, item_id: str
) -> bool:
    """upstream: marketplace-db.ts:286-297。"""
    cursor = conn.execute(
        "DELETE FROM marketplace_items WHERE id = ? AND author_id = ?",
        (item_id, author_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def approve_marketplace_item(
    conn: sqlite3.Connection, item_id: str, published_at: int
) -> bool:
    """upstream: marketplace-db.ts:299-315；仅 pending 可批准。"""
    cursor = conn.execute(
        """UPDATE marketplace_items
           SET status = 'approved', reject_reason = NULL,
               published_at = ?, updated_at = ?
           WHERE id = ? AND status = 'pending'""",
        (published_at, published_at, item_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def reject_marketplace_item(
    conn: sqlite3.Connection, item_id: str, reason: str | None, updated_at: int
) -> bool:
    """upstream: marketplace-db.ts:317-333；仅 pending 可驳回。"""
    cursor = conn.execute(
        """UPDATE marketplace_items
           SET status = 'rejected', reject_reason = ?, updated_at = ?, published_at = NULL
           WHERE id = ? AND status = 'pending'""",
        (reason, updated_at, item_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def increment_download_count(conn: sqlite3.Connection, item_id: str) -> int:
    """upstream: marketplace-db.ts:335-347；原子 +1 后回读。"""
    conn.execute(
        "UPDATE marketplace_items SET download_count = download_count + 1 WHERE id = ?",
        (item_id,),
    )
    conn.commit()
    row = conn.execute(
        "SELECT download_count FROM marketplace_items WHERE id = ?",
        (item_id,),
    ).fetchone()
    return int(row["download_count"]) if row is not None else 0
