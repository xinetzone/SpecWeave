"""红绿区合规策略。

- 红区（禁行）：欺诈、垃圾、诱导点击、未授权数据、荐股、医疗诊断等——任何情况下不得执行。
  对应公理 A5（信任=通用货币，欺诈透支长期信任）与 A2（自愿交换，欺骗不可持续）。
- 绿区（许可）：真实 API 通道需 `enable_real=true` 且用户显式合规确认后才启用。
  对应公理 A5（信誉积累降低信任成本）——真实模式必须有人工可审计的确认。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..models import Opportunity

# 红区禁行行为清单：id → 中文说明
RED_ZONE_BEHAVIORS: dict[str, str] = {
    "fraud": "欺诈（伪造交易/虚假承诺）",
    "spam": "垃圾（未经同意的批量骚扰消息）",
    "clickbait": "诱导点击（夸大/误导性标题或按钮）",
    "unauthorized_data": "未授权数据（未获同意收集或使用个人数据）",
    "stock_tip": "荐股（无资质投资建议）",
    "medical_diagnosis": "医疗诊断（无资质疾病诊断或用药建议）",
}


@dataclass(slots=True)
class ComplianceVerdict:
    """合规判定结果。"""

    allowed: bool
    reason: str = ""
    zone: str = "green"  # red | green


@dataclass(slots=True)
class ComplianceConfig:
    """合规配置（与 config.ComplianceConfig 兼容的轻量视图）。"""

    enable_red_zone: bool = True
    require_confirmation: bool = True
    confirmed_behaviors: list[str] = field(default_factory=list)


def _intent_behavior(opportunity: Opportunity | dict[str, Any]) -> str | None:
    """从机会（或机会 dict）中提取行为标签。"""
    payload = (
        opportunity.payload
        if isinstance(opportunity, Opportunity)
        else opportunity.get("payload", {})
    )
    if not isinstance(payload, dict):
        return None
    return payload.get("behavior")


def _intent_real_mode(opportunity: Opportunity | dict[str, Any]) -> bool:
    payload = (
        opportunity.payload
        if isinstance(opportunity, Opportunity)
        else opportunity.get("payload", {})
    )
    if not isinstance(payload, dict):
        return False
    return bool(payload.get("real_mode", False))


class ComplianceEngine:
    """红绿区合规引擎：decide 之前过滤。"""

    def __init__(self, config: ComplianceConfig | None = None) -> None:
        self.config = config or ComplianceConfig()

    def check(self, opportunity: Opportunity | dict[str, Any]) -> ComplianceVerdict:
        """对机会做合规判定：红区禁行 → 真实模式需确认 → 绿区放行。"""
        behavior = _intent_behavior(opportunity)
        if self.config.enable_red_zone and behavior in RED_ZONE_BEHAVIORS:
            return ComplianceVerdict(
                allowed=False,
                zone="red",
                reason=f"红区禁行行为「{behavior}」：{RED_ZONE_BEHAVIORS[behavior]}",
            )
        if _intent_real_mode(opportunity) and self.config.require_confirmation:
            if behavior not in self.config.confirmed_behaviors:
                return ComplianceVerdict(
                    allowed=False,
                    zone="green",
                    reason=(
                        f"真实模式行为「{behavior}」未获用户显式合规确认，"
                        f"需加入 compliance.confirmed_behaviors 后方可启用"
                    ),
                )
        return ComplianceVerdict(allowed=True, zone="green", reason="合规放行")

    @property
    def red_zone_summary(self) -> str:
        return "；".join(f"{k}={v}" for k, v in RED_ZONE_BEHAVIORS.items())
