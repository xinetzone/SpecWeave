"""反馈层（自进化）：基于结果（收益/转化）更新通道权重（软最大 + 指数加权）。

对应公理 A7（可持续正循环：反馈改善下次价值创造）+ 道家「我无为而民自化」
（agent 从反馈中自进化，自组织而非人肉调度）。
"""

from __future__ import annotations

import logging
import math

from ..channels.registry import ChannelRegistry
from ..models import ChannelState, Feedback

logger = logging.getLogger(__name__)


class Learner:
    """自进化学习器：更新通道权重，使下一轮决策受历史结果影响。"""

    def __init__(self, registry: ChannelRegistry, alpha: float = 0.3, scale: float = 10.0) -> None:
        self.registry = registry
        self.alpha = alpha  # 学习率（指数加权的指数系数）
        self.scale = scale  # 净收益归一化尺度（tanh 饱和点，虚拟货币）

    def learn(
        self, feedbacks: dict[str, Feedback], channel_states: dict[str, ChannelState]
    ) -> None:
        """以本轮各通道反馈更新权重（指数加权 → 软最大归一化）。"""
        if not feedbacks:
            return
        channel_ids = list(channel_states.keys())
        if not channel_ids:
            return

        raw: dict[str, float] = {}
        for cid in channel_ids:
            ch = channel_states[cid]
            fb = feedbacks.get(cid)
            growth = 0.0
            if fb is not None:
                # 净收益 → tanh 压缩到 (-1, 1)，乘以学习率后作为指数
                growth = math.tanh(fb.net / self.scale)
                if not fb.success:
                    growth -= 0.2  # 失败额外惩罚
                channel = self.registry.get(cid)
                if channel is not None:
                    channel.learn_feedback(fb)
            raw[cid] = ch.weight * math.exp(self.alpha * growth)

        total = sum(raw.values())
        if total <= 0:
            return
        n = len(channel_ids)
        for cid in channel_ids:
            # 软最大归一化：均值保持约 1（不改变整体机会数量级）
            channel_states[cid].weight = round(raw[cid] / total * n, 4)
        logger.debug("自进化权重更新完成：%s", {c: channel_states[c].weight for c in channel_ids})

    def apply_weight(self, score: float, weight: float) -> float:
        """将权重作用于机会得分（下一轮决策受权重影响）。"""
        return score * weight
