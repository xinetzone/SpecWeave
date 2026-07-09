"""ConflictResolver 多智能体边界场景测试。

使用 lib.testing 模板库，自动覆盖 N=1,2,3,5,10 个agent的边界场景。
本文件由复盘改进建议驱动创建，防止多agent场景下的饥饿/不公平调度bug。
"""

import pytest

from lib.collaboration.conflict_resolution import (
    ConflictType,
    ConflictReport,
    ConflictResolver,
    ResolutionStatus,
)
from lib.testing import (
    generate_agents,
    agent_scenarios,
    parametrize_agent_counts,
    BOUNDARY_AGENT_COUNTS,
    MultiAgentScenario,
)


@pytest.fixture
def resolver():
    return ConflictResolver()


@parametrize_agent_counts(skip_single=False)
def test_load_balancing_with_n_agents(resolver, n_agents):
    """N个agent场景下，负载均衡应选择真正负载最低的agent。"""
    agents = generate_agents(n_agents, load_strategy="ascending")
    if n_agents == 0:
        return

    reporter_id = next(iter(agents.keys()))
    opponent_id = list(agents.keys())[-1] if n_agents > 1 else reporter_id

    report = ConflictReport(
        reporter_id=reporter_id,
        opponent_id=opponent_id,
        conflict_type=ConflictType.RESPONSIBILITY,
        description=f"{n_agents}个agent负载均衡测试",
        task_id=f"TASK-BOUNDARY-LB-{n_agents}",
        required_capability="coding",
    )

    result = resolver.resolve(report, agents=agents)

    if n_agents == 1:
        assert result.winner == reporter_id
    else:
        loads = {aid: info["load"] for aid, info in agents.items()}
        min_load = min(loads.values())
        expected_candidates = [aid for aid, load in loads.items() if load == min_load]
        assert result.winner in expected_candidates


@parametrize_agent_counts
def test_priority_scheduling_with_n_agents(resolver, n_agents):
    """N个agent资源竞争时，优先级调度始终选择最高优先级agent。"""
    agents = generate_agents(n_agents, priority_strategy="ascending")
    if n_agents == 0:
        return

    all_ids = list(agents.keys())
    reporter_id = all_ids[-1]
    opponent_id = all_ids[0] if n_agents > 1 else reporter_id

    report = ConflictReport(
        reporter_id=reporter_id,
        opponent_id=opponent_id,
        conflict_type=ConflictType.RESOURCE,
        description=f"{n_agents}个agent优先级调度测试",
        task_id=f"TASK-BOUNDARY-PRIO-{n_agents}",
        resource="env:test",
        resource_type="shared_environment",
    )

    request_order = list(reversed(all_ids)) if n_agents > 1 else all_ids
    result = resolver.resolve(report, agents=agents, request_order=request_order)

    if n_agents == 1:
        assert result.winner == reporter_id
    else:
        priorities = {aid: info["priority"] for aid, info in agents.items()}
        highest_priority = min(priorities.values())
        expected_candidates = [aid for aid, prio in priorities.items() if prio == highest_priority]
        assert result.winner in expected_candidates


@parametrize_agent_counts
def test_no_agent_starvation_with_capability_match(resolver, n_agents):
    """能力匹配+负载均衡时，最低负载且有能力的agent不应被饿死。"""
    if n_agents < 2:
        pytest.skip("饥饿场景需要至少2个agent")

    agents = generate_agents(n_agents, load_strategy="extremes")
    all_ids = list(agents.keys())

    report = ConflictReport(
        reporter_id=all_ids[0],
        opponent_id=all_ids[-1],
        conflict_type=ConflictType.RESPONSIBILITY,
        description=f"{n_agents}个agent饥饿测试",
        task_id=f"TASK-BOUNDARY-STARVE-{n_agents}",
        required_capability="coding",
    )

    result = resolver.resolve(report, agents=agents)

    loads = {aid: info["load"] for aid, info in agents.items()}
    min_load = min(loads.values())
    assert loads[result.winner] == min_load


def test_agents_dictionary_not_mutated(resolver):
    """验证防御性拷贝：传入的agents字典不会被resolve方法修改。"""
    scenarios = agent_scenarios(name_prefix="defcopy", counts=BOUNDARY_AGENT_COUNTS)
    for sc in scenarios:
        agents_before = str(sc.agents)
        ids = list(sc.agents.keys())
        if len(ids) < 2:
            ids = ids + ids
        report = ConflictReport(
            reporter_id=ids[0],
            opponent_id=ids[-1],
            conflict_type=ConflictType.RESPONSIBILITY,
            description=f"防御性拷贝验证: {sc.description}",
            task_id=f"TASK-DEFCOPY-{sc.agent_count}",
            required_capability="coding",
        )
        resolver.resolve(report, agents=sc.agents)
        agents_after = str(sc.agents)
        assert agents_before == agents_after, f"场景 {sc.name}: agents字典被修改"


def test_lock_timeout_present_for_all_lock_scenarios(resolver):
    """所有需要锁的场景都必须设置超时，无例外。"""
    for n in BOUNDARY_AGENT_COUNTS:
        agents = generate_agents(n, priority_strategy="ascending")
        ids = list(agents.keys()) if agents else ["dev1", "dev2"]
        if len(ids) < 2:
            ids = ids + [f"dev_extra_{i}" for i in range(2 - len(ids))]
        report = ConflictReport(
            reporter_id=ids[-1],
            opponent_id=ids[0],
            conflict_type=ConflictType.RESOURCE,
            description=f"{n}个agent锁超时测试",
            task_id=f"TASK-LOCK-TIMEOUT-{n}",
            resource="db:main",
            resource_type="database",
            needs_lock=True,
        )
        result = resolver.resolve(report, agents=agents if agents else None)
        assert result.lock_timeout_seconds is not None, f"n={n}: 锁未设置超时"
        assert result.lock_timeout_seconds > 0, f"n={n}: 超时时间必须为正数"


def test_rejection_idempotent_across_scenarios():
    """重复拒绝同一agent在各种场景下都是幂等的。"""
    for n in (2, 3, 5):
        report = ConflictReport(
            reporter_id="dev_a",
            opponent_id="dev_b",
            conflict_type=ConflictType.RESPONSIBILITY,
            description=f"{n}次重复拒绝幂等性测试",
            task_id=f"TASK-IDEMPOTENT-REJ-{n}",
        )
        target = "dev_x"
        for _ in range(n):
            report.add_rejection(target)
        assert report.rejected_by.count(target) == 1
        assert len(report.rejected_by) == 1


@parametrize_agent_counts
def test_deterministic_results_with_same_input(resolver, n_agents):
    """相同输入必须产生确定性结果，无随机性。"""
    agents = generate_agents(n_agents, load_strategy="ascending", priority_strategy="descending")
    ids = list(agents.keys())
    if len(ids) < 2:
        ids = ids + ["dev_fallback"]
        if "dev_fallback" not in agents:
            agents["dev_fallback"] = {"id": "dev_fallback", "role": "developer", "priority": 2, "load": 50, "capabilities": ["coding"]}
    ids = list(agents.keys())

    results = []
    for _ in range(5):
        report = ConflictReport(
            reporter_id=ids[0],
            opponent_id=ids[-1],
            conflict_type=ConflictType.RESPONSIBILITY,
            description="确定性测试",
            task_id=f"TASK-DETERM-{n_agents}",
            required_capability="coding",
        )
        result = resolver.resolve(report, agents=agents)
        results.append((result.winner, result.reason))

    first_winner, first_reason = results[0]
    for winner, reason in results[1:]:
        assert winner == first_winner, f"n={n_agents}: 结果不稳定，winner变化"
