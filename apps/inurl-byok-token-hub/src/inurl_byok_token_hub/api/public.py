"""公开端点：**无鉴权**（源文档 F-099）。

``/api/catalog``、``/api/billing/plans``、``/api/turnstile``、``/api/ads``、
``/api/news`` 均无需令牌；其余接口未授权一律 401。
"""

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/catalog")
def catalog(request: Request, all: str | None = None) -> dict:  # noqa: A002
    """厂商目录。``?all=1`` 与默认返回同一份数据（对齐 F-077 既有行为）。"""
    hub = request.app.state.hub
    include_hidden = not bool(hub.settings.hide_hidden_providers)
    providers = hub.catalog.list_providers(include_hidden=include_hidden)
    return {
        "object": "catalog",
        "providers": [p.model_dump(mode="json") for p in providers],
        "models": [m.model_dump(mode="json") for m in hub.catalog.list_models()],
        "counts": {
            "providers": len(providers),
            "models": len(hub.catalog.list_models()),
            "free": hub.catalog.free_count,
            "paid": hub.catalog.paid_count,
            "hidden": hub.catalog.hidden_count,
        },
    }


@router.get("/billing/plans")
def plans(request: Request) -> dict:
    hub = request.app.state.hub
    return {
        "object": "plans",
        "data": [
            {
                "key": p.key,
                "name": p.name,
                "price_cents": p.price_cents,
                "price_yuan": p.price_yuan,
                "keyLimit": p.key_limit,
            }
            for p in hub.settings.plans
        ],
        "freeKeyLimit": hub.settings.plan("free").key_limit,
        "currency": "CNY",
        "note": "免费档仅 3 个厂商密钥（源文档核心勘误 E1）",
    }


@router.get("/turnstile")
def turnstile(request: Request) -> dict:
    hub = request.app.state.hub
    return {"enabled": hub.settings.turnstile_enabled, "siteKey": "1x00000000000000000000AA"}


@router.get("/ads")
def ads(request: Request) -> dict:
    hub = request.app.state.hub
    return {"object": "list", "data": [a.model_dump(mode="json") for a in hub.ops.ads()]}


@router.get("/news")
def news(request: Request) -> dict:
    hub = request.app.state.hub
    rows = hub.ops.news()
    return {
        "object": "list",
        "featured": [n.model_dump(mode="json") for n in rows if n.featured][:1],
        "data": [n.model_dump(mode="json") for n in rows],
    }
