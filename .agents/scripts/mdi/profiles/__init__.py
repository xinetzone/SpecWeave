"""MDI Profile 模块。

提供四类场景的Profile定义和验证规则：
- SkillProfile: AI Agent Skill
- WebApiProfile: RESTful Web API
- CliToolProfile: 命令行工具
- GraphQLProfile: GraphQL Schema & API
"""

from .base import BaseProfile, ProfileValidationResult, SectionPattern
from .skill_profile import SkillProfile
from .webapi_profile import WebApiProfile
from .clitool_profile import CliToolProfile
from .graphql_profile import GraphQLProfile
from ..models import MDIDocument

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
    import re

    fm_type = doc.frontmatter.get("type", "")
    if isinstance(fm_type, str):
        fm_type_lower = fm_type.lower().strip()
        if fm_type_lower in _PROFILE_MAP:
            return fm_type_lower

    fm_dict_lower = {k.lower(): v for k, v in doc.frontmatter.items()}
    if "baseurl" in fm_dict_lower:
        return "webapi"

    skill_indicators = {"argument-hint", "user-invocable", "paths"}
    fm_keys_lower = set(fm_dict_lower.keys())
    if skill_indicators & fm_keys_lower:
        return "skill"

    graphql_indicators = {"schema", "schema-path", "endpoint"}
    if graphql_indicators & fm_keys_lower and (
        "query-type" in fm_keys_lower or "mutation-type" in fm_keys_lower
        or "graphql" in str(fm_dict_lower.get("endpoint", "")).lower()
    ):
        return "graphql"

    if source_path:
        from pathlib import Path
        p = Path(source_path)
        if p.name.upper() == "SKILL.MD" or "skills" in [part.lower() for part in p.parts]:
            return "skill"
        name_lower = p.name.lower()
        if "cli" in name_lower or "command" in name_lower:
            return "clitool"
        if "graphql" in name_lower or name_lower.endswith(".gql.md") or ".graphql." in name_lower:
            return "graphql"

    full_text_lower = ""
    for s in doc.sections:
        full_text_lower += s.title.lower() + " " + s.content.lower() + " "

    if "type query {" in full_text_lower or "type mutation {" in full_text_lower \
            or "type subscription {" in full_text_lower:
        return "graphql"

    if re.search(r"`(GET|POST|PUT|PATCH|DELETE)\s+/", full_text_lower):
        return "webapi"

    return "skill"
