"""七概念方法论触发匹配工具包。

提供基于自然语言任务描述自动匹配方法论概念组合的能力：
- match_task(text): 根据任务文本返回匹配场景列表
- format_match_result(result): 格式化单个匹配结果为可读字符串
- format_scenario_list(): 返回所有支持场景的列表文本
- format_match_result_dict(result): 转为dict（用于JSON序列化）

典型用法：
    from lib.seven_concepts import match_task, format_match_result

    results = match_task("Sprint结束做复盘")
    print(format_match_result(results[0]))
"""

from .constants import (
    ANTI_PATTERN_WARNINGS,
    CONCEPTS,
    QUALITY_GATES,
    WORKFLOWS,
)
from .models import MatchResult
from .matcher import match_task
from .scenarios import get_all_scenarios
from .formatters import (
    format_match_result,
    format_match_result_dict,
    format_scenario_list,
)

__all__ = [
    "ANTI_PATTERN_WARNINGS",
    "CONCEPTS",
    "QUALITY_GATES",
    "WORKFLOWS",
    "MatchResult",
    "match_task",
    "get_all_scenarios",
    "format_match_result",
    "format_match_result_dict",
    "format_scenario_list",
]
