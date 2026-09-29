"""运营与后台模型：广告位、公告、支付订单（人工核销）、审计事件。

支付口径（源文档 F-097/F-098）：支付宝收银台与个人收款码 + 管理员人工核销
双通道并存；本复刻只实现状态机，不含真实资金流转。
"""

import enum
import time

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(enum.StrEnum):
    CREATED = "created"
    PROOF_SUBMITTED = "proof_submitted"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


#: 合法流转：created → proof_submitted → confirmed/rejected
ORDER_TRANSITIONS: dict[OrderStatus, tuple[OrderStatus, ...]] = {
    OrderStatus.CREATED: (OrderStatus.PROOF_SUBMITTED, OrderStatus.REJECTED),
    OrderStatus.PROOF_SUBMITTED: (OrderStatus.CONFIRMED, OrderStatus.REJECTED),
    OrderStatus.CONFIRMED: (),
    OrderStatus.REJECTED: (),
}


class PaymentOrder(BaseModel):
    """支付订单（默认支付方式为个人收款码 + 人工核销）。"""

    model_config = ConfigDict(frozen=True)

    id: str
    user_id: str
    plan_key: str
    amount_cents: int = 0
    method: str = "manual_qrcode"
    status: OrderStatus = OrderStatus.CREATED
    proof: str = ""
    reviewer: str | None = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class AdItem(BaseModel):
    """广告位条目（``/api/ads`` 无鉴权公开）。"""

    model_config = ConfigDict(frozen=True)

    id: str
    title: str
    body: str = ""
    url: str = ""
    enabled: bool = True


class NewsItem(BaseModel):
    """公告条目（``/api/news`` 无鉴权公开）。"""

    model_config = ConfigDict(frozen=True)

    id: str
    title: str
    summary: str = ""
    url: str = ""
    featured: bool = False
    enabled: bool = True


class AuditEvent(BaseModel):
    """后台审计事件（不含任何 Secret 与消息正文）。"""

    model_config = ConfigDict(frozen=True)

    id: str
    actor_user_id: str
    action: str
    target_id: str = ""
    result: str = "ok"
    created_at: float = Field(default_factory=time.time)


class AdminConfig(BaseModel):
    """系统配置（后台可改）。"""

    model_config = ConfigDict(frozen=True)

    turnstile_enabled: bool = False
    hide_hidden_providers: bool = False
    default_strategy: str = "latency_first"
    default_compression: str = "standard"
    announcement: str = ""
