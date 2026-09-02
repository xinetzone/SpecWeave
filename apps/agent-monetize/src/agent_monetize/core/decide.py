"""决策层：合规过滤 + 通道适配 + 道家门控 → 选择最优机会或待时（A2/A7）。"""

from __future__ import annotations

import logging

from ..channels.registry import ChannelRegistry
from ..compliance.policies import ComplianceEngine
from ..models import ChannelState, Decision, LoopState, Opportunity
from ..tao.gates import TaoGate

logger = logging.getLogger(__name__)


class Decider:
    """决策器：决定「行动哪个机会」或「不行动（待时）」。"""

    def __init__(
        self,
        registry: ChannelRegistry,
        tao_gate: TaoGate,
        compliance: ComplianceEngine,
    ) -> None:
        self.registry = registry
        self.tao_gate = tao_gate
        self.compliance = compliance

    def decide(
        self,
        opportunities: list[Opportunity],
        channel_states: dict[str, ChannelState] | None = None,
        global_state: LoopState | None = None,
    ) -> Decision:
        """对机会列表做决策。

        流程：红区合规过滤 → 通道适配过滤 → 按得分降序 → 道家门控（无为/知止）。
        最高分机会若被门控拦截则整体 no-op（待时）——动善时：最好的机会都不行就不做。
        """
        channel_states = channel_states or {}
        if not opportunities:
            return Decision(channel_id=None, action="no-op", reason="无可用机会")

        # 1) 红区合规过滤
        viable: list[Opportunity] = []
        for opp in opportunities:
            verdict = self.compliance.check(opp)
            if not verdict.allowed:
                logger.info("合规拦截：%s（%s）", opp.channel_id, verdict.reason)
                continue
            channel = self.registry.get(opp.channel_id)
            if channel is not None and not channel.decide_eligibility(opp):
                logger.info("通道不适配：%s", opp.channel_id)
                continue
            viable.append(opp)

        if not viable:
            return Decision(
                channel_id=None,
                action="no-op",
                reason="所有机会均未通过合规/通道适配过滤",
            )

        # 2) 取最高分机会
        viable.sort(key=lambda o: o.score, reverse=True)
        best = viable[0]

        # 3) 道家门控
        report = self.tao_gate.check(best, channel_states.get(best.channel_id), global_state)
        if not report.passed:
            return Decision(
                channel_id=best.channel_id,
                action="no-op",
                score=best.score,
                reason="；".join(report.reasons),
                gates=[r.name for r in report.results if not r.passed],
            )
        return Decision(
            channel_id=best.channel_id,
            action="act",
            score=best.score,
            reason=f"机会得分 {best.score:.3f}，通过无为/知止门",
            gates=[r.name for r in report.results],
        )
