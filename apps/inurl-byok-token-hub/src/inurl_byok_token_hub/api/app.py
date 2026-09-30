"""FastAPI 应用工厂。

组装顺序：``/v1``（本地代理）→ ``/api``（账户/公开）→ ``/api/admin``（后台）。
错误映射见 :mod:`inurl_byok_token_hub.api.errors`：
用户类未授权 401 裸 JSON、管理员越权 403、未匹配路由 401。
"""

from fastapi import FastAPI

from ..config import Settings
from ..services.hub import Hub, build_hub
from .account import router as account_router
from .admin import router as admin_router
from .errors import register_exception_handlers
from .proxy import router as proxy_router
from .public import router as public_router


def create_app(
    settings: Settings,
    *,
    hub: Hub | None = None,
    transport: object | None = None,
) -> FastAPI:
    app = FastAPI(
        title="inurl BYOK Token Hub",
        version="0.1.0",
        description="BYOK 统一令牌枢纽复刻：E2EE 密钥托管 + 本地 OpenAI 兼容代理 + 逻辑别名路由",
        docs_url="/docs",
        redoc_url=None,
    )
    app.state.settings = settings
    app.state.hub = hub if hub is not None else build_hub(settings)
    app.state.transport = transport

    register_exception_handlers(app)

    app.include_router(proxy_router, prefix=settings.api_prefix, tags=["proxy"])
    app.include_router(public_router, prefix="/api", tags=["public"])
    app.include_router(account_router, prefix="/api", tags=["account"])
    app.include_router(admin_router, prefix="/api/admin", tags=["admin"])

    # 精简控制台（服务端渲染，不引入前端构建链）
    from ..web.console import mount_console

    mount_console(app, app.state.hub)

    return app


__all__ = ["create_app"]
