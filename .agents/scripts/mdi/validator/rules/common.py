"""通用MDI验证规则。

提供frontmatter、名称格式、描述长度、强制措辞、章节结构、文件长度、Why解释等通用验证。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..constants import (
    NAME_PATTERN, MAX_NAME_LENGTH, MIN_DESCRIPTION_LENGTH, MAX_DESCRIPTION_LENGTH,
    MAX_SKILL_LINES_WARN, MAX_SKILL_LINES_ERROR,
    WHY_EXPLANATION_PATTERN, MUST_RULE_PATTERN, MANDATORY_TRIGGER_PHRASES,
    DECISION_TREE_PATTERNS,
)
from ..models import ValidationReport
from ...profiles import BaseProfile, SkillProfile

if TYPE_CHECKING:
    from ...models import MDIDocument


def validate_frontmatter(doc: "MDIDocument", profile: BaseProfile, report: ValidationReport) -> None:
    """验证必填和推荐frontmatter字段。"""
    fm = doc.frontmatter

    for field_name in sorted(profile.required_frontmatter):
        value = fm.get(field_name)
        if value is None or (isinstance(value, str) and len(value.strip()) == 0):
            report.add_issue(
                "error", "E001",
                f"缺少必填frontmatter字段: '{field_name}'",
                suggestion=f"在frontmatter中添加 '{field_name}' 字段",
            )

    for field_name in sorted(profile.recommended_frontmatter):
        value = fm.get(field_name)
        if value is None:
            report.add_issue(
                "warn", "W001",
                f"缺少推荐frontmatter字段: '{field_name}'",
                suggestion=f"建议添加 '{field_name}' 字段以提高文档完整性",
            )


def validate_name_format(doc: "MDIDocument", report: ValidationReport) -> None:
    """验证name字段的kebab-case格式。"""
    name = doc.frontmatter.get("name", "")
    if not name or not isinstance(name, str):
        return

    issues = []
    if len(name) > MAX_NAME_LENGTH:
        issues.append(f"长度{len(name)}超过上限{MAX_NAME_LENGTH}字符")
    if name != name.lower():
        issues.append("包含大写字符（应为kebab-case小写）")
    if name.startswith("-"):
        issues.append("以连字符开头")
    if name.endswith("-"):
        issues.append("以连字符结尾")
    if "--" in name:
        issues.append("包含连续连字符")
    if "_" in name:
        issues.append("包含下划线（应使用连字符-）")
    invalid_chars = [c for c in name if not (c.isalnum() or c == "-")]
    if invalid_chars:
        issues.append(f"包含无效字符: {''.join(set(invalid_chars))}（仅允许字母、数字、连字符）")
    if name and not NAME_PATTERN.match(name):
        if not issues:
            issues.append("不符合kebab-case格式")

    if issues:
        report.add_issue(
            "error", "E002",
            f"name字段格式不合法: {'; '.join(issues)}",
            suggestion="name应为kebab-case格式（小写字母、数字、连字符，不以连字符开头/结尾）",
        )


def validate_description_length(doc: "MDIDocument", report: ValidationReport) -> None:
    """验证description字段长度。"""
    desc = doc.frontmatter.get("description", "")
    if not desc or not isinstance(desc, str):
        return

    desc_len = len(desc)
    if desc_len < MIN_DESCRIPTION_LENGTH:
        report.add_issue(
            "warn", "W002",
            f"description过短（{desc_len}字符），建议≥{MIN_DESCRIPTION_LENGTH}字符以明确功能",
            suggestion="补充功能描述和触发场景说明",
        )
    elif desc_len > MAX_DESCRIPTION_LENGTH:
        report.add_issue(
            "warn", "W002",
            f"description过长（{desc_len}字符），超过硬限制{MAX_DESCRIPTION_LENGTH}字符",
            suggestion="精简description，将详细内容移到正文章节",
        )


def validate_mandatory_phrase(doc: "MDIDocument", profile: BaseProfile, report: ValidationReport) -> None:
    """验证Skill description包含强制触发措辞。"""
    if not isinstance(profile, SkillProfile):
        return

    desc = doc.frontmatter.get("description", "")
    if not desc or not isinstance(desc, str):
        return

    has_mandatory = any(phrase in desc for phrase in MANDATORY_TRIGGER_PHRASES)
    if not has_mandatory:
        report.add_issue(
            "error", "E003",
            "Skill description缺少强制触发措辞",
            suggestion="description应包含'必须使用此技能'、'Use this skill'或'MUST use'等强制触发措辞，避免undertrigger",
        )


def validate_sections(doc: "MDIDocument", profile: BaseProfile, content: str, report: ValidationReport) -> None:
    """验证推荐章节结构（如决策树）。"""
    recommended_section_keys = {
        "decision_tree": ("决策树/方案选择章节", "建议添加决策树或方案选择章节，帮助用户选择正确的操作路径"),
    }

    for sp in profile.section_patterns:
        if sp.key in recommended_section_keys:
            label, suggestion = recommended_section_keys[sp.key]
            found = profile.find_sections_by_key(doc, sp.key)
            has_tree_content = any(p.search(content) for p in DECISION_TREE_PATTERNS)
            if not found and not has_tree_content and sp.key == "decision_tree":
                has_multi_scheme = content.count("方案一") + content.count("方案二") >= 2
                if has_multi_scheme:
                    report.add_issue(
                        "warn", "W003",
                        f"缺少{label}（检测到多方案描述）",
                        suggestion=suggestion,
                    )


def validate_file_length(content: str, profile: BaseProfile, report: ValidationReport) -> None:
    """验证文件长度（Skill文件建议≤500行）。"""
    lines = content.count("\n") + 1

    if isinstance(profile, SkillProfile):
        if lines > MAX_SKILL_LINES_ERROR:
            report.add_issue(
                "warn", "W004",
                f"文件过长（{lines}行），严重超过{MAX_SKILL_LINES_WARN}行建议",
                suggestion="考虑使用references/子文档进行渐进式披露，将低频内容拆分出去",
            )
        elif lines > MAX_SKILL_LINES_WARN:
            report.add_issue(
                "warn", "W004",
                f"文件超过{MAX_SKILL_LINES_WARN}行建议（当前{lines}行）",
                suggestion="渐进式披露原则：考虑将详细参考内容移到references/子文档",
            )


def validate_why_explanations(content: str, report: ValidationReport) -> None:
    """验证关键MUST规则后是否有Why解释。"""
    why_count = len(WHY_EXPLANATION_PATTERN.findall(content))
    must_count = len(MUST_RULE_PATTERN.findall(content))

    if must_count >= 3 and why_count < 2:
        report.add_issue(
            "warn", "W005",
            f"Why解释不足：关键MUST类规则{must_count}个，但Why解释仅{why_count}个",
            suggestion="在关键MUST规则后添加 '> **为什么...**' 引用块解释设计意图，帮助理解边界情况",
        )
