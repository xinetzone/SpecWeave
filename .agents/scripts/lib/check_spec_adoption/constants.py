import re

from lib.frontmatter import _YAML_FRONTMATTER_RE

FM_PATTERN = _YAML_FRONTMATTER_RE
REQUIRED_CORE_FIELDS = {'id', 'x-toml-ref'}
FORBIDDEN_EXTERNAL_FIELDS = {'category', 'date', 'tags', 'version', 'changelog'}
PATTERN_LINK_RE = re.compile(r'\]\(([^)]*?/patterns/[^)]+\.md)\)')
LARGE_FILE_THRESHOLD = 300

FENCED_CODE_BLOCK_RE = re.compile(r'```.*?```', re.DOTALL)
INLINE_CODE_RE = re.compile(r'`[^`]+`')
PLACEHOLDER_RE = re.compile(r'[{}<>]|\{\{|\}\}')

BATCH_DEFAULT_TARGETS = [
    ('.agents/', 'specs'),
    ('.agents/scripts/', 'code'),
    ('docs/', 'docs'),
]

PROFILES = {
    'docs': {
        'description': '文档区（默认）- 适用于docs/等内容文档目录',
        'weights': {
            'frontmatter_compliance': 0.25,
            'link_validity': 0.25,
            'source_traceability': 0.20,
            'pattern_reference_rate': 0.15,
            'nav_link_compliance': 0.15,
        },
        'default_exclude_dirs': set(),
        'default_exclude_files': set(),
    },
    'specs': {
        'description': '规范区 - 适用于.agents/等规范定义目录（模式引用/导航降权，排除专用schema文件）',
        'weights': {
            'frontmatter_compliance': 0.35,
            'link_validity': 0.30,
            'source_traceability': 0.25,
            'pattern_reference_rate': 0.05,
            'nav_link_compliance': 0.05,
        },
        'default_exclude_dirs': {'skills', 'scripts/mdi/examples'},
        'default_exclude_files': {'SKILL.md', 'ONBOARDING.md', 'SKILL-TEMPLATE.md', 'ONBOARDING-TEMPLATE.md', 'REGISTRY-TEMPLATE.md', 'capability-registry.md'},
    },
    'code': {
        'description': '代码区 - 适用于scripts/等工具脚本目录（frontmatter降权，链接升权）',
        'weights': {
            'frontmatter_compliance': 0.10,
            'link_validity': 0.40,
            'source_traceability': 0.10,
            'pattern_reference_rate': 0.25,
            'nav_link_compliance': 0.05,
            'large_file_ratio_inverted': 0.10,
        },
        'default_exclude_dirs': {'__pycache__', '.pytest_cache', 'mdi/examples'},
        'default_exclude_files': set(),
    },
}

FM_ISSUE_NAMES = {
    'missing_id': '缺少id字段',
    'missing_xref': '缺少x-toml-ref',
    'has_forbidden_fields': '包含应外部化字段',
    'has_nested': '存在嵌套结构',
    'bloated_fm': 'frontmatter膨胀(>15行)',
}

FM_ISSUE_NAMES_SHORT = {
    'missing_id': '缺id',
    'missing_xref': '缺xref',
    'has_forbidden_fields': '字段未外部化',
    'has_nested': '嵌套结构',
    'bloated_fm': 'FM膨胀',
}

NAV_PATTERNS = ['上一章', '下一章', '返回目录', 'prev', 'next', '返回索引']
