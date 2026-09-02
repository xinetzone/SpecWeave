"""数据模型（dataclasses）：信号 / 机会 / 决策 / 结果 / 反馈 / 通道状态。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Signal:
    """观察层产出的原始机会信号。"""

    channel_id: str
    kind: str = "opportunity"
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel_id": self.channel_id,
            "kind": self.kind,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }


@dataclass(slots=True)
class Opportunity:
    """经 ffi_bridge 打分后的机会（决定是否行动的依据）。"""

    channel_id: str
    expected_return: float
    certainty: float
    scarcity_factor: float
    est_cost: float
    score: float = 0.0
    payload: dict[str, Any] = field(default_factory=dict)
    signal: Signal | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel_id": self.channel_id,
            "expected_return": self.expected_return,
            "certainty": self.certainty,
            "scarcity_factor": self.scarcity_factor,
            "est_cost": self.est_cost,
            "score": self.score,
            "payload": self.payload,
        }


@dataclass(slots=True)
class Decision:
    """决策层产出：行动 or 不行动（no-op / 待时）。"""

    channel_id: str | None
    action: str  # "act" | "no-op"
    score: float = 0.0
    reason: str = ""
    gates: list[str] = field(default_factory=list)

    @property
    def is_noop(self) -> bool:
        return self.action == "no-op"


@dataclass(slots=True)
class ActionResult:
    """行动层产出：一次通道执行的结果。"""

    channel_id: str
    success: bool = True
    revenue: float = 0.0
    cost: float = 0.0
    conversions: int = 0
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def net(self) -> float:
        """净收益 = 收入 - 成本（对应公理 A6：净收益 = 创造价值 − 交易成本 − 再分配让渡）。"""
        return self.revenue - self.cost


@dataclass(slots=True)
class Feedback:
    """反馈层输入：一次行动结果，用于自进化学习。"""

    channel_id: str
    revenue: float = 0.0
    cost: float = 0.0
    conversions: int = 0
    success: bool = True
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def net(self) -> float:
        return self.revenue - self.cost


@dataclass(slots=True)
class ChannelState:
    """单通道运行时状态（余额、权重、历史记录）。"""

    channel_id: str
    weight: float = 1.0
    revenue: float = 0.0
    cost: float = 0.0
    conversions: int = 0
    actions: int = 0
    enabled: bool = True
    history: list[dict[str, Any]] = field(default_factory=list)

    @property
    def net(self) -> float:
        return self.revenue - self.cost

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel_id": self.channel_id,
            "weight": self.weight,
            "revenue": self.revenue,
            "cost": self.cost,
            "conversions": self.conversions,
            "actions": self.actions,
            "enabled": self.enabled,
            "history": self.history[-50:],  # 历史只保留最近 50 条
        }


@dataclass(slots=True)
class LoopState:
    """全局自主循环状态（余额 + 各通道状态 + 历史）。"""

    balance: float = 0.0
    round_count: int = 0
    channels: dict[str, ChannelState] = field(default_factory=dict)

    @property
    def total_revenue(self) -> float:
        return sum(ch.revenue for ch in self.channels.values())

    @property
    def total_cost(self) -> float:
        return sum(ch.cost for ch in self.channels.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "balance": self.balance,
            "round_count": self.round_count,
            "channels": {k: v.to_dict() for k, v in self.channels.items()},
        }
