"""Router 对抗测试用例：针对多模型路由规划中的三种风险。

风险1：策略冲突（多策略同时命中时优先级是否正确）
风险2：路由延迟（直通模式是否有效跳过路由判定）
风险3：阈值主观（复杂度阈值 + 边界越权校验）

参考：docs/multi-model-routing-plan.md §3 对抗审查
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from workspace import Workspace, WorkspaceRegistry
from boundary import BoundaryChecker, BoundaryViolation
from router import (
    ModelRouter,
    DataBoundaryStrategy,
    ComplexityStrategy,
    CostStrategy,
    FallbackStrategy,
    build_default_router,
)


def build_fixture():
    """构建测试工作区与边界、路由器。"""
    registry = WorkspaceRegistry()
    ws = Workspace("finance", "财务工作区", model="local-model", private=True)
    registry.register(ws)

    boundary = BoundaryChecker()
    boundary.set_allowed_models("finance", ["local-model", "strong-model", "cheap-model"])

    router = build_default_router(registry, boundary)
    return registry, boundary, router, ws


class TestStrategyConflict(unittest.TestCase):
    """风险1：策略冲突自动化验证。

    攻击场景：敏感数据任务同时满足复杂度/成本/数据边界策略时，
    数据边界策略（优先级100）必须恒优先。
    """

    def setUp(self) -> None:
        self.registry, self.boundary, self.router, self.ws = build_fixture()

    def test_sensitive_task_wins_over_complexity(self):
        # 敏感任务 + 高复杂度：数据边界策略（优先级100）应优先于复杂度策略（50）
        model = self.router.route("finance", "处理一份客户财务票据", complexity=0.9)
        self.assertEqual(model, "local-model")

    def test_sensitive_task_wins_over_cost(self):
        # 敏感任务 + 简单查询类型：数据边界策略应优先于成本策略
        model = self.router.route("finance", "查看财务票据", task_type="query")
        self.assertEqual(model, "local-model")

    def test_strategy_priority_ordering(self):
        # 验证策略按优先级降序存储
        priorities = [s.priority for s in self.router._strategies]
        self.assertEqual(priorities, sorted(priorities, reverse=True))
        self.assertGreater(priorities[0], priorities[-1])

    def test_high_complexity_nonsensitive_uses_strong(self):
        # 非敏感 + 高复杂度 → 复杂度策略
        model = self.router.route("finance", "分析一段复杂代码逻辑", complexity=0.9)
        self.assertEqual(model, "strong-model")

    def test_simple_query_nonsensitive_uses_cheap(self):
        # 非敏感 + 简单查询 → 成本策略
        model = self.router.route("finance", "查询一下当前时间", task_type="query")
        self.assertEqual(model, "cheap-model")


class TestDirectMode(unittest.TestCase):
    """风险2：路由延迟对抗验证。

    攻击场景：路由判定本身是额外开销，简单任务不值得。
    加固：直通模式跳过路由判定，直接使用工作区默认模型。
    """

    def setUp(self) -> None:
        self.registry, self.boundary, self.router, self.ws = build_fixture()

    def test_direct_mode_uses_default_model(self):
        router = ModelRouter(self.registry, self.boundary, direct_mode=True)
        # 即使任务满足所有策略，直通模式也使用默认模型
        model = router.route("finance", "处理一份客户财务票据", complexity=0.9)
        self.assertEqual(model, "local-model")

    def test_direct_mode_skips_strategy_evaluation(self):
        router = ModelRouter(self.registry, self.boundary, direct_mode=True)
        router.route("finance", "普通任务")
        # 直通模式无策略命中，轨迹显示 direct
        self.assertEqual(router.get_trace()[0]["strategy"], "direct")

    def test_normal_mode_evaluates_strategies(self):
        # 非直通模式才会评估策略
        model = self.router.route("finance", "分析复杂代码", complexity=0.9)
        self.assertEqual(model, "strong-model")
        self.assertEqual(self.router.get_trace()[0]["strategy"], "ComplexityStrategy")


class TestBoundaryAndThreshold(unittest.TestCase):
    """风险3：阈值主观 + 边界越权对抗验证。

    攻击场景1：复杂度阈值客观性——用可观测信号（复杂度参数）作为代理。
    攻击场景2：路由结果必须通过模型白名单校验，越权应被拦截。
    """

    def setUp(self) -> None:
        self.registry, self.boundary, self.router, self.ws = build_fixture()

    def test_routing_outside_whitelist_raises(self):
        # 路由结果的模型不在白名单 → 应抛 BoundaryViolation
        # 白名单仅含 local/strong/cheap，构造一个命中 whitelist 外模型的场景
        restricted = BoundaryChecker()
        restricted.set_allowed_models("finance", ["local-model"])  # 仅允许本地

        router = ModelRouter(self.registry, restricted)
        router.add_strategy(ComplexityStrategy(threshold=0.5, strong_model="strong-model"))
        router.add_strategy(FallbackStrategy())

        with self.assertRaises(BoundaryViolation):
            router.route("finance", "复杂任务", complexity=0.9)

    def test_route_within_whitelist_ok(self):
        # 路由结果在白名单内 → 正常返回
        model = self.router.route("finance", "分析代码", complexity=0.9)
        self.assertIn(model, ["local-model", "strong-model", "cheap-model"])

    def test_complexity_threshold_boundary(self):
        # 阈值边界：0.7 为阈值，0.7 不触发，0.71 触发
        router = ModelRouter(self.registry, self.boundary)
        router.add_strategy(ComplexityStrategy(threshold=0.7, strong_model="strong-model"))
        router.add_strategy(FallbackStrategy())

        below = router.route("finance", "任务", complexity=0.7)
        self.assertEqual(below, "local-model")  # 未过阈值 → 兜底默认

        above = router.route("finance", "任务", complexity=0.71)
        self.assertEqual(above, "strong-model")  # 过阈值 → 强模型

    def test_route_trace_recorded(self):
        self.router.route("finance", "分析代码", complexity=0.9)
        trace = self.router.get_trace()
        self.assertEqual(len(trace), 1)
        self.assertEqual(trace[0]["workspace_id"], "finance")
        self.assertIn("model", trace[0])


if __name__ == "__main__":
    unittest.main()