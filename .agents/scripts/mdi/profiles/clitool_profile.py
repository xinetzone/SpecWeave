"""CLI Tool Profile：命令行工具规范。

定义命令行工具文档的结构要求。
必填Frontmatter: name, description
推荐Frontmatter: version, type, authors, license
"""

from dataclasses import dataclass, field
from pathlib import Path
import re

from .base import BaseProfile, SectionPattern, ProfileValidationResult
from ..models import MDIDocument


CLITOOL_SECTION_PATTERNS: tuple[SectionPattern, ...] = (
    SectionPattern(
        key="overview",
        keywords=("工具概述", "概述", "overview", "简介", "描述"),
        required=False,
    ),
    SectionPattern(
        key="installation",
        keywords=("安装", "installation", "安装方式", "setup", "部署"),
        required=False,
    ),
    SectionPattern(
        key="commands",
        keywords=("命令列表", "命令", "command", "子命令", "用法", "usage"),
        required=False,
    ),
    SectionPattern(
        key="config",
        keywords=("配置", "configuration", "环境变量", "config"),
        required=False,
    ),
)


@dataclass
class CliToolProfile(BaseProfile):
    """命令行工具Profile。

    必填Frontmatter: name, description
    推荐Frontmatter: version, type, authors, license, tags, binaryName, packageName
    """

    profile_type: str = "clitool"

    required_frontmatter: set[str] = field(
        default_factory=lambda: {"name", "description"}
    )
    recommended_frontmatter: set[str] = field(
        default_factory=lambda: {"version", "type", "authors", "license", "tags", "binaryName", "packageName"}
    )

    section_patterns: tuple[SectionPattern, ...] = CLITOOL_SECTION_PATTERNS
