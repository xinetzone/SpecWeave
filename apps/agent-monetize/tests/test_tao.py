"""道家门控测试：无为门 / 知止门 / 门控编排器。"""

from __future__ import annotations

from agent_monetize.config import WuyouConfig, ZhizhiConfig
from agent_monetize.models import ChannelState, LoopState, Opportunity
from agent_monetize.tao.gates import GateReport, TaoGate, WuyouGate, ZhizhiGate


def _opp(**kw) -> Opportunity:
    base = dict(
        channel_id="c",
        expected_return=10.0,
        certainty=0.9,
        scarcity_factor=1.0,
        est_cost=0.5,
    )
    base.update(kw)
    return Opportunity(**base)


class TestWuyouGate:
    def test_pass_when_high_certainty_and_return(self) -> None:
        r = WuyouGate().evaluate(_opp())
        assert r.passed
        assert r.level == "pass"

    def test_block_low_certainty(self) -> None:
        r = WuyouGate().evaluate(_opp(certainty=0.1))
        assert not r.passed
        assert r.level == "limit"

    def test_block_low_expected_return(self) -> None:
        r = WuyouGate().evaluate(_opp(expected_return=0.2))
        assert not r.passed

    def test_custom_thresholds(self) -> None:
        gate = WuyouGate(WuyouConfig(min_certainty=0.8, min_expected_return=20.0))
        assert not gate.evaluate(_opp()).passed
        assert gate.evaluate(_opp(certainty=0.95, expected_return=30.0)).passed


class TestZhizhiGate:
    def test_pass_normally(self) -> None:
        ch = ChannelState(channel_id="c", revenue=5.0)
        st = LoopState(balance=10.0)
        assert ZhizhiGate().evaluate(ch, st).passed

    def test_block_channel_revenue_cap(self) -> None:
        cfg = ZhizhiConfig(per_channel_revenue_cap=10.0)
        ch = ChannelState(channel_id="c", revenue=11.0)
        r = ZhizhiGate(cfg).evaluate(ch, None)
        assert not r.passed
        assert "上限" in r.reason

    def test_block_total_loss_redline(self) -> None:
        cfg = ZhizhiConfig(total_loss_redline=-50.0)
        st = LoopState(balance=-60.0)
        r = ZhizhiGate(cfg).evaluate(None, st)
        assert not r.passed
        assert "红线" in r.reason


class TestTaoGate:
    def test_any_fail_means_fail(self) -> None:
        gate = TaoGate()
        # 确定性极低 → 无为门拦截
        report = gate.check(_opp(certainty=0.1))
        assert not report.passed
        assert "wuyou" in [r.name for r in report.results if not r.passed]

    def test_all_pass(self) -> None:
        gate = TaoGate()
        report = gate.check(_opp(certainty=0.9, expected_return=50.0))
        assert report.passed
        assert len(report.results) == 2

    def test_zhizhi_fail_merged(self) -> None:
        gate = TaoGate(zhizhi=ZhizhiConfig(per_channel_revenue_cap=1.0))
        ch = ChannelState(channel_id="c", revenue=5.0)
        report = gate.check(_opp(), channel_state=ch)
        assert not report.passed
        assert "zhizhi" in [r.name for r in report.results if not r.passed]


def test_gate_report_merge() -> None:
    report = GateReport()
    from agent_monetize.tao.gates import GateResult

    report.merge(GateResult(name="a", passed=True))
    assert report.passed
    report.merge(GateResult(name="b", passed=False, reason="no"))
    assert not report.passed
    assert report.reasons == ["[b] no"]
