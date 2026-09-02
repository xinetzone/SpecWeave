"""自主循环编排：observe → decide → act → learn，支持定时/事件驱动与状态持久化。"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from ..channels.registry import ChannelRegistry
from ..compliance.policies import ComplianceConfig, ComplianceEngine
from ..config import Config, build_initial_loop_state
from ..models import ActionResult, ChannelState, Decision, Feedback, Opportunity
from ..tao.gates import TaoGate
from .act import Actor
from .decide import Decider
from .ffi_bridge import FfiBridge
from .learn import Learner
from .observe import Observer
from .state import StateStore

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RoundRecord:
    """单轮循环记录。"""

    round: int
    decision: Decision
    opportunities: list[Opportunity] = field(default_factory=list)
    action_result: ActionResult | None = None
    feedback: Feedback | None = None
    weight_snapshot: dict[str, float] = field(default_factory=dict)


class AgentLoop:
    """智能体自主循环（四步闭环）。"""

    def __init__(
        self,
        config: Config,
        registry: ChannelRegistry,
        bridge: FfiBridge,
        observer: Observer | None = None,
        decider: Decider | None = None,
        actor: Actor | None = None,
        learner: Learner | None = None,
        state_store: StateStore | None = None,
    ) -> None:
        self.config = config
        self.registry = registry
        self.bridge = bridge

        compliance = ComplianceEngine(
            ComplianceConfig(
                enable_red_zone=config.compliance.enable_red_zone,
                require_confirmation=config.compliance.require_confirmation,
                confirmed_behaviors=list(config.compliance.confirmed_behaviors),
            )
        )
        tao_gate = TaoGate(config.tao.wuyou, config.tao.zhizhi)

        self.observer = observer or Observer(registry, bridge)
        self.decider = decider or Decider(registry, tao_gate, compliance)
        self.actor = actor or Actor()
        self.learner = learner or Learner(registry)
        self.state_store = state_store or StateStore()

        # 状态：优先从持久化文件恢复，否则初始构建
        self.state = build_initial_loop_state(config)
        if config.loop.state_path:
            restored = self.state_store.load(config.loop.state_path)
            if restored is not None:
                self.state = restored

    # -- 单轮 ---------------------------------------------------------
    def run_round(self) -> RoundRecord:
        state = self.state
        weights = {cid: ch.weight for cid, ch in state.channels.items()}

        # 1) observe：机会发现 + 打分（权重影响得分 = 自进化作用于决策）
        opportunities = self.observer.scan(weights)

        # 2) decide：合规 + 通道适配 + 道家门控
        decision = self.decider.decide(opportunities, state.channels, state)

        action_result: ActionResult | None = None
        feedback: Feedback | None = None

        # 3) act：执行最优机会
        if decision.action == "act" and decision.channel_id is not None:
            opp = self._best_opportunity(opportunities, decision.channel_id)
            if opp is None:
                decision = Decision(
                    channel_id=decision.channel_id,
                    action="no-op",
                    score=decision.score,
                    reason="决策目标机会丢失",
                )
            else:
                channel = self.registry.get_or_raise(decision.channel_id)
                action_result = self.actor.execute(channel, opp)
                self._apply_result(decision.channel_id, action_result)
                feedback = Feedback(
                    channel_id=decision.channel_id,
                    revenue=action_result.revenue,
                    cost=action_result.cost,
                    conversions=action_result.conversions,
                    success=action_result.success,
                    details=action_result.details,
                )

        # 4) learn：自进化权重更新（仅在本轮实际行动后有反馈时更新）
        if feedback is not None:
            self.learner.learn({feedback.channel_id: feedback}, state.channels)

        state.round_count += 1

        # 持久化
        if self.config.loop.state_path and (
            state.round_count % max(1, self.config.loop.persist_every) == 0
        ):
            self.state_store.save(state, self.config.loop.state_path)

        record = RoundRecord(
            round=state.round_count,
            decision=decision,
            opportunities=opportunities,
            action_result=action_result,
            feedback=feedback,
            weight_snapshot={cid: ch.weight for cid, ch in state.channels.items()},
        )
        self._log_round(record)
        return record

    # -- 多轮 ---------------------------------------------------------
    def run(self, rounds: int | None = None) -> list[RoundRecord]:
        """连续运行 N 轮；支持定时（event_driven）驱动。"""
        rounds = rounds or self.config.loop.rounds
        records: list[RoundRecord] = []
        for _ in range(rounds):
            records.append(self.run_round())
            if self.config.loop.event_driven and self.config.loop.interval_seconds > 0:
                time.sleep(self.config.loop.interval_seconds)
        return records

    # -- 内部工具 -----------------------------------------------------
    @staticmethod
    def _best_opportunity(opportunities: list[Opportunity], channel_id: str) -> Opportunity | None:
        matches = [o for o in opportunities if o.channel_id == channel_id]
        if not matches:
            return None
        return max(matches, key=lambda o: o.score)

    def _apply_result(self, channel_id: str, result: ActionResult) -> None:
        ch = self.state.channels.get(channel_id)
        if ch is None:
            ch = ChannelState(channel_id=channel_id)
            self.state.channels[channel_id] = ch
        ch.revenue = round(ch.revenue + result.revenue, 3)
        ch.cost = round(ch.cost + result.cost, 3)
        ch.conversions += result.conversions
        ch.actions += 1
        ch.history.append(
            {
                "round": self.state.round_count,
                "revenue": result.revenue,
                "cost": result.cost,
                "net": result.net,
                "success": result.success,
                "details": result.details,
            }
        )
        self.state.balance = round(self.state.balance + result.net, 3)

    def _log_round(self, record: RoundRecord) -> None:
        d = record.decision
        if d.action == "act":
            r = record.action_result
            assert r is not None
            logger.info(
                "round=%d 行动 通道=%s score=%.3f net=%.2f balance=%.2f",
                record.round,
                d.channel_id,
                d.score,
                r.net,
                self.state.balance,
            )
        else:
            logger.info(
                "round=%d 待时(no-op) 原因=%s balance=%.2f",
                record.round,
                d.reason,
                self.state.balance,
            )

    # -- 汇总 ---------------------------------------------------------
    def summary(self) -> dict[str, Any]:
        state = self.state
        return {
            "rounds": state.round_count,
            "balance": state.balance,
            "total_revenue": state.total_revenue,
            "total_cost": state.total_cost,
            "channels": {
                cid: {
                    "weight": ch.weight,
                    "net": ch.net,
                    "revenue": ch.revenue,
                    "cost": ch.cost,
                    "actions": ch.actions,
                    "conversions": ch.conversions,
                }
                for cid, ch in state.channels.items()
            },
        }
