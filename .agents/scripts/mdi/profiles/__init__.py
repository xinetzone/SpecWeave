"""MDI Profile 模块。

提供三类场景的Profile定义和验证规则：
- SkillProfile: AI Agent Skill
- WebApiProfile: RESTful Web API
- CliToolProfile: 命令行工具
"""

from .base import BaseProfile, ProfileValidationResult, SectionPattern
from .skill_profile import SkillProfile
from .webapi_profile import WebApiProfile
from .clitool_profile import CliToolProfile
from ..models import MDIDocument

__all__ = [
    "BaseProfile",
    "ProfileValidationResult",
    "SectionPattern",
    "SkillProfile",
    "WebApiProfile",
    "CliToolProfile",
    "get_profile",
    "detect_profile_type",
]

_PROFILE_MAP: dict[str, type[BaseProfile]] = {
    "skill": SkillProfile,
    "webapi": WebApiProfile,
    "clitool": CliToolProfile,
}


def get_profile(profile_type: str) -> BaseProfile:
    """根据类型获取Profile实例。

    Args:
        profile_type: Profile类型，可选值: "skill", "webapi", "clitool"

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

    检测优先级：
    1. frontmatter中的type字段
    2. frontmatter中存在baseUrl → webapi
    3. frontmatter中存在argument-hint/user-invocable/paths → skill
    4. 文件名或路径包含SKILL.md → skill
    5. 文件名包含cli/command → clitool
    6. 内容中有HTTP方法+路径模式 → webapi
    7. 默认返回skill

    Args:
        doc: MDI文档对象
        source_path: 源文件路径

    Returns:
        Profile类型字符串: "skill", "webapi", 或 "clitool"
    """
    import re

    fm_type = doc.frontmatter.get("type", "")
    if isinstance(fm_type, str):
        fm_type_lower = fm_type.lower().strip()
        if fm_type_lower in _PROFILE_MAP:
            return fm_type_lower

    if "baseurl" in {k.lower(): v for k, v in doc.frontmatter.items()}:
        return "webapi"

    skill_indicators = {"argument-hint", "user-invocable", "paths"}
    fm_keys_lower = {k.lower() for k in doc.frontmatter.keys()}
    if skill_indicators & fm_keys_lower:
        return "skill"

    if source_path:
        from pathlib import Path
        p = Path(source_path)
        if p.name.upper() == "SKILL.MD" or "skills" in [part.lower() for part in p.parts]:
            return "skill"
        name_lower = p.name.lower()
        if "cli" in name_lower or "command" in name_lower:
            return "clitool"

    full_text_lower = ""
    for s in doc.sections:
        full_text_lower += s.title.lower() + " " + s.content.lower() + " "
    if re.search(r"`(GET|POST|PUT|PATCH|DELETE)\s+/", full_text_lower):
        return "webapi"

    return "skill"
