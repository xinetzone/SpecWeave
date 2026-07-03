from pathlib import Path

from .constants import (
    FRONTMATTER_REQUIRED_FIELDS,
    FRONTMATTER_RECOMMENDED_FIELDS,
    VALID_MATURITY_LEVELS,
    ID_PATTERN,
)
from .models import CheckResult


def check_frontmatter(pattern_md, content, fields):
    results = []

    if not fields:
        results.append(CheckResult(
            name="frontmatter存在",
            passed=False,
            severity="error",
            message="缺少frontmatter（元数据块）"
        ))
        return results

    results.append(CheckResult(
        name="frontmatter存在",
        passed=True,
        severity="error",
        message="frontmatter存在"
    ))

    pattern_id = fields.get("id", "")
    if pattern_id:
        pattern_id = str(pattern_id)
        id_valid = bool(ID_PATTERN.match(pattern_id))
        results.append(CheckResult(
            name="frontmatter.id格式",
            passed=id_valid,
            severity="warn",
            message=f"id格式正确（{pattern_id}）" if id_valid
            else f"id格式建议为'pattern-xxx'格式，当前为'{pattern_id}'"
        ))
    else:
        results.append(CheckResult(
            name="frontmatter.id格式",
            passed=False,
            severity="error",
            message="缺少id字段"
        ))

    for fname in FRONTMATTER_REQUIRED_FIELDS - {"id"}:
        value = fields.get(fname)
        passed = value is not None and len(str(value).strip()) > 0
        results.append(CheckResult(
            name=f"frontmatter.{fname}",
            passed=passed,
            severity="error",
            message=f"必需字段 '{fname}' {'存在' if passed else '缺失'}"
        ))

    maturity = fields.get("maturity", "")
    if maturity:
        maturity = str(maturity)
        maturity_valid = maturity in VALID_MATURITY_LEVELS
        results.append(CheckResult(
            name="frontmatter.maturity合法性",
            passed=maturity_valid,
            severity="error" if not maturity_valid else "info",
            message=f"成熟度等级'{maturity}'合法" if maturity_valid
            else f"成熟度等级'{maturity}'不合法，应为L1/L2/L3/L4之一"
        ))

    for fname in FRONTMATTER_RECOMMENDED_FIELDS:
        value = fields.get(fname)
        passed = value is not None
        if not passed:
            results.append(CheckResult(
                name=f"frontmatter.{fname}",
                passed=False,
                severity="warn",
                message=f"建议字段 '{fname}' 缺失（用于成熟度追踪）"
            ))
        else:
            results.append(CheckResult(
                name=f"frontmatter.{fname}",
                passed=True,
                severity="warn",
                message=f"建议字段 '{fname}' 存在（值: {value}）"
            ))

    validation_count = fields.get("validation_count")
    reuse_count = fields.get("reuse_count")
    maturity = fields.get("maturity", "")
    if maturity:
        maturity = str(maturity)
    if maturity == "L1":
        try:
            vc = int(str(validation_count)) if validation_count else 0
            if vc < 1:
                results.append(CheckResult(
                    name="frontmatter.maturity_validation_consistency",
                    passed=False,
                    severity="warn",
                    message="L1模式应至少有1次验证（validation_count≥1）"
                ))
            else:
                results.append(CheckResult(
                    name="frontmatter.maturity_validation_consistency",
                    passed=True,
                    severity="info",
                    message=f"L1成熟度与验证次数一致（validation_count={vc}）"
                ))
        except (ValueError, TypeError):
            pass
    elif maturity == "L2":
        try:
            vc = int(str(validation_count)) if validation_count else 0
            if vc < 2:
                results.append(CheckResult(
                    name="frontmatter.maturity_validation_consistency",
                    passed=False,
                    severity="warn",
                    message="L2模式应至少有2次验证（validation_count≥2）"
                ))
            else:
                results.append(CheckResult(
                    name="frontmatter.maturity_validation_consistency",
                    passed=True,
                    severity="info",
                    message=f"L2成熟度与验证次数一致（validation_count={vc}）"
                ))
        except (ValueError, TypeError):
            pass
    elif maturity == "L3":
        try:
            rc = int(str(reuse_count)) if reuse_count else 0
            if rc < 1:
                results.append(CheckResult(
                    name="frontmatter.maturity_validation_consistency",
                    passed=False,
                    severity="warn",
                    message="L3模式应至少被复用1次（reuse_count≥1）"
                ))
            else:
                results.append(CheckResult(
                    name="frontmatter.maturity_validation_consistency",
                    passed=True,
                    severity="info",
                    message=f"L3成熟度与复用次数一致（reuse_count={rc}）"
                ))
        except (ValueError, TypeError):
            pass
    elif maturity == "L4":
        try:
            vc = int(str(validation_count)) if validation_count else 0
            rc = int(str(reuse_count)) if reuse_count else 0
            if vc < 5 or rc < 3:
                results.append(CheckResult(
                    name="frontmatter.maturity_validation_consistency",
                    passed=False,
                    severity="warn",
                    message="L4模式应至少有5次验证且被复用3次（validation_count≥5, reuse_count≥3）"
                ))
            else:
                results.append(CheckResult(
                    name="frontmatter.maturity_validation_consistency",
                    passed=True,
                    severity="info",
                    message=f"L4成熟度与验证/复用次数一致（validation_count={vc}, reuse_count={rc}）"
                ))
        except (ValueError, TypeError):
            pass

    return results
