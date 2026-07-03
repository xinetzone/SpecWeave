"""变更影响分析与报告格式化。

分析变更对下游产物的影响，提供字典序列化和文本格式化输出。
"""

from __future__ import annotations

import logging
from typing import Any

from .models import ChangeType, DiffResult
from .semver_rules import calculate_overall_severity

logger = logging.getLogger(__name__)


def analyze_impact(diff: DiffResult) -> dict[str, list[str]]:
    """变更影响分析，列出受影响的下游产物。

    Args:
        diff: DiffResult结构化diff结果。

    Returns:
        字典：key为受影响产物类型，value为具体影响描述列表。
        产物类型包括：python_types/typescript_types/openapi_spec/mcp_schema/pytest_tests/jest_tests/cli_skeleton/markdown_docs
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

    if diff.frontmatter_changes:
        for fc in diff.frontmatter_changes:
            if fc.key in ("name", "version", "title"):
                impacts["markdown_docs"].append(f"文档元数据变更: {fc.key}")
            if fc.key == "version":
                impacts["python_types"].append("包版本号需更新")
                impacts["typescript_types"].append("包版本号需更新")

    for iface in diff.removed_interfaces:
        impacts["python_types"].append(f"删除接口 {iface.method} {iface.path}：类型定义需移除（破坏性变更）")
        impacts["typescript_types"].append(f"删除接口 {iface.method} {iface.path}：类型定义需移除（破坏性变更）")
        impacts["openapi_spec"].append(f"删除路径 {iface.path}：OpenAPI paths需移除（破坏性变更）")
        impacts["mcp_schema"].append(f"删除工具 {iface.name}：MCP tools需移除（破坏性变更）")
        impacts["pytest_tests"].append(f"删除接口 {iface.method} {iface.path}：相关测试需移除（破坏性变更）")
        impacts["jest_tests"].append(f"删除接口 {iface.method} {iface.path}：相关测试需移除（破坏性变更）")
        impacts["cli_skeleton"].append(f"删除命令 {iface.name}：Click命令需移除（破坏性变更）")
        impacts["markdown_docs"].append(f"删除接口 {iface.method} {iface.path}：文档章节需移除（破坏性变更）")

    for iface in diff.added_interfaces:
        impacts["python_types"].append(f"新增接口 {iface.method} {iface.path}：需添加TypedDict类型")
        impacts["typescript_types"].append(f"新增接口 {iface.method} {iface.path}：需添加interface类型")
        impacts["openapi_spec"].append(f"新增路径 {iface.path}：需添加OpenAPI path定义")
        impacts["mcp_schema"].append(f"新增工具 {iface.name}：需添加MCP tool定义")
        impacts["pytest_tests"].append(f"新增接口 {iface.method} {iface.path}：需添加测试用例")
        impacts["jest_tests"].append(f"新增接口 {iface.method} {iface.path}：需添加测试用例")
        impacts["cli_skeleton"].append(f"新增命令 {iface.name}：需添加Click命令")
        impacts["markdown_docs"].append(f"新增接口 {iface.method} {iface.path}：需添加文档章节")

    for ic in diff.interface_changes:
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

    return impacts


def to_dict(diff: DiffResult) -> dict[str, Any]:
    """将DiffResult转换为可序列化字典（包含计算后的派生字段）。"""
    from .semver_rules import suggest_version_bump, get_version_bump_recommendation

    return {
        "old_path": str(diff.old_path) if diff.old_path else None,
        "new_path": str(diff.new_path) if diff.new_path else None,
        "old_version": diff.old_version,
        "new_version": diff.new_version,
        "overall_severity": calculate_overall_severity(diff).value,
        "suggested_version": suggest_version_bump(diff),
        "has_changes": diff.has_changes,
        "version_recommendation": get_version_bump_recommendation(diff),
        "frontmatter_changes": [
            {
                "change_type": fc.change_type.value,
                "key": fc.key,
                "old_value": fc.old_value,
                "new_value": fc.new_value,
                "severity": fc.severity.value,
            }
            for fc in diff.frontmatter_changes
        ],
        "added_interfaces": [
            {"method": i.method, "path": i.path, "name": i.name, "summary": i.summary}
            for i in diff.added_interfaces
        ],
        "removed_interfaces": [
            {"method": i.method, "path": i.path, "name": i.name, "summary": i.summary}
            for i in diff.removed_interfaces
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
            for ic in diff.interface_changes
        ],
        "warnings": diff.warnings,
        "impact_analysis": analyze_impact(diff),
    }


def format_text(diff: DiffResult, verbose: bool = False) -> str:
    """将DiffResult格式化为可读文本报告。

    Args:
        diff: DiffResult结构化diff结果。
        verbose: 是否显示详细字段变更（默认False，仅显示摘要）。
    """
    from .semver_rules import suggest_version_bump

    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("MDI 结构化变更分析报告")
    lines.append("=" * 60)
    lines.append(f"旧版本: {diff.old_version or '(未指定)'}")
    lines.append(f"新版本: {diff.new_version or '(未指定)'}")
    severity = calculate_overall_severity(diff)
    lines.append(f"整体严重性: {severity.value.upper()}")
    lines.append(f"建议版本升级: {diff.old_version} → {suggest_version_bump(diff)}")
    lines.append("")

    if diff.frontmatter_changes:
        lines.append("── Frontmatter 变更 ──")
        for fc in diff.frontmatter_changes:
            symbol = {"added": "+", "removed": "-", "modified": "~"}[fc.change_type.value]
            lines.append(f"  {symbol} {fc.key}: {fc.old_value!r} → {fc.new_value!r} [{fc.severity.value}]")
        lines.append("")

    if diff.added_interfaces:
        lines.append(f"── 新增接口 ({len(diff.added_interfaces)}) ──")
        for iface in diff.added_interfaces:
            lines.append(f"  + {iface.method} {iface.path}  ({iface.summary})")
        lines.append("")

    if diff.removed_interfaces:
        lines.append(f"── 删除接口 ({len(diff.removed_interfaces)}) ──")
        for iface in diff.removed_interfaces:
            lines.append(f"  - {iface.method} {iface.path}  ({iface.summary}) [MAJOR]")
        lines.append("")

    if diff.interface_changes:
        lines.append(f"── 修改接口 ({len(diff.interface_changes)}) ──")
        for ic in diff.interface_changes:
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

    impacts = analyze_impact(diff)
    if impacts:
        lines.append("── 变更影响分析 ──")
        for product, details in impacts.items():
            lines.append(f"  [{product}]")
            for d in details:
                lines.append(f"    · {d}")
        lines.append("")

    if diff.warnings:
        lines.append("── 警告 ──")
        for w in diff.warnings:
            lines.append(f"  ⚠️  {w}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)
