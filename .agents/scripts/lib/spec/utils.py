"""Spec 检查工具函数。

提供关键词提取、语义匹配、路径解析、元文档检测等通用工具函数。
"""

import re
from pathlib import Path
from typing import Any

from constants import META_DOC_KEYWORDS, PROJECT_ROOT_PREFIXES


_META_TYPE_PATTERN = re.compile(r"<!--\s*meta_type:\s*(\w+)\s*-->")


def extract_keywords(text: str) -> list[str]:
    """从文本中提取中文关键词（2+ 字符的连续中文字符串）和英文单词。"""
    chinese_words = re.findall(r"[\u4e00-\u9fa5]{2,}", text)
    english_words = re.findall(r"[a-zA-Z]{2,}", text)
    return chinese_words + english_words


def semantic_match(source_text: str, target_text: str, min_matches: int = 2) -> bool:
    """检查两个文本是否语义匹配。

    提取 source 中的关键词，检查 target 中是否包含足够多的相同关键词。
    """
    source_keywords = set(extract_keywords(source_text))
    if not source_keywords:
        return False
    target_keywords = set(extract_keywords(target_text))
    common = source_keywords & target_keywords
    return len(common) >= min_matches


def resolve_path(ref: str, spec_dir: Path, project_root: Path) -> Path:
    """根据引用路径前缀选择基准目录进行解析。

    以 PROJECT_ROOT_PREFIXES 中列出的前缀开头的路径，以项目根目录为基准；
    其他相对路径以 spec 所在目录为基准。
    """
    for prefix in PROJECT_ROOT_PREFIXES:
        if ref.startswith(prefix):
            return project_root / ref
    return spec_dir / ref


def detect_meta_document(spec_text: str) -> tuple[bool, str]:
    """检测 spec.md 是否为元文档（描述其他文档/项目的文档）。

    检测策略：
    1. 优先查找显式标记 `<!-- meta_type: xxx -->`（零误判）
    2. 未找到显式标记时，回退到关键词检测（有误判风险）

    Returns:
        (is_meta, detection_method): 是否为元文档，以及检测方式
            - detection_method: "explicit" | "keyword" | "none"
    """
    match = _META_TYPE_PATTERN.search(spec_text)
    if match:
        return True, "explicit"

    if any(kw in spec_text for kw in META_DOC_KEYWORDS):
        return True, "keyword"

    return False, "none"


# 必须的核心章节（按顺序）—— 兼容纯英文标题和带中文括号标题两种格式
# 格式: (规范名称, 匹配正则, 中文别名)
CORE_CHAPTERS = [
    ("Why", re.compile(r"^##\s+Why(?:[（\(].*?[）\)])?\s*$", re.MULTILINE), "动机"),
    ("What Changes", re.compile(r"^##\s+What\s+Changes(?:[（\(].*?[）\)])?\s*$", re.MULTILINE), "变更摘要"),
    ("Impact", re.compile(r"^##\s+Impact(?:[（\(].*?[）\)])?\s*$", re.MULTILINE), "影响范围"),
    ("ADDED Requirements", re.compile(r"^##\s+ADDED\s+Requirements(?:[（\(].*?[）\)])?\s*$", re.MULTILINE), "新增需求"),
    ("MODIFIED Requirements", re.compile(r"^##\s+MODIFIED\s+Requirements(?:[（\(].*?[）\)])?\s*$", re.MULTILINE), "修改需求"),
    ("REMOVED Requirements", re.compile(r"^##\s+REMOVED\s+Requirements(?:[（\(].*?[）\)])?\s*$", re.MULTILINE), "移除需求"),
]


# 禁止使用的模糊词汇
VAGUE_WORDS = [
    "良好", "优秀", "合适", "不错", "还行",
    "可能", "也许", "大约", "较好", "较快",
    "适量", "基本上", "令人满意",
]


def calculate_score(total_issues: list[Any], chapters_found: list[str], requirements: list) -> int:
    """基于检查结果计算评分 (0-100)。"""
    from .models import Issue

    score = 100

    for issue in total_issues:
        if not isinstance(issue, Issue):
            continue
        if issue.severity == "error":
            if issue.type in ["missing_chapter", "empty_chapter", "missing_version"]:
                score -= 12
            elif issue.type in ["missing_requirement", "missing_scenario"]:
                score -= 8
            elif issue.type in ["missing_scenario_part", "invalid_changelog_format"]:
                score -= 6
            elif issue.type == "missing_shall":
                score -= 4
        else:
            if issue.type in ["vague_criteria", "version_format", "changelog_missing_end", "changelog_order"]:
                score -= 3
            elif issue.type == "chapter_order":
                score -= 2
            elif issue.type in ["empty_changelog", "missing_changelog"]:
                score -= 4

    missing_chapters = len(CORE_CHAPTERS) - len(chapters_found)
    score -= missing_chapters * 5

    if len(requirements) == 0:
        score -= 15

    return max(0, min(100, score))


def discover_spec_dirs(project_root: Path) -> list[Path]:
    """发现项目中的所有 spec 目录。

    扫描 ``project_root / ".trae" / "specs"`` 目录，返回其中所有子目录，
    按名称排序。若 specs 根目录不存在则返回空列表。

    Args:
        project_root: 项目根目录路径。

    Returns:
        spec 子目录列表（按名称升序），无子目录时为空列表。
    """
    specs_root = project_root / ".trae" / "specs"
    if not specs_root.exists():
        return []
    return sorted(
        [d for d in specs_root.iterdir() if d.is_dir()],
        key=lambda p: p.name,
    )
