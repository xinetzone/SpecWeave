import re
from pathlib import Path
from typing import Optional

from lib.frontmatter import extract_yaml_field

from .constants import (
    FRONTMATTER_REQUIRED_FIELDS,
    FRONTMATTER_RECOMMENDED_FIELDS,
    OPEN_STANDARD_ALLOWED_FIELDS,
    OPEN_STANDARD_MAX_NAME_LENGTH,
    OPEN_STANDARD_MAX_DESCRIPTION_LENGTH,
    OPEN_STANDARD_MIN_DESCRIPTION_LENGTH_FOR_STANDARD,
    OPEN_STANDARD_OPTIONAL_DIRS,
)
from .models import CheckResult


def _get_dir_purpose(dirname: str) -> str:
    purposes = {
        "scripts": "用于捆绑可执行脚本",
        "references": "用于详细参考文档，实现渐进式披露",
        "assets": "用于模板、静态资源等",
        "evals": "用于质量评估测试用例",
    }
    return purposes.get(dirname, "可选目录")


def check_open_standards_compliance(skill_md: Path, content: str, frontmatter_text: Optional[str]) -> list[CheckResult]:
    results = []
    skill_dir = skill_md.parent
    dir_name = skill_dir.name

    if not frontmatter_text:
        return results

    name = extract_yaml_field(frontmatter_text, "name")
    desc = extract_yaml_field(frontmatter_text, "description")

    if name:
        name_ok = True

        if len(name) > OPEN_STANDARD_MAX_NAME_LENGTH:
            results.append(CheckResult(
                name="open_standard.name.length",
                passed=False,
                severity="warn",
                message=f"name长度{len(name)}超过开放标准上限{OPEN_STANDARD_MAX_NAME_LENGTH}字符"
            ))
            name_ok = False
        else:
            results.append(CheckResult(
                name="open_standard.name.length",
                passed=True,
                severity="info",
                message=f"name长度{len(name)}字符（≤{OPEN_STANDARD_MAX_NAME_LENGTH}）"
            ))

        name_format_issues = []
        if name != name.lower():
            name_format_issues.append("包含大写字符（开放标准要求小写）")
        if name.startswith("-"):
            name_format_issues.append("以连字符开头")
        if name.endswith("-"):
            name_format_issues.append("以连字符结尾")
        if "--" in name:
            name_format_issues.append("包含连续连字符")
        if "_" in name:
            name_format_issues.append("包含下划线（建议使用连字符-）")
        invalid_chars = [c for c in name if not (c.isalnum() or c == "-")]
        if invalid_chars:
            name_format_issues.append(f"包含无效字符: {''.join(set(invalid_chars))}（仅允许字母、数字、连字符）")

        if name_format_issues:
            results.append(CheckResult(
                name="open_standard.name.format",
                passed=False,
                severity="warn",
                message=f"name格式不符合kebab-case规范：{'；'.join(name_format_issues)}"
            ))
            name_ok = False
        else:
            results.append(CheckResult(
                name="open_standard.name.format",
                passed=True,
                severity="info",
                message="name符合kebab-case小写连字符格式"
            ))

        if name != dir_name:
            results.append(CheckResult(
                name="open_standard.name.dir_match",
                passed=False,
                severity="warn",
                message=f"name应与父目录名一致（name: {name}，目录: {dir_name}）"
            ))
            name_ok = False
        else:
            results.append(CheckResult(
                name="open_standard.name.dir_match",
                passed=True,
                severity="info",
                message="name与目录名一致"
            ))

        if name_ok:
            results.append(CheckResult(
                name="open_standard.name.compliant",
                passed=True,
                severity="info",
                message="name字段完全符合开放标准"
            ))

    if desc:
        if len(desc) > OPEN_STANDARD_MAX_DESCRIPTION_LENGTH:
            results.append(CheckResult(
                name="open_standard.description.max_length",
                passed=False,
                severity="warn",
                message=f"description长度{len(desc)}超过开放标准硬限制{OPEN_STANDARD_MAX_DESCRIPTION_LENGTH}字符"
            ))
        else:
            results.append(CheckResult(
                name="open_standard.description.max_length",
                passed=True,
                severity="info",
                message=f"description长度{len(desc)}字符（≤{OPEN_STANDARD_MAX_DESCRIPTION_LENGTH}硬限制）"
            ))

        if len(desc) < OPEN_STANDARD_MIN_DESCRIPTION_LENGTH_FOR_STANDARD:
            results.append(CheckResult(
                name="open_standard.description.min_length",
                passed=False,
                severity="warn",
                message=f"description过短（{len(desc)}字符），开放标准建议≥{OPEN_STANDARD_MIN_DESCRIPTION_LENGTH_FOR_STANDARD}字符以明确功能和触发时机"
            ))
        else:
            results.append(CheckResult(
                name="open_standard.description.min_length",
                passed=True,
                severity="info",
                message="description长度满足基本要求"
            ))

        trigger_kws = ["when", "使用", "触发", "提到", "Use when", "必须使用"]
        has_trigger = any(kw in desc for kw in trigger_kws)
        results.append(CheckResult(
            name="open_standard.description.trigger_hint",
            passed=has_trigger,
            severity="info" if has_trigger else "info",
            message="description包含触发时机说明" if has_trigger
            else "description建议包含触发时机说明（如 'Use when...'、'当用户提到...'）"
        ))

    for opt_dir in OPEN_STANDARD_OPTIONAL_DIRS:
        dir_path = skill_dir / opt_dir
        exists = dir_path.is_dir()
        results.append(CheckResult(
            name=f"open_standard.structure.{opt_dir}",
            passed=True,
            severity="info",
            message=f"包含 {opt_dir}/ 目录" if exists
            else f"未发现 {opt_dir}/ 目录（可选，{_get_dir_purpose(opt_dir)}）"
        ))

    if frontmatter_text:
        present_fields = set()
        for line in frontmatter_text.split("\n"):
            stripped = line.strip()
            if ":" in stripped and not stripped.startswith("-") and not stripped.startswith("#"):
                key = stripped.split(":", 1)[0].strip()
                if key and not key.startswith("["):
                    present_fields.add(key)

        custom_fields = present_fields - OPEN_STANDARD_ALLOWED_FIELDS - FRONTMATTER_REQUIRED_FIELDS - FRONTMATTER_RECOMMENDED_FIELDS
        if custom_fields:
            results.append(CheckResult(
                name="open_standard.custom_fields",
                passed=True,
                severity="info",
                message=f"使用自定义扩展字段: {', '.join(sorted(custom_fields))}（兼容客户端会安全忽略，不影响跨客户端加载）"
            ))
        else:
            results.append(CheckResult(
                name="open_standard.custom_fields",
                passed=True,
                severity="info",
                message="仅使用标准+项目推荐字段，无额外自定义扩展"
            ))

    has_gotchas = bool(re.search(r"^##\s+\d+\.\s*Gotchas|^##\s+\d+\.\s*(陷阱|反直觉|Gotchas)", content, re.MULTILINE))
    results.append(CheckResult(
        name="open_standard.body.gotchas",
        passed=has_gotchas,
        severity="warn",
        message="包含Gotchas/陷阱与反直觉行为章节" if has_gotchas
        else '建议包含Gotchas章节，列出容易踩的坑和反直觉行为（与"常见错误处理"不同，记录无错误码的隐性陷阱）'
    ))

    name_checks = [r for r in results if r.name.startswith("open_standard.name.")]
    all_name_checks_pass = all(r.passed for r in name_checks if r.severity in ("error", "warn"))
    results.append(CheckResult(
        name="open_standard.compliance",
        passed=all_name_checks_pass,
        severity="info" if all_name_checks_pass else "warn",
        message="Agent Skills开放标准核心规范合规" if all_name_checks_pass
        else "存在开放标准规范警告，可能影响部分兼容客户端的正确解析（建议修复name格式）"
    ))

    return results
