"""通道抽象基类：4 钩子（observe_signal / decide_eligibility / act / learn_feedback）。"""

from __future__ import annotations

import abc
from typing import Any

from ..models import ActionResult, Feedback, Opportunity, Signal


class Channel(abc.ABC):
    """通道基类。

    4 个钩子对应自主循环四步：
      - observe_signal    观察层：采集机会信号（A3 找稀缺 / A4 降搜索成本）
      - decide_eligibility 决策层：机会是否适配本通道
      - act                行动层：执行价值交付与计价（A1 交付价值 / A2 完成交换）
      - learn_feedback     反馈层：接收结果反馈用于自进化（A7 正循环）
    """

    channel_id: str = ""
    kind: str = "generic"
    requires_real_confirmation: bool = False  # 真实模式需合规确认

    def __init__(self, params: dict[str, Any] | None = None) -> None:
        self.params: dict[str, Any] = dict(params or {})

    # -- 元信息 -------------------------------------------------------
    def describe(self) -> dict[str, Any]:
        return {"channel_id": self.channel_id, "kind": self.kind, "params": self.params}

    # -- 4 钩子 --------------------------------------------------------
    @abc.abstractmethod
    def observe_signal(self) -> list[Signal]:
        """返回当前观察到的机会信号列表（沙箱内模拟，不真联网）。"""
        raise NotImplementedError

    def decide_eligibility(self, opportunity: Opportunity) -> bool:
        """判断机会是否适配本通道；默认放行。"""
        return True

    @abc.abstractmethod
    def act(self, opportunity: Opportunity) -> ActionResult:
        """执行一次价值交付并计价（沙箱虚拟货币）。"""
        raise NotImplementedError

    def learn_feedback(self, feedback: Feedback) -> None:  # noqa: B027 - 可选钩子，默认无操作
        """接收结果反馈（通道内自进化钩子，默认无操作）。"""

    # -- 机会经济估算 --------------------------------------------------
    def estimate_opportunity(self, signal: Signal) -> Opportunity:
        """由信号估算机会经济参数（预期收益/确定性/稀缺/成本）。

        默认从 payload 读取；子类可覆盖以注入更精细的模拟。
        """
        payload = signal.payload or {}
        return Opportunity(
            channel_id=self.channel_id,
            expected_return=float(payload.get("expected_return", 0.0)),
            certainty=float(payload.get("certainty", 0.5)),
            scarcity_factor=float(payload.get("scarcity_factor", 0.5)),
            est_cost=float(payload.get("est_cost", 0.1)),
            payload=payload,
            signal=signal,
        )
