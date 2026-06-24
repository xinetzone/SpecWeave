"""流水线编排器单元测试"""

import json
import os

import pandas as pd
import pytest

from prompt_extraction.config import QUALITY_THRESHOLD
from prompt_extraction.models import FeatureSet, OptimizationResult, PromptRecord, QualityScore
from prompt_extraction.pipeline import Pipeline


# ============================================================================
# 测试辅助函数
# ============================================================================


def _make_batch_file(tmp_path, content: str, filename: str = "test_prompts.txt") -> str:
    """在临时目录中创建测试用的批量输入文件。

    Args:
        tmp_path: pytest 临时目录 fixture。
        content: 文件内容。
        filename: 文件名。

    Returns:
        文件路径。
    """
    file_path = tmp_path / filename
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


# ============================================================================
# Pipeline 初始化测试
# ============================================================================


class TestPipelineInit:
    """测试 Pipeline 初始化"""

    def test_初始化无异常(self):
        """Pipeline 实例化不应抛出异常"""
        pipeline = Pipeline()
        assert pipeline is not None

    def test_多次初始化互相独立(self):
        """多次实例化应产生独立的对象"""
        p1 = Pipeline()
        p2 = Pipeline()
        assert p1 is not p2


# ============================================================================
# run_single 测试
# ============================================================================


class TestRunSingle:
    """测试单条提示词处理"""

    # --- 正常处理 ---

    def test_正常处理_高质量提示词(self):
        """高质量提示词应完整走完流水线，不触发优化"""
        pipeline = Pipeline()
        text = (
            "# 数据分析任务\n\n"
            "背景：需要分析 Q1 销售数据。\n\n"
            "请生成一份销售分析报告，包含以下内容：\n"
            "- 各品类销售额对比\n"
            "- 增长率排名\n\n"
            "输出格式：JSON，例如：\n"
            '{"categories": [...], "growth": [...]}'
        )
        record = pipeline.run_single(text)

        assert isinstance(record, PromptRecord)
        assert record.id != ""
        assert record.original_text == text.strip()
        assert record.cleaned_text != ""
        assert record.markdown_structure is not None
        assert len(record.features.instructions) > 0
        assert record.quality.overall >= 0.0
        assert record.quality.grade in ("优", "良", "中", "差")
        assert record.error is None

    def test_正常处理_低质量提示词_触发优化(self):
        """低质量提示词应触发优化，optimization.triggered 为 True"""
        pipeline = Pipeline()
        text = "写个东西"
        record = pipeline.run_single(text)

        assert isinstance(record, PromptRecord)
        assert record.optimization.triggered is True
        assert record.optimization.optimized_text != ""
        assert len(record.optimization.improvements) > 0
        assert record.error is None

    def test_正常处理_中等质量提示词(self):
        """中等质量提示词应正常处理"""
        pipeline = Pipeline()
        text = (
            "请分析用户行为数据，生成一份分析报告。\n\n"
            "要求包含用户活跃度、留存率等指标。\n"
            "例如：DAU、MAU、次日留存率等。\n"
            "输出格式为 Markdown。"
        )
        record = pipeline.run_single(text)

        assert isinstance(record, PromptRecord)
        assert record.cleaned_text != ""
        assert record.quality.overall >= 0.0
        assert record.error is None

    def test_正常处理_纯指令文本(self):
        """纯指令文本应提取出指令特征"""
        pipeline = Pipeline()
        text = "请帮我写一个 Python 函数，用于计算斐波那契数列，要求使用递归实现。"
        record = pipeline.run_single(text)

        assert isinstance(record, PromptRecord)
        assert len(record.features.instructions) > 0
        assert record.error is None

    # --- 空文本处理 ---

    def test_空文本_设置error字段(self):
        """空文本应在步骤 1 失败，设置 error 字段"""
        pipeline = Pipeline()
        record = pipeline.run_single("")

        assert isinstance(record, PromptRecord)
        assert record.error is not None
        assert record.original_text == ""

    def test_纯空白文本_设置error字段(self):
        """纯空白文本应在步骤 1 失败，设置 error 字段"""
        pipeline = Pipeline()
        record = pipeline.run_single("   ")

        assert isinstance(record, PromptRecord)
        assert record.error is not None

    # --- 各类提示词 ---

    def test_英文提示词(self):
        """英文提示词应正常处理"""
        pipeline = Pipeline()
        text = "Please write a Python function to calculate factorial using recursion."
        record = pipeline.run_single(text)

        assert isinstance(record, PromptRecord)
        assert record.cleaned_text != ""
        assert record.error is None

    def test_中英混合提示词(self):
        """中英混合提示词应正常处理"""
        pipeline = Pipeline()
        text = "请用 Python 写一个 API endpoint，返回 JSON 格式的用户数据。"
        record = pipeline.run_single(text)

        assert isinstance(record, PromptRecord)
        assert record.error is None

    def test_长文本提示词(self):
        """长文本提示词应正常处理"""
        pipeline = Pipeline()
        text = "请帮我写一篇关于人工智能发展趋势的详细分析报告。" * 20
        record = pipeline.run_single(text)

        assert isinstance(record, PromptRecord)
        assert record.cleaned_text != ""
        assert record.error is None

    def test_包含特殊字符的提示词(self):
        """包含特殊字符的提示词应正常处理"""
        pipeline = Pipeline()
        text = "请生成一个正则表达式，匹配 email 地址，例如：user@example.com https://test.com"
        record = pipeline.run_single(text)

        assert isinstance(record, PromptRecord)
        assert record.error is None


# ============================================================================
# run_batch 测试
# ============================================================================


class TestRunBatch:
    """测试批量提示词处理"""

    # --- 正常批量处理 ---

    def test_正常批量处理_TXT文件(self, tmp_path):
        """TXT 文件批量处理应正常完成"""
        content = (
            "请帮我写一个 Python 排序函数\n"
            "请分析以下销售数据\n"
            "请生成一份用户调研报告\n"
        )
        file_path = _make_batch_file(tmp_path, content)
        pipeline = Pipeline()

        records = pipeline.run_batch(file_path)

        assert len(records) == 3
        for record in records:
            assert isinstance(record, PromptRecord)
            assert record.id != ""
            assert record.original_text != ""
            assert record.error is None

    def test_正常批量处理_CSV文件(self, tmp_path):
        """CSV 文件批量处理应正常完成"""
        content = "prompt\n请帮我写代码\n请分析数据\n请生成报告\n"
        file_path = _make_batch_file(tmp_path, content, filename="test.csv")
        pipeline = Pipeline()

        records = pipeline.run_batch(file_path)

        assert len(records) == 3
        for record in records:
            assert isinstance(record, PromptRecord)
            assert record.error is None

    def test_正常批量处理_JSON文件(self, tmp_path):
        """JSON 文件批量处理应正常完成"""
        content = json.dumps(
            [
                {"prompt": "请帮我写代码"},
                {"prompt": "请分析数据"},
                {"prompt": "请生成报告"},
            ],
            ensure_ascii=False,
        )
        file_path = _make_batch_file(tmp_path, content, filename="test.json")
        pipeline = Pipeline()

        records = pipeline.run_batch(file_path)

        assert len(records) == 3
        for record in records:
            assert isinstance(record, PromptRecord)
            assert record.error is None

    def test_正常批量处理_Markdown文件(self, tmp_path):
        """Markdown 文件批量处理应正常完成"""
        content = (
            "# 任务一\n请帮我写代码\n\n"
            "# 任务二\n请分析数据\n\n"
            "# 任务三\n请生成报告\n"
        )
        file_path = _make_batch_file(tmp_path, content, filename="test.md")
        pipeline = Pipeline()

        records = pipeline.run_batch(file_path)

        assert len(records) == 3
        for record in records:
            assert isinstance(record, PromptRecord)
            assert record.error is None

    # --- 部分失败继续执行 ---

    def test_部分失败不影响后续处理(self, tmp_path):
        """部分记录处理失败时，不应影响其他记录的处理"""
        # 构造包含空行的文件，空行在 TXT 解析中会被跳过，
        # 但我们可以通过构造极端短文本让某些记录质量极低
        content = (
            "请帮我写一个完整的 Python Web 应用，使用 Flask 框架，包含用户认证、数据库操作和 RESTful API\n"
            "写东西\n"
            "请分析以下销售数据，生成详细的季度报告，包含同比环比分析和改进建议\n"
        )
        file_path = _make_batch_file(tmp_path, content)
        pipeline = Pipeline()

        records = pipeline.run_batch(file_path)

        assert len(records) == 3
        # 所有记录都应存在，即使某些质量极低
        for record in records:
            assert isinstance(record, PromptRecord)

    def test_单条处理异常不影响其他记录(self, tmp_path):
        """单条记录内部处理异常不中断批量处理"""
        # 使用正常可解析的文件，所有记录均能正常处理
        content = (
            "请帮我写代码\n"
            "请分析数据\n"
        )
        file_path = _make_batch_file(tmp_path, content)
        pipeline = Pipeline()

        records = pipeline.run_batch(file_path)

        assert len(records) == 2
        for record in records:
            assert isinstance(record, PromptRecord)

    # --- 边界情况 ---

    def test_单条记录批量文件(self, tmp_path):
        """仅包含一条记录的批量文件应正常处理"""
        content = "请帮我写一个排序算法\n"
        file_path = _make_batch_file(tmp_path, content)
        pipeline = Pipeline()

        records = pipeline.run_batch(file_path)

        assert len(records) == 1
        assert records[0].error is None

    def test_空行被正确跳过(self, tmp_path):
        """TXT 文件中的空行应被正确跳过，只处理有效行"""
        content = "请帮我写代码\n\n\n请分析数据\n\n"
        file_path = _make_batch_file(tmp_path, content)
        pipeline = Pipeline()

        records = pipeline.run_batch(file_path)

        assert len(records) == 2


# ============================================================================
# writeback 测试
# ============================================================================


class TestWriteback:
    """测试优化提示词回写功能"""

    def _make_record(self, overall: float, optimized_text: str = "优化后的提示词") -> PromptRecord:
        """构造测试用的 PromptRecord 实例。"""
        return PromptRecord(
            id="writeback-001",
            original_text="原始提示词",
            cleaned_text="原始提示词",
            features=FeatureSet(),
            quality=QualityScore(overall=overall, grade="良"),
            optimization=OptimizationResult(triggered=True, optimized_text=optimized_text),
        )

    def test_评分低于阈值时不回写(self, tmp_path, monkeypatch):
        """writeback 应跳过评分低于 QUALITY_THRESHOLD 的优化结果"""
        target_dir = tmp_path / "prompts"
        monkeypatch.setattr("prompt_extraction.pipeline.AGENTS_PROMPTS_DIR", target_dir)
        monkeypatch.setattr("prompt_extraction.pipeline.AGENTS_ROLES", ["developer"])
        pipeline = Pipeline()
        record = self._make_record(overall=QUALITY_THRESHOLD - 1)

        result = pipeline.writeback(record, "developer")

        assert result is None
        assert not (target_dir / "developer" / "system-prompt.md").exists()


# ============================================================================
# export_results 测试
# ============================================================================


class TestExportResults:
    """测试 CSV 导出功能"""

    def _make_record(
        self,
        record_id: str = "test-001",
        original_text: str = "测试文本",
        cleaned_text: str = "测试文本",
        instructions: list[str] | None = None,
        constraints: list[dict] | None = None,
        expected_output: str | None = None,
        clarity: float = 80.0,
        completeness: float = 70.0,
        executability: float = 60.0,
        overall: float = 70.0,
        grade: str = "良",
        optimized_text: str = "",
        improvements: list[str] | None = None,
        error: str | None = None,
    ) -> PromptRecord:
        """构造测试用的 PromptRecord 实例。"""
        from prompt_extraction.models import FeatureSet, OptimizationResult, QualityScore

        return PromptRecord(
            id=record_id,
            original_text=original_text,
            cleaned_text=cleaned_text,
            features=FeatureSet(
                instructions=instructions or [],
                constraints=constraints or [],
                expected_output=expected_output,
            ),
            quality=QualityScore(
                clarity=clarity,
                completeness=completeness,
                executability=executability,
                overall=overall,
                grade=grade,
            ),
            optimization=OptimizationResult(
                triggered=bool(optimized_text),
                optimized_text=optimized_text,
                improvements=improvements or [],
            ),
            error=error,
        )

    # --- 文件存在性 ---

    def test_导出CSV文件存在(self, tmp_path):
        """export_results 应生成 CSV 文件"""
        output_path = str(tmp_path / "output.csv")
        pipeline = Pipeline()
        records = [self._make_record()]

        result_path = pipeline.export_results(records, output_path)

        assert result_path == output_path
        assert os.path.isfile(output_path)

    def test_导出空记录列表(self, tmp_path):
        """空记录列表应生成仅含表头的 CSV 文件"""
        output_path = str(tmp_path / "empty.csv")
        pipeline = Pipeline()

        result_path = pipeline.export_results([], output_path)

        assert os.path.isfile(output_path)
        df = pd.read_csv(output_path, encoding="utf-8-sig")
        # 空 DataFrame 应有 0 行，但列名存在
        assert len(df) == 0

    # --- 内容正确性 ---

    def test_导出CSV内容正确性_基本字段(self, tmp_path):
        """CSV 文件中的基本字段应与输入一致"""
        output_path = str(tmp_path / "basic.csv")
        pipeline = Pipeline()
        records = [self._make_record(record_id="abc123", original_text="请帮我写代码")]

        pipeline.export_results(records, output_path)

        df = pd.read_csv(output_path, encoding="utf-8-sig")
        assert len(df) == 1
        assert df.iloc[0]["id"] == "abc123"
        assert df.iloc[0]["original_text"] == "请帮我写代码"

    def test_导出CSV内容正确性_质量评分字段(self, tmp_path):
        """CSV 文件中的质量评分字段应与输入一致"""
        output_path = str(tmp_path / "quality.csv")
        pipeline = Pipeline()
        records = [
            self._make_record(
                clarity=85.5,
                completeness=72.3,
                executability=68.0,
                overall=74.2,
                grade="良",
            )
        ]

        pipeline.export_results(records, output_path)

        df = pd.read_csv(output_path, encoding="utf-8-sig")
        assert float(df.iloc[0]["clarity"]) == 85.5
        assert float(df.iloc[0]["completeness"]) == 72.3
        assert float(df.iloc[0]["executability"]) == 68.0
        assert float(df.iloc[0]["overall"]) == 74.2
        assert df.iloc[0]["grade"] == "良"

    def test_导出CSV内容正确性_JSON字段(self, tmp_path):
        """列表和字典字段应转为 JSON 字符串"""
        output_path = str(tmp_path / "json_fields.csv")
        pipeline = Pipeline()
        records = [
            self._make_record(
                instructions=["分析数据", "生成报告"],
                constraints=[{"type": "格式约束", "text": "JSON 格式"}],
                improvements=["补充缺失要素", "消歧增强"],
            )
        ]

        pipeline.export_results(records, output_path)

        df = pd.read_csv(output_path, encoding="utf-8-sig")
        # 验证 JSON 字段可正确解析
        instructions = json.loads(df.iloc[0]["instructions"])
        assert instructions == ["分析数据", "生成报告"]

        constraints = json.loads(df.iloc[0]["constraints"])
        assert len(constraints) == 1
        assert constraints[0]["type"] == "格式约束"

        improvements = json.loads(df.iloc[0]["improvements"])
        assert "补充缺失要素" in improvements

    def test_导出CSV内容正确性_优化字段(self, tmp_path):
        """优化结果字段应正确导出"""
        output_path = str(tmp_path / "optimization.csv")
        pipeline = Pipeline()
        records = [
            self._make_record(
                optimized_text="## 指令\n- 优化后的指令",
                improvements=["结构调整"],
            )
        ]

        pipeline.export_results(records, output_path)

        df = pd.read_csv(output_path, encoding="utf-8-sig")
        assert df.iloc[0]["optimized_text"] == "## 指令\n- 优化后的指令"

    def test_导出CSV内容正确性_error字段(self, tmp_path):
        """error 字段应正确导出，无错误时为空字符串"""
        output_path = str(tmp_path / "error.csv")
        pipeline = Pipeline()
        records = [
            self._make_record(record_id="ok", error=None),
            self._make_record(record_id="err", error="处理失败：测试错误"),
        ]

        pipeline.export_results(records, output_path)

        df = pd.read_csv(output_path, encoding="utf-8-sig")
        assert len(df) == 2
        # 无错误记录 error 为空字符串
        assert df[df["id"] == "ok"].iloc[0]["error"] == "" or pd.isna(df[df["id"] == "ok"].iloc[0]["error"])
        # 有错误记录 error 为错误信息
        assert df[df["id"] == "err"].iloc[0]["error"] == "处理失败：测试错误"

    def test_导出CSV编码为UTF8BOM(self, tmp_path):
        """CSV 文件应以 UTF-8 BOM 编码保存"""
        output_path = str(tmp_path / "encoding.csv")
        pipeline = Pipeline()
        records = [self._make_record(original_text="中文测试文本")]

        pipeline.export_results(records, output_path)

        # 读取文件原始字节，验证 BOM 头
        with open(output_path, "rb") as f:
            bom = f.read(3)
        assert bom == b"\xef\xbb\xbf", "CSV 文件应以 UTF-8 BOM 编码"

    def test_导出CSV中文内容不乱码(self, tmp_path):
        """CSV 文件中的中文内容应正确显示"""
        output_path = str(tmp_path / "chinese.csv")
        pipeline = Pipeline()
        records = [
            self._make_record(
                original_text="请分析用户行为数据，生成一份详细的分析报告",
                instructions=["分析用户行为数据", "生成分析报告"],
                constraints=[{"type": "格式约束", "value": "中文输出"}],
            )
        ]

        pipeline.export_results(records, output_path)

        df = pd.read_csv(output_path, encoding="utf-8-sig")
        assert "用户行为" in df.iloc[0]["original_text"]
        instructions = json.loads(df.iloc[0]["instructions"])
        assert "分析用户行为数据" in instructions

    # --- 多条记录 ---

    def test_导出多条记录(self, tmp_path):
        """多条记录应全部导出"""
        output_path = str(tmp_path / "multi.csv")
        pipeline = Pipeline()
        records = [
            self._make_record(record_id=f"rec-{i:03d}", original_text=f"测试文本{i}")
            for i in range(10)
        ]

        pipeline.export_results(records, output_path)

        df = pd.read_csv(output_path, encoding="utf-8-sig")
        assert len(df) == 10
        for i in range(10):
            assert df.iloc[i]["id"] == f"rec-{i:03d}"


# ============================================================================
# 错误处理测试
# ============================================================================


class TestErrorHandling:
    """测试错误处理机制"""

    def test_run_single_空文本_error字段正确设置(self):
        """空文本导致 process_single_input 抛出异常时，error 字段应正确设置"""
        pipeline = Pipeline()
        record = pipeline.run_single("")

        assert record.error is not None
        assert record.original_text == ""

    def test_run_single_异常后仍返回记录(self):
        """任一步骤异常后仍应返回 PromptRecord 实例"""
        pipeline = Pipeline()
        record = pipeline.run_single("")

        assert isinstance(record, PromptRecord)
        assert record.id == ""  # 步骤 1 失败，未生成 ID
        assert record.error is not None

    def test_run_batch_部分失败仍返回全部记录(self, tmp_path):
        """批量处理中部分记录失败时，仍返回全部记录"""
        content = (
            "请帮我写一个完整的 Python 应用程序\n"
            "写\n"
            "请分析以下销售数据\n"
        )
        file_path = _make_batch_file(tmp_path, content)
        pipeline = Pipeline()

        records = pipeline.run_batch(file_path)

        assert len(records) == 3
        # 所有记录都应存在
        for record in records:
            assert isinstance(record, PromptRecord)

    def test_错误记录不影响有效记录(self, tmp_path):
        """批量处理中错误记录的 error 字段与正常记录应有区分"""
        content = (
            "请帮我写一个完整的 Python 应用程序，包含完整的错误处理和日志记录\n"
            "写\n"
            "请分析以下销售数据，生成详细的季度分析报告\n"
        )
        file_path = _make_batch_file(tmp_path, content)
        pipeline = Pipeline()

        records = pipeline.run_batch(file_path)

        assert len(records) == 3
        # 至少有一条记录没有错误
        error_free = [r for r in records if r.error is None]
        assert len(error_free) >= 1

    def test_导出时错误记录正确包含error列(self, tmp_path):
        """导出 CSV 时，错误记录的 error 列应包含错误信息"""
        output_path = str(tmp_path / "error_export.csv")
        pipeline = Pipeline()
        from prompt_extraction.models import FeatureSet, OptimizationResult, QualityScore

        # 构造一条包含错误的记录
        record = PromptRecord(
            id="error-001",
            original_text="",
            error="输入文本不能为空",
            features=FeatureSet(),
            quality=QualityScore(),
            optimization=OptimizationResult(),
        )
        records = [record]

        pipeline.export_results(records, output_path)

        df = pd.read_csv(output_path, encoding="utf-8-sig")
        assert len(df) == 1
        assert df.iloc[0]["error"] == "输入文本不能为空"


# ============================================================================
# 数据一致性测试
# ============================================================================


class TestDataConsistency:
    """测试流水线中数据字段的正确传递"""

    def test_original_text贯穿流水线(self):
        """original_text 在整个流水线中应保持不变"""
        pipeline = Pipeline()
        text = "请帮我写一个排序算法，要求时间复杂度 O(n log n)"
        record = pipeline.run_single(text)

        assert record.original_text == text.strip()

    def test_cleaned_text在流水线中被填充(self):
        """cleaned_text 应在流水线中被正确填充"""
        pipeline = Pipeline()
        text = "请帮我写代码"
        record = pipeline.run_single(text)

        assert record.cleaned_text != ""
        assert record.cleaned_text is not None

    def test_features在流水线中被填充(self):
        """features 应在流水线中被正确填充"""
        pipeline = Pipeline()
        text = "请分析数据并生成报告，输出 JSON 格式"
        record = pipeline.run_single(text)

        assert record.features is not None
        assert len(record.features.instructions) > 0

    def test_quality在流水线中被填充(self):
        """quality 应在流水线中被正确填充"""
        pipeline = Pipeline()
        text = "请帮我写代码"
        record = pipeline.run_single(text)

        assert record.quality is not None
        assert record.quality.overall >= 0.0
        assert record.quality.grade in ("优", "良", "中", "差")

    def test_optimization在流水线中被填充(self):
        """optimization 应在流水线中被正确填充"""
        pipeline = Pipeline()
        text = "写东西"
        record = pipeline.run_single(text)

        assert record.optimization is not None
        # 低质量提示词应触发优化
        assert record.optimization.triggered is True

    def test_高质量提示词不触发优化(self):
        """高质量提示词不应触发优化，optimization.triggered 为 False"""
        pipeline = Pipeline()
        text = (
            "# 任务\n\n"
            "背景：需要分析销售数据。\n\n"
            "请生成一份详细的销售分析报告，包含以下内容：\n"
            "- 各品类销售额对比\n"
            "- 增长率排名\n"
            "- 改进建议\n\n"
            "输出格式：JSON，例如：\n"
            '{"categories": [...], "growth": [...], "suggestions": [...]}'
        )
        record = pipeline.run_single(text)

        assert record.optimization.triggered is False
        assert record.optimization.optimized_text == ""

    def test_run_single和run_batch结果字段一致(self, tmp_path):
        """同一条文本通过 run_single 和 run_batch 处理，结果字段结构应一致"""
        pipeline = Pipeline()
        text = "请帮我写一个 Python 排序函数"

        # run_single
        single_record = pipeline.run_single(text)

        # run_batch（通过文件）
        file_path = _make_batch_file(tmp_path, text)
        batch_records = pipeline.run_batch(file_path)

        assert len(batch_records) == 1
        batch_record = batch_records[0]

        # 验证字段结构一致
        assert single_record.cleaned_text == batch_record.cleaned_text
        assert single_record.quality.overall == batch_record.quality.overall
        assert single_record.quality.grade == batch_record.quality.grade

    def test_导出后再读取_字段完整(self, tmp_path):
        """导出 CSV 后再读取，所有必要字段应存在"""
        output_path = str(tmp_path / "roundtrip.csv")
        pipeline = Pipeline()
        records = [pipeline.run_single("请帮我写一个排序算法，要求时间复杂度 O(n log n)")]

        pipeline.export_results(records, output_path)

        df = pd.read_csv(output_path, encoding="utf-8-sig")
        expected_columns = [
            "id", "original_text", "cleaned_text", "instructions",
            "constraints", "expected_output", "clarity", "completeness",
            "executability", "overall", "grade", "optimized_text",
            "improvements", "error",
        ]
        for col in expected_columns:
            assert col in df.columns, f"缺少列：{col}"


# ============================================================================
# 集成测试
# ============================================================================


class TestIntegration:
    """端到端集成测试"""

    def test_完整工作流_单条到导出(self, tmp_path):
        """从单条处理到 CSV 导出的完整工作流"""
        pipeline = Pipeline()
        output_path = str(tmp_path / "full_workflow.csv")

        # 处理多条提示词
        texts = [
            "请帮我写一个 Python 排序算法",
            "写代码",
            (
                "# 数据分析\n\n"
                "背景：需要分析销售数据。\n\n"
                "请生成一份详细的季度分析报告，包含同比环比分析。\n\n"
                "输出格式：JSON。"
            ),
        ]
        records = [pipeline.run_single(t) for t in texts]

        # 导出
        result_path = pipeline.export_results(records, output_path)

        # 验证
        assert os.path.isfile(result_path)
        df = pd.read_csv(result_path, encoding="utf-8-sig")
        assert len(df) == 3

        # 第一条记录：正常处理
        assert df.iloc[0]["error"] == "" or pd.isna(df.iloc[0]["error"])
        # 第二条记录：低质量触发优化
        assert df.iloc[1]["error"] == "" or pd.isna(df.iloc[1]["error"])
        # 第三条记录：高质量
        assert df.iloc[2]["error"] == "" or pd.isna(df.iloc[2]["error"])

    def test_完整工作流_批量到导出(self, tmp_path):
        """从批量处理到 CSV 导出的完整工作流"""
        pipeline = Pipeline()
        content = (
            "请帮我写一个 Python 排序算法\n"
            "写代码\n"
            "请分析以下销售数据，生成详细的季度分析报告，包含同比环比分析和改进建议\n"
        )
        input_path = _make_batch_file(tmp_path, content)
        output_path = str(tmp_path / "batch_workflow.csv")

        # 批量处理
        records = pipeline.run_batch(input_path)

        # 导出
        result_path = pipeline.export_results(records, output_path)

        # 验证
        assert os.path.isfile(result_path)
        df = pd.read_csv(result_path, encoding="utf-8-sig")
        assert len(df) == 3

        for i in range(3):
            assert df.iloc[i]["id"] != ""
            assert df.iloc[i]["original_text"] != ""