"""MDI Profile 模块。

提供四类场景的Profile定义和验证规则：
- SkillProfile: AI Agent Skill
- WebApiProfile: RESTful Web API
- CliToolProfile: 命令行工具
- GraphQLProfile: GraphQL Schema & API
"""

import logging
import re
from pathlib import Path

from .base import BaseProfile, ProfileValidationResult, SectionPattern
from .skill_profile import SkillProfile
from .webapi_profile import WebApiProfile
from .clitool_profile import CliToolProfile
from .graphql_profile import GraphQLProfile
from ..models import MDIDocument

logger = logging.getLogger(__name__)

__all__ = [
    "BaseProfile",
    "ProfileValidationResult",
    "SectionPattern",
    "SkillProfile",
    "WebApiProfile",
    "CliToolProfile",
    "GraphQLProfile",
    "get_profile",
    "detect_profile_type",
]

_PROFILE_MAP: dict[str, type[BaseProfile]] = {
    "skill": SkillProfile,
    "webapi": WebApiProfile,
    "clitool": CliToolProfile,
    "graphql": GraphQLProfile,
}


def get_profile(profile_type: str) -> BaseProfile:
    """根据类型获取Profile实例。

    Args:
        profile_type: Profile类型，可选值: "skill", "webapi", "clitool", "graphql"

    Returns:
        BaseProfile子类实例

    Raises:
        ValueError: 未知的profile类型
    """
    if profile_type not in _PROFILE_MAP:
        raise ValueError(
            f"未知的Profile类型: {profile_type}，"
            f"支持的类型: {', '.join(_PROFILE_MAP.keys())}"
        )
    return _PROFILE_MAP[profile_type]()


def detect_profile_type(doc: MDIDocument, source_path: str = "") -> str:
    """自动检测文档的Profile类型。

    检测优先级（P1最高，P5最低）：
    P1. frontmatter中的type字段显式声明（最高优先级）
    P2. frontmatter特征字段检测：
        - baseUrl → webapi
        - argument-hint/user-invocable/paths → skill
        - schema/endpoint+query-type/mutation-type → graphql
    P3. 文件名/路径特征：
        - SKILL.md或skills/目录 → skill
        - cli/command → clitool
        - graphql/gql → graphql
    P4. 内容特征正则：
        - HTTP方法+路径 → webapi
        - type Query {/type Mutation {/type Subscription { → graphql
    P5. 默认值 → skill

    Args:
        doc: MDI文档对象
        source_path: 源文件路径

    Returns:
        Profile类型字符串: "skill", "webapi", "clitool", "graphql"
    """
    doc_name = doc.frontmatter.get("name", Path(source_path).name if source_path else "<unnamed>")
    logger.info("[ProfileDetector] 开始自动检测Profile: doc=%s, path=%s", doc_name, source_path)
    logger.debug("[ProfileDetector] frontmatter keys: %s", list(doc.frontmatter.keys()))

    fm_type = doc.frontmatter.get("type", "")
    if isinstance(fm_type, str):
        fm_type_lower = fm_type.lower().strip()
        logger.debug("[ProfileDetector] P1检查: frontmatter.type=%r", fm_type_lower)
        if fm_type_lower in _PROFILE_MAP:
            logger.info("[ProfileDetector] P1命中! frontmatter.type显式声明 → %s", fm_type_lower)
            return fm_type_lower

    logger.debug("[ProfileDetector] P2: frontmatter特征字段检测")
    fm_dict_lower = {k.lower(): v for k, v in doc.frontmatter.items()}
    logger.debug("[ProfileDetector] P2.lowercase keys: %s", list(fm_dict_lower.keys()))

    if "baseurl" in fm_dict_lower:
        logger.info("[ProfileDetector] P2命中! 发现baseUrl字段 → webapi")
        return "webapi"

    skill_indicators = {"argument-hint", "user-invocable", "paths"}
    fm_keys_lower = set(fm_dict_lower.keys())
    matched_skill = skill_indicators & fm_keys_lower
    if matched_skill:
        logger.info("[ProfileDetector] P2命中! 发现skill字段: %s → skill", matched_skill)
        return "skill"

    graphql_indicators = {"schema", "schema-path", "endpoint"}
    matched_graphql_fm = graphql_indicators & fm_keys_lower
    has_query_type = "query-type" in fm_keys_lower
    has_mutation_type = "mutation-type" in fm_keys_lower
    endpoint_has_graphql = "graphql" in str(fm_dict_lower.get("endpoint", "")).lower()
    logger.debug("[ProfileDetector] P2 graphql检查: matched_fm=%s, has_query=%s, has_mutation=%s, endpoint_has_gql=%s",
                  matched_graphql_fm, has_query_type, has_mutation_type, endpoint_has_graphql)
    if matched_graphql_fm and (has_query_type or has_mutation_type or endpoint_has_graphql):
        logger.info("[ProfileDetector] P2命中! 发现graphql字段组合: %s → graphql", matched_graphql_fm)
        return "graphql"

    if source_path:
        p = Path(source_path)
        logger.debug("[ProfileDetector] P3: 路径特征检测, name=%s, parts=%s", p.name, [part.lower() for part in p.parts])
        if p.name.upper() == "SKILL.MD" or "skills" in [part.lower() for part in p.parts]:
            logger.info("[ProfileDetector] P3命中! 路径含skills/或文件名为SKILL.md → skill")
            return "skill"
        name_lower = p.name.lower()
        if "cli" in name_lower or "command" in name_lower:
            logger.info("[ProfileDetector] P3命中! 文件名含cli/command → clitool")
            return "clitool"
        if "graphql" in name_lower or name_lower.endswith(".gql.md") or ".graphql." in name_lower:
            logger.info("[ProfileDetector] P3命中! 文件名含graphql/gql → graphql")
            return "graphql"

    logger.debug("[ProfileDetector] P4: 内容特征检测")
    full_text_parts: list[str] = []

    def _collect_text(sections: list) -> None:
        for s in sections:
            full_text_parts.append(s.title)
            full_text_parts.append(s.content)
            for cb in s.code_blocks:
                full_text_parts.append(cb.language or "")
                full_text_parts.append(" ".join(cb.meta) if cb.meta else "")
                full_text_parts.append(cb.content)
            _collect_text(s.subsections)

    _collect_text(doc.sections)
    full_text_lower = " ".join(full_text_parts).lower()

    has_query_type_def = "type query {" in full_text_lower
    has_mutation_type_def = "type mutation {" in full_text_lower
    has_subscription_type_def = "type subscription {" in full_text_lower
    logger.debug("[ProfileDetector] P4 graphql type定义检测: query=%s, mutation=%s, subscription=%s",
                  has_query_type_def, has_mutation_type_def, has_subscription_type_def)
    if has_query_type_def or has_mutation_type_def or has_subscription_type_def:
        logger.info("[ProfileDetector] P4命中! 发现GraphQL type定义 → graphql")
        return "graphql"

    http_match = re.search(r"`(GET|POST|PUT|PATCH|DELETE)\s+/", full_text_lower)
    if http_match:
        logger.info("[ProfileDetector] P4命中! 发现HTTP方法: %s → webapi", http_match.group(1))
        return "webapi"

    logger.info("[ProfileDetector] P5兜底: 未命中任何规则，默认 → skill")
    return "skill"
