"""trae_edge_case_handler 检测与分级模块。

多信号组合检测（multi-signal-detection模式）和三级分级判断逻辑。
"""

from __future__ import annotations

import logging

from .models import BoundaryLevel, Signal

logger = logging.getLogger(__name__)


def check_multi_signal(
    signals: list[Signal],
    min_positive: int = 1,
) -> tuple[bool, list[str]]:
    """多信号组合检测（遵循 multi-signal-detection 模式）。

    信号源按可靠性排序，至少 min_positive 个正向信号命中即确认边界条件成立。
    反向信号（hit=False）辅助确认"未处于该状态"。

    Args:
        signals: 检测信号列表
        min_positive: 确认成立所需的最小正向信号数

    Returns:
        (是否确认边界条件成立, 命中的正向信号名称列表)
    """
    sorted_signals = sorted(signals, key=lambda s: s.reliability, reverse=True)
    positive_hits = [s.name for s in sorted_signals if s.hit]

    confirmed = len(positive_hits) >= min_positive

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "多信号检测: confirmed=%s, positive=%s, negative=%s",
            confirmed,
            positive_hits,
            [s.name for s in sorted_signals if not s.hit],
        )

    return confirmed, positive_hits


def classify_boundary_level(
    core_resource_available: bool,
    state_abnormal: bool,
    affects_main_flow: bool,
) -> BoundaryLevel:
    """边界条件三级分级判断。

    对应规范文档中的分级决策图（第132-145行）：
      - 核心资源不可用 → 致命（fatal）
      - 核心资源可用但状态异常 → 警告（warning）
      - 核心资源可用且不影响主流程 → 提示（info）

    Args:
        core_resource_available: 核心资源（沙箱/凭证/工具）是否可用
        state_abnormal: 状态是否异常（过期/限流/DOM变化）
        affects_main_flow: 是否影响主流程

    Returns:
        边界条件级别
    """
    if not core_resource_available:
        return BoundaryLevel.FATAL
    if state_abnormal:
        return BoundaryLevel.WARNING
    if affects_main_flow:
        return BoundaryLevel.WARNING
    return BoundaryLevel.INFO
