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

VALID_MATURITY_LEVELS = {"L1", "L2", "L3", "L4"}

WHY_EXPLANATION_PATTERN = re.compile(r">\s*\*\*为什么", re.MULTILINE)
CHECKLIST_ITEM_PATTERN = re.compile(r"^- \[ \]", re.MULTILINE)
SECTION_HEADER_PATTERN = re.compile(r"^##\s+(.+)$", re.MULTILINE)
MERMAID_PATTERN = re.compile(r"```mermaid", re.MULTILINE)
CROSS_REFERENCE_PATTERN = re.compile(r"(?:\[[^\]]*\]\(|<a[^>]*>|`)([^)`\s]+\.md)(?:\)|</a>|`)", re.MULTILINE)
ID_PATTERN = re.compile(r"^pattern-[a-z0-9-]+$")
