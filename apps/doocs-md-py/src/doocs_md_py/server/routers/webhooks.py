"""爱发电订单 webhook（upstream: apps/api/src/webhook.ts 1:1）。

公开端点（index.ts:40-41，未挂鉴权组）：
``POST /webhooks/afdian`` 与 ``POST /webhooks/afdian/{token}``。

安全要点（服务公开托管，回调地址可被发现）：
1. 可选路径令牌 AFDIAN_WEBHOOK_TOKEN 阻断随意调用；
2. **永不信任回调体中的订单字段**：只读 out_trade_no，再回查爱发电
   开放 API，以回查结果为权威事实——伪造回调无法开通 Pro。
"""

import sqlite3

import httpx
from fastapi import APIRouter, Depends, Request
from starlette.responses import JSONResponse

from ..afdian import query_order
from ..config import Config
from ..deps import get_db, get_http_client
from ..plan import activate_pro_from_order, parse_github_login_from_remark

router = APIRouter(tags=["webhook"])


def _accepted() -> JSONResponse:
    """静默 200（避免爱发电平台重试）。"""
    return JSONResponse(status_code=200, content={"ec": 200, "em": ""})


@router.post("/webhooks/afdian")
@router.post("/webhooks/afdian/{token}")
async def afdian_webhook(
    request: Request,
    token: str | None = None,
    conn: sqlite3.Connection = Depends(get_db),
    client: httpx.Client = Depends(get_http_client),
) -> JSONResponse:
    config: Config = request.app.state.config

    # upstream: webhook.ts:27-32 配置了路径令牌则必须逐字匹配
    expected_token = config.afdian_webhook_token
    if expected_token and token != expected_token:
        return JSONResponse(status_code=403, content={"ec": 403, "em": "forbidden"})

    # upstream: webhook.ts:35-36 无 API 凭证无法回查，返回 200 避免平台重试
    if not config.is_afdian_configured():
        return _accepted()

    # upstream: webhook.ts:38-44
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400, content={"ec": 400, "em": "invalid_body"}
        )

    if not isinstance(body, dict):
        return _accepted()
    data = body.get("data")
    # upstream: webhook.ts:46-47
    if not isinstance(data, dict) or data.get("type") != "order":
        return _accepted()
    order_body = data.get("order")
    if not isinstance(order_body, dict):
        return _accepted()

    # upstream: webhook.ts:49-51
    raw_trade_no = order_body.get("out_trade_no")
    out_trade_no = raw_trade_no.strip() if isinstance(raw_trade_no, str) else None
    if not out_trade_no:
        return _accepted()

    # upstream: webhook.ts:53-55 以开放平台回查为权威事实
    order = query_order(client, config, out_trade_no)
    if order is None or order.status != 2:
        return _accepted()

    # upstream: webhook.ts:57-61 备注无 GitHub 登录名时静默
    github_login = parse_github_login_from_remark(order.remark)
    if not github_login:
        return _accepted()

    # upstream: webhook.ts:63-64 激活结果不影响回调应答（用户不存在等仅放弃）
    activate_pro_from_order(conn, config, order, github_login)
    return _accepted()
