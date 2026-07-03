"""MDI验证器常量定义。

包含正则表达式模式、阈值限制等配置常量。
"""

import re

NAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]*[a-z0-9]$|^[a-z]$")
MAX_NAME_LENGTH = 64
MIN_DESCRIPTION_LENGTH = 20
MAX_DESCRIPTION_LENGTH = 1024
MAX_SKILL_LINES_WARN = 500
MAX_SKILL_LINES_ERROR = 1000

WHY_EXPLANATION_PATTERN = re.compile(r">\s*\*\*为什么", re.MULTILINE)
MUST_RULE_PATTERN = re.compile(r"\*\*(?:MUST|必须|禁止|严禁|不得|不要|NEVER|SHOULD NOT|SHALL NOT)", re.MULTILINE)
CHECKLIST_ITEM_PATTERN = re.compile(r"^- \[ \]", re.MULTILINE)
FILE_URL_RE = re.compile(r"file:///([A-Za-z]:/[^\s)]+|/[^\s)]+)", re.MULTILINE)
INLINE_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

DECISION_TREE_PATTERNS = [
    re.compile(r"决策树", re.MULTILINE),
    re.compile(r"方案选择", re.MULTILINE),
    re.compile(r"flowchart", re.MULTILINE),
    re.compile(r"├─", re.MULTILINE),
    re.compile(r"└─", re.MULTILINE),
]
SAFETY_CHECKLIST_PATTERN = re.compile(r"安全检查清单|安全清单|检查清单", re.MULTILINE)

WRITE_OPERATION_KEYWORDS = (
    "编辑", "创建", "删除", "发布", "更新", "写",
    "edit", "create", "delete", "post", "update", "write",
    "提交", "修复", "拆分", "移动", "生成",
)
MANDATORY_TRIGGER_PHRASES = ("必须使用", "Use this skill", "MUST use")

ERROR_SCORE_PENALTY = 15
WARN_SCORE_PENALTY = 5
INFO_SCORE_PENALTY = 1
