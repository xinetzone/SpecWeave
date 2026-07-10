"""trae_edge_case_handler 边界条件注册表模块。

边界条件注册、查询和检测入口。
"""

from __future__ import annotations

import logging
from typing import Optional

from .detection import check_multi_signal
from .models import (
    BoundaryAction,
    BoundaryCondition,
    BoundaryContext,
    BoundaryDecision,
    BoundaryLevel,
)

logger = logging.getLogger(__name__)

_BOUNDARY_REGISTRY: dict[str, BoundaryCondition] = {}


def register_boundary(condition: BoundaryCondition) -> None:
    """注册边界条件到全局注册表。"""
    _BOUNDARY_REGISTRY[condition.name] = condition
    logger.debug("注册边界条件: %s (级别: %s)", condition.name, condition.default_level.value)


def get_boundary(name: str) -> BoundaryCondition | None:
    """从注册表查询边界条件。"""
    return _BOUNDARY_REGISTRY.get(name)


def check_boundary(
    name: str,
    context: BoundaryContext,
) -> BoundaryDecision:
    """边界检测入口：查找注册表并执行检测。

    遵循 check-and-restore 模式——检查不改变状态。

    Args:
        name: 边界条件名称
        context: 边界上下文

    Returns:
        边界处理决策（含级别和初始 action）
    """
    condition = _BOUNDARY_REGISTRY.get(name)
    if condition is None:
        logger.warning("未注册的边界条件: %s，视为无边界", name)
        return BoundaryDecision(
            boundary_type=name,
            level=BoundaryLevel.INFO,
            action=BoundaryAction.CONTINUE,
            rationale=f"边界条件 {name} 未注册，跳过检测",
        )

    signals = []
    if condition.check_fn:
        signals = condition.check_fn(context)

    confirmed, hits = check_multi_signal(signals)

    if not confirmed:
        return BoundaryDecision(
            boundary_type=name,
            level=BoundaryLevel.INFO,
            action=BoundaryAction.CONTINUE,
            rationale=f"边界条件 {name} 多信号未确认成立",
            signals_hit=hits,
        )

    return BoundaryDecision(
        boundary_type=name,
        level=condition.default_level,
        action=BoundaryAction.CONTINUE if condition.default_level == BoundaryLevel.INFO else BoundaryAction.DEGRADE,
        rationale=f"边界条件 {name} 确认成立，级别: {condition.default_level.value}",
        signals_hit=hits,
    )
