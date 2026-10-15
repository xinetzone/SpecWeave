"""YAML front-matter 解析（upstream: packages/core/src/utils/front-matter.ts 1:1）。"""

import re
from dataclasses import dataclass
from typing import Any

import yaml

# upstream: front-matter.ts:10（CommonMark/Jekyll 风格，含可选 BOM 与 ... 收尾）
FRONT_MATTER_RE = re.compile(
    r"^\uFEFF?(?:---|= yaml =)[ \t]*\r?\n([\s\S]*?)\r?\n(?:---|\.\.\.|= yaml =)[ \t]*(?:\r?\n|$)"
)

# upstream: front-matter.ts:17（把 "* item" 形态的 YAML 别名风险归一化为 "- " 列表）
_LIST_MARKER_RE = re.compile(r"(^|\n)([ \t]*)\*(?=[ \t]+\S)")


@dataclass(slots=True)
class ParsedFrontMatter:
    attributes: dict[str, Any]
    body: str


def _normalize_md_list_markers(text: str) -> str:
    return _LIST_MARKER_RE.sub(r"\1\2-", text)


def _parse_yaml_object(raw: str) -> dict[str, Any] | None:
    """upstream: parseYamlObject（空→{}，非对象→{}，解析错→None 回退整篇原文）。"""
    try:
        normalized = _normalize_md_list_markers(raw)
        if not normalized.strip():
            return {}
        data = yaml.safe_load(normalized)
        if data is None or not isinstance(data, dict):
            return {}
        return dict(data)
    except yaml.YAMLError:
        return None


def parse_front_matter(markdown_text: str) -> ParsedFrontMatter:
    """upstream: front-matter.ts:36。"""
    match = FRONT_MATTER_RE.match(markdown_text)
    if not match:
        return ParsedFrontMatter(attributes={}, body=markdown_text)

    attributes = _parse_yaml_object(match.group(1) or "")
    if attributes is None:
        return ParsedFrontMatter(attributes={}, body=markdown_text)

    return ParsedFrontMatter(
        attributes=attributes,
        body=markdown_text[match.end() :],
    )
