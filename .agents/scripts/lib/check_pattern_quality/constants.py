# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

import re

PATTERNS_DIR = ".agents/docs/retrospective/patterns"
MIN_PATTERN_LINES = 50
MAX_PATTERN_LINES = 400
RECOMMENDED_MIN_LINES = 80
RECOMMENDED_MAX_LINES = 300

FRONTMATTER_REQUIRED_FIELDS = {"id", "domain", "layer", "maturity", "source"}
FRONTMATTER_RECOMMENDED_FIELDS = {"validation_count", "reuse_count", "documentation_level"}

REQUIRED_SECTIONS = {
    "模式类型": "pattern_type",
    "成熟度": "maturity",
    "适用场景": "applicable_scenarios",
    "问题背景": "problem_background",
}

RECOMMENDED_SECTIONS = {
    "核心规则": "core_rules",
    "核心要素": "core_elements",
    "解决方案": "solution",
    "核心内容": "core_content",
    "操作流程": "workflow",
    "决策速查": "decision_cheatsheet",
}

IMPORTANT_SECTIONS = {
    "实施检查清单": "checklist",
    "反例警示": "anti_patterns",
    "正例": "positive_examples",
    "与现有模式的关系": "related_patterns",
}

INNOVATION_PATTERN_SECTIONS = {
    "失败案例": "failure_cases",
    "反目标": "anti_target",
    "早期预警": "warning_signals",
    "边界": "boundaries",
}

VALID_MATURITY_LEVELS = {"L1", "L2", "L3", "L4"}

INNOVATION_TYPE_KEYWORDS = re.compile(
    r"(创新|跨领域|迁移|逆向适配|方法论模式|创新设计|反向|反直觉|跨界)",
    re.MULTILINE,
)

FAILURE_CASE_PATTERN = re.compile(
    r"(失败案例|反面案例|失败教训|失败警示|负面案例|反噬|事故|被罚款|失败根因)",
    re.MULTILINE,
)

ANTI_TARGET_PATTERN = re.compile(
    r"(反目标|不适用|不适合|不推荐.*场景|对.*无效|对.*有害|边界场景|反目标用户|反目标场景|哪些人|哪些场景)",
    re.MULTILINE,
)

WARNING_SIGNAL_PATTERN = re.compile(
    r"(预警信号|早期预警|警告信号|警示信号|危险信号|何时不该|红旗|red\s*flag)",
    re.IGNORECASE | re.MULTILINE,
)

WHY_EXPLANATION_PATTERN = re.compile(r">\s*\*\*为什么", re.MULTILINE)
CHECKLIST_ITEM_PATTERN = re.compile(r"^- \[ \]", re.MULTILINE)
SECTION_HEADER_PATTERN = re.compile(r"^##\s+(.+)$", re.MULTILINE)
MERMAID_PATTERN = re.compile(r"```mermaid", re.MULTILINE)
CROSS_REFERENCE_PATTERN = re.compile(r"(?:\[[^\]]*\]\(|<a[^>]*>|`)([^)`\s]+\.md)(?:\)|</a>|`)", re.MULTILINE)
ID_PATTERN = re.compile(r"^pattern-[a-z0-9-]+$")

