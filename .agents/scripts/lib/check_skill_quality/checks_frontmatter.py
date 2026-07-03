from pathlib import Path
from typing import Optional

from lib.frontmatter import extract_yaml_field

from .constants import FRONTMATTER_REQUIRED_FIELDS, FRONTMATTER_RECOMMENDED_FIELDS
from .models import CheckResult


def check_frontmatter(skill_md: Path, content: str, frontmatter_text: Optional[str]) -> list[CheckResult]:
    results = []

    if not frontmatter_text:
        results.append(CheckResult(
            name="frontmatter存在",
            passed=False,
            severity="error",
            message="缺少YAML frontmatter（---分隔的元数据块）"
        ))
        return results

    results.append(CheckResult(
        name="frontmatter存在",
        passed=True,
        severity="error",
        message="YAML frontmatter存在"
    ))

    for fname in FRONTMATTER_REQUIRED_FIELDS:
        value = extract_yaml_field(frontmatter_text, fname)
        passed = value is not None and len(value.strip()) > 0
        results.append(CheckResult(
            name=f"frontmatter.{fname}",
            passed=passed,
            severity="error",
            message=f"必需字段 '{fname}' {'存在' if passed else '缺失'}"
        ))

    for fname in FRONTMATTER_RECOMMENDED_FIELDS:
        value = extract_yaml_field(frontmatter_text, fname)
        passed = value is not None
        if not passed:
            results.append(CheckResult(
                name=f"frontmatter.{fname}",
                passed=False,
                severity="warn",
                message=f"建议字段 '{fname}' 缺失（推荐添加以提高可用性）"
            ))
        else:
            results.append(CheckResult(
                name=f"frontmatter.{fname}",
                passed=True,
                severity="warn",
                message=f"建议字段 '{fname}' 存在"
            ))

    return results
