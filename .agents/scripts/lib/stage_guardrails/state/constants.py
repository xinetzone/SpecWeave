"""阶段状态管理器常量定义。"""

from __future__ import annotations

STAGE_ORDER: dict[str, int] = {
    'S1': 1, 'S2': 2, 'S3': 3, 'S4': 4,
    'S5': 5, 'S6': 6, 'S7': 7, 'S8': 8,
}

STAGE_NAMES: dict[str, str] = {
    'S1': '需求接收', 'S2': '方案设计', 'S3': '任务分配', 'S4': '代码实现',
    'S5': '测试编写', 'S6': '代码审查', 'S7': '合并代码', 'S8': '完成确认',
}

VALID_ROLES: set[str] = {'orchestrator', 'architect', 'developer', 'tester', 'reviewer'}

STAGE_ROLES: dict[str, set[str]] = {
    'S1': {'orchestrator'},
    'S2': {'architect'},
    'S3': {'orchestrator'},
    'S4': {'developer'},
    'S5': {'tester'},
    'S6': {'reviewer'},
    'S7': {'orchestrator'},
    'S8': {'orchestrator'},
}
