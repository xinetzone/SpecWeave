"""观察层：机会信号采集 + tvm-ffi 打分（A3 找稀缺 / A4 降搜索成本）。"""

from __future__ import annotations

import logging
from typing import Any

from ..channels.registry import ChannelRegistry
from ..models import Opportunity, Signal
from .ffi_bridge import FfiBridge

logger = logging.getLogger(__name__)


class Observer:
    """观察者：轮询各通道机会信号 → 估算经济参数 → ffi_bridge 打分。"""

    def __init__(self, registry: ChannelRegistry, bridge: FfiBridge) -> None:
        self.registry = registry
        self.bridge = bridge

    def scan(self, channel_weights: dict[str, float] | None = None) -> list[Opportunity]:
        """采集并打分所有机会。

        channel_weights：自进化权重（learn 更新），影响机会的有效得分——
        权重高的通道（历史收益好）机会更易被选中。
        """
        weights = channel_weights or {}
        opportunities: list[Opportunity] = []
        for channel in self.registry.enabled():
            signals = channel.observe_signal()
            for signal in signals:
                opp = channel.estimate_opportunity(signal)
                opp.score = self.bridge.score_opportunity(
                    opp.expected_return,
                    opp.certainty,
                    opp.scarcity_factor,
                    opp.est_cost,
                )
                w = weights.get(channel.channel_id, 1.0)
                opp.score = round(opp.score * w, 4)  # 权重影响下一轮决策（自进化）
                opportunities.append(opp)
        return opportunities


def build_opportunity_from_signal(channel_id: str, signal: Signal, score: float) -> Opportunity:
    """由信号构造机会（供测试与外部复用）。"""
    payload: dict[str, Any] = signal.payload or {}
    return Opportunity(
        channel_id=channel_id,
        expected_return=float(payload.get("expected_return", 0.0)),
        certainty=float(payload.get("certainty", 0.5)),
        scarcity_factor=float(payload.get("scarcity_factor", 0.5)),
        est_cost=float(payload.get("est_cost", 0.1)),
        score=score,
        payload=payload,
        signal=signal,
    )
