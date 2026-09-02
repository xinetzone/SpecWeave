"""沙箱通道 2：数据服务计价模拟（按调用次数 / 按量计价，含阶梯折扣）。

完全在沙箱内运行：不真联网、不真收费。
"""

from __future__ import annotations

import random
from typing import Any

from ..models import ActionResult, Feedback, Opportunity, Signal
from .base import Channel

DEFAULT_PER_CALL_PRICE = 0.8


class DataServiceChannel(Channel):
    """数据服务通道：按调用次数计价，达到量级门槛享折扣（沙箱模拟）。"""

    channel_id = "data_service"
    kind = "data_service"

    def __init__(self, params: dict[str, Any] | None = None, seed: int = 7) -> None:
        super().__init__(params)
        self._rng = random.Random(seed)  # noqa: S311 - 沙箱模拟，需种子可复现
        self.per_call_price = (
            float(params.get("per_call_price", DEFAULT_PER_CALL_PRICE))
            if params
            else DEFAULT_PER_CALL_PRICE
        )
        self.volume_discount_threshold = (
            int(params.get("volume_discount_threshold", 50)) if params else 50
        )
        self.volume_discount_rate = (
            float(params.get("volume_discount_rate", 0.9)) if params else 0.9
        )
        self.call_floor = int(params.get("call_floor", 1)) if params else 1
        self.call_ceiling = int(params.get("call_ceiling", 20)) if params else 20

    # -- 观察层 -------------------------------------------------------
    def observe_signal(self) -> list[Signal]:
        calls_est = self._rng.randint(self.call_floor, self.call_ceiling)
        certainty = round(self._rng.uniform(0.3, 0.97), 3)
        expected_return = round(calls_est * self.per_call_price, 2)
        signal = Signal(
            channel_id=self.channel_id,
            kind="data_request",
            payload={
                "dataset": f"dataset-{self._rng.randint(1, 30)}",
                "calls_estimate": calls_est,
                "expected_return": expected_return,
                "certainty": certainty,
                "scarcity_factor": round(self._rng.uniform(0.1, 1.5), 3),
                "est_cost": 0.1,
                "behavior": None,  # 良性行为，无红区标签
            },
        )
        return [signal]

    # -- 行动层 -------------------------------------------------------
    def act(self, opportunity: Opportunity) -> ActionResult:
        payload = opportunity.payload or {}
        calls_est = int(payload.get("calls_estimate", 5))
        calls = max(0, int(calls_est * self._rng.uniform(0.8, 1.2)))
        unit_price = self.per_call_price
        if calls >= self.volume_discount_threshold:
            unit_price *= self.volume_discount_rate
        revenue = round(calls * unit_price, 2)
        cost = round(calls * 0.005, 3)  # 沙箱服务成本（虚拟）
        return ActionResult(
            channel_id=self.channel_id,
            success=True,
            revenue=revenue,
            cost=cost,
            conversions=calls,
            details={
                "calls": calls,
                "unit_price": round(unit_price, 3),
                "dataset": payload.get("dataset", "unknown"),
                "discounted": calls >= self.volume_discount_threshold,
            },
        )

    def learn_feedback(self, feedback: Feedback) -> None:
        return None


def default_data_params() -> dict[str, Any]:
    return {
        "per_call_price": DEFAULT_PER_CALL_PRICE,
        "volume_discount_threshold": 50,
        "volume_discount_rate": 0.9,
        "call_floor": 1,
        "call_ceiling": 20,
    }
