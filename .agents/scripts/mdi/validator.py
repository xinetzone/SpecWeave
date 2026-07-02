"""MDI (Markdown Interface) 规范验证器。

提供MDI文档的规范化验证能力，支持Skill/WebApi/CliTool三种Profile。
验证规则覆盖frontmatter完整性、章节结构、内容质量、链接规范、Profile特定要求。
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from .models import MDIDocument
from .parser import MDIParser
from .profiles import (
    BaseProfile,
    SkillProfile,
    WebApiProfile,
    CliToolProfile,
    GraphQLProfile,
    get_profile,
    detect_profile_type,
)

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


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


@dataclass
class ValidationIssue:
    """单个验证问题。"""

    severity: str
    code: str
    message: str
    line: int | None
    file: str
    suggestion: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "line": self.line,
            "file": self.file,
        }
        if self.suggestion:
            result["suggestion"] = self.suggestion
        return result


@dataclass
class ValidationReport:
    """MDI文档验证报告。"""

    file: str
    issues: list[ValidationIssue] = field(default_factory=list)
    score: int = 100
    profile_type: str = ""

    def passed(self) -> bool:
        """是否通过验证（无error级别问题）。"""
        return all(i.severity != "error" for i in self.issues)

    def errors(self) -> list[ValidationIssue]:
        """返回所有error级别问题。"""
        return [i for i in self.issues if i.severity == "error"]

    def warnings(self) -> list[ValidationIssue]:
        """返回所有warn级别问题。"""
        return [i for i in self.issues if i.severity == "warn"]

    def infos(self) -> list[ValidationIssue]:
        """返回所有info级别问题。"""
        return [i for i in self.issues if i.severity == "info"]

    def calculate_score(self) -> int:
        """计算质量评分（0-100）。"""
        score = 100
        for issue in self.issues:
            if issue.severity == "error":
                score -= ERROR_SCORE_PENALTY
            elif issue.severity == "warn":
                score -= WARN_SCORE_PENALTY
            elif issue.severity == "info":
                score -= INFO_SCORE_PENALTY
        self.score = max(0, min(100, score))
        return self.score

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "profile": self.profile_type,
            "score": self.score,
            "passed": self.passed(),
            "errorCount": len(self.errors()),
            "warnCount": len(self.warnings()),
            "infoCount": len(self.infos()),
            "issues": [i.to_dict() for i in self.issues],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


def _is_code_fence_context(content: str, pos: int) -> bool:
    """判断位置是否在代码块内。"""
    before = content[:pos]
    fence_count = before.count("```")
    if fence_count % 2 == 1:
        return True
    line_start = before.rfind("\n") + 1
    line_before = before[line_start:]
    tick_count = 0
    i = 0
    while i < len(line_before):
        if line_before[i] == "`":
            run = 1
            while i + run < len(line_before) and line_before[i + run] == "`":
                run += 1
            if run <= 2:
                tick_count += 1
            i += run
        else:
            i += 1
    return tick_count % 2 == 1


def _find_line_number(content: str, search_text: str, start_from: int = 0) -> int | None:
    """在文本中查找指定文本所在行号。"""
    idx = content.find(search_text, start_from)
    if idx == -1:
        return None
    return content.count("\n", 0, idx) + 1


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
        doc: MDIDocument,
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
        self._validate_frontmatter(doc, profile, report)
        self._validate_name_format(doc, report)
        self._validate_description_length(doc, report)
        self._validate_mandatory_phrase(doc, profile, report)
        self._validate_sections(doc, profile, raw_content, report)
        self._validate_file_length(raw_content, profile, report)
        self._validate_why_explanations(raw_content, report)
        self._validate_file_urls(raw_content, report)
        self._validate_relative_links(raw_content, source_path, report)
        self._validate_safety_checklist(doc, profile, raw_content, report)

        if isinstance(profile, SkillProfile):
            self._validate_skill_paths(doc, source_path, report)
        elif isinstance(profile, WebApiProfile):
            self._validate_webapi_specific(doc, profile, report)
        elif isinstance(profile, CliToolProfile):
            self._validate_cli_specific(doc, profile, raw_content, report)

        profile_results = profile.validate(doc)
        for pr in profile_results:
            self._add_issue(
                report,
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

    def _reconstruct_content(self, doc: MDIDocument) -> str:
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

    def _add_issue(
        self,
        report: ValidationReport,
        severity: str,
        code: str,
        message: str,
        line: int | None = None,
        suggestion: str | None = None,
    ) -> None:
        report.issues.append(ValidationIssue(
            severity=severity,
            code=code,
            message=message,
            line=line,
            file=report.file,
            suggestion=suggestion,
        ))

    def _validate_frontmatter(self, doc: MDIDocument, profile: BaseProfile, report: ValidationReport) -> None:
        fm = doc.frontmatter

        for field_name in sorted(profile.required_frontmatter):
            value = fm.get(field_name)
            if value is None or (isinstance(value, str) and len(value.strip()) == 0):
                self._add_issue(
                    report, "error", "E001",
                    f"缺少必填frontmatter字段: '{field_name}'",
                    suggestion=f"在frontmatter中添加 '{field_name}' 字段",
                )

        for field_name in sorted(profile.recommended_frontmatter):
            value = fm.get(field_name)
            if value is None:
                self._add_issue(
                    report, "warn", "W001",
                    f"缺少推荐frontmatter字段: '{field_name}'",
                    suggestion=f"建议添加 '{field_name}' 字段以提高文档完整性",
                )

    def _validate_name_format(self, doc: MDIDocument, report: ValidationReport) -> None:
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
            self._add_issue(
                report, "error", "E002",
                f"name字段格式不合法: {'; '.join(issues)}",
                suggestion="name应为kebab-case格式（小写字母、数字、连字符，不以连字符开头/结尾）",
            )

    def _validate_description_length(self, doc: MDIDocument, report: ValidationReport) -> None:
        desc = doc.frontmatter.get("description", "")
        if not desc or not isinstance(desc, str):
            return

        desc_len = len(desc)
        if desc_len < MIN_DESCRIPTION_LENGTH:
            self._add_issue(
                report, "warn", "W002",
                f"description过短（{desc_len}字符），建议≥{MIN_DESCRIPTION_LENGTH}字符以明确功能",
                suggestion="补充功能描述和触发场景说明",
            )
        elif desc_len > MAX_DESCRIPTION_LENGTH:
            self._add_issue(
                report, "warn", "W002",
                f"description过长（{desc_len}字符），超过硬限制{MAX_DESCRIPTION_LENGTH}字符",
                suggestion="精简description，将详细内容移到正文章节",
            )

    def _validate_mandatory_phrase(self, doc: MDIDocument, profile: BaseProfile, report: ValidationReport) -> None:
        if not isinstance(profile, SkillProfile):
            return

        desc = doc.frontmatter.get("description", "")
        if not desc or not isinstance(desc, str):
            return

        has_mandatory = any(phrase in desc for phrase in MANDATORY_TRIGGER_PHRASES)
        if not has_mandatory:
            self._add_issue(
                report, "error", "E003",
                "Skill description缺少强制触发措辞",
                suggestion="description应包含'必须使用此技能'、'Use this skill'或'MUST use'等强制触发措辞，避免undertrigger",
            )

    def _validate_sections(self, doc: MDIDocument, profile: BaseProfile, content: str, report: ValidationReport) -> None:
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
                        self._add_issue(
                            report, "warn", "W003",
                            f"缺少{label}（检测到多方案描述）",
                            suggestion=suggestion,
                        )

    def _validate_file_length(self, content: str, profile: BaseProfile, report: ValidationReport) -> None:
        lines = content.count("\n") + 1

        if isinstance(profile, SkillProfile):
            if lines > MAX_SKILL_LINES_ERROR:
                self._add_issue(
                    report, "warn", "W004",
                    f"文件过长（{lines}行），严重超过{MAX_SKILL_LINES_WARN}行建议",
                    suggestion="考虑使用references/子文档进行渐进式披露，将低频内容拆分出去",
                )
            elif lines > MAX_SKILL_LINES_WARN:
                self._add_issue(
                    report, "warn", "W004",
                    f"文件超过{MAX_SKILL_LINES_WARN}行建议（当前{lines}行）",
                    suggestion="渐进式披露原则：考虑将详细参考内容移到references/子文档",
                )

    def _validate_why_explanations(self, content: str, report: ValidationReport) -> None:
        why_count = len(WHY_EXPLANATION_PATTERN.findall(content))
        must_count = len(MUST_RULE_PATTERN.findall(content))

        if must_count >= 3 and why_count < 2:
            self._add_issue(
                report, "warn", "W005",
                f"Why解释不足：关键MUST类规则{must_count}个，但Why解释仅{why_count}个",
                suggestion="在关键MUST规则后添加 '> **为什么...**' 引用块解释设计意图，帮助理解边界情况",
            )

    def _validate_file_urls(self, content: str, report: ValidationReport) -> None:
        for m in FILE_URL_RE.finditer(content):
            if _is_code_fence_context(content, m.start()):
                continue
            line = content.count("\n", 0, m.start()) + 1
            self._add_issue(
                report, "warn", "W008",
                f"使用了file:///绝对路径: {m.group(0)[:80]}",
                line=line,
                suggestion="应使用相对路径引用项目内文件",
            )

    def _validate_relative_links(self, content: str, source_path: str, report: ValidationReport) -> None:
        if source_path == "<doc>":
            return

        source_file = Path(source_path)
        if not source_file.exists():
            return

        base_dir = source_file.parent
        project_root = self._find_project_root(source_file)

        for m in INLINE_LINK_RE.finditer(content):
            if _is_code_fence_context(content, m.start()):
                continue
            url = m.group(2).strip()

            if url.startswith("http://") or url.startswith("https://") or url.startswith("mailto:") or url.startswith("#"):
                continue
            if url.startswith("file:///"):
                continue

            url_path = url.split("#")[0]
            if not url_path:
                continue

            if url_path.startswith("/"):
                resolved = (project_root / url_path.lstrip("/")).resolve() if project_root else None
            else:
                resolved = (base_dir / url_path).resolve()

            if resolved and not resolved.exists():
                depth_adjusted = self._try_depth_adjust(url_path, base_dir)
                if depth_adjusted is None:
                    line = content.count("\n", 0, m.start()) + 1
                    self._add_issue(
                        report, "warn", "W007",
                        f"内部相对链接可能无效: [{m.group(1)}]({url_path})",
                        line=line,
                        suggestion="检查目标文件是否存在或路径是否正确",
                    )

    def _try_depth_adjust(self, url_path: str, base_dir: Path) -> Path | None:
        """尝试调整相对路径深度。"""
        from .profiles.base import BaseProfile
        cleaned = url_path.replace("\\", "/")
        while cleaned.startswith("./"):
            cleaned = cleaned[2:]
        parts = cleaned.split("/")
        dotdot_count = 0
        for p in parts:
            if p == "..":
                dotdot_count += 1
            else:
                break
        remaining = parts[dotdot_count:]
        if not remaining:
            return None
        for delta in range(1, 4):
            new_parts = [".."] * (dotdot_count + delta) + remaining
            candidate = (base_dir / "/".join(new_parts)).resolve()
            if candidate.exists():
                return candidate
        return None

    def _find_project_root(self, start: Path) -> Path | None:
        """从起始路径向上查找包含.agents/的项目根目录。"""
        current = start if start.is_dir() else start.parent
        for candidate in [current, *current.parents]:
            if (candidate / ".agents").is_dir():
                return candidate.resolve()
        return None

    def _validate_safety_checklist(
        self, doc: MDIDocument, profile: BaseProfile, content: str, report: ValidationReport
    ) -> None:
        if not isinstance(profile, SkillProfile):
            return

        content_lower = content.lower()
        has_write_ops = any(kw.lower() in content_lower for kw in WRITE_OPERATION_KEYWORDS)
        if not has_write_ops:
            return

        checklist_items = len(CHECKLIST_ITEM_PATTERN.findall(content))
        has_safety_section = bool(SAFETY_CHECKLIST_PATTERN.search(content))

        if not has_safety_section or checklist_items < 3:
            self._add_issue(
                report, "warn", "W006",
                f"写操作Skill安全检查清单不足（检测到{checklist_items}个检查项）",
                suggestion="写操作Skill建议包含至少3项安全检查项（如dry-run预览、幂等性检查、后验验证等）",
            )

    def _validate_skill_paths(self, doc: MDIDocument, source_path: str, report: ValidationReport) -> None:
        paths = doc.frontmatter.get("paths", [])
        if not isinstance(paths, list) or not paths:
            return

        source_file = Path(source_path) if source_path != "<doc>" else None
        if not source_file or not source_file.exists():
            return

        project_root = self._find_project_root(source_file)
        if not project_root:
            return

        for p in paths:
            if not isinstance(p, str):
                continue
            target = (project_root / p).resolve()
            if not target.exists():
                self._add_issue(
                    report, "warn", "W007",
                    f"paths字段引用的文件不存在: '{p}'",
                    suggestion=f"检查路径 '{p}' 是否正确，相对于项目根目录",
                )

    def _validate_webapi_specific(self, doc: MDIDocument, profile: WebApiProfile, report: ValidationReport) -> None:
        base_url = doc.frontmatter.get("baseUrl", "")
        if isinstance(base_url, str) and base_url:
            if not (base_url.startswith("http://") or base_url.startswith("https://")):
                self._add_issue(
                    report, "warn", "W009",
                    f"baseUrl格式不规范: '{base_url}'",
                    suggestion="baseUrl应以http://或https://开头",
                )

        valid_methods = set(profile.supported_http_methods)
        for iface in doc.interfaces:
            if iface.method and iface.method.upper() not in valid_methods:
                self._add_issue(
                    report, "warn", "W010",
                    f"接口 '{iface.name}' 使用了不常见的HTTP方法: {iface.method}",
                    suggestion=f"建议使用标准HTTP方法: {', '.join(valid_methods)}",
                )
            if not iface.parameters and iface.method.upper() in ("POST", "PUT", "PATCH"):
                self._add_issue(
                    report, "info", "I001",
                    f"接口 '{iface.name}'（{iface.method}）未定义参数表",
                )
            if not iface.responses:
                self._add_issue(
                    report, "info", "I002",
                    f"接口 '{iface.name}' 未定义响应表",
                )

    def _validate_cli_specific(
        self, doc: MDIDocument, profile: CliToolProfile, content: str, report: ValidationReport
    ) -> None:
        has_example = "```" in content and ("example" in content.lower() or "示例" in content or "用法" in content or "usage" in content.lower())
        if not has_example:
            self._add_issue(
                report, "info", "I003",
                "CLI工具文档建议包含用法示例代码块",
            )
