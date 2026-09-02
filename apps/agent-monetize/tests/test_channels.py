"""沙箱通道测试：内容计价 + 数据服务。"""

from __future__ import annotations

from agent_monetize.channels.base import Channel
from agent_monetize.channels.content_pricing import ContentPricingChannel, default_content_params
from agent_monetize.channels.data_service import DataServiceChannel, default_data_params
from agent_monetize.channels.registry import ChannelRegistry
from agent_monetize.models import Feedback


class TestContentPricingChannel:
    def test_observe_signal_fields(self) -> None:
        ch = ContentPricingChannel(seed=1)
        signals = ch.observe_signal()
        assert len(signals) == 1
        p = signals[0].payload
        assert p["expected_return"] > 0
        assert 0 <= p["certainty"] <= 1
        assert p["behavior"] is None

    def test_act_deterministic_with_same_seed(self) -> None:
        # 同一种子下两个独立通道实例产生相同结果（RNG 前进不影响跨实例一致性）
        opp = ContentPricingChannel(seed=42).observe_signal()[0]
        r1 = ContentPricingChannel(seed=42).act(
            ContentPricingChannel(seed=42).estimate_opportunity(opp)
        )
        r2 = ContentPricingChannel(seed=42).act(
            ContentPricingChannel(seed=42).estimate_opportunity(opp)
        )
        assert r1.revenue == r2.revenue
        assert r1.revenue >= 0
        assert r1.conversions in (0, 1)
        assert r1.net == r1.revenue - r1.cost

    def test_learn_feedback_noop(self) -> None:
        ch = ContentPricingChannel()
        ch.learn_feedback(Feedback(channel_id="content_pricing", revenue=1.0))
        assert True  # 钩子存在且不抛异常

    def test_default_params(self) -> None:
        assert default_content_params()["read_price"] == 0.5


class TestDataServiceChannel:
    def test_observe_signal_fields(self) -> None:
        ch = DataServiceChannel(seed=2)
        signals = ch.observe_signal()
        p = signals[0].payload
        assert p["expected_return"] > 0
        assert p["behavior"] is None

    def test_act_revenue_positive(self) -> None:
        ch = DataServiceChannel(seed=3)
        opp = ch.estimate_opportunity(ch.observe_signal()[0])
        r = ch.act(opp)
        assert r.revenue > 0
        assert r.conversions >= 1
        assert r.net == r.revenue - r.cost

    def test_volume_discount(self) -> None:
        ch = DataServiceChannel(
            {"per_call_price": 1.0, "volume_discount_threshold": 10, "volume_discount_rate": 0.5},
            seed=5,
        )
        opp = ch.estimate_opportunity(ch.observe_signal()[0])  # 默认调用量 1..20，需构造高调用量
        opp.payload["calls_estimate"] = 100
        r = ch.act(opp)
        assert r.details["discounted"] is True
        assert r.details["unit_price"] == 0.5

    def test_default_params(self) -> None:
        assert default_data_params()["per_call_price"] == 0.8


class TestRegistry:
    def test_register_get_contains(self) -> None:
        reg = ChannelRegistry()
        ch = ContentPricingChannel()
        reg.register(ch)
        assert reg.get("content_pricing") is ch
        assert "content_pricing" in reg
        assert reg.get_or_raise("content_pricing") is ch

    def test_register_empty_id_raises(self) -> None:
        class EmptyIdChannel(Channel):
            channel_id = ""

            def observe_signal(self):
                return []

            def act(self, opportunity):  # type: ignore[no-untyped-def]
                from agent_monetize.models import ActionResult

                return ActionResult(channel_id="", revenue=0.0)

        try:
            ChannelRegistry().register(EmptyIdChannel())
        except ValueError:
            pass
        else:  # pragma: no cover - 不应到达
            raise AssertionError("empty channel_id 应抛 ValueError")

    def test_get_or_raise_missing(self) -> None:
        try:
            ChannelRegistry().get_or_raise("missing")
        except KeyError:
            pass
        else:  # pragma: no cover
            raise AssertionError("missing 应抛 KeyError")

    def test_enabled_and_describe(self) -> None:
        reg = ChannelRegistry()
        reg.register(ContentPricingChannel())
        reg.register(DataServiceChannel())
        assert len(reg.enabled()) == 2
        assert set(reg.describe_all()) == {"content_pricing", "data_service"}
