"""账户与密钥库端点：注册 / 登录 / 解锁 / escrow / 恢复 / 改密 / 密钥 CRUD / 订单。"""

from fastapi import APIRouter, Depends, Request

from ..errors import ByokError, ErrorCode
from ..logging_utils import fingerprint, get_logger
from ..models import TOKEN_PREFIX
from .deps import current_user, require_turnstile

router = APIRouter()
logger = get_logger("api.account")


@router.post("/register")
def register(
    request: Request, payload: dict, _turnstile=Depends(require_turnstile)
) -> dict:
    hub = request.app.state.hub
    email = str(payload.get("email") or "").strip()
    password = str(payload.get("password") or "")
    if not email or not password:
        raise ByokError(ErrorCode.INVALID_REQUEST, "email 与 password 必填")
    result = hub.tokens.register(
        email,
        password,
        invited_by=payload.get("invite_code"),
        plan_key=str(payload.get("plan_key") or "free"),
        vault=hub.vault,
    )
    return {
        "object": "registration",
        "user_id": result.user.id,
        "email": result.user.email,
        "token": result.token,
        "recovery_secret": result.recovery_secret,
        "notice": "统一令牌与恢复密语只显示一次，请离线保存；服务端仅存摘要与密文。",
    }


@router.post("/login")
def login(
    request: Request, payload: dict, _turnstile=Depends(require_turnstile)
) -> dict:
    hub = request.app.state.hub
    token = hub.tokens.login(str(payload.get("email") or ""), str(payload.get("password") or ""))
    return {"object": "login", "token": token, "token_prefix": TOKEN_PREFIX}


@router.post("/unlock")
def unlock(request: Request, payload: dict, user=Depends(current_user)) -> dict:
    """用口令解锁密钥库（主密钥仅驻留内存）。"""
    hub = request.app.state.hub
    hub.unlock(user.id, str(payload.get("password") or ""))
    return {"object": "unlock", "unlocked": True}


@router.post("/unlock/recover")
def unlock_recover(request: Request, payload: dict, user=Depends(current_user)) -> dict:
    hub = request.app.state.hub
    hub.unlock_with_recovery(user.id, str(payload.get("recovery_secret") or ""))
    return {"object": "unlock", "unlocked": True}


@router.get("/escrow")
def escrow(request: Request, user=Depends(current_user)) -> dict:
    """读取双 escrow 密文（仅密文，服务端无明文能力）。"""
    hub = request.app.state.hub
    record = hub.store.escrow.find(lambda e: e.user_id == user.id)
    if record is None:
        raise ByokError(ErrorCode.VAULT_LOCKED, "尚未初始化密钥托管")
    return {
        "object": "escrow",
        "user_id": record.user_id,
        "master_salt": record.master_salt,
        "iterations": record.iterations,
        "generation": record.generation,
        "escrow_pw": record.escrow_pw.cipher.model_dump(mode="json"),
        "escrow_rec": record.escrow_rec.cipher.model_dump(mode="json"),
    }


@router.post("/escrow")
def post_escrow(request: Request, payload: dict, user=Depends(current_user)) -> dict:
    """接管客户端生成的双 escrow 密文（``POST /api/escrow``）。

    原产品是浏览器端 E2EE（主密钥不出浏览器）；本复刻的本地代理需要明文 Key
    才能转发，故服务端必须能解出主密钥——因此上传时必须同传 ``password``：
    服务端据此解出新主密钥，并用它重写全部厂商密钥密文。缺少 ``password``
    时明确报错，不谎报 ``stored``（详见 README 假设说明）。
    """
    hub = request.app.state.hub
    pw = payload.get("escrow_pw")
    rec = payload.get("escrow_rec")
    if not pw or not rec:
        raise ByokError(ErrorCode.INVALID_REQUEST, "escrow_pw 与 escrow_rec 必填")
    password = str(payload.get("password") or "")
    if not password:
        raise ByokError(
            ErrorCode.INVALID_REQUEST,
            "本实现为服务端代理（需明文 Key 转发），上传 escrow 必须同传 password 以便服务端接管新主密钥",
        )
    record, master, reencrypted = hub.vault.adopt_client_escrow(user.id, pw, rec, password)
    hub._master_keys[user.id] = master
    return {
        "object": "escrow",
        "user_id": user.id,
        "stored": True,
        "generation": record.generation,
        "reencrypted": reencrypted,
    }


@router.post("/recover")
def recover(
    request: Request, payload: dict, _turnstile=Depends(require_turnstile)
) -> dict:
    """用恢复密语重置口令（对应 ``/api/recover``）。"""
    hub = request.app.state.hub
    secret = str(payload.get("recovery_secret") or "")
    new_password = str(payload.get("new_password") or "")
    user = hub.tokens.verify_recovery(secret)
    if user is None:
        raise ByokError(ErrorCode.INVALID_RECOVERY)
    old_master = hub.vault.unlock_with_recovery(user.id, secret)
    hub.tokens.reset_password_with_recovery(secret, new_password)
    hub.vault.rotate_escrow(
        user.id, None, new_password, kind="pw", master_key=old_master
    )
    hub._master_keys[user.id] = old_master
    return {"object": "recover", "user_id": user.id, "ok": True}


@router.post("/password")
def change_password(request: Request, payload: dict, user=Depends(current_user)) -> dict:
    """改密：重新包裹主密钥（``/api/password``）。"""
    hub = request.app.state.hub
    old_password = str(payload.get("old_password") or "")
    new_password = str(payload.get("new_password") or "")
    master = hub.vault.unlock_with_password(user.id, old_password)
    hub.tokens.change_password(user.id, old_password, new_password)
    hub.vault.rotate_escrow(user.id, old_password, new_password, kind="pw")
    hub._master_keys[user.id] = master
    return {"object": "password", "ok": True, "reencrypted": True}


@router.get("/keys")
def list_keys(request: Request, user=Depends(current_user)) -> dict:
    hub = request.app.state.hub
    rows = hub.vault.list_keys(user.id)
    return {
        "object": "list",
        "data": [
            {
                "id": r.id,
                "provider_id": r.provider_id,
                "display_name": r.display_name,
                "protocol": r.protocol.value,
                "status": r.status.value,
                "quota_total": r.quota_total,
                "quota_used": r.quota_used,
                "quota_remaining": r.quota_remaining,
                "last_error": r.last_error,
                "generation": r.generation,
            }
            for r in rows
        ],
    }


@router.post("/keys")
def add_key(request: Request, payload: dict, user=Depends(current_user)) -> dict:
    hub = request.app.state.hub
    provider_id = str(payload.get("provider_id") or "")
    api_key = str(payload.get("api_key") or "")
    if not provider_id or not api_key:
        raise ByokError(ErrorCode.INVALID_REQUEST, "provider_id 与 api_key 必填")
    master = hub.master_key(user.id)
    provider = hub.catalog.provider(provider_id)
    record = hub.vault.add_key(
        user.id,
        provider_id,
        api_key,
        master,
        display_name=str(payload.get("display_name") or ""),
        protocol=(provider.protocol if provider else provider_protocol(payload)),
        base_url=str(payload.get("base_url") or (provider.base_url if provider else "")),
        quota_total=(None if payload.get("quota_total") is None else int(payload["quota_total"])),
    )
    logger.info("用户 %s 录入密钥 %s", user.id, fingerprint(api_key))
    return {"object": "key", "id": record.id, "provider_id": record.provider_id, "status": record.status.value}


def provider_protocol(payload: dict):
    from ..models import ProviderProtocol

    raw = str(payload.get("protocol") or "openai_compat")
    return ProviderProtocol(raw)


@router.delete("/keys/{key_id}")
def delete_key(request: Request, key_id: str, user=Depends(current_user)) -> dict:
    hub = request.app.state.hub
    removed = hub.vault.remove_key(user.id, key_id)
    if not removed:
        raise ByokError(ErrorCode.KEY_NOT_FOUND)
    return {"object": "key", "id": key_id, "deleted": True}


@router.get("/orders")
def list_orders(request: Request, user=Depends(current_user)) -> dict:
    hub = request.app.state.hub
    return {"object": "list", "data": [o.model_dump(mode="json") for o in hub.billing.orders(user.id)]}


@router.post("/orders")
def create_order(request: Request, payload: dict, user=Depends(current_user)) -> dict:
    hub = request.app.state.hub
    order = hub.billing.create_order(user.id, str(payload.get("plan_key") or "standard"))
    return order.model_dump(mode="json")


@router.post("/orders/{order_id}/proof")
def submit_proof(request: Request, order_id: str, payload: dict, user=Depends(current_user)) -> dict:
    hub = request.app.state.hub
    order = hub.billing.submit_proof(order_id, str(payload.get("proof") or ""))
    hub.ops.audit(actor_user_id=user.id, action="order.proof", target_id=order_id)
    return order.model_dump(mode="json")
