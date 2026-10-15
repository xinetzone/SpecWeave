"""TR-11.2 UTC 窗口键与三表限流（upstream: plan.ts:52-144、marketplace-db.ts:349-394）。"""

from datetime import datetime, timezone

from doocs_md_py.server import ratelimit as rl
from doocs_md_py.server.plan import SHARE_CREATE_LIMIT, SYNC_RATE_LIMIT

UTC = timezone.utc
# 固定时刻：2026-10-15 13:45:30 UTC
T1 = datetime(2026, 10, 15, 13, 45, 30, tzinfo=UTC)
T2 = datetime(2026, 10, 15, 14, 5, 0, tzinfo=UTC)  # 跨小时
T_NEXT_DAY = datetime(2026, 10, 16, 9, 0, 0, tzinfo=UTC)


def test_utc_keys_format_and_padding():
    assert rl.utc_hour_key(datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)) == "2026-01-02T03"
    assert rl.utc_day_key(datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)) == "2026-01-02"
    assert rl.utc_hour_key(T1) == "2026-10-15T13"
    assert rl.utc_day_key(T1) == "2026-10-15"


def test_naive_datetime_treated_as_utc():
    naive = datetime(2026, 10, 15, 13, 45, 30)
    assert rl.utc_hour_key(naive) == rl.utc_hour_key(T1)


def test_sync_retry_after_to_hour_boundary():
    # (60-45)*60 - 30 = 870
    assert rl.sync_retry_after_sec(T1) == 870
    # 整点：3600
    assert rl.sync_retry_after_sec(datetime(2026, 10, 15, 13, 0, 0, tzinfo=UTC)) == 3600
    # 小时末：最少 1
    assert rl.sync_retry_after_sec(datetime(2026, 10, 15, 13, 59, 59, tzinfo=UTC)) == 1
    assert 1 <= rl.sync_retry_after_sec() <= 3600


def test_day_retry_after_to_utc_midnight():
    # T1 距次日 0 点：10h14m30s = 36870
    assert rl.day_retry_after_sec(T1) == 36_870
    assert rl.day_retry_after_sec(datetime(2026, 10, 15, 23, 59, 59, tzinfo=UTC)) == 1
    assert rl.day_retry_after_sec(datetime(2026, 10, 15, 0, 0, 0, tzinfo=UTC)) == 86_400
    assert 1 <= rl.day_retry_after_sec() <= 86_400


# ---- sync_rate_limits ----


def test_sync_rate_limit_blocks_at_free_cap(conn):
    allowed = 0
    for _ in range(SYNC_RATE_LIMIT["free"]):
        result = rl.check_sync_rate_limit(conn, "u1", "free", now=T1)
        assert result["allowed"] is True
        allowed += 1
    blocked = rl.check_sync_rate_limit(conn, "u1", "free", now=T1)
    assert blocked == {
        "allowed": False,
        "limit": 30,
        "retry_after_sec": 870,
    }
    assert allowed == 30


def test_sync_rate_limit_window_rolls_over(conn):
    for _ in range(SYNC_RATE_LIMIT["free"]):
        rl.check_sync_rate_limit(conn, "u1", "free", now=T1)
    assert rl.check_sync_rate_limit(conn, "u1", "free", now=T1)["allowed"] is False
    # 跨小时计数清零
    assert rl.check_sync_rate_limit(conn, "u1", "free", now=T2)["allowed"] is True


def test_sync_rate_limit_isolated_per_user(conn):
    for _ in range(30):
        rl.check_sync_rate_limit(conn, "a", "free", now=T1)
    assert rl.check_sync_rate_limit(conn, "a", "free", now=T1)["allowed"] is False
    assert rl.check_sync_rate_limit(conn, "b", "free", now=T1)["allowed"] is True


def test_sync_rate_limit_pro_cap(conn):
    for _ in range(SYNC_RATE_LIMIT["pro"]):
        assert rl.check_sync_rate_limit(conn, "p", "pro", now=T1)["allowed"] is True
    result = rl.check_sync_rate_limit(conn, "p", "pro", now=T1)
    assert result["allowed"] is False
    assert result["limit"] == 300


# ---- share_rate_limits（peek 不扣减 / consume 扣减）----


def test_share_peek_does_not_consume(conn):
    for _ in range(5):
        peek = rl.peek_share_create_rate_limit(conn, "u1", "free", now=T1)
        assert peek == {"allowed": True, "limit": 2, "period": "day"}


def test_share_consume_then_block(conn):
    rl.consume_share_create_rate_limit(conn, "u1", "free", now=T1)
    assert rl.peek_share_create_rate_limit(conn, "u1", "free", now=T1)["allowed"] is True
    rl.consume_share_create_rate_limit(conn, "u1", "free", now=T1)
    blocked = rl.peek_share_create_rate_limit(conn, "u1", "free", now=T1)
    assert blocked["allowed"] is False
    assert blocked["limit"] == 2
    assert blocked["retry_after_sec"] == 36_870
    # 次日清零
    assert rl.peek_share_create_rate_limit(conn, "u1", "free", now=T_NEXT_DAY)["allowed"] is True


def test_share_pro_unlimited_is_noop(conn):
    peek = rl.peek_share_create_rate_limit(conn, "p", "pro", now=T1)
    assert peek == {"allowed": True, "limit": None, "period": "day"}
    for _ in range(100):
        rl.consume_share_create_rate_limit(conn, "p", "pro", now=T1)
    assert rl.peek_share_create_rate_limit(conn, "p", "pro", now=T1)["allowed"] is True
    # pro 不写计数行
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM share_rate_limits WHERE scope_key = ?",
        ("share:publish:p",),
    ).fetchone()
    assert row["c"] == 0


def test_share_scope_isolated(conn):
    rl.consume_share_create_rate_limit(conn, "a", "free", now=T1)
    rl.consume_share_create_rate_limit(conn, "a", "free", now=T1)
    assert rl.peek_share_create_rate_limit(conn, "a", "free", now=T1)["allowed"] is False
    assert rl.peek_share_create_rate_limit(conn, "b", "free", now=T1)["allowed"] is True


# ---- marketplace_rate_limits ----


def test_marketplace_consume_blocks_after_limit(conn):
    for i in range(5):
        result = rl.consume_marketplace_publish_rate_limit(conn, "u1", 5, now=T1)
        assert result["allowed"] is True
    blocked = rl.consume_marketplace_publish_rate_limit(conn, "u1", 5, now=T1)
    assert blocked["allowed"] is False
    assert blocked["limit"] == 5
    assert blocked["retry_after_sec"] == 36_870
    # 次日清零
    assert (
        rl.consume_marketplace_publish_rate_limit(conn, "u1", 5, now=T_NEXT_DAY)["allowed"]
        is True
    )


def test_marketplace_scope_prefix_distinct_from_share(conn):
    # share:publish:<u> 与 publish:<u> 是不同表不同 scope，互不影响
    rl.consume_share_create_rate_limit(conn, "u1", "free", now=T1)
    assert (
        rl.consume_marketplace_publish_rate_limit(conn, "u1", 5, now=T1)["allowed"]
        is True
    )


def test_limit_constants_are_upstream_values():
    assert SYNC_RATE_LIMIT == {"free": 30, "pro": 300}
    assert SHARE_CREATE_LIMIT == {"free": 2, "pro": None}
