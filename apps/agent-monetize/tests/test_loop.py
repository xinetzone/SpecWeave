"""端到端自主循环测试：observe → decide → act → learn + 状态持久化。"""

from __future__ import annotations

import os

import pytest

from agent_monetize.channels.content_pricing import ContentPricingChannel
from agent_monetize.channels.data_service import DataServiceChannel
from agent_monetize.channels.registry import ChannelRegistry
from agent_monetize.config import Config, load_config
from agent_monetize.core.ffi_bridge import default_bridge
from agent_monetize.core.loop import AgentLoop
from agent_monetize.core.state import StateStore
from agent_monetize.models import LoopState

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
CONFIG_YAML = os.path.join(PROJECT_ROOT, "config.yaml")


def _make_config() -> Config:
    cfg = load_config(CONFIG_YAML)
    cfg.loop.state_path = ""  # 测试默认不落盘
    return cfg


def _make_loop(cfg: Config | None = None) -> AgentLoop:
    cfg = cfg or _make_config()
    registry = ChannelRegistry()
    registry.register(ContentPricingChannel(seed=cfg.app.seed))
    registry.register(DataServiceChannel(seed=cfg.app.seed + 1))
    bridge = default_bridge(native_lib_paths=[])
    return AgentLoop(config=cfg, registry=registry, bridge=bridge)


class TestLoop:
    def test_run_rounds_returns_records(self) -> None:
        loop = _make_loop()
        records = loop.run(6)
        assert len(records) == 6
        assert all(rec.round == i + 1 for i, rec in enumerate(records))
        assert loop.state.round_count == 6

    def test_decisions_are_act_or_noop(self) -> None:
        loop = _make_loop()
        for rec in loop.run(12):
            assert rec.decision.action in ("act", "no-op")

    def test_balance_consistency(self) -> None:
        loop = _make_loop()
        loop.run(8)
        # 全局余额 = 各通道净收益之和（_apply_result 同步维护两者）
        assert loop.state.balance == round(sum(ch.net for ch in loop.state.channels.values()), 3)

    def test_summary_structure(self) -> None:
        loop = _make_loop()
        loop.run(4)
        s = loop.summary()
        assert s["rounds"] == 4
        assert set(s["channels"]) == {"content_pricing", "data_service"}
        assert s["balance"] >= s["total_revenue"] - s["total_cost"] - 1e-9

    def test_weights_evolve(self) -> None:
        loop = _make_loop()
        loop.run(10)
        weights = {cid: ch.weight for cid, ch in loop.state.channels.items()}
        # 权重经自进化应偏离初始值 1.0（至少一个通道）
        assert any(abs(w - 1.0) > 1e-6 for w in weights.values())

    def test_persistence_roundtrip(self, tmp_path) -> None:
        cfg = _make_config()
        cfg.loop.state_path = str(tmp_path / "state.json")
        cfg.loop.persist_every = 1
        loop = _make_loop(cfg)
        loop.run(3)

        loaded = StateStore().load(cfg.loop.state_path)
        assert loaded is not None
        assert loaded.round_count == 3
        assert set(loaded.channels) == {"content_pricing", "data_service"}

    def test_state_restore_from_disk(self, tmp_path) -> None:
        path = str(tmp_path / "state.json")
        state = LoopState(balance=99.0, round_count=7)
        StateStore().save(state, path)

        cfg = _make_config()
        cfg.loop.state_path = path
        loop = _make_loop(cfg)
        assert loop.state.balance == 99.0
        assert loop.state.round_count == 7


class TestObserverDecider:
    def test_decider_noop_when_no_opportunities(self) -> None:
        from agent_monetize.compliance.policies import ComplianceEngine
        from agent_monetize.core.decide import Decider
        from agent_monetize.tao.gates import TaoGate

        reg = ChannelRegistry()
        decider = Decider(reg, TaoGate(), ComplianceEngine())
        decision = decider.decide([], {})
        assert decision.action == "no-op"

    def test_observer_scores_with_weights(self) -> None:
        from agent_monetize.channels.base import Channel
        from agent_monetize.core.observe import Observer
        from agent_monetize.models import ActionResult, Signal

        class FixedChannel(Channel):
            channel_id = "fixed"

            def observe_signal(self) -> list[Signal]:
                return [
                    Signal(
                        channel_id="fixed",
                        payload={
                            "expected_return": 8.0,
                            "certainty": 0.9,
                            "scarcity_factor": 1.0,
                            "est_cost": 0.2,
                        },
                    )
                ]

            def act(self, opportunity) -> ActionResult:  # type: ignore[no-untyped-def]
                return ActionResult(channel_id="fixed", revenue=1.0)

        reg = ChannelRegistry()
        reg.register(FixedChannel())
        bridge = default_bridge(native_lib_paths=[])
        opps = Observer(reg, bridge).scan({"fixed": 2.0})
        base = Observer(reg, bridge).scan({"fixed": 1.0})
        assert opps
        # 权重 2.0 使得分翻倍（固定信号，无 RNG 漂移）；得分按 4 位小数舍入，允许舍入误差
        assert opps[0].score == pytest.approx(base[0].score * 2.0, abs=0.002)
