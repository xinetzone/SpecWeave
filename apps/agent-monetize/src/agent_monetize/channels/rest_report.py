"""示例真实 API 适配器通道：自定义 REST 上报通道（不含真实资金流转）。

默认关闭。仅当 config `enable_real=true` 且行为 `sandbox-report` 被用户显式
加入 `compliance.confirmed_behaviors` 时才真正对外发送；否则以沙箱空适配器对照。
"""

from __future__ import annotations

import random
from typing import Any

from ..adapters.base import (
    AdapterGuard,
    HttpJsonReportAdapter,
    NoopSandboxAdapter,
    RealAdapterProtocol,
)
from ..models import ActionResult, Feedback, Opportunity, Signal
from .base import Channel

DEFAULT_PER_REPORT_PRICE = 1.0
BEHAVIOR = "sandbox-report"


class RestReportChannel(Channel):
    """REST 上报通道：按报告计价（沙箱演示真实适配器启用守卫）。"""

    channel_id = "rest_report"
    kind = "rest_report"
    requires_real_confirmation = True

    def __init__(
        self,
        params: dict[str, Any] | None = None,
        seed: int = 3,
        enable_real: bool = False,
        confirmed_behaviors: list[str] | None = None,
        adapter: RealAdapterProtocol | None = None,
    ) -> None:
        super().__init__(params)
        params = params or {}
        self._rng = random.Random(seed)  # noqa: S311 - 沙箱模拟，需种子可复现
        self.per_report_price = float(params.get("per_report_price", DEFAULT_PER_REPORT_PRICE))
        self.enable_real = enable_real
        self.behavior = BEHAVIOR
        self.confirmed = bool(adapter) or (BEHAVIOR in (confirmed_behaviors or []))

        endpoint = params.get("endpoint") or None
        if adapter is not None:
            self.adapter = adapter
        elif enable_real:
            self.adapter = HttpJsonReportAdapter(endpoint=endpoint)
        else:
            self.adapter = NoopSandboxAdapter(behavior=self.behavior)
        self.guard = AdapterGuard(confirmed_behaviors)
        self._verdict = self.guard.allow(
            self.adapter, enable_real=enable_real, behavior=self.behavior
        )

    @property
    def real_enabled(self) -> bool:
        """真实模式是否被启用（enable_real + 合规确认双条件）。"""
        return self._verdict.allowed

    # -- 观察层 -------------------------------------------------------
    def observe_signal(self) -> list[Signal]:
        if not self.real_enabled:
            return []  # 默认关闭：真实通道不产出信号
        certainty = round(self._rng.uniform(0.7, 0.95), 3)
        return [
            Signal(
                channel_id=self.channel_id,
                kind="report_request",
                payload={
                    "expected_return": self.per_report_price,
                    "certainty": certainty,
                    "scarcity_factor": 1.0,
                    "est_cost": 0.05,
                    "behavior": self.behavior,
                    "real_mode": True,
                },
            )
        ]

    # -- 行动层 -------------------------------------------------------
    def act(self, opportunity: Opportunity) -> ActionResult:
        if not self.real_enabled:
            return ActionResult(
                channel_id=self.channel_id,
                success=False,
                revenue=0.0,
                cost=0.0,
                details={"reason": "真实通道未启用（enable_real=false 或未获合规确认）"},
            )
        payload = opportunity.payload or {}
        report = {
            "report_id": f"r-{self._rng.randint(1000, 9999)}",
            "topic": payload.get("dataset", "report"),
            "sandbox": True,
            "no_real_money": True,
        }
        try:
            resp = self.adapter.send(report)
            return ActionResult(
                channel_id=self.channel_id,
                success=True,
                revenue=round(self.per_report_price, 2),
                cost=0.05,
                conversions=1,
                details={"adapter": self.adapter.name, "response": resp},
            )
        except Exception as exc:  # pragma: no cover - 网络异常
            return ActionResult(
                channel_id=self.channel_id,
                success=False,
                revenue=0.0,
                cost=0.05,
                details={"error": str(exc)},
            )

    def learn_feedback(self, feedback: Feedback) -> None:
        return None


def default_report_params() -> dict[str, Any]:
    return {"per_report_price": DEFAULT_PER_REPORT_PRICE}
