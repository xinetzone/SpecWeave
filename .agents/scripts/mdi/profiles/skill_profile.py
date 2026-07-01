"""Skill Profile：AI Agent Skill规范。

兼容现有SKILL.md实践，定义AI Agent可调用能力的结构要求。
必填Frontmatter仅name和description，其余为推荐字段。
章节使用关键词模糊匹配，不要求精确章节名。
"""

from dataclasses import dataclass, field
from pathlib import Path
import re

from .base import BaseProfile, SectionPattern, ProfileValidationResult
from ..models import MDIDocument


SKILL_SECTION_PATTERNS: tuple[SectionPattern, ...] = (
    SectionPattern(
        key="description",
        keywords=("功能描述", "描述", "description", "概述", "skillid", "skill id"),
        required=False,
    ),
    SectionPattern(
        key="when_to_use",
        keywords=("何时使用", "触发条件", "使用场景", "whentouse", "when to use", "触发"),
        required=False,
    ),
    SectionPattern(
        key="decision_tree",
        keywords=("决策树", "方案选择", "decision", "选型", "flowchart"),
        required=False,
    ),
    SectionPattern(
        key="core_steps",
        keywords=("核心步骤", "核心命令", "快速开始", "使用方法", "howtouse", "步骤", "命令"),
        required=False,
    ),
    SectionPattern(
        key="safety_checklist",
        keywords=("安全检查清单", "安全清单", "检查清单", "safety", "checklist", "确认清单"),
        required=False,
    ),
    SectionPattern(
        key="gotchas",
        keywords=("陷阱", "gotchas", "常见问题", "注意事项", "常见陷阱"),
        required=False,
    ),
)


@dataclass
class SkillProfile(BaseProfile):
    """AI Agent Skill Profile。

    必填Frontmatter: name, description
    推荐Frontmatter: version, argument-hint, user-invocable, paths
    所有章节均为推荐（使用关键词模糊匹配）。
    """

    profile_type: str = "skill"

    required_frontmatter: set[str] = field(
        default_factory=lambda: {"name", "description"}
    )
    recommended_frontmatter: set[str] = field(
        default_factory=lambda: {"version", "argument-hint", "user-invocable", "paths"}
    )

    section_patterns: tuple[SectionPattern, ...] = SKILL_SECTION_PATTERNS

    MANDATORY_PHRASES: tuple[str, ...] = ("必须使用", "Use this skill", "MUST use")
    WRITE_OPERATION_KEYWORDS: tuple[str, ...] = (
        "编辑", "创建", "删除", "发布", "更新", "写",
        "edit", "create", "delete", "post", "update", "write",
        "提交", "修复", "拆分", "移动", "生成",
    )

    def get_write_operation_keywords(self) -> tuple[str, ...]:
        return self.WRITE_OPERATION_KEYWORDS
