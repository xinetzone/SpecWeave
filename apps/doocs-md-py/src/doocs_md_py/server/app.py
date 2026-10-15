"""FastAPI 应用工厂（upstream: apps/api/src/index.ts 装配顺序 1:1）。

含：全局 CORS（origin.ts 语义）、健康检查、统一 ApiError 处理器；业务路由由
T10-T18 按上游挂载点逐步注册（/auth 已挂载；后续 /upload、/sync、/share、
/marketplace、/emojis、/notifications、/webhooks/afdian），静态前端托管在 T19 挂载。
"""

import sqlite3

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response

from .. import __version__
from .config import Config, load_config
from .emoji_storage import build_emoji_backend
from .httputil import ApiError, error_response
from .origin import is_allowed_origin, is_browser_extension_origin
from .routers import auth as auth_router
from .routers import emojis as emojis_router
from .routers import marketplace as marketplace_router
from .routers import notifications as notifications_router
from .routers import share as share_router
from .routers import sync as sync_router
from .routers import upload as upload_router
from .routers import webhooks as webhooks_router

# upstream: index.ts:22-25
_CORS_METHODS = "GET, POST, PATCH, DELETE, OPTIONS"
_CORS_HEADERS = "Authorization, Content-Type"
_CORS_MAX_AGE = "86400"


def _origin_allowed(config: Config, origin: str | None) -> bool:
    return bool(origin) and (
        is_allowed_origin(config.app_url, origin) or is_browser_extension_origin(origin)
    )


def create_app(
    config: Config | None = None,
    *,
    conn: sqlite3.Connection | None = None,
    http_client: httpx.Client | None = None,
) -> FastAPI:
    """构造 ASGI app；测试可注入 Config、内存 SQLite 连接与 MockTransport httpx 客户端。"""
    config = config or load_config()

    app = FastAPI(
        title="doocs-md-py",
        version=__version__,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.config = config
    if conn is not None:
        app.state.db = conn
    if http_client is not None:
        app.state.http_client = http_client
    # 表情资产后端（upstream EMOJI_ASSETS R2 binding）；测试可替换 state 属性
    app.state.emoji_storage = build_emoji_backend(config, http_client=http_client)

    # 统一业务错误体（upstream 各 c.json({error}, status)）
    @app.exception_handler(ApiError)
    async def handle_api_error(_request: Request, exc: ApiError) -> Response:
        return error_response(
            exc.status_code, exc.message, extra=exc.extra, headers=exc.headers
        )

    app.include_router(auth_router.router)
    # 爱发电订单回调（webhook.ts，index.ts:40-41；公开端点，路径令牌可选）
    app.include_router(webhooks_router.router)
    # 上游 index.ts:53-64：/me 与 /sync/* 同在鉴权 api 组
    app.include_router(auth_router.me_router)
    app.include_router(sync_router.router)
    # 分享：/share/* 走路由内鉴权依赖，/s/* 公开（share.ts，index.ts:44-61）
    app.include_router(share_router.router)
    # 图片上传（upload.ts，index.ts:35-37）
    app.include_router(upload_router.router)
    # 主题/组件市场（marketplace.ts，index.ts:47-48）
    app.include_router(marketplace_router.router)
    # 表情资产（emojis.ts，index.ts:50）
    app.include_router(emojis_router.router)
    # 站内通知（notifications.ts，index.ts:63，鉴权 api 组）
    app.include_router(notifications_router.router)

    # CORS：upstream index.ts:19-28（Hono cors 中间件语义）
    @app.middleware("http")
    async def cors_middleware(request: Request, call_next):  # noqa: ANN001, ANN202
        origin = request.headers.get("origin")
        allowed = _origin_allowed(config, origin)

        # 预检：允许时直接 204 + 全部 CORS 头，不进入业务路由；
        # 不允许时不加 CORS 头并继续（Hono cors 行为：await next()）。
        if request.method == "OPTIONS" and request.headers.get("access-control-request-method"):
            if allowed:
                return Response(
                    status_code=204,
                    headers={
                        "Access-Control-Allow-Origin": origin,
                        "Access-Control-Allow-Credentials": "true",
                        "Access-Control-Allow-Methods": _CORS_METHODS,
                        "Access-Control-Allow-Headers": _CORS_HEADERS,
                        "Access-Control-Max-Age": _CORS_MAX_AGE,
                        "Vary": "Origin",
                    },
                )
            return await call_next(request)

        response = await call_next(request)
        if allowed:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            # Vary 必须随实际请求回显，缓存才不会跨 origin 串用
            response.headers.setdefault("Vary", "Origin")
        return response

    @app.get("/")
    async def health() -> dict[str, str | bool]:
        # upstream: index.ts:30
        return {"name": "md-api", "ok": True}

    return app


def serve(host: str = "127.0.0.1", port: int = 8800, config: Config | None = None) -> None:
    """uvicorn 启动入口（mdpy serve，T19 完整化静态托管）。"""
    import uvicorn

    uvicorn.run(create_app(config), host=host, port=port)
