# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

from .constants import (
    FRONTMATTER_REQUIRED_FIELDS,
    FRONTMATTER_RECOMMENDED_FIELDS,
    ID_PATTERN,
)
from .maturity import CANONICAL_LEVELS, normalize_maturity
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

    maturity_raw = fields.get("maturity", "")
    norm = normalize_maturity(maturity_raw)
    if norm.status == "empty":
        # 缺失已由 FRONTMATTER_REQUIRED_FIELDS 报 error，此处不重复扣分
        pass
    elif norm.status == "level":
        results.append(CheckResult(
            name="frontmatter.maturity合法性",
            passed=True,
            severity="info",
            message=f"成熟度'{norm.raw}'合法（归一为基础等级 {norm.base}）"
        ))
    else:
        reason = "为历史描述性词" if norm.status == "alias" else "不在等级阶梯内"
        results.append(CheckResult(
            name="frontmatter.maturity合法性",
            passed=False,
            severity="warn",
            message=f"成熟度'{norm.raw}'{reason}，建议改用 {'/'.join(CANONICAL_LEVELS)} 之一"
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

    results.extend(_check_maturity_consistency(norm.base, fields))
    return results


def _check_maturity_consistency(base, fields):
    """按归一后的基础等级校验 verification/reuse 计数一致性。

    L1.5（同谱系双案例）与 L2（≥2 独立案例）同用 validation_count≥2 口径。
    """
    if base is None:
        return []

    try:
        vc = int(str(fields.get("validation_count"))) if fields.get("validation_count") else 0
    except (ValueError, TypeError):
        return []
    try:
        rc = int(str(fields.get("reuse_count"))) if fields.get("reuse_count") else 0
    except (ValueError, TypeError):
        return []

    name = "frontmatter.maturity_validation_consistency"
    if base == "L1":
        ok, msg = vc >= 1, f"L1成熟度与验证次数一致（validation_count={vc}）"
        fail = "L1模式应至少有1次验证（validation_count≥1）"
    elif base in ("L1.5", "L2"):
        ok, msg = vc >= 2, f"{base}成熟度与验证次数一致（validation_count={vc}）"
        fail = f"{base}模式应至少有2次验证（validation_count≥2）"
    elif base == "L3":
        ok, msg = rc >= 1, f"L3成熟度与复用次数一致（reuse_count={rc}）"
        fail = "L3模式应至少被复用1次（reuse_count≥1）"
    elif base == "L4":
        ok, msg = (vc >= 5 and rc >= 3), f"L4成熟度与验证/复用次数一致（validation_count={vc}, reuse_count={rc}）"
        fail = "L4模式应至少有5次验证且被复用3次（validation_count≥5, reuse_count≥3）"
    else:
        return []

    return [CheckResult(
        name=name,
        passed=ok,
        severity="info" if ok else "warn",
        message=msg if ok else fail
    )]
