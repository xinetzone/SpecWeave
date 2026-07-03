"""MDI版本控制数据模型。

包含所有变更相关的数据结构定义，纯数据容器，不含业务逻辑。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from mdi.models import MDIDocument, Interface, Parameter, Response, ErrorCode


class ChangeType(str, Enum):
    """变更类型枚举。"""

    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


class ChangeSeverity(str, Enum):
    """变更严重性（用于语义化版本判定）。

    严重性排序：MAJOR > MINOR > PATCH > NONE
    """

    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    NONE = "none"

    @property
    def _order(self) -> int:
        return {"major": 3, "minor": 2, "patch": 1, "none": 0}[self.value]

    def __lt__(self, other: "ChangeSeverity") -> bool:
        if not isinstance(other, ChangeSeverity):
            return NotImplemented
        return self._order < other._order

    def __gt__(self, other: "ChangeSeverity") -> bool:
        if not isinstance(other, ChangeSeverity):
            return NotImplemented
        return self._order > other._order


@dataclass
class FieldChange:
    """字段级变更。"""

    field: str
    old_value: Any
    new_value: Any
    severity: ChangeSeverity = ChangeSeverity.PATCH


@dataclass
class ParameterChange:
    """参数变更。"""

    change_type: ChangeType
    name: str
    location: str = ""
    old_param: Parameter | None = None
    new_param: Parameter | None = None
    field_changes: list[FieldChange] = field(default_factory=list)
    severity: ChangeSeverity = ChangeSeverity.PATCH


@dataclass
class ResponseChange:
    """响应变更。"""

    change_type: ChangeType
    status_code: str | int
    old_response: Response | None = None
    new_response: Response | None = None
    field_changes: list[FieldChange] = field(default_factory=list)
    severity: ChangeSeverity = ChangeSeverity.PATCH


@dataclass
class ErrorChange:
    """错误码变更。"""

    change_type: ChangeType
    code: str | int
    old_error: ErrorCode | None = None
    new_error: ErrorCode | None = None
    field_changes: list[FieldChange] = field(default_factory=list)
    severity: ChangeSeverity = ChangeSeverity.MINOR


@dataclass
class InterfaceChange:
    """接口变更。"""

    change_type: ChangeType
    method: str
    path: str
    old_interface: Interface | None = None
    new_interface: Interface | None = None
    field_changes: list[FieldChange] = field(default_factory=list)
    parameter_changes: list[ParameterChange] = field(default_factory=list)
    response_changes: list[ResponseChange] = field(default_factory=list)
    error_changes: list[ErrorChange] = field(default_factory=list)
    severity: ChangeSeverity = ChangeSeverity.PATCH


@dataclass
class FrontmatterChange:
    """Frontmatter变更。"""

    change_type: ChangeType
    key: str
    old_value: Any = None
    new_value: Any = None
    severity: ChangeSeverity = ChangeSeverity.PATCH


@dataclass
class DiffResult:
    """MDI文档结构化diff结果（纯数据容器）。

    业务逻辑方法（overall_severity/suggest_version_bump/impact_analysis/to_dict/format_text）
    已移至对应模块的独立函数，保持单一职责。
    """

    old_path: Path | None
    new_path: Path | None
    old_version: str
    new_version: str
    frontmatter_changes: list[FrontmatterChange] = field(default_factory=list)
    interface_changes: list[InterfaceChange] = field(default_factory=list)
    added_interfaces: list[Interface] = field(default_factory=list)
    removed_interfaces: list[Interface] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        """是否有任何变更。"""
        return bool(
            self.frontmatter_changes
            or self.interface_changes
            or self.added_interfaces
            or self.removed_interfaces
        )

    def overall_severity(self) -> "ChangeSeverity":
        """计算整体变更严重性（向后兼容方法，委托给semver_rules.calculate_overall_severity）。"""
        from .semver_rules import calculate_overall_severity
        return calculate_overall_severity(self)

    def suggest_version_bump(self, current_version: str | None = None) -> str:
        """基于变更严重性建议版本号升级（向后兼容方法，委托给semver_rules.suggest_version_bump）。"""
        from .semver_rules import suggest_version_bump
        return suggest_version_bump(self, current_version)

    def impact_analysis(self) -> dict[str, list[str]]:
        """变更影响分析（向后兼容方法，委托给impact_analyzer.analyze_impact）。"""
        from .impact_analyzer import analyze_impact
        return analyze_impact(self)

    def to_dict(self) -> dict[str, Any]:
        """转换为可序列化字典（向后兼容方法，委托给impact_analyzer.to_dict）。"""
        from .impact_analyzer import to_dict
        return to_dict(self)

    def format_text(self, verbose: bool = False) -> str:
        """格式化为可读文本报告（向后兼容方法，委托给impact_analyzer.format_text）。"""
        from .impact_analyzer import format_text
        return format_text(self, verbose)
