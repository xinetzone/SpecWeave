"""trae_edge_case_handler 数据模型模块。

枚举类型和dataclass定义：
- BoundaryLevel: 三级分级（fatal/warning/info）
- BoundaryScene: 四大边界场景
- BoundaryAction: 处理决策动作
- Signal: 检测信号
- BoundaryCondition: 边界条件定义
- BoundaryContext: 边界检测上下文
- BoundaryDecision: 边界处理决策
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


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
