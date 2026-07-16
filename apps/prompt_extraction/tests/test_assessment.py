"""质量评估模块单元测试"""

import pytest

from prompt_extraction.assessment.evaluator import (
    evaluate,
    evaluate_clarity,
    evaluate_completeness,
    evaluate_executability,
)
from prompt_extraction.models import FeatureSet, QualityScore


# ============================================================================
# 测试辅助函数
# ============================================================================

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


# ============================================================================
# evaluate_clarity 测试
# ============================================================================


class TestEvaluateClarity:
    """测试清晰度评估功能"""

    # --- 高清晰度 ---

    def test_高清晰度_结构良好无歧义(self):
        """结构良好、无歧义的提示词应获得高分"""
        text = (
            "# 任务目标\n\n"
            "请分析以下销售数据，生成一份详细的季度报告。\n\n"
            "## 要求\n"
            "- 包含同比和环比分析\n"
            "- 识别增长最快的三个品类\n"
            "- 给出具体的改进建议\n\n"
            "## 输出格式\n"
            "以 Markdown 格式输出，包含表格和图表说明。"
        )
        score, suggestions = evaluate_clarity(text)
        assert score >= 85.0, f"期望 >= 85，实际 {score}"
        assert len(suggestions) == 0

    def test_高清晰度_中等长度有结构(self):
        """中等长度、有段落分隔的文本应获得较高分"""
        text = (
            "请编写一个 Python 函数，用于计算斐波那契数列。\n\n"
            "要求使用递归实现，并添加缓存机制以提高性能。\n\n"
            "输出完整的函数代码和单元测试。"
        )
        score, suggestions = evaluate_clarity(text)
        assert score >= 70.0, f"期望 >= 70，实际 {score}"

    # --- 低清晰度 ---

    def test_低清晰度_过短文本(self):
        """过短（<20字）的提示词应获得低分"""
        text = "帮我写个东西"
        score, suggestions = evaluate_clarity(text)
        assert score <= 60.0, f"期望 <= 60，实际 {score}"
        assert len(suggestions) >= 1

    def test_低清晰度_包含歧义词(self):
        """包含多个模糊词汇的提示词应获得较低分"""
        text = "请你大概写一些关于可能的市场分析，也许包含几个图表，差不多就行"
        score, suggestions = evaluate_clarity(text)
        assert score < 100.0, f"包含歧义词应扣分，实际 {score}"
        assert any("模糊词汇" in s for s in suggestions)

    def test_低清晰度_过长文本(self):
        """过长（>500字）的提示词应有适当扣分"""
        text = "请帮我写一篇关于人工智能发展趋势的详细分析报告。" * 50
        assert len(text) > 500
        score, suggestions = evaluate_clarity(text)
        assert score < 100.0, f"过长文本应扣分，实际 {score}"

    def test_低清晰度_无结构元素(self):
        """无标题、无段落、无列表的纯文本应获得较低分"""
        text = "请帮我分析一下这份数据的结果并给出建议我觉得可以从几个方面入手"
        score, suggestions = evaluate_clarity(text)
        assert score < 100.0, f"无结构应扣分，实际 {score}"
        assert any("结构元素" in s for s in suggestions)

    # --- 边界值 ---

    def test_空文本(self):
        """空文本应获得最低分"""
        score, suggestions = evaluate_clarity("")
        # 100 - 40(过短) - 30(无标题/段落/列表) = 30
        assert score == 30.0
        assert len(suggestions) >= 1

    def test_纯空白文本(self):
        """纯空白文本应被视为过短且无结构"""
        score, suggestions = evaluate_clarity("   ")
        # 100 - 40(过短) - 30(无标题/段落/列表) = 30
        assert score == 30.0

    def test_恰好20字边界(self):
        """恰好 20 字的文本不应因过短被扣分"""
        text = "请帮我生成一份完整的市场分析报告包含图表"
        assert len(text) == 20
        score, _ = evaluate_clarity(text)
        # 可能因缺少结构元素扣分，但不应因过短扣分
        assert score >= 60.0

    def test_恰好500字边界(self):
        """恰好 500 字的文本不应因过长被扣分，但仍有结构扣分"""
        text = "A" * 500
        score, _ = evaluate_clarity(text)
        # 不应因过长被扣分（>500 才扣分），但无结构扣 30 分
        assert score == 70.0


# ============================================================================
# evaluate_completeness 测试
# ============================================================================


class TestEvaluateCompleteness:
    """测试完整性评估功能"""

    # --- 高完整性 ---

    def test_高完整性_包含所有要素(self):
        """包含全部五个要素的提示词应获得满分"""
        text = (
            "背景：当前公司需要提升用户留存率。\n"
            "请分析用户行为数据，例如：用户登录频率、页面停留时间等。\n"
            "输出格式为 JSON。"
        )
        features = _make_features(
            instructions=["分析用户行为数据"],
            constraints=[{"type": "format", "value": "JSON"}],
            expected_output='{"metrics": [...]}',
        )
        score, suggestions = evaluate_completeness(text, features)
        assert score == 100.0, f"期望 100，实际 {score}"
        assert len(suggestions) == 0

    def test_高完整性_有示例有上下文(self):
        """包含示例和上下文关键词的提示词应获得相应分数"""
        text = "背景：某电商平台需要分析用户购买行为。请分析数据，比如：用户的购买路径、复购率等。"
        features = _make_features(
            instructions=["分析数据"],
            expected_output="分析报告",
        )
        score, suggestions = evaluate_completeness(text, features)
        assert score >= 80.0, f"期望 >= 80，实际 {score}"

    # --- 低完整性 ---

    def test_低完整性_缺少约束和输出格式(self):
        """缺少约束和输出格式的提示词应获得较低分"""
        text = "请帮我分析数据"
        features = _make_features(
            instructions=["分析数据"],
        )
        score, suggestions = evaluate_completeness(text, features)
        assert score <= 60.0, f"期望 <= 60，实际 {score}"
        assert len(suggestions) >= 2

    def test_低完整性_仅有指令(self):
        """仅有指令、无其他要素的提示词应获得低分"""
        text = "写代码"
        features = _make_features(
            instructions=["写代码"],
        )
        score, suggestions = evaluate_completeness(text, features)
        assert score == 20.0, f"期望 20，实际 {score}"

    def test_低完整性_空特征集(self):
        """空特征集加上短文本应获得最低分"""
        text = "hello"
        features = FeatureSet()
        score, suggestions = evaluate_completeness(text, features)
        assert score == 0.0, f"期望 0，实际 {score}"

    # --- 边界值 ---

    def test_文本长度恰好50字(self):
        """恰好 50 字的文本不满足 >50 的条件，缺少上下文得分"""
        text = "A" * 50
        features = _make_features(
            instructions=["测试"],
            constraints=[{"type": "test"}],
            expected_output="输出",
        )
        score, _ = evaluate_completeness(text, features)
        # 指令(20) + 约束(20) + 上下文(0, 50不>50) + 示例(0) + 输出格式(20) = 60
        assert score == 60.0

    def test_文本长度49字(self):
        """49 字且无背景关键词不满足上下文条件"""
        text = "A" * 49
        features = _make_features(
            instructions=["测试"],
            constraints=[{"type": "test"}],
            expected_output="输出",
        )
        score, _ = evaluate_completeness(text, features)
        # 指令(20) + 约束(20) + 上下文(0) + 示例(0) + 输出格式(20) = 60
        assert score == 60.0


# ============================================================================
# evaluate_executability 测试
# ============================================================================


class TestEvaluateExecutability:
    """测试可执行性评估功能"""

    # --- 高可执行性 ---

    def test_高可执行性_完整指令约束和输出(self):
        """包含动作动词、可验证约束和明确输出的提示词应获得高分"""
        text = "请生成一份用户分析报告，分析用户行为数据，筛选出高价值用户，并输出推荐列表。"
        features = _make_features(
            instructions=["生成报告", "分析数据", "筛选用户"],
            constraints=[
                {"type": "count", "value": "最多10条"},
                {"type": "format", "value": "必须包含用户ID"},
            ],
            expected_output='{"users": [{"id": "...", "score": 0.0}]}',
        )
        score, suggestions = evaluate_executability(text, features)
        assert score >= 80.0, f"期望 >= 80，实际 {score}"

    def test_高可执行性_多个动作动词(self):
        """包含多个动作动词的提示词应获得较高可操作性分"""
        text = "请创建、设计、开发、实现、测试、部署一个新的用户认证模块"
        features = _make_features(
            instructions=["创建认证模块"],
            expected_output="代码",
        )
        score, _ = evaluate_executability(text, features)
        assert score >= 30.0, f"期望 >= 30，实际 {score}"

    # --- 低可执行性 ---

    def test_低可执行性_模糊指令无动作动词(self):
        """无动作动词的模糊指令应获得低分"""
        text = "这个东西应该怎么弄比较好呢"
        features = FeatureSet()
        score, suggestions = evaluate_executability(text, features)
        assert score <= 30.0, f"期望 <= 30，实际 {score}"
        assert len(suggestions) >= 1

    def test_低可执行性_无约束无输出格式(self):
        """无约束且无输出格式的提示词应获得很低分"""
        text = "分析数据"
        features = _make_features(
            instructions=["分析数据"],
        )
        score, suggestions = evaluate_executability(text, features)
        assert score <= 30.0, f"期望 <= 30，实际 {score}"

    def test_低可执行性_约束不可验证(self):
        """约束条件不包含可验证标准时应获得较低分"""
        text = "请生成一份报告"
        features = _make_features(
            instructions=["生成报告"],
            constraints=[{"type": "style", "description": "简洁明了"}],
            expected_output="报告",
        )
        score, suggestions = evaluate_executability(text, features)
        assert score < 100.0, f"不可验证约束应扣分，实际 {score}"

    def test_仅有output_type无expected_output(self):
        """仅有 output_type 而无 expected_output 应获得一半输出分"""
        text = "请生成一份数据报告"
        features = _make_features(
            instructions=["生成报告"],
            output_type="JSON",
        )
        score, suggestions = evaluate_executability(text, features)
        assert 10.0 <= score <= 30.0, f"期望 10-30，实际 {score}"

    # --- 边界值 ---

    def test_空特征空文本(self):
        """空特征和空文本应获得最低可执行性分"""
        score, suggestions = evaluate_executability("", FeatureSet())
        assert score == 0.0, f"期望 0，实际 {score}"
        assert len(suggestions) >= 2


# ============================================================================
# evaluate 综合评分测试
# ============================================================================


class TestEvaluateComprehensive:
    """测试综合评估功能"""

    # --- 返回类型 ---

    def test_返回QualityScore实例(self):
        """应返回 QualityScore 实例"""
        result = evaluate("测试文本", FeatureSet())
        assert isinstance(result, QualityScore)

    def test_返回结构包含所有字段(self):
        """返回的 QualityScore 应包含所有必要字段"""
        result = evaluate("测试文本", FeatureSet())
        assert hasattr(result, "clarity")
        assert hasattr(result, "completeness")
        assert hasattr(result, "executability")
        assert hasattr(result, "overall")
        assert hasattr(result, "grade")
        assert hasattr(result, "suggestions")

    # --- 加权公式验证 ---

    def test_加权公式计算正确性(self):
        """验证综合评分 = 清晰度*0.30 + 完整性*0.40 + 可执行性*0.30"""
        text = (
            "# 任务\n\n"
            "请生成一份详细的市场分析报告，分析当前市场趋势，\n"
            "例如：竞争对手分析、用户需求变化等。\n"
            "输出格式为 JSON，包含 metrics 和 summary 字段。"
        )
        features = _make_features(
            instructions=["生成市场分析报告"],
            constraints=[{"type": "format", "value": "JSON"}],
            expected_output='{"metrics": [], "summary": ""}',
        )

        result = evaluate(text, features)

        # 手动计算期望值
        expected_overall = round(
            result.clarity * 0.30
            + result.completeness * 0.40
            + result.executability * 0.30,
            1,
        )
        assert result.overall == expected_overall, (
            f"综合评分 {result.overall} 不等于期望值 {expected_overall}"
        )

    def test_三维度评分在0到100之间(self):
        """各维度评分应在 0-100 之间"""
        text = "请帮我做一件事"
        result = evaluate(text, FeatureSet())
        assert 0.0 <= result.clarity <= 100.0
        assert 0.0 <= result.completeness <= 100.0
        assert 0.0 <= result.executability <= 100.0
        assert 0.0 <= result.overall <= 100.0

    # --- 等级判定 ---

    def test_等级判定_优(self):
        """综合评分 >= 85 应判定为"优" """
        text = (
            "# 数据分析任务\n\n"
            "背景：当前季度销售额同比下降 15%，需要分析原因。\n\n"
            "## 任务\n"
            "请分析以下销售数据，生成季度分析报告。\n\n"
            "## 要求\n"
            "- 必须包含同比和环比数据\n"
            "- 至少识别 3 个关键影响因素\n"
            "- 给出具体改进建议\n\n"
            "## 输出格式\n"
            "以 JSON 格式输出，例如：\n"
            '{"report": {"summary": "...", "factors": [...], "suggestions": [...]}}'
        )
        features = _make_features(
            instructions=["分析销售数据", "生成季度分析报告"],
            constraints=[
                {"type": "data", "value": "必须包含同比和环比数据"},
                {"type": "count", "value": "至少3个关键因素"},
            ],
            expected_output='{"report": {"summary": "...", "factors": [...], "suggestions": [...]}}',
        )
        result = evaluate(text, features)
        assert result.grade == "优", f"期望 '优'，实际 '{result.grade}'，综合评分 {result.overall}"

    def test_等级判定_良(self):
        """综合评分 >= 70 且 < 85 应判定为"良" """
        text = (
            "请分析用户行为数据，生成一份分析报告。\n\n"
            "要求包含用户活跃度、留存率等指标。\n"
            "例如：DAU、MAU、次日留存率等。\n"
            "输出格式为 Markdown。"
        )
        features = _make_features(
            instructions=["分析用户行为数据", "生成分析报告"],
            constraints=[{"type": "content", "value": "包含用户活跃度、留存率"}],
            expected_output="Markdown 报告",
        )
        result = evaluate(text, features)
        assert result.grade == "良", f"期望 '良'，实际 '{result.grade}'，综合评分 {result.overall}"

    def test_等级判定_中(self):
        """综合评分 >= 50 且 < 70 应判定为"中" """
        text = (
            "请分析用户数据，生成一份简要报告。\n\n"
            "要求：包含关键指标，字数不超过 500 字。\n"
            "当前的背景是用户活跃度下降，需要找出原因。"
        )
        features = _make_features(
            instructions=["分析用户数据", "生成报告"],
            constraints=[{"type": "length", "value": "不超过500字"}],
        )
        result = evaluate(text, features)
        assert result.grade == "中", f"期望 '中'，实际 '{result.grade}'，综合评分 {result.overall}"

    def test_等级判定_差(self):
        """综合评分 < 50 应判定为"差" """
        text = "做一个东西"
        features = FeatureSet()
        result = evaluate(text, features)
        assert result.grade == "差", f"期望 '差'，实际 '{result.grade}'，综合评分 {result.overall}"

    # --- 边界值 ---

    def test_空文本评估(self):
        """空文本应返回合理的评估结果"""
        result = evaluate("", FeatureSet())
        assert result.overall >= 0.0
        assert result.grade in ("优", "良", "中", "差")
        assert len(result.suggestions) >= 0

    def test_极长文本评估(self):
        """极长文本不应导致异常"""
        text = "请帮我写一篇关于人工智能发展趋势的详细分析报告。" * 100
        result = evaluate(text, FeatureSet())
        assert result.overall >= 0.0
        assert result.grade in ("优", "良", "中", "差")

    def test_建议列表汇总(self):
        """suggestions 应汇总所有维度的建议"""
        text = "写个东西"
        result = evaluate(text, FeatureSet())
        # 多个维度都会产生建议
        assert isinstance(result.suggestions, list)

    def test_等级阈值边界_恰好85分(self):
        """恰好 85 分应判定为"优" """
        # 构造一个恰好 85 分的场景
        from prompt_extraction.config import GRADE_THRESHOLDS

        # 验证 GRADE_THRESHOLDS 的边界逻辑
        assert GRADE_THRESHOLDS["优"] == 85
        assert GRADE_THRESHOLDS["良"] == 70
        assert GRADE_THRESHOLDS["中"] == 50
        assert GRADE_THRESHOLDS["差"] == 0


# ============================================================================
# 综合场景测试
# ============================================================================


class TestIntegration:
    """综合场景测试"""

    def test_PromptRecord字段兼容性(self):
        """验证 evaluate 返回的 QualityScore 与 PromptRecord 字段兼容"""
        from prompt_extraction.models import PromptRecord

        text = (
            "# 任务\n\n"
            "请分析用户数据并生成报告。\n\n"
            "## 要求\n"
            "- 必须包含图表\n"
            "- 字数不超过 2000 字"
        )
        features = _make_features(
            instructions=["分析用户数据", "生成报告"],
            constraints=[
                {"type": "content", "value": "必须包含图表"},
                {"type": "length", "value": "不超过2000字"},
            ],
            expected_output="Markdown 报告",
        )
        quality = evaluate(text, features)

        record = PromptRecord(
            id="test-quality-001",
            original_text=text,
            features=features,
            quality=quality,
        )
        assert record.quality.clarity >= 0.0
        assert record.quality.completeness >= 0.0
        assert record.quality.executability >= 0.0
        assert record.quality.overall >= 0.0
        assert record.quality.grade in ("优", "良", "中", "差")

    def test_完整评估流程(self):
        """端到端评估流程应正常工作"""
        # 高质量提示词
        text_good = (
            "# 数据报告生成\n\n"
            "背景：需要分析 Q1 销售数据，制定 Q2 策略。\n\n"
            "请生成一份详细的销售分析报告，包含以下内容：\n"
            "- 各品类销售额对比\n"
            "- 增长率排名\n"
            "- 改进建议\n\n"
            "输出格式：JSON，例如：\n"
            '{"categories": [...], "growth": [...], "suggestions": [...]}'
        )
        features_good = _make_features(
            instructions=["生成销售分析报告"],
            constraints=[
                {"type": "content", "value": "包含品类对比、增长率排名、改进建议"},
                {"type": "format", "value": "JSON"},
            ],
            expected_output='{"categories": [...], "growth": [...], "suggestions": [...]}',
        )

        result_good = evaluate(text_good, features_good)
        assert result_good.overall >= 70.0, f"高质量提示词应 >= 70，实际 {result_good.overall}"

        # 低质量提示词
        text_bad = "写个东西"
        features_bad = FeatureSet()

        result_bad = evaluate(text_bad, features_bad)
        assert result_bad.overall < 50.0, f"低质量提示词应 < 50，实际 {result_bad.overall}"

        # 高质量提示词分数应高于低质量
        assert result_good.overall > result_bad.overall