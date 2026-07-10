"""多智能体边界场景测试模板。

为仲裁/调度类模块提供标准化的多agent测试场景生成器，
自动覆盖N=1,2,3,5,10等边界数量场景。
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from collections.abc import Callable
import pytest


BOUNDARY_AGENT_COUNTS = (1, 2, 3, 5, 10)


@dataclass
class MultiAgentScenario:
    """多agent测试场景描述。"""

    name: str
    agent_count: int
    agents: dict[str, dict[str, Any]]
    description: str = ""
    expected_winner: str | None = None
    expected_access_order: list[str] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def generate_agents(
    count: int,
    *,
    role: str = "developer",
    priority_strategy: str = "uniform",
    load_strategy: str = "ascending",
    capabilities: list[str] | None = None,
    id_prefix: str = "agent",
) -> dict[str, dict[str, Any]]:
    """生成指定数量的agent字典。

    Args:
        count: agent数量，推荐使用BOUNDARY_AGENT_COUNTS中的值
        role: 角色名称
        priority_strategy: 优先级策略
            - "uniform": 所有agent优先级相同(2)
            - "ascending": 优先级从1递增（第一个最高）
            - "descending": 优先级递减（最后一个最高）
            - "random": 随机优先级1-5
        load_strategy: 负载策略
            - "uniform": 所有agent负载相同(50)
            - "ascending": 负载递增（第一个最低）
            - "descending": 负载递减（最后一个最低）
            - "extremes": 第一个最高(99)，最后一个最低(1)，其余均匀
        capabilities: 能力列表，None则默认所有agent有"coding"能力
        id_prefix: agent ID前缀

    Returns:
        dict[str, dict]: agent字典 {agent_id: agent_info}
    """
    agents: dict[str, dict[str, Any]] = {}
    base_caps = capabilities or ["coding"]

    for i in range(count):
        aid = f"{id_prefix}_{i}" if count > 1 else id_prefix

        if priority_strategy == "uniform":
            priority = 2
        elif priority_strategy == "ascending":
            priority = i + 1
        elif priority_strategy == "descending":
            priority = count - i
        else:
            priority = (i % 5) + 1

        if load_strategy == "uniform":
            load = 50
        elif load_strategy == "ascending":
            load = int(10 + (i / max(count - 1, 1)) * 80) if count > 1 else 50
        elif load_strategy == "descending":
            load = int(90 - (i / max(count - 1, 1)) * 80) if count > 1 else 50
        elif load_strategy == "extremes":
            if count == 1:
                load = 50
            elif i == 0:
                load = 99
            elif i == count - 1:
                load = 1
            else:
                load = int(99 - (i / (count - 1)) * 98)

        agent_caps = list(base_caps)
        agents[aid] = {
            "id": aid,
            "role": role,
            "priority": priority,
            "load": load,
            "capabilities": agent_caps,
        }

    return agents


def agent_scenarios(
    *,
    name_prefix: str = "scenario",
    counts: tuple[int, ...] = BOUNDARY_AGENT_COUNTS,
    priority_strategies: tuple[str, ...] = ("uniform", "ascending", "descending"),
    load_strategies: tuple[str, ...] = ("uniform", "ascending", "descending", "extremes"),
    role: str = "developer",
    capabilities: list[str] | None = None,
) -> list[MultiAgentScenario]:
    """生成多agent边界场景矩阵。

    Args:
        name_prefix: 场景名称前缀
        counts: agent数量元组，默认覆盖1,2,3,5,10
        priority_strategies: 要测试的优先级策略组合
        load_strategies: 要测试的负载策略组合
        role: 角色名
        capabilities: 能力列表

    Returns:
        list[MultiAgentScenario]: 测试场景列表
    """
    scenarios: list[MultiAgentScenario] = []

    for count in counts:
        for prio_strat in priority_strategies:
            for load_strat in load_strategies:
                name = f"{name_prefix}_n{count}_prio-{prio_strat}_load-{load_strat}"
                agents = generate_agents(
                    count,
                    role=role,
                    priority_strategy=prio_strat,
                    load_strategy=load_strat,
                    capabilities=capabilities,
                )

                expected_winner = None
                if count == 1:
                    expected_winner = next(iter(agents.keys()))
                elif prio_strat == "ascending" and load_strat != "extremes":
                    expected_winner = f"agent_0" if count > 1 else role
                elif load_strat == "extremes" and count >= 2:
                    expected_winner = f"agent_{count - 1}"

                scenarios.append(
                    MultiAgentScenario(
                        name=name,
                        agent_count=count,
                        agents=agents,
                        description=f"{count}个agent, 优先级策略={prio_strat}, 负载策略={load_strat}",
                        expected_winner=expected_winner,
                        metadata={
                            "priority_strategy": prio_strat,
                            "load_strategy": load_strat,
                        },
                    )
                )

    return scenarios


def parametrize_agent_counts(
    *test_funcs: Callable,
    counts: tuple[int, ...] = BOUNDARY_AGENT_COUNTS,
    skip_single: bool = False,
):
    """装饰器：为测试函数参数化不同agent数量。

    用法:
        @parametrize_agent_counts
        def test_load_balancing(n_agents):
            agents = generate_agents(n_agents, load_strategy="ascending")
            # 测试逻辑...

    Args:
        test_funcs: 要装饰的测试函数
        counts: agent数量元组
        skip_single: 是否跳过n=1的单agent场景
    """
    effective_counts = tuple(c for c in counts if not (skip_single and c == 1))

    def decorator(func):
        return pytest.mark.parametrize(
            "n_agents",
            effective_counts,
            ids=[f"agents={n}" for n in effective_counts],
        )(func)

    if test_funcs:
        if len(test_funcs) == 1:
            return decorator(test_funcs[0])
        return [decorator(f) for f in test_funcs]
    return decorator


BOUNDARY_ASSERTIONS = {
    "no_starvation": "所有capability匹配的候选agent中，低负载/高优先级agent应在合理轮次内被选中",
    "deterministic": "相同输入应产生相同结果，无随机波动",
    "timeout_protection": "涉及锁/等待的操作必须有超时机制",
    "idempotent_rejection": "重复拒绝同一agent不应改变拒绝集合大小",
    "defensive_copy": "传入的agents字典不应被resolve方法修改",
    "empty_input": "空agents字典/None输入应抛出明确异常而非崩溃",
    "invalid_values": "负优先级、超范围负载等无效值应被处理或拒绝",
    "tie_breaking": "所有agent优先级和负载完全相同时应有确定性的平局打破机制",
    "missing_fields": "缺少必要字段的agent应被优雅处理或跳过",
    "large_scale": "大规模agent场景(100+)应性能正常不超时",
}


EXTREME_AGENT_COUNTS = (0, 1, 2, 3, 5, 10, 50, 100)


def generate_malformed_agents(
    variant: str = "missing_priority",
    base_count: int = 3,
) -> dict[str, dict[str, Any]]:
    """生成包含异常/畸形数据的agent字典，用于错误处理测试。

    Args:
        variant: 畸形数据类型
            - "missing_priority": 部分agent缺少priority字段
            - "missing_load": 部分agent缺少load字段
            - "missing_capabilities": 部分agent缺少capabilities字段
            - "negative_priority": 优先级为负数
            - "negative_load": 负载为负数
            - "load_over_100": 负载超过100
            - "empty_capabilities": capabilities为空列表
            - "mixed_roles": 混合多种角色
            - "duplicate_id_effect": 构造ID相似场景
        base_count: 基础agent数量

    Returns:
        dict[str, dict]: 包含畸形数据的agent字典
    """
    agents = generate_agents(base_count)

    if variant == "missing_priority":
        del agents["agent_0"]["priority"]
    elif variant == "missing_load":
        del agents["agent_0"]["load"]
    elif variant == "missing_capabilities":
        del agents["agent_0"]["capabilities"]
    elif variant == "negative_priority":
        agents["agent_0"]["priority"] = -1
    elif variant == "negative_load":
        agents["agent_0"]["load"] = -50
    elif variant == "load_over_100":
        agents["agent_0"]["load"] = 150
    elif variant == "empty_capabilities":
        agents["agent_0"]["capabilities"] = []
    elif variant == "mixed_roles":
        agents["agent_0"]["role"] = "architect"
        agents["agent_1"]["role"] = "reviewer" if base_count > 2 else "architect"
    elif variant == "extreme_priority_range":
        agents["agent_0"]["priority"] = 999
        if base_count > 1:
            agents[f"agent_{base_count-1}"]["priority"] = 0

    return agents


def generate_tie_scenario(count: int = 5) -> dict[str, dict[str, Any]]:
    """生成完全平局场景：所有agent优先级和负载完全相同。

    用于测试平局打破机制的确定性。
    """
    agents = generate_agents(count, priority_strategy="uniform", load_strategy="uniform")
    for info in agents.values():
        info["capabilities"] = ["coding"]
    return agents


def generate_partial_capability_match(
    count: int = 5,
    required_cap: str = "design",
    matching_count: int = 2,
) -> dict[str, dict[str, Any]]:
    """生成部分agent能力匹配场景。

    Args:
        count: 总agent数
        required_cap: 需要的能力
        matching_count: 拥有该能力的agent数量

    Returns:
        dict[str, dict]: agents字典，其中matching_count个agent拥有required_cap
    """
    agents = generate_agents(count, load_strategy="ascending")
    ids = list(agents.keys())
    for i, aid in enumerate(ids):
        if i < matching_count:
            agents[aid]["capabilities"] = ["coding", required_cap]
        else:
            agents[aid]["capabilities"] = ["coding"]
    return agents


def edge_scenarios() -> list[MultiAgentScenario]:
    """生成全套边缘测试场景，覆盖极端输入和异常情况。

    Returns:
        list[MultiAgentScenario]: 边缘场景列表
    """
    scenarios: list[MultiAgentScenario] = []

    scenarios.append(
        MultiAgentScenario(
            name="edge_empty_agents",
            agent_count=0,
            agents={},
            description="空agents字典",
            metadata={"edge_type": "empty_input"},
        )
    )

    scenarios.append(
        MultiAgentScenario(
            name="edge_single_agent",
            agent_count=1,
            agents=generate_agents(1),
            description="单agent场景（无竞争）",
            expected_winner="agent",
            metadata={"edge_type": "single_agent"},
        )
    )

    scenarios.append(
        MultiAgentScenario(
            name="edge_all_tie_5",
            agent_count=5,
            agents=generate_tie_scenario(5),
            description="5个agent完全平局（优先级和负载都相同）",
            metadata={"edge_type": "tie_breaking"},
        )
    )

    scenarios.append(
        MultiAgentScenario(
            name="edge_all_tie_10",
            agent_count=10,
            agents=generate_tie_scenario(10),
            description="10个agent完全平局",
            metadata={"edge_type": "tie_breaking"},
        )
    )

    scenarios.append(
        MultiAgentScenario(
            name="edge_large_scale_50",
            agent_count=50,
            agents=generate_agents(50, load_strategy="ascending"),
            description="50个agent大规模场景",
            metadata={"edge_type": "large_scale"},
        )
    )

    scenarios.append(
        MultiAgentScenario(
            name="edge_large_scale_100",
            agent_count=100,
            agents=generate_agents(100, load_strategy="extremes"),
            description="100个agent超大规模场景",
            expected_winner="agent_99",
            metadata={"edge_type": "large_scale"},
        )
    )

    for malformed_type in [
        "missing_priority",
        "missing_load",
        "missing_capabilities",
        "negative_priority",
        "negative_load",
        "load_over_100",
        "empty_capabilities",
        "mixed_roles",
        "extreme_priority_range",
    ]:
        scenarios.append(
            MultiAgentScenario(
                name=f"edge_malformed_{malformed_type}",
                agent_count=3,
                agents=generate_malformed_agents(malformed_type, base_count=3),
                description=f"畸形数据: {malformed_type}",
                metadata={"edge_type": "malformed", "variant": malformed_type},
            )
        )

    scenarios.append(
        MultiAgentScenario(
            name="edge_partial_capability_match",
            agent_count=5,
            agents=generate_partial_capability_match(5, "design", matching_count=2),
            description="5个agent中仅2个具备所需能力",
            metadata={"edge_type": "partial_match", "required_cap": "design"},
        )
    )

    scenarios.append(
        MultiAgentScenario(
            name="edge_no_capability_match",
            agent_count=5,
            agents=generate_partial_capability_match(5, "architecture", matching_count=0),
            description="5个agent中无人具备所需能力",
            metadata={"edge_type": "no_match", "required_cap": "architecture"},
        )
    )

    scenarios.append(
        MultiAgentScenario(
            name="edge_all_capability_match",
            agent_count=10,
            agents=generate_agents(10, capabilities=["coding", "design"]),
            description="10个agent全部具备所需能力",
            metadata={"edge_type": "all_match"},
        )
    )

    return scenarios

