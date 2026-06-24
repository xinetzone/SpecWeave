"""提示词萃取系统全局配置

所有常量定义已迁移至 prompt_extraction.constants 包，
本模块保留重导出以维持向后兼容。
"""

from prompt_extraction.constants import (
    QUALITY_THRESHOLD,
    CLARITY_WEIGHT,
    COMPLETENESS_WEIGHT,
    EXECUTABILITY_WEIGHT,
    GRADE_THRESHOLDS,
    DEFAULT_OUTPUT_DIR,
    AGENTS_DIR,
    AGENTS_PROMPTS_DIR,
    AGENTS_ROLES_DIR,
    AGENTS_ROLES,
)

