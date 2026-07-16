"""提示词优化生成模块

提供提示词质量判定、缺失要素补充、歧义消除、结构重组和差异对比等优化功能。
"""

from prompt_extraction.config import QUALITY_THRESHOLD
from prompt_extraction.constants import AMBIGUITY_MAP, CONTEXT_EXTRACT_KEYWORDS
from prompt_extraction.messages import (
    IMPROVE_DISAMBIGUATE,
    IMPROVE_RESTRUCTURE,
    IMPROVE_SUPPLEMENT,
)
from prompt_extraction.models import FeatureSet, OptimizationResult, PromptRecord, QualityScore


# ============================================================================
# 优化判定
# ============================================================================


def should_optimize(quality: QualityScore) -> bool:
    """判断是否需要触发优化。

    当综合评分低于 QUALITY_THRESHOLD（60）时返回 True，
    否则返回 False。

    Args:
        quality: 质量评分实例

    Returns:
        是否需要优化
    """
    return quality.overall < QUALITY_THRESHOLD


# ============================================================================
# 缺失要素补充
# ============================================================================


def _infer_output_format(text: str) -> str:
    """根据文本内容推断输出格式说明。

    Args:
        text: 原始文本

    Returns:
        推断出的输出格式说明文本
    """
    text_lower = text.lower()

    if "json" in text_lower:
        return "请以 JSON 格式输出，包含明确的字段名和结构化数据。"
    if "markdown" in text_lower or "md" in text_lower:
        return "请以 Markdown 格式输出，使用标题、列表、代码块等结构化元素。"
    if "列表" in text:
        return "请以列表形式输出，逐条列出各项内容。"
    if "代码" in text:
        return "请输出完整的代码，包含必要的注释和错误处理。"
    if "报告" in text:
        return "请以结构化报告格式输出，包含摘要、正文和结论。"
    if "表格" in text:
        return "请以表格形式输出，列标题清晰，数据对齐。"
    if "翻译" in text:
        return "请输出翻译结果，保持原文格式和语义。"
    if "总结" in text or "摘要" in text:
        return "请以简洁的段落形式输出总结内容。"
    # 默认推断
    return "请以清晰、结构化的文本格式输出，包含必要的标题和段落分隔。"


def _detect_implicit_constraints(text: str) -> list[str]:
    """检测文本中的隐含约束并将其显式化。

    Args:
        text: 原始文本

    Returns:
        显式化的约束列表
    """
    constraints: list[str] = []

    # 检测"必须"类约束
    if "必须" in text:
        constraints.append("请严格遵守所有「必须」类要求，不可遗漏。")

    # 检测数量/范围类约束
    if any(kw in text for kw in ("不超过", "至少", "最多", "最少", "不少于", "不多于")):
        constraints.append("请严格遵守文本中指定的数量、范围、长度等限制条件。")

    # 检测格式类约束
    if any(kw in text for kw in ("JSON", "Markdown", "YAML", "XML", "CSV", "表格")):
        constraints.append("请严格按照指定的格式输出，确保格式正确、可解析。")

    # 检测"不能"/"禁止"类约束
    if any(kw in text for kw in ("不能", "禁止", "不允许", "切勿", "不要")):
        constraints.append("请严格遵守所有禁止性要求，避免出现被禁止的内容。")

    # 检测"例如"/"比如"类约束（示例约束）
    if any(kw in text for kw in ("例如", "比如", "如", "示例")):
        constraints.append("请参考文本中提供的示例格式和风格进行输出。")

    return constraints


def supplement_missing_elements(text: str, features: FeatureSet) -> str:
    """补充缺失要素。

    如果 features.expected_output 为空，根据上下文推断并补充合理的输出格式说明；
    如果 features.constraints 为空，检测是否有隐含约束并显式化。

    Args:
        text: 原始文本
        features: 特征集

    Returns:
        补充后的文本
    """
    result = text

    # 补充缺失的输出格式
    if not features.expected_output:
        output_format = _infer_output_format(text)
        if not result.endswith("\n"):
            result += "\n"
        result += f"\n{output_format}"

    # 补充缺失的约束
    if not features.constraints:
        implicit = _detect_implicit_constraints(text)
        if implicit:
            if not result.endswith("\n"):
                result += "\n"
            result += "\n## 约束\n"
            for constraint in implicit:
                result += f"- {constraint}\n"

    return result


# ============================================================================
# 歧义消除
# ============================================================================


def disambiguate(text: str) -> str:
    """消除歧义增强。

    检测并改写模糊表述，将歧义表述替换为更精确、可操作的表述。

    替换规则：
    - "可能"/"也许"/"或许" → "请明确判断"
    - "大概"/"大致" → "请明确说明"
    - "差不多"/"基本上" → "精确地"
    - "一些"/"几个"/"若干" → "列出所有"
    - "左右" → "精确地"

    Args:
        text: 原始文本

    Returns:
        消歧后的文本
    """
    result = text
    # 按键长度降序排列，优先匹配长词，避免短词误匹配
    sorted_keys = sorted(AMBIGUITY_MAP.keys(), key=len, reverse=True)
    for ambiguous in sorted_keys:
        replacement = AMBIGUITY_MAP[ambiguous]
        result = result.replace(ambiguous, replacement)
    return result


# ============================================================================
# 结构重组
# ============================================================================


def _extract_context(text: str) -> str:
    """从文本中提取上下文/背景信息。

    Args:
        text: 原始文本

    Returns:
        提取的上下文文本，无上下文时返回空字符串
    """
    lines = text.split("\n")
    context_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped and any(stripped.startswith(kw) for kw in CONTEXT_EXTRACT_KEYWORDS):
            context_lines.append(stripped)
    return "\n".join(context_lines)


def restructure(text: str, features: FeatureSet) -> str:
    """将结构混乱的提示词重组为标准 Markdown 结构。

    标准结构：
    ## 指令
    ...
    ## 约束
    ...
    ## 上下文
    ...
    ## 输出格式
    ...

    Args:
        text: 原始文本
        features: 特征集

    Returns:
        重组后的标准 Markdown 文本
    """
    sections: list[str] = []

    # 指令章节
    if features.instructions:
        sections.append("## 指令")
        for instr in features.instructions:
            sections.append(f"- {instr}")
        sections.append("")
    elif text.strip():
        # 无指令特征时，将原始文本的核心内容作为指令
        sections.append("## 指令")
        sections.append(text.strip())
        sections.append("")

    # 约束章节
    if features.constraints:
        sections.append("## 约束")
        for constraint in features.constraints:
            if isinstance(constraint, dict):
                value = constraint.get("value", str(constraint))
                sections.append(f"- {value}")
            else:
                sections.append(f"- {constraint}")
        sections.append("")

    # 上下文章节
    context = _extract_context(text)
    if context:
        sections.append("## 上下文")
        sections.append(context)
        sections.append("")

    # 输出格式章节
    if features.expected_output:
        sections.append("## 输出格式")
        sections.append(features.expected_output)
        sections.append("")

    # 如果所有章节都为空，保留原始文本作为指令
    if not sections:
        sections.append("## 指令")
        sections.append(text.strip())
        sections.append("")

    return "\n".join(sections).rstrip()


# ============================================================================
# 差异对比
# ============================================================================


def generate_diff(original: str, optimized: str) -> str:
    """生成优化前后对比 diff。

    逐行比较，标注新增/修改的行：
    - 以 + 前缀表示新增行
    - 以 - 前缀表示删除行
    - 空行表示未变更行

    Args:
        original: 优化前文本
        optimized: 优化后文本

    Returns:
        diff 格式的对比文本
    """
    import difflib

    original_lines = original.splitlines()
    optimized_lines = optimized.splitlines()

    diff_result: list[str] = []
    matcher = difflib.SequenceMatcher(None, original_lines, optimized_lines)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            # 相同行：输出空行
            diff_result.extend([""] * (i2 - i1))
        elif tag == "replace":
            # 替换：先输出删除行，再输出新增行
            for idx in range(i1, i2):
                diff_result.append(f"-{original_lines[idx]}")
            for idx in range(j1, j2):
                diff_result.append(f"+{optimized_lines[idx]}")
        elif tag == "delete":
            # 删除
            for idx in range(i1, i2):
                diff_result.append(f"-{original_lines[idx]}")
        elif tag == "insert":
            # 新增
            for idx in range(j1, j2):
                diff_result.append(f"+{optimized_lines[idx]}")

    return "\n".join(diff_result)


# ============================================================================
# 统一优化入口
# ============================================================================


def optimize(record: PromptRecord) -> OptimizationResult:
    """统一优化入口。

    如果 should_optimize 返回 True，依次调用：
    1. 补充缺失要素（supplement_missing_elements）
    2. 消歧增强（disambiguate）
    3. 结构调整（restructure）
    然后生成优化前后对比 diff。

    如果不需要优化，返回 triggered=False 的空结果。

    Args:
        record: 提示词记录

    Returns:
        OptimizationResult 实例
    """
    if not should_optimize(record.quality):
        return OptimizationResult(triggered=False)

    # 使用清洗后的文本，若为空则回退到原始文本
    source_text = record.cleaned_text or record.original_text

    improvements: list[str] = []

    # 步骤一：补充缺失要素
    supplemented = supplement_missing_elements(source_text, record.features)
    if supplemented != source_text:
        improvements.append(IMPROVE_SUPPLEMENT)
        source_text = supplemented

    # 步骤二：消除歧义
    disambiguated = disambiguate(source_text)
    if disambiguated != source_text:
        improvements.append(IMPROVE_DISAMBIGUATE)
        source_text = disambiguated

    # 步骤三：结构重组
    restructured = restructure(source_text, record.features)
    if restructured != source_text:
        improvements.append(IMPROVE_RESTRUCTURE)
        source_text = restructured

    # 生成对比 diff
    original_text = record.cleaned_text or record.original_text
    diff = generate_diff(original_text, source_text)

    return OptimizationResult(
        triggered=True,
        optimized_text=source_text,
        improvements=improvements,
        diff=diff,
    )