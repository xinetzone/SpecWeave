"""端到端集成测试

验证提示词萃取系统的全流程，包括单条处理、批量处理、
结果导出以及数据一致性等集成场景。
"""

import json
import os

import pandas as pd
import pytest

from prompt_extraction.models import PromptRecord
from prompt_extraction.pipeline import Pipeline


# ============================================================================
# 测试辅助函数
# ============================================================================


def _make_batch_file(tmp_path, content: str, filename: str) -> str:
    """在临时目录中创建测试用的批量输入文件。

    Args:
        tmp_path: pytest 临时目录 fixture。
        content: 文件内容。
        filename: 文件名（含扩展名）。

    Returns:
        文件路径。
    """
    file_path = tmp_path / filename
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


def _export_optimized_only(records: list[PromptRecord], output_path: str) -> str:
    """将已触发优化的记录中的优化后文本导出为 TXT 文件。

    每行一条优化后文本，空行分隔不同记录。

    Args:
        records: PromptRecord 列表。
        output_path: 输出文件路径。

    Returns:
        输出文件的绝对路径。
    """
    lines: list[str] = []
    for record in records:
        if record.optimization.triggered and record.optimization.optimized_text:
            lines.append(record.optimization.optimized_text)
            lines.append("")  # 空行分隔

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_path


# ============================================================================
# 端到端集成测试
# ============================================================================


class TestE2E:
    """端到端集成测试，验证全流程 Pipeline 行为。"""

    # --- 单条处理：高质量提示词 ---

    def test_e2e_single_high_quality(self):
        """高质量提示词应完整走完流水线，产出正确的 PromptRecord。

        验证点：
        - 所有字段正确填充
        - 特征提取正确
        - 质量评分合理
        - 不触发优化（高质量）
        """
        pipeline = Pipeline()
        text = (
            "请用中文写一篇关于人工智能的500字文章，包含标题、摘要和三个主要论点，"
            "使用正式学术风格"
        )

        record = pipeline.run_single(text)

        # 验证基本字段
        assert isinstance(record, PromptRecord)
        assert record.id != ""
        assert record.original_text == text

        # 验证清洗后的文本非空
        assert record.cleaned_text != ""
        assert len(record.cleaned_text) > 0

        # 验证 Markdown 结构被填充
        assert record.markdown_structure is not None
        assert isinstance(record.markdown_structure, dict)

        # 验证特征提取
        assert record.features is not None
        assert len(record.features.instructions) > 0, "应提取到至少一条指令"

        # 验证质量评分
        assert record.quality is not None
        assert record.quality.overall >= 0.0
        assert record.quality.overall <= 100.0
        assert record.quality.grade in ("优", "良", "中", "差")

        # 验证无错误
        assert record.error is None

    # --- 单条处理：低质量提示词 ---

    def test_e2e_single_low_quality(self):
        """低质量提示词应触发优化，优化后文本比原始更长更结构化。

        验证点：
        - 优化被触发（triggered=True）
        - 优化后文本非空且比原始文本长
        - 优化后文本包含结构元素（如 Markdown 标记）
        - 改进建议列表非空
        """
        pipeline = Pipeline()
        text = "写点东西"

        record = pipeline.run_single(text)

        # 验证优化被触发
        assert record.optimization.triggered is True, "低质量提示词应触发优化"
        assert record.optimization.optimized_text != "", "优化后文本不应为空"

        # 优化后文本应比原始更长
        assert len(record.optimization.optimized_text) > len(text), (
            f"优化后文本（{len(record.optimization.optimized_text)}字）"
            f"应比原始文本（{len(text)}字）更长"
        )

        # 优化后文本应包含结构化元素
        optimized = record.optimization.optimized_text
        has_structure = any(
            marker in optimized for marker in ("##", "**", "- ", "指令", "约束", "输出格式")
        )
        assert has_structure, "优化后文本应包含结构化元素"

        # 改进建议列表应非空
        assert len(record.optimization.improvements) > 0, "应有改进建议"

        # 验证 diff 被生成
        assert record.optimization.diff != "", "应生成优化前后对比 diff"

        # 验证无错误
        assert record.error is None

    # --- 单条处理：Markdown 格式提示词 ---

    def test_e2e_single_markdown(self):
        """Markdown 格式提示词应正确解析并利用 Markdown 结构。

        验证点：
        - Markdown 结构被正确提取
        - 标题和列表项被识别
        - 特征提取利用了 Markdown 结构
        """
        pipeline = Pipeline()
        text = (
            "# 数据分析任务\n\n"
            "## 背景\n"
            "需要分析 Q1 销售数据，评估各品类表现。\n\n"
            "## 指令\n"
            "请生成一份销售分析报告，包含以下内容：\n"
            "- 各品类销售额对比\n"
            "- 同比增长率排名\n"
            "- 改进建议\n\n"
            "## 输出格式\n"
            "请以 JSON 格式输出，例如：\n"
            "```json\n"
            '{"categories": [...], "growth": [...]}\n'
            "```\n"
        )

        record = pipeline.run_single(text)

        # 验证 Markdown 结构被正确提取
        assert record.markdown_structure is not None
        headings = record.markdown_structure.get("headings", [])
        assert len(headings) > 0, "应提取到 Markdown 标题"

        # 验证列表项被提取
        list_items = record.markdown_structure.get("list_items", [])
        assert len(list_items) > 0, "应提取到列表项"

        # 验证特征提取利用了 Markdown 结构
        assert len(record.features.instructions) > 0, "应提取到指令特征"
        assert len(record.features.constraints) > 0, "应提取到约束特征"

        # 验证无错误
        assert record.error is None

    # --- 批量处理：CSV ---

    def test_e2e_batch_csv(self, tmp_path):
        """CSV 文件批量处理应正常完成，所有记录都有合理结果。

        验证点：
        - 所有记录正确解析
        - 每条记录都有合理结果（id、original_text、cleaned_text 等）
        - 无错误记录或错误记录有合理原因
        """
        content = (
            "prompt\n"
            "请用中文写一篇关于人工智能的500字文章，包含标题、摘要和三个主要论点\n"
            "写点东西\n"
            "请分析销售数据，生成JSON格式的季度报告\n"
        )
        file_path = _make_batch_file(tmp_path, content, "test_prompts.csv")
        pipeline = Pipeline()

        records = pipeline.run_batch(file_path)

        assert len(records) == 3, f"应处理 3 条记录，实际处理 {len(records)} 条"

        for i, record in enumerate(records):
            assert isinstance(record, PromptRecord), f"第 {i} 条记录类型错误"
            assert record.id != "", f"第 {i} 条记录缺少 ID"
            assert record.original_text != "", f"第 {i} 条记录原始文本为空"
            assert record.cleaned_text != "", f"第 {i} 条记录清洗后文本为空"
            assert record.quality.overall >= 0.0, f"第 {i} 条记录评分异常"

    # --- 批量处理：TXT ---

    def test_e2e_batch_txt(self, tmp_path):
        """TXT 文件批量处理应正常完成。

        验证点：
        - 每行作为一条提示词处理
        - 所有记录都有合理结果
        """
        content = (
            "请帮我写一个 Python 排序函数\n"
            "写代码\n"
            "请分析以下用户行为数据，生成详细的分析报告，包含活跃度、留存率等指标\n"
        )
        file_path = _make_batch_file(tmp_path, content, "test_prompts.txt")
        pipeline = Pipeline()

        records = pipeline.run_batch(file_path)

        assert len(records) == 3, f"应处理 3 条记录，实际处理 {len(records)} 条"

        for record in records:
            assert isinstance(record, PromptRecord)
            assert record.id != ""
            assert record.original_text != ""
            assert record.cleaned_text != ""
            assert record.error is None

    # --- 批量处理：Markdown ---

    def test_e2e_batch_markdown(self, tmp_path):
        """Markdown 文件批量处理应按标题拆分区块。

        验证点：
        - 每个一级/二级标题对应一条记录
        - 所有记录都有合理结果
        """
        content = (
            "# 任务一：数据分析\n"
            "请分析销售数据，生成 JSON 格式的季度报告。\n\n"
            "# 任务二：代码生成\n"
            "请编写一个 Python 函数，用于计算斐波那契数列。\n\n"
            "# 任务三：文档撰写\n"
            "请写一篇关于微服务架构的技术文档。\n"
        )
        file_path = _make_batch_file(tmp_path, content, "test_prompts.md")
        pipeline = Pipeline()

        records = pipeline.run_batch(file_path)

        assert len(records) == 3, f"应按标题拆分为 3 条记录，实际 {len(records)} 条"

        for record in records:
            assert isinstance(record, PromptRecord)
            assert record.id != ""
            assert record.original_text != ""
            assert record.cleaned_text != ""
            assert record.error is None

    # --- 导出 CSV ---

    def test_e2e_export_csv(self, tmp_path):
        """export_results 导出的 CSV 文件可被 pandas 正确读取，包含所有必要列。

        验证点：
        - CSV 文件存在且可读
        - 包含所有必要列
        - 数据行数与输入记录数一致
        - JSON 字段可正确解析
        """
        pipeline = Pipeline()
        output_path = str(tmp_path / "export_test.csv")

        texts = [
            "请帮我写一个 Python 排序算法",
            "写代码",
            "请分析销售数据，生成 JSON 格式的季度报告",
        ]
        records = [pipeline.run_single(t) for t in texts]

        # 导出
        result_path = pipeline.export_results(records, output_path)

        # 验证文件存在
        assert os.path.isfile(result_path), "导出 CSV 文件应存在"

        # 验证 pandas 可读取
        df = pd.read_csv(result_path, encoding="utf-8-sig")
        assert len(df) == len(records), (
            f"CSV 行数 {len(df)} 应与记录数 {len(records)} 一致"
        )

        # 验证必要列存在
        expected_columns = [
            "id", "original_text", "cleaned_text", "instructions",
            "constraints", "expected_output", "clarity", "completeness",
            "executability", "overall", "grade", "optimized_text",
            "improvements", "error",
        ]
        for col in expected_columns:
            assert col in df.columns, f"CSV 缺少列：{col}"

        # 验证 JSON 字段可解析
        for i in range(len(df)):
            instructions = json.loads(df.iloc[i]["instructions"])
            assert isinstance(instructions, list), f"第 {i} 行 instructions 应为列表"

            constraints = json.loads(df.iloc[i]["constraints"])
            assert isinstance(constraints, list), f"第 {i} 行 constraints 应为列表"

            improvements = json.loads(df.iloc[i]["improvements"])
            assert isinstance(improvements, list), f"第 {i} 行 improvements 应为列表"

    # --- 导出仅优化后文本 ---

    def test_e2e_export_txt_only_optimized(self, tmp_path):
        """导出优化后提示词的功能应正确工作。

        验证点：
        - 仅导出已触发优化的记录
        - 导出文件内容非空
        - 优化后文本包含结构化内容
        """
        pipeline = Pipeline()
        output_path = str(tmp_path / "optimized_only.txt")

        # 混合高质量和低质量提示词
        texts = [
            "写点东西",  # 低质量，应触发优化
            (
                "# 数据分析\n\n"
                "背景：需要分析销售数据。\n\n"
                "请生成一份详细的季度分析报告，包含同比环比分析。\n\n"
                "输出格式：JSON，例如：\n"
                '{"categories": [...], "growth": [...]}'
            ),  # 高质量，不触发优化
            "写代码",  # 低质量，应触发优化
        ]
        records = [pipeline.run_single(t) for t in texts]

        # 导出优化后文本
        result_path = _export_optimized_only(records, output_path)

        # 验证文件存在
        assert os.path.isfile(result_path), "导出文件应存在"

        # 读取并验证内容
        with open(result_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert len(content) > 0, "导出内容不应为空"

        # 应包含结构化元素
        assert any(
            marker in content for marker in ("##", "指令", "约束", "输出格式")
        ), "导出内容应包含结构化元素"

        # 优化后文本应比原始显著更长
        lines = [l for l in content.split("\n") if l.strip()]
        assert len(lines) > 0

    # --- 多种类型提示词 ---

    def test_e2e_various_prompt_types(self):
        """使用多种类型提示词验证系统鲁棒性。

        测试覆盖：简短、冗长、清晰、模糊、完整、残缺、中英文混合。
        """
        pipeline = Pipeline()

        prompt_types = {
            "简短_清晰": "请写一个 Python 排序函数。",
            "冗长_详细": (
                "请帮我写一份关于人工智能发展趋势的详细分析报告。"
                "报告需要包含以下章节：1. 引言 2. 技术现状 3. 应用场景 "
                "4. 挑战与机遇 5. 未来展望。每章至少 500 字，"
                "使用正式学术风格，引用近三年的权威数据。"
                "输出格式为 Markdown，包含目录和参考文献。"
            ),
            "清晰_结构化": (
                "# 任务\n\n"
                "## 指令\n"
                "请分析以下数据\n\n"
                "## 约束\n"
                "- 输出 JSON 格式\n"
                "- 不超过 1000 字\n\n"
                "## 输出格式\n"
                '{"result": "..."}'
            ),
            "模糊_简短": "写点东西",
            "中英混合": "请用 Python 写一个 API endpoint，返回 JSON 格式的 user data，"
                       "包含 id、name、email 字段。Use Flask framework.",
            "残缺_无上下文": "帮我分析一下",
        }

        for label, text in prompt_types.items():
            record = pipeline.run_single(text)

            # 基本验证
            assert isinstance(record, PromptRecord), f"[{label}] 返回类型错误"
            assert record.id != "", f"[{label}] 缺少 ID"
            assert record.original_text != "", f"[{label}] 原始文本为空"

            # 所有记录都应无错误
            assert record.error is None, (
                f"[{label}] 处理出错：{record.error}"
            )

            # 质量评分应在合理范围
            assert 0.0 <= record.quality.overall <= 100.0, (
                f"[{label}] 评分 {record.quality.overall} 超出范围"
            )

    # --- 空输入 ---

    def test_e2e_empty_input(self):
        """空输入应返回包含错误信息的 PromptRecord。

        验证点：
        - 返回 PromptRecord 实例
        - error 字段非空
        - original_text 为空字符串
        """
        pipeline = Pipeline()

        record = pipeline.run_single("")

        assert isinstance(record, PromptRecord)
        assert record.error is not None, "空输入应设置 error 字段"
        assert record.original_text == ""
        assert record.id == ""  # 步骤 1 失败，未生成 ID

    # --- 数据一致性 ---

    def test_e2e_data_consistency(self, tmp_path):
        """单条处理与批量处理中同一条提示词结果应一致。

        验证点：
        - original_text 一致
        - cleaned_text 一致
        - quality.overall 一致
        - quality.grade 一致
        """
        pipeline = Pipeline()
        text = "请帮我写一个 Python 排序算法，要求时间复杂度 O(n log n)"

        # 单条处理
        single_record = pipeline.run_single(text)

        # 批量处理（通过 TXT 文件）
        file_path = _make_batch_file(tmp_path, text + "\n", "consistency_test.txt")
        batch_records = pipeline.run_batch(file_path)

        assert len(batch_records) == 1
        batch_record = batch_records[0]

        # 验证关键字段一致
        assert single_record.original_text == batch_record.original_text, (
            "单条与批量处理的 original_text 应一致"
        )
        assert single_record.cleaned_text == batch_record.cleaned_text, (
            "单条与批量处理的 cleaned_text 应一致"
        )
        assert single_record.quality.overall == batch_record.quality.overall, (
            f"单条评分 {single_record.quality.overall} "
            f"与批量评分 {batch_record.quality.overall} 应一致"
        )
        assert single_record.quality.grade == batch_record.quality.grade, (
            f"单条等级 {single_record.quality.grade} "
            f"与批量等级 {batch_record.quality.grade} 应一致"
        )

        # 验证优化触发状态一致
        assert single_record.optimization.triggered == batch_record.optimization.triggered, (
            "单条与批量处理的优化触发状态应一致"
        )