"""第一性原理知识分类体系。

从第一性原理出发定义知识本质类型，实现多维标签体系，
支持按知识本质维度（factual/procedural/conditional/metacognitive）
和验证状态（draft/verified/peer-reviewed/deprecated）进行检索。

分类体系设计原则：
- 从知识本质出发，而非类比现有目录结构
- 与现有目录体系共存，形成多维标签
- 向后兼容，旧条目无需强制迁移
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 知识分类定义
# ---------------------------------------------------------------------------

KNOWLEDGE_TYPE_DEFINITIONS = {
    "factual": {
        "label": "事实性知识",
        "description": "描述客观事实、定义、数据、术语的知识。回答「是什么」的问题。",
        "examples": ["术语定义", "API文档", "配置参数说明", "技术规范"],
        "typical_dir": "reference/",
    },
    "procedural": {
        "label": "程序性知识",
        "description": "描述如何执行操作、步骤、流程的知识。回答「怎么做」的问题。",
        "examples": ["操作指南", "教程", "工作流", "检查清单"],
        "typical_dir": "best-practices/",
    },
    "conditional": {
        "label": "条件性知识",
        "description": "描述何时、为何使用某种方法的知识。回答「什么时候用/为什么」的问题。",
        "examples": ["决策矩阵", "选型指南", "场景分析", "权衡文档"],
        "typical_dir": "learning/",
    },
    "metacognitive": {
        "label": "元认知知识",
        "description": "关于认知过程本身的知识，反思学习方法和思维模式。回答「如何思考」的问题。",
        "examples": ["方法论", "认知模式", "经验复盘", "思维框架"],
        "typical_dir": "learning/",
    },
}

VALIDATION_STATUSES = {
    "draft": "草稿——初始创建，未经验证",
    "verified": "已验证——至少一次实践验证通过",
    "peer-reviewed": "同行评审——经过他人审查确认",
    "deprecated": "已废弃——不再推荐使用",
}

VALID_KNOWLEDGE_TYPES = frozenset(KNOWLEDGE_TYPE_DEFINITIONS.keys())
VALID_VALIDATION_STATUSES = frozenset(VALIDATION_STATUSES.keys())


# ---------------------------------------------------------------------------
# 分类与验证
# ---------------------------------------------------------------------------

def classify_knowledge(
    content: str,
    metadata: dict[str, str | list[str]] | None = None,
) -> str:
    """基于内容特征自动推断知识类型。

    启发式推断规则：
    - 包含大量步骤/操作说明 → procedural
    - 包含决策逻辑/条件判断 → conditional
    - 包含反思/方法论/元分析 → metacognitive
    - 其余 → factual（默认）

    Args:
        content: 正文内容。
        metadata: 可选的元数据字典，用于辅助判断。

    Returns:
        知识类型字符串（factual/procedural/conditional/metacognitive）。
    """
    content_lower = content.lower()

    # 程序性特征：步骤编号、操作动词
    procedural_signals = [
        "步骤", "step", "操作", "执行", "运行", "配置",
        "1.", "2.", "3.", "首先", "然后", "最后",
        "command", "cli", "how to", "教程", "指南",
        "```",  # 代码块
    ]
    procedural_score = sum(1 for s in procedural_signals if s in content_lower)

    # 条件性特征：决策/选择/权衡
    conditional_signals = [
        "取决于", "选择", "权衡", "决策", "场景",
        "when", "if", "适用", "不适用", "对比",
        "trade", "decision", "选择标准", "优先级",
    ]
    conditional_score = sum(1 for s in conditional_signals if s in content_lower)

    # 元认知特征：反思/方法论/模式
    metacognitive_signals = [
        "方法论", "反思", "模式", "洞察", "经验",
        "原则", "思维", "认知", "复盘", "最佳实践",
        "pattern", "insight", "methodology", "principle",
        "lesson", "learned",
    ]
    metacognitive_score = sum(1 for s in metacognitive_signals if s in content_lower)

    scores = {
        "procedural": procedural_score,
        "conditional": conditional_score,
        "metacognitive": metacognitive_score,
    }

    best_type = max(scores, key=scores.get)
    if scores[best_type] >= 3:
        return best_type

    return "factual"


def validate_knowledge_type(knowledge_type: str) -> tuple[bool, str]:
    """验证知识类型是否合法。

    Args:
        knowledge_type: 待验证的知识类型字符串。

    Returns:
        (is_valid, error_msg) 元组。
    """
    if not knowledge_type:
        return False, "知识类型不能为空"
    if knowledge_type not in VALID_KNOWLEDGE_TYPES:
        return False, (
            f"无效的知识类型 '{knowledge_type}'，"
            f"有效值: {', '.join(sorted(VALID_KNOWLEDGE_TYPES))}"
        )
    return True, ""


def validate_validation_status(status: str) -> tuple[bool, str]:
    """验证验证状态是否合法。

    Args:
        status: 待验证的验证状态字符串。

    Returns:
        (is_valid, error_msg) 元组。
    """
    if not status:
        return False, "验证状态不能为空"
    if status not in VALID_VALIDATION_STATUSES:
        return False, (
            f"无效的验证状态 '{status}'，"
            f"有效值: {', '.join(sorted(VALID_VALIDATION_STATUSES))}"
        )
    return True, ""


def get_type_info(knowledge_type: str) -> dict[str, str | list[str]] | None:
    """获取知识类型的详细信息。

    Args:
        knowledge_type: 知识类型字符串。

    Returns:
        包含 label/description/examples/typical_dir 的字典；无效类型返回 None。
    """
    return KNOWLEDGE_TYPE_DEFINITIONS.get(knowledge_type)


def list_all_types() -> list[dict[str, str | list[str]]]:
    """列出所有知识类型及其定义。

    Returns:
        所有知识类型定义列表。
    """
    return [
        {"type": k, **v}
        for k, v in KNOWLEDGE_TYPE_DEFINITIONS.items()
    ]


# ---------------------------------------------------------------------------
# 多维检索
# ---------------------------------------------------------------------------

def filter_by_type(
    entries: list[dict[str, str | list[str]]],
    knowledge_type: str,
) -> list[dict[str, str | list[str]]]:
    """按知识类型筛选条目。

    Args:
        entries: 知识条目元数据列表（每个条目需包含 knowledge_type 字段）。
        knowledge_type: 目标知识类型。

    Returns:
        匹配的条目列表。
    """
    return [
        e for e in entries
        if e.get("knowledge_type", "factual") == knowledge_type
    ]


def filter_by_validation_status(
    entries: list[dict[str, str | list[str]]],
    status: str,
) -> list[dict[str, str | list[str]]]:
    """按验证状态筛选条目。

    Args:
        entries: 知识条目元数据列表（每个条目需包含 validation_status 字段）。
        status: 目标验证状态。

    Returns:
        匹配的条目列表。
    """
    return [
        e for e in entries
        if e.get("validation_status", "draft") == status
    ]


def filter_by_security_level(
    entries: list[dict[str, str | list[str]]],
    level: str,
) -> list[dict[str, str | list[str]]]:
    """按安全级别筛选条目。

    Args:
        entries: 知识条目元数据列表（每个条目需包含 security_level 字段）。
        level: 目标安全级别。

    Returns:
        匹配的条目列表。
    """
    return [
        e for e in entries
        if e.get("security_level", "public") == level
    ]


def multi_filter(
    entries: list[dict[str, str | list[str]]],
    *,
    knowledge_type: str | None = None,
    validation_status: str | None = None,
    security_level: str | None = None,
    tags: list[str] | None = None,
) -> list[dict[str, str | list[str]]]:
    """多维组合筛选。

    所有条件为 AND 关系，None 表示不筛选该维度。

    Args:
        entries: 知识条目元数据列表。
        knowledge_type: 知识类型筛选。
        validation_status: 验证状态筛选。
        security_level: 安全级别筛选。
        tags: 标签筛选（条目需包含所有指定标签）。

    Returns:
        匹配的条目列表。
    """
    result = entries

    if knowledge_type:
        result = filter_by_type(result, knowledge_type)

    if validation_status:
        result = filter_by_validation_status(result, validation_status)

    if security_level:
        result = filter_by_security_level(result, security_level)

    if tags:
        result = [
            e for e in result
            if all(t in (e.get("tags") or []) for t in tags)
        ]

    return result


def compute_classification_stats(
    entries: list[dict[str, str | list[str]]],
) -> dict[str, dict[str, int]]:
    """计算分类统计信息。

    Args:
        entries: 知识条目元数据列表。

    Returns:
        按维度分组的统计字典，格式：
        {
            "by_type": {"factual": N, "procedural": N, ...},
            "by_validation": {"draft": N, "verified": N, ...},
            "by_security": {"public": N, "internal": N, ...},
        }
    """
    by_type: dict[str, int] = {t: 0 for t in VALID_KNOWLEDGE_TYPES}
    by_validation: dict[str, int] = {s: 0 for s in VALID_VALIDATION_STATUSES}
    by_security: dict[str, int] = {"public": 0, "internal": 0, "confidential": 0}

    for entry in entries:
        kt = entry.get("knowledge_type", "factual")
        if isinstance(kt, str) and kt in by_type:
            by_type[kt] += 1

        vs = entry.get("validation_status", "draft")
        if isinstance(vs, str) and vs in by_validation:
            by_validation[vs] += 1

        sl = entry.get("security_level", "public")
        if isinstance(sl, str) and sl in by_security:
            by_security[sl] += 1

    return {
        "by_type": by_type,
        "by_validation": by_validation,
        "by_security": by_security,
    }