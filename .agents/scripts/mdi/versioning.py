"""MDI 版本控制与变更管理工具。

提供结构化diff、变更影响分析、语义化版本检查能力。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from mdi.models import MDIDocument, Interface, Parameter, Response, ErrorCode
from mdi.parser import MDIParser

logger = logging.getLogger(__name__)


class ChangeType(str, Enum):
    """变更类型枚举。"""

    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


class ChangeSeverity(str, Enum):
    """变更严重性（用于语义化版本判定）。"""

    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    NONE = "none"


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
    """MDI文档结构化diff结果。"""

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

    def overall_severity(self) -> ChangeSeverity:
        """计算整体变更严重性。"""
        severities = [ChangeSeverity.NONE]

        for fc in self.frontmatter_changes:
            severities.append(fc.severity)

        for ic in self.interface_changes:
            severities.append(ic.severity)
            for pc in ic.parameter_changes:
                severities.append(pc.severity)
            for rc in ic.response_changes:
                severities.append(rc.severity)
            for ec in ic.error_changes:
                severities.append(ec.severity)

        if self.removed_interfaces:
            severities.append(ChangeSeverity.MAJOR)

        if ChangeSeverity.MAJOR in severities:
            return ChangeSeverity.MAJOR
        if self.added_interfaces or ChangeSeverity.MINOR in severities:
            return ChangeSeverity.MINOR
        if ChangeSeverity.PATCH in severities:
            return ChangeSeverity.PATCH
        return ChangeSeverity.NONE

    def suggest_version_bump(self, current_version: str | None = None) -> str:
        """基于变更严重性建议版本号升级。

        Args:
            current_version: 当前版本号（如"1.2.3"），如未提供使用文档中解析的版本。

        Returns:
            建议的新版本号字符串。
        """
        version = current_version or self.old_version or "0.1.0"
        parts = version.split(".")
        while len(parts) < 3:
            parts.append("0")

        try:
            major = int(parts[0])
            minor = int(parts[1])
            patch = int(parts[2])
        except ValueError:
            major, minor, patch = 0, 1, 0

        severity = self.overall_severity()

        if severity == ChangeSeverity.MAJOR:
            return f"{major + 1}.0.0"
        elif severity == ChangeSeverity.MINOR:
            return f"{major}.{minor + 1}.0"
        elif severity == ChangeSeverity.PATCH:
            return f"{major}.{minor}.{patch + 1}"
        else:
            return version

    def impact_analysis(self) -> dict[str, list[str]]:
        """变更影响分析，列出受影响的下游产物。

        Returns:
            字典：key为受影响产物类型，value为具体影响描述列表。
        """
        impacts: dict[str, list[str]] = {
            "python_types": [],
            "typescript_types": [],
            "openapi_spec": [],
            "mcp_schema": [],
            "pytest_tests": [],
            "jest_tests": [],
            "cli_skeleton": [],
            "markdown_docs": [],
        }

        severity = self.overall_severity()

        if self.frontmatter_changes:
            for fc in self.frontmatter_changes:
                if fc.key in ("name", "version", "title"):
                    impacts["markdown_docs"].append(f"文档元数据变更: {fc.key}")
                if fc.key == "version":
                    impacts["python_types"].append("包版本号需更新")
                    impacts["typescript_types"].append("包版本号需更新")

        for iface in self.removed_interfaces:
            impacts["python_types"].append(f"删除接口 {iface.method} {iface.path}：类型定义需移除（破坏性变更）")
            impacts["typescript_types"].append(f"删除接口 {iface.method} {iface.path}：类型定义需移除（破坏性变更）")
            impacts["openapi_spec"].append(f"删除路径 {iface.path}：OpenAPI paths需移除（破坏性变更）")
            impacts["mcp_schema"].append(f"删除工具 {iface.name}：MCP tools需移除（破坏性变更）")
            impacts["pytest_tests"].append(f"删除接口 {iface.method} {iface.path}：相关测试需移除（破坏性变更）")
            impacts["jest_tests"].append(f"删除接口 {iface.method} {iface.path}：相关测试需移除（破坏性变更）")
            impacts["cli_skeleton"].append(f"删除命令 {iface.name}：Click命令需移除（破坏性变更）")
            impacts["markdown_docs"].append(f"删除接口 {iface.method} {iface.path}：文档章节需移除（破坏性变更）")

        for iface in self.added_interfaces:
            impacts["python_types"].append(f"新增接口 {iface.method} {iface.path}：需添加TypedDict类型")
            impacts["typescript_types"].append(f"新增接口 {iface.method} {iface.path}：需添加interface类型")
            impacts["openapi_spec"].append(f"新增路径 {iface.path}：需添加OpenAPI path定义")
            impacts["mcp_schema"].append(f"新增工具 {iface.name}：需添加MCP tool定义")
            impacts["pytest_tests"].append(f"新增接口 {iface.method} {iface.path}：需添加测试用例")
            impacts["jest_tests"].append(f"新增接口 {iface.method} {iface.path}：需添加测试用例")
            impacts["cli_skeleton"].append(f"新增命令 {iface.name}：需添加Click命令")
            impacts["markdown_docs"].append(f"新增接口 {iface.method} {iface.path}：需添加文档章节")

        for ic in self.interface_changes:
            iface_id = f"{ic.method} {ic.path}"
            for fc in ic.field_changes:
                if fc.field == "summary" or fc.field == "description":
                    impacts["markdown_docs"].append(f"{iface_id} 描述变更：文档需更新")
                    impacts["openapi_spec"].append(f"{iface_id} 描述变更：OpenAPI info需更新")
                    impacts["mcp_schema"].append(f"{iface_id} 描述变更：MCP description需更新")

            for pc in ic.parameter_changes:
                param_id = f"{pc.location}参数 {pc.name}" if pc.location else f"参数 {pc.name}"
                if pc.change_type == ChangeType.REMOVED:
                    impacts["python_types"].append(f"{iface_id} 删除{param_id}：类型定义需移除（破坏性变更）")
                    impacts["typescript_types"].append(f"{iface_id} 删除{param_id}：类型定义需移除（破坏性变更）")
                    impacts["openapi_spec"].append(f"{iface_id} 删除{param_id}：parameters/schema需移除")
                    impacts["pytest_tests"].append(f"{iface_id} 删除{param_id}：测试用例需更新")
                    impacts["jest_tests"].append(f"{iface_id} 删除{param_id}：测试用例需更新")
                elif pc.change_type == ChangeType.ADDED:
                    impacts["python_types"].append(f"{iface_id} 新增{param_id}：需添加类型字段")
                    impacts["typescript_types"].append(f"{iface_id} 新增{param_id}：需添加类型字段")
                    impacts["openapi_spec"].append(f"{iface_id} 新增{param_id}：需添加参数定义")
                    impacts["pytest_tests"].append(f"{iface_id} 新增{param_id}：需补充测试用例")
                    impacts["jest_tests"].append(f"{iface_id} 新增{param_id}：需补充测试用例")
                elif pc.change_type == ChangeType.MODIFIED:
                    for ffc in pc.field_changes:
                        if ffc.field == "type":
                            impacts["python_types"].append(f"{iface_id} {param_id}类型变更: {ffc.old_value}→{ffc.new_value}（可能破坏性）")
                            impacts["typescript_types"].append(f"{iface_id} {param_id}类型变更: {ffc.old_value}→{ffc.new_value}（可能破坏性）")
                            impacts["openapi_spec"].append(f"{iface_id} {param_id}类型变更：schema需更新")
                            impacts["pytest_tests"].append(f"{iface_id} {param_id}类型变更：Mock数据和断言需更新")
                            impacts["jest_tests"].append(f"{iface_id} {param_id}类型变更：Mock数据和断言需更新")
                        elif ffc.field == "required":
                            impacts["python_types"].append(f"{iface_id} {param_id}必填性变更：类型Optional需调整")
                            impacts["typescript_types"].append(f"{iface_id} {param_id}必填性变更：类型可选性需调整")
                            impacts["openapi_spec"].append(f"{iface_id} {param_id}required字段需更新")
                            impacts["pytest_tests"].append(f"{iface_id} {param_id}必填性变更：测试参数需调整")
                            impacts["jest_tests"].append(f"{iface_id} {param_id}必填性变更：测试参数需调整")

            for rc in ic.response_changes:
                resp_id = f"响应 {rc.status_code}"
                if rc.change_type == ChangeType.REMOVED:
                    impacts["python_types"].append(f"{iface_id} 删除{resp_id}：响应类型需移除（破坏性变更）")
                    impacts["typescript_types"].append(f"{iface_id} 删除{resp_id}：响应类型需移除（破坏性变更）")
                    impacts["openapi_spec"].append(f"{iface_id} 删除{resp_id}：responses需移除")
                elif rc.change_type == ChangeType.ADDED:
                    impacts["python_types"].append(f"{iface_id} 新增{resp_id}：需添加响应类型")
                    impacts["typescript_types"].append(f"{iface_id} 新增{resp_id}：需添加响应类型")
                    impacts["openapi_spec"].append(f"{iface_id} 新增{resp_id}：需添加响应定义")
                elif rc.change_type == ChangeType.MODIFIED:
                    impacts["openapi_spec"].append(f"{iface_id} {resp_id} schema变更：需更新")

            for ec in ic.error_changes:
                err_id = f"错误码 {ec.code}"
                if ec.change_type == ChangeType.ADDED:
                    impacts["markdown_docs"].append(f"{iface_id} 新增{err_id}：错误码表需更新")
                    impacts["pytest_tests"].append(f"{iface_id} 新增{err_id}：需补充错误场景测试")
                    impacts["jest_tests"].append(f"{iface_id} 新增{err_id}：需补充错误场景测试")

        for key in list(impacts.keys()):
            if not impacts[key]:
                del impacts[key]

        if severity == ChangeSeverity.MAJOR:
            logger.warning("检测到MAJOR级别变更（破坏性变更），请检查所有下游产物兼容性")
        elif severity == ChangeSeverity.MINOR:
            logger.info("检测到MINOR级别变更（向后兼容功能新增）")
        elif severity == ChangeSeverity.PATCH:
            logger.info("检测到PATCH级别变更（向后兼容问题修复）")

        return impacts

    def to_dict(self) -> dict[str, Any]:
        """转换为可序列化字典。"""
        return {
            "old_path": str(self.old_path) if self.old_path else None,
            "new_path": str(self.new_path) if self.new_path else None,
            "old_version": self.old_version,
            "new_version": self.new_version,
            "overall_severity": self.overall_severity().value,
            "suggested_version": self.suggest_version_bump(),
            "has_changes": self.has_changes,
            "frontmatter_changes": [
                {
                    "change_type": fc.change_type.value,
                    "key": fc.key,
                    "old_value": fc.old_value,
                    "new_value": fc.new_value,
                    "severity": fc.severity.value,
                }
                for fc in self.frontmatter_changes
            ],
            "added_interfaces": [
                {"method": i.method, "path": i.path, "name": i.name, "summary": i.summary}
                for i in self.added_interfaces
            ],
            "removed_interfaces": [
                {"method": i.method, "path": i.path, "name": i.name, "summary": i.summary}
                for i in self.removed_interfaces
            ],
            "interface_changes": [
                {
                    "change_type": ic.change_type.value,
                    "method": ic.method,
                    "path": ic.path,
                    "severity": ic.severity.value,
                    "field_changes": [
                        {"field": fc.field, "old": fc.old_value, "new": fc.new_value}
                        for fc in ic.field_changes
                    ],
                    "parameter_changes": [
                        {
                            "change_type": pc.change_type.value,
                            "name": pc.name,
                            "location": pc.location,
                            "severity": pc.severity.value,
                        }
                        for pc in ic.parameter_changes
                    ],
                    "response_changes": [
                        {
                            "change_type": rc.change_type.value,
                            "status_code": rc.status_code,
                            "severity": rc.severity.value,
                        }
                        for rc in ic.response_changes
                    ],
                    "error_changes": [
                        {
                            "change_type": ec.change_type.value,
                            "code": ec.code,
                            "severity": ec.severity.value,
                        }
                        for ec in ic.error_changes
                    ],
                }
                for ic in self.interface_changes
            ],
            "warnings": self.warnings,
            "impact_analysis": self.impact_analysis(),
        }

    def format_text(self, verbose: bool = False) -> str:
        """格式化为可读文本报告。"""
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("MDI 结构化变更分析报告")
        lines.append("=" * 60)
        lines.append(f"旧版本: {self.old_version or '(未指定)'}")
        lines.append(f"新版本: {self.new_version or '(未指定)'}")
        severity = self.overall_severity()
        lines.append(f"整体严重性: {severity.value.upper()}")
        lines.append(f"建议版本升级: {self.old_version} → {self.suggest_version_bump()}")
        lines.append("")

        if self.frontmatter_changes:
            lines.append("── Frontmatter 变更 ──")
            for fc in self.frontmatter_changes:
                symbol = {"added": "+", "removed": "-", "modified": "~"}[fc.change_type.value]
                lines.append(f"  {symbol} {fc.key}: {fc.old_value!r} → {fc.new_value!r} [{fc.severity.value}]")
            lines.append("")

        if self.added_interfaces:
            lines.append(f"── 新增接口 ({len(self.added_interfaces)}) ──")
            for iface in self.added_interfaces:
                lines.append(f"  + {iface.method} {iface.path}  ({iface.summary})")
            lines.append("")

        if self.removed_interfaces:
            lines.append(f"── 删除接口 ({len(self.removed_interfaces)}) ──")
            for iface in self.removed_interfaces:
                lines.append(f"  - {iface.method} {iface.path}  ({iface.summary}) [MAJOR]")
            lines.append("")

        if self.interface_changes:
            lines.append(f"── 修改接口 ({len(self.interface_changes)}) ──")
            for ic in self.interface_changes:
                lines.append(f"  ~ {ic.method} {ic.path} [{ic.severity.value}]")
                if verbose:
                    for fc in ic.field_changes:
                        lines.append(f"      · {fc.field}: {fc.old_value!r} → {fc.new_value!r}")
                    for pc in ic.parameter_changes:
                        symbol = {"added": "+", "removed": "-", "modified": "~"}[pc.change_type.value]
                        lines.append(f"      {symbol} {pc.location}参数 {pc.name} [{pc.severity.value}]")
                    for rc in ic.response_changes:
                        symbol = {"added": "+", "removed": "-", "modified": "~"}[rc.change_type.value]
                        lines.append(f"      {symbol} 响应 {rc.status_code} [{rc.severity.value}]")
                    for ec in ic.error_changes:
                        symbol = {"added": "+", "removed": "-", "modified": "~"}[ec.change_type.value]
                        lines.append(f"      {symbol} 错误码 {ec.code} [{ec.severity.value}]")
            lines.append("")

        impacts = self.impact_analysis()
        if impacts:
            lines.append("── 变更影响分析 ──")
            for product, details in impacts.items():
                lines.append(f"  [{product}]")
                for d in details:
                    lines.append(f"    · {d}")
            lines.append("")

        if self.warnings:
            lines.append("── 警告 ──")
            for w in self.warnings:
                lines.append(f"  ⚠️  {w}")
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)


def _diff_value(a: Any, b: Any) -> bool:
    """比较两个值是否不同。"""
    if isinstance(a, str) and isinstance(b, str):
        return a.strip() != b.strip()
    return a != b


def _compare_parameters(
    old_params: list[Parameter],
    new_params: list[Parameter],
) -> list[ParameterChange]:
    """比较两个参数列表，返回变更列表。"""
    changes: list[ParameterChange] = []
    old_map = {(p.name, p.location): p for p in old_params}
    new_map = {(p.name, p.location): p for p in new_params}

    for key, new_p in new_map.items():
        if key not in old_map:
            severity = ChangeSeverity.MAJOR if new_p.required else ChangeSeverity.MINOR
            changes.append(ParameterChange(
                change_type=ChangeType.ADDED,
                name=new_p.name,
                location=new_p.location,
                new_param=new_p,
                severity=severity,
            ))
            logger.debug("参数新增: %s %s (required=%s, severity=%s)", new_p.location, new_p.name, new_p.required, severity.value)
        else:
            old_p = old_map[key]
            field_changes: list[FieldChange] = []

            if _diff_value(old_p.type, new_p.type):
                field_changes.append(FieldChange(
                    field="type",
                    old_value=old_p.type,
                    new_value=new_p.type,
                    severity=ChangeSeverity.MAJOR,
                ))
            if old_p.required != new_p.required:
                severity = ChangeSeverity.MAJOR if new_p.required else ChangeSeverity.MINOR
                field_changes.append(FieldChange(
                    field="required",
                    old_value=old_p.required,
                    new_value=new_p.required,
                    severity=severity,
                ))
            if _diff_value(old_p.description, new_p.description):
                field_changes.append(FieldChange(
                    field="description",
                    old_value=old_p.description,
                    new_value=new_p.description,
                    severity=ChangeSeverity.PATCH,
                ))
            if _diff_value(old_p.default, new_p.default):
                field_changes.append(FieldChange(
                    field="default",
                    old_value=old_p.default,
                    new_value=new_p.default,
                    severity=ChangeSeverity.MINOR,
                ))

            if field_changes:
                param_severity = max((fc.severity for fc in field_changes), key=lambda s: s.value)
                changes.append(ParameterChange(
                    change_type=ChangeType.MODIFIED,
                    name=new_p.name,
                    location=new_p.location,
                    old_param=old_p,
                    new_param=new_p,
                    field_changes=field_changes,
                    severity=param_severity,
                ))
                logger.debug("参数修改: %s %s, %d个字段变更", new_p.location, new_p.name, len(field_changes))

    for key, old_p in old_map.items():
        if key not in new_map:
            changes.append(ParameterChange(
                change_type=ChangeType.REMOVED,
                name=old_p.name,
                location=old_p.location,
                old_param=old_p,
                severity=ChangeSeverity.MAJOR,
            ))
            logger.debug("参数删除: %s %s", old_p.location, old_p.name)

    return changes


def _compare_responses(
    old_resps: list[Response],
    new_resps: list[Response],
) -> list[ResponseChange]:
    """比较两个响应列表。"""
    changes: list[ResponseChange] = []
    old_map = {str(r.status_code): r for r in old_resps}
    new_map = {str(r.status_code): r for r in new_resps}

    for code, new_r in new_map.items():
        if code not in old_map:
            changes.append(ResponseChange(
                change_type=ChangeType.ADDED,
                status_code=new_r.status_code,
                new_response=new_r,
                severity=ChangeSeverity.MINOR,
            ))
        else:
            old_r = old_map[code]
            field_changes: list[FieldChange] = []
            if _diff_value(old_r.description, new_r.description):
                field_changes.append(FieldChange("description", old_r.description, new_r.description, ChangeSeverity.PATCH))
            if field_changes:
                changes.append(ResponseChange(
                    change_type=ChangeType.MODIFIED,
                    status_code=new_r.status_code,
                    old_response=old_r,
                    new_response=new_r,
                    field_changes=field_changes,
                    severity=ChangeSeverity.PATCH,
                ))

    for code, old_r in old_map.items():
        if code not in new_map:
            changes.append(ResponseChange(
                change_type=ChangeType.REMOVED,
                status_code=old_r.status_code,
                old_response=old_r,
                severity=ChangeSeverity.MAJOR,
            ))

    return changes


def _compare_errors(
    old_errs: list[ErrorCode],
    new_errs: list[ErrorCode],
) -> list[ErrorChange]:
    """比较两个错误码列表。"""
    changes: list[ErrorChange] = []
    old_map = {str(e.code): e for e in old_errs}
    new_map = {str(e.code): e for e in new_errs}

    for code, new_e in new_map.items():
        if code not in old_map:
            changes.append(ErrorChange(
                change_type=ChangeType.ADDED,
                code=new_e.code,
                new_error=new_e,
                severity=ChangeSeverity.MINOR,
            ))
        else:
            old_e = old_map[code]
            field_changes: list[FieldChange] = []
            if _diff_value(old_e.message, new_e.message):
                field_changes.append(FieldChange("message", old_e.message, new_e.message, ChangeSeverity.PATCH))
            if _diff_value(old_e.description, new_e.description):
                field_changes.append(FieldChange("description", old_e.description, new_e.description, ChangeSeverity.PATCH))
            if field_changes:
                changes.append(ErrorChange(
                    change_type=ChangeType.MODIFIED,
                    code=new_e.code,
                    old_error=old_e,
                    new_error=new_e,
                    field_changes=field_changes,
                    severity=ChangeSeverity.PATCH,
                ))

    for code, old_e in old_map.items():
        if code not in new_map:
            changes.append(ErrorChange(
                change_type=ChangeType.REMOVED,
                code=old_e.code,
                old_error=old_e,
                severity=ChangeSeverity.MAJOR,
            ))

    return changes


def diff_documents(old_doc: MDIDocument, new_doc: MDIDocument) -> DiffResult:
    """对比两个MDIDocument，生成结构化diff结果。

    Args:
        old_doc: 旧版本MDI文档。
        new_doc: 新版本MDI文档。

    Returns:
        DiffResult结构化diff结果。
    """
    logger.info("开始对比MDI文档: %s vs %s", old_doc.source_path, new_doc.source_path)

    result = DiffResult(
        old_path=old_doc.source_path,
        new_path=new_doc.source_path,
        old_version=str(old_doc.frontmatter.get("version", "")),
        new_version=str(new_doc.frontmatter.get("version", "")),
    )

    old_fm = old_doc.frontmatter or {}
    new_fm = new_doc.frontmatter or {}
    all_keys = set(old_fm.keys()) | set(new_fm.keys())

    for key in sorted(all_keys):
        old_val = old_fm.get(key)
        new_val = new_fm.get(key)
        if key not in old_fm:
            result.frontmatter_changes.append(FrontmatterChange(
                change_type=ChangeType.ADDED,
                key=key,
                new_value=new_val,
                severity=ChangeSeverity.PATCH,
            ))
        elif key not in new_fm:
            result.frontmatter_changes.append(FrontmatterChange(
                change_type=ChangeType.REMOVED,
                key=key,
                old_value=old_val,
                severity=ChangeSeverity.MAJOR if key in ("name",) else ChangeSeverity.MINOR,
            ))
        elif _diff_value(old_val, new_val):
            severity = ChangeSeverity.PATCH
            result.frontmatter_changes.append(FrontmatterChange(
                change_type=ChangeType.MODIFIED,
                key=key,
                old_value=old_val,
                new_value=new_val,
                severity=severity,
            ))

    old_iface_map = {(i.method, i.path): i for i in old_doc.interfaces}
    new_iface_map = {(i.method, i.path): i for i in new_doc.interfaces}

    for key, new_iface in new_iface_map.items():
        if key not in old_iface_map:
            result.added_interfaces.append(new_iface)
            logger.debug("接口新增: %s %s", new_iface.method, new_iface.path)
        else:
            old_iface = old_iface_map[key]
            field_changes: list[FieldChange] = []

            if _diff_value(old_iface.name, new_iface.name):
                field_changes.append(FieldChange("name", old_iface.name, new_iface.name, ChangeSeverity.MAJOR))
            if _diff_value(old_iface.summary, new_iface.summary):
                field_changes.append(FieldChange("summary", old_iface.summary, new_iface.summary, ChangeSeverity.PATCH))
            if _diff_value(old_iface.description, new_iface.description):
                field_changes.append(FieldChange("description", old_iface.description, new_iface.description, ChangeSeverity.PATCH))

            param_changes = _compare_parameters(old_iface.parameters, new_iface.parameters)
            resp_changes = _compare_responses(old_iface.responses, new_iface.responses)
            err_changes = _compare_errors(old_iface.errors, new_iface.errors)

            if field_changes or param_changes or resp_changes or err_changes:
                all_sub_severities = (
                    [fc.severity for fc in field_changes]
                    + [pc.severity for pc in param_changes]
                    + [rc.severity for rc in resp_changes]
                    + [ec.severity for ec in err_changes]
                )
                iface_severity = max(all_sub_severities, key=lambda s: s.value) if all_sub_severities else ChangeSeverity.PATCH
                result.interface_changes.append(InterfaceChange(
                    change_type=ChangeType.MODIFIED,
                    method=new_iface.method,
                    path=new_iface.path,
                    old_interface=old_iface,
                    new_interface=new_iface,
                    field_changes=field_changes,
                    parameter_changes=param_changes,
                    response_changes=resp_changes,
                    error_changes=err_changes,
                    severity=iface_severity,
                ))
                logger.debug(
                    "接口修改: %s %s, %d字段 %d参数 %d响应 %d错误变更",
                    new_iface.method, new_iface.path,
                    len(field_changes), len(param_changes), len(resp_changes), len(err_changes),
                )

    for key, old_iface in old_iface_map.items():
        if key not in new_iface_map:
            result.removed_interfaces.append(old_iface)
            logger.debug("接口删除: %s %s", old_iface.method, old_iface.path)

    logger.info(
        "对比完成: %d frontmatter变更, %d新增接口, %d删除接口, %d修改接口",
        len(result.frontmatter_changes),
        len(result.added_interfaces),
        len(result.removed_interfaces),
        len(result.interface_changes),
    )

    return result


def diff_files(old_path: str | Path, new_path: str | Path) -> DiffResult:
    """对比两个MDI文件。

    Args:
        old_path: 旧版本MDI文件路径。
        new_path: 新版本MDI文件路径。

    Returns:
        DiffResult结构化diff结果。
    """
    parser = MDIParser()
    old_doc = parser.parse_file(Path(old_path))
    new_doc = parser.parse_file(Path(new_path))
    return diff_documents(old_doc, new_doc)


def diff_strings(old_content: str, new_content: str, source_name: str = "<string>") -> DiffResult:
    """对比两个MDI内容字符串。

    Args:
        old_content: 旧版本MDI内容。
        new_content: 新版本MDI内容。
        source_name: 源名称标识，用于错误定位。

    Returns:
        DiffResult结构化diff结果。
    """
    parser = MDIParser()
    old_doc = parser.parse_text(old_content, source=source_name)
    new_doc = parser.parse_text(new_content, source=source_name)
    return diff_documents(old_doc, new_doc)


VERSIONING_BEST_PRACTICES = """\
# MDI 版本控制最佳实践

## 语义化版本规范

MDI 文档遵循语义化版本（SemVer）：`MAJOR.MINOR.PATCH`

- **MAJOR**：破坏性变更
  - 删除接口
  - 删除参数
  - 参数类型变更（不兼容）
  - 必填参数新增
  - 响应状态码删除

- **MINOR**：向后兼容功能新增
  - 新增接口
  - 新增可选参数
  - 新增响应状态码
  - 新增错误码

- **PATCH**：向后兼容问题修复
  - 描述文本修正
  - 示例更新
  - 错别字修复
  - 文档格式调整

## Changelog 自动生成建议

使用 `mdi diff` 命令自动生成变更日志：

```bash
python -m mdi diff old.md new.md --format markdown > CHANGELOG.md
```

## Commit Message 规范

遵循 Conventional Commits：

- `feat(api):` 新增接口 → MINOR 版本
- `fix(api):` 修复问题 → PATCH 版本
- `refactor(api)!:` 破坏性重构 → MAJOR 版本
- `docs:` 文档更新 → PATCH 版本

## 推荐工作流

1. 修改 MDI 文档前，先确认当前版本号
2. 修改完成后运行 `mdi diff` 检查变更影响
3. 根据建议的版本号更新 frontmatter 中的 `version` 字段
4. 重新生成所有下游代码（类型、测试、OpenAPI等）
5. 运行测试确保无回归
6. Commit 并更新 CHANGELOG
"""


def get_version_bump_recommendation(diff_result: DiffResult) -> dict[str, Any]:
    """获取版本升级建议详情。

    Args:
        diff_result: diff结果对象。

    Returns:
        包含建议详情的字典。
    """
    severity = diff_result.overall_severity()
    current = diff_result.old_version or "0.1.0"
    suggested = diff_result.suggest_version_bump()

    reasons: list[str] = []
    if diff_result.removed_interfaces:
        reasons.append(f"删除了 {len(diff_result.removed_interfaces)} 个接口（破坏性变更）")

    major_param_changes = 0
    for ic in diff_result.interface_changes:
        for pc in ic.parameter_changes:
            if pc.severity == ChangeSeverity.MAJOR:
                major_param_changes += 1
        for rc in ic.response_changes:
            if rc.severity == ChangeSeverity.MAJOR:
                major_param_changes += 1
    if major_param_changes:
        reasons.append(f"{major_param_changes} 个参数/响应发生破坏性变更")

    if diff_result.added_interfaces:
        reasons.append(f"新增了 {len(diff_result.added_interfaces)} 个接口（功能新增）")

    if severity == ChangeSeverity.PATCH:
        reasons.append("仅描述/文档等非功能性变更")

    return {
        "current_version": current,
        "suggested_version": suggested,
        "bump_type": severity.value,
        "reasons": reasons,
        "has_breaking_changes": severity == ChangeSeverity.MAJOR,
        "should_regenerate": True,
        "should_run_tests": True,
    }
