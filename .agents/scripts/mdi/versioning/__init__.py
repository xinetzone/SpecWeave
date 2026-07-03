"""MDI 版本控制与变更管理工具。

提供结构化diff、变更影响分析、语义化版本检查能力。

拆分结构（遵循单一职责原则）：
- models: 数据模型定义（枚举、Change dataclass、DiffResult容器）
- diff_engine: 结构化diff计算引擎
- semver_rules: SemVer严重性判定与版本升级建议
- impact_analyzer: 影响分析与报告格式化

向后兼容：所有公共API均可直接从 `mdi.versioning` 导入，无需修改现有代码。
"""

from .models import (
    ChangeType,
    ChangeSeverity,
    FieldChange,
    ParameterChange,
    ResponseChange,
    ErrorChange,
    InterfaceChange,
    FrontmatterChange,
    DiffResult,
)
from .diff_engine import (
    diff_documents,
    diff_files,
    diff_strings,
    _diff_value,
    _compare_parameters,
    _compare_responses,
    _compare_errors,
)
from .semver_rules import (
    calculate_overall_severity,
    suggest_version_bump,
    get_version_bump_recommendation,
    VERSIONING_BEST_PRACTICES,
    log_severity_summary,
)
from .impact_analyzer import (
    analyze_impact,
    to_dict,
    format_text,
)

__all__ = [
    "ChangeType",
    "ChangeSeverity",
    "FieldChange",
    "ParameterChange",
    "ResponseChange",
    "ErrorChange",
    "InterfaceChange",
    "FrontmatterChange",
    "DiffResult",
    "diff_documents",
    "diff_files",
    "diff_strings",
    "calculate_overall_severity",
    "suggest_version_bump",
    "get_version_bump_recommendation",
    "VERSIONING_BEST_PRACTICES",
    "log_severity_summary",
    "analyze_impact",
    "to_dict",
    "format_text",
]
