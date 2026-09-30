"""精简 Jinja2 控制台：把只读/少量写操作的页面挂到既有 FastAPI app 上。

会话与鉴权
----------
页面会话依赖一枚 httponly Cookie ``byok_console_token``（``samesite=lax``、
``path=/console``），取值后一律交给 :meth:`TokenService.verify` 校验；校验失败统一
**303 重定向**到 ``/console/login``。Cookie 内只放统一令牌本身，模板上下文中不含
任何令牌串，页面也**绝不渲染明文厂商 Key**（只渲染密文记录的元数据与额度口径）。

这是精简控制台，不还原原产品全部交互：仅提供密钥库、用量、路由与压缩偏好、
套餐与订单四组页面，以及密钥删除、偏好保存、下单与提交支付凭证几个动作。
"""

from pathlib import Path

from fastapi import APIRouter, FastAPI, Form, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..api.deps import extract_token
from ..errors import ByokError, ErrorCode
from ..models import (
    COMPRESSION_SPECS,
    STRATEGIES,
    STRATEGY_LABELS,
    CompressionLevel,
    User,
    UserSettings,
)
from ..services.hub import Hub

#: 会话 Cookie 名与作用域（只作用于控制台路径，避免污染 API 调用）
COOKIE_NAME = "byok_console_token"
COOKIE_PATH = "/console"
COOKIE_MAX_AGE = 3600 * 12

#: 登录成功后落地页
LANDING_URL = "/console/keys"
LOGIN_URL = "/console/login"

#: 随包模板目录
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

_templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _current_user(request: Request, hub: Hub):
    """读取会话凭据并校验：Cookie 优先，其次 ``Authorization`` / ``X-API-Key``。"""
    token = request.cookies.get(COOKIE_NAME) or extract_token(request)
    return hub.tokens.verify(token)


def _login_redirect() -> RedirectResponse:
    return RedirectResponse(url=LOGIN_URL, status_code=303)


def _render(request: Request, name: str, context: dict) -> Response:
    """渲染模板；始终注入 request，供 Jinja2 生成站内链接。"""
    return _templates.TemplateResponse(request=request, name=name, context=context)


def _split_list(raw: str) -> tuple[str, ...]:
    """把候选列表文本框内容解析为去重元组（逗号或换行分隔）。"""
    items: list[str] = []
    for chunk in raw.replace("\n", ",").replace("，", ",").split(","):
        item = chunk.strip()
        if item and item not in items:
            items.append(item)
    return tuple(items)


def _default_settings(hub: Hub, user_id: str) -> UserSettings:
    """用户尚未保存偏好时的默认值（取自全局配置，便于文案与 API 保持一致）。"""
    return UserSettings(
        user_id=user_id,
        strategy=hub.settings.default_strategy,
        combo=hub.settings.default_combo,
        compression=CompressionLevel(hub.settings.default_compression),
        auto_models=tuple(hub.settings.auto_models),
        auto_provider_order=tuple(hub.settings.auto_provider_order),
    )


def mount_console(app: FastAPI, hub: Hub) -> None:
    """把控制台路由挂载到已有 app（路由前缀 ``/console``）。"""
    app.state.hub = hub
    router = APIRouter()

    # ------------------------------------------------------------- 登录/退出
    @router.get("/login")
    def login_page(request: Request) -> Response:
        return _render(request, "login.html", {"error": ""})

    @router.post("/login")
    def login_submit(request: Request, token: str = Form("")) -> Response:
        user = hub.tokens.verify(token.strip())
        if user is None:
            return _render(
                request,
                "login.html",
                {"error": "令牌无效或已失效，请粘贴以 byok_live_ 开头的统一令牌"},
            )
        response = RedirectResponse(url=LANDING_URL, status_code=303)
        response.set_cookie(
            COOKIE_NAME,
            token.strip(),
            max_age=COOKIE_MAX_AGE,
            httponly=True,
            samesite="lax",
            path=COOKIE_PATH,
        )
        return response

    @router.post("/logout")
    def logout() -> Response:
        response = RedirectResponse(url=LOGIN_URL, status_code=303)
        response.delete_cookie(COOKIE_NAME, path=COOKIE_PATH)
        return response

    # ----------------------------------------------------------------- 密钥库
    @router.get("/keys")
    def keys_page(request: Request) -> Response:
        user = _current_user(request, hub)
        if user is None:
            return _login_redirect()
        rows = hub.vault.list_keys(user.id)
        return _render(
            request,
            "keys.html",
            {
                "user": user,
                "rows": rows,
                "plan": hub.billing.plan_of(user),
                "key_limit": hub.billing.key_limit(user),
                "key_count": len(rows),
            },
        )

    @router.post("/keys/{key_id}/delete")
    def keys_delete(request: Request, key_id: str) -> Response:
        user = _current_user(request, hub)
        if user is None:
            return _login_redirect()
        hub.vault.remove_key(user.id, key_id)
        return RedirectResponse(url="/console/keys", status_code=303)

    # ------------------------------------------------------------------- 用量
    @router.get("/usage")
    def usage_page(request: Request) -> Response:
        user = _current_user(request, hub)
        if user is None:
            return _login_redirect()
        return _render(
            request,
            "usage.html",
            {
                "user": user,
                "rows": hub.usage.summaries(user.id),
                "total_calls": hub.usage.total_calls(user.id),
            },
        )

    # ------------------------------------------------------- 路由与压缩偏好
    @router.get("/routes")
    def routes_page(request: Request) -> Response:
        user = _current_user(request, hub)
        if user is None:
            return _login_redirect()
        saved = hub.store.settings.find(lambda s: s.user_id == user.id)
        current = saved if saved is not None else _default_settings(hub, user.id)
        return _routes_view(request, user, current, error="")

    @router.post("/routes")
    def routes_save(
        request: Request,
        strategy: str = Form(""),
        combo: str = Form(""),
        compression: str = Form(""),
        auto_models: str = Form(""),
        auto_provider_order: str = Form(""),
    ) -> Response:
        user = _current_user(request, hub)
        if user is None:
            return _login_redirect()
        default = _default_settings(hub, user.id)
        try:
            level = CompressionLevel(compression.strip() or default.compression.value)
        except ValueError:
            level = default.compression
        row = UserSettings(
            user_id=user.id,
            strategy=strategy.strip() if strategy.strip() in STRATEGIES else default.strategy,
            combo=combo.strip(),
            compression=level,
            auto_models=_split_list(auto_models) or default.auto_models,
            auto_provider_order=_split_list(auto_provider_order) or default.auto_provider_order,
        )
        hub.store.settings.upsert(lambda s: s.user_id == user.id, row)
        return RedirectResponse(url="/console/routes?saved=1", status_code=303)

    def _routes_view(request: Request, user: User, current: UserSettings, error: str) -> Response:
        return _render(
            request,
            "routes.html",
            {
                "user": user,
                "current": current,
                "strategies": [
                    {"key": key, "label": STRATEGY_LABELS.get(key, key)} for key in STRATEGIES
                ],
                "levels": [
                    {"value": level.value, "rate": spec[0], "label": spec[1]}
                    for level, spec in COMPRESSION_SPECS.items()
                ],
                "combo_layers": tuple(part for part in current.combo.split(">") if part.strip()),
                "saved": bool(request.query_params.get("saved")),
                "error": error,
            },
        )

    # ----------------------------------------------------------------- 套餐
    @router.get("/plans")
    def plans_page(request: Request) -> Response:
        user = _current_user(request, hub)
        if user is None:
            return _login_redirect()
        return _plans_view(request, user, error="")

    @router.post("/plans")
    def plans_submit(
        request: Request,
        action: str = Form(""),
        plan_key: str = Form(""),
        order_id: str = Form(""),
        proof: str = Form(""),
    ) -> Response:
        user = _current_user(request, hub)
        if user is None:
            return _login_redirect()
        try:
            if action == "create":
                hub.billing.create_order(user.id, plan_key.strip())
            elif action == "proof":
                hub.billing.submit_proof(order_id.strip(), proof.strip())
            else:
                raise ByokError(ErrorCode.INVALID_REQUEST, "未知操作，请重新提交")
        except ByokError as exc:
            return _plans_view(request, user, error=exc.message)
        return RedirectResponse(url="/console/plans?saved=1", status_code=303)

    def _plans_view(request: Request, user: User, error: str) -> Response:
        current_plan = hub.billing.plan_of(user)
        return _render(
            request,
            "plans.html",
            {
                "user": user,
                "plans": [
                    {
                        "key": plan.key,
                        "name": plan.name,
                        "price": plan.price_yuan,
                        "limit": plan.key_limit,
                        "current": plan.key == current_plan.key,
                    }
                    for plan in hub.settings.plans
                ],
                "orders": hub.billing.orders(user_id=user.id),
                "saved": bool(request.query_params.get("saved")),
                "error": error,
            },
        )

    app.include_router(router, prefix="/console")


__all__ = [
    "COOKIE_NAME",
    "COOKIE_PATH",
    "LANDING_URL",
    "LOGIN_URL",
    "TEMPLATES_DIR",
    "mount_console",
]
