"""语义化版本（SemVer）规则引擎。

基于DiffResult计算变更严重性，生成版本号升级建议。
"""

from __future__ import annotations

import logging
from typing import Any

from .models import ChangeSeverity, DiffResult

logger = logging.getLogger(__name__)


def calculate_overall_severity(diff: DiffResult) -> ChangeSeverity:
    """计算整体变更严重性。

    规则优先级（按顺序判断，先匹配先返回）：
    - 删除接口/MAJOR级字段变更 → MAJOR（破坏性变更）
    - 新增接口/MINOR级字段变更 → MINOR（功能新增）
    - PATCH级字段变更 → PATCH（问题修复）
    - 无变更 → NONE
    """
    severities = [ChangeSeverity.NONE]

    for fc in diff.frontmatter_changes:
        severities.append(fc.severity)

    for ic in diff.interface_changes:
        severities.append(ic.severity)
        for pc in ic.parameter_changes:
            severities.append(pc.severity)
        for rc in ic.response_changes:
            severities.append(rc.severity)
        for ec in ic.error_changes:
            severities.append(ec.severity)

    if diff.removed_interfaces:
        severities.append(ChangeSeverity.MAJOR)

    if ChangeSeverity.MAJOR in severities:
        return ChangeSeverity.MAJOR
    if diff.added_interfaces or ChangeSeverity.MINOR in severities:
        return ChangeSeverity.MINOR
    if ChangeSeverity.PATCH in severities:
        return ChangeSeverity.PATCH
    return ChangeSeverity.NONE


def suggest_version_bump(diff: DiffResult, current_version: str | None = None) -> str:
    """基于变更严重性建议版本号升级。

    Args:
        diff: DiffResult结构化diff结果。
        current_version: 当前版本号（如"1.2.3"），如未提供使用文档中解析的版本。

    Returns:
        建议的新版本号字符串。

    Examples:
        MAJOR变更：1.2.3 → 2.0.0
        MINOR变更：1.2.3 → 1.3.0
        PATCH变更：1.2.3 → 1.2.4
        无变更：  1.2.3 → 1.2.3
    """
    version = current_version or diff.old_version or "0.1.0"
    parts = version.split(".")
    while len(parts) < 3:
        parts.append("0")

    try:
        major = int(parts[0])
        minor = int(parts[1])
        patch = int(parts[2])
    except ValueError:
        major, minor, patch = 0, 1, 0

    severity = calculate_overall_severity(diff)

    if severity == ChangeSeverity.MAJOR:
        return f"{major + 1}.0.0"
    elif severity == ChangeSeverity.MINOR:
        return f"{major}.{minor + 1}.0"
    elif severity == ChangeSeverity.PATCH:
        return f"{major}.{minor}.{patch + 1}"
    else:
        return version


def get_version_bump_recommendation(diff: DiffResult) -> dict[str, Any]:
    """获取版本升级建议详情（包含原因说明）。

    Args:
        diff: DiffResult结构化diff结果。

    Returns:
        包含建议详情的字典：
        - current_version: 当前版本
        - suggested_version: 建议版本
        - bump_type: 升级类型（major/minor/patch/none）
        - reasons: 升级原因列表
        - has_breaking_changes: 是否包含破坏性变更
        - should_regenerate: 是否需要重新生成下游代码
        - should_run_tests: 是否需要运行测试
    """
    severity = calculate_overall_severity(diff)
    current = diff.old_version or "0.1.0"
    suggested = suggest_version_bump(diff)

    reasons: list[str] = []
    if diff.removed_interfaces:
        reasons.append(f"删除了 {len(diff.removed_interfaces)} 个接口（破坏性变更）")

    major_param_changes = 0
    for ic in diff.interface_changes:
        for pc in ic.parameter_changes:
            if pc.severity == ChangeSeverity.MAJOR:
                major_param_changes += 1
        for rc in ic.response_changes:
            if rc.severity == ChangeSeverity.MAJOR:
                major_param_changes += 1
    if major_param_changes:
        reasons.append(f"{major_param_changes} 个参数/响应发生破坏性变更")

    if diff.added_interfaces:
        reasons.append(f"新增了 {len(diff.added_interfaces)} 个接口（功能新增）")

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


def log_severity_summary(diff: DiffResult) -> None:
    """记录变更严重性日志摘要。"""
    severity = calculate_overall_severity(diff)
    if severity == ChangeSeverity.MAJOR:
        logger.warning("检测到MAJOR级别变更（破坏性变更），请检查所有下游产物兼容性")
    elif severity == ChangeSeverity.MINOR:
        logger.info("检测到MINOR级别变更（向后兼容功能新增）")
    elif severity == ChangeSeverity.PATCH:
        logger.info("检测到PATCH级别变更（向后兼容问题修复）")
