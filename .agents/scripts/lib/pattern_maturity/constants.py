"""模式成熟度工具 - 常量定义。"""


# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

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

# 排除非模式内容文件：
# - README.md：目录说明（统计表载体，单独走 verify 校验）
# - CATEGORIES.md：分类元数据
# - index.md：docgen/check-index 自动生成的导航索引，FM 规则明确"子目录 index.md 禁 FM"
# - log.md：模式库变更日志（changelog），非模式条目
EXCLUDED_FILENAMES = {'README.md', 'CATEGORIES.md', 'index.md', 'log.md'}

PATTERNS_DIR = 'docs/retrospective/patterns'

README_STATS_TABLE_RE = re.compile(
    r"^\|\s*\**([\w/-]+?)\**\s*\|\s*\**(\d+)\**\s*\|\s*\**(\d+)\**\s*\|\s*\**(\d+)\**\s*\|\s*\**(\d+)\**\s*\|\s*\**(\d+)\**\s*\|",
    re.MULTILINE,
)

README_INDEX_TABLE_RE = re.compile(
    r"\|\s*(\S+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|"
)

