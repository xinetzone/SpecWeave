"""红绿区合规策略测试。"""

from __future__ import annotations

from agent_monetize.compliance.policies import (
    RED_ZONE_BEHAVIORS,
    ComplianceConfig,
    ComplianceEngine,
)
from agent_monetize.models import Opportunity


def _opp(behavior: str | None = None, real_mode: bool = False) -> Opportunity:
    return Opportunity(
        channel_id="c",
        expected_return=10.0,
        certainty=0.9,
        scarcity_factor=1.0,
        est_cost=0.1,
        payload={"behavior": behavior, "real_mode": real_mode},
    )


class TestComplianceEngine:
    def test_red_zone_blocked(self) -> None:
        engine = ComplianceEngine()
        for behavior in RED_ZONE_BEHAVIORS:
            verdict = engine.check(_opp(behavior=behavior))
            assert not verdict.allowed
            assert verdict.zone == "red"

    def test_green_zone_allowed(self) -> None:
        engine = ComplianceEngine()
        assert engine.check(_opp(behavior=None)).allowed

    def test_real_mode_requires_confirmation(self) -> None:
        engine = ComplianceEngine()
        verdict = engine.check(_opp(behavior="sandbox-report", real_mode=True))
        assert not verdict.allowed
        assert verdict.zone == "green"

    def test_real_mode_with_confirmation_allowed(self) -> None:
        engine = ComplianceEngine(ComplianceConfig(confirmed_behaviors=["sandbox-report"]))
        verdict = engine.check(_opp(behavior="sandbox-report", real_mode=True))
        assert verdict.allowed

    def test_red_zone_disabled(self) -> None:
        engine = ComplianceEngine(ComplianceConfig(enable_red_zone=False))
        assert engine.check(_opp(behavior="fraud")).allowed

    def test_red_zone_summary_nonempty(self) -> None:
        assert "fraud" in ComplianceEngine().red_zone_summary
