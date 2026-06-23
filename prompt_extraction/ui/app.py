"""提示词萃取系统 —— Streamlit 可视化主应用

提供文件上传和手动输入两种输入方式，
串联流水线处理，展示处理结果与质量评分。
"""

import os
import tempfile
from collections import Counter

import pandas as pd
import streamlit as st

from prompt_extraction.config import QUALITY_THRESHOLD
from prompt_extraction.models import PromptRecord
from prompt_extraction.pipeline import Pipeline
from prompt_extraction.ui.components.diff_viewer import render_diff_viewer
from prompt_extraction.ui.components.export_button import render_export_buttons
from prompt_extraction.ui.components.radar_chart import render_radar_chart
from prompt_extraction.ui.components.score_card import render_score_card

# ── 页面配置 ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="提示词萃取系统",
    page_icon="🔍",
    layout="wide",
)

# ── 页面标题 ──────────────────────────────────────────────────────────────
st.title("🔍 提示词萃取系统")
st.markdown("对提示词文本进行清洗、特征提取、质量评估与优化，提升提示词工程效率。")

# ── 初始化 Pipeline ───────────────────────────────────────────────────────
if "pipeline" not in st.session_state:
    st.session_state.pipeline = Pipeline()

# ── 侧边栏：输入方式选择 ──────────────────────────────────────────────────
with st.sidebar:
    st.header("输入配置")
    input_mode = st.radio(
        "选择输入方式",
        options=["文件上传", "手动输入"],
        index=0,
        label_visibility="collapsed",
    )

    uploaded_file = None
    manual_text = ""

    if input_mode == "文件上传":
        st.subheader("📁 文件上传")
        uploaded_file = st.file_uploader(
            "上传提示词文件",
            type=["csv", "json", "txt", "md"],
            help="支持 CSV、JSON、TXT、Markdown 格式",
        )
        if uploaded_file is not None:
            st.success(f"已上传：{uploaded_file.name}")
            st.caption(f"文件大小：{uploaded_file.size / 1024:.1f} KB")
    else:
        st.subheader("✏️ 手动输入")
        manual_text = st.text_area(
            "请输入提示词文本",
            height=200,
            placeholder="在此粘贴或输入提示词文本...",
        )

    # 处理按钮
    process_disabled = False
    if input_mode == "文件上传" and uploaded_file is None:
        process_disabled = True
    elif input_mode == "手动输入" and not manual_text.strip():
        process_disabled = True

    st.button(
        "🚀 开始萃取",
        type="primary",
        use_container_width=True,
        disabled=process_disabled,
        key="process_button",
    )

# ── 处理逻辑 ──────────────────────────────────────────────────────────────
if st.session_state.get("process_button"):
    pipeline = st.session_state.pipeline

    with st.spinner("正在处理提示词，请稍候..."):
        if input_mode == "文件上传" and uploaded_file is not None:
            # 将上传文件保存到临时目录，再调用 run_batch
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(uploaded_file.name)[1],
            ) as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_path = tmp_file.name

            try:
                records = pipeline.run_batch(tmp_path)
                st.session_state.results = records
            finally:
                # 清理临时文件
                os.unlink(tmp_path)
        else:
            # 手动输入单条处理
            record = pipeline.run_single(manual_text.strip())
            records = [record]
            st.session_state.results = records

    st.success("处理完成！")

# ── 结果展示 ──────────────────────────────────────────────────────────────
if "results" in st.session_state and st.session_state.results:
    records: list[PromptRecord] = st.session_state.results

    # 筛选有效记录（无错误的记录）
    valid_records = [r for r in records if not r.error]
    error_records = [r for r in records if r.error]

    st.divider()
    st.header("📊 处理结果")

    # ── 批量处理：统计摘要 ─────────────────────────────────────────────
    if len(records) > 1:
        st.subheader("统计摘要")
        col_total, col_avg, col_errors = st.columns(3)
        with col_total:
            st.metric("总数量", len(records))
        with col_avg:
            if valid_records:
                avg_score = sum(r.quality.overall for r in valid_records) / len(valid_records)
                st.metric("平均评分", f"{avg_score:.1f}")
            else:
                st.metric("平均评分", "N/A")
        with col_errors:
            st.metric("错误数量", len(error_records))

        # 各等级数量统计
        if valid_records:
            grade_counts = Counter(r.quality.grade for r in valid_records)
            st.markdown("**各等级分布：**")
            grade_cols = st.columns(4)
            grade_order = ["优", "良", "中", "差"]
            grade_colors = {"优": "green", "良": "blue", "中": "orange", "差": "red"}
            for i, grade in enumerate(grade_order):
                with grade_cols[i]:
                    count = grade_counts.get(grade, 0)
                    st.metric(
                        label=grade,
                        value=count,
                        delta=None,
                    )

    # ── 结果列表表格 ──────────────────────────────────────────────────
    st.subheader("结果列表")

    # 构建表格数据
    table_data: list[dict] = []
    for record in records:
        # 原始文本摘要（截取前 80 个字符）
        text_summary = record.original_text.replace("\n", " ").strip()
        if len(text_summary) > 80:
            text_summary = text_summary[:80] + "..."

        table_data.append({
            "ID": record.id,
            "原始文本摘要": text_summary,
            "综合评分": record.quality.overall if not record.error else None,
            "等级": record.quality.grade if not record.error else "错误",
            "状态": "错误" if record.error else "正常",
        })

    df = pd.DataFrame(table_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.TextColumn("ID", width="small"),
            "原始文本摘要": st.column_config.TextColumn("原始文本摘要", width="large"),
            "综合评分": st.column_config.NumberColumn("综合评分", format="%.1f"),
            "等级": st.column_config.TextColumn("等级", width="small"),
            "状态": st.column_config.TextColumn("状态", width="small"),
        },
    )

    # ── 展开详情 ──────────────────────────────────────────────────────
    st.subheader("记录详情")
    for i, record in enumerate(records):
        expander_label = f"#{record.id} — 综合评分：{record.quality.overall:.1f} ({record.quality.grade})"
        if record.error:
            expander_label = f"#{record.id} — ⚠️ 处理异常"

        with st.expander(expander_label, expanded=(len(records) == 1)):
            if record.error:
                st.error(f"处理过程中发生错误：{record.error}")
                st.markdown("**原始文本：**")
                st.text(record.original_text)
                continue

            # 原始文本
            st.markdown("### 原始文本")
            st.text_area(
                label=f"原始文本-{i}",
                value=record.original_text,
                height=150,
                disabled=True,
                key=f"orig_{i}",
                label_visibility="collapsed",
            )

            # 清洗后文本
            st.markdown("### 清洗后文本")
            st.text_area(
                label=f"清洗后文本-{i}",
                value=record.cleaned_text,
                height=150,
                disabled=True,
                key=f"clean_{i}",
                label_visibility="collapsed",
            )

            # 提取特征
            st.markdown("### 提取特征")
            features = record.features
            if features.instructions:
                st.markdown("**指令：**")
                for instr in features.instructions:
                    st.markdown(f"- {instr}")
            if features.constraints:
                st.markdown("**约束：**")
                for constraint in features.constraints:
                    if isinstance(constraint, dict):
                        for k, v in constraint.items():
                            st.markdown(f"- **{k}**：{v}")
                    else:
                        st.markdown(f"- {constraint}")
            if features.expected_output:
                st.markdown(f"**期望输出格式：**{features.expected_output}")
            if features.output_type:
                st.markdown(f"**输出类型：**{features.output_type}")

            # 质量评分
            st.markdown("### 质量评分")
            col_score, col_radar = st.columns([1, 1])
            with col_score:
                render_score_card(record.quality)
            with col_radar:
                st.plotly_chart(
                    render_radar_chart(record.quality),
                    use_container_width=True,
                )

            # 优化对比
            if record.quality.overall < QUALITY_THRESHOLD:
                st.markdown("### 优化对比")
                render_diff_viewer(
                    original=record.original_text,
                    optimized=record.optimization.optimized_text,
                    improvements=record.optimization.improvements,
                )

    # ── 导出按钮 ──────────────────────────────────────────────────────
    st.divider()
    st.subheader("📥 导出结果")
    render_export_buttons(records)
elif "results" in st.session_state and not st.session_state.results:
    st.info("请通过侧边栏上传文件或输入文本，然后点击「开始萃取」按钮。")

# ── 页脚 ──────────────────────────────────────────────────────────────────
st.divider()
st.caption("提示词萃取系统 · 基于 Streamlit 构建")