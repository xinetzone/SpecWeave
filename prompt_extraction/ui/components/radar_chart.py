"""雷达图组件：展示提示词质量多维度评分"""

import plotly.graph_objects as go
import plotly.express as px

from prompt_extraction.constants import (
    RADAR_ANGULAR_TICK_FONT_SIZE,
    RADAR_CATEGORIES,
    RADAR_FILL_COLOR,
    RADAR_GRID_COLOR,
    RADAR_HEIGHT,
    RADAR_LINE_COLOR,
    RADAR_LINE_WIDTH,
    RADAR_MARGIN,
    RADAR_RANGE_MAX,
    RADAR_RANGE_MIN,
    RADAR_TICK_FONT_SIZE,
)
from prompt_extraction.messages import RADAR_CHART_NAME, RADAR_HOVER_TEMPLATE
from prompt_extraction.models import QualityScore


def render_radar_chart(quality: QualityScore) -> go.Figure:
    """使用 Plotly 绘制雷达图，展示清晰度、完整性、可执行性三个维度。

    Args:
        quality: 质量评分对象。

    Returns:
        Plotly Figure 对象，可在 Streamlit 中通过 st.plotly_chart 渲染。
    """
    # 维度名称与对应数值
    values = [quality.clarity, quality.completeness, quality.executability]

    # 闭合雷达图（首尾相连）
    categories_closed = RADAR_CATEGORIES + [RADAR_CATEGORIES[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill="toself",
            name=RADAR_CHART_NAME,
            line=dict(color=RADAR_LINE_COLOR, width=RADAR_LINE_WIDTH),
            fillcolor=RADAR_FILL_COLOR,
            hovertemplate=RADAR_HOVER_TEMPLATE,
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[RADAR_RANGE_MIN, RADAR_RANGE_MAX],
                tickfont=dict(size=RADAR_TICK_FONT_SIZE),
                gridcolor=RADAR_GRID_COLOR,
            ),
            angularaxis=dict(
                tickfont=dict(size=RADAR_ANGULAR_TICK_FONT_SIZE),
                gridcolor=RADAR_GRID_COLOR,
            ),
        ),
        showlegend=False,
        margin=RADAR_MARGIN,
        height=RADAR_HEIGHT,
    )

    return fig