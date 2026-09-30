"""用量与计费模型：调用台账、计费事件。

用量口径（源文档 F-081）：每厂商「手填额度 − 已用 = 剩余」。
"""

import enum
import time

from pydantic import BaseModel, ConfigDict, Field


class CallStatus(enum.StrEnum):
    SUCCESS = "success"
    FAILOVER = "failover"
    FAILED = "failed"


class UsageRecord(BaseModel):
    """单次调用台账。"""

    model_config = ConfigDict(frozen=True)

    id: str
    user_id: str
    provider_id: str
    model_id: str
    alias: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    status: CallStatus = CallStatus.SUCCESS
    latency_ms: float = 0.0
    failover_count: int = 0
    created_at: float = Field(default_factory=time.time)

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class UsageSummary(BaseModel):
    """按厂商聚合的用量视图。"""

    model_config = ConfigDict(frozen=True)

    provider_id: str
    calls: int = 0
    total_tokens: int = 0
    quota_total: int | None = None
    quota_used: int = 0

    @property
    def quota_remaining(self) -> int | None:
        if self.quota_total is None:
            return None
        return max(0, self.quota_total - self.quota_used)


class BillingEventKind(enum.StrEnum):
    PLAN_CHANGE = "plan_change"
    ORDER_CREATED = "order_created"
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_REJECTED = "order_rejected"
    INVITE_BONUS = "invite_bonus"


class BillingEvent(BaseModel):
    """计费事件（不含真实资金流转）。"""

    model_config = ConfigDict(frozen=True)

    id: str
    user_id: str
    kind: BillingEventKind
    amount_cents: int = 0
    note: str = ""
    created_at: float = Field(default_factory=time.time)
