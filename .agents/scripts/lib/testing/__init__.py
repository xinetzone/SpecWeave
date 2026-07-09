"""测试辅助工具库。

提供边界场景测试模板、参数化测试fixture、多智能体边缘场景生成器。
专为仲裁/调度类并发模块设计，覆盖正常场景、边界场景、异常输入场景。
"""

from .multi_agent import (
    generate_agents,
    agent_scenarios,
    edge_scenarios,
    generate_malformed_agents,
    generate_tie_scenario,
    generate_partial_capability_match,
    MultiAgentScenario,
    parametrize_agent_counts,
    BOUNDARY_AGENT_COUNTS,
    EXTREME_AGENT_COUNTS,
    BOUNDARY_ASSERTIONS,
)

__all__ = [
    "generate_agents",
    "agent_scenarios",
    "edge_scenarios",
    "generate_malformed_agents",
    "generate_tie_scenario",
    "generate_partial_capability_match",
    "MultiAgentScenario",
    "parametrize_agent_counts",
    "BOUNDARY_AGENT_COUNTS",
    "EXTREME_AGENT_COUNTS",
    "BOUNDARY_ASSERTIONS",
]
