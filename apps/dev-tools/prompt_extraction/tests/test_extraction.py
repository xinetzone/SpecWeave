"""特征提取模块单元测试"""

import pytest
from prompt_extraction.extraction.extractor import (
    extract_instructions,
    extract_constraints,
    extract_expected_output,
    extract_from_markdown_structure,
    extract_features,
)
from prompt_extraction.models import FeatureSet


# ═══════════════════════════════════════════════════════════════
# extract_instructions 测试
# ═══════════════════════════════════════════════════════════════

class TestExtractInstructions:
    """测试指令提取功能"""

    def test_明确指令_关键词_请(self):
        """包含"请"关键词的提示词应被识别为指令"""
        text = "请帮我写一份关于人工智能的报告。"
        result = extract_instructions(text)
        assert len(result) == 1
        assert "请帮我写一份关于人工智能的报告" in result[0]

    def test_明确指令_关键词_生成(self):
        """包含"生成"关键词的提示词应被识别为指令"""
        text = "生成一份用户增长分析报告。"
        result = extract_instructions(text)
        assert len(result) == 1
        assert "生成一份用户增长分析报告" in result[0]

    def test_明确指令_祈使句开头(self):
        """以动词开头的祈使句应被识别为指令"""
        text = "分析以下数据并总结关键趋势。"
        result = extract_instructions(text)
        assert len(result) == 1
        assert "分析以下数据并总结关键趋势" in result[0]

    def test_明确指令_多句混合(self):
        """多句提示词中应正确提取所有指令句"""
        text = "请帮我写一篇技术文章。主题是微服务架构。分析现有系统的优缺点。"
        result = extract_instructions(text)
        assert len(result) >= 2
        # 应包含"请帮我写一篇技术文章"和"分析现有系统的优缺点"
        assert any("请帮我写一篇技术文章" in r for r in result)
        assert any("分析现有系统的优缺点" in r for r in result)

    def test_无指令_普通陈述句(self):
        """普通陈述句不应被识别为指令"""
        text = "今天天气很好，适合出去散步。"
        result = extract_instructions(text)
        assert len(result) == 0

    def test_空文本(self):
        """空文本应返回空列表"""
        result = extract_instructions("")
        assert result == []

    def test_空白文本(self):
        """仅包含空白的文本应返回空列表"""
        result = extract_instructions("   \n  \t  ")
        assert result == []

    def test_仅换行符(self):
        """仅包含换行符的文本应返回空列表"""
        result = extract_instructions("\n\n\n")
        assert result == []


# ═══════════════════════════════════════════════════════════════
# extract_constraints 测试
# ═══════════════════════════════════════════════════════════════

class TestExtractConstraints:
    """测试约束条件提取功能"""

    def test_格式约束_字数限制(self):
        """包含字数限制的提示词应被识别为格式约束"""
        text = "回答字数不能超过500字。"
        result = extract_constraints(text)
        assert len(result) == 1
        assert result[0]["type"] == "格式约束"
        assert "500字" in result[0]["text"]

    def test_格式约束_输出格式(self):
        """包含输出格式要求的提示词应被识别为格式约束"""
        text = "请以JSON格式返回结果。"
        result = extract_constraints(text)
        assert len(result) == 1
        assert result[0]["type"] == "格式约束"

    def test_内容约束_必须包含(self):
        """包含"必须"关键词的提示词应被识别为内容约束"""
        text = "报告必须包含数据分析部分。"
        result = extract_constraints(text)
        assert len(result) == 1
        assert result[0]["type"] == "内容约束"
        assert "必须包含" in result[0]["text"]

    def test_内容约束_不能(self):
        """包含"不能"关键词的提示词应被识别为内容约束"""
        text = "不能包含任何敏感信息。"
        result = extract_constraints(text)
        assert len(result) == 1
        assert result[0]["type"] == "内容约束"

    def test_风格约束_语气(self):
        """包含语气要求的提示词应被识别为风格约束"""
        text = "请使用正式专业的语气撰写。"
        result = extract_constraints(text)
        assert len(result) == 1
        assert result[0]["type"] == "风格约束"

    def test_风格约束_语言(self):
        """包含语言要求的提示词应被识别为风格约束"""
        text = "请用中文回答。"
        result = extract_constraints(text)
        assert len(result) == 1
        assert result[0]["type"] == "风格约束"

    def test_多约束混合(self):
        """多约束混合的提示词应正确分类"""
        text = "请用中文写一份报告。字数不超过1000字。必须包含数据分析。语气要正式。"
        result = extract_constraints(text)
        assert len(result) >= 2
        types = [c["type"] for c in result]
        assert "格式约束" in types
        assert "风格约束" in types

    def test_无约束_普通文本(self):
        """普通文本不应识别到约束"""
        text = "这是一段普通的描述文字。"
        result = extract_constraints(text)
        assert len(result) == 0

    def test_空文本(self):
        """空文本应返回空列表"""
        result = extract_constraints("")
        assert result == []


# ═══════════════════════════════════════════════════════════════
# extract_expected_output 测试
# ═══════════════════════════════════════════════════════════════

class TestExtractExpectedOutput:
    """测试预期输出格式识别功能"""

    def test_输出类型_JSON(self):
        """识别 JSON 输出类型"""
        text = "请以JSON格式返回结果。"
        desc, otype = extract_expected_output(text)
        assert desc is not None
        assert "JSON" in desc
        assert otype == "JSON"

    def test_输出类型_列表(self):
        """识别列表输出类型"""
        text = "请以列表形式列出所有选项。"
        desc, otype = extract_expected_output(text)
        assert desc is not None
        assert otype == "列表"

    def test_输出类型_表格(self):
        """识别表格输出类型"""
        text = "以表格形式输出对比结果。"
        desc, otype = extract_expected_output(text)
        assert desc is not None
        assert otype == "表格"

    def test_输出类型_代码(self):
        """识别代码输出类型"""
        text = "输出一段Python代码实现该功能。"
        desc, otype = extract_expected_output(text)
        assert desc is not None
        assert otype == "代码"

    def test_输出类型_文本(self):
        """识别文本输出类型"""
        text = "返回一段文字描述。"
        desc, otype = extract_expected_output(text)
        assert desc is not None
        assert otype == "文本"

    def test_无预期输出(self):
        """无输出格式要求的文本应返回 None"""
        text = "请帮我分析一下这个数据。"
        desc, otype = extract_expected_output(text)
        assert desc is None
        assert otype is None

    def test_空文本(self):
        """空文本应返回 (None, None)"""
        desc, otype = extract_expected_output("")
        assert desc is None
        assert otype is None


# ═══════════════════════════════════════════════════════════════
# extract_from_markdown_structure 测试
# ═══════════════════════════════════════════════════════════════

class TestExtractFromMarkdownStructure:
    """测试 Markdown 结构辅助提取功能"""

    def test_标题转为指令(self):
        """标题应被提取为指令"""
        md = {
            "headings": ["需求分析", "技术方案", "实现步骤"],
        }
        result = extract_from_markdown_structure(md)
        assert len(result.instructions) == 3
        assert "需求分析" in result.instructions
        assert "技术方案" in result.instructions
        assert "实现步骤" in result.instructions

    def test_标题_dict格式转为指令(self):
        """标题字典格式应正确提取文本"""
        md = {
            "headings": [
                {"text": "项目背景"},
                {"content": "功能需求"},
            ],
        }
        result = extract_from_markdown_structure(md)
        assert len(result.instructions) == 2
        assert "项目背景" in result.instructions
        assert "功能需求" in result.instructions

    def test_列表项转为约束(self):
        """列表项应被提取为约束"""
        md = {
            "list_items": [
                "必须包含用户登录功能",
                "不能超过100行代码",
                "使用正式语气",
            ],
        }
        result = extract_from_markdown_structure(md)
        assert len(result.constraints) == 3
        types = [c["type"] for c in result.constraints]
        assert "内容约束" in types
        assert "格式约束" in types
        assert "风格约束" in types

    def test_列表项_无约束关键词(self):
        """无约束关键词的列表项默认归类为内容约束"""
        md = {
            "list_items": ["第一步：初始化项目", "第二步：安装依赖"],
        }
        result = extract_from_markdown_structure(md)
        assert len(result.constraints) == 2
        for c in result.constraints:
            assert c["type"] == "内容约束"

    def test_代码块转为预期输出_字符串格式(self):
        """代码块字符串应被提取为预期输出"""
        code = '{"name": "test", "version": "1.0"}'
        md = {
            "code_blocks": [code],
        }
        result = extract_from_markdown_structure(md)
        assert result.expected_output == code
        assert result.output_type == "代码"

    def test_代码块_JSON语言标注(self):
        """JSON 语言标注的代码块应识别为 JSON 类型"""
        md = {
            "code_blocks": [
                {"language": "json", "content": '{"key": "value"}'},
            ],
        }
        result = extract_from_markdown_structure(md)
        assert result.expected_output == '{"key": "value"}'
        assert result.output_type == "JSON"

    def test_代码块_HTML语言标注(self):
        """HTML 语言标注的代码块应识别为 HTML 类型"""
        md = {
            "code_blocks": [
                {"lang": "html", "code": "<div>Hello</div>"},
            ],
        }
        result = extract_from_markdown_structure(md)
        assert result.expected_output == "<div>Hello</div>"
        assert result.output_type == "HTML"

    def test_代码块_Markdown语言标注(self):
        """Markdown 语言标注的代码块应识别为 Markdown 类型"""
        md = {
            "code_blocks": [
                {"language": "markdown", "content": "# 标题\n内容"},
            ],
        }
        result = extract_from_markdown_structure(md)
        assert result.output_type == "Markdown"

    def test_空结构(self):
        """空字典应返回空的 FeatureSet"""
        result = extract_from_markdown_structure({})
        assert result.instructions == []
        assert result.constraints == []
        assert result.expected_output is None

    def test_None结构(self):
        """None 应返回空的 FeatureSet"""
        result = extract_from_markdown_structure(None)
        assert result.instructions == []
        assert result.constraints == []
        assert result.expected_output is None


# ═══════════════════════════════════════════════════════════════
# extract_features 统一入口测试
# ═══════════════════════════════════════════════════════════════

class TestExtractFeatures:
    """测试统一入口函数"""

    def test_纯文本提取(self):
        """纯文本（无 Markdown 结构）应正确提取特征"""
        text = "请帮我写一份Python代码，实现快速排序算法。以代码形式返回。"
        result = extract_features(text)
        assert isinstance(result, FeatureSet)
        assert len(result.instructions) >= 1
        assert result.expected_output is not None
        assert result.output_type == "代码"

    def test_纯文本_无特征(self):
        """无特征文本应返回空的 FeatureSet"""
        text = "今天天气不错。"
        result = extract_features(text)
        assert isinstance(result, FeatureSet)
        assert result.instructions == []
        assert result.constraints == []
        assert result.expected_output is None
        assert result.output_type is None

    def test_空文本_纯文本模式(self):
        """空文本应返回空的 FeatureSet"""
        result = extract_features("")
        assert isinstance(result, FeatureSet)
        assert result.instructions == []
        assert result.constraints == []
        assert result.expected_output is None

    def test_带Markdown结构合并(self):
        """Markdown 结构应与文本提取结果合并"""
        text = "请帮我写一份技术文档。"
        md = {
            "headings": ["技术方案设计"],
            "list_items": ["必须包含架构图"],
            "code_blocks": [{"language": "json", "content": '{"status": "ok"}'}],
        }
        result = extract_features(text, md_structure=md)
        assert isinstance(result, FeatureSet)
        # 文本提取的指令
        assert any("请帮我写一份技术文档" in r for r in result.instructions)
        # Markdown 标题提取的指令
        assert any("技术方案设计" in r for r in result.instructions)
        # Markdown 列表提取的约束
        assert len(result.constraints) >= 1
        # Markdown 代码块提取的预期输出
        assert result.expected_output == '{"status": "ok"}'
        assert result.output_type == "JSON"

    def test_合并去重(self):
        """合并时应去除重复的指令"""
        text = "请写一份报告。"
        # 标题与文本中的指令相同
        md = {
            "headings": ["请写一份报告"],
        }
        result = extract_features(text, md_structure=md)
        # 不应重复
        assert result.instructions.count("请写一份报告。") + result.instructions.count("请写一份报告") <= 2
        # 去重后指令数应合理
        assert len(result.instructions) >= 1

    def test_Markdown代码块优先于文本输出(self):
        """Markdown 代码块的输出应优先于文本中提取的输出"""
        text = "请以列表形式返回结果。"
        md = {
            "code_blocks": [{"language": "json", "content": '{"data": []}'}],
        }
        result = extract_features(text, md_structure=md)
        # Markdown 代码块的结果应优先
        assert result.expected_output == '{"data": []}'
        assert result.output_type == "JSON"

    def test_混合特征场景_完整提示词(self):
        """一个完整的混合特征提示词应正确提取所有特征"""
        text = (
            "请帮我写一份关于微服务架构的技术文章。"
            "文章字数不能超过3000字。"
            "必须包含架构图示例。"
            "请使用正式专业的语气。"
            "以Markdown格式返回结果。"
        )
        result = extract_features(text)
        assert isinstance(result, FeatureSet)
        # 有指令
        assert len(result.instructions) >= 1
        # 有约束（格式、内容、风格）
        assert len(result.constraints) >= 3
        constraint_types = {c["type"] for c in result.constraints}
        assert "格式约束" in constraint_types
        assert "内容约束" in constraint_types
        assert "风格约束" in constraint_types
        # 有预期输出
        assert result.expected_output is not None
        assert result.output_type == "Markdown"

    def test_混合特征_带Markdown结构(self):
        """混合特征 + Markdown 结构应完整合并"""
        text = "请帮我写一份数据分析报告。语气要正式。"
        md = {
            "headings": ["数据概览", "趋势分析"],
            "list_items": [
                "必须包含可视化图表",
                "不能使用外部数据源",
            ],
            "code_blocks": [
                {"language": "python", "code": "import pandas as pd\nprint(df.head())"},
            ],
        }
        result = extract_features(text, md_structure=md)
        assert isinstance(result, FeatureSet)
        # 文本指令 + 标题指令
        assert len(result.instructions) >= 3
        # 文本约束 + 列表约束
        assert len(result.constraints) >= 3
        # 代码块输出
        assert result.expected_output is not None
        assert result.output_type == "代码"


# ═══════════════════════════════════════════════════════════════
# 边界情况测试
# ═══════════════════════════════════════════════════════════════

class TestEdgeCases:
    """测试边界情况"""

    def test_仅标点符号(self):
        """仅包含标点符号的文本"""
        result = extract_features("。！？.!?")
        assert isinstance(result, FeatureSet)
        assert result.instructions == []
        assert result.constraints == []

    def test_超长文本(self):
        """超长文本应能正常处理"""
        text = "请写一篇文章。" * 100
        result = extract_features(text)
        assert isinstance(result, FeatureSet)
        assert len(result.instructions) > 0

    def test_中英文混合(self):
        """中英文混合文本"""
        text = "Please write a Python script. 请写一个Python脚本。"
        result = extract_instructions(text)
        assert len(result) >= 1