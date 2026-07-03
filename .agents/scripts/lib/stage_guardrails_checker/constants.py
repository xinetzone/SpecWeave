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

SG_EVENTS = {
    'STAGE_ENTER', 'DOC_CHECK', 'DOC_READ', 'DOC_MISSING',
    'BOUNDARY_CHECK', 'BOUNDARY_PASS', 'INTERCEPT', 'BYPASS_DETECTED',
    'JUMP_REQUEST', 'JUMP_APPROVED', 'JUMP_REJECTED', 'STAGE_EXIT', 'ERROR',
    'PDR_CONFIRM',
}

PDR_EVENTS = {
    'PDR_START', 'PDR_DOC_READ', 'PDR_DOC_SKIP', 'PDR_DOC_MISSING',
    'PDR_DOC_REQ_GAP', 'PDR_CONFIRM', 'PDR_ERROR',
}

SG_LEVELS = {'DEBUG', 'INFO', 'WARN', 'ERROR'}

STAGE_ORDER = {'S1': 1, 'S2': 2, 'S3': 3, 'S4': 4, 'S5': 5, 'S6': 6, 'S7': 7, 'S8': 8}
STAGE_NAMES = {
    'S1': '需求接收', 'S2': '方案设计', 'S3': '任务分配', 'S4': '代码实现',
    'S5': '测试编写', 'S6': '代码审查', 'S7': '合并代码', 'S8': '完成确认',
}

ERROR_TYPES = {'UNAUTHORIZED_JUMP', 'CRITICAL_DOC_MISSING', 'VIOLATION_EXECUTED',
               'INVALID_STATE', 'APPROVAL_CONFLICT', 'CRITICAL_MISSING', 'PARSE_ERROR',
               'PERMISSION_DENIED', 'CIRCULAR_REF', 'GOVERNANCE_LAYER_SKIP'}

GOVERNANCE_LAYERS = {
    'B1': {'name': '规范定义', 'order': 1},
    'B2': {'name': '离线检测', 'order': 2},
    'C1': {'name': '运行时拦截', 'order': 3},
    'C2': {'name': '可视化仪表盘', 'order': 4},
}

GOVERNANCE_KEYWORDS = {
    'B1': ['规范', '规则', '标准', '指南', 'policy', 'rule', 'standard', 'guideline'],
    'B2': ['检测', '检查', '扫描', '静态分析', 'check', 'detect', 'scan', 'lint', '离线'],
    'C1': ['拦截', '阻断', '运行时', '强制执行', 'intercept', 'block', 'runtime', 'enforce'],
    'C2': ['可视化', '仪表盘', '报表', '统计', 'dashboard', 'visualize', 'report', 'metric'],
}