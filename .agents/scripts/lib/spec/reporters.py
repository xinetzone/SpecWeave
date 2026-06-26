"""Spec 检查报告生成器。

提供终端彩色报告和 JSON 报告生成功能。
"""

import json
from typing import Any

from lib.cli import print_pass, print_warn, print_error, print_header, print_summary


def generate_consistency_terminal_report(
    spec_dir: str,
    requirement_coverage: dict[str, Any],
    scenario_coverage: dict[str, Any],
    data_consistency: dict[str, Any],
    cross_references: dict[str, Any],
    requirement_distinctness: dict[str, Any],
    requirement_clarity: dict[str, Any],
    scenario_executability: dict[str, Any],
) -> tuple[int, int, int]:
    """生成一致性检查的终端彩色报告，返回 (通过数, 警告数, 错误数)。"""
    pass_count = 0
    warn_count = 0
    error_count = 0

    print_header("规格文档一致性检查报告")
    print(f"检查目录: {spec_dir}")
    print()

    print("[需求 → 任务覆盖]")
    for req_name, task_name in requirement_coverage["covered"]:
        print_pass(f"需求 \"{req_name}\" → 任务 \"{task_name}\"")
        pass_count += 1
    for req_name in requirement_coverage["uncovered"]:
        print_warn(f"需求 \"{req_name}\" 在 tasks.md 中无对应任务")
        warn_count += 1
    print()

    print("[场景 → 检查点覆盖]")
    for scenario_name, cp_text in scenario_coverage["covered"]:
        print_pass(f"场景 \"{scenario_name}\" → 检查点 \"{cp_text}\"")
        pass_count += 1
    for scenario_name in scenario_coverage["uncovered"]:
        print_warn(f"场景 \"{scenario_name}\" 在 checklist.md 中无对应检查点")
        warn_count += 1
    print()

    print("[数据引用一致性]")
    for item in data_consistency["consistent"]:
        print_pass(item)
        pass_count += 1
    for item in data_consistency["inconsistent"]:
        print_error(item)
        error_count += 1
    for item in data_consistency.get("warnings", []):
        print_warn(item)
        warn_count += 1
    print()

    print("[交叉引用有效性]")
    for path_str in cross_references["valid"]:
        print_pass(path_str)
        pass_count += 1
    for path_str in cross_references["invalid"]:
        print_error(f"{path_str} — 文件不存在")
        error_count += 1
    print()

    print("[区分度检查 - Requirement 名称唯一性]")
    duplicates = requirement_distinctness.get("duplicates", [])
    if not duplicates:
        print_pass("所有 Requirement 名称唯一")
        pass_count += 1
    else:
        for dup in duplicates:
            sections_str = ", ".join(dup["sections"]) if dup["sections"] else "未知"
            print_warn(f"Requirement 名称 \"{dup['name']}\" 重复 {dup['count']} 次（出现章节：{sections_str}）")
            warn_count += 1
    print()

    print("[清晰度检查 - Requirement 描述关键词重复]")
    repetitive = requirement_clarity.get("repetitive", [])
    if not repetitive:
        print_pass("Requirement 描述无明显关键词重复")
        pass_count += 1
    else:
        for item in repetitive:
            words_str = ", ".join(
                f"\"{w['word']}\"({w['count']}次)" for w in item["repeated_words"]
            )
            print_warn(f"Requirement \"{item['name']}\" 描述存在关键词重复: {words_str}")
            warn_count += 1
    print()

    print("[可执行性检查 - Scenario 结构完整性]")
    missing_structure = scenario_executability.get("missing_structure", [])
    if not missing_structure:
        print_pass("所有 Scenario 结构完整（包含 WHEN/GIVEN 和 THEN/EXPECT）")
        pass_count += 1
    else:
        for item in missing_structure:
            missing_str = ", ".join(item["missing"])
            print_error(f"Scenario \"{item['name']}\" 缺少结构: {missing_str}")
            error_count += 1
    print()

    print_summary(pass_count, warn_count, error_count)

    return pass_count, warn_count, error_count


def generate_consistency_json_report(
    spec_dir: str,
    requirement_coverage: dict[str, Any],
    scenario_coverage: dict[str, Any],
    data_consistency: dict[str, Any],
    cross_references: dict[str, Any],
    requirement_distinctness: dict[str, Any],
    requirement_clarity: dict[str, Any],
    scenario_executability: dict[str, Any],
    pass_count: int,
    warn_count: int,
    error_count: int,
) -> str:
    """生成一致性检查的 JSON 格式报告。"""
    report = {
        "spec_dir": spec_dir,
        "summary": {
            "pass": pass_count,
            "warning": warn_count,
            "error": error_count,
        },
        "checks": {
            "requirement_task_coverage": {
                "covered": [
                    {"requirement": r, "task": t}
                    for r, t in requirement_coverage["covered"]
                ],
                "uncovered": requirement_coverage["uncovered"],
            },
            "scenario_checkpoint_coverage": {
                "covered": [
                    {"scenario": s, "checkpoint": c}
                    for s, c in scenario_coverage["covered"]
                ],
                "uncovered": scenario_coverage["uncovered"],
            },
            "data_consistency": {
                "consistent": data_consistency["consistent"],
                "inconsistent": data_consistency["inconsistent"],
                "warnings": data_consistency.get("warnings", []),
            },
            "cross_references": {
                "valid": cross_references["valid"],
                "invalid": cross_references["invalid"],
            },
            "requirement_distinctness": requirement_distinctness,
            "requirement_clarity": requirement_clarity,
            "scenario_executability": scenario_executability,
        },
    }
    return json.dumps(report, ensure_ascii=False, indent=2)


def print_format_result_text(result, verbose: bool = False):
    """以文本格式输出格式检查结果。"""
    print(f"\n{'='*60}")
    print(f"检查文件: {result.spec_path}")
    print(f"评分: {result.score}/100")
    print(f"{'='*60}")

    if result.errors:
        print(f"\n错误 ({len(result.errors)} 项):")
        for err in result.errors:
            print_error(f"[{err['type']}] {err['name']}: {err['message']}")

    if result.warnings:
        print(f"\n警告 ({len(result.warnings)} 项):")
        for warn in result.warnings:
            print_warn(f"[{warn['type']}] {warn['name']}: {warn['message']}")

    if not result.errors and not result.warnings:
        print_pass("检查通过，无错误和警告")
    elif not result.errors and result.warnings:
        print_pass("检查通过（有警告，建议优化）")

    if verbose and not result.errors:
        print("\n检查详情:")
        print_pass("核心章节结构完整")
        print_pass("Requirement 定义规范")
        print_pass("Scenario 结构完整")
        print_pass("验收标准可验证")
        print_pass("版本号与变更日志规范")


def print_format_summary_text(results: list):
    """输出格式检查摘要（多文件模式）。"""
    total = len(results)
    passed = sum(1 for r in results if not r.errors)
    failed = total - passed

    print(f"\n{'='*60}")
    print(f"检查摘要")
    print(f"{'='*60}")
    print(f"总计检查: {total} 个 spec 目录")
    print(f"通过（无错误）: {passed} 个")
    print(f"未通过（有错误）: {failed} 个")

    if failed > 0:
        print(f"\n未通过的 spec:")
        for r in results:
            if r.errors:
                print(f"  - {r.spec_path}: 评分 {r.score}/100, {len(r.errors)} 个错误")

    low_score = [r for r in results if r.score < 80]
    if low_score:
        print(f"\n评分低于 80 分的 spec:")
        for r in low_score:
            print(f"  - {r.spec_path}: 评分 {r.score}/100")
