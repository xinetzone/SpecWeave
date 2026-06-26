#!/usr/bin/env python3
"""规格文档一致性检查工具。

检查 spec.md、tasks.md、checklist.md 三份文档之间的一致性，包括：
- 需求 → 任务覆盖检查
- 场景 → 检查点覆盖检查
- 关键数据引用一致性检查
- 交叉引用路径有效性检查
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from constants import SPEC_MATCH_THRESHOLD
from lib.project import resolve_project_root
from lib.cli import print_warn, print_error, add_common_args
from lib.spec import discover_spec_dirs
from lib.spec.parsers import parse_spec, parse_tasks, parse_checklist
from lib.spec.utils import detect_meta_document
from lib.spec.consistency_checkers import (
    check_requirement_task_coverage,
    check_scenario_checkpoint_coverage,
    check_data_consistency,
    check_cross_references,
    check_requirement_distinctness,
    check_requirement_clarity,
    check_scenario_executability,
)
from lib.spec.reporters import (
    generate_consistency_terminal_report,
    generate_consistency_json_report,
)


def run_spec_checks(
    spec_dir: Path,
    project_root: Path,
    match_threshold: int = 1,
) -> dict:
    """对单个 spec 目录执行所有一致性检查，返回结果字典。

    集中处理「解析 + 检查 + 统计」逻辑，供 ``check_single_spec`` 与
    main() 的 JSON 批量分支复用，避免重复实现。

    Args:
        spec_dir: spec 目录路径。
        project_root: 项目根目录（用于交叉引用路径解析）。
        match_threshold: 语义匹配最少共同关键词数。

    Returns:
        包含以下键的字典:
        - requirement_coverage, scenario_coverage, data_consistency,
        - cross_references, requirement_distinctness, requirement_clarity,
        - scenario_executability, pass_count, warn_count, error_count,
        - missing_files (list, 空列表表示文件齐全)

        当 ``missing_files`` 非空时，其余结果键为 ``None``，
        ``error_count`` 记为 1，调用方应据此跳过报告生成。
    """
    result: dict[str, Any] = {
        "requirement_coverage": None,
        "scenario_coverage": None,
        "data_consistency": None,
        "cross_references": None,
        "requirement_distinctness": None,
        "requirement_clarity": None,
        "scenario_executability": None,
        "pass_count": 0,
        "warn_count": 0,
        "error_count": 0,
        "missing_files": [],
    }

    spec_file = spec_dir / "spec.md"
    tasks_file = spec_dir / "tasks.md"
    checklist_file = spec_dir / "checklist.md"

    missing = []
    if not spec_file.exists():
        missing.append("spec.md")
    if not tasks_file.exists():
        missing.append("tasks.md")
    if not checklist_file.exists():
        missing.append("checklist.md")

    if missing:
        result["missing_files"] = missing
        result["error_count"] = 1
        return result

    spec_data = parse_spec(spec_file)
    tasks_data = parse_tasks(tasks_file)
    checklist_data = parse_checklist(checklist_file)

    spec_text = spec_file.read_text(encoding="utf-8")
    is_meta, _ = detect_meta_document(spec_text)

    requirement_coverage = check_requirement_task_coverage(
        spec_data["requirements"], tasks_data["tasks"], match_threshold=match_threshold
    )
    scenario_coverage = check_scenario_checkpoint_coverage(
        spec_data["scenarios"], checklist_data["checkpoints"], match_threshold=match_threshold
    )
    data_consistency = check_data_consistency(
        spec_data["data_refs"],
        tasks_data["stats"],
        checklist_data["stats"],
        is_meta=is_meta,
    )
    cross_references = check_cross_references(
        spec_text,
        project_root,
        spec_dir,
    )

    requirement_distinctness = check_requirement_distinctness(spec_data["requirements"])
    requirement_clarity = check_requirement_clarity(spec_data["requirements"])
    scenario_executability = check_scenario_executability(
        spec_data["scenarios"], spec_text
    )

    pass_count = 0
    warn_count = 0
    error_count = 0

    pass_count += len(requirement_coverage["covered"])
    warn_count += len(requirement_coverage["uncovered"])

    pass_count += len(scenario_coverage["covered"])
    warn_count += len(scenario_coverage["uncovered"])

    pass_count += len(data_consistency["consistent"])
    error_count += len(data_consistency["inconsistent"])
    warn_count += len(data_consistency.get("warnings", []))

    pass_count += len(cross_references["valid"])
    error_count += len(cross_references["invalid"])

    warn_count += len(requirement_distinctness["duplicates"])
    warn_count += len(requirement_clarity["repetitive"])
    error_count += len(scenario_executability["missing_structure"])

    result.update(
        {
            "requirement_coverage": requirement_coverage,
            "scenario_coverage": scenario_coverage,
            "data_consistency": data_consistency,
            "cross_references": cross_references,
            "requirement_distinctness": requirement_distinctness,
            "requirement_clarity": requirement_clarity,
            "scenario_executability": scenario_executability,
            "pass_count": pass_count,
            "warn_count": warn_count,
            "error_count": error_count,
        }
    )
    return result


def check_single_spec(
    spec_dir: Path,
    json_output: bool = False,
    match_threshold: int = 1,
) -> int:
    """对单个 spec 目录执行一致性检查。

    Args:
        spec_dir: spec 目录路径
        json_output: 是否以 JSON 格式输出
        match_threshold: 语义匹配最少共同关键词数

    Returns:
        退出码：0 表示全部通过，1 表示有错误
    """
    project_root = resolve_project_root(__file__)
    result = run_spec_checks(spec_dir, project_root, match_threshold)

    if result["missing_files"]:
        missing_files = result["missing_files"]
        if json_output:
            error_report = {
                "spec_dir": str(spec_dir),
                "summary": {"pass": 0, "warning": 0, "error": 1},
                "checks": {},
                "error": f"缺少文件: {', '.join(missing_files)}",
            }
            print(json.dumps(error_report, ensure_ascii=False, indent=2))
        else:
            print_error(
                f"spec 目录 {spec_dir} 中缺少文件: {', '.join(missing_files)}"
            )
        return 1

    if json_output:
        print(
            generate_consistency_json_report(
                str(spec_dir),
                result["requirement_coverage"],
                result["scenario_coverage"],
                result["data_consistency"],
                result["cross_references"],
                result["requirement_distinctness"],
                result["requirement_clarity"],
                result["scenario_executability"],
                result["pass_count"],
                result["warn_count"],
                result["error_count"],
            )
        )
    else:
        generate_consistency_terminal_report(
            str(spec_dir),
            result["requirement_coverage"],
            result["scenario_coverage"],
            result["data_consistency"],
            result["cross_references"],
            result["requirement_distinctness"],
            result["requirement_clarity"],
            result["scenario_executability"],
        )

    return 0 if result["error_count"] == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="规格文档一致性检查工具",
    )
    add_common_args(parser)
    parser.add_argument(
        "--spec-dir",
        type=str,
        default=None,
        help="指定要检查的 spec 目录路径",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="扫描所有 spec 目录（默认行为）",
    )
    parser.add_argument(
        "--match-threshold",
        type=int,
        default=SPEC_MATCH_THRESHOLD,
        help="语义匹配最少共同关键词数（默认：1）",
    )

    args = parser.parse_args()
    project_root = resolve_project_root(__file__)

    if args.spec_dir:
        spec_dir = Path(args.spec_dir)
        if not spec_dir.is_absolute():
            spec_dir = project_root / args.spec_dir
        if not spec_dir.exists():
            print_error(f"spec 目录不存在: {spec_dir}")
            return 1
        return check_single_spec(
            spec_dir, json_output=args.json, match_threshold=args.match_threshold
        )

    spec_dirs = discover_spec_dirs(project_root)
    if not spec_dirs:
        print_warn("未找到任何 spec 目录")
        return 0

    overall_exit_code = 0

    if args.json:
        all_reports = []
        for spec_dir in spec_dirs:
            result = run_spec_checks(spec_dir, project_root, args.match_threshold)

            if result["missing_files"]:
                all_reports.append({
                    "spec_dir": str(spec_dir),
                    "summary": {"pass": 0, "warning": 0, "error": 1},
                    "checks": {},
                    "error": f"缺少文件: {', '.join(result['missing_files'])}",
                })
                overall_exit_code = 1
                continue

            if result["error_count"] > 0:
                overall_exit_code = 1

            # 复用 generate_consistency_json_report 构造单 spec 报告，
            # 通过 json.loads 转为字典加入批量列表，避免重复字段映射逻辑。
            report_json = generate_consistency_json_report(
                str(spec_dir),
                result["requirement_coverage"],
                result["scenario_coverage"],
                result["data_consistency"],
                result["cross_references"],
                result["requirement_distinctness"],
                result["requirement_clarity"],
                result["scenario_executability"],
                result["pass_count"],
                result["warn_count"],
                result["error_count"],
            )
            all_reports.append(json.loads(report_json))

        print(json.dumps(all_reports, ensure_ascii=False, indent=2))
    else:
        for spec_dir in spec_dirs:
            exit_code = check_single_spec(
                spec_dir, json_output=False, match_threshold=args.match_threshold
            )
            if exit_code != 0:
                overall_exit_code = 1
            print()

    return overall_exit_code


if __name__ == "__main__":
    sys.exit(main())
