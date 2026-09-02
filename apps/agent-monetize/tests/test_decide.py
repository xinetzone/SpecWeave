"""决策层专项测试：覆盖合规过滤、通道适配过滤与「全部过滤后待时」分支。"""

from __future__ import annotations

from agent_monetize.channels.base import Channel
from agent_monetize.channels.registry import ChannelRegistry
from agent_monetize.compliance.policies import ComplianceEngine
from agent_monetize.core.decide import Decider
from agent_monetize.models import ActionResult, Opportunity
from agent_monetize.tao.gates import TaoGate


class ViableChannel(Channel):
    """默认放行的绿区通道。"""

    channel_id = "viable"

    def observe_signal(self) -> list:  # type: ignore[no-untyped-def]
        return []

    def act(self, opportunity: Opportunity) -> ActionResult:  # noqa: ARG002 - 测试桩
        return ActionResult(channel_id=self.channel_id, revenue=1.0)


class IneligibleChannel(ViableChannel):
    """通道级不适配：eligible 恒为 False。"""

    channel_id = "ineligible"

    def decide_eligibility(self, opportunity: Opportunity) -> bool:  # noqa: ARG002 - 测试桩
        return False


def _opp(channel_id: str, behavior: str | None = None, score: float = 5.0) -> Opportunity:
    payload = {}
    if behavior:
        payload["behavior"] = behavior
    return Opportunity(
        channel_id=channel_id,
        expected_return=10.0,
        certainty=0.9,
        scarcity_factor=1.0,
        est_cost=0.2,
        score=score,
        payload=payload,
    )


def _decider(*channels: Channel) -> Decider:
    reg = ChannelRegistry()
    for ch in channels:
        reg.register(ch)
    return Decider(reg, TaoGate(), ComplianceEngine())


def test_decide_blocks_red_zone_and_acts_on_green() -> None:
    decider = _decider(ViableChannel())
    decision = decider.decide(
        [_opp("viable", behavior="fraud", score=9.0), _opp("viable", score=5.0)]
    )
    assert decision.action == "act"
    assert decision.channel_id == "viable"


def test_decide_skips_ineligible_channel() -> None:
    decider = _decider(IneligibleChannel(), ViableChannel())
    decision = decider.decide(
        [_opp("ineligible", score=9.0), _opp("viable", score=5.0)]
    )
    assert decision.action == "act"
    assert decision.channel_id == "viable"


def test_decide_noop_when_all_filtered() -> None:
    decider = _decider(ViableChannel())
    decision = decider.decide([_opp("viable", behavior="spam", score=9.0)])
    assert decision.action == "no-op"
    assert "所有机会均未通过合规/通道适配过滤" in decision.reason
