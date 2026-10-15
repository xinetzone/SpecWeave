"""极简 ASGI 应用与 HTTP 路由（零第三方依赖，适配 Vercel Python Runtime）。

路由一览：
  GET  /                       客服对话页
  GET  /admin                  管理后台页
  GET  /static/<file>          静态资源（白名单）
  GET  /api/health             健康检查（云端/大模型就绪状态）
  POST /api/chat               一轮对话（支持 BYOK 请求头）
  GET  /api/history            当前会话历史
  POST /api/feedback           满意度评价
  POST /api/session            新建会话
  GET  /api/admin/overview     统计总览
  GET  /api/admin/sessions     会话列表
  GET  /api/admin/sessions/:id 会话明细
  GET  /api/admin/faq          知识库列表
  POST /api/admin/faq          新增知识库条目
"""

import asyncio
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs

from .agent import Agent
from .config import Config
from .faq import FaqIndex
from .store import Feedback, Store, build_store, new_id

SESSION_COOKIE = "cs_sid"
ADMIN_COOKIE = "cs_admin_token"
ADMIN_HEADER = "x-admin-token"
# Vercel 内部重写可能把请求路径替换为函数路径，需要还原原始路径
FUNCTION_PATHS = ("/api/index", "/api/index.py", "/api/index/")

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".json": "application/json; charset=utf-8",
}
STATIC_WHITELIST = {"index.html", "admin.html", "styles.css", "chat.js", "admin.js"}

Headers = List[Tuple[bytes, bytes]]
Response = Tuple[int, Headers, bytes]


# ---- 请求 / 响应 ---------------------------------------------------------


class Request:
    def __init__(self, scope: Dict[str, Any], body: bytes) -> None:
        self.method: str = str(scope.get("method", "GET")).upper()
        self.path: str = str(scope.get("path", "/") or "/")
        self.headers: Dict[str, str] = {
            k.decode("latin-1").lower(): v.decode("latin-1")
            for k, v in scope.get("headers", [])
        }
        raw_query = scope.get("query_string", b"") or b""
        parsed = parse_qs(raw_query.decode("latin-1"))
        self.query: Dict[str, str] = {k: v[0] for k, v in parsed.items() if v}
        self._body = body
        self.path = self._effective_path()

    def _effective_path(self) -> str:
        """兼容 Vercel 内部重写：请求路径可能被替换为函数路径 /api/index。

        还原优先级：Vercel 原始路径头 > 重写携带的 ?p= 查询参数 > 当前路径。
        """
        if self.path not in FUNCTION_PATHS:
            return self.path
        for header in ("x-original-path", "x-vercel-original-path", "x-matched-path"):
            value = self.headers.get(header)
            if value and value not in FUNCTION_PATHS:
                return value
        value = self.query.get("p") or "/"
        return value if value.startswith("/") else "/" + value

    @property
    def cookies(self) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for part in (self.headers.get("cookie") or "").split(";"):
            if "=" in part:
                key, value = part.strip().split("=", 1)
                out[key] = value
        return out

    def json(self) -> Dict[str, Any]:
        if not self._body:
            return {}
        try:
            data = json.loads(self._body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {}
        return data if isinstance(data, dict) else {}


def _cookie_header(name: str, value: str, max_age: int = 86400 * 30) -> str:
    return f"{name}={value}; Path=/; Max-Age={max_age}; HttpOnly; SameSite=Lax"


def _respond(
    status: int,
    body: bytes,
    content_type: str,
    cookies: Optional[Dict[str, str]] = None,
) -> Response:
    headers: Headers = [
        (b"content-type", content_type.encode("latin-1")),
        (b"content-length", str(len(body)).encode("latin-1")),
        (b"cache-control", b"no-store"),
    ]
    for name, value in (cookies or {}).items():
        headers.append((b"set-cookie", _cookie_header(name, value).encode("latin-1")))
    return status, headers, body


def _json(status: int, data: Any, cookies: Optional[Dict[str, str]] = None) -> Response:
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    return _respond(status, payload, "application/json; charset=utf-8", cookies)


def _text(status: int, message: str) -> Response:
    return _respond(status, message.encode("utf-8"), "text/plain; charset=utf-8")


# ---- 静态资源 ------------------------------------------------------------


def _web_dir() -> Path:
    here = Path(__file__).resolve()
    candidates = [
        here.parent.parent.parent / "web",  # src/support_agent -> 应用根
        here.parent.parent / "web",
        Path.cwd() / "web",
    ]
    for base in candidates:
        if base.is_dir():
            return base
    return candidates[0]


def _static(name: str) -> Optional[Response]:
    if name not in STATIC_WHITELIST:
        return None
    path = _web_dir() / name
    if not path.is_file():
        return None
    ctype = MIME.get(path.suffix, "application/octet-stream")
    return _respond(200, path.read_bytes(), ctype)


def _page(name: str) -> Response:
    resp = _static(name)
    if resp is None:
        return _text(500, f"静态页面缺失：{name}（请检查 web/ 目录是否随源码一起部署）")
    return resp


# ---- 上下文 --------------------------------------------------------------


class Context:
    def __init__(self, cfg: Config, store: Store, faq: FaqIndex) -> None:
        self.cfg = cfg
        self.store = store
        self.faq = faq
        self.agent = Agent(cfg, store, faq)


# ---- 业务处理 ------------------------------------------------------------


def _session_id(req: Request) -> str:
    for source in (req.cookies.get(SESSION_COOKIE), req.query.get("session_id")):
        if source:
            return str(source)
    return new_id("s")


def _chat(ctx: Context, req: Request) -> Response:
    body = req.json()
    text = str(body.get("message") or "").strip()
    if not text:
        return _json(400, {"error": "empty_message", "message": "请输入内容"})
    text = text[: ctx.cfg.max_input_chars]

    session_id = str(body.get("session_id") or "").strip() or _session_id(req)
    cfg = ctx.cfg.with_llm(
        base_url=req.headers.get("x-llm-base-url") or str(body.get("llm_base_url") or ""),
        api_key=req.headers.get("x-llm-api-key") or str(body.get("llm_api_key") or ""),
        model=req.headers.get("x-llm-model") or str(body.get("llm_model") or ""),
    )
    try:
        result = ctx.agent.handle(session_id, text, cfg=cfg)
    except Exception as exc:  # 永不 500
        return _json(200, {
            "session_id": session_id,
            "reply": f"服务暂时不可用（{exc}）。已为您记录问题，请稍后重试或回复「转人工」。",
            "intent": "other",
            "intent_label": "通用咨询",
            "source": "human",
            "needs_human": True,
            "ticket_id": new_id("tk"),
            "faq": [],
            "latency_ms": 0,
            "degraded": True,
        })

    return _json(200, result.to_dict(), cookies={SESSION_COOKIE: session_id})


def _history(ctx: Context, req: Request) -> Response:
    session_id = req.query.get("session_id") or _session_id(req)
    messages = ctx.store.session_messages(session_id)
    return _json(
        200,
        {
            "session_id": session_id,
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "intent": m.intent,
                    "source": m.source,
                    "needs_human": m.needs_human,
                    "created_at": m.created_at,
                }
                for m in messages
            ],
        },
    )


def _feedback(ctx: Context, req: Request) -> Response:
    body = req.json()
    try:
        rating = int(body.get("rating") or 0)
    except (TypeError, ValueError):
        rating = 0
    if rating < 1 or rating > 5:
        return _json(400, {"error": "invalid_rating", "message": "评分需为 1-5"})
    session_id = str(body.get("session_id") or "").strip() or _session_id(req)
    ctx.store.ensure_session(session_id)
    ctx.store.add_feedback(
        Feedback(
            session_id=session_id,
            rating=rating,
            resolved=bool(body.get("resolved", rating >= 4)),
            comment=str(body.get("comment") or "")[:500],
        )
    )
    return _json(200, {"ok": True, "session_id": session_id, "rating": rating})


def _new_session(ctx: Context, req: Request) -> Response:
    session_id = new_id("s")
    ctx.store.ensure_session(session_id)
    return _json(200, {"session_id": session_id}, cookies={SESSION_COOKIE: session_id})


def _health(ctx: Context, req: Request) -> Response:
    health = ctx.store.health()
    return _json(
        200,
        {
            "ok": True,
            "service": "support-agent",
            "cloud_ready": ctx.cfg.cloud_ready,
            "llm_ready": ctx.cfg.llm_ready,
            "storage": health,
            "degraded": bool(getattr(ctx.store, "degraded", False)),
            "faq_count": len(ctx.faq.entries),
        },
    )


# ---- 管理后台 ------------------------------------------------------------


def _admin_guard(ctx: Context, req: Request) -> Optional[Response]:
    if not ctx.cfg.admin_token:
        return _json(
            503,
            {
                "error": "admin_token_missing",
                "message": "请配置环境变量 ADMIN_TOKEN 后重启服务，再访问管理后台",
            },
        )
    provided = (
        req.headers.get(ADMIN_HEADER)
        or req.query.get("token")
        or req.cookies.get(ADMIN_COOKIE)
        or ""
    )
    if (provided or "").strip() != ctx.cfg.admin_token.strip():
        return _json(401, {"error": "unauthorized", "message": "ADMIN_TOKEN 不正确"})
    return None


def _admin_overview(ctx: Context, req: Request) -> Response:
    guard = _admin_guard(ctx, req)
    if guard:
        return guard
    try:
        limit = int(req.query.get("limit") or 200)
    except ValueError:
        limit = 200
    stats = ctx.store.stats(limit=min(max(limit, 1), 500))
    stats["cloud_ready"] = ctx.cfg.cloud_ready
    stats["llm_ready"] = ctx.cfg.llm_ready
    stats["faq_count"] = len(ctx.faq.entries)
    return _json(200, stats)


def _admin_sessions(ctx: Context, req: Request) -> Response:
    guard = _admin_guard(ctx, req)
    if guard:
        return guard
    try:
        limit = int(req.query.get("limit") or 50)
    except ValueError:
        limit = 50
    keyword = (req.query.get("q") or "").strip()
    sessions = ctx.store.list_sessions(limit=min(max(limit, 1), 200))
    rows = []
    for session in sessions:
        if keyword and keyword not in session.id and keyword not in (session.last_intent or ""):
            continue
        rows.append(
            {
                "id": session.id,
                "status": session.status,
                "transferred": session.transferred,
                "last_intent": session.last_intent,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
            }
        )
    return _json(200, {"sessions": rows, "total": len(rows)})


def _admin_session_detail(ctx: Context, req: Request, session_id: str) -> Response:
    guard = _admin_guard(ctx, req)
    if guard:
        return guard
    messages = ctx.store.session_messages(session_id)
    if not messages:
        sessions = ctx.store.list_sessions(limit=200)
        if not any(s.id == session_id for s in sessions):
            return _json(404, {"error": "not_found"})
    feedback = [f for f in ctx.store.list_feedback() if f.session_id == session_id]
    return _json(
        200,
        {
            "session_id": session_id,
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "intent": m.intent,
                    "source": m.source,
                    "needs_human": m.needs_human,
                    "low_confidence": m.low_confidence,
                    "faq_ids": m.faq_ids,
                    "latency_ms": m.latency_ms,
                    "created_at": m.created_at,
                }
                for m in messages
            ],
            "feedback": [
                {
                    "rating": f.rating,
                    "resolved": f.resolved,
                    "comment": f.comment,
                    "created_at": f.created_at,
                }
                for f in feedback
            ],
        },
    )


def _admin_faq_list(ctx: Context, req: Request) -> Response:
    guard = _admin_guard(ctx, req)
    if guard:
        return guard
    return _json(200, {"faq": [entry.to_dict() for entry in ctx.faq.entries]})


def _admin_faq_create(ctx: Context, req: Request) -> Response:
    guard = _admin_guard(ctx, req)
    if guard:
        return guard
    body = req.json()
    question = str(body.get("question") or "").strip()
    answer = str(body.get("answer") or "").strip()
    if not question or not answer:
        return _json(400, {"error": "invalid_faq", "message": "question 与 answer 必填"})
    entry = {
        "id": str(body.get("id") or "").strip() or f"faq-{uuid.uuid4().hex[:10]}",
        "category": str(body.get("category") or "other"),
        "question": question,
        "answer": answer,
        "keywords": str(body.get("keywords") or ""),
    }
    ctx.store.add_faq(entry)
    ctx.faq.reload_remote(ctx.store)
    return _json(200, {"ok": True, "entry": entry})


# ---- 路由分发 ------------------------------------------------------------


def dispatch(ctx: Context, req: Request) -> Response:
    path = req.path.rstrip("/") or "/"
    method = req.method

    if method == "GET" and path == "/":
        return _page("index.html")
    if method == "GET" and path in ("/admin", "/admin.html"):
        return _page("admin.html")
    if method == "GET" and path.startswith("/static/"):
        resp = _static(path[len("/static/") :])
        return resp or _json(404, {"error": "not_found"})
    if method == "GET" and path == "/favicon.ico":
        return _respond(200, b"", "image/x-icon")

    if method == "GET" and path == "/api/health":
        return _health(ctx, req)
    if method == "POST" and path == "/api/chat":
        return _chat(ctx, req)
    if method == "GET" and path == "/api/history":
        return _history(ctx, req)
    if method == "POST" and path == "/api/feedback":
        return _feedback(ctx, req)
    if method == "POST" and path == "/api/session":
        return _new_session(ctx, req)

    if path == "/api/admin/overview" and method == "GET":
        return _admin_overview(ctx, req)
    if path == "/api/admin/sessions" and method == "GET":
        return _admin_sessions(ctx, req)
    if path.startswith("/api/admin/sessions/") and method == "GET":
        return _admin_session_detail(ctx, req, path[len("/api/admin/sessions/") :])
    if path == "/api/admin/faq" and method == "GET":
        return _admin_faq_list(ctx, req)
    if path == "/api/admin/faq" and method == "POST":
        return _admin_faq_create(ctx, req)

    return _json(404, {"error": "not_found", "path": path})


def build_context(
    cfg: Optional[Config] = None,
    store: Optional[Store] = None,
    faq: Optional[FaqIndex] = None,
) -> Context:
    cfg = cfg or Config.from_env()
    store = store or build_store(cfg)
    faq = faq or FaqIndex.load(cfg, store)
    return Context(cfg, store, faq)


async def _read_body(receive) -> bytes:
    chunks: List[bytes] = []
    while True:
        message = await receive()
        mtype = message.get("type")
        if mtype == "http.request":
            chunks.append(message.get("body", b""))
            if not message.get("more_body"):
                break
        elif mtype == "http.disconnect":
            break
    return b"".join(chunks)


def build_app(
    cfg: Optional[Config] = None,
    store: Optional[Store] = None,
    faq: Optional[FaqIndex] = None,
):
    """构建 ASGI 应用（Vercel 直接导出该对象即可）。"""
    ctx = build_context(cfg, store, faq)

    async def app(scope, receive, send):
        if scope.get("type") != "http":
            return
        body = await _read_body(receive)
        request = Request(scope, body)
        loop = asyncio.get_running_loop()
        status, headers, payload = await loop.run_in_executor(None, dispatch, ctx, request)
        await send({"type": "http.response.start", "status": status, "headers": headers})
        await send({"type": "http.response.body", "body": payload})

    return app


__all__ = ["build_app", "build_context", "dispatch", "Request", "Context"]
