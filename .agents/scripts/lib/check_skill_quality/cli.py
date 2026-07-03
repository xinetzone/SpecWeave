import argparse
import json
import sys
from pathlib import Path

from lib.project import resolve_project_root
from lib.cli import print_error, print_warn, print_header, add_common_args, setup_safe_output
from lib.frontmatter import parse_yaml_frontmatter, extract_yaml_field
import lib.quality_report as quality_report
from lib.quality_rules import check_no_file_url

from .constants import SKILLS_DIR
from .models import CheckResult, SkillReport
from .discovery import find_skill_files
from .checks_frontmatter import check_frontmatter
from .checks_description import check_description
from .checks_content import (
    check_file_length,
    check_why_explanations,
    check_safety_write_ops,
    check_decision_tree,
    check_trigger_tiers,
)
from .checks_open_standard import check_open_standards_compliance
from .scoring import calculate_score


def check_skill(skill_md: Path, root: Path) -> SkillReport:
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
