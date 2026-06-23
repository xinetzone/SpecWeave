"""雷达图组件：展示提示词质量多维度评分"""

import plotly.graph_objects as go
import plotly.express as px

from prompt_extraction.models import QualityScore


def render_radar_chart(quality: QualityScore) -> go.Figure:
    """使用 Plotly 绘制雷达图，展示清晰度、完整性、可执行性三个维度。

    Args:
        quality: 质量评分对象。

    Returns:
        Plotly Figure 对象，可在 Streamlit 中通过 st.plotly_chart 渲染。
    """
    # 维度名称与对应数值
    categories = ["清晰度", "完整性", "可执行性"]
    values = [quality.clarity, quality.completeness, quality.executability]

    # 闭合雷达图（首尾相连）
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill="toself",
            name="质量评分",
            line=dict(color="#1f77b4", width=2),
            fillcolor="rgba(31, 119, 180, 0.25)",
            hovertemplate="%{theta}: %{r:.1f} 分<extra></extra>",
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=11),
                gridcolor="rgba(0,0,0,0.1)",
            ),
            angularaxis=dict(
                tickfont=dict(size=13),
                gridcolor="rgba(0,0,0,0.1)",
            ),
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40),
        height=380,
    )

    return fig