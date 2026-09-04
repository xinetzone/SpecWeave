# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

import re

# spec 匹配阈值（用于 check 子命令的语义匹配）
SPEC_MATCH_THRESHOLD = 1

# ============================================================
# status 合法值域（以 TRAE-spec-mode Skill 为权威）
# ============================================================
VALID_STATUSES: set[str] = {
    "draft",
    "planning",
    "in-progress",
    "approved",
    "implemented",
    "completed",
    "pending-approval",
    "review",
    "deprecated",
    "archived",
}

# ============================================================
# 非法 status → 合法 status 的归一化映射
# ============================================================
# 新增非法值时在这里补充映射即可，自动被 format --fix-status 消费
STATUS_NORMALIZATION_MAP: dict[str, str] = {
    "complete": "completed",
    "awaiting-approval": "pending-approval",
    "in_progress": "in-progress",
    "proposed": "draft",
    "candidate": "draft",
    "pending": "draft",
    "done": "completed",
    "active": "in-progress",
    "wip": "in-progress",
    "todo": "draft",
    "to-do": "draft",
    "approved-pending": "pending-approval",
}

# ============================================================
# spec 三件套文件名
# ============================================================
SPEC_TRIPLET: list[str] = ["spec.md", "tasks.md", "review.md"]
SPEC_TRIPLET_LEGACY_CHECKLIST: str = "checklist.md"  # 已废止，统一用 review.md

# ============================================================
# frontmatter 相关正则
# ============================================================
# YAML frontmatter 起始
YAML_FM_START_RE = re.compile(r"^---[ \t]*\r?\n")
# YAML frontmatter 闭合
YAML_FM_CLOSE_RE = re.compile(r"^---[ \t]*\r?$", re.MULTILINE)

# TOML frontmatter 起始（必须在文件最开头或紧跟前导空白后，即 lstrip 后）
TOML_FM_START_RE = re.compile(r"^\+\+\+[ \t]*\r?\n")
# TOML frontmatter 闭合
TOML_FM_CLOSE_RE = re.compile(r"^\+\+\+[ \t]*\r?$", re.MULTILINE)

# 从 frontmatter body 中提取 status 行（YAML / TOML）
# 允许前导空白（indent），值部分用非贪婪匹配，行尾只匹配水平空白避免吃掉换行符
STATUS_LINE_YAML_RE = re.compile(r"^[ \t]*status\s*:\s*(.+?)[ \t]*$", re.MULTILINE)
STATUS_LINE_TOML_RE = re.compile(r"^[ \t]*status\s*=\s*(.+?)[ \t]*$", re.MULTILINE)

# 从正文提取 H1 标题
H1_TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)

# ============================================================
# 旧常量（test_gen.py 等依赖，保留以兼容）
# ============================================================
_REQ_SEC_RE = re.compile(r"^##\s+(ADDED|MODIFIED|REMOVED)\s+Requirements?", re.IGNORECASE)
_REQ_HDR_RE = re.compile(r"^###\s+Requirement:\s+(.+)")
_SCN_HDR_RE = re.compile(r"^####\s+Scenario:\s+(.+)")

__all__ = [
    "SPEC_MATCH_THRESHOLD",
    "VALID_STATUSES",
    "STATUS_NORMALIZATION_MAP",
    "SPEC_TRIPLET",
    "SPEC_TRIPLET_LEGACY_CHECKLIST",
    "YAML_FM_START_RE",
    "YAML_FM_CLOSE_RE",
    "TOML_FM_START_RE",
    "TOML_FM_CLOSE_RE",
    "STATUS_LINE_YAML_RE",
    "STATUS_LINE_TOML_RE",
    "H1_TITLE_RE",
    # 旧常量（test_gen.py 等依赖）
    "_REQ_SEC_RE",
    "_REQ_HDR_RE",
    "_SCN_HDR_RE",
]
