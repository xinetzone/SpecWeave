from typing import Optional

from lib.frontmatter import extract_yaml_field

from .constants import (
    MIN_DESCRIPTION_LENGTH,
    RECOMMENDED_DESCRIPTION_LENGTH,
    MANDATORY_TRIGGER_PHRASES,
)
from .models import CheckResult


def check_description(frontmatter_text: str | None) -> list[CheckResult]:
    results = []

    if not frontmatter_text:
        return results

    desc = extract_yaml_field(frontmatter_text, "description")
    if not desc:
        return results

    desc_len = len(desc)

    results.append(CheckResult(
        name="description.length",
        passed=desc_len >= MIN_DESCRIPTION_LENGTH,
        severity="warn" if desc_len >= MIN_DESCRIPTION_LENGTH else "error",
        message=f"Description长度{desc_len}字符" + (
            "（建议≥150字符以包含足够触发词）" if desc_len < RECOMMENDED_DESCRIPTION_LENGTH else ""
        )
    ))

    has_mandatory = any(phrase in desc for phrase in MANDATORY_TRIGGER_PHRASES)
    results.append(CheckResult(
        name="description.mandatory_phrase",
        passed=has_mandatory,
        severity="warn",
        message="Description包含强制触发措辞（'必须使用此技能'等）" if has_mandatory
        else "Description缺少强制触发措辞（建议添加'必须使用此技能'等，避免undertrigger）"
    ))

    has_trigger_context = any(kw in desc for kw in ["当用户", "when", "触发", "提到"])
    results.append(CheckResult(
        name="description.trigger_context",
        passed=has_trigger_context,
        severity="warn",
        message="Description包含触发场景说明" if has_trigger_context
        else "Description缺少触发场景说明（建议说明'当用户提到XX时'触发）"
    ))

    return results
