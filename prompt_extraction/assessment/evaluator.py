"""提示词质量评估模块

提供清晰度、完整性、可执行性三个维度的质量评估，
以及综合评分与等级判定功能。
"""

import re

from prompt_extraction.config import (
    CLARITY_WEIGHT,
    COMPLETENESS_WEIGHT,
    EXECUTABILITY_WEIGHT,
    GRADE_THRESHOLDS,
)
from prompt_extraction.models import FeatureSet, QualityScore

# ============================================================================
# 模糊词汇列表（用于清晰度评估中的歧义检测）
# ============================================================================
_AMBIGUOUS_WORDS = [
    "可能", "大概", "也许", "差不多", "一些",
    "或许", "好像", "似乎", "某种", "某种程度",
    "若干", "左右", "大约", "估计", "大致",
]

# ============================================================================
# 动作动词列表（用于可执行性评估中的指令可操作性检测）
# ============================================================================
_ACTION_VERBS = [
    "生成", "创建", "编写", "分析", "计算", "提取",
    "总结", "翻译", "转换", "设计", "开发", "实现",
    "构建", "修改", "优化", "查找", "搜索", "回答",
    "解释", "描述", "列出", "排序", "分类", "比较",
    "验证", "检查", "评估", "审查", "重构", "部署",
    "配置", "安装", "运行", "执行", "测试", "调试",
    "导出", "导入", "解析", "处理", "读取", "写入",
    "绘制", "展示", "输出", "格式化", "整理", "归纳",
    "推导", "推断", "预测", "推荐", "筛选", "过滤",
]

# ============================================================================
# 背景描述关键词（用于完整性评估中的上下文检测）
# ============================================================================
_BACKGROUND_KEYWORDS = [
    "背景", "概述", "简介", "当前", "目前",
    "场景", "角色", "设定", "环境", "上下文",
    "前提", "前置条件", "假设", "已知", "现状",
    "需求", "目标", "目的", "问题", "痛点",
]


def evaluate_clarity(text: str) -> tuple[float, list[str]]:
    """评估提示词的清晰度。

    基于以下维度进行评分：
    - 文本长度：过短（<20字）大幅扣分，过长（>500字）适当扣分
    - 结构层次：是否有标题、段落分隔、列表等结构元素
    - 歧义度：是否包含模糊词汇

    参数：
        text: 提示词文本。

    返回：
        (评分 0-100, 改进建议列表)。
    """
    score = 100.0
    suggestions = []

    # --- 1. 文本长度评估 ---
    length = len(text)
    if length < 20:
        score -= 40
        suggestions.append(f"文本过短（当前{length}字），建议补充更多细节和明确要求")
    elif length > 500:
        score -= 10
        suggestions.append(f"文本过长（当前{length}字），建议精简至核心要点，避免冗余信息")

    # --- 2. 结构层次评估 ---
    has_headings = bool(re.search(r"^#{1,6}\s", text, re.MULTILINE))
    has_paragraphs = len(re.split(r"\n\s*\n", text)) >= 2
    has_lists = bool(re.search(r"^[\-\*\+]\s|^\d+\.\s", text, re.MULTILINE))

    missing_structure = []
    if not has_headings:
        missing_structure.append("标题/章节划分")
    if not has_paragraphs:
        missing_structure.append("段落分隔")
    if not has_lists:
        missing_structure.append("列表/编号")

    if missing_structure:
        deduction = len(missing_structure) * 10
        score -= deduction
        suggestions.append(
            f"缺少结构元素：{'、'.join(missing_structure)}，"
            "建议使用标题、分段和列表组织内容，提升可读性"
        )

    # --- 3. 歧义度评估 ---
    found_ambiguous = [w for w in _AMBIGUOUS_WORDS if w in text]
    if found_ambiguous:
        deduction = min(len(found_ambiguous) * 5, 30)
        score -= deduction
        suggestions.append(
            f"包含模糊词汇：{'、'.join(found_ambiguous)}，"
            "建议使用明确、具体的表述替代，避免歧义"
        )

    score = max(0.0, min(100.0, score))
    return (score, suggestions)


def evaluate_completeness(text: str, features: FeatureSet) -> tuple[float, list[str]]:
    """评估提示词的完整性。

    基于以下五个要素进行评分，每项各占 20 分：
    - 指令：features.instructions 是否非空
    - 约束：features.constraints 是否非空
    - 上下文：文本长度 > 50 字或包含背景描述
    - 示例：文本中是否包含"例如"、"比如"、"示例"等关键词
    - 输出格式：features.expected_output 是否非空

    参数：
        text: 提示词文本。
        features: 从提示词中提取的特征集。

    返回：
        (评分 0-100, 改进建议列表)。
    """
    score = 0.0
    suggestions = []

    # --- 1. 指令要素（20分）---
    if features.instructions:
        score += 20
    else:
        suggestions.append('缺少明确指令，建议添加具体的操作要求（如"生成"、"分析"、"翻译"等）')

    # --- 2. 约束要素（20分）---
    if features.constraints:
        score += 20
    else:
        suggestions.append("缺少约束条件，建议添加对输出格式、长度、风格等方面的限制要求")

    # --- 3. 上下文要素（20分）---
    has_context = len(text) > 50 or any(kw in text for kw in _BACKGROUND_KEYWORDS)
    if has_context:
        score += 20
    else:
        suggestions.append("缺少上下文信息，建议补充背景描述、使用场景或目标受众等说明")

    # --- 4. 示例要素（20分）---
    has_examples = any(kw in text for kw in ["例如", "比如", "示例", "举例", "如", "像"])
    if has_examples:
        score += 20
    else:
        suggestions.append("缺少示例，建议添加输入/输出示例以明确期望效果")

    # --- 5. 输出格式要素（20分）---
    if features.expected_output:
        score += 20
    else:
        suggestions.append("缺少输出格式说明，建议明确指定期望的输出结构（如 JSON、Markdown、列表等）")

    return (score, suggestions)


def evaluate_executability(text: str, features: FeatureSet) -> tuple[float, list[str]]:
    """评估提示词的可执行性。

    基于以下三个维度进行评分，每项约 33 分：
    - 指令可操作性：文本中是否包含具体的动作动词
    - 约束可验证性：约束是否有明确的标准或条件
    - 输出可判定性：是否可通过 features.expected_output 或 output_type 判定输出格式

    参数：
        text: 提示词文本。
        features: 从提示词中提取的特征集。

    返回：
        (评分 0-100, 改进建议列表)。
    """
    score = 0.0
    suggestions = []

    # --- 1. 指令可操作性（33分）---
    found_verbs = [v for v in _ACTION_VERBS if v in text]
    if found_verbs:
        # 动作动词越多，可操作性越强，上限 33 分
        verb_score = min(len(found_verbs) * 5, 33)
        score += verb_score
    else:
        suggestions.append('缺少可操作的动作指令，建议使用具体动词（如"生成"、"分析"、"翻译"）明确操作')

    # --- 2. 约束可验证性（33分）---
    if features.constraints:
        # 检查约束是否包含可验证的标准
        verifiable_count = 0
        for constraint in features.constraints:
            constraint_text = str(constraint)
            # 包含数字、范围、明确条件等视为可验证
            if re.search(r"\d+", constraint_text) or any(
                kw in constraint_text for kw in ["必须", "不能", "不得", "要求", "限制", "不超过", "至少", "严格", "精确"]
            ):
                verifiable_count += 1

        if verifiable_count > 0:
            # 可验证约束越多，分数越高
            ratio = verifiable_count / len(features.constraints)
            constraint_score = min(ratio * 33, 33)
            score += constraint_score
        else:
            suggestions.append("约束条件不够明确可验证，建议添加具体数值、范围或明确标准")
    else:
        suggestions.append("缺少约束条件，无法评估可验证性，建议添加明确的限制条件")

    # --- 3. 输出可判定性（34分）---
    if features.expected_output:
        score += 34
    elif features.output_type:
        score += 17
        suggestions.append("输出格式不够明确，建议补充具体的输出示例或格式说明")
    else:
        suggestions.append("缺少输出格式定义，建议明确指定输出类型（如 JSON、Markdown、纯文本等）")

    score = min(score, 100.0)
    return (score, suggestions)


def evaluate(text: str, features: FeatureSet) -> QualityScore:
    """综合评估提示词质量。

    依次调用清晰度、完整性、可执行性三个维度的评估函数，
    按 config.py 中定义的权重计算综合评分，根据 GRADE_THRESHOLDS 判定等级。

    参数：
        text: 提示词文本。
        features: 从提示词中提取的特征集。

    返回：
        QualityScore 实例，包含各维度评分、综合评分、等级和汇总改进建议。
    """
    clarity_score, clarity_suggestions = evaluate_clarity(text)
    completeness_score, completeness_suggestions = evaluate_completeness(text, features)
    executability_score, executability_suggestions = evaluate_executability(text, features)

    # 加权计算综合评分
    overall = (
        clarity_score * CLARITY_WEIGHT
        + completeness_score * COMPLETENESS_WEIGHT
        + executability_score * EXECUTABILITY_WEIGHT
    )
    overall = round(overall, 1)

    # 根据阈值判定等级
    grade = "差"
    # 按阈值从高到低排序，确保正确匹配
    for grade_name in sorted(GRADE_THRESHOLDS.keys(), key=lambda k: GRADE_THRESHOLDS[k], reverse=True):
        if overall >= GRADE_THRESHOLDS[grade_name]:
            grade = grade_name
            break

    # 汇总所有改进建议
    all_suggestions = []
    all_suggestions.extend(clarity_suggestions)
    all_suggestions.extend(completeness_suggestions)
    all_suggestions.extend(executability_suggestions)

    return QualityScore(
        clarity=clarity_score,
        completeness=completeness_score,
        executability=executability_score,
        overall=overall,
        grade=grade,
        suggestions=all_suggestions,
    )