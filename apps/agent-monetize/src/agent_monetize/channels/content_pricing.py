"""沙箱通道 1：内容计价模拟（生成内容 → 按阅读/采纳计价，虚拟货币）。

完全在沙箱内运行：不真联网、不真收费，仅模拟价值交换闭环。
"""

from __future__ import annotations

import random
from typing import Any

from ..models import ActionResult, Feedback, Opportunity, Signal
from .base import Channel

DEFAULT_READ_PRICE = 0.5
DEFAULT_ADOPTION_BONUS = 5.0


class ContentPricingChannel(Channel):
    """内容计价通道：按阅读次数计价 + 采纳加成（沙箱模拟）。"""

    channel_id = "content_pricing"
    kind = "content_pricing"

    def __init__(self, params: dict[str, Any] | None = None, seed: int = 42) -> None:
        super().__init__(params)
        self._rng = random.Random(seed)  # noqa: S311 - 沙箱模拟，需种子可复现
        self.read_price = (
            float(params.get("read_price", DEFAULT_READ_PRICE)) if params else DEFAULT_READ_PRICE
        )
        self.adoption_bonus = (
            float(params.get("adoption_bonus", DEFAULT_ADOPTION_BONUS))
            if params
            else DEFAULT_ADOPTION_BONUS
        )
        self.click_floor = int(params.get("click_floor", 3)) if params else 3
        self.click_ceiling = int(params.get("click_ceiling", 12)) if params else 12

    # -- 观察层 -------------------------------------------------------
    def observe_signal(self) -> list[Signal]:
        reads_est = self._rng.randint(self.click_floor, self.click_ceiling)
        adoption_prob = round(self._rng.uniform(0.1, 0.7), 3)
        certainty = round(self._rng.uniform(0.35, 0.95), 3)
        expected_return = round(
            reads_est * self.read_price + adoption_prob * self.adoption_bonus, 2
        )
        signal = Signal(
            channel_id=self.channel_id,
            kind="content_opportunity",
            payload={
                "topic": f"topic-{self._rng.randint(1, 20)}",
                "reads_estimate": reads_est,
                "adoption_prob": adoption_prob,
                "expected_return": expected_return,
                "certainty": certainty,
                "scarcity_factor": round(self._rng.uniform(0.2, 1.8), 3),
                "est_cost": 0.2,
                "behavior": None,  # 良性行为，无红区标签
            },
        )
        return [signal]

    # -- 行动层 -------------------------------------------------------
    def act(self, opportunity: Opportunity) -> ActionResult:
        payload = opportunity.payload or {}
        reads_est = int(payload.get("reads_estimate", 5))
        adoption_prob = float(payload.get("adoption_prob", 0.3))
        reads = max(0, int(reads_est * self._rng.uniform(0.7, 1.3)))
        adopted = self._rng.random() < adoption_prob
        revenue = round(reads * self.read_price + (self.adoption_bonus if adopted else 0.0), 2)
        cost = round(reads * 0.01, 2)  # 沙箱计算成本（虚拟）
        return ActionResult(
            channel_id=self.channel_id,
            success=True,
            revenue=revenue,
            cost=cost,
            conversions=1 if adopted else 0,
            details={
                "reads": reads,
                "adopted": adopted,
                "title": f"《{payload.get('topic', 'unknown')} 深度解析》",
            },
        )

    def learn_feedback(self, feedback: Feedback) -> None:
        # 通道内自进化钩子：可在此微调策略（本示例由外层 Learner 统一更新权重）
        return None


# 保持参数取值与默认常量一致，便于测试直接引用
def default_content_params() -> dict[str, Any]:
    return {
        "read_price": DEFAULT_READ_PRICE,
        "adoption_bonus": DEFAULT_ADOPTION_BONUS,
        "click_floor": 3,
        "click_ceiling": 12,
    }
