"""导出按钮组件：提供 CSV 和 TXT 格式的结果导出功能"""

import os
from datetime import datetime

import streamlit as st

from prompt_extraction.config import DEFAULT_OUTPUT_DIR
from prompt_extraction.models import PromptRecord
from prompt_extraction.pipeline import Pipeline


def render_export_buttons(records: list[PromptRecord]) -> None:
    """提供两个导出按钮：导出完整结果 CSV 和仅导出优化后提示词 TXT。

    Args:
        records: 处理完成的 PromptRecord 列表。
    """
    if not records:
        st.info("暂无处理结果可供导出。")
        return

    col_csv, col_txt = st.columns(2)

    # 确保输出目录存在
    os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

    # 创建 Pipeline 实例用于导出
    pipeline = Pipeline()

    with col_csv:
        csv_path = os.path.join(
            DEFAULT_OUTPUT_DIR,
            f"prompt_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        )
        pipeline.export_results(records, csv_path)
        with open(csv_path, "rb") as f:
            st.download_button(
                label="导出完整结果 (CSV)",
                data=f,
                file_name=os.path.basename(csv_path),
                mime="text/csv",
                use_container_width=True,
            )

    with col_txt:
        # 仅导出优化后的提示词文本，每条一行
        optimized_lines: list[str] = []
        for record in records:
            text = record.optimization.optimized_text or record.cleaned_text or record.original_text
            # 移除换行，合并为单行
            text = text.replace("\n", " ").replace("\r", " ").strip()
            if text:
                optimized_lines.append(text)

        if optimized_lines:
            txt_content = "\n".join(optimized_lines)
            txt_path = os.path.join(
                DEFAULT_OUTPUT_DIR,
                f"optimized_prompts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            )
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(txt_content)
            with open(txt_path, "rb") as f:
                st.download_button(
                    label="导出优化后提示词 (TXT)",
                    data=f,
                    file_name=os.path.basename(txt_path),
                    mime="text/plain",
                    use_container_width=True,
                )
        else:
            st.info("无可导出的优化后提示词。")