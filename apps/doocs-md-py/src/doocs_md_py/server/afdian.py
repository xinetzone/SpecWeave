"""爱发电开放平台客户端（upstream: apps/api/src/afdian.ts 1:1）。

HTTP 调用显式注入 httpx.Client（测试经 MockTransport 拦截，不产生真实网络）；
签名仅使用标准库 hashlib，不引入 NFR-2 白名单外依赖。
"""

import hashlib
import json
import re
import time
from dataclasses import dataclass
from typing import Any

import httpx

from .config import DEFAULT_AFDIAN_API_BASE, Config

# upstream: afdian.ts:26 仅去末尾一个斜杠（非 rstrip）
_TRAILING_SLASH_RE = re.compile(r"/$")


@dataclass(slots=True)
class AfdianOrder:
    """upstream: afdian.ts:6-17 AfdianOrder（title 可选）。"""

    out_trade_no: str
    user_id: str
    plan_id: str
    month: Any
    total_amount: str
    show_amount: str
    status: Any
    remark: str
    product_type: Any
    title: str | None = None

    @classmethod
    def from_dict(cls, item: dict) -> "AfdianOrder":
        """从开放平台 JSON 构造；字符串字段缺失归一为空串（与 ?? 防御等价）。"""

        def text(key: str) -> str:
            value = item.get(key)
            return value if isinstance(value, str) else ""

        title = item.get("title")
        return cls(
            out_trade_no=text("out_trade_no"),
            user_id=text("user_id"),
            plan_id=text("plan_id"),
            # status/month/product_type 上游声明 number；保留原值交由资格判定，
            # None/字符串等异常值自然无法通过 === 2 等数值比较
            month=item.get("month"),
            total_amount=text("total_amount"),
            show_amount=text("show_amount"),
            status=item.get("status"),
            remark=text("remark"),
            product_type=item.get("product_type"),
            title=title if isinstance(title, str) else None,
        )


def _api_base(config: Config) -> str:
    """upstream: afdian.ts:25-27。"""
    return _TRAILING_SLASH_RE.sub("", config.afdian_api_base or DEFAULT_AFDIAN_API_BASE)


def sign(token: str, params: str, ts: int, user_id: str) -> str:
    """upstream: afdian.ts:29-32 md5(token + params{...}ts{...}user_id{...})。"""
    kv = f"params{params}ts{ts}user_id{user_id}"
    return hashlib.md5((token + kv).encode("utf-8")).hexdigest()  # noqa: S324


def afdian_request(
    client: httpx.Client,
    config: Config,
    endpoint: str,
    params_obj: dict,
    *,
    now_s: int | None = None,
) -> Any:
    """upstream: afdian.ts:34-60；未配置 user_id/token 抛 RuntimeError。

    请求体与 JSON.stringify 逐字一致（紧凑分隔符、非 ASCII 不转义），
    保证 sign 拼接的 params 串与实际发送的 JSON 字符串值字节相同。
    """
    user_id = config.afdian_user_id
    token = config.afdian_api_token
    if not user_id or not token:
        # upstream: afdian.ts:41-42
        raise RuntimeError("afdian_not_configured")

    params = json.dumps(params_obj, ensure_ascii=False, separators=(",", ":"))
    ts = int(now_s) if now_s is not None else int(time.time())
    body = {
        "user_id": user_id,
        "params": params,
        "ts": ts,
        "sign": sign(token, params, ts, user_id),
    }

    response = client.post(
        f"{_api_base(config)}/{endpoint}",
        content=json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    # upstream: afdian.ts:59 直接 res.json()，不校验 HTTP 状态码
    return response.json()


def query_order(
    client: httpx.Client,
    config: Config,
    out_trade_no: str,
    *,
    now_s: int | None = None,
) -> AfdianOrder | None:
    """upstream: afdian.ts:62-69；ec!=200 或无 list 项返回 None。"""
    result = afdian_request(
        client,
        config,
        "query-order",
        {"out_trade_no": out_trade_no},
        now_s=now_s,
    )
    if not isinstance(result, dict) or result.get("ec") != 200:
        return None
    data = result.get("data")
    if not isinstance(data, dict):
        return None
    order_list = data.get("list")
    if not isinstance(order_list, list) or not order_list:
        return None
    first = order_list[0]
    return AfdianOrder.from_dict(first) if isinstance(first, dict) else None


def is_pro_eligible_order(config: Config, order: AfdianOrder) -> bool:
    """upstream: afdian.ts:76-92。

    status=2 已支付；product_type 0（常规方案）或 1（一次性商品）均可；
    AFDIAN_PRO_PLAN_IDS 白名单为空表示全部接受。
    """
    if order.status != 2:
        return False
    if order.product_type != 0 and order.product_type != 1:
        return False

    # config.afdian_pro_plan_ids 已按 split(",")→trim→过滤空段解析（_csv）
    if not config.afdian_pro_plan_ids:
        # upstream: afdian.ts:88-89
        return True

    return order.plan_id in config.afdian_pro_plan_ids
