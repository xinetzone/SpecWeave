"""TR-17.1 爱发电 webhook 与手动激活。

upstream: apps/api/src/{afdian.ts,webhook.ts,activate.ts,plan.ts:146-195}
- 签名已知答案向量；
- query_order 请求要素（去尾斜杠/紧凑 JSON/签名重算）与全空分支 MockTransport；
- isProEligibleOrder status/product_type/plan 白名单；
- activateProFromOrder：不合格/用户不存在/续费 max/过期基准/幂等/月数兜底；
- webhook：路径令牌 403、未配置静默 200、坏 JSON 400、非订单静默、
  只信 out_trade_no（伪造回调字段无效）、命中激活、幂等双回调；
- POST /sync/activate：503/400/404/403/成功/幂等全分支。
"""

import json
import time

import httpx
import pytest
from fastapi.testclient import TestClient

from doocs_md_py.server import db
from doocs_md_py.server.afdian import (
    AfdianOrder,
    is_pro_eligible_order,
    query_order,
    sign,
)
from doocs_md_py.server.app import create_app
from doocs_md_py.server.config import Config
from doocs_md_py.server.plan import (
    MS_PER_SPONSOR_MONTH,
    activate_pro_from_order,
)
from doocs_md_py.server.security import issue_token

JWT_SECRET = "afdian-jwt-secret-0123456789-abcdef-00"
FIXED_NOW_MS = 2_000_000_000_000
DAY_MS = 24 * 60 * 60 * 1000
MONTH_MS = MS_PER_SPONSOR_MONTH

# TR-17.1 已知答案：md5(token + params{...}ts{...}user_id{...})
# 独立进程预先计算，锁定拼接顺序
SIGN_PARAMS = '{"out_trade_no":"202610150000000001"}'
SIGN_EXPECTED = "378c76ef644fb7a11ed0ec0584b0aaeb"


# ---- 工厂 ----


def make_order(
    *,
    no: str = "O1",
    status: int = 2,
    product_type: int = 0,
    plan_id: str = "plan-a",
    month: int = 1,
    remark: str = "octocat",
    user_id: str = "fan-1",
    title: str | None = None,
) -> AfdianOrder:
    return AfdianOrder(
        out_trade_no=no,
        user_id=user_id,
        plan_id=plan_id,
        month=month,
        total_amount="31.00",
        show_amount="31.00",
        status=status,
        remark=remark,
        product_type=product_type,
        title=title,
    )


def afdian_payload(order: AfdianOrder) -> dict:
    item = {
        "out_trade_no": order.out_trade_no,
        "user_id": order.user_id,
        "plan_id": order.plan_id,
        "month": order.month,
        "total_amount": order.total_amount,
        "show_amount": order.show_amount,
        "status": order.status,
        "remark": order.remark,
        "product_type": order.product_type,
    }
    if order.title is not None:
        item["title"] = order.title
    return {"ec": 200, "em": "", "data": {"list": [item]}}


class AfdianMock:
    """按 out_trade_no 回放响应；未登记单号回 ec=400。记录全部请求。"""

    def __init__(self, responses: dict | None = None) -> None:
        self.responses = responses or {}
        self.requests: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        body = json.loads(request.content)
        params = json.loads(body["params"])
        payload = self.responses.get(
            params["out_trade_no"], {"ec": 400, "em": "order not found"}
        )
        return httpx.Response(200, json=payload)


def make_client(
    conn,
    mock: AfdianMock,
    *,
    configured: bool = True,
    webhook_token: str = "",
    plan_ids: tuple[str, ...] = (),
    api_base: str = "https://afdian.example/api/open",
):
    cfg = Config(
        jwt_secret=JWT_SECRET,
        afdian_user_id="afd_u" if configured else "",
        afdian_api_token="afd_tok" if configured else "",
        afdian_api_base=api_base,
        afdian_webhook_token=webhook_token,
        afdian_pro_plan_ids=plan_ids,
    )
    http_client = httpx.Client(transport=httpx.MockTransport(mock.handler))
    app = create_app(cfg, conn=conn, http_client=http_client)
    return TestClient(app), cfg, http_client


def auth(sub: str = "user-001", login: str = "octocat") -> dict:
    return {
        "Authorization": f"Bearer {issue_token(JWT_SECRET, sub, login)}"
    }


def order_row(conn, out_trade_no: str):
    return conn.execute(
        "SELECT * FROM afdian_orders WHERE out_trade_no = ?",
        (out_trade_no,),
    ).fetchone()


# ---- 1. 签名已知答案向量 ----


def test_sign_known_answer_vector():
    # upstream: afdian.ts:29-32
    assert (
        sign("test_token_123", SIGN_PARAMS, 1760529600, "afdian_user_42")
        == SIGN_EXPECTED
    )


# ---- 2. isProEligibleOrder ----


def test_is_pro_eligible_order_status_and_product_type():
    cfg = Config()
    assert is_pro_eligible_order(cfg, make_order(status=2, product_type=0))
    assert is_pro_eligible_order(cfg, make_order(status=2, product_type=1))
    # upstream: afdian.ts:77-81
    assert not is_pro_eligible_order(cfg, make_order(status=1))
    assert not is_pro_eligible_order(cfg, make_order(status=3))
    assert not is_pro_eligible_order(cfg, make_order(product_type=2))
    assert not is_pro_eligible_order(cfg, make_order(product_type=-1))


def test_is_pro_eligible_order_plan_whitelist():
    # upstream: afdian.ts:83-91 空白名单=全接受
    assert is_pro_eligible_order(Config(), make_order(plan_id="anything"))
    cfg = Config(afdian_pro_plan_ids=("plan-a", "plan-b"))
    assert is_pro_eligible_order(cfg, make_order(plan_id="plan-a"))
    assert is_pro_eligible_order(cfg, make_order(plan_id="plan-b"))
    assert not is_pro_eligible_order(cfg, make_order(plan_id="plan-x"))


# ---- 3. query_order 请求要素与空分支 ----


def test_query_order_request_shape_and_signature():
    mock = AfdianMock({"O1": afdian_payload(make_order(no="O1", title="Pro x1"))})
    cfg = Config(
        afdian_user_id="afd_u",
        afdian_api_token="afd_tok",
        # 末尾斜杠必须被剥掉（upstream: afdian.ts:26）
        afdian_api_base="https://afdian.example/api/open/",
    )
    client = httpx.Client(transport=httpx.MockTransport(mock.handler))

    order = query_order(client, cfg, "O1", now_s=1760529600)

    assert order is not None
    assert order.out_trade_no == "O1"
    assert order.status == 2
    assert order.product_type == 0
    assert order.month == 1
    assert order.remark == "octocat"
    assert order.title == "Pro x1"

    assert len(mock.requests) == 1
    req = mock.requests[0]
    assert req.method == "POST"
    assert str(req.url) == "https://afdian.example/api/open/query-order"
    assert req.headers["content-type"] == "application/json"

    body = json.loads(req.content)
    assert set(body.keys()) == {"user_id", "params", "ts", "sign"}
    assert body["user_id"] == "afd_u"
    assert body["ts"] == 1760529600
    assert isinstance(body["ts"], int)
    # params 是 JSON 字符串而非对象
    assert isinstance(body["params"], str)
    assert json.loads(body["params"]) == {"out_trade_no": "O1"}
    # 签名按实际发送的 params 串重算必须一致
    assert body["sign"] == sign("afd_tok", body["params"], 1760529600, "afd_u")


def test_query_order_ts_defaults_to_current_epoch():
    mock = AfdianMock({"O1": afdian_payload(make_order(no="O1"))})
    cfg = Config(afdian_user_id="u", afdian_api_token="t")
    client = httpx.Client(transport=httpx.MockTransport(mock.handler))
    before = int(time.time())
    assert query_order(client, cfg, "O1") is not None
    after = int(time.time())
    ts = json.loads(mock.requests[0].content)["ts"]
    assert before <= ts <= after


@pytest.mark.parametrize(
    "payload",
    [
        {"ec": 400, "em": "bad"},
        {"em": "no ec"},
        {"ec": 200},
        {"ec": 200, "data": {}},
        {"ec": 200, "data": {"list": []}},
        {"ec": 200, "data": {"list": None}},
        {"ec": 200, "data": {"list": ["not-an-object"]}},
        [],
        "unexpected",
    ],
)
def test_query_order_returns_none_for_empty_or_malformed(payload):
    mock = AfdianMock({"X": payload})
    cfg = Config(afdian_user_id="u", afdian_api_token="t")
    client = httpx.Client(transport=httpx.MockTransport(mock.handler))
    assert query_order(client, cfg, "X") is None


def test_query_order_raises_when_not_configured():
    def must_not_request(_request):  # pragma: no cover - 不应被调用
        raise AssertionError("afdian API must not be called when unconfigured")

    client = httpx.Client(transport=httpx.MockTransport(must_not_request))
    with pytest.raises(RuntimeError, match="afdian_not_configured"):
        query_order(client, Config(), "O1")


# ---- 4. activateProFromOrder ----


def test_activate_pro_from_order_ineligible(conn, user_id):
    cfg = Config()
    cases = [
        make_order(no="I1", status=1),
        make_order(no="I2", status=3),
        make_order(no="I3", product_type=2),
    ]
    for order in cases:
        result = activate_pro_from_order(
            conn, cfg, order, "octocat", now_ms_value=FIXED_NOW_MS
        )
        assert result == {"ok": False, "reason": "ineligible_plan"}
        assert order_row(conn, order.out_trade_no) is None

    cfg_wl = Config(afdian_pro_plan_ids=("plan-x",))
    result = activate_pro_from_order(
        conn, cfg_wl, make_order(no="I4", plan_id="plan-a"),
        "octocat", now_ms_value=FIXED_NOW_MS,
    )
    assert result == {"ok": False, "reason": "ineligible_plan"}
    assert order_row(conn, "I4") is None
    user = db.get_user_by_id(conn, user_id)
    assert user.plan == "free"
    assert user.plan_expires_at is None


def test_activate_pro_from_order_user_not_found(conn):
    result = activate_pro_from_order(
        conn, Config(), make_order(no="U1", remark="ghost"),
        "ghost-login", now_ms_value=FIXED_NOW_MS,
    )
    assert result == {"ok": False, "reason": "user_not_found"}
    assert order_row(conn, "U1") is None


def test_activate_pro_from_order_success_writes_batch(conn, user_id):
    order = make_order(no="S1", month=1)
    result = activate_pro_from_order(
        conn, Config(), order, "octocat", now_ms_value=FIXED_NOW_MS
    )
    assert result == {"ok": True, "expires_at": FIXED_NOW_MS + MONTH_MS}

    user = db.get_user_by_id(conn, user_id)
    assert user.plan == "pro"
    assert user.plan_expires_at == FIXED_NOW_MS + MONTH_MS

    row = order_row(conn, "S1")
    assert row is not None
    # upstream: plan.ts:188-191 列序与取值
    assert row["out_trade_no"] == "S1"
    assert row["user_id"] == user_id
    assert row["github_login"] == "octocat"
    assert row["months"] == 1
    assert row["processed_at"] == FIXED_NOW_MS


def test_activate_pro_from_order_target_login_case_insensitive(conn, user_id):
    # 目标登录名大小写不敏感；落库 github_login 取 users 表行的实际 login
    result = activate_pro_from_order(
        conn, Config(), make_order(no="S2"),
        "OctoCat", now_ms_value=FIXED_NOW_MS,
    )
    assert result["ok"] is True
    assert order_row(conn, "S2")["github_login"] == "octocat"


def test_activate_pro_from_order_renews_from_max_future_expiry(conn, user_id):
    # 已在有效期内：base = max(当前到期, now)（upstream: plan.ts:47）
    future = FIXED_NOW_MS + 10 * DAY_MS
    conn.execute(
        "UPDATE users SET plan = 'pro', plan_expires_at = ? WHERE id = ?",
        (future, user_id),
    )
    conn.execute(
        "INSERT INTO afdian_orders VALUES (?, ?, ?, ?, ?)",
        ("OLD", user_id, "octocat", 1, FIXED_NOW_MS - 30 * DAY_MS),
    )
    result = activate_pro_from_order(
        conn, Config(), make_order(no="R1", month=1),
        "octocat", now_ms_value=FIXED_NOW_MS,
    )
    assert result == {"ok": True, "expires_at": future + MONTH_MS}


def test_activate_pro_from_order_expired_pro_uses_now_base(conn, user_id):
    # 已过期：base 回落到 now
    conn.execute(
        "UPDATE users SET plan = 'pro', plan_expires_at = ? WHERE id = ?",
        (FIXED_NOW_MS - 100 * DAY_MS, user_id),
    )
    result = activate_pro_from_order(
        conn, Config(), make_order(no="R2", month=2),
        "octocat", now_ms_value=FIXED_NOW_MS,
    )
    assert result == {"ok": True, "expires_at": FIXED_NOW_MS + 2 * MONTH_MS}


def test_activate_pro_from_order_zero_month_floors_to_one(conn, user_id):
    # upstream: plan.ts:48 Math.max(1, Math.floor(months) || 1)
    result = activate_pro_from_order(
        conn, Config(), make_order(no="R3", month=0),
        "octocat", now_ms_value=FIXED_NOW_MS,
    )
    assert result == {"ok": True, "expires_at": FIXED_NOW_MS + MONTH_MS}
    assert order_row(conn, "R3")["months"] == 0


def test_activate_pro_from_order_idempotent_same_trade_no(conn, user_id):
    order = make_order(no="D1", month=1)
    first = activate_pro_from_order(
        conn, Config(), order, "octocat", now_ms_value=FIXED_NOW_MS
    )
    # 重复回调即便携带不同 month/不同当前时刻，也不再续期
    duplicate = make_order(no="D1", month=6)
    second = activate_pro_from_order(
        conn, Config(), duplicate, "octocat",
        now_ms_value=FIXED_NOW_MS + 999_999,
    )
    assert first == {"ok": True, "expires_at": FIXED_NOW_MS + MONTH_MS}
    assert second == first
    rows = conn.execute(
        "SELECT COUNT(*) AS c FROM afdian_orders WHERE out_trade_no = 'D1'"
    ).fetchone()
    assert rows["c"] == 1
    user = db.get_user_by_id(conn, user_id)
    assert user.plan_expires_at == FIXED_NOW_MS + MONTH_MS


def test_activate_pro_from_order_processed_but_null_expiry(conn, user_id):
    # upstream: plan.ts:180 user.plan_expires_at ?? Date.now() 分支
    conn.execute(
        "INSERT INTO afdian_orders VALUES (?, ?, ?, ?, ?)",
        ("D2", user_id, "octocat", 1, FIXED_NOW_MS - 1),
    )
    result = activate_pro_from_order(
        conn, Config(), make_order(no="D2"),
        "octocat", now_ms_value=FIXED_NOW_MS,
    )
    assert result == {"ok": True, "expires_at": FIXED_NOW_MS}
    user = db.get_user_by_id(conn, user_id)
    assert user.plan == "free"
    assert user.plan_expires_at is None


# ---- 5. webhook ----


def test_webhook_wrong_or_missing_path_token_403(conn):
    mock = AfdianMock()
    client, _, _ = make_client(conn, mock, webhook_token="secret")

    r = client.post("/webhooks/afdian/wrong", json={"data": {}})
    assert r.status_code == 403
    assert r.json() == {"ec": 403, "em": "forbidden"}

    r2 = client.post("/webhooks/afdian", json={"data": {}})
    assert r2.status_code == 403
    assert r2.json() == {"ec": 403, "em": "forbidden"}

    # 令牌校验先于一切：不产生爱发电回查
    assert mock.requests == []


def test_webhook_unconfigured_silent_200_even_with_bad_json(conn):
    mock = AfdianMock()
    client, _, _ = make_client(conn, mock, configured=False)
    r = client.post(
        "/webhooks/afdian",
        content=b"{bad json",
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 200
    assert r.json() == {"ec": 200, "em": ""}
    assert mock.requests == []


def test_webhook_bad_json_400_when_configured(conn):
    mock = AfdianMock()
    client, _, _ = make_client(conn, mock, webhook_token="secret")
    r = client.post(
        "/webhooks/afdian/secret",
        content=b"{bad json",
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 400
    assert r.json() == {"ec": 400, "em": "invalid_body"}
    assert mock.requests == []


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"data": {}},
        {"data": {"type": "normal"}},
        {"data": {"type": "order"}},
        {"data": {"type": "order", "order": {}}},
        {"data": {"type": "order", "order": {"out_trade_no": "   "}}},
        {"data": {"type": "order", "order": {"out_trade_no": 123}}},
        {"data": {"type": "order", "order": "not-an-object"}},
        [1, 2, 3],
    ],
)
def test_webhook_silent_200_without_requery(conn, body):
    mock = AfdianMock()
    client, _, _ = make_client(conn, mock)
    r = client.post("/webhooks/afdian", json=body)
    assert r.status_code == 200
    assert r.json() == {"ec": 200, "em": ""}
    assert mock.requests == []


def test_webhook_requery_missing_or_unpaid_silent_200(conn, user_id):
    mock = AfdianMock(
        {
            "P1": afdian_payload(make_order(no="P1", status=3)),
        }
    )
    client, _, _ = make_client(conn, mock)

    # 回查无此单（mock 未登记 → ec=400）
    r = client.post(
        "/webhooks/afdian",
        json={"data": {"type": "order", "order": {"out_trade_no": "MISSING"}}},
    )
    assert r.status_code == 200
    # 回查存在但未支付
    r2 = client.post(
        "/webhooks/afdian",
        json={"data": {"type": "order", "order": {"out_trade_no": "P1"}}},
    )
    assert r2.status_code == 200

    user = db.get_user_by_id(conn, user_id)
    assert user.plan == "free"
    assert order_row(conn, "MISSING") is None
    assert order_row(conn, "P1") is None


def test_webhook_remark_without_login_silent_200(conn, user_id):
    # 中文备注不含可识别的 GitHub 用户名片段
    mock = AfdianMock(
        {"W0": afdian_payload(make_order(no="W0", remark="感谢支持"))}
    )
    client, _, _ = make_client(conn, mock)
    r = client.post(
        "/webhooks/afdian",
        json={"data": {"type": "order", "order": {"out_trade_no": "W0"}}},
    )
    assert r.status_code == 200
    assert order_row(conn, "W0") is None
    assert db.get_user_by_id(conn, user_id).plan == "free"


def test_webhook_activates_user_and_ignores_forged_fields(conn, user_id):
    order = make_order(no="W1", remark="octocat", month=1)
    mock = AfdianMock({"W1": afdian_payload(order)})
    client, _, _ = make_client(conn, mock, webhook_token="secret")

    r = client.post(
        "/webhooks/afdian/secret",
        json={
            "ec": 200,
            "data": {
                "type": "order",
                # 仅 out_trade_no 被采信；其余回调字段即便伪造也无效
                "order": {"out_trade_no": "W1", "status": 9, "remark": "fake"},
            },
        },
    )
    assert r.status_code == 200
    assert r.json() == {"ec": 200, "em": ""}

    user = db.get_user_by_id(conn, user_id)
    assert user.plan == "pro"
    expected = int(time.time() * 1000) + MONTH_MS
    assert abs(user.plan_expires_at - expected) < 5000
    assert order_row(conn, "W1") is not None
    assert len(mock.requests) == 1

    # 伪造回调：自称已支付的 W2，开放平台回查 status=3 → 不激活
    mock.responses["W2"] = afdian_payload(
        make_order(no="W2", status=3, remark="octocat")
    )
    r2 = client.post(
        "/webhooks/afdian/secret",
        json={
            "data": {
                "type": "order",
                "order": {"out_trade_no": "W2", "status": 2},
            }
        },
    )
    assert r2.status_code == 200
    assert order_row(conn, "W2") is None
    assert db.get_user_by_id(conn, user_id).plan == "pro"  # 状态未变


def test_webhook_unknown_login_still_200(conn, user_id):
    mock = AfdianMock(
        {"W3": afdian_payload(make_order(no="W3", remark="ghost-login"))}
    )
    client, _, _ = make_client(conn, mock)
    r = client.post(
        "/webhooks/afdian",
        json={"data": {"type": "order", "order": {"out_trade_no": "W3"}}},
    )
    assert r.status_code == 200
    assert order_row(conn, "W3") is None
    assert db.get_user_by_id(conn, user_id).plan == "free"


def test_webhook_double_callback_idempotent(conn, user_id):
    order = make_order(no="W4", remark="octocat")
    mock = AfdianMock({"W4": afdian_payload(order)})
    client, _, _ = make_client(conn, mock)
    body = {"data": {"type": "order", "order": {"out_trade_no": "W4"}}}

    r1 = client.post("/webhooks/afdian", json=body)
    first_expiry = db.get_user_by_id(conn, user_id).plan_expires_at
    time.sleep(0.02)
    r2 = client.post("/webhooks/afdian", json=body)

    assert r1.status_code == r2.status_code == 200
    assert db.get_user_by_id(conn, user_id).plan_expires_at == first_expiry
    assert (
        conn.execute(
            "SELECT COUNT(*) AS c FROM afdian_orders WHERE out_trade_no = 'W4'"
        ).fetchone()["c"]
        == 1
    )


# ---- 6. POST /sync/activate ----


def test_activate_route_requires_auth(conn):
    mock = AfdianMock()
    client, _, _ = make_client(conn, mock)
    r = client.post("/sync/activate", json={"orderNo": "A1"})
    assert r.status_code == 401
    assert r.json() == {"error": "unauthorized"}
    assert mock.requests == []


def test_activate_route_503_when_unconfigured(conn, user_id):
    mock = AfdianMock()
    client, _, _ = make_client(conn, mock, configured=False)
    r = client.post(
        "/sync/activate", json={"orderNo": "A1"}, headers=auth()
    )
    assert r.status_code == 503
    assert r.json() == {"error": "afdian_not_configured"}
    assert mock.requests == []


def test_activate_route_invalid_json_400(conn, user_id):
    mock = AfdianMock()
    client, _, _ = make_client(conn, mock)
    r = client.post(
        "/sync/activate",
        content=b"oops",
        headers={**auth(), "Content-Type": "application/json"},
    )
    assert r.status_code == 400
    assert r.json() == {"error": "invalid_body"}
    assert mock.requests == []


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"orderNo": ""},
        {"orderNo": "   "},
        {"orderNo": 123},
        {"wrong": "field"},
    ],
)
def test_activate_route_order_no_required_400(conn, user_id, body):
    mock = AfdianMock()
    client, _, _ = make_client(conn, mock)
    r = client.post("/sync/activate", json=body, headers=auth())
    assert r.status_code == 400
    assert r.json() == {"error": "order_no_required"}
    assert mock.requests == []


def test_activate_route_ghost_user_404(conn):
    mock = AfdianMock({"A1": afdian_payload(make_order(no="A1"))})
    client, _, _ = make_client(conn, mock)
    r = client.post(
        "/sync/activate",
        json={"orderNo": "A1"},
        headers=auth(sub="user-ghost", login="ghost"),
    )
    assert r.status_code == 404
    assert r.json() == {"error": "not_found"}
    assert mock.requests == []


def test_activate_route_order_not_found_404(conn, user_id):
    mock = AfdianMock()
    client, _, _ = make_client(conn, mock)
    r = client.post(
        "/sync/activate", json={"orderNo": "MISSING"}, headers=auth()
    )
    assert r.status_code == 404
    assert r.json() == {"error": "order_not_found"}
    assert len(mock.requests) == 1


def test_activate_route_order_not_paid_400(conn, user_id):
    mock = AfdianMock(
        {"A2": afdian_payload(make_order(no="A2", status=3))}
    )
    client, _, _ = make_client(conn, mock)
    r = client.post(
        "/sync/activate", json={"orderNo": "A2"}, headers=auth()
    )
    assert r.status_code == 400
    assert r.json() == {"error": "order_not_paid"}


def test_activate_route_remark_mismatch_403(conn, user_id):
    mock = AfdianMock(
        {"A3": afdian_payload(make_order(no="A3", remark="other-guy"))}
    )
    client, _, _ = make_client(conn, mock)
    r = client.post(
        "/sync/activate", json={"orderNo": "A3"}, headers=auth()
    )
    assert r.status_code == 403
    assert r.json() == {"error": "remark_mismatch"}
    assert order_row(conn, "A3") is None


def test_activate_route_ineligible_plan_400(conn, user_id):
    # status=2 过路由状态守卫，product_type=2 在激活函数内被判不合格
    mock = AfdianMock(
        {"A4": afdian_payload(make_order(no="A4", product_type=2))}
    )
    client, _, _ = make_client(conn, mock)
    r = client.post(
        "/sync/activate", json={"orderNo": "A4"}, headers=auth()
    )
    assert r.status_code == 400
    assert r.json() == {"error": "ineligible_plan"}
    assert order_row(conn, "A4") is None

    # plan 白名单不匹配同样 400
    mock2 = AfdianMock(
        {"A5": afdian_payload(make_order(no="A5", plan_id="plan-x"))}
    )
    client2, _, _ = make_client(conn, mock2, plan_ids=("plan-a",))
    r2 = client2.post(
        "/sync/activate", json={"orderNo": "A5"}, headers=auth()
    )
    assert r2.status_code == 400
    assert r2.json() == {"error": "ineligible_plan"}


def test_activate_route_success_me_reflects_pro(conn, user_id):
    mock = AfdianMock(
        {"A6": afdian_payload(make_order(no="A6", remark=""))}
    )
    client, _, _ = make_client(conn, mock)

    r = client.post(
        "/sync/activate", json={"orderNo": "A6"}, headers=auth()
    )
    assert r.status_code == 200
    payload = r.json()
    assert payload["plan"] == "pro"
    assert isinstance(payload["planExpiresAt"], int)
    expected = int(time.time() * 1000) + MONTH_MS
    assert abs(payload["planExpiresAt"] - expected) < 5000

    # github: 前缀 + 大小写混合的备注也能命中当前用户（第二单验证书写形式）
    mock.responses["A7"] = afdian_payload(
        make_order(no="A7", remark="github:OctoCat", month=1)
    )
    r2 = client.post(
        "/sync/activate", json={"orderNo": "A7"}, headers=auth()
    )
    assert r2.status_code == 200
    # 续费在 A6 到期时间基础上叠加 31 天
    assert r2.json()["planExpiresAt"] == payload["planExpiresAt"] + MONTH_MS

    me = client.get("/me", headers=auth())
    assert me.status_code == 200
    assert me.json()["plan"] == "pro"


def test_activate_route_idempotent_same_order(conn, user_id):
    mock = AfdianMock(
        {"A8": afdian_payload(make_order(no="A8", remark="octocat"))}
    )
    client, _, _ = make_client(conn, mock)
    r1 = client.post(
        "/sync/activate", json={"orderNo": "A8"}, headers=auth()
    )
    time.sleep(0.02)
    r2 = client.post(
        "/sync/activate", json={"orderNo": "A8"}, headers=auth()
    )
    assert r1.status_code == r2.status_code == 200
    assert r1.json()["planExpiresAt"] == r2.json()["planExpiresAt"]
    assert (
        conn.execute(
            "SELECT COUNT(*) AS c FROM afdian_orders WHERE out_trade_no = 'A8'"
        ).fetchone()["c"]
        == 1
    )
    # 每次都要回查开放平台（幂等只在 DB 激活层）
    assert len(mock.requests) == 2
