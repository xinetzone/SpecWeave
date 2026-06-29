#!/usr/bin/env python3
"""Spec 文档工具集。

聚合以下 Spec 相关功能：
  check      - 规格文档一致性检查（需求→任务覆盖、场景→检查点覆盖等）
  format     - Spec 文档标准化格式检查（章节完整性、验收标准、版本规范）
  gen-tests  - 从 spec.md 生成 pytest 测试骨架

用法：
  python spec-tool.py check [--spec-dir DIR] [--match-threshold N]
  python spec-tool.py format [--spec-dir DIR] [--check-all] [--format text|json|yaml] [-v]
  python spec-tool.py gen-tests [--spec DIR | --all] [--output FILE] [--output-dir DIR] [--dry-run]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from constants import SPEC_MATCH_THRESHOLD
from lib.cli import print_header, print_pass, print_warn, print_error, print_summary, setup_safe_output
from lib.project import resolve_project_root
from lib.spec import discover_spec_dirs
from lib.spec.models import Issue, SpecCheckResult
from lib.spec.parsers import parse_spec, parse_tasks, parse_checklist
from lib.spec.utils import detect_meta_document, CORE_CHAPTERS, calculate_score
from lib.spec.format_checkers import (
    detect_core_chapters,
    check_chapter_not_empty,
    detect_requirements,
    check_acceptance_criteria,
    check_version_and_changelog,
)
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
    print_format_result_text,
    print_format_summary_text,
)


# ============================================================
# check 子命令：一致性检查
# ============================================================

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


# ============================================================
# format 子命令：格式标准化检查
# ============================================================

def _check_spec_file(spec_path: str, verbose: bool) -> SpecCheckResult:
    result = SpecCheckResult(spec_path=spec_path)
    try:
        content = Path(spec_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        result.errors.append({"type": "file_not_found", "name": spec_path, "message": f"文件不存在: {spec_path}"})
        return result
    except Exception as e:
        result.errors.append({"type": "read_error", "name": spec_path, "message": f"读取文件失败: {str(e)}"})
        return result

    all_issues: list[Issue] = []
    if verbose:
        print(f"[检查中] 核心章节检测...")
    chapter_issues, found_chapters, _ = detect_core_chapters(content)
    all_issues.extend(chapter_issues)

    for ch_name, pattern, _ in CORE_CHAPTERS:
        issue = check_chapter_not_empty(content, ch_name, pattern)
        if issue:
            all_issues.append(issue)

    if verbose:
        print(f"[检查中] Requirement 完整性验证...")
    req_issues, requirements = detect_requirements(content)
    all_issues.extend(req_issues)

    if verbose:
        print(f"[检查中] 验收标准可验证性检查...")
    crit_issues = check_acceptance_criteria(content)
    all_issues.extend(crit_issues)

    if verbose:
        print(f"[检查中] 版本号与变更日志检测...")
    ver_issues, _ = check_version_and_changelog(content)
    all_issues.extend(ver_issues)

    result.errors = [{"type": i.type, "name": i.name, "message": i.message} for i in all_issues if i.severity == "error"]
    result.warnings = [{"type": i.type, "name": i.name, "message": i.message} for i in all_issues if i.severity == "warning"]
    result.score = calculate_score(all_issues, found_chapters, requirements)

    if verbose:
        print(f"[完成] 评分: {result.score}, 错误: {len(result.errors)}, 警告: {len(result.warnings)}")
    return result


def _find_spec_dirs(base_path: Path, check_all: bool) -> list[Path]:
    if not base_path.exists():
        return []
    if check_all:
        return sorted([p.parent for p in base_path.rglob("spec.md") if p.is_file()])
    if (base_path / "spec.md").exists():
        return [base_path]
    return []


def cmd_format(args) -> int:
    root = args.path or resolve_project_root(__file__)

    fmt = args.format
    if args.json:
        fmt = "json"

    spec_dir_arg = Path(args.spec_dir)
    if not spec_dir_arg.is_absolute():
        spec_dir_arg = root / spec_dir_arg

    if args.check_all:
        spec_dirs = _find_spec_dirs(spec_dir_arg, True)
        if not spec_dirs:
            spec_dirs = discover_spec_dirs(root)
    else:
        if (spec_dir_arg / "spec.md").exists():
            spec_dirs = [spec_dir_arg]
        else:
            spec_dirs = discover_spec_dirs(root)

    if not spec_dirs:
        if fmt == "json":
            print(json.dumps({
                "spec_dir": args.spec_dir, "score": 0,
                "errors": [{"type": "not_found", "name": args.spec_dir, "message": "未找到 spec 目录或 spec.md 文件"}],
                "warnings": [],
            }, ensure_ascii=False, indent=2))
            return 2
        else:
            print(f"错误: 未找到 spec 目录或 spec.md 文件: {args.spec_dir}", file=sys.stderr)
            return 2

    results = []
    for sd in spec_dirs:
        spec_path = str(sd / "spec.md")
        if args.verbose:
            print(f"\n正在检查: {spec_path}")
        results.append(_check_spec_file(spec_path, args.verbose))

    if fmt == "json":
        data = results[0].to_dict() if len(results) == 1 else [r.to_dict() for r in results]
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif fmt == "yaml":
        try:
            import yaml
            data = results[0].to_dict() if len(results) == 1 else [r.to_dict() for r in results]
            print(yaml.dump(data, allow_unicode=True, default_flow_style=False))
        except ImportError:
            print("错误: 需要 PyYAML 库支持 YAML 输出，请安装: pip install pyyaml", file=sys.stderr)
            return 2
    else:
        if len(results) == 1:
            print_format_result_text(results[0], args.verbose)
        else:
            print_format_summary_text(results)
            for r in results:
                print_format_result_text(r, args.verbose)

    return 1 if any(r.errors for r in results) else 0


# ============================================================
# gen-tests 子命令：测试骨架生成
# ============================================================

_REQ_SEC_RE = re.compile(r"^##\s+(ADDED|MODIFIED|REMOVED)\s+Requirements?", re.IGNORECASE)
_REQ_HDR_RE = re.compile(r"^###\s+Requirement:\s+(.+)")
_SCN_HDR_RE = re.compile(r"^####\s+Scenario:\s+(.+)")


def _parse_requirements(spec_text: str) -> list[dict]:
    requirements = []
    cur_section = "UNKNOWN"
    cur_name = ""
    cur_scenarios: list[str] = []

    def flush():
        nonlocal cur_name
        if cur_name:
            requirements.append({"name": cur_name, "section": cur_section, "scenarios": list(cur_scenarios)})
            cur_name = ""
            cur_scenarios.clear()

    for line in spec_text.splitlines():
        s = line.strip()
        m = _REQ_SEC_RE.match(s)
        if m:
            flush()
            cur_section = m.group(1).upper()
            continue
        m = _REQ_HDR_RE.match(s)
        if m:
            flush()
            cur_name = m.group(1).strip()
            continue
        m = _SCN_HDR_RE.match(s)
        if m:
            cur_scenarios.append(m.group(1).strip())

    flush()
    return requirements


def _to_test_name(req_name: str) -> str:
    keywords = re.findall(r"[\u4e00-\u9fa5]{2,}|[a-zA-Z]{2,}", req_name)
    if not keywords:
        san = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fa5_]", "_", req_name)
        return f"test_{san[:50]}"
    short = "_".join(keywords[:4])
    return f"test_{short[:50]}"


def _sanitize_class_name(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fa5]", "", name)
    return (cleaned[:30] if cleaned else "TestRequirement")


def _format_docstring(req: dict, indent: str = "    ") -> str:
    lines = [f'{indent}"""{req["name"]}', f"{indent}"]
    if req["scenarios"]:
        lines.append(f"{indent}验收场景：")
        for s in req["scenarios"]:
            lines.append(f"{indent}  - {s}")
    lines.append(f'{indent}"""')
    return "\n".join(lines)


def _generate_test_file(requirements: list[dict], spec_id: str, indent: str = "    ") -> str:
    lines = [
        f'"""自动生成的测试骨架',
        f"",
        f"来源：.trae/specs/{spec_id}/spec.md",
        f"生成工具：.agents/scripts/spec-tool.py gen-tests",
        f"",
        f"注意：本文件为骨架代码，每个测试函数内部的断言需根据",
        f"实际业务逻辑手动填写。Scenario 注释提供了验收场景指引。",
        f'"""',
        f"",
        f"import pytest",
        f"",
        f"",
    ]
    if not requirements:
        lines.append("# 无 Requirement 定义，跳过测试类生成")
        lines.append("")
        return "\n".join(lines)

    cls = f"Test{_sanitize_class_name(spec_id.replace('-', '_'))}"
    lines.append(f"class {cls}:")
    lines.append(f'{indent}"""对应 spec: {spec_id}"""')
    lines.append("")
    for req in requirements:
        tn = _to_test_name(req["name"])
        lines.append(f"{indent}def {tn}(self):")
        lines.append(_format_docstring(req, indent * 2))
        lines.append(f"{indent}{indent}# TODO: 根据验收场景编写具体测试逻辑")
        lines.append(f"{indent}{indent}# Requirement 来自 {req['section']} 章节")
        lines.append(f"{indent}{indent}pass")
        lines.append("")
    return "\n".join(lines)


def _gen_for_spec(spec_dir: Path, output_path: Path | None, dry_run: bool) -> int:
    spec_file = spec_dir / "spec.md"
    if not spec_file.exists():
        print_warn(f"跳过 {spec_dir.name}: 缺少 spec.md")
        return 0
    text = spec_file.read_text(encoding="utf-8")
    reqs = _parse_requirements(text)
    if not reqs:
        print_warn(f"跳过 {spec_dir.name}: 无 Requirement 定义")
        return 0

    code = _generate_test_file(reqs, spec_dir.name)
    if dry_run or output_path is None:
        print(code)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(code, encoding="utf-8")
        print_pass(f"{spec_dir.name} → {output_path} ({len(reqs)} 个 Requirement)")
    return len(reqs)


def cmd_gen_tests(args) -> int:
    root = args.path or resolve_project_root(__file__)

    if args.spec:
        spec_dir = Path(args.spec)
        if not spec_dir.is_absolute():
            spec_dir = root / args.spec
        out = None
        if args.output:
            out = Path(args.output)
        elif not args.dry_run:
            out = spec_dir / "tests" / f"test_{spec_dir.name}.py"
        _gen_for_spec(spec_dir, out, args.dry_run)
        return 0

    spec_dirs = discover_spec_dirs(root)
    if not spec_dirs:
        print_warn("未找到任何 spec 目录")
        return 0

    out_dir = Path(args.output_dir) if args.output_dir else (root / "tests" / "generated")
    total = 0

    print_header("测试骨架生成")
    print(f"输出目录: {out_dir}")
    print()

    for sd in spec_dirs:
        out_path = out_dir / f"test_{sd.name}.py"
        n = _gen_for_spec(sd, out_path, args.dry_run)
        total += n

    print()
    print_summary(total, 0, 0)
    return 0


# ============================================================
# CLI 入口
# ============================================================

def add_common_args(sp):
    sp.add_argument('--path', type=Path, default=None, help='项目根目录路径（默认自动解析）')
    sp.add_argument('--json', action='store_true', default=False, help='以 JSON 格式输出结果')


def main():
    setup_safe_output()
    parser = argparse.ArgumentParser(description='Spec 文档工具集')
    subparsers = parser.add_subparsers(dest='command', help='可用子命令')

    p_check = subparsers.add_parser('check', help='规格文档一致性检查')
    add_common_args(p_check)
    p_check.add_argument('--spec-dir', type=str, default=None, help='指定要检查的 spec 目录')
    p_check.add_argument('--all', action='store_true', default=False, help='扫描所有 spec 目录（默认行为）')
    p_check.add_argument('--match-threshold', type=int, default=SPEC_MATCH_THRESHOLD, help='语义匹配最少共同关键词数')

    p_fmt = subparsers.add_parser('format', help='Spec 文档标准化格式检查')
    add_common_args(p_fmt)
    p_fmt.add_argument('--spec-dir', type=str, default='.trae/specs/', help='spec 基目录（默认: .trae/specs/）')
    p_fmt.add_argument('--check-all', action='store_true', help='递归检查所有子目录')
    p_fmt.add_argument('--format', choices=['text', 'json', 'yaml'], default='text', help='输出格式（默认: text）')
    p_fmt.add_argument('--verbose', '-v', action='store_true', help='显示详细输出')

    p_gt = subparsers.add_parser('gen-tests', help='从 spec.md 生成 pytest 测试骨架')
    add_common_args(p_gt)
    g = p_gt.add_mutually_exclusive_group()
    g.add_argument('--spec', type=str, help='单个 spec 目录路径')
    g.add_argument('--all', action='store_true', help='扫描所有 spec 目录')
    p_gt.add_argument('--output', type=str, default=None, help='输出文件路径（单文件模式）')
    p_gt.add_argument('--output-dir', type=str, default=None, help='输出目录（--all 模式）')
    p_gt.add_argument('--dry-run', action='store_true', help='仅打印生成内容，不写入文件')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1

    cmd_map = {'check': cmd_check, 'format': cmd_format, 'gen-tests': cmd_gen_tests}
    return cmd_map[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
