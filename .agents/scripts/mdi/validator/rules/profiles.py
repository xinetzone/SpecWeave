"""Profile特定验证规则。

包含Skill、WebApi、CliTool三种Profile的专属验证规则。
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ..constants import (
    CHECKLIST_ITEM_PATTERN, SAFETY_CHECKLIST_PATTERN, WRITE_OPERATION_KEYWORDS,
)
from ..models import ValidationReport
from ..utils import find_project_root

if TYPE_CHECKING:
    from ...models import MDIDocument
    from ...profiles import SkillProfile, WebApiProfile, CliToolProfile, GraphQLProfile


def validate_safety_checklist(
    doc: MDIDocument, profile: SkillProfile, content: str, report: ValidationReport
) -> None:
    """验证写操作Skill包含安全检查清单（仅Skill Profile）。"""
    content_lower = content.lower()
    has_write_ops = any(kw.lower() in content_lower for kw in WRITE_OPERATION_KEYWORDS)
    if not has_write_ops:
        return

    checklist_items = len(CHECKLIST_ITEM_PATTERN.findall(content))
    has_safety_section = bool(SAFETY_CHECKLIST_PATTERN.search(content))

    if not has_safety_section or checklist_items < 3:
        report.add_issue(
            "warn", "W006",
            f"写操作Skill安全检查清单不足（检测到{checklist_items}个检查项）",
            suggestion="写操作Skill建议包含至少3项安全检查项（如dry-run预览、幂等性检查、后验验证等）",
        )


def validate_skill_paths(doc: MDIDocument, source_path: str, report: ValidationReport) -> None:
    """验证Skill paths字段引用的文件存在（仅Skill Profile）。"""
    paths = doc.frontmatter.get("paths", [])
    if not isinstance(paths, list) or not paths:
        return

    source_file = Path(source_path) if source_path != "<doc>" else None
    if not source_file or not source_file.exists():
        return

    project_root = find_project_root(source_file)
    if not project_root:
        return

    for p in paths:
        if not isinstance(p, str):
            continue
        target = (project_root / p).resolve()
        if not target.exists():
            report.add_issue(
                "warn", "W007",
                f"paths字段引用的文件不存在: '{p}'",
                suggestion=f"检查路径 '{p}' 是否正确，相对于项目根目录",
            )


def validate_webapi_specific(doc: MDIDocument, profile: WebApiProfile, report: ValidationReport) -> None:
    """WebApi Profile特定验证（baseUrl格式、HTTP方法、参数/响应定义）。"""
    base_url = doc.frontmatter.get("baseUrl", "")
    if isinstance(base_url, str) and base_url:
        if not (base_url.startswith("http://") or base_url.startswith("https://")):
            report.add_issue(
                "warn", "W009",
                f"baseUrl格式不规范: '{base_url}'",
                suggestion="baseUrl应以http://或https://开头",
            )

    valid_methods = set(profile.supported_http_methods)
    for iface in doc.interfaces:
        if iface.method and iface.method.upper() not in valid_methods:
            report.add_issue(
                "warn", "W010",
                f"接口 '{iface.name}' 使用了不常见的HTTP方法: {iface.method}",
                suggestion=f"建议使用标准HTTP方法: {', '.join(valid_methods)}",
            )
        if not iface.parameters and iface.method.upper() in ("POST", "PUT", "PATCH"):
            report.add_issue(
                "info", "I001",
                f"接口 '{iface.name}'（{iface.method}）未定义参数表",
            )
        if not iface.responses:
            report.add_issue(
                "info", "I002",
                f"接口 '{iface.name}' 未定义响应表",
            )


def validate_cli_specific(
    doc: MDIDocument, profile: CliToolProfile, content: str, report: ValidationReport
) -> None:
    """CliTool Profile特定验证（用法示例检查）。"""
    has_example = "```" in content and ("example" in content.lower() or "示例" in content or "用法" in content or "usage" in content.lower())
    if not has_example:
        report.add_issue(
            "info", "I003",
            "CLI工具文档建议包含用法示例代码块",
        )
