from pathlib import Path

from .constants import (
    MAX_SKILL_LINES,
    WHY_EXPLANATION_PATTERN,
    WRITE_OPERATION_KEYWORDS,
    DRY_RUN_KEYWORDS,
    IDEMPOTENT_KEYWORDS,
    POST_VERIFY_PATTERN,
    CHECKLIST_VERIFY_PATTERN,
    SAFETY_CHECKLIST_PATTERN,
    CHECKLIST_ITEM_PATTERN,
    DECISION_TREE_PATTERNS,
)
from .models import CheckResult


def check_file_length(skill_md: Path, content: str) -> list[CheckResult]:
    lines = content.count("\n") + 1

    passed = lines <= MAX_SKILL_LINES
    return [
        CheckResult(
            name="file.length",
            passed=passed,
            severity="warn" if passed else "error",
            message=f"文件{lines}行"
            + (
                "（符合≤500行规范）"
                if passed
                else f"（超过{MAX_SKILL_LINES}行建议，考虑使用references/子文档进行渐进式披露）"
            ),
        )
    ]


def check_why_explanations(content: str) -> list[CheckResult]:
    results = []

    why_count = len(WHY_EXPLANATION_PATTERN.findall(content))
    has_why = why_count >= 2

    results.append(CheckResult(
        name="why.explanations",
        passed=has_why,
        severity="warn",
        message=f"包含{why_count}个Why设计意图解释" + ("（建议关键决策都有Why解释）" if why_count < 5 else "")
    ))

    must_count = content.count("**MUST") + content.count("**必须")
    if must_count > why_count * 2 and must_count > 3:
        results.append(CheckResult(
            name="why.vs_must_ratio",
            passed=False,
            severity="warn",
            message=f"MUST类规则{must_count}个，Why解释{why_count}个——纯规则过多，建议补充设计意图解释帮助边界情况判断"
        ))
    else:
        results.append(CheckResult(
            name="why.vs_must_ratio",
            passed=True,
            severity="warn",
            message="MUST规则与Why解释比例合理"
        ))

    return results


def check_safety_write_ops(content: str) -> list[CheckResult]:
    results = []

    has_write_ops = any(kw in content.lower() for kw in [k.lower() for k in WRITE_OPERATION_KEYWORDS])
    if not has_write_ops:
        results.append(CheckResult(
            name="safety.write_ops_detected",
            passed=True,
            severity="info",
            message="未检测到写操作关键词，跳过安全检查"
        ))
        return results

    results.append(CheckResult(
        name="safety.write_ops_detected",
        passed=True,
        severity="info",
        message="检测到写操作关键词，执行安全机制检查"
    ))

    has_dryrun = any(kw in content.lower() for kw in [k.lower() for k in DRY_RUN_KEYWORDS])
    results.append(CheckResult(
        name="safety.dry_run",
        passed=has_dryrun,
        severity="error" if not has_dryrun else "info",
        message="包含dry-run/预览/预检机制" if has_dryrun
        else "缺少dry-run/预览机制——写操作Skill必须支持预览确认"
    ))

    has_idempotent_kw = any(kw in content for kw in IDEMPOTENT_KEYWORDS)
    has_post_verify = bool(POST_VERIFY_PATTERN.search(content))
    has_checklist_verify = bool(CHECKLIST_VERIFY_PATTERN.search(content))
    has_idempotent = has_idempotent_kw or has_post_verify or has_checklist_verify
    idempotent_msg = "包含幂等性检查"
    if has_post_verify and not has_idempotent_kw:
        idempotent_msg = "包含后验验证步骤（步骤级验证/确认）"
    elif has_checklist_verify and not has_idempotent_kw:
        idempotent_msg = "包含完成态检查项（清单级验证）"
    results.append(CheckResult(
        name="safety.idempotent",
        passed=has_idempotent,
        severity="warn",
        message=idempotent_msg if has_idempotent
        else "建议添加幂等性检查（避免重复操作）"
    ))

    has_checklist = bool(SAFETY_CHECKLIST_PATTERN.search(content))
    checklist_items = len(CHECKLIST_ITEM_PATTERN.findall(content))
    results.append(CheckResult(
        name="safety.checklist",
        passed=has_checklist and checklist_items >= 5,
        severity="warn",
        message=f"包含安全检查清单（{checklist_items}个检查项）" if has_checklist
        else "建议添加结构化安全检查清单（逐项确认）"
    ))

    return results


def check_decision_tree(content: str) -> list[CheckResult]:
    results = []

    has_multiple_schemes = content.count("方案一") + content.count("方案二") >= 2 or content.count("**方案1") >= 2

    if has_multiple_schemes:
        has_tree = any(p.search(content) for p in DECISION_TREE_PATTERNS)
        results.append(CheckResult(
            name="decision_tree.present",
            passed=has_tree,
            severity="warn",
            message="多方案时包含决策树/选型指引" if has_tree
            else "检测到多方案但缺少决策树——建议提供明确的选型逻辑降低决策负担"
        ))
    else:
        results.append(CheckResult(
            name="decision_tree.present",
            passed=True,
            severity="info",
            message="单方案Skill，无需决策树"
        ))

    return results


def check_trigger_tiers(content: str) -> list[CheckResult]:
    results = []

    has_t0 = "T0" in content and ("弱信号" in content or "weak" in content.lower())
    has_t1 = "T1" in content and ("中信号" in content or "medium" in content.lower())
    has_t2 = "T2" in content and ("强信号" in content or "strong" in content.lower())

    is_tiered = has_t0 or has_t1 or has_t2

    if not is_tiered:
        results.append(CheckResult(
            name="trigger.tiered",
            passed=True,
            severity="info",
            message="未采用三级信号分级（建议按Keyless模式分级：T0弱/T1中/T2强，提升冷启动效率）"
        ))
        return results

    results.append(CheckResult(
        name="trigger.tiered",
        passed=True,
        severity="info",
        message="已采用三级信号分级（Keyless渐进式披露模式）"
    ))

    all_complete = has_t0 and has_t1 and has_t2
    missing = []
    if not has_t0:
        missing.append("T0弱信号")
    if not has_t1:
        missing.append("T1中信号")
    if not has_t2:
        missing.append("T2强信号")

    results.append(CheckResult(
        name="trigger.tiers_complete",
        passed=all_complete,
        severity="warn",
        message="三级信号完整（T0+T1+T2）" if all_complete
        else f"三级信号不完整，缺少：{'、'.join(missing)}"
    ))

    if has_t2:
        action_verbs = ["画", "生成", "检查", "修复", "创建", "导出", "拆分", "提交", "分析", "draw", "create", "check", "fix", "generate"]
        t2_section = ""
        for line in content.split("\n"):
            if "T2" in line and "强信号" in line:
                t2_section = line
                break
        has_action = any(v in t2_section for v in action_verbs) if t2_section else False
        results.append(CheckResult(
            name="trigger.t2_action_intent",
            passed=has_action,
            severity="warn",
            message="T2强信号包含动宾组合（执行意图词）" if has_action
            else "T2强信号建议包含动宾组合词（画/生成/检查/修复等），区分'明确执行'与'领域名词'"
        ))

    return results
