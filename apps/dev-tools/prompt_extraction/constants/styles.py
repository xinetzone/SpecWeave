"""提示词萃取系统 —— CSS 样式与颜色常量

集中管理 UI 组件中的 CSS 样式、颜色值、字体大小等视觉常量，
便于统一主题调整与后续主题切换功能实现。
"""

# ============================================================================
# 评分卡片 CSS 样式（score_card.py）
# ============================================================================

# 等级标签样式模板
GRADE_LABEL_STYLE = (
    "font-size:14px;color:rgba(49,51,63,0.6);margin-bottom:4px;"
)

# 等级数值样式模板（颜色由 grade_color 动态填充）
GRADE_VALUE_STYLE = (
    "font-size:32px;font-weight:700;color:{color};margin:0;"
)

# 等级容器样式
GRADE_CONTAINER_STYLE = "text-align:center;"

# ============================================================================
# 雷达图颜色与样式（radar_chart.py）
# ============================================================================

RADAR_LINE_COLOR = "#1f77b4"
RADAR_LINE_WIDTH = 2
RADAR_FILL_COLOR = "rgba(31, 119, 180, 0.25)"
RADAR_GRID_COLOR = "rgba(0,0,0,0.1)"
RADAR_TICK_FONT_SIZE = 11
RADAR_ANGULAR_TICK_FONT_SIZE = 13
RADAR_RANGE_MIN = 0
RADAR_RANGE_MAX = 100
RADAR_HEIGHT = 380
RADAR_MARGIN = dict(l=40, r=40, t=40, b=40)
