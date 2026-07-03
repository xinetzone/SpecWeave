"""trae_edge_case_handler 异常处理流程模块。

致命/警告/提示三级处理流程及统一分发入口。
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Optional

from .models import BoundaryAction, BoundaryContext, BoundaryDecision, BoundaryLevel

logger = logging.getLogger(__name__)


def handle_fatal_boundary(
    condition_name: str,
    context: BoundaryContext,
    alternatives: Optional[list[Callable[[], bool]]] = None,
    notifier: Optional[Callable[[str, str], None]] = None,
) -> BoundaryDecision:
    """致命级处理流程（规范文档第149-172行）。

    流程：记录诊断日志 → 尝试替代方案 → 若无替代则优雅退出 → 通知用户。

    Args:
        condition_name: 边界条件名称
        context: 边界上下文
        alternatives: 替代方案列表（按优先级排序，每个返回是否成功）
        notifier: 通知函数（接收消息和手动操作指引）

    Returns:
        边界处理决策（action 通常为 EXIT，若替代成功则为 CONTINUE）
    """
    logger.error(
        "[FATAL] 致命边界条件: %s | 操作: %s | 平台: %s",
        condition_name, context.operation, context.platform,
    )

    fallback_used = None
    recovered = False

    if alternatives:
        for i, alt_fn in enumerate(alternatives):
            alt_name = f"alternative_{i + 1}"
            logger.info("尝试替代方案 %s", alt_name)
            try:
                if alt_fn():
                    fallback_used = alt_name
                    recovered = True
                    logger.info("替代方案 %s 生效", alt_name)
                    break
            except Exception as e:
                logger.warning("替代方案 %s 失败: %s", alt_name, e)

    if recovered:
        action = BoundaryAction.CONTINUE
        rationale = f"致命边界 {condition_name} 通过替代方案 {fallback_used} 恢复"
    else:
        action = BoundaryAction.EXIT
        rationale = f"致命边界 {condition_name} 无可用替代方案，需退出"
        if notifier:
            manual_guide = (
                f"操作 {context.operation} 受阻于 {condition_name}。\n"
                f"请手动执行该操作，或检查环境配置后重试。"
            )
            notifier(f"边界阻断: {condition_name}", manual_guide)

    return BoundaryDecision(
        boundary_type=condition_name,
        level=BoundaryLevel.FATAL,
        action=action,
        rationale=rationale,
        fallback_used=fallback_used,
        recovered=recovered,
    )


def handle_warning_boundary(
    condition_name: str,
    context: BoundaryContext,
    degrade_fn: Optional[Callable[[], bool]] = None,
    verify_fn: Optional[Callable[[], bool]] = None,
    max_retries: int = 2,
) -> BoundaryDecision:
    """警告级处理流程（规范文档第174-196行）。

    流程：记录警告日志 → 执行降级操作 → 验证恢复结果 → 继续或升级。

    降级操作遵循 dry-run-first 原则（涉及状态变更时先预览再执行）。
    同一警告级边界在单次任务内降级失败 ≥ max_retries 次，升级为致命级。

    Args:
        condition_name: 边界条件名称
        context: 边界上下文
        degrade_fn: 降级操作函数（返回是否执行成功）
        verify_fn: 验证恢复函数（返回是否恢复成功）
        max_retries: 最大降级重试次数，超过后升级为致命

    Returns:
        边界处理决策（CONTINUE 或升级为 EXIT）
    """
    logger.warning(
        "[WARNING] 警告边界条件: %s | 操作: %s", condition_name, context.operation,
    )

    fallback_used = None
    recovered = False
    retry_count = 0

    if degrade_fn:
        for attempt in range(1, max_retries + 1):
            logger.info("降级操作第 %d/%d 次尝试", attempt, max_retries)
            try:
                if degrade_fn():
                    fallback_used = f"degrade_attempt_{attempt}"
                    if verify_fn:
                        recovered = verify_fn()
                    else:
                        recovered = True
                    if recovered:
                        logger.info("降级操作成功，恢复验证通过")
                        break
                    else:
                        logger.warning("降级操作执行但恢复验证失败")
                else:
                    logger.warning("降级操作第 %d 次失败", attempt)
            except Exception as e:
                logger.warning("降级操作第 %d 次异常: %s", attempt, e)
            retry_count = attempt

    if recovered:
        action = BoundaryAction.CONTINUE
        rationale = f"警告边界 {condition_name} 通过降级操作恢复"
    elif retry_count >= max_retries:
        action = BoundaryAction.EXIT
        rationale = (
            f"警告边界 {condition_name} 降级失败 {retry_count} 次，升级为致命"
        )
        logger.error("[FATAL] %s", rationale)
    else:
        action = BoundaryAction.DEGRADE
        rationale = f"警告边界 {condition_name} 无降级方案，标记降级继续"

    return BoundaryDecision(
        boundary_type=condition_name,
        level=BoundaryLevel.WARNING if recovered else BoundaryLevel.FATAL,
        action=action,
        rationale=rationale,
        fallback_used=fallback_used,
        recovered=recovered,
    )


def handle_info_boundary(
    condition_name: str,
    context: BoundaryContext,
) -> BoundaryDecision:
    """提示级处理流程（规范文档第198-211行）。

    流程：记录提示日志 → 继续原操作 → 操作完成后汇总报告。

    提示级边界不触发任何状态变更，仅记录供汇总。
    """
    logger.info(
        "[INFO] 提示边界条件: %s | 操作: %s | 记录供汇总", condition_name, context.operation,
    )

    return BoundaryDecision(
        boundary_type=condition_name,
        level=BoundaryLevel.INFO,
        action=BoundaryAction.CONTINUE,
        rationale=f"提示边界 {condition_name} 不影响主流程，继续操作",
    )


def handle_boundary(
    decision: BoundaryDecision,
    context: BoundaryContext,
    **kwargs: Any,
) -> BoundaryDecision:
    """统一边界处理入口，根据级别分发到对应处理流程。

    Args:
        decision: 已检测并分级的边界决策（需包含 level）
        context: 边界上下文
        **kwargs: 传递给具体处理函数的额外参数

    Returns:
        更新后的边界处理决策
    """
    level = decision.level
    name = decision.boundary_type

    if level == BoundaryLevel.FATAL:
        return handle_fatal_boundary(name, context, **kwargs)
    elif level == BoundaryLevel.WARNING:
        return handle_warning_boundary(name, context, **kwargs)
    else:
        return handle_info_boundary(name, context)
