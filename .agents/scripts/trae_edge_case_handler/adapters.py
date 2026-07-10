"""trae_edge_case_handler 特殊场景适配策略模块。

4个预定义适配策略：沙箱限制、PowerShell编码、论坛登录过期、DOM结构变化。
"""

from __future__ import annotations

import logging
from typing import Optional
from collections.abc import Callable

from .detection import check_multi_signal
from .models import BoundaryAction, BoundaryContext, BoundaryDecision, BoundaryLevel, Signal

logger = logging.getLogger(__name__)


def adapt_sandbox_limitation(
    context: BoundaryContext,
    use_integrated_browser: bool = False,
    user_confirmed_disable: bool = False,
) -> BoundaryDecision:
    """沙箱限制适配策略（规范文档第217-225行）。

    优先级：
      1. 优先使用 Trae 集成浏览器（已登录无沙箱限制）
      2. 使用 dangerouslyDisableSandbox 绕过（需用户确认）
      3. 回退到手动操作指引

    Args:
        context: 边界上下文
        use_integrated_browser: 是否可用集成浏览器
        user_confirmed_disable: 用户是否确认禁用沙箱

    Returns:
        适配决策
    """
    if use_integrated_browser:
        return BoundaryDecision(
            boundary_type="trae-ide-sandbox-limitation",
            level=BoundaryLevel.INFO,
            action=BoundaryAction.CONTINUE,
            rationale="使用 Trae 集成浏览器绕过沙箱限制",
            fallback_used="integrated_browser",
            recovered=True,
        )

    if user_confirmed_disable:
        return BoundaryDecision(
            boundary_type="trae-ide-sandbox-limitation",
            level=BoundaryLevel.WARNING,
            action=BoundaryAction.DEGRADE,
            rationale="用户确认后禁用沙箱，须识别具体受限资源",
            fallback_used="dangerouslyDisableSandbox",
            recovered=True,
        )

    return BoundaryDecision(
        boundary_type="trae-ide-sandbox-limitation",
        level=BoundaryLevel.FATAL,
        action=BoundaryAction.EXIT,
        rationale="沙箱限制无法绕过，回退到手动操作指引",
        fallback_used=None,
        recovered=False,
    )


def adapt_powershell_encoding(
    context: BoundaryContext,
    is_multiline: bool = False,
    garbled_affects_result: bool = False,
) -> BoundaryDecision:
    """PowerShell 编码适配策略（规范文档第227-235行）。

    优先级：
      1. 多行文本使用 -F 文件参数而非 -m 内联参数
      2. 中文乱码不影响实际内容时忽略
      3. 编码冲突时显式设置 chcp 65001

    Args:
        context: 边界上下文
        is_multiline: 是否为多行文本命令
        garbled_affects_result: 乱码是否影响结果判断

    Returns:
        适配决策
    """
    if is_multiline:
        return BoundaryDecision(
            boundary_type="trae-toolchain-powershell-encoding",
            level=BoundaryLevel.INFO,
            action=BoundaryAction.CONTINUE,
            rationale="多行文本使用 -F 文件参数避免引号转义问题",
            fallback_used="file_parameter",
            recovered=True,
        )

    if not garbled_affects_result:
        return BoundaryDecision(
            boundary_type="trae-toolchain-powershell-encoding",
            level=BoundaryLevel.INFO,
            action=BoundaryAction.CONTINUE,
            rationale="乱码仅出现在日志输出，不影响实际内容，忽略",
            fallback_used="ignore_garble",
            recovered=True,
        )

    return BoundaryDecision(
        boundary_type="trae-toolchain-powershell-encoding",
        level=BoundaryLevel.WARNING,
        action=BoundaryAction.DEGRADE,
        rationale="乱码影响结果判断，显式设置 chcp 65001 切换至 UTF-8",
        fallback_used="chcp_65001",
        recovered=True,
    )


def adapt_forum_login_expired(
    context: BoundaryContext,
    signals: list[Signal],
    relogin_fn: Callable[[], bool] | None = None,
    verify_fn: Callable[[], bool] | None = None,
) -> BoundaryDecision:
    """论坛登录状态过期适配策略（规范文档第237-246行）。

    流程：
      1. 多信号确认过期
      2. 提示用户重新执行 login 命令
      3. 重新登录后恢复操作
      4. 记录过期频率用于优化

    Args:
        context: 边界上下文
        signals: 登录状态检测信号
        relogin_fn: 重新登录函数
        verify_fn: 登录态验证函数

    Returns:
        适配决策
    """
    confirmed, hits = check_multi_signal(signals, min_positive=2)

    if not confirmed:
        return BoundaryDecision(
            boundary_type="trae-forum-login-expired",
            level=BoundaryLevel.INFO,
            action=BoundaryAction.CONTINUE,
            rationale="多信号未确认登录过期，继续操作",
            signals_hit=hits,
        )

    logger.warning("论坛登录状态过期，信号命中: %s", hits)

    if relogin_fn and verify_fn:
        try:
            if relogin_fn() and verify_fn():
                return BoundaryDecision(
                    boundary_type="trae-forum-login-expired",
                    level=BoundaryLevel.WARNING,
                    action=BoundaryAction.CONTINUE,
                    rationale="登录过期通过重新登录恢复",
                    signals_hit=hits,
                    fallback_used="relogin",
                    recovered=True,
                )
        except Exception as e:
            logger.error("重新登录失败: %s", e)

    return BoundaryDecision(
        boundary_type="trae-forum-login-expired",
        level=BoundaryLevel.WARNING,
        action=BoundaryAction.EXIT,
        rationale="登录过期且无法自动恢复，请手动执行 login 命令",
        signals_hit=hits,
        fallback_used=None,
        recovered=False,
    )


def adapt_dom_structure_change(
    context: BoundaryContext,
    semantic_locator_available: bool = False,
    backup_selectors: list[str] | None = None,
    js_query_fn: Callable[[], bool] | None = None,
) -> BoundaryDecision:
    """DOM 结构变化适配策略（规范文档第248-257行）。

    优先级：
      1. 优先使用语义定位（文本/role/label）
      2. 使用多选择器备选链
      3. 使用 JavaScript DOM 查询兜底
      4. 记录新 DOM 结构用于更新选择器常量

    Args:
        context: 边界上下文
        semantic_locator_available: 语义定位器是否可用
        backup_selectors: 备选选择器列表
        js_query_fn: JS DOM 查询函数（返回是否成功）

    Returns:
        适配决策
    """
    if semantic_locator_available:
        return BoundaryDecision(
            boundary_type="trae-forum-dom-change",
            level=BoundaryLevel.INFO,
            action=BoundaryAction.CONTINUE,
            rationale="使用语义定位（role/label/text）适配 DOM 变化",
            fallback_used="semantic_locator",
            recovered=True,
        )

    if backup_selectors:
        return BoundaryDecision(
            boundary_type="trae-forum-dom-change",
            level=BoundaryLevel.WARNING,
            action=BoundaryAction.DEGRADE,
            rationale=f"使用 {len(backup_selectors)} 个备选选择器适配 DOM 变化",
            fallback_used="backup_selectors",
            recovered=True,
        )

    if js_query_fn:
        try:
            if js_query_fn():
                return BoundaryDecision(
                    boundary_type="trae-forum-dom-change",
                    level=BoundaryLevel.WARNING,
                    action=BoundaryAction.DEGRADE,
                    rationale="使用 JavaScript DOM 查询兜底",
                    fallback_used="js_dom_query",
                    recovered=True,
                )
        except Exception as e:
            logger.warning("JS DOM 查询失败: %s", e)

    return BoundaryDecision(
        boundary_type="trae-forum-dom-change",
        level=BoundaryLevel.FATAL,
        action=BoundaryAction.EXIT,
        rationale="DOM 变化导致所有定位策略失效，需更新选择器常量",
        fallback_used=None,
        recovered=False,
    )
