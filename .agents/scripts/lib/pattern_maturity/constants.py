"""模式成熟度工具 - 常量定义。"""

DOMAIN_LABELS = {
    'architecture': '架构',
    'code': '代码',
    'methodology': '方法论',
    'other': '其他',
}

CATEGORY_LABELS = {
    'methodology': '方法论模式',
    'architecture': '架构模式',
    'code': '代码模式',
    'other': '其他',
}

STATUS_ICONS = {
    'upgrade': '[UP]',
    'anomaly': '[!!]',
    'ok': '[OK]',
}

DOMAIN_ORDER = ['methodology', 'code', 'architecture']

UPGRADE_THRESHOLD = 2
ANOMALY_THRESHOLD = 1
