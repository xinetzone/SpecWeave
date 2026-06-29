#!/usr/bin/env python3
"""Skill 质量检查器：验证 .agents/skills/ 下的 SKILL.md 是否符合五要素模型规范。

检查项基于 .agents/rules/skill-development.md 规范：
  1. Frontmatter 完整性（name/description必需字段）
  2. Description 质量（触发词覆盖、强制措辞、长度）
  3. 文件长度控制（≤500行，渐进式披露原则）
  4. Why 解释覆盖率（关键规则有设计意图说明）
  5. 安全检查清单（写操作Skill必须有dry-run/幂等/验证/确认）
  6. 路径规范（相对路径，无file:///绝对路径）
  7. 决策树/方案选择（多方案时有决策指引）
  8. 资产盘点检查（优化现有Skill时检查）

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

SKILLS_DIR = ".agents/skills"
MAX_SKILL_LINES = 500
MIN_DESCRIPTION_LENGTH = 50
RECOMMENDED_DESCRIPTION_LENGTH = 150

FRONTMATTER_REQUIRED_FIELDS = {"name", "description"}
FRONTMATTER_RECOMMENDED_FIELDS = {"version", "argument-hint", "user-invocable", "paths"}

MANDATORY_TRIGGER_PHRASES = ["必须使用", "Use this skill", "必须", "MUST use"]
WRITE_OPERATION_KEYWORDS = ["编辑", "创建", "删除", "发布", "更新", "写", "edit", "create", "delete", "post", "update", "write"]
DRY_RUN_KEYWORDS = ["dry-run", "dry_run", "dryrun", "预览", "试运行", "预演"]
IDEMPOTENT_KEYWORDS = ["幂等", "idempotent", "重复检查", "已存在", "skipped"]
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
FILE_URL_PATTERN = re.compile(r"file:///")


@dataclass
class CheckResult:
    """单个检查项结果"""
    name: str
    passed: bool
    severity: str
    message: str
    line: Optional[int] = None


@dataclass
class SkillReport:
    """单个Skill的完整检查报告"""
    skill_path: Path
    skill_name: str
    results: list[CheckResult] = field(default_factory=list)
    score: int = 0

    @property
    def errors(self) -> list[CheckResult]:
        return [r for r in self.results if r.severity == "error" and not r.passed]

    @property
    def warnings(self) -> list[CheckResult]:
        return [r for r in self.results if r.severity == "warn" and not r.passed]

    @property
    def passes(self) -> list[CheckResult]:
        return [r for r in self.results if r.passed]


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
    results = []
    lines = content.count("\n") + 1

    passed = lines <= MAX_SKILL_LINES
    results.append(CheckResult(
        name="file.length",
        passed=passed,
        severity="warn" if passed else "error",
        message=f"文件{lines}行" + ("（符合≤500行规范）" if passed else f"（超过{MAX_SKILL_LINES}行建议，考虑使用references/子文档进行渐进式披露）")
    ))

    return results


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
        message="包含dry-run/预览机制" if has_dryrun
        else "缺少dry-run/预览机制——写操作Skill必须支持预览确认"
    ))

    has_idempotent = any(kw in content for kw in IDEMPOTENT_KEYWORDS)
    results.append(CheckResult(
        name="safety.idempotent",
        passed=has_idempotent,
        severity="warn",
        message="包含幂等性检查" if has_idempotent
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


def check_paths(content: str) -> list[CheckResult]:
    """检查路径规范"""
    results = []

    file_urls = FILE_URL_PATTERN.findall(content)
    has_file_url = len(file_urls) > 0
    results.append(CheckResult(
        name="paths.no_file_url",
        passed=not has_file_url,
        severity="error",
        message="无file:///绝对路径" if not has_file_url
        else f"发现{len(file_urls)}处file:///绝对路径（应使用相对路径）"
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
    report.results.extend(check_paths(content))
    report.results.extend(check_decision_tree(content))

    report.score = calculate_score(report)
    return report


def print_skill_report(report: SkillReport, root_dir: Path, verbose: bool = False) -> None:
    """打印单个Skill检查结果"""
    try:
        rel_path = report.skill_path.relative_to(root_dir)
    except (ValueError, IndexError):
        rel_path = report.skill_path
    score_color = "\033[92m" if report.score >= 80 else "\033[93m" if report.score >= 60 else "\033[91m"
    reset = "\033[0m"
    print(f"\n  {score_color}【{report.skill_name}】{report.score}分{reset} ({rel_path})")

    for r in report.results:
        if r.passed and not verbose:
            continue
        if r.severity == "error" and not r.passed:
            print_error(f"    [FAIL] {r.name}: {r.message}")
        elif r.severity == "warn" and not r.passed:
            print_warn(f"    [WARN] {r.name}: {r.message}")
        elif verbose:
            if r.passed:
                print_pass(f"    [PASS] {r.name}: {r.message}")


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
        output = {
            "skills_dir": str(skills_dir),
            "skill_count": len(reports),
            "skills": [
                {
                    "name": r.skill_name,
                    "path": str(r.skill_path.relative_to(root_dir)),
                    "score": r.score,
                    "errors": [{"name": res.name, "message": res.message} for res in r.errors],
                    "warnings": [{"name": res.name, "message": res.message} for res in r.warnings],
                    "pass_count": len(r.passes),
                }
                for r in reports
            ],
            "average_score": sum(r.score for r in reports) // len(reports) if reports else 0,
            "total_errors": sum(len(r.errors) for r in reports),
            "total_warnings": sum(len(r.warnings) for r in reports),
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    if args.score:
        for r in reports:
            print(f"{r.skill_name}: {r.score}")
        avg = sum(r.score for r in reports) // len(reports) if reports else 0
        print(f"平均: {avg}")
        failed = [r for r in reports if r.score < args.threshold]
        sys.exit(1 if failed else 0)

    print_header("Skill 质量检查（五要素模型）")
    print(f"  扫描目录: {skills_dir}")
    print(f"  检查项: Frontmatter/Description/长度/Why解释/安全清单/路径规范/决策树")
    print(f"  发现 {len(reports)} 个 Skill")

    for report in reports:
        print_skill_report(report, root_dir, verbose=args.verbose)

    total_errors = sum(len(r.errors) for r in reports)
    total_warnings = sum(len(r.warnings) for r in reports)
    total_passes = sum(len(r.passes) for r in reports)
    avg_score = sum(r.score for r in reports) // len(reports) if reports else 0

    print()
    print(f"  平均质量分: {avg_score}/100")
    print_summary(
        pass_count=total_passes,
        warn_count=total_warnings,
        error_count=total_errors,
    )

    if avg_score < args.threshold:
        print()
        print_warn(f"平均评分{avg_score}低于阈值{args.threshold}，建议根据上述改进项优化后再提交")
        print()
        print("改进指引：")
        print("  1. Description：补充触发词和'必须使用此技能'强制措辞（参见forum-posting正面示例）")
        print("  2. Why解释：关键MUST规则后添加'> **为什么？**'引用块解释设计意图")
        print("  3. 安全清单：写操作Skill必须有dry-run+幂等检查+用户确认清单")
        print("  4. 文件长度：超过500行时，将低频内容移到references/子文档")
        print("  5. 决策树：多方案时提供树形选型指引而非并列罗列")
        print("  6. 参考模板：.agents/skills/SKILL-TEMPLATE.md 包含完整五要素框架")

    failed = [r for r in reports if r.errors]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
