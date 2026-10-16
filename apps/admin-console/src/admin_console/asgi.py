"""极简 ASGI 应用与 HTTP 路由（零第三方依赖，适配 Vercel Python Runtime）。

路由一览：
  GET  /                        重定向到 /app
  GET  /login                   登录页
  GET  /app                     后台单页（未登录跳 /login）
  GET  /static/<file>           静态资源（白名单）
  GET  /api/health              健康检查（云端/会话密钥就绪状态）
  POST /api/auth/login          登录
  POST /api/auth/logout         登出
  GET  /api/auth/me             当前账号
  GET  /api/meta                分类 / 标签 / 状态枚举
  GET  /api/dashboard           看板聚合
  GET  /api/items               条目列表（搜索/筛选/排序/分页）
  POST /api/items               新建条目
  GET  /api/items/:id           条目详情
  PATCH/DELETE /api/items/:id   更新 / 删除（PATCH 支持乐观并发）
  POST /api/items/bulk          批量改状态 / 删除
  GET/POST /api/categories      分类列表 / 新建
  PATCH/DELETE /api/categories/:id
  GET/POST /api/tags            标签列表 / 新建
  DELETE /api/tags/:id
  POST /api/uploads             上传（裸二进制 + X-File-Name 头）
  GET  /api/attachments         附件列表
  DELETE /api/attachments/:id
  GET  /api/logs                操作日志
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, unquote

from .config import Config
from .security import (
    CSRF_COOKIE,
    CSRF_HEADER,
    SESSION_COOKIE,
    LoginLimiter,
    csrf_ok,
    new_csrf_token,
    origin_ok,
    sign_session,
    verify_session,
)
from .storage import Storage, StorageError
from .store import Conflict, MemoryStore, SupabaseStore, build_store
from .validate import (
    STATUSES,
    STATUS_LABELS,
    clean_item,
    clean_taxonomy,
    first_error,
)

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".json": "application/json; charset=utf-8",
}
STATIC_WHITELIST = {"login.html", "app.html", "styles.css", "app.js"}
# Vercel 内部重写可能把请求路径替换为函数路径，需要还原原始路径
FUNCTION_PATHS = ("/api/index", "/api/index.py", "/api/index/")

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
        self.body = body
        self.path = self._effective_path()

    def _effective_path(self) -> str:
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
        if not self.body:
            return {}
        try:
            data = json.loads(self.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {}
        return data if isinstance(data, dict) else {}

    @property
    def is_secure(self) -> bool:
        proto = (self.headers.get("x-forwarded-proto") or "").lower()
        return proto == "https"


def _cookie(name: str, value: str, max_age: int = 0, httponly: bool = True, secure: bool = False) -> str:
    parts = [f"{name}={value}", "Path=/", "SameSite=Lax"]
    if max_age:
        parts.append(f"Max-Age={max_age}")
    else:
        parts.append("Max-Age=0")
    if httponly:
        parts.append("HttpOnly")
    if secure:
        parts.append("Secure")
    return "; ".join(parts)


def _respond(
    status: int,
    body: bytes,
    content_type: str,
    cookies: Optional[List[str]] = None,
    location: str = "",
) -> Response:
    headers: Headers = [
        (b"content-type", content_type.encode("latin-1")),
        (b"content-length", str(len(body)).encode("latin-1")),
        (b"cache-control", b"no-store"),
        (b"x-content-type-options", b"nosniff"),
        (b"referrer-policy", b"no-referrer"),
    ]
    if location:
        headers.append((b"location", location.encode("latin-1")))
    for value in cookies or []:
        headers.append((b"set-cookie", value.encode("latin-1")))
    return status, headers, body


def _json(status: int, data: Any, cookies: Optional[List[str]] = None, location: str = "") -> Response:
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    return _respond(status, payload, "application/json; charset=utf-8", cookies, location)


def _text(status: int, message: str) -> Response:
    return _respond(status, message.encode("utf-8"), "text/plain; charset=utf-8")


# ---- 静态资源 ------------------------------------------------------------


def _web_dir() -> Path:
    here = Path(__file__).resolve()
    candidates = [here.parent.parent.parent / "web", here.parent.parent / "web", Path.cwd() / "web"]
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
    return _respond(200, path.read_bytes(), MIME.get(path.suffix, "application/octet-stream"))


def _page(name: str) -> Response:
    resp = _static(name)
    if resp is None:
        return _text(500, f"静态页面缺失：{name}（请检查 web/ 目录是否随源码一起部署）")
    return resp


# ---- 上下文 --------------------------------------------------------------


class Context:
    def __init__(self, cfg: Config, store, storage: Storage) -> None:
        self.cfg = cfg
        self.store = store
        self.storage = storage
        self.limiter = LoginLimiter()


def build_context(cfg: Optional[Config] = None, store=None, storage: Optional[Storage] = None) -> Context:
    cfg = cfg or Config.from_env()
    store = store if store is not None else build_store(cfg)
    storage = storage if storage is not None else Storage(cfg)
    return Context(cfg, store, storage)


# ---- 鉴权 ----------------------------------------------------------------


def current_user(ctx: Context, req: Request) -> Optional[Dict[str, Any]]:
    token = req.cookies.get(SESSION_COOKIE) or ""
    if not token:
        return None
    return verify_session(token, ctx.cfg.session_secret)


def _require_user(ctx: Context, req: Request) -> Tuple[Optional[Dict[str, Any]], Optional[Response]]:
    user = current_user(ctx, req)
    if not user:
        return None, _json(401, {"error": "unauthorized", "message": "请先登录"})
    return user, None


def _require_write(ctx: Context, req: Request) -> Tuple[Optional[Dict[str, Any]], Optional[Response]]:
    """写操作三重校验：登录 + Origin 同源 + CSRF 双提交。"""
    user, guard = _require_user(ctx, req)
    if guard:
        return None, guard
    if not origin_ok(req.headers):
        return None, _json(403, {"error": "bad_origin", "message": "跨站请求已被拒绝"})
    if not csrf_ok(req.headers.get(CSRF_HEADER) or "", req.cookies.get(CSRF_COOKIE) or ""):
        return None, _json(403, {"error": "bad_csrf", "message": "CSRF 校验失败，请刷新页面重试"})
    return user, None


def _require_json(ctx: Context, req: Request) -> Tuple[Optional[Dict[str, Any]], Optional[Response]]:
    user, guard = _require_write(ctx, req)
    if guard:
        return None, guard
    if "application/json" not in (req.headers.get("content-type") or "").lower():
        return None, _json(415, {"error": "unsupported_media_type", "message": "请求体必须是 application/json"})
    return user, None


# ---- 业务处理 ------------------------------------------------------------


def _health(ctx: Context, req: Request) -> Response:
    return _json(200, {
        "ok": True,
        "service": "admin-console",
        "cloud_ready": ctx.cfg.cloud_ready,
        "secret_persistent": not ctx.cfg.ephemeral_secret,
        "storage": ctx.store.health(),
        "degraded": bool(getattr(ctx.store, "degraded", False)),
        "demo_login": bool(getattr(ctx.store, "degraded", False) and ctx.cfg.demo_admin_enabled),
    })


def _login(ctx: Context, req: Request) -> Response:
    if not origin_ok(req.headers):
        return _json(403, {"error": "bad_origin", "message": "跨站请求已被拒绝"})
    if "application/json" not in (req.headers.get("content-type") or "").lower():
        return _json(415, {"error": "unsupported_media_type", "message": "请求体必须是 application/json"})
    body = req.json()
    email = str(body.get("email") or "").strip().lower()
    password = str(body.get("password") or "")
    if not email or not password:
        return _json(400, {"error": "invalid_input", "message": "邮箱与口令不能为空"})
    if ctx.limiter.is_locked(email):
        return _json(429, {"error": "too_many_attempts", "message": "尝试过于频繁，请 10 分钟后再试"})

    admin = ctx.store.verify_credentials(email, password)
    if not admin:
        ctx.limiter.register_failure(email)
        # 恒定提示：不区分账号不存在与口令错误
        return _json(401, {"error": "invalid_credentials", "message": "邮箱或口令不正确"})
    ctx.limiter.register_success(email)
    ctx.store.touch_login(str(admin.get("id") or ""))

    role = str(admin.get("role") or "admin")
    token = sign_session(ctx.cfg.session_secret, str(admin.get("email")), role,
                         ctx.cfg.session_ttl, str(admin.get("display_name") or ""))
    csrf = new_csrf_token()
    secure = req.is_secure
    cookies = [
        _cookie(SESSION_COOKIE, token, ctx.cfg.session_ttl, httponly=True, secure=secure),
        _cookie(CSRF_COOKIE, csrf, ctx.cfg.session_ttl, httponly=False, secure=secure),
    ]
    return _json(200, {
        "ok": True,
        "user": {"email": admin.get("email"), "display_name": admin.get("display_name"), "role": role},
        "csrf": csrf,
    }, cookies=cookies)


def _logout(ctx: Context, req: Request) -> Response:
    secure = req.is_secure
    cookies = [
        _cookie(SESSION_COOKIE, "", 0, httponly=True, secure=secure),
        _cookie(CSRF_COOKIE, "", 0, httponly=False, secure=secure),
    ]
    return _json(200, {"ok": True}, cookies=cookies)


def _me(ctx: Context, req: Request) -> Response:
    user = current_user(ctx, req)
    if not user:
        return _json(401, {"error": "unauthorized", "message": "请先登录"})
    return _json(200, {"user": user})


def _meta(ctx: Context, req: Request) -> Response:
    user, guard = _require_user(ctx, req)
    if guard:
        return guard
    return _json(200, {
        "categories": ctx.store.list_categories(),
        "tags": [str(t.get("name")) for t in ctx.store.list_tags()],
        "statuses": [{"value": s, "label": STATUS_LABELS[s]} for s in STATUSES],
        "upload": {
            "max_bytes": ctx.cfg.max_upload_bytes,
            "types": list(ctx.cfg.upload_types),
            "enabled": ctx.storage.enabled,
        },
        "role": str(user.get("role") or "admin"),
        "user": {"email": user.get("sub"), "display_name": user.get("name"), "role": user.get("role")},
    })


def _decorate(ctx: Context, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    names = {str(c.get("id")): str(c.get("name") or "") for c in ctx.store.list_categories()}
    for row in rows:
        row["category_name"] = names.get(str(row.get("category_id") or ""), "")
    return rows


def _dashboard(ctx: Context, req: Request) -> Response:
    user, guard = _require_user(ctx, req)
    if guard:
        return guard
    data = ctx.store.dashboard()
    data["degraded"] = bool(getattr(ctx.store, "degraded", False))
    data["cloud_ready"] = ctx.cfg.cloud_ready
    return _json(200, data)


def _items_list(ctx: Context, req: Request) -> Response:
    user, guard = _require_user(ctx, req)
    if guard:
        return guard
    params = {
        "q": req.query.get("q") or "",
        "status": req.query.get("status") or "",
        "category_id": req.query.get("category_id") or "",
        "tag": req.query.get("tag") or "",
        "sort": req.query.get("sort") or "",
        "order": req.query.get("order") or "",
        "page": req.query.get("page") or "",
        "page_size": req.query.get("page_size") or "",
    }
    rows, total = ctx.store.list_items(params)
    page = int(params["page"] or 0) or 1
    try:
        size = int(params["page_size"] or 0) or ctx.cfg.page_size
    except ValueError:
        size = ctx.cfg.page_size
    return _json(200, {"items": _decorate(ctx, rows), "total": total, "page": page, "page_size": size})


def _item_create(ctx: Context, req: Request) -> Response:
    user, guard = _require_json(ctx, req)
    if guard:
        return guard
    data, errors = clean_item(req.json())
    if errors:
        return _json(400, {"error": "invalid_input", "message": first_error(errors), "fields": errors})
    actor = str(user.get("sub") or "")
    row = ctx.store.create_item(data, actor)
    return _json(200, {"ok": True, "item": _decorate(ctx, [row])[0]})


def _item_detail(ctx: Context, req: Request, item_id: str) -> Response:
    user, guard = _require_user(ctx, req)
    if guard:
        return guard
    row = ctx.store.get_item(item_id)
    if not row:
        return _json(404, {"error": "not_found", "message": "内容不存在"})
    return _json(200, {"item": _decorate(ctx, [row])[0]})


def _item_update(ctx: Context, req: Request, item_id: str) -> Response:
    user, guard = _require_json(ctx, req)
    if guard:
        return guard
    payload = req.json()
    data, errors = clean_item(payload, partial=True)
    if errors:
        return _json(400, {"error": "invalid_input", "message": first_error(errors), "fields": errors})
    if not data:
        return _json(400, {"error": "empty_payload", "message": "没有需要更新的字段"})
    try:
        row = ctx.store.update_item(item_id, data, str(user.get("sub") or ""),
                                    str(payload.get("expected_updated_at") or ""))
    except Conflict as exc:
        return _json(409, {"error": "conflict", "message": exc.message})
    if not row:
        return _json(404, {"error": "not_found", "message": "内容不存在"})
    return _json(200, {"ok": True, "item": _decorate(ctx, [row])[0]})


def _item_delete(ctx: Context, req: Request, item_id: str) -> Response:
    user, guard = _require_write(ctx, req)
    if guard:
        return guard
    ctx.store.delete_item(item_id, str(user.get("sub") or ""))
    return _json(200, {"ok": True})


def _items_bulk(ctx: Context, req: Request) -> Response:
    user, guard = _require_json(ctx, req)
    if guard:
        return guard
    body = req.json()
    ids = [str(x) for x in (body.get("ids") or []) if str(x).strip()]
    action = str(body.get("action") or "").strip()
    if not ids:
        return _json(400, {"error": "invalid_input", "message": "请先选择要操作的内容"})
    if action not in (*STATUSES, "delete"):
        return _json(400, {"error": "invalid_input", "message": "批量动作不合法"})
    try:
        count = ctx.store.bulk_update(ids[:100], action, str(user.get("sub") or ""))
    except Conflict as exc:
        return _json(409, {"error": "conflict", "message": exc.message})
    return _json(200, {"ok": True, "affected": count})


def _categories(ctx: Context, req: Request) -> Response:
    user, guard = _require_user(ctx, req)
    if guard:
        return guard
    return _json(200, {"categories": ctx.store.list_categories()})


def _category_create(ctx: Context, req: Request) -> Response:
    user, guard = _require_json(ctx, req)
    if guard:
        return guard
    data, errors = clean_taxonomy(req.json(), "category")
    if errors:
        return _json(400, {"error": "invalid_input", "message": first_error(errors), "fields": errors})
    try:
        row = ctx.store.create_category(data)
    except Conflict as exc:
        return _json(409, {"error": "conflict", "message": exc.message})
    ctx.store.add_log(str(user.get("sub") or ""), "create_category", str(row.get("id")),
                      f"新建分类「{data['name']}」")
    return _json(200, {"ok": True, "category": row})


def _category_update(ctx: Context, req: Request, category_id: str) -> Response:
    user, guard = _require_json(ctx, req)
    if guard:
        return guard
    data, errors = clean_taxonomy(req.json(), "category")
    if errors:
        return _json(400, {"error": "invalid_input", "message": first_error(errors), "fields": errors})
    row = ctx.store.update_category(category_id, data)
    if not row:
        return _json(404, {"error": "not_found", "message": "分类不存在"})
    return _json(200, {"ok": True, "category": row})


def _category_delete(ctx: Context, req: Request, category_id: str) -> Response:
    user, guard = _require_write(ctx, req)
    if guard:
        return guard
    try:
        ctx.store.delete_category(category_id)
    except Conflict as exc:
        return _json(409, {"error": "conflict", "message": exc.message})
    return _json(200, {"ok": True})


def _tags(ctx: Context, req: Request) -> Response:
    user, guard = _require_user(ctx, req)
    if guard:
        return guard
    return _json(200, {"tags": ctx.store.list_tags()})


def _tag_create(ctx: Context, req: Request) -> Response:
    user, guard = _require_json(ctx, req)
    if guard:
        return guard
    data, errors = clean_taxonomy(req.json(), "tag")
    if errors:
        return _json(400, {"error": "invalid_input", "message": first_error(errors), "fields": errors})
    row = ctx.store.create_tag(data)
    return _json(200, {"ok": True, "tag": row})


def _tag_delete(ctx: Context, req: Request, tag_id: str) -> Response:
    user, guard = _require_write(ctx, req)
    if guard:
        return guard
    try:
        ctx.store.delete_tag(tag_id)
    except Conflict as exc:
        return _json(409, {"error": "conflict", "message": exc.message})
    return _json(200, {"ok": True})


def _upload(ctx: Context, req: Request) -> Response:
    user, guard = _require_write(ctx, req)
    if guard:
        return guard
    filename = unquote(req.headers.get("x-file-name") or "") or "upload.bin"
    content_type = (req.headers.get("content-type") or "application/octet-stream").split(";")[0].strip()
    item_id = (req.headers.get("x-item-id") or "").strip()
    try:
        result = ctx.storage.upload(filename, content_type, req.body)
    except StorageError as exc:
        return _json(exc.status, {"error": exc.code, "message": exc.message})
    meta = {
        "item_id": item_id or None,
        "filename": filename[:200],
        "path": str(result["path"]),
        "url": str(result["url"]),
        "content_type": content_type,
        "size": int(result["size"]),
    }
    row = ctx.store.add_attachment(meta, str(user.get("sub") or ""))
    return _json(200, {"ok": True, "attachment": row, "degraded": bool(result.get("degraded"))})


def _attachments(ctx: Context, req: Request) -> Response:
    user, guard = _require_user(ctx, req)
    if guard:
        return guard
    item_id = (req.query.get("item_id") or "").strip()
    return _json(200, {"attachments": ctx.store.list_attachments(item_id)})


def _attachment_delete(ctx: Context, req: Request, attachment_id: str) -> Response:
    user, guard = _require_write(ctx, req)
    if guard:
        return guard
    row = ctx.store.delete_attachment(attachment_id, str(user.get("sub") or ""))
    if not row:
        return _json(404, {"error": "not_found", "message": "附件不存在"})
    ctx.storage.delete(str(row.get("path") or ""))
    return _json(200, {"ok": True})


def _logs(ctx: Context, req: Request) -> Response:
    user, guard = _require_user(ctx, req)
    if guard:
        return guard
    try:
        limit = int(req.query.get("limit") or 20)
    except ValueError:
        limit = 20
    return _json(200, {"logs": ctx.store.list_logs(limit)})


# ---- 路由分发 ------------------------------------------------------------


def dispatch(ctx: Context, req: Request) -> Response:
    path = req.path.rstrip("/") or "/"
    method = req.method

    if method == "GET" and path == "/":
        return _respond(302, b"", "text/plain; charset=utf-8", location="/app")
    if method == "GET" and path == "/login":
        return _page("login.html")
    if method == "GET" and path in ("/app", "/admin"):
        if not current_user(ctx, req):
            return _respond(302, b"", "text/plain; charset=utf-8", location="/login")
        return _page("app.html")
    if method == "GET" and path.startswith("/static/"):
        resp = _static(path[len("/static/"):])
        return resp or _json(404, {"error": "not_found"})
    if method == "GET" and path == "/favicon.ico":
        return _respond(200, b"", "image/x-icon")

    if method == "GET" and path == "/api/health":
        return _health(ctx, req)
    if method == "POST" and path == "/api/auth/login":
        return _login(ctx, req)
    if method == "POST" and path == "/api/auth/logout":
        return _logout(ctx, req)
    if method == "GET" and path == "/api/auth/me":
        return _me(ctx, req)
    if method == "GET" and path == "/api/meta":
        return _meta(ctx, req)
    if method == "GET" and path == "/api/dashboard":
        return _dashboard(ctx, req)
    if method == "GET" and path == "/api/logs":
        return _logs(ctx, req)

    if path == "/api/items" and method == "GET":
        return _items_list(ctx, req)
    if path == "/api/items" and method == "POST":
        return _item_create(ctx, req)
    if path == "/api/items/bulk" and method == "POST":
        return _items_bulk(ctx, req)
    if path.startswith("/api/items/") and method == "GET":
        return _item_detail(ctx, req, path[len("/api/items/"):])
    if path.startswith("/api/items/") and method == "PATCH":
        return _item_update(ctx, req, path[len("/api/items/"):])
    if path.startswith("/api/items/") and method == "DELETE":
        return _item_delete(ctx, req, path[len("/api/items/"):])

    if path == "/api/categories" and method == "GET":
        return _categories(ctx, req)
    if path == "/api/categories" and method == "POST":
        return _category_create(ctx, req)
    if path.startswith("/api/categories/") and method == "PATCH":
        return _category_update(ctx, req, path[len("/api/categories/"):])
    if path.startswith("/api/categories/") and method == "DELETE":
        return _category_delete(ctx, req, path[len("/api/categories/"):])

    if path == "/api/tags" and method == "GET":
        return _tags(ctx, req)
    if path == "/api/tags" and method == "POST":
        return _tag_create(ctx, req)
    if path.startswith("/api/tags/") and method == "DELETE":
        return _tag_delete(ctx, req, path[len("/api/tags/"):])

    if path == "/api/uploads" and method == "POST":
        return _upload(ctx, req)
    if path == "/api/attachments" and method == "GET":
        return _attachments(ctx, req)
    if path.startswith("/api/attachments/") and method == "DELETE":
        return _attachment_delete(ctx, req, path[len("/api/attachments/"):])

    return _json(404, {"error": "not_found", "path": path})


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


def build_app(cfg: Optional[Config] = None, store=None, storage: Optional[Storage] = None):
    """构建 ASGI 应用（Vercel 直接导出该对象即可）。"""
    ctx = build_context(cfg, store, storage)

    async def app(scope, receive, send):
        if scope.get("type") != "http":
            return
        body = await _read_body(receive)
        request = Request(scope, body)
        loop = asyncio.get_running_loop()
        try:
            status, headers, payload = await loop.run_in_executor(None, dispatch, ctx, request)
        except Exception as exc:  # 永不 500：兜底为可读 JSON
            status, headers, payload = _json(500, {"error": "internal_error", "message": f"服务异常：{exc}"})
        await send({"type": "http.response.start", "status": status, "headers": headers})
        await send({"type": "http.response.body", "body": payload})

    return app


__all__ = [
    "build_app",
    "build_context",
    "dispatch",
    "Request",
    "Context",
    "MemoryStore",
    "SupabaseStore",
]
