"""优化生成模块单元测试"""

import pytest

from prompt_extraction.models import FeatureSet, OptimizationResult, PromptRecord, QualityScore
from prompt_extraction.optimization.optimizer import (
    disambiguate,
    generate_diff,
    optimize,
    restructure,
    should_optimize,
    supplement_missing_elements,
)


# ============================================================================
# 测试辅助函数
# ============================================================================


def _make_quality(
    overall: float = 0.0,
    clarity: float = 0.0,
    completeness: float = 0.0,
    executability: float = 0.0,
    grade: str = "差",
    suggestions: list[str] | None = None,
) -> QualityScore:
    """快速构造 QualityScore 实例的辅助函数。"""
    return QualityScore(
        clarity=clarity,
        completeness=completeness,
        executability=executability,
        overall=overall,
        grade=grade,
        suggestions=suggestions or [],
    )


def _make_features(
    instructions: list[str] | None = None,
    constraints: list[dict] | None = None,
    expected_output: str | None = None,
    output_type: str | None = None,
) -> FeatureSet:
    """快速构造 FeatureSet 实例的辅助函数。"""
    return FeatureSet(
        instructions=instructions or [],
        constraints=constraints or [],
        expected_output=expected_output,
        output_type=output_type,
    )


def _make_record(
    original_text: str = "",
    cleaned_text: str = "",
    features: FeatureSet | None = None,
    quality: QualityScore | None = None,
) -> PromptRecord:
    """快速构造 PromptRecord 实例的辅助函数。"""
    return PromptRecord(
        id="test-001",
        original_text=original_text,
        cleaned_text=cleaned_text,
        features=features or FeatureSet(),
        quality=quality or _make_quality(),
    )


# ============================================================================
# should_optimize 测试
# ============================================================================


class TestShouldOptimize:
    """测试优化触发判定功能"""

    def test_评分低于60触发优化(self):
        """综合评分 < 60 时应返回 True"""
        quality = _make_quality(overall=45.0)
        assert should_optimize(quality) is True

    def test_评分59点9触发优化(self):
        """综合评分 59.9 应触发优化"""
        quality = _make_quality(overall=59.9)
        assert should_optimize(quality) is True

    def test_评分等于60不触发优化(self):
        """综合评分恰好 60 不应触发优化（边界值）"""
        quality = _make_quality(overall=60.0)
        assert should_optimize(quality) is False

    def test_评分大于60不触发优化(self):
        """综合评分 > 60 时应返回 False"""
        quality = _make_quality(overall=85.0)
        assert should_optimize(quality) is False

    def test_评分0触发优化(self):
        """综合评分 0 应触发优化"""
        quality = _make_quality(overall=0.0)
        assert should_optimize(quality) is True

    def test_评分100不触发优化(self):
        """综合评分 100 不应触发优化"""
        quality = _make_quality(overall=100.0)
        assert should_optimize(quality) is False


# ============================================================================
# supplement_missing_elements 测试
# ============================================================================


class TestSupplementMissingElements:
    """测试缺失要素补充功能"""

    def test_缺少expected_output时补充JSON格式(self):
        """文本中提到 JSON 时，应补充 JSON 格式说明"""
        text = "请分析数据并生成 JSON 报告"
        features = _make_features(
            instructions=["分析数据"],
            constraints=[{"type": "format", "value": "JSON"}],
            expected_output=None,  # 缺失
        )
        result = supplement_missing_elements(text, features)
        assert "JSON" in result
        assert "结构化数据" in result

    def test_缺少expected_output时补充报告格式(self):
        """文本中提到"报告"时，应补充报告格式说明"""
        text = "请生成一份分析报告"
        features = _make_features(
            instructions=["生成报告"],
            expected_output=None,  # 缺失
        )
        result = supplement_missing_elements(text, features)
        assert "报告" in result

    def test_缺少expected_output时补充默认格式(self):
        """文本中无明确格式提示时，应补充默认格式说明"""
        text = "请帮我做一件事"
        features = _make_features(
            instructions=["做一件事"],
            expected_output=None,  # 缺失
        )
        result = supplement_missing_elements(text, features)
        assert "结构化" in result

    def test_有expected_output时不修改(self):
        """已有 expected_output 时不应追加额外格式说明"""
        text = "请分析数据"
        features = _make_features(
            instructions=["分析数据"],
            expected_output="以 JSON 格式输出",
        )
        result = supplement_missing_elements(text, features)
        # 原始文本应保留，不应有额外的格式追加
        assert text in result

    def test_缺少constraints时补充隐含约束(self):
        """文本中包含"必须"等关键词时，应显式化约束"""
        text = "请分析数据，必须包含图表"
        features = _make_features(
            instructions=["分析数据"],
            constraints=[],  # 缺失
            expected_output="JSON",
        )
        result = supplement_missing_elements(text, features)
        assert "## 约束" in result
        assert "必须" in result

    def test_有constraints时不添加隐含约束(self):
        """已有 constraints 时不应追加额外约束"""
        text = "请分析数据，必须包含图表"
        features = _make_features(
            instructions=["分析数据"],
            constraints=[{"type": "content", "value": "必须包含图表"}],
            expected_output="JSON",
        )
        result = supplement_missing_elements(text, features)
        # 不应出现额外的 ## 约束 章节
        assert "## 约束" not in result

    def test_同时缺少expected_output和constraints(self):
        """同时缺少输出格式和约束时，两者都应补充"""
        text = "请帮我写一份报告，必须包含图表和分析"
        features = _make_features(
            instructions=["写报告"],
            expected_output=None,
            constraints=[],
        )
        result = supplement_missing_elements(text, features)
        assert "报告" in result
        assert "## 约束" in result


# ============================================================================
# disambiguate 测试
# ============================================================================


class TestDisambiguate:
    """测试歧义消除功能"""

    def test_替换可能为请明确判断(self):
        """模糊词"可能"应替换为"请明确判断" """
        text = "请分析可能的原因"
        result = disambiguate(text)
        assert "可能" not in result
        assert "请明确判断" in result

    def test_替换也许为请明确判断(self):
        """模糊词"也许"应替换为"请明确判断" """
        text = "也许需要调整方案"
        result = disambiguate(text)
        assert "也许" not in result
        assert "请明确判断" in result

    def test_替换一些为列出所有(self):
        """模糊词"一些"应替换为"列出所有" """
        text = "请列出一些关键指标"
        result = disambiguate(text)
        assert "一些" not in result
        assert "列出所有" in result

    def test_替换几个为列出所有(self):
        """模糊词"几个"应替换为"列出所有" """
        text = "请分析几个问题"
        result = disambiguate(text)
        assert "几个" not in result
        assert "列出所有" in result

    def test_替换差不多为精确地(self):
        """模糊词"差不多"应替换为"精确地" """
        text = "差不多需要三个步骤"
        result = disambiguate(text)
        assert "差不多" not in result
        assert "精确地" in result

    def test_替换大概为请明确说明(self):
        """模糊词"大概"应替换为"请明确说明" """
        text = "大概需要分析以下几个方面"
        result = disambiguate(text)
        assert "大概" not in result
        assert "请明确说明" in result

    def test_替换左右为精确地(self):
        """模糊词"左右"应替换为"精确地" """
        text = "输出五条左右的数据"
        result = disambiguate(text)
        assert "左右" not in result
        assert "精确地" in result

    def test_多个歧义词同时替换(self):
        """多个歧义词应全部被替换"""
        text = "可能大概有一些差不多的问题，需要几个方案左右"
        result = disambiguate(text)
        for word in ("可能", "大概", "一些", "差不多", "几个", "左右"):
            assert word not in result, f"'{word}' 未被替换"
        assert "请明确判断" in result
        assert "请明确说明" in result
        assert "列出所有" in result
        assert "精确地" in result

    def test_无歧义词文本不变(self):
        """无歧义词的文本应保持不变"""
        text = "请分析当前季度销售数据，生成包含图表和趋势分析的详细报告"
        result = disambiguate(text)
        assert result == text


# ============================================================================
# restructure 测试
# ============================================================================


class TestRestructure:
    """测试结构重组功能"""

    def test_有指令和约束时生成标准结构(self):
        """有 instructions 和 constraints 时应生成包含指令和约束章节的结构"""
        text = "请分析数据"
        features = _make_features(
            instructions=["分析数据", "生成报告"],
            constraints=[{"type": "format", "value": "JSON 格式"}],
        )
        result = restructure(text, features)
        assert "## 指令" in result
        assert "## 约束" in result
        assert "分析数据" in result
        assert "生成报告" in result
        assert "JSON 格式" in result

    def test_有输出格式时包含输出格式章节(self):
        """有 expected_output 时应包含输出格式章节"""
        text = "请分析数据"
        features = _make_features(
            instructions=["分析数据"],
            expected_output='{"result": "..."}',
        )
        result = restructure(text, features)
        assert "## 输出格式" in result
        assert '{"result": "..."}' in result

    def test_有上下文时包含上下文章节(self):
        """文本中包含"背景"等内容时应提取到上下文章节"""
        text = "背景：当前用户活跃度下降\n请分析数据并生成报告"
        features = _make_features(
            instructions=["分析数据", "生成报告"],
        )
        result = restructure(text, features)
        assert "## 上下文" in result
        assert "用户活跃度下降" in result

    def test_无指令时使用原始文本作为指令(self):
        """无 instructions 时，应将原始文本作为指令章节内容"""
        text = "请帮我分析用户数据"
        features = FeatureSet()  # 空特征集
        result = restructure(text, features)
        assert "## 指令" in result
        assert "分析用户数据" in result

    def test_空特征空文本仍生成指令章节(self):
        """空特征和空文本时也应生成指令章节"""
        text = ""
        features = FeatureSet()
        result = restructure(text, features)
        assert "## 指令" in result

    def test_包含所有章节的完整结构(self):
        """包含所有要素时应生成完整的四章节结构"""
        text = "背景：当前系统存在性能瓶颈\n请分析性能数据，生成优化方案"
        features = _make_features(
            instructions=["分析性能数据", "生成优化方案"],
            constraints=[
                {"type": "length", "value": "不超过2000字"},
                {"type": "format", "value": "Markdown"},
            ],
            expected_output="## 优化方案\n- 问题分析\n- 改进建议",
        )
        result = restructure(text, features)
        assert "## 指令" in result
        assert "## 约束" in result
        assert "## 上下文" in result
        assert "## 输出格式" in result
        assert "分析性能数据" in result
        assert "生成优化方案" in result
        assert "不超过2000字" in result
        assert "性能瓶颈" in result


# ============================================================================
# generate_diff 测试
# ============================================================================


class TestGenerateDiff:
    """测试差异对比生成功能"""

    def test_相同文本无差异(self):
        """相同文本应生成全空行的 diff"""
        text = "请分析数据\n生成报告"
        result = generate_diff(text, text)
        lines = result.split("\n")
        # 相同行全部为空行
        for line in lines:
            assert line == "" or line == ""

    def test_新增行以加号前缀表示(self):
        """新增行应以 + 前缀标识"""
        original = "请分析数据"
        optimized = "请分析数据\n生成报告"
        result = generate_diff(original, optimized)
        assert "+生成报告" in result

    def test_删除行以减号前缀表示(self):
        """删除行应以 - 前缀标识"""
        original = "请分析数据\n生成报告"
        optimized = "请分析数据"
        result = generate_diff(original, optimized)
        assert "-生成报告" in result

    def test_修改行以减号和加号表示(self):
        """修改行应同时出现 - 和 + 行"""
        original = "请分析数据"
        optimized = "请分析用户数据"
        result = generate_diff(original, optimized)
        assert "-请分析数据" in result
        assert "+请分析用户数据" in result

    def test_混合差异正确标注(self):
        """混合增删改的 diff 应正确标注"""
        original = "标题\n第一章\n旧内容\n结尾"
        optimized = "标题\n第一章\n新内容\n附录"
        result = generate_diff(original, optimized)
        lines = result.split("\n")
        # 第一行相同 → 空行
        assert lines[0] == ""
        # 第二行相同 → 空行
        assert lines[1] == ""
        # 第三行修改 → - 旧 + 新
        assert "-旧内容" in result
        assert "+新内容" in result
        # 第四行修改 → - 结尾 + 附录
        assert "-结尾" in result
        assert "+附录" in result

    def test_返回字符串类型(self):
        """generate_diff 应返回字符串"""
        result = generate_diff("a", "b")
        assert isinstance(result, str)


# ============================================================================
# optimize 统一入口测试
# ============================================================================


class TestOptimize:
    """测试统一优化入口功能"""

    def test_触发优化全流程(self):
        """低评分记录应触发优化并返回完整结果"""
        text = "请可能大概分析一下数据，生成一些报告"
        features = _make_features(
            instructions=["分析数据"],
            expected_output=None,
            constraints=[],
        )
        quality = _make_quality(overall=45.0)
        record = _make_record(
            original_text=text,
            cleaned_text=text,
            features=features,
            quality=quality,
        )
        result = optimize(record)
        assert result.triggered is True
        assert len(result.optimized_text) > 0
        assert len(result.improvements) > 0
        assert len(result.diff) > 0

    def test_不触发优化(self):
        """高评分记录不应触发优化"""
        text = "请分析数据并生成报告"
        features = _make_features(
            instructions=["分析数据", "生成报告"],
            constraints=[{"type": "format", "value": "JSON"}],
            expected_output='{"result": "..."}',
        )
        quality = _make_quality(overall=85.0)
        record = _make_record(
            original_text=text,
            features=features,
            quality=quality,
        )
        result = optimize(record)
        assert result.triggered is False
        assert result.optimized_text == ""
        assert result.improvements == []
        assert result.diff == ""

    def test_优化结果字段完整性(self):
        """优化结果应包含所有必要字段"""
        text = "请分析数据"
        features = _make_features(
            instructions=["分析数据"],
            expected_output=None,
            constraints=[],
        )
        quality = _make_quality(overall=30.0)
        record = _make_record(
            original_text=text,
            features=features,
            quality=quality,
        )
        result = optimize(record)
        assert isinstance(result, OptimizationResult)
        assert hasattr(result, "triggered")
        assert hasattr(result, "optimized_text")
        assert hasattr(result, "improvements")
        assert hasattr(result, "diff")
        assert result.triggered is True
        assert isinstance(result.optimized_text, str)
        assert isinstance(result.improvements, list)
        assert isinstance(result.diff, str)

    def test_优化后文本包含歧义消除(self):
        """优化后的文本应消除歧义词汇"""
        text = "请可能大概分析一下数据"
        features = _make_features(
            instructions=["分析数据"],
            expected_output="JSON",
            constraints=[{"type": "format", "value": "JSON"}],
        )
        quality = _make_quality(overall=40.0)
        record = _make_record(
            original_text=text,
            features=features,
            quality=quality,
        )
        result = optimize(record)
        assert "可能" not in result.optimized_text
        assert "大概" not in result.optimized_text

    def test_优化后文本包含结构重组(self):
        """优化后的文本应包含标准 Markdown 结构"""
        text = "背景：系统性能下降\n请分析并生成优化方案"
        features = _make_features(
            instructions=["分析系统性能", "生成优化方案"],
            constraints=[{"type": "length", "value": "不超过2000字"}],
            expected_output="Markdown 报告",
        )
        quality = _make_quality(overall=50.0)
        record = _make_record(
            original_text=text,
            features=features,
            quality=quality,
        )
        result = optimize(record)
        assert "## 指令" in result.optimized_text
        assert "## 约束" in result.optimized_text
        assert "## 上下文" in result.optimized_text
        assert "## 输出格式" in result.optimized_text

    def test_improvements记录了优化步骤(self):
        """improvements 应记录所有执行的优化步骤"""
        text = "请可能分析一下数据"
        features = _make_features(
            instructions=["分析数据"],
            expected_output=None,
            constraints=[],
        )
        quality = _make_quality(overall=35.0)
        record = _make_record(
            original_text=text,
            features=features,
            quality=quality,
        )
        result = optimize(record)
        # 至少应包含补充缺失要素和消歧增强
        assert any("补充缺失要素" in imp for imp in result.improvements)
        assert any("消歧增强" in imp for imp in result.improvements)

    def test_使用cleaned_text优先(self):
        """当 cleaned_text 存在时，应优先使用 cleaned_text"""
        original = "请分析数据（原始版本）"
        cleaned = "请分析数据（清洗后版本）"
        features = _make_features(
            instructions=["分析数据"],
            expected_output=None,
            constraints=[],
        )
        quality = _make_quality(overall=30.0)
        record = _make_record(
            original_text=original,
            cleaned_text=cleaned,
            features=features,
            quality=quality,
        )
        result = optimize(record)
        # 优化后的文本应基于 cleaned_text
        assert "清洗后版本" in result.optimized_text or "分析数据" in result.optimized_text
        # diff 中应包含 cleaned_text 的内容
        assert "清洗后版本" in result.diff or "清洗后" in result.diff

    def test_优化diff格式正确(self):
        """优化后的 diff 应包含正确的 +/- 标注"""
        text = "请分析数据"
        features = _make_features(
            instructions=["分析数据"],
            expected_output=None,
            constraints=[],
        )
        quality = _make_quality(overall=30.0)
        record = _make_record(
            original_text=text,
            features=features,
            quality=quality,
        )
        result = optimize(record)
        # diff 应包含 + 前缀（新增行）或 - 前缀（删除行）
        assert "+" in result.diff or "-" in result.diff or result.diff == ""


# ============================================================================
# 综合场景测试
# ============================================================================


class TestIntegration:
    """综合场景测试"""

    def test_完整优化流程端到端(self):
        """端到端优化流程：低质量提示词 → 补充 → 消歧 → 重组 → diff"""
        text = "请可能大概写一些关于市场分析的东西，差不多就行"
        features = _make_features(
            instructions=["写市场分析"],
            expected_output=None,
            constraints=[],
        )
        quality = _make_quality(overall=25.0)
        record = _make_record(
            original_text=text,
            features=features,
            quality=quality,
        )
        result = optimize(record)

        # 验证触发
        assert result.triggered is True

        # 验证消歧：不包含原歧义词汇
        assert "可能" not in result.optimized_text
        assert "大概" not in result.optimized_text
        assert "一些" not in result.optimized_text
        assert "差不多" not in result.optimized_text

        # 验证补充：包含输出格式说明
        assert "报告" in result.optimized_text or "市场" in result.optimized_text

        # 验证重组：包含标准结构
        assert "## 指令" in result.optimized_text

        # 验证 diff：非空且有标注
        assert len(result.diff) > 0

        # 验证 improvements：记录了优化步骤
        assert len(result.improvements) >= 2

    def test_高质量提示词不触发优化流程(self):
        """高质量提示词不应执行任何优化步骤"""
        text = (
            "# 任务\n\n"
            "请分析以下销售数据，生成季度报告。\n\n"
            "## 要求\n"
            "- 必须包含同比和环比分析\n"
            "- 识别增长最快的三个品类\n\n"
            "## 输出格式\n"
            "以 JSON 格式输出。"
        )
        features = _make_features(
            instructions=["分析销售数据", "生成季度报告"],
            constraints=[
                {"type": "content", "value": "必须包含同比和环比分析"},
                {"type": "count", "value": "识别增长最快的三个品类"},
            ],
            expected_output='{"report": "..."}',
        )
        quality = _make_quality(overall=90.0)
        record = _make_record(
            original_text=text,
            features=features,
            quality=quality,
        )
        result = optimize(record)
        assert result.triggered is False
        assert result.optimized_text == ""
        assert result.improvements == []
        assert result.diff == ""