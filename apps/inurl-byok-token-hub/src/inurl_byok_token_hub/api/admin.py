"""管理员端点（八模块后台）。非管理员一律 **403** ``{"error": "forbidden"}``。"""

from fastapi import APIRouter, Depends, Request

from ..errors import ByokError, ErrorCode
from .deps import require_admin

router = APIRouter()


@router.get("/modules")
def modules(request: Request, admin=Depends(require_admin)) -> dict:  # noqa: ARG001
    hub = request.app.state.hub
    return {"object": "list", "data": list(hub.ops.modules())}


@router.get("/users")
def users(request: Request, admin=Depends(require_admin)) -> dict:
    hub = request.app.state.hub
    rows = hub.store.users.all()
    return {
        "object": "list",
        "data": [
            {
                "id": u.id,
                "email": u.email,
                "role": u.role.value,
                "plan_key": u.plan_key,
                "invite_bonus": u.invite_bonus,
                "created_at": u.created_at,
            }
            for u in rows
        ],
        "total": len(rows),
    }


@router.get("/keys")
def keys(request: Request, admin=Depends(require_admin)) -> dict:
    hub = request.app.state.hub
    return {
        "object": "list",
        "data": [
            {
                "id": k.id,
                "user_id": k.user_id,
                "provider_id": k.provider_id,
                "status": k.status.value,
                "generation": k.generation,
            }
            for k in hub.store.keys.all()
        ],
    }


@router.get("/usage")
def usage(request: Request, admin=Depends(require_admin)) -> dict:
    hub = request.app.state.hub
    return {
        "object": "usage",
        "total_calls": hub.usage.total_calls(),
        "records": [r.model_dump(mode="json") for r in hub.usage.records()[:200]],
        "health": {k: v.state for k, v in hub.health.snapshot().items()},
    }


@router.get("/orders")
def orders(request: Request, admin=Depends(require_admin)) -> dict:
    hub = request.app.state.hub
    return {"object": "list", "data": [o.model_dump(mode="json") for o in hub.billing.orders()]}


@router.post("/orders/{order_id}/confirm")
def confirm_order(request: Request, order_id: str, admin=Depends(require_admin)) -> dict:
    """人工核销：确认收款后升级套餐。"""
    hub = request.app.state.hub
    order = hub.billing.confirm_order(order_id, admin.id)
    hub.ops.audit(actor_user_id=admin.id, action="order.confirm", target_id=order_id)
    return order.model_dump(mode="json")


@router.post("/orders/{order_id}/reject")
def reject_order(request: Request, order_id: str, admin=Depends(require_admin)) -> dict:
    hub = request.app.state.hub
    order = hub.billing.reject_order(order_id, admin.id)
    hub.ops.audit(actor_user_id=admin.id, action="order.reject", target_id=order_id)
    return order.model_dump(mode="json")


@router.get("/config")
def get_config(request: Request, admin=Depends(require_admin)) -> dict:  # noqa: ARG001
    hub = request.app.state.hub
    return hub.ops.config().model_dump(mode="json")


@router.put("/config")
def put_config(request: Request, payload: dict, admin=Depends(require_admin)) -> dict:
    hub = request.app.state.hub
    unknown = set(payload) - set(hub.ops.config().model_fields)
    if unknown:
        raise ByokError(ErrorCode.INVALID_REQUEST, f"未知配置项 {sorted(unknown)}")
    config = hub.ops.set_config(**payload)
    hub.ops.audit(actor_user_id=admin.id, action="config.update", target_id=",".join(payload))
    return config.model_dump(mode="json")


@router.get("/audit")
def audit(request: Request, admin=Depends(require_admin)) -> dict:  # noqa: ARG001
    hub = request.app.state.hub
    return {"object": "list", "data": [e.model_dump(mode="json") for e in hub.ops.audit_log()]}


@router.post("/catalog/reload")
def reload_catalog(request: Request, admin=Depends(require_admin)) -> dict:
    """重新加载目录（对应「catalog 更新需重启代理」的显式动作）。"""
    hub = request.app.state.hub
    hub.catalog.reload()
    hub.ops.audit(actor_user_id=admin.id, action="catalog.reload")
    return {"object": "catalog", "reloaded": True, "providers": len(hub.catalog.list_providers())}


@router.post("/content/ad")
def add_ad(request: Request, payload: dict, admin=Depends(require_admin)) -> dict:
    hub = request.app.state.hub
    item = hub.ops.add_ad(str(payload.get("title") or ""), str(payload.get("body") or ""))
    hub.ops.audit(actor_user_id=admin.id, action="content.ad", target_id=item.id)
    return item.model_dump(mode="json")


@router.post("/content/news")
def add_news(request: Request, payload: dict, admin=Depends(require_admin)) -> dict:
    hub = request.app.state.hub
    item = hub.ops.add_news(
        str(payload.get("title") or ""),
        str(payload.get("summary") or ""),
        featured=bool(payload.get("featured", False)),
    )
    hub.ops.audit(actor_user_id=admin.id, action="content.news", target_id=item.id)
    return item.model_dump(mode="json")
