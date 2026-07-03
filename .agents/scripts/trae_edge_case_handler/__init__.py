"""trae_edge_case_handler — Trae 边界情况处理决策模块。

从 .agents/teams/trae-edge-case-handler.md 规范文档提取的可执行决策逻辑，
覆盖四大边界场景的检测、三级分级、异常处理流程与特殊场景适配策略。

核心能力：
  - 多信号组合检测（遵循 multi-signal-detection 模式）
  - 三级分级判断（致命/警告/提示）
  - 标准化异常处理流程（检测→分级→处理→决策）
  - 4个预定义适配策略（沙箱/PowerShell/登录过期/DOM变化）

拆分结构（遵循单一职责原则）：
- models: 数据模型（枚举和dataclass定义）
- detection: 多信号检测和三级分级判断
- handlers: 异常处理流程（致命/警告/提示三级处理）
- adapters: 4个特殊场景适配策略
- registry: 边界条件注册表和检测入口
- defaults: 19个默认边界条件初始化
- summary: 边界情况汇总报告

向后兼容：所有公共API均可直接从 trae_edge_case_handler 导入，无需修改现有代码。
"""

from __future__ import annotations

from .adapters import (
    adapt_dom_structure_change,
    adapt_forum_login_expired,
    adapt_powershell_encoding,
    adapt_sandbox_limitation,
)
from .defaults import _init_default_boundaries
from .detection import check_multi_signal, classify_boundary_level
from .handlers import (
    handle_boundary,
    handle_fatal_boundary,
    handle_info_boundary,
    handle_warning_boundary,
)
from .models import (
    BoundaryAction,
    BoundaryCondition,
    BoundaryContext,
    BoundaryDecision,
    BoundaryLevel,
    BoundaryScene,
    Signal,
)
from .registry import _BOUNDARY_REGISTRY, check_boundary, get_boundary, register_boundary
from .summary import BoundarySummary

_init_default_boundaries()

__all__ = [
    "BoundaryLevel",
    "BoundaryScene",
    "BoundaryAction",
    "Signal",
    "BoundaryCondition",
    "BoundaryContext",
    "BoundaryDecision",
    "check_multi_signal",
    "classify_boundary_level",
    "handle_fatal_boundary",
    "handle_warning_boundary",
    "handle_info_boundary",
    "handle_boundary",
    "adapt_sandbox_limitation",
    "adapt_powershell_encoding",
    "adapt_forum_login_expired",
    "adapt_dom_structure_change",
    "register_boundary",
    "get_boundary",
    "check_boundary",
    "_BOUNDARY_REGISTRY",
    "BoundarySummary",
]
