"""自进化学习器测试：指数加权 + 软最大归一化。"""

from __future__ import annotations

from agent_monetize.channels.content_pricing import ContentPricingChannel
from agent_monetize.channels.registry import ChannelRegistry
from agent_monetize.core.learn import Learner
from agent_monetize.models import ChannelState, Feedback


def _states() -> dict[str, ChannelState]:
    return {
        "a": ChannelState(channel_id="a"),
        "b": ChannelState(channel_id="b"),
    }


class TestLearner:
    def test_no_feedback_no_change(self) -> None:
        st = _states()
        Learner(ChannelRegistry()).learn({}, st)
        assert all(ch.weight == 1.0 for ch in st.values())

    def test_positive_feedback_boosts_weight(self) -> None:
        st = _states()
        fbs = {"a": Feedback(channel_id="a", revenue=5.0, cost=0.0, success=True)}
        Learner(ChannelRegistry(), alpha=0.3).learn(fbs, st)
        assert st["a"].weight > 1.0
        assert st["b"].weight < 1.0
        # 软最大：权重均值保持约 1
        total = st["a"].weight + st["b"].weight
        assert abs(total - 2.0) < 0.01

    def test_failure_penalizes(self) -> None:
        st = _states()
        fbs = {"a": Feedback(channel_id="a", revenue=0.0, cost=1.0, success=False)}
        Learner(ChannelRegistry()).learn(fbs, st)
        assert st["a"].weight < 1.0

    def test_channel_learn_feedback_hook_called(self) -> None:
        reg = ChannelRegistry()
        ch = ContentPricingChannel()
        reg.register(ch)
        st = _states()
        st["content_pricing"] = ChannelState(channel_id="content_pricing")
        st.pop("b")
        fbs = {"content_pricing": Feedback(channel_id="content_pricing", revenue=2.0, success=True)}
        Learner(reg).learn(fbs, st)
        assert st["content_pricing"].weight != 1.0

    def test_apply_weight(self) -> None:
        learner = Learner(ChannelRegistry())
        assert learner.apply_weight(2.0, 1.5) == 3.0
