"""Router 模块：多模型路由（P0 骨架）。

对应 multi-model-routing-plan：
- 感知层：判断任务类型与复杂度
- 策略层：基于约束（成本/速度/数据边界）选择模型
- 执行层：调用目标模型，记录轨迹
- 边界层：复用 BoundaryChecker 的模型边界检查，确保不越权

P0 阶段实现基础骨架：ModelRouter 类 + 策略接口 + 兜底默认模型。
P1 阶段将补充四种具体策略（数据边界/复杂度/成本/兜底）。
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

from workspace import WorkspaceRegistry
from boundary import BoundaryChecker, BoundaryViolation

logger = logging.getLogger(__name__)


class RouteStrategy:
    """路由策略基类（接口）。

    子类实现 should_route 与 route 方法，决定是否命中该策略及目标模型。
    """

    priority: int = 0  # 优先级，数值越大越优先

    def should_route(self, task: str, task_type: str = "", complexity: float = 0.0) -> bool:
        """判断当前任务是否命中该策略。"""
        raise NotImplementedError

    def route(self, workspace_model: str) -> str:
        """返回该策略命中的目标模型。"""
        raise NotImplementedError


class DataBoundaryStrategy(RouteStrategy):
    """数据边界策略：任务涉及敏感数据时强制本地模型（硬约束，最高优先级）。"""

    priority = 100

    def __init__(self, sensitive_keywords: Optional[List[str]] = None) -> None:
        self._keywords = sensitive_keywords or ["敏感", "票据", "财务", "机密"]

    def should_route(self, task: str, task_type: str = "", complexity: float = 0.0) -> bool:
        return any(k in task for k in self._keywords)

    def route(self, workspace_model: str) -> str:
        return "local-model"


class ComplexityStrategy(RouteStrategy):
    """复杂度策略：任务复杂度超过阈值时路由到强模型。"""

    priority = 50

    def __init__(self, threshold: float = 0.7, strong_model: str = "strong-model") -> None:
        self._threshold = threshold
        self._strong_model = strong_model

    def should_route(self, task: str, task_type: str = "", complexity: float = 0.0) -> bool:
        return complexity > self._threshold

    def route(self, workspace_model: str) -> str:
        return self._strong_model


class CostStrategy(RouteStrategy):
    """成本策略：简单查询任务路由到便宜模型。"""

    priority = 30

    def __init__(self, simple_types: Optional[List[str]] = None, cheap_model: str = "cheap-model") -> None:
        self._simple_types = simple_types or ["query", "read", "lookup"]
        self._cheap_model = cheap_model

    def should_route(self, task: str, task_type: str = "", complexity: float = 0.0) -> bool:
        return task_type in self._simple_types

    def route(self, workspace_model: str) -> str:
        return self._cheap_model


class FallbackStrategy(RouteStrategy):
    """兜底策略：无匹配时使用工作区默认模型（最低优先级）。"""

    priority = 0

    def should_route(self, task: str, task_type: str = "", complexity: float = 0.0) -> bool:
        return True

    def route(self, workspace_model: str) -> str:
        return workspace_model


class ModelRouter:
    """多模型路由器。

    职责：
    1. 感知层：接收任务与约束信息
    2. 策略层：按优先级应用策略，选择目标模型
    3. 边界层：校验路由结果是否在工作区模型白名单内
    4. 执行层：返回目标模型名，记录路由轨迹

    Args:
        registry: 工作区注册中心（用于获取工作区默认模型）
        boundary: 边界检查器（用于模型白名单校验）
        direct_mode: 直通模式（True 时跳过路由判定，直接使用工作区默认模型）
    """

    def __init__(
        self,
        registry: WorkspaceRegistry,
        boundary: BoundaryChecker,
        direct_mode: bool = False,
    ) -> None:
        self.registry = registry
        self.boundary = boundary
        self.direct_mode = direct_mode
        self._strategies: List[RouteStrategy] = []
        self._trace: List[Dict[str, Any]] = []

    def add_strategy(self, strategy: RouteStrategy) -> None:
        """注册一个路由策略，按优先级排序存储。"""
        self._strategies.append(strategy)
        self._strategies.sort(key=lambda s: s.priority, reverse=True)

    def route(
        self,
        workspace_id: str,
        task: str,
        task_type: str = "",
        complexity: float = 0.0,
    ) -> str:
        """路由：给定任务，返回匹配的模型。

        Args:
            workspace_id: 目标工作区 ID
            task: 任务描述
            task_type: 任务类型（用于成本策略）
            complexity: 任务复杂度（0.0 ~ 1.0，用于复杂度策略）

        Returns:
            匹配的模型名。

        Raises:
            BoundaryViolation: 路由结果不在工作区模型白名单内
        """
        ws = self.registry.get(workspace_id)
        default_model = ws.model

        # 直通模式：跳过路由判定，直接使用工作区默认模型
        if self.direct_mode:
            logger.info("[Router] 直通模式，使用默认模型 model=%s", default_model)
            self._record(workspace_id, "direct", default_model, task)
            return default_model

        # 感知层：逐策略判定（按优先级降序）
        for strategy in self._strategies:
            if strategy.should_route(task, task_type, complexity):
                chosen = strategy.route(default_model)
                logger.info(
                    "[Router] 策略命中 strategy=%s 目标模型=%s 默认模型=%s",
                    strategy.__class__.__name__, chosen, default_model,
                )
                self._validate_boundary(workspace_id, chosen, task)
                self._record(workspace_id, strategy.__class__.__name__, chosen, task)
                return chosen

        # 兜底（无显式策略注册时使用默认模型）
        logger.info("[Router] 无策略命中，使用默认模型 model=%s", default_model)
        self._record(workspace_id, "fallback", default_model, task)
        return default_model

    def _validate_boundary(self, workspace_id: str, model: str, task: str) -> None:
        """边界层：校验目标模型是否在工作区白名单内。"""
        ws = self.registry.get(workspace_id)
        # 临时校验模型白名单（不修改 workspace 的 model 字段）
        allowed = self.boundary._allowed_models.get(workspace_id)
        if allowed is not None and model not in allowed:
            logger.warning(
                "[Router] 路由越界：workspace=%s model=%s 不在白名单 %s",
                workspace_id, model, allowed,
            )
            raise BoundaryViolation(
                f"模型边界：路由目标模型 {model!r} 不在工作区 {ws.name} 白名单 {allowed} 内"
            )

    def _record(self, workspace_id: str, strategy: str, model: str, task: str) -> None:
        """记录路由轨迹。"""
        self._trace.append({
            "workspace_id": workspace_id,
            "strategy": strategy,
            "model": model,
            "task": task,
        })

    def get_trace(self) -> List[Dict[str, Any]]:
        """返回路由轨迹记录。"""
        return list(self._trace)


def build_default_router(registry: WorkspaceRegistry, boundary: BoundaryChecker) -> ModelRouter:
    """构建带默认策略的 P0 路由器。"""
    router = ModelRouter(registry, boundary)
    router.add_strategy(DataBoundaryStrategy())
    router.add_strategy(ComplexityStrategy())
    router.add_strategy(CostStrategy())
    router.add_strategy(FallbackStrategy())
    return router