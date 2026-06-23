"""特征提取模块：从提示词文本中提取结构化特征"""

import re
from prompt_extraction.models import FeatureSet

# ── 指令关键词 ──────────────────────────────────────────────
_INSTRUCTION_KEYWORDS = [
    "请", "要求", "需要", "帮我", "写", "生成", "创建",
    "分析", "总结", "翻译", "解释", "描述", "列出", "比较",
    "设计", "实现", "修改", "优化", "重构", "测试", "部署",
    "计算", "评估", "推荐", "搜索", "查找", "提取", "转换",
    "回答", "说明", "阐述", "论述", "展示", "演示",
]

# ── 约束关键词 → 约束类型映射 ────────────────────────────────
_CONSTRAINT_TYPE_MAP = {
    # 格式约束
    "格式": "格式约束", "字数": "格式约束", "长度": "格式约束",
    "最多": "格式约束", "最少": "格式约束", "不超过": "格式约束",
    "不少于": "格式约束", "限制在": "格式约束", "字符": "格式约束",
    "JSON": "格式约束", "json": "格式约束",
    "列表": "格式约束", "表格": "格式约束", "代码": "格式约束",
    "段落": "格式约束", "标题": "格式约束", "编号": "格式约束",
    "分段": "格式约束", "缩进": "格式约束", "标点": "格式约束",
    # 内容约束
    "必须": "内容约束", "不能": "内容约束", "不要": "内容约束",
    "禁止": "内容约束", "限制": "内容约束", "不允许": "内容约束",
    "角色": "内容约束", "身份": "内容约束", "作为": "内容约束",
    "充当": "内容约束", "扮演": "内容约束",
    "包含": "内容约束", "不包括": "内容约束", "涵盖": "内容约束",
    "基于": "内容约束", "参考": "内容约束", "依据": "内容约束",
    "仅用": "内容约束", "只使用": "内容约束", "仅限": "内容约束",
    "避免": "内容约束", "忽略": "内容约束", "排除": "内容约束",
    "主题": "内容约束", "领域": "内容约束", "范围": "内容约束",
    "背景": "内容约束", "上下文": "内容约束",
    # 风格约束
    "风格": "风格约束", "语言": "风格约束", "语气": "风格约束",
    "口吻": "风格约束", "语调": "风格约束", "文风": "风格约束",
    "正式": "风格约束", "非正式": "风格约束", "口语": "风格约束",
    "书面": "风格约束", "专业": "风格约束", "幽默": "风格约束",
    "严肃": "风格约束", "亲切": "风格约束", "简洁": "风格约束",
    "详细": "风格约束", "通俗": "风格约束", "学术": "风格约束",
    "中文": "风格约束", "英文": "风格约束", "中英": "风格约束",
    "英文翻译": "风格约束",
}

# ── 预期输出关键词 ──────────────────────────────────────────
_OUTPUT_KEYWORDS = [
    "返回", "输出", "格式", "以.*形式", "形式为",
    "JSON", "列表", "表格", "代码", "文本", "段落",
    "Markdown", "markdown", "HTML", "XML", "YAML", "CSV",
    "数组", "对象", "字典", "字符串", "数字",
]

# ── 输出类型映射 ────────────────────────────────────────────
_OUTPUT_TYPE_MAP = {
    "JSON": "JSON", "json": "JSON",
    "列表": "列表", "清单": "列表",
    "表格": "表格", "表": "表格",
    "代码": "代码", "程序": "代码", "脚本": "代码",
    "Markdown": "Markdown", "markdown": "Markdown",
    "HTML": "HTML", "html": "HTML",
    "XML": "XML", "xml": "XML",
    "YAML": "YAML", "yaml": "YAML",
    "CSV": "CSV", "csv": "CSV",
    "文本": "文本", "段落": "文本", "文字": "文本",
}


def _split_sentences(text: str) -> list[str]:
    """将文本拆分为句子，保留中文和英文句末标点"""
    # 按常见句末标点拆分：。！？.!? 以及换行
    sentences = re.split(r'(?<=[。！？.!?\n])', text)
    return [s.strip() for s in sentences if s.strip()]


def _is_imperative_sentence(sentence: str) -> bool:
    """判断是否为祈使句（动词开头）"""
    # 常见祈使动词前缀
    imperative_prefixes = [
        "写", "生成", "创建", "分析", "总结", "翻译", "解释",
        "描述", "列出", "比较", "设计", "实现", "修改", "优化",
        "重构", "测试", "部署", "计算", "评估", "推荐", "搜索",
        "查找", "提取", "转换", "回答", "说明", "阐述", "论述",
        "展示", "演示", "定义", "构造", "构建", "组装", "绘制",
        "启动", "停止", "运行", "执行", "安装", "配置", "设置",
        "打开", "关闭", "保存", "删除", "复制", "移动", "检查",
        "验证", "确认", "确保", "选择", "输入", "键入", "导入",
        "导出", "读取", "发送", "接收", "调用", "返回",
    ]
    first_word = sentence.strip().split()[0] if sentence.strip().split() else ""
    return first_word in imperative_prefixes


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
        has_keyword = any(kw in stripped for kw in _INSTRUCTION_KEYWORDS)
        # 规则2：祈使句开头
        is_imperative = _is_imperative_sentence(stripped)

        if has_keyword or is_imperative:
            instructions.append(stripped)

    return instructions


def _classify_constraint(text: str) -> str:
    """根据约束文本中的关键词判断约束类型"""
    for keyword, ctype in _CONSTRAINT_TYPE_MAP.items():
        if keyword in text:
            return ctype
    return "内容约束"  # 默认归类为内容约束


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
        has_constraint = any(kw in stripped for kw in _CONSTRAINT_TYPE_MAP)
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
        for type_keyword, type_name in _OUTPUT_TYPE_MAP.items():
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
                    kw in item for kw in _CONSTRAINT_TYPE_MAP
                ) else "内容约束"
                features.constraints.append({"type": ctype, "text": item})
            elif isinstance(item, dict):
                text = item.get("text", "") or item.get("content", "")
                if text:
                    ctype = _classify_constraint(text) if any(
                        kw in text for kw in _CONSTRAINT_TYPE_MAP
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