"""评分卡片组件：展示提示词质量评分与等级"""

import streamlit as st

from prompt_extraction.models import QualityScore

# 等级对应的颜色映射
_GRADE_COLORS = {
    "优": "#28a745",  # 绿色
    "良": "#007bff",  # 蓝色
    "中": "#fd7e14",  # 橙色
    "差": "#dc3545",  # 红色
}


def render_score_card(quality: QualityScore) -> None:
    """使用 st.metric 展示综合评分、清晰度、完整性、可执行性与等级。

    根据等级使用不同颜色：优=绿色、良=蓝色、中=橙色、差=红色。

    Args:
        quality: 质量评分对象。
    """
    grade_color = _GRADE_COLORS.get(quality.grade, "#6c757d")

    # 第一行：综合评分与等级
    col_overall, col_grade = st.columns(2)
    with col_overall:
        st.metric(
            label="综合评分",
            value=f"{quality.overall:.1f}",
            delta=None,
        )
    with col_grade:
        st.markdown(
            f"<div style='text-align:center;'>"
            f"<p style='font-size:14px;color:rgba(49,51,63,0.6);margin-bottom:4px;'>等级</p>"
            f"<p style='font-size:32px;font-weight:700;color:{grade_color};margin:0;'>"
            f"{quality.grade}</p></div>",
            unsafe_allow_html=True,
        )

    # 第二行：三个维度评分
    col_clarity, col_completeness, col_exec = st.columns(3)
    with col_clarity:
        st.metric(label="清晰度", value=f"{quality.clarity:.1f}")
    with col_completeness:
        st.metric(label="完整性", value=f"{quality.completeness:.1f}")
    with col_exec:
        st.metric(label="可执行性", value=f"{quality.executability:.1f}")

    # 优化建议
    if quality.suggestions:
        st.markdown("**优化建议：**")
        for suggestion in quality.suggestions:
            st.markdown(f"- {suggestion}")