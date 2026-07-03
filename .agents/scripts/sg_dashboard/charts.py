"""sg-dashboard Mermaid图表生成模块。

提供事件分布饼图和阶段拦截对比柱状图生成。
"""

from __future__ import annotations

from collections import Counter

from .constants import STAGE_NAMES, STAGE_ORDER


def generate_mermaid_pie(event_counts: Counter) -> str:
    """生成事件类型分布Mermaid饼图。"""
    top_events = event_counts.most_common(8)
    lines = ['pie title SG-LOG 事件类型分布']
    for event, count in top_events:
        lines.append(f'    "{event}" : {count}')
    return '\n'.join(lines)


def generate_mermaid_bar_chart(stage_intercept: dict, stage_pass: dict) -> str:
    """生成各阶段操作拦截/放行对比Mermaid xychart。"""
    stages_sorted = sorted(
        set(list(stage_intercept.keys()) + list(stage_pass.keys())),
        key=lambda s: STAGE_ORDER.get(s, 99),
    )
    if not stages_sorted:
        return 'pie title 暂无数据\n    "无数据" : 1'

    x_labels = ', '.join(f'"{STAGE_NAMES.get(s, s)}"' for s in stages_sorted)
    pass_vals = [stage_pass.get(s, 0) for s in stages_sorted]
    intercept_vals = [stage_intercept.get(s, 0) for s in stages_sorted]
    max_val = max((p + i for p, i in zip(pass_vals, intercept_vals)), default=1)
    lines = ['xychart-beta', '    title "各阶段操作拦截/放行对比"',
             f'    x-axis [{x_labels}]',
             f'    y-axis "操作次数" 0 --> {max_val + 2}',
             f'    bar [{", ".join(str(v) for v in pass_vals)}]',
             f'    bar [{", ".join(str(v) for v in intercept_vals)}]']
    return '\n'.join(lines)
