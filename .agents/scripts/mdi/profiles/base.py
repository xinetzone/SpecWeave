"""MDI 基础Profile类。

定义所有Profile共有的字段和验证规则，使用关键词模糊匹配章节。
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import re

from ..models import MDIDocument


@dataclass
class ProfileValidationResult:
    """单个验证项结果。"""

    name: str
    passed: bool
    severity: str
    message: str
    line: int | None = None


@dataclass
class SectionPattern:
    """章节关键词匹配模式。"""

    key: str
    keywords: tuple[str, ...]
    required: bool = False


@dataclass
class BaseProfile:
    """MDI Profile基类。

    所有具体Profile（Skill/WebApi/CliTool）继承此类，
    定义必填/推荐字段和章节，并实现验证逻辑。
    """

    profile_type: str = "base"

    required_frontmatter: set[str] = field(
        default_factory=lambda: {"name", "description"}
    )
    recommended_frontmatter: set[str] = field(
        default_factory=lambda: {"version", "type", "authors", "license"}
    )

    section_patterns: tuple[SectionPattern, ...] = ()

    supported_http_methods: tuple[str, ...] = ()

    def match_section(self, section_title: str, pattern_key: str) -> bool:
        """用关键词模糊匹配章节标题。"""
        normalized = self._normalize_title(section_title)
        for sp in self.section_patterns:
            if sp.key == pattern_key:
                for kw in sp.keywords:
                    if self._normalize_title(kw) in normalized:
                        return True
        return False

    def find_sections_by_key(self, doc: MDIDocument, pattern_key: str) -> list:
        """查找匹配指定关键词模式的所有章节（含子章节）。"""
        results = []

        def _walk(sections: list) -> None:
            for s in sections:
                if self.match_section(s.title, pattern_key):
                    results.append(s)
                _walk(s.subsections)

        _walk(doc.sections)
        return results

    def get_section_content(self, doc: MDIDocument, pattern_key: str) -> str:
        """获取匹配章节的合并内容。"""
        sections = self.find_sections_by_key(doc, pattern_key)
        parts = []
        for s in sections:
            parts.append(s.content)
            for cb in s.code_blocks:
                parts.append(cb.content)
        return "\n".join(parts)

    def get_full_text(self, doc: MDIDocument) -> str:
        """获取文档全文（含所有章节和子章节内容）。"""
        parts: list[str] = []

        def _walk(sections: list) -> None:
            for s in sections:
                parts.append(s.title)
                parts.append(s.content)
                for cb in s.code_blocks:
                    parts.append(cb.content)
                for lst in s.lists:
                    if isinstance(lst, dict) and "items" in lst:
                        for item in lst["items"]:
                            if isinstance(item, str):
                                parts.append(item)
                            elif hasattr(item, "text"):
                                parts.append(item.text)
                _walk(s.subsections)

        _walk(doc.sections)
        return "\n".join(parts)

    @staticmethod
    def _normalize_title(title: str) -> str:
        """标准化标题文本用于匹配（去除序号、空格、转小写）。"""
        cleaned = re.sub(r"^\d+\.?\d*\.?\s*", "", title.strip())
        cleaned = re.sub(r"\s+", "", cleaned)
        return cleaned.lower()
