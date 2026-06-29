"""trae_edge_case_handler.py — Trae 边界情况处理决策模块。

从 .agents/teams/trae-edge-case-handler.md 规范文档提取的可执行决策逻辑，
覆盖四大边界场景的检测、三级分级、异常处理流程与特殊场景适配策略。

核心能力：
  - 多信号组合检测（遵循 multi-signal-detection 模式）
  - 三级分级判断（致命/警告/提示）
  - 标准化异常处理流程（检测→分级→处理→决策）
  - 4个预定义适配策略（沙箱/PowerShell/登录过期/DOM变化）

使用示例：
  from trae_edge_case_handler import (
      check_boundary, handle_boundary, BoundaryContext
  )

  context = BoundaryContext(operation="forum_reply", platform="windows")
  decision = check_boundary("trae-forum-login-expired", context)
  result = handle_boundary(decision, context)

设计原则：
  - 检查函数不改变状态（遵循 check-and-restore 模式）
  - 降级操作遵循 dry-run-first 原则
  - 所有决策通过返回值传递，不通过副作用
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


# ============================================================================
# 数据模型
# ============================================================================

class BoundaryLevel(Enum):
    """边界条件三级分级（规范文档第120-128行）。"""

    FATAL = "fatal"
    WARNING = "warning"
    INFO = "info"


class BoundaryScene(Enum):
    """四大边界场景（规范文档第30-57行）。"""

    IDE_INTEGRATION = "trae-ide-integration"
    FORUM_OPERATION = "trae-forum-operation"
    EXTERNAL_TOOLCHAIN = "trae-external-toolchain"
    TRAE_WORK = "trae-work"


class BoundaryAction(Enum):
    """处理决策动作（规范文档第267-268行）。"""

    CONTINUE = "continue"
    DEGRADE = "degrade"
    EXIT = "exit"


@dataclass
class Signal:
    """检测信号（规范文档第112-118行）。

    遵循多信号组合检测模式，每个信号有可靠性排序，
    反向信号（hit=False）辅助确认"未处于该状态"。
    """

    name: str
    hit: bool
    value: Any = None
    reliability: int = 0


@dataclass
class BoundaryCondition:
    """边界条件定义（规范文档第63-104行）。"""

    name: str
    scene: BoundaryScene
    default_level: BoundaryLevel
    description: str = ""
    check_fn: Optional[Callable[[BoundaryContext], list[Signal]]] = None


@dataclass
class BoundaryContext:
    """边界检测上下文，传递环境信息与操作意图。"""

    operation: str = ""
    platform: str = ""
    tool_version: str = ""
    env_vars: dict[str, str] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class BoundaryDecision:
    """边界处理决策（规范文档第272-286行）。

    对应规范文档中的输出接口决策 JSON。
    """

    boundary_type: str
    level: BoundaryLevel
    action: BoundaryAction
    rationale: str
    signals_hit: list[str] = field(default_factory=list)
    fallback_used: Optional[str] = None
    recovered: bool = False
    diagnostic_log: str = ""


# ============================================================================
# 多信号组合检测（规范文档第108-118行）
# ============================================================================

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


# ============================================================================
# 三级分级判断（规范文档第120-145行）
# ============================================================================

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


# ============================================================================
# 异常处理流程（规范文档第147-211行）
# ============================================================================

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

    # 尝试替代方案
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

    # 决策
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

    # 决策
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


# ============================================================================
# 特殊场景适配策略（规范文档第213-257行）
# ============================================================================

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
    relogin_fn: Optional[Callable[[], bool]] = None,
    verify_fn: Optional[Callable[[], bool]] = None,
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
    backup_selectors: Optional[list[str]] = None,
    js_query_fn: Optional[Callable[[], bool]] = None,
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


# ============================================================================
# 边界条件注册表（规范文档第63-104行的19个边界条件）
# ============================================================================

_BOUNDARY_REGISTRY: dict[str, BoundaryCondition] = {}


def register_boundary(condition: BoundaryCondition) -> None:
    """注册边界条件到全局注册表。"""
    _BOUNDARY_REGISTRY[condition.name] = condition
    logger.debug("注册边界条件: %s (级别: %s)", condition.name, condition.default_level.value)


def get_boundary(name: str) -> Optional[BoundaryCondition]:
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

    signals: list[Signal] = []
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


# ============================================================================
# 预定义边界条件注册
# ============================================================================

def _init_default_boundaries() -> None:
    """初始化规范文档中定义的19个默认边界条件。"""

    # --- Trae IDE 集成边界（4个）---
    register_boundary(BoundaryCondition(
        name="trae-ide-sandbox-limitation",
        scene=BoundaryScene.IDE_INTEGRATION,
        default_level=BoundaryLevel.FATAL,
        description="沙箱文件系统限制：写入操作返回权限错误",
    ))
    register_boundary(BoundaryCondition(
        name="trae-ide-mcp-unavailable",
        scene=BoundaryScene.IDE_INTEGRATION,
        default_level=BoundaryLevel.WARNING,
        description="MCP 工具可用性波动：工具调用返回 not found/timeout",
    ))
    register_boundary(BoundaryCondition(
        name="trae-ide-browser-login-dependency",
        scene=BoundaryScene.IDE_INTEGRATION,
        default_level=BoundaryLevel.WARNING,
        description="集成浏览器登录状态依赖：操作跳转至登录页",
    ))
    register_boundary(BoundaryCondition(
        name="trae-ide-terminal-session-isolation",
        scene=BoundaryScene.IDE_INTEGRATION,
        default_level=BoundaryLevel.INFO,
        description="IDE 内终端会话隔离：命令间状态不持久",
    ))

    # --- Trae 论坛操作边界（6个）---
    register_boundary(BoundaryCondition(
        name="trae-forum-login-expired",
        scene=BoundaryScene.FORUM_OPERATION,
        default_level=BoundaryLevel.WARNING,
        description="登录状态过期：Cookie 失效，页面跳转登录页",
    ))
    register_boundary(BoundaryCondition(
        name="trae-forum-dom-change",
        scene=BoundaryScene.FORUM_OPERATION,
        default_level=BoundaryLevel.WARNING,
        description="DOM 结构变化：CSS 选择器返回空",
    ))
    register_boundary(BoundaryCondition(
        name="trae-forum-rate-limit",
        scene=BoundaryScene.FORUM_OPERATION,
        default_level=BoundaryLevel.WARNING,
        description="频率限制触发：HTTP 429 或页面提示操作太频繁",
    ))
    register_boundary(BoundaryCondition(
        name="trae-forum-draft-accumulation",
        scene=BoundaryScene.FORUM_OPERATION,
        default_level=BoundaryLevel.INFO,
        description="草稿残留堆积：草稿列表超过阈值",
    ))
    register_boundary(BoundaryCondition(
        name="trae-forum-review-status-uncertain",
        scene=BoundaryScene.FORUM_OPERATION,
        default_level=BoundaryLevel.INFO,
        description="帖子审核状态不确定：状态为 pending/queued",
    ))
    register_boundary(BoundaryCondition(
        name="trae-forum-pagination-anomaly",
        scene=BoundaryScene.FORUM_OPERATION,
        default_level=BoundaryLevel.WARNING,
        description="回复分页导航异常：分页选择器失效",
    ))

    # --- Trae 外部工具链边界（5个）---
    register_boundary(BoundaryCondition(
        name="trae-toolchain-install-failed",
        scene=BoundaryScene.EXTERNAL_TOOLCHAIN,
        default_level=BoundaryLevel.FATAL,
        description="工具安装失败：command not found",
    ))
    register_boundary(BoundaryCondition(
        name="trae-toolchain-api-key-missing",
        scene=BoundaryScene.EXTERNAL_TOOLCHAIN,
        default_level=BoundaryLevel.FATAL,
        description="API Key 缺失：环境变量为空，API 返回 401/403",
    ))
    register_boundary(BoundaryCondition(
        name="trae-toolchain-version-incompatible",
        scene=BoundaryScene.EXTERNAL_TOOLCHAIN,
        default_level=BoundaryLevel.WARNING,
        description="工具版本不兼容：参数不支持或版本低于要求",
    ))
    register_boundary(BoundaryCondition(
        name="trae-toolchain-powershell-encoding",
        scene=BoundaryScene.EXTERNAL_TOOLCHAIN,
        default_level=BoundaryLevel.WARNING,
        description="跨平台编码差异：中文乱码或引号转义异常",
    ))
    register_boundary(BoundaryCondition(
        name="trae-toolchain-network-unreachable",
        scene=BoundaryScene.EXTERNAL_TOOLCHAIN,
        default_level=BoundaryLevel.WARNING,
        description="网络可达性不确定：连接超时或 DNS 解析失败",
    ))

    # --- Trae Work 边界（4个）---
    register_boundary(BoundaryCondition(
        name="trae-work-token-expired",
        scene=BoundaryScene.TRAE_WORK,
        default_level=BoundaryLevel.WARNING,
        description="授权 Token 过期：API 返回 401 或 token_expired",
    ))
    register_boundary(BoundaryCondition(
        name="trae-work-api-rate-limited",
        scene=BoundaryScene.TRAE_WORK,
        default_level=BoundaryLevel.WARNING,
        description="API 限流：HTTP 429 或 X-RateLimit-Remaining: 0",
    ))
    register_boundary(BoundaryCondition(
        name="trae-work-link-permission-denied",
        scene=BoundaryScene.TRAE_WORK,
        default_level=BoundaryLevel.INFO,
        description="消息链接权限限制：访问返回 403",
    ))
    register_boundary(BoundaryCondition(
        name="trae-work-app-scope-insufficient",
        scene=BoundaryScene.TRAE_WORK,
        default_level=BoundaryLevel.FATAL,
        description="飞书应用范围不足：app_scope_insufficient",
    ))


# 模块加载时自动初始化默认边界条件
_init_default_boundaries()


# ============================================================================
# 汇总报告（规范文档第198-211行：提示级处理流程的汇总步骤）
# ============================================================================

@dataclass
class BoundarySummary:
    """边界情况汇总报告（规范文档第206行）。"""

    total: int = 0
    fatal_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    entries: list[BoundaryDecision] = field(default_factory=list)

    def add(self, decision: BoundaryDecision) -> None:
        """添加一条边界决策到汇总。"""
        self.total += 1
        if decision.level == BoundaryLevel.FATAL:
            self.fatal_count += 1
        elif decision.level == BoundaryLevel.WARNING:
            self.warning_count += 1
        else:
            self.info_count += 1
        self.entries.append(decision)

    def report(self) -> str:
        """生成汇总报告文本。"""
        lines = [
            f"边界情况汇总: 共 {self.total} 条",
            f"  致命(fatal): {self.fatal_count}",
            f"  警告(warning): {self.warning_count}",
            f"  提示(info): {self.info_count}",
        ]
        for entry in self.entries:
            lines.append(
                f"  [{entry.level.value}] {entry.boundary_type}: {entry.rationale}"
            )
        return "\n".join(lines)
