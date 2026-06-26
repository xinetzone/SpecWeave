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
    spec_file = spec_dir / "spec.md"
    tasks_file = spec_dir / "tasks.md"
    checklist_file = spec_dir / "checklist.md"

    missing_files = []
    if not spec_file.exists():
        missing_files.append("spec.md")
    if not tasks_file.exists():
        missing_files.append("tasks.md")
    if not checklist_file.exists():
        missing_files.append("checklist.md")

    if missing_files:
        if json_output:
            error_report = {
                "spec_dir": str(spec_dir),
                "summary": {"pass": 0, "warning": 0, "error": 1},
                "checks": {},
                "error": f"缺少文件: {', '.join(missing_files)}",
            }
            print(json.dumps(error_report, ensure_ascii=False, indent=2))
        else:
            print_error(f"spec 目录 {spec_dir} 中缺少文件: {', '.join(missing_files)}")
        return 1

    spec_data = parse_spec(spec_file)
    tasks_data = parse_tasks(tasks_file)
    checklist_data = parse_checklist(checklist_file)

    spec_text = spec_file.read_text(encoding="utf-8")

    project_root = resolve_project_root(__file__)
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

    if json_output:
        print(
            generate_consistency_json_report(
                str(spec_dir),
                requirement_coverage,
                scenario_coverage,
                data_consistency,
                cross_references,
                requirement_distinctness,
                requirement_clarity,
                scenario_executability,
                pass_count,
                warn_count,
                error_count,
            )
        )
    else:
        generate_consistency_terminal_report(
            str(spec_dir),
            requirement_coverage,
            scenario_coverage,
            data_consistency,
            cross_references,
            requirement_distinctness,
            requirement_clarity,
            scenario_executability,
        )

    return 0 if error_count == 0 else 1


def discover_spec_dirs(project_root: Path) -> list[Path]:
    """发现项目中的所有 spec 目录。"""
    specs_root = project_root / ".trae" / "specs"
    if not specs_root.exists():
        return []
    return sorted(
        [d for d in specs_root.iterdir() if d.is_dir()],
        key=lambda p: p.name,
    )


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
                all_reports.append({
                    "spec_dir": str(spec_dir),
                    "summary": {"pass": 0, "warning": 0, "error": 1},
                    "checks": {},
                    "error": f"缺少文件: {', '.join(missing)}",
                })
                overall_exit_code = 1
                continue

            spec_data = parse_spec(spec_file)
            tasks_data = parse_tasks(tasks_file)
            checklist_data = parse_checklist(checklist_file)

            spec_text = spec_file.read_text(encoding="utf-8")
            is_meta, _ = detect_meta_document(spec_text)

            requirement_coverage = check_requirement_task_coverage(
                spec_data["requirements"], tasks_data["tasks"],
                match_threshold=args.match_threshold,
            )
            scenario_coverage = check_scenario_checkpoint_coverage(
                spec_data["scenarios"], checklist_data["checkpoints"],
                match_threshold=args.match_threshold,
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

            pass_count = (
                len(requirement_coverage["covered"])
                + len(scenario_coverage["covered"])
                + len(data_consistency["consistent"])
                + len(cross_references["valid"])
            )
            warn_count = (
                len(requirement_coverage["uncovered"])
                + len(scenario_coverage["uncovered"])
                + len(data_consistency.get("warnings", []))
                + len(requirement_distinctness["duplicates"])
                + len(requirement_clarity["repetitive"])
            )
            error_count = (
                len(data_consistency["inconsistent"])
                + len(cross_references["invalid"])
                + len(scenario_executability["missing_structure"])
            )

            if error_count > 0:
                overall_exit_code = 1

            all_reports.append({
                "spec_dir": str(spec_dir),
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
            })

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
