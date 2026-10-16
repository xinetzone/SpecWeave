"""上传限流（upstream: apps/api/src/upload-rate.ts 1:1）。

注意：上游复用 ``share_rate_limits`` 表，仅 scope_key 命名空间不同
（``upload:ip:<ip>`` / ``upload:user:<id>``）；窗口为 UTC 小时，retryAfter
到下一整点（与 sync 同一公式）。成功上传后才计数。
"""

import sqlite3
from datetime import datetime

from .config import UPLOAD_RATE_LIMIT
from .ratelimit import utc_hour_key, sync_retry_after_sec


# upstream: upload-rate.ts:9-12
def upload_rate_limit_retry_after_sec(now: datetime | None = None) -> int:
    return sync_retry_after_sec(now)


# upstream: upload-rate.ts:14-25
def get_upload_rate_limit_count(
    conn: sqlite3.Connection, scope_key: str, *, now: datetime | None = None
) -> int:
    hour_key = utc_hour_key(now)
    row = conn.execute(
        "SELECT count FROM share_rate_limits WHERE scope_key = ? AND hour_key = ?",
        (scope_key, hour_key),
    ).fetchone()
    return int(row["count"]) if row is not None else 0


# upstream: upload-rate.ts:27-39
def increment_upload_rate_limit(
    conn: sqlite3.Connection, scope_key: str, *, now: datetime | None = None
) -> None:
    hour_key = utc_hour_key(now)
    conn.execute(
        """INSERT INTO share_rate_limits (scope_key, hour_key, count) VALUES (?, ?, 1)
           ON CONFLICT(scope_key, hour_key) DO UPDATE SET count = count + 1""",
        (scope_key, hour_key),
    )
    conn.commit()


# upstream: upload-rate.ts:41-47
def upload_rate_limit_for_plan(plan: str | None) -> int:
    if plan == "pro":
        return UPLOAD_RATE_LIMIT["pro"]
    if plan == "free":
        return UPLOAD_RATE_LIMIT["free"]
    return UPLOAD_RATE_LIMIT["anonymous"]
