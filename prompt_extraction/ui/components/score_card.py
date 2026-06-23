"""评分卡片组件：展示提示词质量评分与等级"""

import streamlit as st

from prompt_extraction.constants import (
    GRADE_COLORS,
    GRADE_CONTAINER_STYLE,
    GRADE_DEFAULT_COLOR,
    GRADE_LABEL_STYLE,
    GRADE_VALUE_STYLE,
)
from prompt_extraction.messages import (
    CARD_CLARITY_LABEL,
    CARD_COMPLETENESS_LABEL,
    CARD_EXECUTABILITY_LABEL,
    CARD_GRADE_LABEL,
    CARD_OVERALL_LABEL,
    CARD_SUGGESTIONS,
)
from prompt_extraction.models import QualityScore


def render_score_card(quality: QualityScore) -> None:
    """使用 st.metric 展示综合评分、清晰度、完整性、可执行性与等级。

    根据等级使用不同颜色：优=绿色、良=蓝色、中=橙色、差=红色。

    Args:
        quality: 质量评分对象。
    """
    grade_color = GRADE_COLORS.get(quality.grade, GRADE_DEFAULT_COLOR)

    # 第一行：综合评分与等级
    col_overall, col_grade = st.columns(2)
    with col_overall:
        st.metric(
            label=CARD_OVERALL_LABEL,
            value=f"{quality.overall:.1f}",
            delta=None,
        )
    with col_grade:
        st.markdown(
            f"<div style='{GRADE_CONTAINER_STYLE}'>"
            f"<p style='{GRADE_LABEL_STYLE}'>{CARD_GRADE_LABEL}</p>"
            f"<p style='{GRADE_VALUE_STYLE.format(color=grade_color)}'>"
            f"{quality.grade}</p></div>",
            unsafe_allow_html=True,
        )

    # 第二行：三个维度评分
    col_clarity, col_completeness, col_exec = st.columns(3)
    with col_clarity:
        st.metric(label=CARD_CLARITY_LABEL, value=f"{quality.clarity:.1f}")
    with col_completeness:
        st.metric(label=CARD_COMPLETENESS_LABEL, value=f"{quality.completeness:.1f}")
    with col_exec:
        st.metric(label=CARD_EXECUTABILITY_LABEL, value=f"{quality.executability:.1f}")

    # 优化建议
    if quality.suggestions:
        st.markdown(CARD_SUGGESTIONS)
        for suggestion in quality.suggestions:
            st.markdown(f"- {suggestion}")