#!/usr/bin/env python3
"""Spec目录产出物归档检查：检测spec目录中是否存在未归档的产出物文件。

spec目录应仅包含过程性文件（spec.md/tasks.md/checklist.md），
分析报告、原文、任务产出等最终产物应归档到 docs/retrospective/reports/ 下。

扫描 `.trae/specs/` 下所有spec目录，检测：
  1. spec目录中是否存在产出物文件（analysis-report.md、article-content.md、task*-*.md等）
  2. 已标记完成的spec是否仍留存产出物文件

用法：
  python check-spec-output-archive.py
  python check-spec-output-archive.py --fix   # 输出修复建议
  python check-spec-output-archive.py --json  # JSON格式输出
"""

import argparse
import json
import re
import sys
from pathlib import Path

from lib.project import resolve_project_root
from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, add_common_args

SPECS_ROOT = ".trae/specs"

SPEC_ALLOWED_FILES = {
    "spec.md",
    "tasks.md",
    "checklist.md",
    "README.md",
    ".gitkeep",
}

OUTPUT_FILE_PATTERNS = [
    re.compile(r"analysis-report\.md$", re.IGNORECASE),
    re.compile(r"article-content\.md$", re.IGNORECASE),
    re.compile(r"cleaned-article\.md$", re.IGNORECASE),
    re.compile(r"task\d+[-_].+\.md$", re.IGNORECASE),
    re.compile(r".*-output\.md$", re.IGNORECASE),
    re.compile(r"prd-summary\.md$", re.IGNORECASE),
    re.compile(r".*-insights?\.md$", re.IGNORECASE),
    re.compile(r".*-analysis\.md$", re.IGNORECASE),
    re.compile(r"execution-retrospective\.md$", re.IGNORECASE),
    re.compile(r"comprehensive-insights\.md$", re.IGNORECASE),
    re.compile(r"core-insights\.md$", re.IGNORECASE),
    re.compile(r"critical-analysis\.md$", re.IGNORECASE),
    re.compile(r"learning-notes\.md$", re.IGNORECASE),
    re.compile(r"methodologies\.md$", re.IGNORECASE),
    re.compile(r"practical-recommendations\.md$", re.IGNORECASE),
    re.compile(r"success-factors\.md$", re.IGNORECASE),
    re.compile(r"specweave-comparison\.md$", re.IGNORECASE),
    re.compile(r"\d{2}-.+\.md$", re.IGNORECASE),
]

TASK_FILE_PATTERNS = [
    re.compile(r"^task\d+", re.IGNORECASE),
]


def is_output_file(filename: str) -> bool:
    for pattern in OUTPUT_FILE_PATTERNS:
        if pattern.search(filename):
            return True
    if filename.lower().endswith(".md") and filename.lower() not in {f.lower() for f in SPEC_ALLOWED_FILES}:
        if any(p.search(filename) for p in TASK_FILE_PATTERNS):
            return True
    return False


def is_spec_dir(path: Path) -> bool:
    return (path / "spec.md").exists() or (path / "tasks.md").exists()


def discover_spec_dirs(root: Path) -> list[Path]:
    specs_root = root / SPECS_ROOT
    if not specs_root.exists():
        return []
    spec_dirs = []
    for entry in sorted(specs_root.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        if is_spec_dir(entry):
            spec_dirs.append(entry)
        else:
            for sub in sorted(entry.iterdir()):
                if sub.is_dir() and not sub.name.startswith(".") and is_spec_dir(sub):
                    spec_dirs.append(sub)
    return spec_dirs


def is_spec_completed(spec_dir: Path) -> bool:
    tasks_file = spec_dir / "tasks.md"
    if not tasks_file.exists():
        return False
    content = tasks_file.read_text(encoding="utf-8", errors="ignore")
    pending_count = content.count("- [ ]")
    in_progress_count = content.count("- [/]")
    total_tasks = len(re.findall(r"^## \[.\] Task \d+:", content, re.MULTILINE))
    if total_tasks > 0 and pending_count == 0 and in_progress_count == 0:
        return True
    return "[x]" in content and pending_count == 0 and in_progress_count == 0


def scan_spec(spec_dir: Path, root: Path) -> dict:
    rel_path = str(spec_dir.relative_to(root))
    output_files = []
    allowed_files = []
    other_files = []

    for f in sorted(spec_dir.iterdir()):
        if f.name.startswith("."):
            continue
        if f.is_dir():
            other_files.append(f"{f.name}/")
            continue
        if f.name in SPEC_ALLOWED_FILES:
            allowed_files.append(f.name)
        elif is_output_file(f.name):
            output_files.append(f.name)
        elif f.suffix == ".md":
            output_files.append(f.name)
        else:
            other_files.append(f.name)

    completed = is_spec_completed(spec_dir)

    return {
        "path": rel_path,
        "name": spec_dir.name,
        "completed": completed,
        "allowed_files": allowed_files,
        "output_files": output_files,
        "other_files": other_files,
        "has_violations": len(output_files) > 0 or (completed and len(output_files) > 0),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Spec目录产出物归档检查：检测spec目录中未归档的产出物文件"
    )
    parser.add_argument("--fix", action="store_true", help="输出修复建议")
    add_common_args(parser)
    args = parser.parse_args()

    root_dir = resolve_project_root(__file__)
    spec_dirs = discover_spec_dirs(root_dir)

    results = []
    violations = []

    for sd in spec_dirs:
        result = scan_spec(sd, root_dir)
        results.append(result)
        if result["has_violations"]:
            violations.append(result)

    if args.json:
        output = {
            "specs_root": str(root_dir / SPECS_ROOT),
            "total_specs": len(results),
            "violation_count": len(violations),
            "allowed_files": sorted(SPEC_ALLOWED_FILES),
            "violations": [
                {
                    "path": v["path"],
                    "name": v["name"],
                    "completed": v["completed"],
                    "output_files": v["output_files"],
                    "other_files": v["other_files"],
                }
                for v in violations
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print_header("Spec目录产出物归档检查")
    print(f"  扫描根目录: {root_dir / SPECS_ROOT}")
    print(f"  允许文件: {', '.join(sorted(SPEC_ALLOWED_FILES))}")
    print(f"  扫描spec数量: {len(results)}")
    print()

    if violations:
        for v in violations:
            status = "✅已完成" if v["completed"] else "🔧进行中"
            print_error(f"{v['path']} ({status})")
            for of in v["output_files"]:
                print(f"    产出物文件: {of}")
            for of in v["other_files"]:
                print_warn(f"    非标准文件: {of}")
            print()
    else:
        print_pass("所有spec目录文件合规，产出物已正确归档")

    completed_with_output = [v for v in violations if v["completed"]]
    in_progress_with_output = [v for v in violations if not v["completed"]]

    print()
    if args.fix and violations:
        print("修复指引：")
        print()
        for v in completed_with_output:
            print(f"  【{v['name']}】(已完成，需归档)")
            print(f"    1. 在 docs/retrospective/reports/insight-extraction/external-learning/ 下创建归档目录")
            print(f"    2. 使用 git mv 将产出物移至归档目录")
            print(f"    3. 创建归档README.md（含frontmatter、核心指标、文件索引）")
            print(f"    4. 更新主题README.md中的交付物链接指向归档目录")
            print(f"    5. 验证spec目录仅保留spec.md/tasks.md/checklist.md")
            print()
        if in_progress_with_output:
            print(f"  注：{len(in_progress_with_output)}个进行中的spec包含产出物文件，")
            print(f"      这些在任务完成后也需要归档。")
            print()

    print_summary(
        pass_count=len(results) - len(violations),
        warn_count=len(in_progress_with_output),
        error_count=len(completed_with_output),
    )

    sys.exit(1 if completed_with_output else 0)


if __name__ == "__main__":
    main()
