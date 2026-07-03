"""结构化Diff计算引擎。

负责对比两个MDIDocument，生成DiffResult数据对象。
仅包含diff比较逻辑，不包含版本规则和影响分析。
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from mdi.models import MDIDocument, Interface, Parameter, Response, ErrorCode
from mdi.parser import MDIParser

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

logger = logging.getLogger(__name__)


def _diff_value(a: Any, b: Any) -> bool:
    """比较两个值是否不同（字符串忽略前后空白）。"""
    if isinstance(a, str) and isinstance(b, str):
        return a.strip() != b.strip()
    return a != b


def _compare_parameters(
    old_params: list[Parameter],
    new_params: list[Parameter],
) -> list[ParameterChange]:
    """比较两个参数列表，返回变更列表。

    严重性规则：
    - 新增必填参数：MAJOR（破坏性）
    - 新增可选参数：MINOR
    - 删除参数：MAJOR（破坏性）
    - 参数类型变更：MAJOR（破坏性）
    - required从false变true：MAJOR（破坏性）
    - required从true变false：MINOR
    - 默认值变更：MINOR
    - 描述变更：PATCH
    """
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
                param_severity = max((fc.severity for fc in field_changes))
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
        DiffResult结构化diff结果（纯数据对象，需配合semver_rules/impact_analyzer使用）。
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
                iface_severity = max(all_sub_severities) if all_sub_severities else ChangeSeverity.PATCH
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
