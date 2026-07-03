import json
from pathlib import Path
from typing import Any

from lib.cli import print_warn, print_error
from lib.project import resolve_project_root
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


def _run_spec_checks(spec_dir: Path, project_root: Path, match_threshold: int = 1) -> dict[str, Any]:
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

    rc = check_requirement_task_coverage(spec_data["requirements"], tasks_data["tasks"], match_threshold=match_threshold)
    sc = check_scenario_checkpoint_coverage(spec_data["scenarios"], checklist_data["checkpoints"], match_threshold=match_threshold)
    dc = check_data_consistency(spec_data["data_refs"], tasks_data["stats"], checklist_data["stats"], is_meta=is_meta)
    cr = check_cross_references(spec_text, project_root, spec_dir)
    rd = check_requirement_distinctness(spec_data["requirements"])
    rcl = check_requirement_clarity(spec_data["requirements"])
    se = check_scenario_executability(spec_data["scenarios"], spec_text)

    pass_c = len(rc["covered"]) + len(sc["covered"]) + len(dc["consistent"]) + len(cr["valid"])
    warn_c = len(rc["uncovered"]) + len(sc["uncovered"]) + len(dc.get("warnings", [])) + len(rd["duplicates"]) + len(rcl["repetitive"])
    err_c = len(dc["inconsistent"]) + len(cr["invalid"]) + len(se["missing_structure"])

    result.update({
        "requirement_coverage": rc,
        "scenario_coverage": sc,
        "data_consistency": dc,
        "cross_references": cr,
        "requirement_distinctness": rd,
        "requirement_clarity": rcl,
        "scenario_executability": se,
        "pass_count": pass_c,
        "warn_count": warn_c,
        "error_count": err_c,
    })
    return result


def _check_single(spec_dir: Path, project_root: Path, json_output: bool, match_threshold: int) -> int:
    result = _run_spec_checks(spec_dir, project_root, match_threshold)
    if result["missing_files"]:
        if json_output:
            print(json.dumps({
                "spec_dir": str(spec_dir),
                "summary": {"pass": 0, "warning": 0, "error": 1},
                "checks": {},
                "error": f"缺少文件: {', '.join(result['missing_files'])}",
            }, ensure_ascii=False, indent=2))
        else:
            print_error(f"spec 目录 {spec_dir} 中缺少文件: {', '.join(result['missing_files'])}")
        return 1

    if json_output:
        print(generate_consistency_json_report(
            str(spec_dir),
            result["requirement_coverage"], result["scenario_coverage"],
            result["data_consistency"], result["cross_references"],
            result["requirement_distinctness"], result["requirement_clarity"],
            result["scenario_executability"],
            result["pass_count"], result["warn_count"], result["error_count"],
        ))
    else:
        generate_consistency_terminal_report(
            str(spec_dir),
            result["requirement_coverage"], result["scenario_coverage"],
            result["data_consistency"], result["cross_references"],
            result["requirement_distinctness"], result["requirement_clarity"],
            result["scenario_executability"],
        )
    return 0 if result["error_count"] == 0 else 1


def cmd_check(args) -> int:
    root = args.path or resolve_project_root(__file__)

    if args.spec_dir:
        spec_dir = Path(args.spec_dir)
        if not spec_dir.is_absolute():
            spec_dir = root / args.spec_dir
        if not spec_dir.exists():
            print_error(f"spec 目录不存在: {spec_dir}")
            return 1
        return _check_single(spec_dir, root, args.json, args.match_threshold)

    spec_dirs = discover_spec_dirs(root)
    if not spec_dirs:
        print_warn("未找到任何 spec 目录")
        return 0

    exit_code = 0
    if args.json:
        reports = []
        for sd in spec_dirs:
            r = _run_spec_checks(sd, root, args.match_threshold)
            if r["missing_files"]:
                reports.append({
                    "spec_dir": str(sd),
                    "summary": {"pass": 0, "warning": 0, "error": 1},
                    "checks": {},
                    "error": f"缺少文件: {', '.join(r['missing_files'])}",
                })
                exit_code = 1
                continue
            if r["error_count"] > 0:
                exit_code = 1
            reports.append(json.loads(generate_consistency_json_report(
                str(sd), r["requirement_coverage"], r["scenario_coverage"],
                r["data_consistency"], r["cross_references"],
                r["requirement_distinctness"], r["requirement_clarity"],
                r["scenario_executability"],
                r["pass_count"], r["warn_count"], r["error_count"],
            )))
        print(json.dumps(reports, ensure_ascii=False, indent=2))
    else:
        for sd in spec_dirs:
            ec = _check_single(sd, root, False, args.match_threshold)
            if ec != 0:
                exit_code = 1
            print()
    return exit_code
