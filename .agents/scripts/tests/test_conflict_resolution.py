"""lib.collaboration.conflict_resolution 单元测试。

覆盖三种冲突类型：职责冲突、技术分歧、资源竞争，以及升级机制。
"""

import pytest

from lib.collaboration.conflict_resolution import (
    ConflictType,
    ConflictReport,
    ArbitrationResult,
    ResolutionStatus,
    ConflictResolver,
)


@pytest.fixture
def resolver():
    return ConflictResolver()


@pytest.fixture
def agent_a():
    return {"id": "developer", "role": "developer", "priority": 2, "load": 50}


@pytest.fixture
def agent_b():
    return {"id": "reviewer", "role": "reviewer", "priority": 2, "load": 50}


@pytest.fixture
def architect():
    return {"id": "architect", "role": "architect", "priority": 3, "load": 30}


class TestConflictTypeEnum:
    """ConflictType 枚举测试。"""

    def test_three_conflict_types_exist(self):
        assert ConflictType.RESPONSIBILITY.value == "responsibility"
        assert ConflictType.TECHNICAL.value == "technical"
        assert ConflictType.RESOURCE.value == "resource"

    def test_from_string_valid(self):
        assert ConflictType.from_str("responsibility") == ConflictType.RESPONSIBILITY
        assert ConflictType.from_str("technical") == ConflictType.TECHNICAL
        assert ConflictType.from_str("resource") == ConflictType.RESOURCE

    def test_from_string_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown conflict type"):
            ConflictType.from_str("invalid_type")


class TestConflictReport:
    """ConflictReport 数据模型测试。"""

    def test_create_valid_report(self, agent_a, agent_b):
        report = ConflictReport(
            reporter_id=agent_a["id"],
            opponent_id=agent_b["id"],
            conflict_type=ConflictType.RESPONSIBILITY,
            description="双方都认为模块编码是自己的职责",
            task_id="TASK-001",
        )
        assert report.reporter_id == "developer"
        assert report.opponent_id == "reviewer"
        assert report.conflict_type == ConflictType.RESPONSIBILITY
        assert report.resolved is False

    def test_report_requires_description(self, agent_a, agent_b):
        with pytest.raises(ValueError, match="description cannot be empty"):
            ConflictReport(
                reporter_id=agent_a["id"],
                opponent_id=agent_b["id"],
                conflict_type=ConflictType.TECHNICAL,
                description="",
                task_id="TASK-002",
            )


class TestArbitrationResult:
    """ArbitrationResult 数据模型测试。"""

    def test_successful_arbitration(self):
        result = ArbitrationResult(
            status=ResolutionStatus.RESOLVED,
            winner="developer",
            reason="初始任务分配为准",
            arbiter="orchestrator",
        )
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "developer"
        assert result.resolved is True

    def test_escalated_arbitration(self):
        result = ArbitrationResult(
            status=ResolutionStatus.ESCALATED,
            winner=None,
            reason="一级仲裁未解决，升级至人工",
            arbiter="orchestrator",
        )
        assert result.status == ResolutionStatus.ESCALATED
        assert result.resolved is False


class TestResponsibilityConflict:
    """职责冲突仲裁测试（Orchestrator负责，4条规则）。"""

    def test_priority_rule_initial_allocation_wins(self, resolver, agent_a, agent_b):
        """优先级原则：初始分配为准。"""
        report = ConflictReport(
            reporter_id="reviewer",
            opponent_id="developer",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="代码实现任务职责归属争议",
            task_id="TASK-101",
            initial_assignee="developer",
        )
        result = resolver.resolve(report)
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "developer"
        assert "初始分配" in result.reason
        assert result.arbiter == "orchestrator"

    def test_capability_matching_rule(self, resolver):
        """能力匹配原则：匹配职责声明的角色获胜。"""
        dev = {"id": "dev1", "role": "developer", "capabilities": ["coding", "testing"]}
        arch = {"id": "arch1", "role": "architect", "capabilities": ["design", "modeling"]}
        report = ConflictReport(
            reporter_id="dev1",
            opponent_id="arch1",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="数据库模型设计任务归属争议",
            task_id="TASK-102",
            required_capability="design",
        )
        result = resolver.resolve(report, agents={"dev1": dev, "arch1": arch})
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "arch1"
        assert "能力匹配" in result.reason

    def test_load_balancing_rule(self, resolver):
        """负载均衡原则：相同优先级时低负载者接手。"""
        busy = {"id": "busy_dev", "role": "developer", "load": 90, "priority": 2}
        free = {"id": "free_dev", "role": "developer", "load": 20, "priority": 2}
        report = ConflictReport(
            reporter_id="busy_dev",
            opponent_id="free_dev",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="两个开发都不想接手的新任务分配争议",
            task_id="TASK-103",
            initial_assignee=None,
        )
        result = resolver.resolve(report, agents={"busy_dev": busy, "free_dev": free})
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "free_dev"
        assert "负载均衡" in result.reason

    def test_historical_ownership_rule(self, resolver):
        """历史归属原则：历史上负责该模块者优先。"""
        agent_a = {"id": "dev_a", "role": "developer", "load": 50, "priority": 2}
        agent_b = {"id": "dev_b", "role": "developer", "load": 50, "priority": 2}
        report = ConflictReport(
            reporter_id="dev_a",
            opponent_id="dev_b",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="模块维护职责争议",
            task_id="TASK-104",
            module_path="lib/checks/vendor.py",
        )
        history = {"lib/checks/vendor.py": "dev_b"}
        result = resolver.resolve(
            report,
            agents={"dev_a": agent_a, "dev_b": agent_b},
            module_ownership_history=history,
        )
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "dev_b"
        assert "历史归属" in result.reason


class TestTechnicalConflict:
    """技术分歧决策测试（Architect负责，5条规则）。"""

    def test_spec_first_rule(self, resolver):
        """规范优先原则：符合项目规范的方案获胜。"""
        report = ConflictReport(
            reporter_id="dev1",
            opponent_id="dev2",
            conflict_type=ConflictType.TECHNICAL,
            description="关于Mermaid边标签格式的争议",
            task_id="TASK-201",
            proposal_a="边标签使用 -->|文本| 格式",
            proposal_b="边标签使用 -->| 文本 | 带空格格式",
        )
        spec_rules = {"mermaid_edge_label": "使用-->|文本|格式，不加空格"}
        result = resolver.resolve(report, spec_rules=spec_rules)
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "dev1"
        assert result.arbiter == "architect"
        assert "规范优先" in result.reason

    def test_best_practice_rule(self, resolver):
        """最佳实践原则：无明确规范时选择业界最佳实践。"""
        report = ConflictReport(
            reporter_id="dev_a",
            opponent_id="dev_b",
            conflict_type=ConflictType.TECHNICAL,
            description="错误处理方案争议",
            task_id="TASK-202",
            proposal_a="使用异常抛出+上层统一捕获",
            proposal_b="使用返回错误码+手动检查",
        )
        result = resolver.resolve(report, spec_rules={})
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "dev_a"
        assert "最佳实践" in result.reason

    def test_maintainability_rule(self, resolver):
        """可维护性原则：选择更易维护的方案。"""
        report = ConflictReport(
            reporter_id="dev1",
            opponent_id="dev2",
            conflict_type=ConflictType.TECHNICAL,
            description="代码实现方案争议",
            task_id="TASK-203",
            proposal_a="拆分模块，单一职责，函数<50行",
            proposal_b="单文件大函数，200行完成所有逻辑",
        )
        result = resolver.resolve(report, spec_rules={})
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "dev1"
        assert "可维护性" in result.reason

    def test_minimal_change_rule(self, resolver):
        """最小变更原则：选择对现有代码改动最小的方案。"""
        report = ConflictReport(
            reporter_id="dev1",
            opponent_id="dev2",
            conflict_type=ConflictType.TECHNICAL,
            description="Bug修复方案争议",
            task_id="TASK-204",
            proposal_a="局部修复，修改1个函数",
            proposal_b="重构整个模块，修改10个文件",
            is_bugfix=True,
        )
        result = resolver.resolve(report, spec_rules={})
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "dev1"
        assert "最小变更" in result.reason

    def test_architect_final_arbitration_rule(self, resolver):
        """Architect终裁原则：所有规则无法判断时，由Architect直接决定。"""
        report = ConflictReport(
            reporter_id="dev_a",
            opponent_id="dev_b",
            conflict_type=ConflictType.TECHNICAL,
            description="两种方案各有优劣，无明显偏好",
            task_id="TASK-205",
            proposal_a="方案A（性能优先）",
            proposal_b="方案B（可读性优先）",
        )
        result = resolver.resolve(
            report,
            spec_rules={},
            architect_decision="dev_b",
        )
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "dev_b"
        assert "终裁" in result.reason


class TestResourceConflict:
    """资源竞争调度测试（Orchestrator负责，4条规则）。"""

    def test_serial_access_rule(self, resolver):
        """串行访问原则：独占资源需要按顺序访问。"""
        report = ConflictReport(
            reporter_id="dev1",
            opponent_id="dev2",
            conflict_type=ConflictType.RESOURCE,
            description="两个角色同时需要写入同一文件",
            task_id="TASK-301",
            resource="file:config.yaml",
            resource_type="exclusive_file",
        )
        result = resolver.resolve(report, request_order=["dev1", "dev2"])
        assert result.status == ResolutionStatus.RESOLVED
        assert result.access_order == ["dev1", "dev2"]
        assert "串行访问" in result.reason
        assert result.arbiter == "orchestrator"

    def test_priority_scheduling_rule(self, resolver):
        """优先级调度原则：高优先级角色优先获得资源。"""
        high = {"id": "hotfix_dev", "role": "developer", "priority": 1}
        normal = {"id": "feature_dev", "role": "developer", "priority": 3}
        report = ConflictReport(
            reporter_id="feature_dev",
            opponent_id="hotfix_dev",
            conflict_type=ConflictType.RESOURCE,
            description="紧急修复和功能开发都需要测试环境资源",
            task_id="TASK-302",
            resource="env:test",
            resource_type="shared_environment",
        )
        result = resolver.resolve(
            report,
            agents={"hotfix_dev": high, "feature_dev": normal},
        )
        assert result.status == ResolutionStatus.RESOLVED
        assert result.access_order[0] == "hotfix_dev"
        assert "优先级调度" in result.reason

    def test_lock_mechanism_rule(self, resolver):
        """锁机制原则：支持资源锁定，完成后释放。"""
        report = ConflictReport(
            reporter_id="dev1",
            opponent_id="dev2",
            conflict_type=ConflictType.RESOURCE,
            description="数据库迁移时的表锁竞争",
            task_id="TASK-303",
            resource="db:main",
            resource_type="database",
            needs_lock=True,
        )
        result = resolver.resolve(report, request_order=["dev1", "dev2"])
        assert result.status == ResolutionStatus.RESOLVED
        assert result.lock_holder == "dev1"
        assert "锁机制" in result.reason

    def test_resource_isolation_rule(self, resolver):
        """资源隔离原则：可隔离资源分配独立副本。"""
        report = ConflictReport(
            reporter_id="dev_a",
            opponent_id="dev_b",
            conflict_type=ConflictType.RESOURCE,
            description="两个开发都需要独立的测试环境",
            task_id="TASK-304",
            resource="env:test",
            resource_type="isolatable_environment",
            can_isolate=True,
        )
        result = resolver.resolve(report)
        assert result.status == ResolutionStatus.RESOLVED
        assert result.isolated is True
        assert "资源隔离" in result.reason


class TestEscalationMechanism:
    """冲突升级机制测试。"""

    def test_escalate_when_both_parties_reject(self, resolver, agent_a, agent_b):
        """双方都不接受一级仲裁结果时升级。"""
        report = ConflictReport(
            reporter_id=agent_a["id"],
            opponent_id=agent_b["id"],
            conflict_type=ConflictType.RESPONSIBILITY,
            description="严重职责争议，双方都不接受初步仲裁",
            task_id="TASK-401",
            initial_assignee=agent_a["id"],
            rejected_by=[agent_a["id"], agent_b["id"]],
        )
        result = resolver.resolve(report)
        assert result.status == ResolutionStatus.ESCALATED
        assert result.resolved is False
        assert "升级" in result.reason

    def test_escalate_when_out_of_scope(self, resolver, agent_a, architect):
        """超出规范范围的技术分歧升级至人工。"""
        report = ConflictReport(
            reporter_id=agent_a["id"],
            opponent_id=architect["id"],
            conflict_type=ConflictType.TECHNICAL,
            description="涉及新技术选型，超出现有规范",
            task_id="TASK-402",
            proposal_a="使用新技术A",
            proposal_b="使用新技术B",
            out_of_spec_scope=True,
        )
        result = resolver.resolve(report, spec_rules={})
        assert result.status == ResolutionStatus.ESCALATED
        assert result.needs_human is True

    def test_logging_all_steps(self, resolver, agent_a, agent_b):
        """冲突处理全过程应有日志记录。"""
        logs = []
        resolver_with_log = ConflictResolver(logger=lambda msg: logs.append(msg))
        report = ConflictReport(
            reporter_id=agent_a["id"],
            opponent_id=agent_b["id"],
            conflict_type=ConflictType.RESPONSIBILITY,
            description="测试日志记录",
            task_id="TASK-501",
            initial_assignee=agent_a["id"],
        )
        resolver_with_log.resolve(report)
        assert len(logs) >= 3
        assert any("冲突报告" in log for log in logs)
        assert any("仲裁结果" in log for log in logs)


class TestConflictTypesIntegration:
    """冲突类型识别与自动路由集成测试。"""

    def test_responsibility_routes_to_orchestrator(self, resolver, agent_a, agent_b):
        report = ConflictReport(
            reporter_id=agent_a["id"],
            opponent_id=agent_b["id"],
            conflict_type=ConflictType.RESPONSIBILITY,
            description="职责争议",
            task_id="TASK-INT-1",
            initial_assignee=agent_a["id"],
        )
        result = resolver.resolve(report)
        assert result.arbiter == "orchestrator"

    def test_technical_routes_to_architect(self, resolver, agent_a, agent_b):
        report = ConflictReport(
            reporter_id=agent_a["id"],
            opponent_id=agent_b["id"],
            conflict_type=ConflictType.TECHNICAL,
            description="技术分歧",
            task_id="TASK-INT-2",
            proposal_a="方案A",
            proposal_b="方案B",
        )
        result = resolver.resolve(report, spec_rules={"default": "A"})
        assert result.arbiter == "architect"

    def test_resource_routes_to_orchestrator(self, resolver, agent_a, agent_b):
        report = ConflictReport(
            reporter_id=agent_a["id"],
            opponent_id=agent_b["id"],
            conflict_type=ConflictType.RESOURCE,
            description="资源竞争",
            task_id="TASK-INT-3",
            resource="test_env",
            resource_type="shared",
        )
        result = resolver.resolve(report, request_order=[agent_a["id"], agent_b["id"]])
        assert result.arbiter == "orchestrator"


class TestDeadlockPrevention:
    """死锁/活锁预防机制测试。"""

    def test_lock_has_timeout(self, resolver):
        """资源锁必须附带超时，防止持有者崩溃导致永久死锁。"""
        report = ConflictReport(
            reporter_id="dev1",
            opponent_id="dev2",
            conflict_type=ConflictType.RESOURCE,
            description="数据库锁竞争",
            task_id="TASK-DEADLOCK-1",
            resource="db:main",
            needs_lock=True,
        )
        result = resolver.resolve(report, request_order=["dev1", "dev2"])
        assert result.lock_holder == "dev1"
        assert result.lock_timeout_seconds is not None
        assert result.lock_timeout_seconds > 0

    def test_custom_lock_timeout(self):
        """支持自定义锁超时时间。"""
        resolver = ConflictResolver(lock_timeout_seconds=60)
        report = ConflictReport(
            reporter_id="dev1",
            opponent_id="dev2",
            conflict_type=ConflictType.RESOURCE,
            description="短超时资源",
            task_id="TASK-DEADLOCK-2",
            resource="cache:hot",
            needs_lock=True,
        )
        result = resolver.resolve(report, request_order=["dev1", "dev2"])
        assert result.lock_timeout_seconds == 60

    def test_rejected_by_deduplication(self):
        """rejected_by列表自动去重，防止同一agent重复拒绝绕过升级检查。"""
        report = ConflictReport(
            reporter_id="dev1",
            opponent_id="dev2",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="测试拒绝去重",
            task_id="TASK-DEADLOCK-3",
            rejected_by=["dev1", "dev1", "dev1"],
        )
        assert len(report.rejected_by) == 1

    def test_add_rejection_dedup(self):
        """add_rejection方法防止重复添加。"""
        report = ConflictReport(
            reporter_id="dev1",
            opponent_id="dev2",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="测试add_rejection去重",
            task_id="TASK-DEADLOCK-4",
        )
        report.add_rejection("dev1")
        report.add_rejection("dev1")
        report.add_rejection("dev2")
        assert report.rejected_by == ["dev1", "dev2"]

    def test_two_distinct_rejections_triggers_escalation(self, resolver):
        """双方都拒绝（去重后）触发升级，而不是需要>=2次重复拒绝。"""
        report = ConflictReport(
            reporter_id="dev1",
            opponent_id="dev2",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="双方各拒绝一次",
            task_id="TASK-DEADLOCK-5",
            rejected_by=["dev1", "dev2"],
        )
        result = resolver.resolve(report)
        assert result.status == ResolutionStatus.ESCALATED
        assert result.needs_human is True

    def test_infinite_loop_prevention_via_escalation(self, resolver):
        """升级机制防止无限循环仲裁（双方拒绝后不再继续规则匹配）。"""
        report = ConflictReport(
            reporter_id="dev_a",
            opponent_id="dev_b",
            conflict_type=ConflictType.TECHNICAL,
            description="技术分歧但双方都拒绝",
            task_id="TASK-DEADLOCK-6",
            proposal_a="方案A",
            proposal_b="方案B",
            rejected_by=["dev_a", "dev_b"],
        )
        result = resolver.resolve(report, spec_rules={"key": "value"})
        assert result.status == ResolutionStatus.ESCALATED
        assert result.arbiter == "architect"


class TestPerformanceAndCorrectness:
    """性能优化和多agent场景正确性测试。"""

    def test_from_str_uses_cache(self):
        """from_str使用缓存字典O(1)查找，不是每次线性遍历。"""
        for _ in range(100):
            assert ConflictType.from_str("responsibility") == ConflictType.RESPONSIBILITY
            assert ConflictType.from_str("technical") == ConflictType.TECHNICAL
            assert ConflictType.from_str("resource") == ConflictType.RESOURCE

    def test_multi_agent_load_balancing_selects_lowest(self, resolver):
        """多agent（>2）场景下负载均衡选择真正最低负载的agent。"""
        agents = {
            "dev_heavy": {"load": 90, "capabilities": ["coding"]},
            "dev_medium": {"load": 50, "capabilities": ["coding"]},
            "dev_light": {"load": 10, "capabilities": ["coding"]},
        }
        report = ConflictReport(
            reporter_id="dev_heavy",
            opponent_id="dev_light",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="三个开发竞争新任务",
            task_id="TASK-PERF-1",
            required_capability="coding",
        )
        result = resolver.resolve(report, agents=agents)
        assert result.winner == "dev_light"

    def test_multi_agent_priority_scheduling(self, resolver):
        """多agent资源竞争时，正确按优先级排序所有agent。"""
        agents = {
            "hotfix": {"priority": 1},
            "feature_a": {"priority": 2},
            "feature_b": {"priority": 3},
            "chore": {"priority": 5},
        }
        report = ConflictReport(
            reporter_id="chore",
            opponent_id="feature_b",
            conflict_type=ConflictType.RESOURCE,
            description="四个任务竞争测试环境",
            task_id="TASK-PERF-2",
            resource="env:test",
        )
        result = resolver.resolve(
            report,
            agents=agents,
            request_order=["chore", "feature_b", "feature_a", "hotfix"],
        )
        assert result.winner == "hotfix"
        assert result.access_order[0] == "hotfix"

    def test_defensive_copy_agents_not_mutated(self, resolver):
        """传入的agents字典不被修改（防御性拷贝）。"""
        agents = {"dev1": {"load": 50}, "dev2": {"load": 80}}
        original = str(agents)
        report = ConflictReport(
            reporter_id="dev1",
            opponent_id="dev2",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="测试防御性拷贝",
            task_id="TASK-PERF-3",
        )
        resolver.resolve(report, agents=agents)
        assert str(agents) == original

    def test_capability_match_with_tie_uses_load(self, resolver):
        """多个agent都满足能力要求时，选择负载最低的。"""
        agents = {
            "dev_expert": {"capabilities": ["design", "coding"], "load": 60},
            "dev_junior": {"capabilities": ["design"], "load": 20},
        }
        report = ConflictReport(
            reporter_id="dev_expert",
            opponent_id="dev_junior",
            conflict_type=ConflictType.RESPONSIBILITY,
            description="设计任务分配",
            task_id="TASK-PERF-4",
            required_capability="design",
        )
        result = resolver.resolve(report, agents=agents)
        assert result.winner == "dev_junior"
        assert "负载均衡" in result.reason or "能力匹配" in result.reason

    def test_lock_timeout_in_priority_scheduling(self, resolver):
        """优先级调度+锁机制也附带超时。"""
        agents = {
            "urgent": {"priority": 1},
            "normal": {"priority": 3},
        }
        report = ConflictReport(
            reporter_id="normal",
            opponent_id="urgent",
            conflict_type=ConflictType.RESOURCE,
            description="紧急任务需要数据库锁",
            task_id="TASK-PERF-5",
            resource="db:main",
            needs_lock=True,
        )
        result = resolver.resolve(report, agents=agents)
        assert result.winner == "urgent"
        assert result.lock_holder == "urgent"
        assert result.lock_timeout_seconds is not None


class TestBestPracticeConfigurable:
    """最佳实践规则可配置性测试。"""

    def test_custom_best_practice_rules(self):
        """支持自定义最佳实践规则，不依赖硬编码。"""
        custom_rules = {
            "my_rule": (("preferred_kw",), ("bad_kw",)),
        }
        resolver = ConflictResolver(best_practice_rules=custom_rules)
        report = ConflictReport(
            reporter_id="dev1",
            opponent_id="dev2",
            conflict_type=ConflictType.TECHNICAL,
            description="自定义规则测试",
            task_id="TASK-CFG-1",
            proposal_a="方案使用preferred_kw",
            proposal_b="方案使用bad_kw",
        )
        result = resolver.resolve(report, spec_rules={})
        assert result.winner == "dev1"
        assert result.status == ResolutionStatus.RESOLVED

