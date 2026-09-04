# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

import json
import sys
from pathlib import Path

from lib.cli import print_error, print_pass, print_warn
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
from .frontmatter_fixer import process_spec_file, process_spec_dir
from .metadata_checker import scan_spec_metadata, format_terminal_report


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

    # === 模式 1：frontmatter 自动修复 ===
    if getattr(args, "fix_frontmatter", False):
        return _cmd_fix_frontmatter(args, root, spec_dir_arg, fmt)

    # === 模式 2：原有格式检查 ===
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


def _cmd_fix_frontmatter(args, root: Path, spec_dir_arg: Path, fmt: str) -> int:
    """处理 --fix-frontmatter 模式：补全 frontmatter + 归一化 status."""
    # 确定扫描范围
    if (spec_dir_arg / "spec.md").exists():
        # 单个 spec 文件
        spec_files = [spec_dir_arg / "spec.md"]
    elif spec_dir_arg.exists():
        # 目录递归扫描
        spec_files = sorted(spec_dir_arg.rglob("spec.md"))
    else:
        print_error(f"spec 目录或文件不存在: {spec_dir_arg}")
        return 2

    if not spec_files:
        if fmt == "json":
            print(json.dumps({
                "total": 0, "added": 0, "status_added": 0, "normalized": 0,
                "skipped": 0, "error": 0, "results": [],
            }, ensure_ascii=False, indent=2))
        else:
            print_warn("未找到任何 spec.md 文件")
        return 0

    dry_run = getattr(args, "dry_run", False)
    default_status = getattr(args, "default_status", "draft")
    add_date = getattr(args, "add_date", False)

    # 批量处理（开启所有修复开关：补全缺失 + 归一化）
    results = []
    stats = {"added": 0, "would_add": 0, "status_added": 0, "would_add_status": 0,
             "normalized": 0, "would_normalize": 0, "skipped": 0, "error": 0}

    for sf in spec_files:
        r = process_spec_file(
            sf,
            default_status=default_status,
            add_date=add_date,
            fix_missing_status=True,
            normalize_status=True,
            dry_run=dry_run,
        )
        results.append(r)
        action = r["action"]
        if action in stats:
            stats[action] += 1

    if fmt == "json":
        report = {
            "total": len(spec_files),
            "dry_run": dry_run,
            "default_status": default_status,
            "add_date": add_date,
            "stats": stats,
            "results": results,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_fix_report(stats, results, dry_run)

    return 1 if stats["error"] > 0 else 0


def _print_fix_report(stats: dict, results: list, dry_run: bool) -> None:
    """打印 frontmatter 修复的终端报告。"""
    sep = "=" * 60
    print(sep)
    print(f"Spec Frontmatter 批量修复{'（预览模式）' if dry_run else ''}")
    print(sep)
    print(f"  总计 spec.md: {sum(stats.values())} 个")
    if dry_run:
        print(f"  将新增 frontmatter: {stats['would_add']} 个")
        print(f"  将补全 status: {stats['would_add_status']} 个")
        print(f"  将归一化 status: {stats['would_normalize']} 个")
    else:
        print(f"  已新增 frontmatter: {stats['added']} 个")
        print(f"  已补全 status: {stats['status_added']} 个")
        print(f"  已归一化 status: {stats['normalized']} 个")
    print(f"  跳过: {stats['skipped']} 个")
    print(f"  错误: {stats['error']} 个")
    print()

    # 打印错误
    errors = [r for r in results if r["action"] == "error"]
    if errors:
        print("-- 错误详情 --")
        for r in errors[:10]:
            print(f"  [E] {r['file']}: {r['reason']}")
        if len(errors) > 10:
            print(f"  ... 还有 {len(errors) - 10} 个")
        print()

    total_changed = (
        stats["would_add"] + stats["would_add_status"] + stats["would_normalize"]
        if dry_run
        else stats["added"] + stats["status_added"] + stats["normalized"]
    )
    if stats["error"] == 0:
        if dry_run:
            print_pass(f"预览完成，{total_changed} 个文件将被修改")
        else:
            print_pass(f"完成，{total_changed} 个文件已修改")
    else:
        print_warn("完成，但有部分文件出错")
    print(sep)

