"""真实 API 适配器通道（RestReportChannel）测试：合规启用守卫与沙箱对照。"""

from __future__ import annotations

from agent_monetize.channels.rest_report import RestReportChannel
from agent_monetize.models import ActionResult, Opportunity


class _StubAdapter:
    """不发网络的测试替身：记录发送负载并返回固定响应。"""

    name = "stub"
    requires_real_confirmation = True

    def __init__(self) -> None:
        self.sent: list[dict] = []

    def send(self, payload: dict) -> dict:  # type: ignore[no-untyped-def]
        self.sent.append(payload)
        return {"status": 200, "body": "ok"}


class TestRestReportChannel:
    def test_disabled_by_default(self) -> None:
        ch = RestReportChannel(enable_real=False)
        assert ch.real_enabled is False
        assert ch.observe_signal() == []

    def test_act_fails_when_not_enabled(self) -> None:
        ch = RestReportChannel(enable_real=False)
        result = ch.act(
            Opportunity(
                channel_id="rest_report",
                expected_return=1.0,
                certainty=0.9,
                scarcity_factor=1.0,
                est_cost=0.05,
            )
        )
        assert isinstance(result, ActionResult)
        assert result.success is False
        assert result.revenue == 0.0

    def test_real_requires_confirmation(self) -> None:
        ch = RestReportChannel(enable_real=True, confirmed_behaviors=[])
        assert ch.real_enabled is False

    def test_real_enabled_with_confirmation(self) -> None:
        ch = RestReportChannel(enable_real=True, confirmed_behaviors=["sandbox-report"])
        assert ch.real_enabled is True
        signals = ch.observe_signal()
        assert len(signals) == 1
        assert signals[0].payload["real_mode"] is True

    def test_act_uses_adapter_when_enabled(self) -> None:
        stub = _StubAdapter()
        ch = RestReportChannel(
            enable_real=True,
            confirmed_behaviors=["sandbox-report"],
            adapter=stub,  # type: ignore[arg-type]
        )
        opp = ch.estimate_opportunity(ch.observe_signal()[0])
        result = ch.act(opp)
        assert result.success is True
        assert result.revenue > 0
        assert stub.sent, "适配器应收到上报负载"
        assert stub.sent[0]["no_real_money"] is True
