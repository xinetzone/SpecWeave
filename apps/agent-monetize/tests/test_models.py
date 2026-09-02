"""数据模型不变量测试。"""

from __future__ import annotations

from agent_monetize.models import (
    ActionResult,
    ChannelState,
    Decision,
    Feedback,
    LoopState,
    Opportunity,
    Signal,
)


class TestModels:
    def test_action_result_net(self) -> None:
        r = ActionResult(channel_id="c", revenue=10.0, cost=3.0)
        assert r.net == 7.0

    def test_feedback_net(self) -> None:
        fb = Feedback(channel_id="c", revenue=5.0, cost=2.0)
        assert fb.net == 3.0

    def test_channel_state_net_and_to_dict(self) -> None:
        ch = ChannelState(channel_id="c", revenue=10.0, cost=4.0, conversions=2, actions=3)
        assert ch.net == 6.0
        d = ch.to_dict()
        assert d["channel_id"] == "c"
        assert d["revenue"] == 10.0
        assert d["history"] == []

    def test_channel_state_history_truncated(self) -> None:
        ch = ChannelState(channel_id="c")
        ch.history = [{"i": i} for i in range(60)]
        assert len(ch.to_dict()["history"]) == 50

    def test_loop_state_totals(self) -> None:
        st = LoopState()
        st.channels["a"] = ChannelState(channel_id="a", revenue=1.0, cost=0.2)
        st.channels["b"] = ChannelState(channel_id="b", revenue=3.0, cost=1.0)
        assert st.total_revenue == 4.0
        assert st.total_cost == 1.2

    def test_opportunity_to_dict(self) -> None:
        opp = Opportunity(
            channel_id="c",
            expected_return=10.0,
            certainty=0.8,
            scarcity_factor=1.0,
            est_cost=0.5,
            score=3.2,
        )
        d = opp.to_dict()
        assert d["score"] == 3.2
        assert d["channel_id"] == "c"

    def test_decision_is_noop(self) -> None:
        assert Decision(channel_id=None, action="no-op").is_noop
        assert not Decision(channel_id="c", action="act").is_noop

    def test_signal_to_dict(self) -> None:
        s = Signal(channel_id="c", payload={"a": 1}, timestamp=1.0)
        d = s.to_dict()
        assert d["channel_id"] == "c"
        assert d["kind"] == "opportunity"
