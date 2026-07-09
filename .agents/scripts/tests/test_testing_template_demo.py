"""lib.testing 多智能体测试模板库功能演示与自验证测试。

本文件展示测试模板库的所有核心功能，并验证模板本身的正确性：
- generate_agents() 各种策略组合的agent生成
- @parametrize_agent_counts 参数化装饰器
- agent_scenarios() 场景矩阵生成
- BOUNDARY_ASSERTIONS 边界断言验证

本文件同时作为使用示例，可直接参考编写仲裁/调度类模块的边界测试。
"""

import pytest

from lib.testing import (
    generate_agents,
    agent_scenarios,
    parametrize_agent_counts,
    BOUNDARY_AGENT_COUNTS,
    BOUNDARY_ASSERTIONS,
    MultiAgentScenario,
)


class TestGenerateAgents:
    """验证 generate_agents() 函数在各种策略下的正确性。"""

    def test_uniform_priority_all_equal(self):
        """uniform策略：所有agent优先级相同"""
        for n in BOUNDARY_AGENT_COUNTS:
            agents = generate_agents(n, priority_strategy="uniform")
            assert len(agents) == n
            priorities = {info["priority"] for info in agents.values()}
            assert priorities == {2}, f"n={n}: uniform策略应统一优先级为2"

    def test_uniform_load_all_equal(self):
        """uniform策略：所有agent负载相同"""
        for n in BOUNDARY_AGENT_COUNTS:
            agents = generate_agents(n, load_strategy="uniform")
            loads = {info["load"] for info in agents.values()}
            assert loads == {50}, f"n={n}: uniform策略应统一负载为50"

    def test_ascending_priority_increases(self):
        """ascending策略：优先级从1递增"""
        for n in (2, 3, 5, 10):
            agents = generate_agents(n, priority_strategy="ascending")
            sorted_by_id = [agents[f"agent_{i}"]["priority"] for i in range(n)]
            assert sorted_by_id == list(range(1, n + 1)), f"n={n}: 优先级应从1到{n}递增"

    def test_ascending_load_increases(self):
        """ascending策略：负载递增，第一个最低"""
        for n in (2, 3, 5, 10):
            agents = generate_agents(n, load_strategy="ascending")
            loads = [agents[f"agent_{i}"]["load"] for i in range(n)]
            assert loads[0] < loads[-1], f"n={n}: 第一个agent负载应最低"
            assert loads == sorted(loads), f"n={n}: 负载应严格递增"

    def test_descending_priority_decreases(self):
        """descending策略：最后一个agent优先级最高"""
        for n in (2, 3, 5, 10):
            agents = generate_agents(n, priority_strategy="descending")
            first_prio = agents["agent_0"]["priority"]
            last_prio = agents[f"agent_{n-1}"]["priority"]
            assert last_prio == 1, f"n={n}: 最后一个agent优先级应为1（最高）"
            assert first_prio == n, f"n={n}: 第一个agent优先级应为{n}（最低）"

    def test_extremes_load_first_highest_last_lowest(self):
        """extremes策略：第一个负载99最高，最后一个1最低"""
        for n in (2, 3, 5, 10):
            agents = generate_agents(n, load_strategy="extremes")
            assert agents["agent_0"]["load"] == 99, f"n={n}: 第一个agent负载应为99"
            assert agents[f"agent_{n-1}"]["load"] == 1, f"n={n}: 最后一个agent负载应为1"

    def test_custom_capabilities(self):
        """支持自定义能力列表"""
        agents = generate_agents(3, capabilities=["design", "modeling", "coding"])
        for info in agents.values():
            assert "design" in info["capabilities"]
            assert "modeling" in info["capabilities"]
            assert "coding" in info["capabilities"]

    def test_custom_id_prefix(self):
        """支持自定义ID前缀"""
        agents = generate_agents(3, id_prefix="dev")
        assert "dev_0" in agents
        assert "dev_1" in agents
        assert "dev_2" in agents

    def test_custom_role(self):
        """支持自定义角色名"""
        agents = generate_agents(2, role="architect")
        for info in agents.values():
            assert info["role"] == "architect"

    def test_single_agent_id(self):
        """n=1时ID使用前缀本身，不添加_0后缀"""
        agents = generate_agents(1)
        assert "agent" in agents
        assert len(agents) == 1
        assert agents["agent"]["id"] == "agent"

    def test_all_agents_have_required_fields(self):
        """所有生成的agent必须包含标准字段"""
        required_fields = {"id", "role", "priority", "load", "capabilities"}
        for n in BOUNDARY_AGENT_COUNTS:
            agents = generate_agents(n)
            for aid, info in agents.items():
                assert required_fields.issubset(info.keys()), f"n={n}, {aid}: 缺少必要字段"
                assert info["id"] == aid, f"n={n}, {aid}: id字段与key不匹配"


class TestParametrizeDecorator:
    """验证 @parametrize_agent_counts 装饰器正确参数化。"""

    @parametrize_agent_counts
    def test_receives_n_agents_parameter(self, n_agents):
        """参数化后测试函数应收到n_agents参数"""
        assert isinstance(n_agents, int)
        assert n_agents in BOUNDARY_AGENT_COUNTS

    @parametrize_agent_counts(skip_single=True)
    def test_skip_single_skips_n_equals_1(self, n_agents):
        """skip_single=True时n>=2"""
        assert n_agents >= 2
        assert n_agents in BOUNDARY_AGENT_COUNTS

    @parametrize_agent_counts(counts=(2, 5))
    def test_custom_counts(self, n_agents):
        """支持自定义counts参数"""
        assert n_agents in (2, 5)


class TestAgentScenarios:
    """验证 agent_scenarios() 场景矩阵生成。"""

    def test_default_scenarios_count(self):
        """默认配置应生成 5数量 × 3优先级策略 × 4负载策略 = 60个场景"""
        scenarios = agent_scenarios()
        assert len(scenarios) == 5 * 3 * 4
        for sc in scenarios:
            assert isinstance(sc, MultiAgentScenario)

    def test_scenario_metadata_present(self):
        """每个场景应有正确的元数据"""
        scenarios = agent_scenarios(counts=(2,), priority_strategies=("uniform",), load_strategies=("ascending",))
        assert len(scenarios) == 1
        sc = scenarios[0]
        assert sc.agent_count == 2
        assert sc.metadata["priority_strategy"] == "uniform"
        assert sc.metadata["load_strategy"] == "ascending"

    def test_scenarios_have_valid_agents(self):
        """所有场景的agents字典有效"""
        scenarios = agent_scenarios(counts=(1, 3, 10))
        for sc in scenarios:
            assert len(sc.agents) == sc.agent_count
            for aid, info in sc.agents.items():
                assert "priority" in info
                assert "load" in info

    def test_scenario_name_format(self):
        """场景名称格式规范：{prefix}_n{N}_prio-{strategy}_load-{strategy}"""
        scenarios = agent_scenarios(name_prefix="demo", counts=(2,))
        for sc in scenarios:
            assert sc.name.startswith("demo_n2_prio-")
            assert "_load-" in sc.name


class TestBoundaryAssertions:
    """验证 BOUNDARY_ASSERTIONS 文档常量完整性。"""

    def test_assertions_dictionary_not_empty(self):
        """断言参考字典应包含核心边界检查项"""
        required_keys = {"no_starvation", "deterministic", "timeout_protection", "idempotent_rejection", "defensive_copy"}
        assert required_keys.issubset(BOUNDARY_ASSERTIONS.keys())
        for key, desc in BOUNDARY_ASSERTIONS.items():
            assert isinstance(desc, str)
            assert len(desc) > 10, f"{key}: 断言描述不应为空"


class TestTemplateEndToEnd:
    """端到端演示：使用模板编写一个完整的边界测试示例。

    这是一个参考示例，展示如何用lib.testing为一个假设的调度器模块编写测试。
    """

    @pytest.fixture
    def mock_scheduler(self):
        """模拟一个简单的优先级调度器（示例被测对象）"""
        class MockScheduler:
            def schedule(self, agents: dict, task_load: int = 50) -> str:
                if not agents:
                    raise ValueError("no agents")
                candidates = list(agents.keys())
                return min(candidates, key=lambda aid: (agents[aid].get("priority", 99), agents[aid].get("load", 50)))
        return MockScheduler()

    @parametrize_agent_counts
    def test_scheduler_selects_highest_priority(self, mock_scheduler, n_agents):
        """示例：N个agent时，调度器总是选择优先级最高的"""
        agents = generate_agents(n_agents, priority_strategy="ascending")
        winner = mock_scheduler.schedule(agents)
        priorities = {aid: info["priority"] for aid, info in agents.items()}
        min_prio = min(priorities.values())
        assert priorities[winner] == min_prio

    @parametrize_agent_counts(skip_single=True)
    def test_scheduler_no_starvation_extremes(self, mock_scheduler, n_agents):
        """示例：极端负载分布下，最低负载agent不被饿死"""
        agents = generate_agents(n_agents, priority_strategy="uniform", load_strategy="extremes")
        winner = mock_scheduler.schedule(agents)
        loads = {aid: info["load"] for aid, info in agents.items()}
        assert loads[winner] == min(loads.values()), "极端负载下最低负载agent应被选中"

    def test_scenario_matrix_for_exploratory_testing(self, mock_scheduler):
        """示例：使用agent_scenarios进行探索性测试（所有策略组合）"""
        scenarios = agent_scenarios(
            name_prefix="scheduler_demo",
            counts=(2, 3, 5),
            priority_strategies=("uniform", "ascending"),
            load_strategies=("ascending", "extremes"),
        )
        for sc in scenarios:
            winner = mock_scheduler.schedule(sc.agents)
            assert winner in sc.agents, f"场景{sc.name}: winner必须是候选agent之一"

            priorities = {aid: info["priority"] for aid, info in sc.agents.items()}
            loads = {aid: info["load"] for aid, info in sc.agents.items()}
            min_prio = min(priorities.values())
            prio_candidates = [aid for aid, p in priorities.items() if p == min_prio]
            assert winner in prio_candidates, f"场景{sc.name}: 必须从最高优先级候选中选择"

            if len(prio_candidates) > 1:
                prio_loads = {aid: loads[aid] for aid in prio_candidates}
                assert loads[winner] == min(prio_loads.values()), f"场景{sc.name}: 优先级相同时选最低负载"


class TestTemplateUsableForConflictResolver:
    """验证模板可以直接用于ConflictResolver测试（集成验证）。"""

    @pytest.fixture
    def resolver(self):
        from lib.collaboration.conflict_resolution import ConflictResolver
        return ConflictResolver()

    @parametrize_agent_counts
    def test_template_integration_load_balancing(self, resolver, n_agents):
        """使用模板验证ConflictResolver在N个agent下负载均衡正确性"""
        from lib.collaboration.conflict_resolution import ConflictType, ConflictReport
        agents = generate_agents(n_agents, load_strategy="ascending", capabilities=["coding"])
        ids = list(agents.keys())
        if n_agents == 1:
            reporter = opponent = ids[0]
        else:
            reporter, opponent = ids[0], ids[-1]

        report = ConflictReport(
            reporter_id=reporter,
            opponent_id=opponent,
            conflict_type=ConflictType.RESPONSIBILITY,
            description=f"模板集成测试 n={n_agents}",
            task_id=f"TASK-TPL-{n_agents}",
            required_capability="coding",
        )
        result = resolver.resolve(report, agents=agents)
        loads = {aid: info["load"] for aid, info in agents.items()}
        assert loads[result.winner] == min(loads.values())
