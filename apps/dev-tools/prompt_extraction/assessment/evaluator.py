"""提示词质量评估模块

提供清晰度、完整性、可执行性三个维度的质量评估，
以及综合评分与等级判定功能。
"""

from prompt_extraction.config import (
    CLARITY_WEIGHT,
    COMPLETENESS_WEIGHT,
    EXECUTABILITY_WEIGHT,
    GRADE_THRESHOLDS,
)
from prompt_extraction.constants import (
    AMBIGUOUS_WORDS,
    ACTION_VERBS,
    BACKGROUND_KEYWORDS,
    EXAMPLE_KEYWORDS,
    VERIFIABLE_CONSTRAINT_KEYWORDS,
    TEXT_TOO_SHORT_LENGTH,
    TEXT_TOO_LONG_LENGTH,
    SCORE_DEDUCTION_TOO_SHORT,
    SCORE_DEDUCTION_TOO_LONG,
    SCORE_DEDUCTION_PER_MISSING_STRUCTURE,
    SCORE_DEDUCTION_PER_AMBIGUOUS,
    SCORE_DEDUCTION_AMBIGUOUS_MAX,
    SCORE_INSTRUCTION,
    SCORE_CONSTRAINT,
    SCORE_CONTEXT,
    SCORE_EXAMPLE,
    SCORE_OUTPUT_FORMAT,
    CONTEXT_LENGTH_THRESHOLD,
    VERB_SCORE_PER,
    VERB_SCORE_MAX,
    CONSTRAINT_VERIFIABLE_SCORE_MAX,
    OUTPUT_DETERMINABLE_SCORE,
    OUTPUT_TYPE_PARTIAL_SCORE,
    RE_HEADING,
    RE_PARAGRAPH_SPLIT,
    RE_LIST_MARKER,
    RE_DIGIT,
)
from prompt_extraction.messages import (
    SUGGEST_TEXT_TOO_SHORT,
    SUGGEST_TEXT_TOO_LONG,
    SUGGEST_MISSING_STRUCTURE,
    SUGGEST_AMBIGUOUS_WORDS,
    SUGGEST_MISSING_INSTRUCTION,
    SUGGEST_MISSING_CONSTRAINT,
    SUGGEST_MISSING_CONTEXT,
    SUGGEST_MISSING_EXAMPLE,
    SUGGEST_MISSING_OUTPUT_FORMAT,
    SUGGEST_MISSING_VERBS,
    SUGGEST_UNVERIFIABLE_CONSTRAINT,
    SUGGEST_NO_CONSTRAINT,
    SUGGEST_OUTPUT_NOT_CLEAR,
    SUGGEST_NO_OUTPUT_FORMAT,
)
from prompt_extraction.models import FeatureSet, QualityScore


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
    if length < TEXT_TOO_SHORT_LENGTH:
        score -= SCORE_DEDUCTION_TOO_SHORT
        suggestions.append(SUGGEST_TEXT_TOO_SHORT.format(text_len=length))
    elif length > TEXT_TOO_LONG_LENGTH:
        score -= SCORE_DEDUCTION_TOO_LONG
        suggestions.append(SUGGEST_TEXT_TOO_LONG.format(text_len=length))

    # --- 2. 结构层次评估 ---
    has_headings = bool(RE_HEADING.search(text))
    has_paragraphs = len(RE_PARAGRAPH_SPLIT.split(text)) >= 2
    has_lists = bool(RE_LIST_MARKER.search(text))

    missing_structure = []
    if not has_headings:
        missing_structure.append("标题/章节划分")
    if not has_paragraphs:
        missing_structure.append("段落分隔")
    if not has_lists:
        missing_structure.append("列表/编号")

    if missing_structure:
        deduction = len(missing_structure) * SCORE_DEDUCTION_PER_MISSING_STRUCTURE
        score -= deduction
        suggestions.append(
            SUGGEST_MISSING_STRUCTURE.format(missing="、".join(missing_structure))
        )

    # --- 3. 歧义度评估 ---
    found_ambiguous = [w for w in AMBIGUOUS_WORDS if w in text]
    if found_ambiguous:
        deduction = min(len(found_ambiguous) * SCORE_DEDUCTION_PER_AMBIGUOUS, SCORE_DEDUCTION_AMBIGUOUS_MAX)
        score -= deduction
        suggestions.append(
            SUGGEST_AMBIGUOUS_WORDS.format(words="、".join(found_ambiguous))
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

    # --- 1. 指令要素 ---
    if features.instructions:
        score += SCORE_INSTRUCTION
    else:
        suggestions.append(SUGGEST_MISSING_INSTRUCTION)

    # --- 2. 约束要素 ---
    if features.constraints:
        score += SCORE_CONSTRAINT
    else:
        suggestions.append(SUGGEST_MISSING_CONSTRAINT)

    # --- 3. 上下文要素 ---
    has_context = len(text) > CONTEXT_LENGTH_THRESHOLD or any(kw in text for kw in BACKGROUND_KEYWORDS)
    if has_context:
        score += SCORE_CONTEXT
    else:
        suggestions.append(SUGGEST_MISSING_CONTEXT)

    # --- 4. 示例要素 ---
    has_examples = any(kw in text for kw in EXAMPLE_KEYWORDS)
    if has_examples:
        score += SCORE_EXAMPLE
    else:
        suggestions.append(SUGGEST_MISSING_EXAMPLE)

    # --- 5. 输出格式要素 ---
    if features.expected_output:
        score += SCORE_OUTPUT_FORMAT
    else:
        suggestions.append(SUGGEST_MISSING_OUTPUT_FORMAT)

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

    # --- 1. 指令可操作性 ---
    found_verbs = [v for v in ACTION_VERBS if v in text]
    if found_verbs:
        verb_score = min(len(found_verbs) * VERB_SCORE_PER, VERB_SCORE_MAX)
        score += verb_score
    else:
        suggestions.append(SUGGEST_MISSING_VERBS)

    # --- 2. 约束可验证性 ---
    if features.constraints:
        verifiable_count = 0
        for constraint in features.constraints:
            constraint_text = str(constraint)
            if RE_DIGIT.search(constraint_text) or any(
                kw in constraint_text for kw in VERIFIABLE_CONSTRAINT_KEYWORDS
            ):
                verifiable_count += 1

        if verifiable_count > 0:
            ratio = verifiable_count / len(features.constraints)
            constraint_score = min(ratio * CONSTRAINT_VERIFIABLE_SCORE_MAX, CONSTRAINT_VERIFIABLE_SCORE_MAX)
            score += constraint_score
        else:
            suggestions.append(SUGGEST_UNVERIFIABLE_CONSTRAINT)
    else:
        suggestions.append(SUGGEST_NO_CONSTRAINT)

    # --- 3. 输出可判定性 ---
    if features.expected_output:
        score += OUTPUT_DETERMINABLE_SCORE
    elif features.output_type:
        score += OUTPUT_TYPE_PARTIAL_SCORE
        suggestions.append(SUGGEST_OUTPUT_NOT_CLEAR)
    else:
        suggestions.append(SUGGEST_NO_OUTPUT_FORMAT)

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