"""Web API Profile：RESTful API规范。

定义RESTful API接口文档的结构要求。
必填Frontmatter: name, description, baseUrl
推荐Frontmatter: version, type, authors, license
"""

from dataclasses import dataclass, field
from pathlib import Path
import re

from .base import BaseProfile, SectionPattern, ProfileValidationResult
from ..models import MDIDocument


WEBAPI_SECTION_PATTERNS: tuple[SectionPattern, ...] = (
    SectionPattern(
        key="overview",
        keywords=("接口概览", "概览", "overview", "概述", "简介"),
        required=False,
    ),
    SectionPattern(
        key="auth",
        keywords=("认证", "授权", "auth", "authentication", "鉴权"),
        required=False,
    ),
    SectionPattern(
        key="interfaces",
        keywords=("接口列表", "api列表", "接口", "api", "endpoints", "接口定义"),
        required=False,
    ),
)


@dataclass
class WebApiProfile(BaseProfile):
    """RESTful Web API Profile。

    必填Frontmatter: name, description, baseUrl
    推荐Frontmatter: version, type, authors, license, tags, servers, securitySchemes
    """

    profile_type: str = "webapi"

    required_frontmatter: set[str] = field(
        default_factory=lambda: {"name", "description", "baseUrl"}
    )
    recommended_frontmatter: set[str] = field(
        default_factory=lambda: {"version", "type", "authors", "license", "tags", "servers", "securitySchemes"}
    )

    section_patterns: tuple[SectionPattern, ...] = WEBAPI_SECTION_PATTERNS

    supported_http_methods: tuple[str, ...] = ("GET", "POST", "PUT", "PATCH", "DELETE")
