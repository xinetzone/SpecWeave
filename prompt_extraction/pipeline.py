"""提示词萃取流水线编排器

串联输入处理、预处理、特征提取、质量评估和优化生成模块，
提供单条处理、批量处理和结果导出能力。
支持将优化后的提示词回写至 .agents/prompts/ 角色目录。
"""

import json
from pathlib import Path

import pandas as pd

from prompt_extraction.assessment.evaluator import evaluate
from prompt_extraction.config import QUALITY_THRESHOLD, AGENTS_PROMPTS_DIR, AGENTS_ROLES
from prompt_extraction.constants import DEFAULT_OUTPUT_DIR
from prompt_extraction.extraction.extractor import extract_features
from prompt_extraction.input.input_handler import process_batch_input, process_single_input
from prompt_extraction.models import PromptRecord
from prompt_extraction.optimization.optimizer import optimize
from prompt_extraction.preprocessing.cleaner import clean_text
from prompt_extraction.preprocessing.normalizer import normalize_text

# ── CSV 导出列名常量 ───────────────────────────────────────────────────
EXPORT_COLUMNS = [
    "id", "original_text", "cleaned_text", "instructions",
    "constraints", "expected_output", "clarity", "completeness",
    "executability", "overall", "grade", "optimized_text",
    "improvements", "error",
]


class Pipeline:
    """提示词萃取流水线编排器。

    串联所有处理模块，提供单条处理、批量处理和结果导出能力。
    """

    def __init__(self) -> None:
        """初始化流水线，无需特殊操作。"""
        pass

    def _process_record(self, record: PromptRecord) -> PromptRecord:
        """对 PromptRecord 执行流水线核心步骤（步骤 2-6）。

        依次执行清洗、标准化、特征提取、质量评估和优化，
        任一步骤抛出异常时记录 error 字段并继续。

        Args:
            record: 已设置 original_text 的 PromptRecord 实例。

        Returns:
            填充完整的 PromptRecord 实例。
        """
        try:
            # 步骤 2：文本清洗，获取清洗后文本和 Markdown 结构信息
            cleaned_text_result, md_structure, _metadata = clean_text(record.original_text)
            record.cleaned_text = cleaned_text_result
            record.markdown_structure = md_structure

            # 步骤 3：文本标准化
            normalized = normalize_text(record.cleaned_text)
            record.cleaned_text = normalized

            # 步骤 4：特征提取
            features = extract_features(record.cleaned_text, md_structure)
            record.features = features

            # 步骤 5：质量评估
            quality = evaluate(record.cleaned_text, features)
            record.quality = quality

            # 步骤 6：低于阈值时触发优化
            if quality.overall < QUALITY_THRESHOLD:
                optimization = optimize(record)
                record.optimization = optimization
        except Exception as e:
            record.error = str(e)

        return record

    def run_single(self, text: str) -> PromptRecord:
        """处理单条提示词的完整流水线。

        Args:
            text: 单条提示词文本。

        Returns:
            填充完整的 PromptRecord 实例。若任一步骤异常，error 字段将包含错误信息。
        """
        # 步骤 1：创建 PromptRecord
        try:
            record = process_single_input(text)
        except Exception as e:
            record = PromptRecord(original_text=text, error=str(e))
            return record

        # 步骤 2-6：执行核心流水线
        return self._process_record(record)

    def run_batch(self, file_path: str) -> list[PromptRecord]:
        """批量处理提示词文件。

        先调用解析器解析文件为 PromptRecord 列表，
        再对每条记录依次执行核心流水线步骤。
        单条记录失败不影响后续记录的处理。

        Args:
            file_path: 待处理的文件路径（支持 CSV、JSON、TXT、Markdown）。

        Returns:
            所有 PromptRecord 列表（含错误记录）。
        """
        # 步骤 1：解析文件，获取 PromptRecord 列表
        records = process_batch_input(file_path)

        # 步骤 2-6：逐条执行核心流水线
        results: list[PromptRecord] = []
        for record in records:
            processed = self._process_record(record)
            results.append(processed)

        return results

    def writeback(self, record: PromptRecord, role: str) -> str | None:
        """将优化后的提示词回写至 .agents/prompts/<role>/ 目录。

        若记录的优化评分高于阈值，则将优化后文本追加到对应角色的
        system-prompt.md 文件末尾（以"## 萃取优化模式"章节分隔）。

        Args:
            record: 已处理完毕（含优化结果）的 PromptRecord 实例。
            role: 目标角色名（须在 AGENTS_ROLES 中）。

        Returns:
            写入的文件绝对路径；若 role 无效或无可优化内容则返回 None。
        """
        if role not in AGENTS_ROLES:
            print(f"  警告: 角色 '{role}' 不在已知角色列表 {AGENTS_ROLES} 中，跳过回写")
            return None

        if record.optimization is None or not record.optimization.optimized_text:
            print(f"  跳过: 记录 {record.id} 无优化内容")
            return None

        target_dir = AGENTS_PROMPTS_DIR / role
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "system-prompt.md"

        # 已有文件则追加，否则新建
        existing = ""
        if target_file.exists():
            existing = target_file.read_text(encoding="utf-8")

        # 避免重复写入相同内容
        if record.optimization.optimized_text.strip() in existing:
            print(f"  跳过: 记录 {record.id} 的优化内容已存在于 {target_file}")
            return str(target_file)

        section_header = "\n\n---\n\n## 萃取优化模式"
        grade_info = f"（评分: {record.quality.overall:.1f}, 等级: {record.quality.grade}）\n\n"
        new_section = (
            f"{section_header}\n"
            f"{grade_info}"
            f"{record.optimization.optimized_text.strip()}\n"
        )

        target_file.write_text(existing + new_section, encoding="utf-8")
        print(f"  已回写: 记录 {record.id} → {target_file}")
        return str(target_file)

    def writeback_batch(self, records: list[PromptRecord], role: str) -> list[str]:
        """批量回写优化后的提示词至指定角色目录。

        Args:
            records: 已处理完毕的 PromptRecord 列表。
            role: 目标角色名。

        Returns:
            已写入的文件绝对路径列表。
        """
        results: list[str] = []
        for record in records:
            path = self.writeback(record, role)
            if path:
                results.append(path)
        return results

    def export_results(self, records: list[PromptRecord], output_path: str) -> str:
        """将处理结果导出为 CSV 文件。

        将 PromptRecord 列表转换为 pandas DataFrame，
        列表和字典字段转为 JSON 字符串，以 UTF-8 BOM 编码保存，
        确保 Excel 兼容性。

        Args:
            records: PromptRecord 列表。
            output_path: 输出 CSV 文件路径。

        Returns:
            输出文件的绝对路径。
        """
        # 构建数据行
        rows: list[dict] = []
        for record in records:
            row = {
                "id": record.id,
                "original_text": record.original_text,
                "cleaned_text": record.cleaned_text,
                "instructions": json.dumps(record.features.instructions, ensure_ascii=False),
                "constraints": json.dumps(record.features.constraints, ensure_ascii=False),
                "expected_output": record.features.expected_output or "",
                "clarity": record.quality.clarity,
                "completeness": record.quality.completeness,
                "executability": record.quality.executability,
                "overall": record.quality.overall,
                "grade": record.quality.grade,
                "optimized_text": record.optimization.optimized_text,
                "improvements": json.dumps(record.optimization.improvements, ensure_ascii=False),
                "error": record.error or "",
            }
            rows.append(row)

        # 转换为 DataFrame 并保存
        df = pd.DataFrame(rows, columns=EXPORT_COLUMNS)
        df.to_csv(output_path, index=False, encoding="utf-8-sig")

        return output_path