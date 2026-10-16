"""UTC 时间窗口限流（upstream: apps/api/src/plan.ts:52-144 + marketplace-db.ts:349-394）。

三张计数表（迁移 0002-0004 已建）：
- sync_rate_limits(user_id, hour_key)：同步 pull/push 共用，UTC 小时桶；
- share_rate_limits(scope_key, hour_key)：分享发布/解锁失败，日键也存入 hour_key 列
  （逐字保留上游列名复用）；
- marketplace_rate_limits(scope_key, day_key)：市场发布，UTC 日桶。

所有函数接受可注入 ``now``（timezone-aware UTC datetime），默认取当前 UTC 时间，
便于窗口边界测试。
"""

import sqlite3
from datetime import datetime, timedelta, timezone

from .plan import SHARE_CREATE_LIMIT, SYNC_RATE_LIMIT


def _clock(now: datetime | None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if now.tzinfo is None:
        # 注入的 naive datetime 一律按 UTC 解释（JS Date 恒为 UTC 时刻）
        return now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def utc_hour_key(now: datetime | None = None) -> str:
    """upstream: plan.ts:52-55 ``YYYY-MM-DDTHH``。"""
    d = _clock(now)
    return f"{d.year:04d}-{d.month:02d}-{d.day:02d}T{d.hour:02d}"


def utc_day_key(now: datetime | None = None) -> str:
    """upstream: plan.ts:57-60 / marketplace-db.ts:349-352 ``YYYY-MM-DD``。"""
    d = _clock(now)
    return f"{d.year:04d}-{d.month:02d}-{d.day:02d}"


def sync_retry_after_sec(now: datetime | None = None) -> int:
    """upstream: plan.ts:83-85 到下一 UTC 整点的剩余秒（忽略毫秒），最少 1。"""
    d = _clock(now)
    return max(1, (60 - d.minute) * 60 - d.second)


def day_retry_after_sec(now: datetime | None = None) -> int:
    """upstream: plan.ts:62-66 / marketplace-db.ts:354-358 到下一 UTC 0 点，最少 1。"""
    d = _clock(now)
    next_midnight = (d + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return max(1, int((next_midnight - d).total_seconds()))


def check_sync_rate_limit(
    conn: sqlite3.Connection,
    user_id: str,
    plan: str,
    *,
    now: datetime | None = None,
) -> dict:
    """upstream: plan.ts:68-97。

    先查后插（upsert count+1）；超限不计数，返回 retryAfterSec 到小时末。
    """
    limit = SYNC_RATE_LIMIT[plan]
    hour_key = utc_hour_key(now)

    row = conn.execute(
        "SELECT count FROM sync_rate_limits WHERE user_id = ? AND hour_key = ?",
        (user_id, hour_key),
    ).fetchone()
    count = int(row["count"]) if row is not None else 0
    if count >= limit:
        return {
            "allowed": False,
            "limit": limit,
            "retry_after_sec": sync_retry_after_sec(now),
        }

    conn.execute(
        """INSERT INTO sync_rate_limits (user_id, hour_key, count) VALUES (?, ?, 1)
           ON CONFLICT(user_id, hour_key) DO UPDATE SET count = count + 1""",
        (user_id, hour_key),
    )
    conn.commit()
    return {"allowed": True, "limit": limit}


def peek_share_create_rate_limit(
    conn: sqlite3.Connection,
    user_id: str,
    plan: str,
    *,
    now: datetime | None = None,
) -> dict:
    """upstream: plan.ts:99-122；只查看不扣减。pro（limit=None）直接放行。"""
    limit = SHARE_CREATE_LIMIT[plan]
    if limit is None:
        return {"allowed": True, "limit": None, "period": "day"}

    scope_key = f"share:publish:{user_id}"
    day_key = utc_day_key(now)

    row = conn.execute(
        "SELECT count FROM share_rate_limits WHERE scope_key = ? AND hour_key = ?",
        (scope_key, day_key),
    ).fetchone()
    count = int(row["count"]) if row is not None else 0
    if count >= limit:
        return {
            "allowed": False,
            "limit": limit,
            "period": "day",
            "retry_after_sec": day_retry_after_sec(now),
        }
    return {"allowed": True, "limit": limit, "period": "day"}


def consume_share_create_rate_limit(
    conn: sqlite3.Connection,
    user_id: str,
    plan: str,
    *,
    now: datetime | None = None,
) -> None:
    """upstream: plan.ts:125-144；成功创建/更新后扣减；pro 不计。"""
    limit = SHARE_CREATE_LIMIT[plan]
    if limit is None:
        return

    scope_key = f"share:publish:{user_id}"
    day_key = utc_day_key(now)
    conn.execute(
        """INSERT INTO share_rate_limits (scope_key, hour_key, count) VALUES (?, ?, 1)
           ON CONFLICT(scope_key, hour_key) DO UPDATE SET count = count + 1""",
        (scope_key, day_key),
    )
    conn.commit()


def consume_marketplace_publish_rate_limit(
    conn: sqlite3.Connection,
    user_id: str,
    limit: int,
    *,
    now: datetime | None = None,
) -> dict:
    """upstream: marketplace-db.ts:360-394；scope=publish:<user>，UTC 日桶。"""
    day_key = utc_day_key(now)
    scope_key = f"publish:{user_id}"

    row = conn.execute(
        "SELECT count FROM marketplace_rate_limits WHERE scope_key = ? AND day_key = ?",
        (scope_key, day_key),
    ).fetchone()
    count = int(row["count"]) if row is not None else 0
    if count >= limit:
        return {
            "allowed": False,
            "limit": limit,
            "retry_after_sec": day_retry_after_sec(now),
        }

    conn.execute(
        """INSERT INTO marketplace_rate_limits (scope_key, day_key, count)
           VALUES (?, ?, 1)
           ON CONFLICT(scope_key, day_key) DO UPDATE SET count = count + 1""",
        (scope_key, day_key),
    )
    conn.commit()
    return {"allowed": True, "limit": limit}
