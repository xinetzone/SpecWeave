"""sg-dashboard 常量定义。

包含日志正则、阶段顺序、阶段名称、SG事件集合等常量。
"""

import re

LOG_LINE_RE = re.compile(
    r'\[(SG-LOG|PDR-LOG)\]\s*\|\s*'
    r'level=(\w+)\s*\|\s*'
    r'event=(\w+)\s*\|\s*'
    r'stage=(\w+)\s*\|\s*'
    r'role=(\w+)\s*\|\s*'
    r'session=([^|]+?)\s*\|\s*'
    r'msg=([^|]+?)(?:\s*\|\s*ctx=(.+))?$'
)

STAGE_ORDER = {'S1': 1, 'S2': 2, 'S3': 3, 'S4': 4, 'S5': 5, 'S6': 6, 'S7': 7, 'S8': 8}

STAGE_NAMES = {
    'S1': '需求接收', 'S2': '方案设计', 'S3': '任务分配', 'S4': '代码实现',
    'S5': '测试编写', 'S6': '代码审查', 'S7': '合并代码', 'S8': '完成确认',
    'NONE': '无活跃阶段',
}

SG_EVENTS = {
    'STAGE_ENTER', 'STAGE_EXIT', 'DOC_CHECK', 'PDR_CONFIRM',
    'BOUNDARY_CHECK', 'BOUNDARY_PASS', 'INTERCEPT', 'BYPASS_DETECTED',
    'JUMP_REQUEST', 'JUMP_APPROVED', 'JUMP_REJECTED', 'ERROR',
}
