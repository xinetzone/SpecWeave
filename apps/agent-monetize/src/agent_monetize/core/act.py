"""行动层：执行通道交付与计价（A1 交付价值 / A2 完成交换）。"""

from __future__ import annotations

import logging

from ..channels.base import Channel
from ..models import ActionResult, Opportunity

logger = logging.getLogger(__name__)


class Actor:
    """行动器：将决策交给对应通道执行。"""

    def execute(self, channel: Channel, opportunity: Opportunity) -> ActionResult:
        result = channel.act(opportunity)
        logger.info(
            "通道 [%s] 执行完成：revenue=%.2f cost=%.2f net=%.2f success=%s",
            channel.channel_id,
            result.revenue,
            result.cost,
            result.net,
            result.success,
        )
        return result
