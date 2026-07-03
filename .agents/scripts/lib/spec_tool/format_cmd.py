import json
import sys
from pathlib import Path

from lib.cli import print_error
from lib.project import resolve_project_root
from lib.spec import discover_spec_dirs
from lib.spec.models import SpecCheckResult
from lib.spec.utils import CORE_CHAPTERS, calculate_score
from lib.spec.format_checkers import (
    detect_core_chapters,
    check_chapter_not_empty,
    detect_requirements,
    check_acceptance_criteria,
    check_version_and_changelog,
)
from lib.spec.reporters import (
    print_format_result_text,
    print_format_summary_text,
)


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

    all_issues = []
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
