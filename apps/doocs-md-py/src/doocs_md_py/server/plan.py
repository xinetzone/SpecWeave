"""套餐（free/pro）判定、续费与赞助备注解析。

upstream: apps/api/src/plan.ts:5-50（纯函数部分）。
小时/日键限流函数（上游同文件的 checkSyncRateLimit/peek/consume 及
marketplace-db.ts 的市场限流）在 T11 移植到 ratelimit.py，额度常量在此声明。
"""

import math
import re
import sqlite3
import time

from . import db
from .afdian import AfdianOrder, is_pro_eligible_order
from .config import Config

# upstream: plan.ts:7
MS_PER_SPONSOR_MONTH = 31 * 24 * 60 * 60 * 1000

# upstream: plan.ts:9-12
SYNC_RATE_LIMIT = {"free": 30, "pro": 300}

# upstream: plan.ts:15-18（pro: None 表示不限）
SHARE_CREATE_LIMIT: dict[str, int | None] = {"free": 2, "pro": None}

# upstream: plan.ts:30 GitHub 登录名：1-39 字符，字母数字开头结尾，中划线仅在内部
_REMARK_LOGIN_RE = re.compile(
    r"^(?:github\s*[:：]\s*)?([a-z0-9](?:[a-z0-9-]{0,37}[a-z0-9])?)$",
    re.IGNORECASE,
)
# upstream: plan.ts:35
_TOKEN_LOGIN_RE = re.compile(
    r"^[a-z0-9](?:[a-z0-9-]{0,37}[a-z0-9])?$", re.IGNORECASE
)
# upstream: plan.ts:35 空白与中英文逗号分号分隔
_SPLIT_RE = re.compile(r"[\s,，;；]+")


def _now_ms(now_ms_value: int | None) -> int:
    return time.time_ns() // 1_000_000 if now_ms_value is None else now_ms_value


def normalize_github_login(value: str) -> str:
    """upstream: plan.ts:20-22 trim + lowercase。"""
    return value.strip().lower()


def parse_github_login_from_remark(remark: str) -> str | None:
    """upstream: plan.ts:24-37。

    先整体匹配裸用户名或 ``github:用户名``（含中文冒号）；失败则取第一个
    形如 GitHub 用户名的分隔片段；均失败返回 None。
    """
    trimmed = remark.strip()
    if not trimmed:
        return None

    match = _REMARK_LOGIN_RE.match(trimmed)
    if match:
        return normalize_github_login(match.group(1))

    for part in _SPLIT_RE.split(trimmed):
        if _TOKEN_LOGIN_RE.match(part):
            return normalize_github_login(part)
    return None


def get_effective_plan(
    plan: str, plan_expires_at_ms: int | None, *, now_ms_value: int | None = None
) -> str:
    """upstream: plan.ts:39-43；仅 pro 且到期时间严格晚于现在才有效。"""
    now = _now_ms(now_ms_value)
    if plan == "pro" and plan_expires_at_ms is not None and plan_expires_at_ms > now:
        return "pro"
    return "free"


def extend_plan_expires(
    current_expires_at_ms: int | None, months: float, *, now_ms_value: int | None = None
) -> int:
    """upstream: plan.ts:45-49。

    基准 = max(未过期的当前到期时间, now)；月数 floor 后至少 1；每 sponsor 月=31 天。
    注意上游 ``Math.floor(months) || 1``：floor 得 0（含 NaN/0/负数）时兜底 1。
    """
    now = _now_ms(now_ms_value)
    base = (
        current_expires_at_ms
        if current_expires_at_ms is not None and current_expires_at_ms > now
        else now
    )
    # Math.floor(NaN)=NaN → ||1 兜底；math.floor(nan) 抛 ValueError，同样兜 0
    try:
        floored = math.floor(months)
    except (ValueError, OverflowError, TypeError):
        floored = 0
    month_count = max(1, floored or 1)
    return base + month_count * MS_PER_SPONSOR_MONTH


def activate_pro_from_order(
    conn: sqlite3.Connection,
    config: Config,
    order: AfdianOrder,
    target_github_login: str,
    *,
    now_ms_value: int | None = None,
) -> dict:
    """upstream: plan.ts:166-195 activateProFromOrder。

    返回 ``{"ok": True, "expires_at": int}`` 或
    ``{"ok": False, "reason": "ineligible_plan" | "user_not_found"}``。
    同一 out_trade_no 重复进入时幂等：不再续期，回库中既有到期时间
    （plan_expires_at 为 NULL 时回当前时刻，逐字 ``?? Date.now()``）。
    """
    # upstream: plan.ts:171-172
    if not is_pro_eligible_order(config, order):
        return {"ok": False, "reason": "ineligible_plan"}

    # upstream: plan.ts:174-176
    user = db.get_user_by_github_login(conn, target_github_login)
    if user is None:
        return {"ok": False, "reason": "user_not_found"}

    # upstream: plan.ts:178-182 幂等短路
    if db.is_order_processed(conn, order.out_trade_no):
        expires_at = (
            user.plan_expires_at
            if user.plan_expires_at is not None
            else _now_ms(now_ms_value)
        )
        return {"ok": True, "expires_at": expires_at}

    # upstream: plan.ts:184
    expires_at = extend_plan_expires(
        user.plan_expires_at, order.month, now_ms_value=now_ms_value
    )

    # upstream: plan.ts:186-192 D1 batch（UPDATE users + INSERT afdian_orders）
    # SQLite 用单事务等价：任一失败整体回滚
    processed_at = _now_ms(now_ms_value)
    with conn:
        conn.execute(
            "UPDATE users SET plan = 'pro', plan_expires_at = ? WHERE id = ?",
            (expires_at, user.id),
        )
        conn.execute(
            """INSERT INTO afdian_orders
                   (out_trade_no, user_id, github_login, months, processed_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                order.out_trade_no,
                user.id,
                user.login,
                order.month,
                processed_at,
            ),
        )

    return {"ok": True, "expires_at": expires_at}
