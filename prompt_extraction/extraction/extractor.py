"""特征提取模块：从提示词文本中提取结构化特征"""

import re
from prompt_extraction.constants import (
    INSTRUCTION_KEYWORDS,
    IMPERATIVE_PREFIXES,
    CONSTRAINT_TYPE_MAP,
    OUTPUT_KEYWORDS,
    OUTPUT_TYPE_MAP,
    RE_SENTENCE_SPLIT,
)
from prompt_extraction.models import FeatureSet


def _split_sentences(text: str) -> list[str]:
    """将文本拆分为句子，保留中文和英文句末标点"""
    # 按常见句末标点拆分：。！？.!? 以及换行
    sentences = RE_SENTENCE_SPLIT.split(text)
    return [s.strip() for s in sentences if s.strip()]


def _is_imperative_sentence(sentence: str) -> bool:
    """判断是否为祈使句（动词开头）"""
    first_word = sentence.strip().split()[0] if sentence.strip().split() else ""
    return first_word in IMPERATIVE_PREFIXES


def extract_instructions(text: str) -> list[str]:
    """识别核心指令。

    基于以下规则提取指令：
    1. 包含指令关键词（请、要求、需要、帮我、写、生成等）的句子
    2. 以动词开头的祈使句

    Args:
        text: 原始提示词文本

    Returns:
        指令字符串列表
    """
    if not text or not text.strip():
        return []

    sentences = _split_sentences(text)
    instructions = []

    for sentence in sentences:
        stripped = sentence.strip()
        if not stripped:
            continue

        # 规则1：包含指令关键词
        has_keyword = any(kw in stripped for kw in INSTRUCTION_KEYWORDS)
        # 规则2：祈使句开头
        is_imperative = _is_imperative_sentence(stripped)

        if has_keyword or is_imperative:
            instructions.append(stripped)

    return instructions


def _classify_constraint(text: str) -> str:
    """根据约束文本中的关键词判断约束类型"""
    for keyword, ctype in CONSTRAINT_TYPE_MAP.items():
        if keyword in text:
            return ctype
    return "内容约束"


def extract_constraints(text: str) -> list[dict]:
    """识别约束条件。

    基于关键词匹配识别格式约束、内容约束和风格约束。

    Args:
        text: 原始提示词文本

    Returns:
        约束条件列表，每项为 {"type": "约束类型", "text": "约束原文"}
    """
    if not text or not text.strip():
        return []

    sentences = _split_sentences(text)
    constraints = []

    for sentence in sentences:
        stripped = sentence.strip()
        if not stripped:
            continue

        # 检查是否包含任何约束关键词
        has_constraint = any(kw in stripped for kw in CONSTRAINT_TYPE_MAP)
        if has_constraint:
            ctype = _classify_constraint(stripped)
            constraints.append({"type": ctype, "text": stripped})

    return constraints


def extract_expected_output(text: str) -> tuple[str | None, str | None]:
    """识别预期输出格式。

    基于关键词匹配判断输出描述和输出类型。

    Args:
        text: 原始提示词文本

    Returns:
        (输出描述, 输出类型) 或 (None, None)，表示未识别到预期输出
    """
    if not text or not text.strip():
        return None, None

    sentences = _split_sentences(text)
    output_description = None
    output_type = None

    for sentence in sentences:
        stripped = sentence.strip()
        if not stripped:
            continue

        # 检查是否包含输出相关关键词
        has_output_kw = False
        for kw in ["返回", "输出", "格式", "以.*形式", "形式为"]:
            if kw.startswith("以") or kw == "形式为":
                if re.search(kw, stripped):
                    has_output_kw = True
                    break
            elif kw in stripped:
                has_output_kw = True
                break

        if not has_output_kw:
            continue

        # 记录输出描述
        if output_description is None:
            output_description = stripped

        # 检测输出类型
        for type_keyword, type_name in OUTPUT_TYPE_MAP.items():
            if type_keyword in stripped:
                output_type = type_name
                break

    return output_description, output_type


def extract_from_markdown_structure(md_structure: dict) -> FeatureSet:
    """利用 Markdown 结构信息辅助提取特征。

    映射规则：
    - 标题（heading） → 指令分区
    - 列表项（list_item） → 约束或步骤
    - 代码块（code_block） → 预期输出示例

    Args:
        md_structure: Markdown 解析结构字典

    Returns:
        FeatureSet 实例
    """
    features = FeatureSet()

    if not md_structure:
        return features

    # 从标题提取指令
    headings = md_structure.get("headings", [])
    if isinstance(headings, list):
        for heading in headings:
            if isinstance(heading, str):
                features.instructions.append(heading)
            elif isinstance(heading, dict):
                text = heading.get("text", "") or heading.get("content", "")
                if text:
                    features.instructions.append(text)

    # 从列表项提取约束
    list_items = md_structure.get("list_items", [])
    if isinstance(list_items, list):
        for item in list_items:
            if isinstance(item, str):
                ctype = _classify_constraint(item) if any(
                    kw in item for kw in CONSTRAINT_TYPE_MAP
                ) else "内容约束"
                features.constraints.append({"type": ctype, "text": item})
            elif isinstance(item, dict):
                text = item.get("text", "") or item.get("content", "")
                if text:
                    ctype = _classify_constraint(text) if any(
                        kw in text for kw in CONSTRAINT_TYPE_MAP
                    ) else "内容约束"
                    features.constraints.append({"type": ctype, "text": text})

    # 从代码块提取预期输出示例
    code_blocks = md_structure.get("code_blocks", [])
    if isinstance(code_blocks, list) and len(code_blocks) > 0:
        first_block = code_blocks[0]
        if isinstance(first_block, str):
            features.expected_output = first_block
            features.output_type = "代码"
        elif isinstance(first_block, dict):
            lang = first_block.get("language", "") or first_block.get("lang", "")
            code = first_block.get("content", "") or first_block.get("code", "")
            if code:
                features.expected_output = code
                # 根据语言标注推断输出类型
                lang_lower = lang.lower() if lang else ""
                if lang_lower in ("json",):
                    features.output_type = "JSON"
                elif lang_lower in ("html", "xml"):
                    features.output_type = lang.upper()
                elif lang_lower in ("markdown", "md"):
                    features.output_type = "Markdown"
                else:
                    features.output_type = "代码"

    return features


def _merge_features(base: FeatureSet, extra: FeatureSet) -> FeatureSet:
    """合并两个 FeatureSet，避免重复条目"""
    merged = FeatureSet()

    # 合并指令
    seen_instructions = set()
    for instr in base.instructions + extra.instructions:
        if instr not in seen_instructions:
            seen_instructions.add(instr)
            merged.instructions.append(instr)

    # 合并约束
    seen_constraints = set()
    for c in base.constraints + extra.constraints:
        key = (c["type"], c["text"])
        if key not in seen_constraints:
            seen_constraints.add(key)
            merged.constraints.append(c)

    # 合并预期输出：优先使用 Markdown 结构提取的代码块结果
    if extra.expected_output:
        merged.expected_output = extra.expected_output
        merged.output_type = extra.output_type
    elif base.expected_output:
        merged.expected_output = base.expected_output
        merged.output_type = base.output_type

    return merged


def extract_features(
    text: str,
    md_structure: dict | None = None,
) -> FeatureSet:
    """特征提取统一入口。

    先调用基础提取函数从纯文本中提取特征，
    如果 md_structure 不为空，则合并 Markdown 结构提取结果。

    Args:
        text: 原始提示词文本
        md_structure: Markdown 解析结构字典，可选

    Returns:
        FeatureSet 实例
    """
    # 基础提取
    instructions = extract_instructions(text)
    constraints = extract_constraints(text)
    expected_output, output_type = extract_expected_output(text)

    base_features = FeatureSet(
        instructions=instructions,
        constraints=constraints,
        expected_output=expected_output,
        output_type=output_type,
    )

    # 如果提供了 Markdown 结构，合并提取结果
    if md_structure:
        md_features = extract_from_markdown_structure(md_structure)
        return _merge_features(base_features, md_features)

    return base_features