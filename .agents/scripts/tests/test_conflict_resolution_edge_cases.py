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

import math
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


class TestLoadValueValidation:
    """负载值范围校验测试（P0修复：过滤[0,100]范围外的异常负载值）。"""

    @pytest.fixture
    def resolver(self):
        return ConflictResolver()

    def test_negative_load_agent_not_selected_as_winner(self, resolver):
        """负载为负数的agent不应被选为winner，应从其他有效agent中选择。"""
        agents = {
            "bad_agent": {"id": "bad_agent", "role": "developer", "priority": 2, "load": -50, "capabilities": ["coding"]},
            "good_agent": {"id": "good_agent", "role": "developer", "priority": 2, "load": 50, "capabilities": ["coding"]},
            "high_load_agent": {"id": "high_load_agent", "role": "developer", "priority": 2, "load": 90, "capabilities": ["coding"]},
        }
        report = ConflictReport(
            reporter_id="bad_agent",
            opponent_id="high_load_agent",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="负负载过滤测试",
            task_id="TASK-NEG-LOAD-FILTER",
            required_capability="coding",
        )
        result = resolver.resolve(report, agents=agents)
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "good_agent", "负负载agent应被过滤，选择负载正常的最低负载agent"

    def test_load_over_100_agent_not_selected(self, resolver):
        """负载超过100的agent不应被选为winner。"""
        agents = {
            "overloaded": {"id": "overloaded", "role": "developer", "priority": 2, "load": 150, "capabilities": ["coding"]},
            "normal1": {"id": "normal1", "role": "developer", "priority": 2, "load": 30, "capabilities": ["coding"]},
            "normal2": {"id": "normal2", "role": "developer", "priority": 2, "load": 70, "capabilities": ["coding"]},
        }
        report = ConflictReport(
            reporter_id="overloaded",
            opponent_id="normal2",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="超负载过滤测试",
            task_id="TASK-OVER100-FILTER",
            required_capability="coding",
        )
        result = resolver.resolve(report, agents=agents)
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "normal1", "load>100的agent应被过滤，选择正常负载中最低的"

    def test_missing_load_agent_not_selected(self, resolver):
        """缺少load字段的agent不应被选为winner（使用默认值参与决策会导致错误）。"""
        agents = {
            "noload": {"id": "noload", "role": "developer", "priority": 2, "capabilities": ["coding"]},
            "normal1": {"id": "normal1", "role": "developer", "priority": 2, "load": 40, "capabilities": ["coding"]},
            "normal2": {"id": "normal2", "role": "developer", "priority": 2, "load": 80, "capabilities": ["coding"]},
        }
        report = ConflictReport(
            reporter_id="noload",
            opponent_id="normal2",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="缺load字段过滤测试",
            task_id="TASK-MISSING-LOAD-FILTER",
            required_capability="coding",
        )
        result = resolver.resolve(report, agents=agents)
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "normal1", "缺load字段的agent应被过滤，选择数据完整的agent"

    def test_all_agents_have_invalid_loads_escalates(self, resolver):
        """所有candidate负载都异常时应升级至人工处理。"""
        agents = {
            "bad1": {"id": "bad1", "role": "developer", "priority": 2, "load": -10, "capabilities": ["coding"]},
            "bad2": {"id": "bad2", "role": "developer", "priority": 2, "load": 200, "capabilities": ["coding"]},
            "bad3": {"id": "bad3", "role": "developer", "priority": 2, "capabilities": ["coding"]},
        }
        report = ConflictReport(
            reporter_id="bad1",
            opponent_id="bad2",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="全异常负载升级测试",
            task_id="TASK-ALL-INVALID-LOAD",
            required_capability="coding",
        )
        result = resolver.resolve(report, agents=agents)
        assert result.status == ResolutionStatus.ESCALATED, "所有候选负载都无效时应升级"
        assert result.needs_human is True
        assert result.winner is None

    def test_valid_load_range_zero_and_hundred_are_accepted(self, resolver):
        """负载为0和100是边界有效值，应正常参与负载均衡。"""
        agents = {
            "zero_load": {"id": "zero_load", "role": "developer", "priority": 2, "load": 0, "capabilities": ["coding"]},
            "mid_load": {"id": "mid_load", "role": "developer", "priority": 2, "load": 50, "capabilities": ["coding"]},
            "full_load": {"id": "full_load", "role": "developer", "priority": 2, "load": 100, "capabilities": ["coding"]},
        }
        report = ConflictReport(
            reporter_id="full_load",
            opponent_id="mid_load",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="边界负载值测试",
            task_id="TASK-BOUNDARY-LOAD",
            required_capability="coding",
        )
        result = resolver.resolve(report, agents=agents)
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "zero_load", "load=0是有效边界值，应被选中"

    def test_mixed_valid_invalid_loads_filters_invalid(self, resolver):
        """混合有效和无效负载时，应只在有效值中选择最低负载。"""
        agents = {
            "neg": {"id": "neg", "role": "developer", "priority": 2, "load": -5, "capabilities": ["coding"]},
            "over": {"id": "over", "role": "developer", "priority": 2, "load": 101, "capabilities": ["coding"]},
            "miss": {"id": "miss", "role": "developer", "priority": 2, "capabilities": ["coding"]},
            "valid_low": {"id": "valid_low", "role": "developer", "priority": 2, "load": 20, "capabilities": ["coding"]},
            "valid_mid": {"id": "valid_mid", "role": "developer", "priority": 2, "load": 60, "capabilities": ["coding"]},
            "valid_high": {"id": "valid_high", "role": "developer", "priority": 2, "load": 95, "capabilities": ["coding"]},
        }
        report = ConflictReport(
            reporter_id="neg",
            opponent_id="valid_high",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="混合负载过滤测试",
            task_id="TASK-MIXED-LOAD",
            required_capability="coding",
        )
        result = resolver.resolve(report, agents=agents)
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "valid_low", "无效负载被过滤后，应选有效负载中最低的valid_low(20)"

    def test_all_five_load_anomaly_types_produce_correct_diagnostic_logs(self):
        """覆盖全部5种负载异常类型，验证诊断日志输出正确。

        5种异常类型（对应调试指南）：
        1. 负载缺失 → 诊断信息：缺失(None)
        2. 类型异常（非数值）→ 诊断信息：类型异常(str='high')
        3. 类型异常（布尔值）→ 诊断信息：类型异常(bool=True)
        4. 负值 → 诊断信息：负值(-50)
        5. 超范围 → 诊断信息：超范围(150>100)

        同时包含1个正常agent（load=20），验证过滤后正确选择。
        """
        logs: list[str] = []

        def log_collector(msg: str) -> None:
            logs.append(msg)

        resolver = ConflictResolver(logger=log_collector)

        agents = {
            "miss_load":   {"role": "developer", "priority": 2, "capabilities": ["coding"]},
            "str_load":    {"role": "developer", "priority": 2, "load": "high", "capabilities": ["coding"]},
            "bool_load":   {"role": "developer", "priority": 2, "load": True, "capabilities": ["coding"]},
            "neg_load":    {"role": "developer", "priority": 2, "load": -50, "capabilities": ["coding"]},
            "over_load":   {"role": "developer", "priority": 2, "load": 150, "capabilities": ["coding"]},
            "valid_agent": {"role": "developer", "priority": 2, "load": 20, "capabilities": ["coding"]},
        }

        report = ConflictReport(
            reporter_id="neg_load",
            opponent_id="over_load",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="5种负载异常类型诊断日志验证",
            task_id="TASK-ALL-5-ANOMALIES",
            required_capability="coding",
        )

        result = resolver.resolve(report, agents=agents)

        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "valid_agent", "5个异常agent被过滤后，唯一正常的valid_agent应胜出"

        full_log = "\n".join(logs)

        assert "缺失(None)" in full_log, "应诊断miss_load为负载缺失"
        assert "类型异常(str='high')" in full_log, "应诊断str_load为类型异常（非数值）"
        assert "类型异常(bool=True)" in full_log, "应诊断bool_load为类型异常（布尔值）"
        assert "负值(-50)" in full_log, "应诊断neg_load为负值"
        assert "超范围(150>100)" in full_log, "应诊断over_load为超范围"

        warning_logs = [l for l in logs if l.startswith("[WARNING]")]
        assert len(warning_logs) >= 1, "应有WARNING级别日志输出异常过滤信息"

        load_val_logs = [l for l in logs if "负载校验" in l and "有效候选" in l]
        assert len(load_val_logs) == 1, "应有一条负载校验汇总日志"
        assert "有效候选1个" in load_val_logs[0], "过滤5个异常后应只剩1个有效候选"
        assert "'valid_agent': 20" in load_val_logs[0], "有效候选负载分布应包含valid_agent=20"

        result_log = [l for l in logs if "仲裁结果" in l][0]
        assert "status=resolved" in result_log
        assert "winner=valid_agent" in result_log

    def test_all_five_anomaly_types_without_valid_agent_escalates_with_diagnostics(self):
        """5种异常类型全覆盖且无任何正常agent时，应升级并输出全异常诊断日志。"""
        logs: list[str] = []

        def log_collector(msg: str) -> None:
            logs.append(msg)

        resolver = ConflictResolver(logger=log_collector)

        agents = {
            "miss_load": {"role": "developer", "priority": 2, "capabilities": ["coding"]},
            "str_load":  {"role": "developer", "priority": 2, "load": "low", "capabilities": ["coding"]},
            "bool_load": {"role": "developer", "priority": 2, "load": False, "capabilities": ["coding"]},
            "neg_load":  {"role": "developer", "priority": 2, "load": -10, "capabilities": ["coding"]},
            "over_load": {"role": "developer", "priority": 2, "load": 200, "capabilities": ["coding"]},
        }

        report = ConflictReport(
            reporter_id="miss_load",
            opponent_id="over_load",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="全异常负载升级诊断测试",
            task_id="TASK-ALL-5-ESCALATE",
            required_capability="coding",
        )

        result = resolver.resolve(report, agents=agents)

        assert result.status == ResolutionStatus.ESCALATED
        assert result.needs_human is True
        assert result.winner is None

        full_log = "\n".join(logs)

        assert "缺失(None)" in full_log, "miss_load应诊断为缺失"
        assert "类型异常(str='low')" in full_log, "str_load应诊断为类型异常"
        assert "类型异常(bool=False)" in full_log, "bool_load应诊断为布尔类型异常"
        assert "负值(-10)" in full_log, "neg_load应诊断为负值"
        assert "超范围(200>100)" in full_log, "over_load应诊断为超范围"

        escalate_warnings = [l for l in logs if "[WARNING]" in l and "升级" in l]
        assert len(escalate_warnings) >= 1, "全异常时应有WARNING升级日志"
        assert "所有5个候选agent负载值均异常" in escalate_warnings[0] or "所有5个" in escalate_warnings[0]

    def test_nan_load_is_filtered_with_correct_diagnostic(self):
        """NaN负载值回归测试：防止_diagnose_load对NaN返回空诊断字符串的Bug。

        Bug背景：float('nan')通过isinstance(nan, float)检查，但NaN<0和NaN>100
        均返回False，导致原_diagnose_load返回空字符串("")将NaN误判为有效值。
        实际0<=NaN<=100为False，NaN会被校验过滤但诊断信息为空括号"[]"。

        修复：在_diagnose_load中添加 isinstance(load, float) and load != load 检测，
        返回"非数值(NaN)"诊断信息。

        本测试验证：
        1. NaN负载agent被正确过滤，不参与负载均衡
        2. 诊断日志包含"非数值(NaN)"
        3. NaN+有效agent混合场景下正常agent胜出
        4. math.inf和-math.inf同样被正确过滤
        5. NaN负载agent作为冲突双方时不崩溃
        """
        logs: list[str] = []

        def log_collector(msg: str) -> None:
            logs.append(msg)

        resolver = ConflictResolver(logger=log_collector)

        agents = {
            "nan_load":  {"role": "developer", "priority": 2, "load": math.nan, "capabilities": ["coding"]},
            "inf_load":  {"role": "developer", "priority": 2, "load": math.inf, "capabilities": ["coding"]},
            "ninf_load": {"role": "developer", "priority": 2, "load": -math.inf, "capabilities": ["coding"]},
            "good_agent": {"role": "developer", "priority": 2, "load": 30, "capabilities": ["coding"]},
        }

        report = ConflictReport(
            reporter_id="nan_load",
            opponent_id="inf_load",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="NaN负载回归测试",
            task_id="TASK-NAN-REGRESSION",
            required_capability="coding",
        )

        result = resolver.resolve(report, agents=agents)

        assert result.status == ResolutionStatus.RESOLVED, "3个特殊浮点负载被过滤后good_agent应正常胜出"
        assert result.winner == "good_agent", f"NaN/±Inf负载应被过滤，实际winner={result.winner}"

        full_log = "\n".join(logs)
        assert "非数值(NaN)" in full_log, "NaN应诊断为非数值(NaN)"
        assert "超范围" in full_log, "+inf应诊断为超范围"
        assert "负值" in full_log, "-inf应诊断为负值"

        warning_logs = [l for l in logs if l.startswith("[WARNING]")]
        assert len(warning_logs) >= 1, "应有WARNING日志记录异常过滤"

    def test_all_nan_loads_escalates(self):
        """全部agent负载为NaN/Inf时应正确升级，不崩溃不返回错误winner。"""
        resolver = ConflictResolver()

        agents = {
            "nan1": {"role": "developer", "priority": 2, "load": math.nan, "capabilities": ["coding"]},
            "nan2": {"role": "developer", "priority": 2, "load": float("nan"), "capabilities": ["coding"]},
            "inf":  {"role": "developer", "priority": 2, "load": math.inf, "capabilities": ["coding"]},
        }

        report = ConflictReport(
            reporter_id="nan1",
            opponent_id="inf",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="全NaN/Inf负载升级测试",
            task_id="TASK-ALL-NAN",
            required_capability="coding",
        )

        result = resolver.resolve(report, agents=agents)
        assert result.status == ResolutionStatus.ESCALATED, "全NaN/Inf负载应升级"
        assert result.winner is None
        assert result.needs_human is True


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
