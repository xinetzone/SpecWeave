"""TR-10.2 套餐纯函数（upstream: apps/api/src/plan.ts:20-50）。"""

import math

import pytest

from doocs_md_py.server.plan import (
    MS_PER_SPONSOR_MONTH,
    SHARE_CREATE_LIMIT,
    SYNC_RATE_LIMIT,
    extend_plan_expires,
    get_effective_plan,
    normalize_github_login,
    parse_github_login_from_remark,
)

NOW = 1_000_000_000_000


@pytest.mark.parametrize(
    ("remark", "expected"),
    [
        ("", None),
        ("   ", None),
        ("octocat", "octocat"),
        ("  OctoCat ", "octocat"),
        ("github:octocat", "octocat"),
        ("github：Octo_Cat", None),  # 下划线非法且无合法片段
        ("GitHub : oCtO-cAt", "octo-cat"),
        # upstream: find 返回第一个形似用户名的片段——"thanks" 自身即合法用户名
        ("thanks to octo-cat for sponsorship", "thanks"),
        ("赞助 octo_cat 谢谢", None),  # 下划线非法；中文不分词
        ("备注,a-b;c；d", "a-b"),
        ("a", "a"),
        ("a" + "-" * 37 + "b", "a" + "-" * 37 + "b"),  # 39 字符：长度上限
    ],
)
def test_parse_github_login(remark, expected):
    assert parse_github_login_from_remark(remark) == expected


def test_login_length_bounds():
    assert parse_github_login_from_remark("a" + "-" * 37 + "b") == "a" + "-" * 37 + "b"
    # 40 字符超界
    assert parse_github_login_from_remark("a" + "-" * 38 + "b") is None
    # 中划线不得在首尾
    assert parse_github_login_from_remark("-abc") is None
    assert parse_github_login_from_remark("abc-") is None


def test_normalize():
    assert normalize_github_login("  AbC ") == "abc"


def test_effective_plan():
    assert get_effective_plan("free", None, now_ms_value=NOW) == "free"
    assert get_effective_plan("pro", None, now_ms_value=NOW) == "free"
    assert get_effective_plan("pro", NOW - 1, now_ms_value=NOW) == "free"
    # upstream: 严格大于；相等视为过期
    assert get_effective_plan("pro", NOW, now_ms_value=NOW) == "free"
    assert get_effective_plan("pro", NOW + 1, now_ms_value=NOW) == "pro"
    assert get_effective_plan("whatever", NOW + 10, now_ms_value=NOW) == "free"


def test_extend_from_now_floor_and_clamp():
    # 无到期/已过期 → 基准 now
    assert extend_plan_expires(None, 1, now_ms_value=NOW) == NOW + MS_PER_SPONSOR_MONTH
    assert extend_plan_expires(NOW - 10, 2, now_ms_value=NOW) == NOW + 2 * MS_PER_SPONSOR_MONTH
    # 未过期 → 基准为当前到期
    future = NOW + 5 * MS_PER_SPONSOR_MONTH
    assert extend_plan_expires(future, 1, now_ms_value=NOW) == future + MS_PER_SPONSOR_MONTH
    # floor 3.9 → 3
    assert extend_plan_expires(None, 3.9, now_ms_value=NOW) == NOW + 3 * MS_PER_SPONSOR_MONTH
    # 0 / 负数 / NaN 兜底 1
    assert extend_plan_expires(None, 0, now_ms_value=NOW) == NOW + MS_PER_SPONSOR_MONTH
    assert extend_plan_expires(None, -2, now_ms_value=NOW) == NOW + MS_PER_SPONSOR_MONTH
    nan = float("nan")
    assert extend_plan_expires(None, nan, now_ms_value=NOW) == NOW + MS_PER_SPONSOR_MONTH


def test_limit_constants_match_upstream():
    assert SYNC_RATE_LIMIT == {"free": 30, "pro": 300}
    assert SHARE_CREATE_LIMIT == {"free": 2, "pro": None}
    assert MS_PER_SPONSOR_MONTH == 31 * 24 * 60 * 60 * 1000
    assert math.floor(3.9) == 3
