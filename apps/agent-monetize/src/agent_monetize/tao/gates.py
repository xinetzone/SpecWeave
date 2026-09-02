"""道家门控：无为门（动善时）与知止门（知足不辱，知止不殆）。

- 无为门 wuyou：机会确定性 / 预期收益低于阈值 → 不行动（no-op / 待时）。
  对应公理 A7（可持续正循环）+ 道家「动善时」（择时而动，低确定性不行动）。
- 知止门 zhizhi：单通道收益上限、总亏损红线 → 阻断越界行动。
  对应公理 A6（再分配约束）+ 道家「知止不殆」（设红线止损，不无限加杠杆）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from ..config import WuyouConfig, ZhizhiConfig
from ..models import ChannelState, LoopState, Opportunity

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class GateResult:
    """单个门的结果。"""

    name: str
    passed: bool
    reason: str = ""
    level: str = "block"  # block（阻断行动）| limit（限流）| pass


@dataclass(slots=True)
class GateReport:
    """多门联合评估结果。"""

    passed: bool = True
    reasons: list[str] = field(default_factory=list)
    results: list[GateResult] = field(default_factory=list)

    def merge(self, result: GateResult) -> None:
        self.results.append(result)
        if not result.passed:
            self.passed = False
            self.reasons.append(f"[{result.name}] {result.reason}")


class WuyouGate:
    """无为门：机会确定性/预期收益低于阈值则不行动（待时）。"""

    name = "wuyou"

    def __init__(self, config: WuyouConfig | None = None) -> None:
        self.config = config or WuyouConfig()

    def evaluate(self, opportunity: Opportunity) -> GateResult:
        if opportunity.certainty < self.config.min_certainty:
            return GateResult(
                name=self.name,
                passed=False,
                level="limit",
                reason=f"机会确定性 {opportunity.certainty:.2f} 低于阈值 {self.config.min_certainty}，待时而动（无为）",
            )
        if opportunity.expected_return < self.config.min_expected_return:
            return GateResult(
                name=self.name,
                passed=False,
                level="limit",
                reason=(
                    f"预期收益 {opportunity.expected_return:.2f} 低于阈值 "
                    f"{self.config.min_expected_return}，不划算则不行动（无为）"
                ),
            )
        return GateResult(
            name=self.name, passed=True, level="pass", reason="确定性/收益达标，可行动"
        )


class ZhizhiGate:
    """知止门：单通道收益上限 + 总亏损红线。"""

    name = "zhizhi"

    def __init__(self, config: ZhizhiConfig | None = None) -> None:
        self.config = config or ZhizhiConfig()

    def evaluate(
        self,
        channel_state: ChannelState | None,
        global_state: LoopState | None,
        opportunity: Opportunity | None = None,
    ) -> GateResult:
        if (
            channel_state is not None
            and channel_state.revenue >= self.config.per_channel_revenue_cap
        ):
            return GateResult(
                name=self.name,
                passed=False,
                reason=(
                    f"单通道收益 {channel_state.revenue:.2f} 已达上限 "
                    f"{self.config.per_channel_revenue_cap:.2f}，知止不殆"
                ),
            )
        if global_state is not None and global_state.balance <= self.config.total_loss_redline:
            return GateResult(
                name=self.name,
                passed=False,
                reason=(
                    f"总余额 {global_state.balance:.2f} 触及亏损红线 "
                    f"{self.config.total_loss_redline:.2f}，整体停摆止损"
                ),
            )
        return GateResult(
            name=self.name, passed=True, level="pass", reason="未触达收益上限/亏损红线"
        )


class TaoGate:
    """道家治理门控编排器：decide 前过滤机会。"""

    def __init__(
        self, wuyou: WuyouConfig | None = None, zhizhi: ZhizhiConfig | None = None
    ) -> None:
        self.wuyou = WuyouGate(wuyou)
        self.zhizhi = ZhizhiGate(zhizhi)

    def check(
        self,
        opportunity: Opportunity,
        channel_state: ChannelState | None = None,
        global_state: LoopState | None = None,
    ) -> GateReport:
        """对单个机会执行全部门控。任一不过则整体不过。"""
        report = GateReport()
        report.merge(self.wuyou.evaluate(opportunity))
        report.merge(self.zhizhi.evaluate(channel_state, global_state, opportunity))
        return report
