"""提示词萃取系统全局配置"""

# 质量评估
QUALITY_THRESHOLD = 60  # 触发优化阈值（0-100）
CLARITY_WEIGHT = 0.30
COMPLETENESS_WEIGHT = 0.40
EXECUTABILITY_WEIGHT = 0.30

# 等级映射
GRADE_THRESHOLDS = {
    "优": 85,
    "良": 70,
    "中": 50,
    "差": 0,
}

# 输出
DEFAULT_OUTPUT_DIR = "output"