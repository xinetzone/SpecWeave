"""HTTP 层测试：路由、会话 Cookie、满意度、管理后台鉴权。"""

import json

from support_agent import llm
from support_agent.asgi import Request, build_context, dispatch
from support_agent.config import Config
from support_agent.faq import FaqIndex
from support_agent.store import MemoryStore

ADMIN = "admintoken"


def ctx_with(chat=None):
    cfg = Config(llm_api_key="sk-test", llm_base_url="https://example.test/v1", admin_token=ADMIN)
    store = MemoryStore()
    faq = FaqIndex()
    context = build_context(cfg, store, faq)
    if chat is not None:
        context.agent.chat = chat
    return context


def call(context, method, path, body=None, headers=None, query=""):
    raw = json.dumps(body or {}).encode("utf-8") if body is not None else b""
    header_list = [(b"content-type", b"application/json")]
    for key, value in (headers or {}).items():
        header_list.append((key.encode("latin-1"), value.encode("latin-1")))
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "query_string": query.encode("latin-1"),
        "headers": header_list,
    }
    return dispatch(context, Request(scope, raw))


def payload(response):
    return json.loads(response[2].decode("utf-8"))


def echo_chat(_cfg, messages, **kwargs):
    return "这是回复", 11


def test_index_page_served():
    context = ctx_with(echo_chat)
    status, headers, body = call(context, "GET", "/")
    assert status == 200
    assert b"text/html" in dict(headers)[b"content-type"]


def test_admin_page_served():
    context = ctx_with(echo_chat)
    status, _headers, body = call(context, "GET", "/admin")
    assert status == 200
    assert "管理后台" in body.decode("utf-8")


def test_health_reports_readiness():
    context = ctx_with(echo_chat)
    data = payload(call(context, "GET", "/api/health"))
    assert data["ok"] is True
    assert data["llm_ready"] is True
    assert data["cloud_ready"] is False


def test_chat_returns_reply_and_sets_cookie():
    context = ctx_with(echo_chat)
    status, headers, body = call(context, "POST", "/api/chat", {"message": "我要退款"})
    assert status == 200
    data = json.loads(body.decode("utf-8"))
    assert data["intent"] == "refund"
    assert data["reply"] == "这是回复"
    cookie_headers = [v for k, v in headers if k == b"set-cookie"]
    assert any(b"cs_sid=" in v for v in cookie_headers)


def test_chat_rejects_empty_message():
    context = ctx_with(echo_chat)
    status, _headers, body = call(context, "POST", "/api/chat", {"message": "  "})
    assert status == 400


def test_chat_survives_agent_failure():
    def broken(_cfg, messages, **kwargs):
        raise llm.LLMError("down")

    context = ctx_with(broken)
    status, _headers, body = call(context, "POST", "/api/chat", {"message": "zzz 无关"})
    assert status == 200
    assert json.loads(body.decode("utf-8"))["needs_human"] is True


def test_feedback_validates_rating():
    context = ctx_with(echo_chat)
    call(context, "POST", "/api/chat", {"message": "你好", "session_id": "s-1"})
    bad = call(context, "POST", "/api/feedback", {"rating": 9, "session_id": "s-1"})
    assert bad[0] == 400
    ok = payload(call(context, "POST", "/api/feedback", {"rating": 5, "session_id": "s-1"}))
    assert ok["ok"] is True


def test_history_returns_messages():
    context = ctx_with(echo_chat)
    call(context, "POST", "/api/chat", {"message": "你好", "session_id": "s-2"})
    data = payload(call(context, "GET", "/api/history", query="session_id=s-2"))
    assert len(data["messages"]) == 2


def test_admin_requires_token():
    context = ctx_with(echo_chat)
    assert call(context, "GET", "/api/admin/overview")[0] == 401
    assert call(context, "GET", "/api/admin/overview", headers={"x-admin-token": ADMIN})[0] == 200


def test_admin_without_configured_token_is_503():
    cfg = Config(llm_api_key="", admin_token="")
    context = build_context(cfg, MemoryStore(), FaqIndex())
    assert call(context, "GET", "/api/admin/overview")[0] == 503


def test_admin_overview_and_session_detail():
    context = ctx_with(echo_chat)
    call(context, "POST", "/api/chat", {"message": "我要退款", "session_id": "s-3"})
    headers = {"x-admin-token": ADMIN}

    overview = payload(call(context, "GET", "/api/admin/overview", headers=headers))
    assert overview["sessions"] >= 1
    assert overview["intent_distribution"].get("refund") == 1

    listing = payload(call(context, "GET", "/api/admin/sessions", headers=headers))
    assert any(row["id"] == "s-3" for row in listing["sessions"])

    detail = payload(call(context, "GET", "/api/admin/sessions/s-3", headers=headers))
    assert len(detail["messages"]) == 2


def test_admin_faq_create():
    context = ctx_with(echo_chat)
    headers = {"x-admin-token": ADMIN, "content-type": "application/json"}
    resp = call(
        context,
        "POST",
        "/api/admin/faq",
        {"question": "怎么改绑定手机号", "answer": "个人中心 → 安全设置", "keywords": "手机号,改绑定"},
        headers=headers,
    )
    assert resp[0] == 200
    listing = payload(call(context, "GET", "/api/admin/faq", headers=headers))
    assert any(item["question"] == "怎么改绑定手机号" for item in listing["faq"])


def test_vercel_rewrite_path_is_restored_from_query():
    """Vercel 内部重写把路径替换为 /api/index 时，应从 ?p= 还原。"""
    context = ctx_with(echo_chat)
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/index",
        "query_string": b"p=api%2Fhealth",
        "headers": [],
    }
    data = payload(dispatch(context, Request(scope, b"")))
    assert data["ok"] is True
    assert data["service"] == "support-agent"


def test_vercel_rewrite_root_falls_back_to_page():
    context = ctx_with(echo_chat)
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/index",
        "query_string": b"p=",
        "headers": [],
    }
    status, _headers, body = dispatch(context, Request(scope, b""))
    assert status == 200
    assert "<html" in body.decode("utf-8").lower()


def test_unknown_route_404():
    context = ctx_with(echo_chat)
    assert call(context, "GET", "/api/nope")[0] == 404
