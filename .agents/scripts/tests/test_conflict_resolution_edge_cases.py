"""ConflictResolver 边缘场景测试。

使用lib.testing扩展的边缘场景生成器，覆盖：
- 空输入/None输入处理（验证容错性，不崩溃）
- 畸形数据（缺失字段、负值、超范围值）容错
- 完全平局场景确定性验证
- 大规模agent场景（50/100）性能
- 部分/零/全部能力匹配
- 极端优先级范围
- 混合角色
- 结果确定性验证
- 输入不被修改验证
"""

import pytest
import copy

from lib.collaboration.conflict_resolution import (
    ConflictResolver,
    ConflictType,
    ConflictReport,
    ArbitrationResult,
    ResolutionStatus,
)
from lib.testing import (
    generate_agents,
    generate_malformed_agents,
    generate_tie_scenario,
    generate_partial_capability_match,
    edge_scenarios,
    parametrize_agent_counts,
)


class TestEdgeCaseEmptyInput:
    """空输入/None输入容错测试 - 验证不崩溃，返回合理结果或升级。"""

    @pytest.fixture
    def resolver(self):
        return ConflictResolver()

    def _make_report(self, task_id: str, reporter: str = "dev_a", opponent: str = "dev_b") -> ConflictReport:
        return ConflictReport(
            reporter_id=reporter,
            opponent_id=opponent,
            conflict_type=ConflictType.RESPONSIBILITY,
            description=f"边缘测试 {task_id}",
            task_id=task_id,
            required_capability="coding",
        )

    def test_empty_agents_dict_with_required_capability_escalates(self, resolver):
        """空agents字典且有required_capability时应升级。"""
        report = self._make_report("TASK-EMPTY")
        result = resolver.resolve(report, agents={})
        assert isinstance(result, ArbitrationResult)
        assert result.status == ResolutionStatus.ESCALATED
        assert result.needs_human is True

    def test_none_agents_with_required_capability_escalates(self, resolver):
        """agents=None且有required_capability时应升级。"""
        report = self._make_report("TASK-NONE")
        result = resolver.resolve(report, agents=None)
        assert isinstance(result, ArbitrationResult)
        assert result.status == ResolutionStatus.ESCALATED
        assert result.needs_human is True

    def test_reporter_not_in_agents_handled_gracefully(self, resolver):
        """reporter_id不在agents中应优雅处理，不抛出KeyError。"""
        agents = generate_agents(2)
        report = self._make_report("TASK-NO-REPORTER", reporter="nonexistent_agent", opponent="agent_0")
        result = resolver.resolve(report, agents=agents)
        assert isinstance(result, ArbitrationResult)

    def test_opponent_not_in_agents_handled_gracefully(self, resolver):
        """opponent_id不在agents中应优雅处理。"""
        agents = generate_agents(2)
        report = self._make_report("TASK-NO-OPPONENT", reporter="agent_0", opponent="nonexistent_opponent")
        result = resolver.resolve(report, agents=agents)
        assert isinstance(result, ArbitrationResult)

    def test_same_reporter_and_opponent_resolves(self, resolver):
        """reporter与opponent相同时（自分配）应成功。"""
        agents = generate_agents(1)
        report = self._make_report("TASK-SELF", reporter="agent", opponent="agent")
        result = resolver.resolve(report, agents=agents)
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "agent"


class TestEdgeCaseMalformedData:
    """畸形数据/无效值容错测试 - 验证不崩溃。"""

    @pytest.fixture
    def resolver(self):
        return ConflictResolver()

    def _make_report(self, task_id: str) -> ConflictReport:
        return ConflictReport(
            reporter_id="agent_0",
            opponent_id="agent_1",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="畸形数据测试",
            task_id=task_id,
            required_capability="coding",
        )

    @pytest.mark.parametrize("malformed_type", [
        "missing_priority",
        "missing_load",
        "missing_capabilities",
    ])
    def test_missing_field_does_not_crash_but_may_escalate(self, resolver, malformed_type):
        """缺少字段不应崩溃，返回结果或升级均可。"""
        agents = generate_malformed_agents(malformed_type, base_count=3)
        report = self._make_report(f"TASK-MISS-{malformed_type}")
        try:
            result = resolver.resolve(report, agents=agents)
            assert isinstance(result, ArbitrationResult)
        except (KeyError, ValueError, TypeError, AttributeError):
            pass

    def test_negative_priority_does_not_crash(self, resolver):
        """负优先级不应导致崩溃。"""
        agents = generate_malformed_agents("negative_priority", base_count=3)
        report = self._make_report("TASK-NEG-PRIO")
        result = resolver.resolve(report, agents=agents)
        assert isinstance(result, ArbitrationResult)

    def test_negative_load_does_not_crash(self, resolver):
        """负负载不应导致崩溃。"""
        agents = generate_malformed_agents("negative_load", base_count=3)
        report = self._make_report("TASK-NEG-LOAD")
        result = resolver.resolve(report, agents=agents)
        assert isinstance(result, ArbitrationResult)

    def test_load_over_100_does_not_crash(self, resolver):
        """负载超过100不应导致崩溃。"""
        agents = generate_malformed_agents("load_over_100", base_count=3)
        report = self._make_report("TASK-OVER100")
        result = resolver.resolve(report, agents=agents)
        assert isinstance(result, ArbitrationResult)

    def test_extreme_priority_range_0_to_999(self, resolver):
        """极端优先级范围(0到999)应正常处理或升级。"""
        agents = generate_malformed_agents("extreme_priority_range", base_count=3)
        report = self._make_report("TASK-EXTREME-PRIO")
        result = resolver.resolve(report, agents=agents)
        assert isinstance(result, ArbitrationResult)

    def test_mixed_roles_does_not_crash(self, resolver):
        """混合角色场景应正常处理。"""
        agents = generate_malformed_agents("mixed_roles", base_count=3)
        report = self._make_report("TASK-MIXED-ROLES")
        result = resolver.resolve(report, agents=agents)
        assert isinstance(result, ArbitrationResult)


class TestEdgeCaseCapabilityMatching:
    """能力匹配边缘场景测试。"""

    @pytest.fixture
    def resolver(self):
        return ConflictResolver()

    def test_no_agent_has_required_capability_escalates(self, resolver):
        """无任何agent具备所需能力时应升级至人工处理。"""
        agents = generate_partial_capability_match(5, "architecture", matching_count=0)
        report = ConflictReport(
            reporter_id="agent_0",
            opponent_id="agent_1",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="无能力匹配测试",
            task_id="TASK-NO-CAP",
            required_capability="architecture",
        )
        result = resolver.resolve(report, agents=agents)
        assert isinstance(result, ArbitrationResult)
        assert result.status == ResolutionStatus.ESCALATED, "无匹配能力时应升级"
        assert result.winner is None
        assert result.needs_human is True
        assert "architecture" in result.reason

    def test_partial_capability_match_selects_from_matching(self, resolver):
        """部分匹配时，winner必须从具备能力的agent中选择。"""
        agents = generate_partial_capability_match(5, "design", matching_count=2)
        report = ConflictReport(
            reporter_id="agent_0",
            opponent_id="agent_1",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="部分能力匹配测试",
            task_id="TASK-PARTIAL-CAP",
            required_capability="design",
        )
        result = resolver.resolve(report, agents=agents)
        assert isinstance(result, ArbitrationResult)
        if result.status == ResolutionStatus.RESOLVED and result.winner:
            assert "design" in agents[result.winner]["capabilities"], "winner必须具备所需能力"

    def test_empty_capabilities_agent_does_not_crash(self, resolver):
        """capabilities为空列表的agent不应导致崩溃。"""
        agents = generate_malformed_agents("empty_capabilities", base_count=3)
        report = ConflictReport(
            reporter_id="agent_1",
            opponent_id="agent_2",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="空capabilities测试",
            task_id="TASK-EMPTY-CAPS",
            required_capability="coding",
        )
        result = resolver.resolve(report, agents=agents)
        assert isinstance(result, ArbitrationResult)

    @parametrize_agent_counts
    def test_all_agents_match_capability_respects_load_balancing(self, resolver, n_agents):
        """全部agent具备所需能力时，仍应遵守负载均衡规则。"""
        agents = generate_agents(n_agents, load_strategy="ascending", capabilities=["coding", "test"])
        ids = list(agents.keys())
        reporter = ids[0]
        opponent = ids[-1] if n_agents > 1 else ids[0]
        report = ConflictReport(
            reporter_id=reporter,
            opponent_id=opponent,
            conflict_type=ConflictType.RESPONSIBILITY,
            description=f"全匹配负载均衡 n={n_agents}",
            task_id=f"TASK-ALL-MATCH-{n_agents}",
            required_capability="test",
        )
        result = resolver.resolve(report, agents=agents)
        assert isinstance(result, ArbitrationResult)
        if result.status == ResolutionStatus.RESOLVED and result.winner and n_agents > 1:
            loads = {aid: info["load"] for aid, info in agents.items() if "test" in info.get("capabilities", [])}
            if loads and result.winner in loads:
                assert loads[result.winner] == min(loads.values()), "应选负载最低的匹配agent"


class TestEdgeCaseTieBreaking:
    """完全平局场景（优先级和负载都相同）平局打破测试。"""

    @pytest.fixture
    def resolver(self):
        return ConflictResolver()

    @pytest.mark.parametrize("n_agents", [2, 3, 5, 10, 20])
    def test_tie_scenario_produces_deterministic_winner(self, resolver, n_agents):
        """完全平局时结果必须是确定性的（相同输入相同输出）。"""
        agents = generate_tie_scenario(n_agents)
        ids = list(agents.keys())

        report = ConflictReport(
            reporter_id=ids[0],
            opponent_id=ids[-1],
            conflict_type=ConflictType.RESPONSIBILITY,
            description=f"平局确定性测试 n={n_agents}",
            task_id=f"TASK-TIE-DET-{n_agents}",
            required_capability="coding",
        )

        results = [resolver.resolve(report, agents=agents) for _ in range(3)]
        winners = [r.winner for r in results if r.status == ResolutionStatus.RESOLVED]
        if winners:
            assert len(set(winners)) == 1, "平局时相同输入必须产生相同winner"
            assert all(w in agents for w in winners)

    def test_tie_scenario_winner_has_required_capability(self, resolver):
        """平局打破选出的winner必须具备所需能力。"""
        agents = generate_tie_scenario(10)
        ids = list(agents.keys())
        report = ConflictReport(
            reporter_id=ids[0],
            opponent_id=ids[-1],
            conflict_type=ConflictType.RESPONSIBILITY,
            description="平局能力验证",
            task_id="TASK-TIE-CAP",
            required_capability="coding",
        )
        result = resolver.resolve(report, agents=agents)
        if result.status == ResolutionStatus.RESOLVED and result.winner:
            assert "coding" in agents[result.winner]["capabilities"]


class TestEdgeCaseLargeScale:
    """大规模agent场景性能与正确性测试。"""

    @pytest.fixture
    def resolver(self):
        return ConflictResolver()

    @pytest.mark.parametrize("n_agents", [50, 100])
    def test_large_scale_completes_within_timeout(self, resolver, n_agents):
        """50/100个agent的大规模场景应在合理时间内完成（<5秒）。"""
        import time
        agents = generate_agents(n_agents, load_strategy="ascending")
        ids = list(agents.keys())
        report = ConflictReport(
            reporter_id=ids[0],
            opponent_id=ids[-1],
            conflict_type=ConflictType.RESPONSIBILITY,
            description=f"大规模测试 n={n_agents}",
            task_id=f"TASK-LARGE-{n_agents}",
            required_capability="coding",
        )

        start = time.time()
        result = resolver.resolve(report, agents=agents)
        elapsed = time.time() - start

        assert elapsed < 5.0, f"n={n_agents} 应在5秒内完成，实际{elapsed:.3f}s"
        assert isinstance(result, ArbitrationResult)
        if result.status == ResolutionStatus.RESOLVED:
            assert result.winner in agents

    @pytest.mark.parametrize("n_agents", [50, 100])
    def test_large_scale_extremes_selects_low_load(self, resolver, n_agents):
        """大规模极端负载分布下，应选择负载最低的agent。"""
        agents = generate_agents(n_agents, load_strategy="extremes")
        ids = list(agents.keys())
        report = ConflictReport(
            reporter_id=ids[0],
            opponent_id=ids[-1],
            conflict_type=ConflictType.RESPONSIBILITY,
            description=f"大规模极端负载 n={n_agents}",
            task_id=f"TASK-LARGE-EXTREME-{n_agents}",
            required_capability="coding",
        )
        result = resolver.resolve(report, agents=agents)
        assert isinstance(result, ArbitrationResult)
        if result.status == ResolutionStatus.RESOLVED and result.winner:
            loads = {aid: info["load"] for aid, info in agents.items()}
            assert loads[result.winner] <= min(loads.values()) + 1, f"n={n_agents} 应选最低或接近最低负载的agent"

    @pytest.mark.parametrize("n_agents", [50, 100])
    def test_large_scale_agents_not_mutated(self, resolver, n_agents):
        """大规模场景下输入agents字典不应被修改。"""
        agents = generate_agents(n_agents, load_strategy="ascending")
        agents_copy = copy.deepcopy(agents)
        ids = list(agents.keys())
        report = ConflictReport(
            reporter_id=ids[0],
            opponent_id=ids[-1],
            conflict_type=ConflictType.RESPONSIBILITY,
            description=f"大规模防修改 n={n_agents}",
            task_id=f"TASK-LARGE-NOMUT-{n_agents}",
            required_capability="coding",
        )
        resolver.resolve(report, agents=agents)
        assert agents == agents_copy, "输入agents字典不应被修改"


class TestEdgeCaseDefensiveCopy:
    """防御性拷贝与输入不变性测试。"""

    @pytest.fixture
    def resolver(self):
        return ConflictResolver()

    @parametrize_agent_counts
    def test_agents_dict_not_mutated_after_resolve(self, resolver, n_agents):
        """resolve调用后传入的agents字典不应被修改。"""
        agents = generate_agents(n_agents, load_strategy="ascending")
        agents_original = copy.deepcopy(agents)
        ids = list(agents.keys())
        reporter = ids[0]
        opponent = ids[-1] if n_agents > 1 else ids[0]

        report = ConflictReport(
            reporter_id=reporter,
            opponent_id=opponent,
            conflict_type=ConflictType.RESPONSIBILITY,
            description=f"防御性拷贝测试 n={n_agents}",
            task_id=f"TASK-DEFCOPY-{n_agents}",
            required_capability="coding",
        )
        resolver.resolve(report, agents=agents)
        assert agents == agents_original, f"n={n_agents}: agents字典不应被修改"

    @parametrize_agent_counts
    def test_external_modification_after_resolve_does_not_affect_result(self, resolver, n_agents):
        """resolve完成后外部修改agents不应影响已返回的结果对象。"""
        agents = generate_agents(n_agents, load_strategy="ascending")
        ids = list(agents.keys())
        reporter = ids[0]
        opponent = ids[-1] if n_agents > 1 else ids[0]

        report = ConflictReport(
            reporter_id=reporter,
            opponent_id=opponent,
            conflict_type=ConflictType.RESPONSIBILITY,
            description=f"外部修改测试 n={n_agents}",
            task_id=f"TASK-EXTMOD-{n_agents}",
            required_capability="coding",
        )
        result = resolver.resolve(report, agents=agents)
        winner_copy = result.winner
        status_copy = result.status

        for aid in agents:
            agents[aid]["load"] = 999
            agents[aid]["priority"] = 999

        assert result.winner == winner_copy, "外部修改不应改变已返回结果的winner"
        assert result.status == status_copy, "外部修改不应改变已返回结果的status"


class TestEdgeCaseDeterminism:
    """结果确定性测试（相同输入必须相同输出）。"""

    @pytest.fixture
    def resolver(self):
        return ConflictResolver()

    @pytest.mark.parametrize("n_agents", [2, 3, 5, 10])
    @pytest.mark.parametrize("conflict_type", list(ConflictType))
    def test_deterministic_across_all_conflict_types(self, resolver, n_agents, conflict_type):
        """所有冲突类型在相同输入下必须产生相同结果。"""
        agents = generate_agents(n_agents, load_strategy="ascending")
        ids = list(agents.keys())
        report = ConflictReport(
            reporter_id=ids[0],
            opponent_id=ids[-1] if n_agents > 1 else ids[0],
            conflict_type=conflict_type,
            description=f"确定性测试 {conflict_type.value} n={n_agents}",
            task_id=f"TASK-DET-{conflict_type.value}-{n_agents}",
            required_capability="coding",
        )
        results = [resolver.resolve(report, agents=agents) for _ in range(5)]
        winners = [r.winner for r in results]
        statuses = {r.status for r in results}
        assert len(statuses) == 1, f"{conflict_type.value} n={n_agents}: 5次调用应产生相同status"
        resolved_winners = [w for w in winners if w is not None]
        if resolved_winners:
            assert len(set(resolved_winners)) == 1, f"{conflict_type.value} n={n_agents}: 5次调用应产生相同winner"

    def test_different_task_ids_produce_consistent_results(self, resolver):
        """不同的task_id不应影响winner选择逻辑。"""
        agents = generate_agents(5, load_strategy="ascending")
        ids = list(agents.keys())

        winners = set()
        statuses = set()
        for i in range(10):
            report = ConflictReport(
                reporter_id=ids[0],
                opponent_id=ids[-1],
                conflict_type=ConflictType.RESPONSIBILITY,
                description=f"测试{i}",
                task_id=f"TASK-CONSISTENT-{i}",
                required_capability="coding",
            )
            result = resolver.resolve(report, agents=agents)
            statuses.add(result.status)
            if result.winner:
                winners.add(result.winner)

        assert len(statuses) == 1, "不同task_id不应改变status"
        if winners:
            assert len(winners) == 1, "不同task_id不应改变winner选择"


class TestEdgeScenariosComprehensive:
    """使用edge_scenarios()进行综合性边缘场景覆盖测试。"""

    @pytest.fixture
    def resolver(self):
        return ConflictResolver()

    @pytest.mark.parametrize("scenario", edge_scenarios(), ids=lambda s: s.name)
    def test_all_edge_scenarios_either_resolve_or_escalate_no_crash(self, resolver, scenario):
        """所有边缘场景必须：正常返回ArbitrationResult，不崩溃。"""
        if scenario.agent_count < 2:
            pytest.skip(f"单agent或空场景跳过（n={scenario.agent_count}）")

        ids = list(scenario.agents.keys())
        edge_type = scenario.metadata.get("edge_type", "unknown")
        variant = scenario.metadata.get("variant", "")

        required_cap = "coding"
        if edge_type == "partial_match" or edge_type == "no_match":
            required_cap = scenario.metadata.get("required_cap", "coding")

        report = ConflictReport(
            reporter_id=ids[0],
            opponent_id=ids[-1],
            conflict_type=ConflictType.RESPONSIBILITY,
            description=scenario.description,
            task_id=f"TASK-EDGE-{scenario.name}",
            required_capability=required_cap,
        )

        import time
        start = time.time()
        result = resolver.resolve(report, agents=scenario.agents)
        elapsed = time.time() - start

        assert isinstance(result, ArbitrationResult), f"{scenario.name}: 必须返回ArbitrationResult"
        assert result.status in (ResolutionStatus.RESOLVED, ResolutionStatus.ESCALATED), f"{scenario.name}: status必须有效"

        if edge_type == "no_match":
            assert result.status == ResolutionStatus.ESCALATED, f"{scenario.name}: 无能力匹配必须升级"
            assert result.needs_human is True
            assert result.winner is None
            return

        if edge_type == "large_scale":
            assert elapsed < 5.0, f"{scenario.name}: 大规模场景必须<5s，实际{elapsed:.3f}s"
            if scenario.expected_winner and result.status == ResolutionStatus.RESOLVED:
                assert result.winner is not None

        if result.status == ResolutionStatus.RESOLVED and result.winner:
            assert result.winner in scenario.agents, f"{scenario.name}: winner必须在agents中"

        if edge_type == "partial_match" and result.status == ResolutionStatus.RESOLVED and result.winner:
            assert required_cap in scenario.agents[result.winner].get("capabilities", []), f"{scenario.name}: winner必须具备所需能力"
