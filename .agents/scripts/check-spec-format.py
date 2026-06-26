#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spec 文档标准化检查工具

检查 spec.md 文档是否符合标准格式规范，包括：
- 核心章节完整性
- Requirement 结构和 Scenario 完整性
- 验收标准可验证性
- 版本号与变更日志规范
"""

import argparse
import json
import os
import sys
from pathlib import Path

from lib.project import resolve_project_root
from lib.spec.models import Issue, SpecCheckResult
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


def check_spec_file(spec_path: str, verbose: bool = False) -> SpecCheckResult:
    """执行完整的 spec 文件检查。"""
    result = SpecCheckResult(spec_path=spec_path)

    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        result.errors.append({
            "type": "file_not_found",
            "name": spec_path,
            "message": f"文件不存在: {spec_path}",
        })
        return result
    except Exception as e:
        result.errors.append({
            "type": "read_error",
            "name": spec_path,
            "message": f"读取文件失败: {str(e)}",
        })
        return result

    all_issues = []

    if verbose:
        print(f"[检查中] 核心章节检测...")
    chapter_issues, found_chapters, _ = detect_core_chapters(content)
    all_issues.extend(chapter_issues)

    for chapter_name, pattern, _ in CORE_CHAPTERS:
        issue = check_chapter_not_empty(content, chapter_name, pattern)
        if issue:
            all_issues.append(issue)

    if verbose:
        print(f"[检查中] Requirement 完整性验证...")
    req_issues, requirements = detect_requirements(content)
    all_issues.extend(req_issues)

    if verbose:
        print(f"[检查中] 验收标准可验证性检查...")
    criteria_issues = check_acceptance_criteria(content)
    all_issues.extend(criteria_issues)

    if verbose:
        print(f"[检查中] 版本号与变更日志检测...")
    version_issues, _ = check_version_and_changelog(content)
    all_issues.extend(version_issues)

    result.errors = [{"type": i.type, "name": i.name, "message": i.message}
                    for i in all_issues if i.severity == "error"]
    result.warnings = [{"type": i.type, "name": i.name, "message": i.message}
                       for i in all_issues if i.severity == "warning"]

    result.score = calculate_score(all_issues, found_chapters, requirements)

    if verbose:
        print(f"[完成] 评分: {result.score}, 错误: {len(result.errors)}, 警告: {len(result.warnings)}")

    return result


def find_spec_directories(base_path: str, check_all: bool) -> list[str]:
    """查找要检查的 spec 目录。"""
    base = Path(base_path)
    if not base.exists():
        return []

    if check_all:
        spec_dirs = []
        for spec_file in base.rglob("spec.md"):
            spec_dirs.append(str(spec_file.parent))
        return spec_dirs
    else:
        if (base / "spec.md").exists():
            return [str(base)]
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Spec 文档标准化检查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python check-spec-format.py                                    # 检查默认目录
  python check-spec-format.py --spec-dir .trae/specs/XXX         # 指定目录
  python check-spec-format.py --check-all                        # 检查所有子目录
  python check-spec-format.py --format json --verbose            # JSON 输出格式
  python check-spec-format.py --check-all --format text          # 检查所有 spec 并文本输出
        """
    )

    parser.add_argument(
        "--spec-dir",
        type=str,
        default=".trae/specs/",
        help="指定要检查的 spec 目录路径 (默认: .trae/specs/)"
    )

    parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json", "yaml"],
        default="text",
        help="输出格式 (默认: text)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细输出"
    )

    parser.add_argument(
        "--check-all",
        action="store_true",
        help="递归检查指定目录下所有包含 spec.md 的子目录"
    )

    args = parser.parse_args()

    project_root = resolve_project_root(__file__)
    spec_dir_arg = args.spec_dir
    if not os.path.isabs(spec_dir_arg):
        spec_dir_arg = str(project_root / spec_dir_arg)

    spec_dirs = find_spec_directories(spec_dir_arg, args.check_all)

    if not spec_dirs:
        if args.format == "json":
            error_result = {
                "spec_dir": args.spec_dir,
                "score": 0,
                "errors": [{"type": "not_found", "name": args.spec_dir, "message": "未找到 spec 目录或 spec.md 文件"}],
                "warnings": []
            }
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
            sys.exit(2)
        else:
            print(f"错误: 未找到 spec 目录或 spec.md 文件: {args.spec_dir}", file=sys.stderr)
            sys.exit(2)

    results = []
    for spec_dir in spec_dirs:
        spec_path = os.path.join(spec_dir, "spec.md")
        if args.verbose:
            print(f"\n正在检查: {spec_path}")
        result = check_spec_file(spec_path, args.verbose)
        results.append(result)

    if args.format == "json":
        if len(results) == 1:
            print(json.dumps(results[0].to_dict(), ensure_ascii=False, indent=2))
        else:
            print(json.dumps([r.to_dict() for r in results], ensure_ascii=False, indent=2))
    elif args.format == "yaml":
        try:
            import yaml
            if len(results) == 1:
                print(yaml.dump(results[0].to_dict(), allow_unicode=True, default_flow_style=False))
            else:
                print(yaml.dump([r.to_dict() for r in results], allow_unicode=True, default_flow_style=False))
        except ImportError:
            print("错误: 需要 PyYAML 库支持 YAML 输出，请安装: pip install pyyaml", file=sys.stderr)
            sys.exit(2)
    else:
        if len(results) == 1:
            print_format_result_text(results[0], args.verbose)
        else:
            print_format_summary_text(results)
            for r in results:
                print_format_result_text(r, args.verbose)

    has_errors = any(r.errors for r in results)
    if has_errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
