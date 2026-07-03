import re

SKILLS_DIR = ".agents/skills"
MAX_SKILL_LINES = 500
MIN_DESCRIPTION_LENGTH = 50
RECOMMENDED_DESCRIPTION_LENGTH = 150

FRONTMATTER_REQUIRED_FIELDS = {"name", "description"}
FRONTMATTER_RECOMMENDED_FIELDS = {"version", "argument-hint", "user-invocable", "paths"}

OPEN_STANDARD_ALLOWED_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
OPEN_STANDARD_MAX_NAME_LENGTH = 64
OPEN_STANDARD_MAX_DESCRIPTION_LENGTH = 1024
OPEN_STANDARD_MIN_DESCRIPTION_LENGTH_FOR_STANDARD = 20
OPEN_STANDARD_OPTIONAL_DIRS = ["scripts", "references", "assets", "evals"]

MANDATORY_TRIGGER_PHRASES = ["必须使用", "Use this skill", "必须", "MUST use"]
WRITE_OPERATION_KEYWORDS = ["编辑", "创建", "删除", "发布", "更新", "写", "edit", "create", "delete", "post", "update", "write"]
DRY_RUN_KEYWORDS = ["dry-run", "dry_run", "dryrun", "预览", "试运行", "预演", "预检", "预检查", "预提交", "质量门"]
IDEMPOTENT_KEYWORDS = ["幂等", "idempotent", "重复检查", "已存在", "skipped", "验证结果", "无遗漏", "无残留", "收尾验证", "无断链", "已更新"]
POST_VERIFY_PATTERN = re.compile(r"步骤\d+[：:].*(?:验证|确认|检查)", re.MULTILINE)
CHECKLIST_VERIFY_PATTERN = re.compile(r"^- \[ \].*(?:已验证|已确认|已检查|已更新|已完成|已区分|已明确|无断链|无遗漏|无残留|更新了)", re.MULTILINE)
CONFIRMATION_KEYWORDS = ["确认", "confirm", "获得.*确认", "用户确认"]
WHY_EXPLANATION_PATTERN = re.compile(r">\s*\*\*为什么", re.MULTILINE)
DECISION_TREE_PATTERNS = [
    re.compile(r"决策树", re.MULTILINE),
    re.compile(r"方案选择", re.MULTILINE),
    re.compile(r"├─", re.MULTILINE),
    re.compile(r"└─", re.MULTILINE),
    re.compile(r"flowchart", re.MULTILINE),
]
SAFETY_CHECKLIST_PATTERN = re.compile(r"安全检查清单|检查清单.*逐项", re.MULTILINE)
CHECKLIST_ITEM_PATTERN = re.compile(r"^- \[ \]", re.MULTILINE)
