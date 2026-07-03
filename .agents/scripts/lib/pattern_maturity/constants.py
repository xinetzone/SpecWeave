"""模式成熟度工具 - 常量定义。"""

import re

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

REQUIRED_FIELDS = [
    'id',
    'domain',
    'layer',
    'maturity',
    'validation_count',
    'reuse_count',
    'documentation_level',
    'source',
]

MATURITY_LEVELS = ['L1', 'L2', 'L3', 'L4']

PATTERN_DOMAINS = ['methodology-patterns', 'code-patterns', 'architecture-patterns']

EXCLUDED_FILENAMES = {'README.md', 'CATEGORIES.md'}

PATTERNS_DIR = 'docs/retrospective/patterns'

README_STATS_TABLE_RE = re.compile(
    r"^\|\s*\**([\w/-]+?)\**\s*\|\s*\**(\d+)\**\s*\|\s*\**(\d+)\**\s*\|\s*\**(\d+)\**\s*\|\s*\**(\d+)\**\s*\|\s*\**(\d+)\**\s*\|",
    re.MULTILINE,
)

README_INDEX_TABLE_RE = re.compile(
    r"\|\s*(\S+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|"
)
