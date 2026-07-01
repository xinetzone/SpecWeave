#!/usr/bin/env python3
"""Skill 质量检查器：验证 .agents/skills/ 下的 SKILL.md 是否符合五要素模型规范 + Agent Skills 开放标准合规性。

检查项基于 .agents/rules/skill-development.md 规范 + agentskills.io 开放标准：
  【五要素模型·项目规范】
  1. Frontmatter 完整性（name/description必需字段）
  2. Description 质量（触发词覆盖、强制措辞、长度）
  3. 文件长度控制（≤500行，渐进式披露原则）
  4. Why 解释覆盖率（关键规则有设计意图说明）
  5. 安全检查清单（写操作Skill必须有dry-run/幂等/验证/确认）
  6. 路径规范（相对路径，无file:///绝对路径）
  7. 决策树/方案选择（多方案时有决策指引）
  8. 触发词三级信号分级（Keyless渐进式披露模式：T0弱/T1中/T2强）
  9. 资产盘点检查（优化现有Skill时检查）
  【Agent Skills开放标准·跨客户端兼容】
  10. name格式规范（kebab-case小写、长度≤64、仅字母数字连字符、与目录名一致）
  11. description长度硬限制（≤1024字符）
  12. 可选目录结构提示（scripts/references/assets/evals）
  13. 自定义扩展字段识别（兼容性说明）
  14. Gotchas/常见陷阱章节建议

用法：
  python check-skill-quality.py                     # 检查所有Skill
  python check-skill-quality.py --path <skill-dir> # 检查指定Skill目录
  python check-skill-quality.py --json             # JSON格式输出
  python check-skill-quality.py --score            # 输出质量评分(0-100)
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from lib.project import resolve_project_root
from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, add_common_args, setup_safe_output
from lib.frontmatter import parse_yaml_frontmatter, extract_yaml_field
from lib.rules import load_rules
import lib.quality_report as quality_report
from lib.quality_rules import check_no_file_url

SKILLS_DIR = ".agents/skills"
MAX_SKILL_LINES = 500
MIN_DESCRIPTION_LENGTH = 50
RECOMMENDED_DESCRIPTION_LENGTH = 150

FRONTMATTER_REQUIRED_FIELDS = {"name", "description"}
FRONTMATTER_RECOMMENDED_FIELDS = {"version", "argument-hint", "user-invocable", "paths"}

OPEN_STANDARD_ALLOWED_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
OPEN_STANDARD_MAX_NAME_LENGTH = 64
OPEN_STANDARD_MAX_DESCRIPTION_LENGTH = 1024
OPEN_STANDARD_MIN_DESCRIPTION_LENGTH_FOR_STANDARD = 20
OPEN_STANDARD_OPTIONAL_DIRS = ["scripts", "references", "assets", "evals"]

MANDATORY_TRIGGER_PHRASES = ["必须使用", "Use this skill", "必须", "MUST use"]
WRITE_OPERATION_KEYWORDS = ["编辑", "创建", "删除", "发布", "更新", "写", "edit", "create", "delete", "post", "update", "write"]
DRY_RUN_KEYWORDS = ["dry-run", "dry_run", "dryrun", "预览", "试运行", "预演", "预检", "预检查", "预提交", "质量门"]
IDEMPOTENT_KEYWORDS = ["幂等", "idempotent", "重复检查", "已存在", "skipped", "验证结果", "无遗漏", "无残留", "收尾验证", "无断链", "已更新"]
POST_VERIFY_PATTERN = re.compile(r"步骤\d+[：:].*(?:验证|确认|检查)", re.MULTILINE)
CHECKLIST_VERIFY_PATTERN = re.compile(r"^- \[ \].*(?:已验证|已确认|已检查|已更新|已完成|已区分|已明确|无断链|无遗漏|无残留|更新了)", re.MULTILINE)
CONFIRMATION_KEYWORDS = ["确认", "confirm", "获得.*确认", "用户确认"]
WHY_EXPLANATION_PATTERN = re.compile(r">\s*\*\*为什么", re.MULTILINE)
DECISION_TREE_PATTERNS = [
    re.compile(r"决策树", re.MULTILINE),
    re.compile(r"方案选择", re.MULTILINE),
    re.compile(r"├─", re.MULTILINE),
    re.compile(r"└─", re.MULTILINE),
    re.compile(r"flowchart", re.MULTILINE),
]
SAFETY_CHECKLIST_PATTERN = re.compile(r"安全检查清单|检查清单.*逐项", re.MULTILINE)
CHECKLIST_ITEM_PATTERN = re.compile(r"^- \[ \]", re.MULTILINE)
@dataclass
class CheckResult:
    """单个检查项结果"""
    name: str
    passed: bool
    severity: str
    message: str
    line: Optional[int] = None


@dataclass
class SkillReport(quality_report.ResultGroupMixin):
    """单个Skill的完整检查报告"""
    skill_path: Path
    skill_name: str
    results: list[CheckResult] = field(default_factory=list)
    score: int = 0


def find_skill_files(root: Path, skills_dir: Path, target_path: Optional[Path] = None) -> list[Path]:
    """发现所有SKILL.md文件"""
    rules = load_rules()
    skill_files = []

    if target_path:
        target = target_path if target_path.is_file() else target_path / "SKILL.md"
        if target.exists():
            return [target]
        return []

    if not skills_dir.exists():
        return []

    for skill_md in skills_dir.rglob("SKILL.md"):
        should_skip, _ = rules.should_skip_file(skill_md, root_dir=root)
        if should_skip:
            continue
        if skill_md.name == "SKILL-TEMPLATE.md" or "SKILL-TEMPLATE" in str(skill_md):
            continue
        skill_files.append(skill_md)

    return sorted(skill_files)


def check_frontmatter(skill_md: Path, content: str, frontmatter_text: Optional[str]) -> list[CheckResult]:
    """检查Frontmatter完整性"""
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


def check_description(frontmatter_text: Optional[str]) -> list[CheckResult]:
    """检查Description质量（Trigger-Ready规范）"""
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


def check_file_length(skill_md: Path, content: str) -> list[CheckResult]:
    """检查文件长度（渐进式披露原则）"""
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
    """检查Why解释覆盖率"""
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
    """检查写操作安全机制（Safety Checklist）"""
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
    """检查多方案决策树"""
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
    """检查触发词三级信号分级（Keyless渐进式披露模式）

    检测SKILL.md是否采用T0弱信号/T1中信号/T2强信号三级分级。
    未分级的Skill不扣分（向后兼容），分级但不完整的扣warn分。
    """
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

    # T2强信号应包含动宾组合（动词关键词），检查是否含有执行意图词
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


def check_open_standards_compliance(skill_md: Path, content: str, frontmatter_text: Optional[str]) -> list[CheckResult]:
    """检查 Agent Skills 开放标准（agentskills.io）跨客户端兼容性

    检查项：
    - name格式：kebab-case小写、长度≤64、仅字母数字连字符、与目录名一致
    - description长度：硬限制≤1024字符
    - 可选目录结构提示（scripts/references/assets/evals）
    - 自定义扩展字段识别（兼容性说明）
    - Gotchas/常见陷阱章节建议
    """
    results = []
    skill_dir = skill_md.parent
    dir_name = skill_dir.name

    if not frontmatter_text:
        return results

    name = extract_yaml_field(frontmatter_text, "name")
    desc = extract_yaml_field(frontmatter_text, "description")

    # name 格式检查
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

    # description 硬限制检查
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

    # 可选目录结构检查
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

    # 自定义扩展字段识别
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

    # Gotchas/常见陷阱章节
    has_gotchas = any(kw in content for kw in ["## Gotchas", "## 常见错误", "## 常见问题", "## 陷阱", "## 易错点"])
    results.append(CheckResult(
        name="open_standard.body.gotchas",
        passed=has_gotchas,
        severity="info",
        message="包含Gotchas/常见陷阱章节" if has_gotchas
        else "建议包含Gotchas/常见陷阱章节，列出容易犯错的点（最佳实践）"
    ))

    # 总结性检查项
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


def _get_dir_purpose(dirname: str) -> str:
    """返回可选目录的用途说明"""
    purposes = {
        "scripts": "用于捆绑可执行脚本",
        "references": "用于详细参考文档，实现渐进式披露",
        "assets": "用于模板、静态资源等",
        "evals": "用于质量评估测试用例",
    }
    return purposes.get(dirname, "可选目录")


def calculate_score(report: SkillReport) -> int:
    """计算质量评分（0-100）"""
    score = 100

    for r in report.results:
        if r.passed:
            continue
        if r.severity == "error":
            score -= 15
        elif r.severity == "warn":
            score -= 5
        elif r.severity == "info":
            score -= 1

    return max(0, min(100, score))


def check_skill(skill_md: Path, root: Path) -> SkillReport:
    """检查单个Skill"""
    content = skill_md.read_text(encoding="utf-8")
    frontmatter_text = parse_yaml_frontmatter(skill_md)

    skill_name = extract_yaml_field(frontmatter_text, "name") if frontmatter_text else skill_md.parent.name
    report = SkillReport(
        skill_path=skill_md,
        skill_name=skill_name or skill_md.parent.name
    )

    report.results.extend(check_frontmatter(skill_md, content, frontmatter_text))
    report.results.extend(check_description(frontmatter_text))
    report.results.extend(check_file_length(skill_md, content))
    report.results.extend(check_why_explanations(content))
    report.results.extend(check_safety_write_ops(content))
    report.results.extend(check_no_file_url(content, lambda **kw: CheckResult(**kw)))
    report.results.extend(check_decision_tree(content))
    report.results.extend(check_trigger_tiers(content))
    report.results.extend(check_open_standards_compliance(skill_md, content, frontmatter_text))

    report.score = calculate_score(report)
    return report


def print_skill_report(report: SkillReport, root_dir: Path, verbose: bool = False) -> None:
    """打印单个Skill检查结果"""
    rel_path = quality_report.safe_relative_to(report.skill_path, root_dir)
    quality_report.print_scored_report_cli(
        score=report.score,
        header=f"【{report.skill_name}】{report.score}分 ({rel_path})",
        extra_lines=[],
        results=report.results,
        verbose=verbose,
    )


def main() -> None:
    setup_safe_output()
    parser = argparse.ArgumentParser(
        description="Skill质量检查：验证SKILL.md符合五要素模型规范"
    )
    add_common_args(parser)
    parser.add_argument("--score", action="store_true", help="仅输出质量评分")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示通过项详情")
    parser.add_argument("--threshold", type=int, default=70, help="评分阈值（低于则退出码1，默认70）")
    args = parser.parse_args()

    root_dir = resolve_project_root(__file__)
    skills_dir = root_dir / SKILLS_DIR

    target_path = Path(args.path).resolve() if args.path else None
    skill_files = find_skill_files(root_dir, skills_dir, target_path)

    if not skill_files:
        msg = f"未找到SKILL.md文件（目录: {skills_dir}）"
        if args.json:
            print(json.dumps({"error": msg, "skills": []}, ensure_ascii=False, indent=2))
        else:
            print_error(msg)
        sys.exit(1)

    reports = [check_skill(f, root_dir) for f in skill_files]

    if args.json:
        output = quality_report.build_json_output(
            reports,
            root_dir,
            base_dir_key="skills_dir",
            base_dir_value=skills_dir,
            count_key="skill_count",
            items_key="skills",
            item_builder=lambda r: {
                "name": r.skill_name,
                "path": str(quality_report.safe_relative_to(r.skill_path, root_dir)),
                **quality_report.common_report_fields(r),
            },
        )
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    if args.score:
        for r in reports:
            print(f"{r.skill_name}: {r.score}")
        avg = sum(r.score for r in reports) // len(reports) if reports else 0
        print(f"平均: {avg}")
        failed = [r for r in reports if r.score < args.threshold]
        sys.exit(1 if failed else 0)

    print_header("Skill 质量检查（五要素模型 + Agent Skills开放标准）")
    print(f"  扫描目录: {skills_dir}")
    print(f"  检查项: Frontmatter/Description/长度/Why解释/安全清单/路径规范/决策树/触发词分级/开放标准合规")
    print(f"  发现 {len(reports)} 个 Skill")

    for report in reports:
        print_skill_report(report, root_dir, verbose=args.verbose)

    stats = quality_report.print_aggregate_summary(reports)
    avg_score = stats["avg_score"]

    if avg_score < args.threshold:
        print()
        print_warn(f"平均评分{avg_score}低于阈值{args.threshold}，建议根据上述改进项优化后再提交")
        print()
        print("改进指引：")
        print("  【五要素模型·项目规范】")
        print("  1. Description：补充触发词和'必须使用此技能'强制措辞（参见forum-posting正面示例）")
        print("  2. Why解释：关键MUST规则后添加'> **为什么？**'引用块解释设计意图")
        print("  3. 安全清单：写操作Skill必须有dry-run+幂等检查+用户确认清单")
        print("  4. 文件长度：超过500行时，将低频内容移到references/子文档")
        print("  5. 决策树：多方案时提供树形选型指引而非并列罗列")
        print("  6. 参考模板：.agents/skills/SKILL-TEMPLATE.md 包含完整五要素框架")
        print("  【Agent Skills开放标准·跨客户端兼容】")
        print("  7. name格式：使用kebab-case小写连字符（如my-skill-name），长度≤64字符，与目录名一致")
        print("  8. description：长度≤1024字符（硬限制），包含触发时机说明")
        print("  9. 可选目录：scripts/捆绑脚本、references/详细文档、assets/静态资源、evals/测试用例")
        print("  10. 自定义字段：项目扩展字段（version/argument-hint等）兼容客户端会安全忽略，无需移除")

    failed = [r for r in reports if r.errors]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
