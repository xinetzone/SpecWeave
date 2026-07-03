"""MDI验证器核心类。

提供MDIValidator主类，负责文档解析、验证流程编排和批量验证。
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from .models import ValidationReport
from .rules import (
    validate_frontmatter, validate_name_format, validate_description_length,
    validate_mandatory_phrase, validate_sections, validate_file_length,
    validate_why_explanations, validate_file_urls, validate_relative_links,
    validate_safety_checklist, validate_skill_paths, validate_webapi_specific,
    validate_cli_specific,
)
from ..parser import MDIParser
from ..profiles import (
    BaseProfile, SkillProfile, WebApiProfile, CliToolProfile, GraphQLProfile,
    get_profile, detect_profile_type,
)

SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


class MDIValidator:
    """MDI文档规范验证器。

    支持Skill/WebApi/CliTool三种Profile的验证，可自动检测Profile类型。
    提供文件验证、文档对象验证和批量验证能力。

    Args:
        profile_type: Profile类型，"auto"自动检测或指定"skill"/"webapi"/"clitool"。
    """

    def __init__(self, profile_type: str = "auto") -> None:
        self.profile_type = profile_type
        self._parser = MDIParser(profile_type="auto")

    def validate_file(self, path: str | Path) -> ValidationReport:
        """验证一个MDI文件。

        Args:
            path: MDI文件路径。

        Returns:
            ValidationReport验证报告。
        """
        file_path = Path(path).resolve()
        content = file_path.read_text(encoding="utf-8")
        doc = self._parser.parse_text(content, source=str(file_path))
        doc.source_path = file_path
        return self.validate_document(doc, source_path=str(file_path), raw_content=content)

    def validate_document(
        self,
        doc: Any,
        source_path: str = "<doc>",
        raw_content: str | None = None,
    ) -> ValidationReport:
        """验证已解析的MDIDocument对象。

        Args:
            doc: 已解析的MDI文档对象。
            source_path: 源文件路径（用于报告和相对路径解析）。
            raw_content: 原始文本内容（用于链接检查等需要原文的验证）。

        Returns:
            ValidationReport验证报告。
        """
        if self.profile_type == "auto":
            detected = detect_profile_type(doc, source_path)
            profile = get_profile(detected)
        else:
            profile = get_profile(self.profile_type)
            detected = self.profile_type

        if raw_content is None and doc.source_path and doc.source_path.exists():
            raw_content = doc.source_path.read_text(encoding="utf-8")
        if raw_content is None:
            raw_content = self._reconstruct_content(doc)

        report = ValidationReport(file=source_path, profile_type=detected)

        validate_frontmatter(doc, profile, report)
        validate_name_format(doc, report)
        validate_description_length(doc, report)
        validate_mandatory_phrase(doc, profile, report)
        validate_sections(doc, profile, raw_content, report)
        validate_file_length(raw_content, profile, report)
        validate_why_explanations(raw_content, report)
        validate_file_urls(raw_content, report)
        validate_relative_links(raw_content, source_path, report)
        validate_safety_checklist(doc, profile, raw_content, report)

        if isinstance(profile, SkillProfile):
            validate_skill_paths(doc, source_path, report)
        elif isinstance(profile, WebApiProfile):
            validate_webapi_specific(doc, profile, report)
        elif isinstance(profile, CliToolProfile):
            validate_cli_specific(doc, profile, raw_content, report)

        profile_results = profile.validate(doc)
        for pr in profile_results:
            report.add_issue(
                severity=pr.severity if not pr.passed else "info",
                code=f"GQL_{pr.name}" if isinstance(profile, GraphQLProfile) else f"P_{pr.name}",
                message=pr.message,
                line=pr.line,
            )

        report.calculate_score()
        return report

    def batch_validate(self, paths: list[str | Path]) -> list[ValidationReport]:
        """批量验证多个MDI文件。

        Args:
            paths: MDI文件路径列表。

        Returns:
            ValidationReport列表。
        """
        reports = []
        for p in paths:
            path = Path(p)
            if path.is_dir():
                for md_file in sorted(path.rglob("*.md")):
                    if md_file.name.upper() == "SKILL.MD" or self._looks_like_mdi(md_file):
                        reports.append(self.validate_file(md_file))
            else:
                reports.append(self.validate_file(path))
        return reports

    def _looks_like_mdi(self, path: Path) -> bool:
        """简单判断文件是否可能是MDI文档。"""
        try:
            content = path.read_text(encoding="utf-8")
            return content.startswith("---") or content.startswith("+++")
        except Exception:
            return False

    def _reconstruct_content(self, doc: Any) -> str:
        """从MDIDocument重建文本内容（包含章节、子章节、code blocks）。"""
        parts: list[str] = []

        def _walk(sections: list, level: int) -> None:
            for section in sections:
                parts.append(f"{'#' * level} {section.title}")
                parts.append(section.content)
                for cb in section.code_blocks:
                    if cb.language:
                        if cb.language.startswith("directive:"):
                            directive_name = cb.language[len("directive:"):]
                            header = f"{{{directive_name}}} {cb.meta}".rstrip()
                            parts.append(f"```{header}")
                        else:
                            header = f"{cb.language} {cb.meta}".strip()
                            parts.append(f"```{header}")
                    else:
                        parts.append("```")
                    parts.append(cb.content)
                    parts.append("```")
                for table in section.tables:
                    parts.append(str(table))
                for lst in section.lists:
                    parts.append(str(lst))
                _walk(section.subsections, level + 1)

        _walk(doc.sections, 1)
        return "\n".join(parts)
