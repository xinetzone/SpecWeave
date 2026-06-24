#!/usr/bin/env python3
"""复盘报告归类验证：检查 reports/ 根目录下是否存在未归类的报告。

扫描 `docs/retrospective/reports/` 目录，检测两类违规：
  1. 直接放置在 reports/ 根目录下的报告子目录（应归入分类子目录）
  2. 直接放置在 reports/ 根目录下的独立 .md 文件（README.md 除外）

用法：
  python check-report-categorization.py
  python check-report-categorization.py --json   # JSON 格式输出
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from lib.project import resolve_project_root
from lib.cli import print_pass, print_warn, print_error, print_header, print_summary

# ── 已知分类目录 ──────────────────────────────────────────────

KNOWN_CATEGORIES = {
    "atomization",
    "competitive-analysis",
    "insight-extraction",
    "project-governance",
    "roles-teams",
    "spec-system",
}

REPORTS_DIR_NAME = "docs/retrospective/reports"
INDEX_FILE = "README.md"


def scan_reports_dir(reports_dir: Path) -> tuple[list[str], list[str]]:
    """扫描 reports/ 根目录，分离已知分类与疑似违规项。

    Returns:
        (known_dirs, violations): 已知分类目录名列表、违规项路径列表（相对路径）。
    """
    if not reports_dir.exists():
        return [], []

    known: list[str] = []
    violations: list[str] = []

    for entry in sorted(reports_dir.iterdir()):
        rel = str(entry.relative_to(reports_dir.resolve().parent.parent))

        if entry.is_dir():
            if entry.name in KNOWN_CATEGORIES:
                known.append(entry.name)
            elif not entry.name.startswith("."):
                violations.append(rel)
        elif entry.is_file() and entry.suffix == ".md":
            if entry.name != INDEX_FILE and not entry.name.startswith("."):
                violations.append(rel)

    return known, violations


def main() -> None:
    parser = argparse.ArgumentParser(
        description="复盘报告归类验证：检查 reports/ 根目录下是否存在未归类的报告"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="以 JSON 格式输出结果",
    )
    args = parser.parse_args()

    root_dir = resolve_project_root(__file__)
    reports_dir = root_dir / REPORTS_DIR_NAME

    known, violations = scan_reports_dir(reports_dir)

    # ── JSON 输出 ──────────────────────────────────────────
    if args.json:
        result = {
            "reports_dir": str(reports_dir),
            "known_categories": known,
            "missing_categories": sorted(KNOWN_CATEGORIES - set(known)),
            "violations": violations,
            "violation_count": len(violations),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # ── 终端输出 ────────────────────────────────────────────
    print_header("复盘报告归类验证")
    print(f"  扫描目录: {reports_dir}")
    print(f"  已注册分类 ({len(KNOWN_CATEGORIES)} 个): {', '.join(sorted(KNOWN_CATEGORIES))}")
    print()

    # 检查缺失的分类目录
    missing = KNOWN_CATEGORIES - set(known)
    if missing:
        for cat in sorted(missing):
            print_warn(f"分类目录不存在: {cat}/")

    # 检查已注册但为空的分类目录
    for cat in sorted(known):
        cat_dir = reports_dir / cat
        sub_items = [e for e in cat_dir.iterdir() if not e.name.startswith(".")]
        if not sub_items:
            print_warn(f"分类目录为空: {cat}/")

    # 违规项
    if violations:
        print()
        for v in violations:
            print_error(f"未归类报告: {v}")
    else:
        print()
        print_pass("所有报告均已正确归入分类子目录")

    # 摘要
    print()
    print_summary(
        pass_count=0 if violations else 1,
        warn_count=len(missing) if missing else 0,
        error_count=len(violations),
    )

    if violations:
        print()
        print("修复指引：")
        print("  1. 对照 docs/retrospective/reports/README.md「一、分类标准」确定归属分类")
        print("  2. 将报告目录移入对应分类子目录")
        print("  3. 在 README.md 中更新索引（第二节 + 四.1 + 四.2）")
        print("  4. 重新运行本脚本验证")

    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
