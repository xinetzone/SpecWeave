"""站内通知数据层（upstream: apps/api/src/notifications-db.ts 1:1）。

T15 市场路由消费 ``resolve_admin_user_ids`` 与 ``notify_users``；列表/已读等
端点在 T16 挂载，数据层函数一并移植到位。
"""

import json
import sqlite3
import uuid
from typing import Any

from .config import Config
from .marketplace_admin import get_admin_logins
from .plan import normalize_github_login

VALID_NOTIFICATION_TYPES = (
    "marketplace_pending",
    "marketplace_approved",
    "marketplace_rejected",
)


def _compact_json(value: Any) -> str:
    """等价 JS JSON.stringify（紧凑、不转义非 ASCII）。"""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def parse_payload(raw: str) -> dict:
    """upstream: notifications-db.ts:36-52 损坏 payload 兜底而非抛错。"""
    try:
        parsed = json.loads(raw)
    except (ValueError, TypeError):
        parsed = None
    if not isinstance(parsed, dict):
        parsed = {}
    reject_reason = parsed.get("rejectReason")
    # upstream: 字符串原样；否则 `parsed.rejectReason ?? null`——数字/布尔/对象
    # 等非 nullish 值保留，仅 undefined（键缺失）与 null 归一为 None
    if isinstance(reject_reason, str):
        resolved_reason: Any = reject_reason
    else:
        resolved_reason = reject_reason if reject_reason is not None else None
    return {
        "itemId": parsed.get("itemId") if isinstance(parsed.get("itemId"), str) else "",
        "itemType": "component" if parsed.get("itemType") == "component" else "theme",
        "name": parsed.get("name") if isinstance(parsed.get("name"), str) else "",
        "slug": parsed.get("slug") if isinstance(parsed.get("slug"), str) else "",
        "rejectReason": resolved_reason,
    }


def row_to_notification(row: sqlite3.Row) -> dict:
    """upstream: notifications-db.ts:54-62。"""
    return {
        "id": row["id"],
        "type": row["type"],
        "payload": parse_payload(row["payload"]),
        "readAt": row["read_at"],
        "createdAt": row["created_at"],
    }


def resolve_admin_user_ids(
    conn: sqlite3.Connection,
    config: Config,
    *,
    exclude_user_id: str | None = None,
) -> list[str]:
    """upstream: notifications-db.ts:65-83；白名单解析为 users 表中已存在的 id。"""
    logins = list(get_admin_logins(config))
    if not logins:
        return []
    ids: list[str] = []
    for login in logins:
        row = conn.execute(
            "SELECT id FROM users WHERE lower(login) = ?",
            (normalize_github_login(login),),
        ).fetchone()
        if row is None or not row["id"]:
            continue
        if exclude_user_id and row["id"] == exclude_user_id:
            continue
        ids.append(row["id"])
    return ids


def notify_users(
    conn: sqlite3.Connection,
    user_ids: list[str],
    *,
    notification_type: str,
    payload: dict,
    created_at: int,
) -> None:
    """upstream: notifications-db.ts:85-114；去重、过滤空 id、批量插入。"""
    unique = list(dict.fromkeys(uid for uid in user_ids if uid))
    if not unique:
        return
    with conn:
        for user_id in unique:
            conn.execute(
                """INSERT INTO notifications (id, user_id, type, payload, read_at, created_at)
                   VALUES (?, ?, ?, ?, NULL, ?)""",
                (
                    str(uuid.uuid4()),
                    user_id,
                    notification_type,
                    _compact_json(payload),
                    created_at,
                ),
            )


def list_notifications(
    conn: sqlite3.Connection, user_id: str, *, page: int, page_size: int
) -> tuple[list[sqlite3.Row], int]:
    """upstream: notifications-db.ts:116-142；created_at DESC 分页。"""
    offset = (page - 1) * page_size
    total_row = conn.execute(
        "SELECT COUNT(*) AS total FROM notifications WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    total = int(total_row["total"]) if total_row is not None else 0
    rows = conn.execute(
        """SELECT id, user_id, type, payload, read_at, created_at
           FROM notifications WHERE user_id = ?
           ORDER BY created_at DESC
           LIMIT ? OFFSET ?""",
        (user_id, page_size, offset),
    ).fetchall()
    return list(rows), total


def count_unread_notifications(conn: sqlite3.Connection, user_id: str) -> int:
    """upstream: notifications-db.ts:144-155。"""
    row = conn.execute(
        "SELECT COUNT(*) AS total FROM notifications WHERE user_id = ? AND read_at IS NULL",
        (user_id,),
    ).fetchone()
    return int(row["total"]) if row is not None else 0


def mark_notification_read(
    conn: sqlite3.Connection, user_id: str, notification_id: str, read_at: int
) -> bool:
    """upstream: notifications-db.ts:157-171；仅未读行可更新，返回是否命中。"""
    cursor = conn.execute(
        """UPDATE notifications SET read_at = ?
           WHERE id = ? AND user_id = ? AND read_at IS NULL""",
        (read_at, notification_id, user_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def get_notification_by_id(
    conn: sqlite3.Connection, user_id: str, notification_id: str
) -> sqlite3.Row | None:
    """upstream: notifications-db.ts:173-185。"""
    return conn.execute(
        """SELECT id, user_id, type, payload, read_at, created_at
           FROM notifications WHERE id = ? AND user_id = ?""",
        (notification_id, user_id),
    ).fetchone()


def mark_all_notifications_read(conn: sqlite3.Connection, user_id: str, read_at: int) -> int:
    """upstream: notifications-db.ts:187-200；返回更新行数。"""
    cursor = conn.execute(
        """UPDATE notifications SET read_at = ?
           WHERE user_id = ? AND read_at IS NULL""",
        (read_at, user_id),
    )
    conn.commit()
    return cursor.rowcount


def clear_all_notifications(conn: sqlite3.Connection, user_id: str) -> int:
    """upstream: notifications-db.ts:202-210；返回删除行数。"""
    cursor = conn.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
    conn.commit()
    return cursor.rowcount
