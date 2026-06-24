#!/usr/bin/env python3
"""模式成熟度偏差扫描：检查 patterns/ 中所有模式文件的成熟度与验证次数是否一致。

根据 auto-generate-threshold 模式定义的阈值规则：
  validation_count >= 2 且 maturity = "L1" → 应升级至 L2

扫描结果输出：
  - --json: 以 JSON 格式输出应升级的模式列表（供自动化流水线消费）
  - 默认：以人类可读格式输出扫描报告

用法：
  python scan-maturity-upgrades.py
  python scan-maturity-upgrades.py --json
  python scan-maturity-upgrades.py --all  # 输出所有模式的状态摘要
"""

import argparse
import json
import sys
from pathlib import Path

from lib.project import resolve_project_root
from lib.frontmatter import parse_toml_frontmatter, extract_frontmatter_field
from lib.cli import (
    print_pass,
    print_warn,
    print_error,
    print_header,
    print_summary,
    add_common_args,
)

# 模式文件目录
PATTERNS_DIR = "docs/retrospective/patterns"

# 成熟度等级顺序
MATURITY_ORDER = {"L1": 0, "L2": 1, "L3": 2, "L4": 3}

# 排除的 README 文件名
EXCLUDED_FILENAMES = {"README.md"}


def scan_patterns(patterns_dir: Path) -> list[dict]:
    """扫描 patterns/ 目录，返回每个模式文件的核心字段。

    Returns:
        [{file, id, maturity, validation_count, reuse_count}, ...]
    """
    results = []
    for md_file in sorted(patterns_dir.rglob("*.md")):
        if md_file.name in EXCLUDED_FILENAMES:
            continue

        fm = parse_toml_frontmatter(md_file)
        if fm is None:
            print_warn(f"无 frontmatter: {md_file.relative_to(patterns_dir)}")
            continue

        maturity = extract_frontmatter_field(fm, "maturity") or "unknown"
        vc_raw = extract_frontmatter_field(fm, "validation_count")
        rc_raw = extract_frontmatter_field(fm, "reuse_count")

        try:
            validation_count = int(vc_raw) if vc_raw else 0
        except ValueError:
            validation_count = 0

        try:
            reuse_count = int(rc_raw) if rc_raw else 0
        except ValueError:
            reuse_count = 0

        results.append({
            "file": str(md_file.relative_to(patterns_dir.parent)),
            "id": extract_frontmatter_field(fm, "id") or "",
            "maturity": maturity,
            "validation_count": validation_count,
            "reuse_count": reuse_count,
        })

    return results


def classify(pattern: dict) -> str:
    """根据 auto-generate-threshold 规则分类单个模式的状态。

    Returns:
        "upgrade": 应升级（validation_count >= 2 且 maturity = L1）
        "ok": 状态一致
        "anomaly": 异常（validation_count = 1 但 maturity >= L2）
    """
    vc = pattern["validation_count"]
    maturity = pattern["maturity"]

    if vc >= 2 and maturity == "L1":
        return "upgrade"
    elif vc == 1 and maturity in ("L2", "L3", "L4"):
        return "anomaly"
    else:
        return "ok"


def build_stats(patterns: list[dict]) -> dict:
    """构建统计摘要。"""
    total = len(patterns)
    maturity_counts = {}
    validation_total = 0
    upgrades = []
    anomalies = []

    for p in patterns:
        m = p["maturity"]
        maturity_counts[m] = maturity_counts.get(m, 0) + 1
        validation_total += p["validation_count"]

        status = classify(p)
        if status == "upgrade":
            upgrades.append(p)
        elif status == "anomaly":
            anomalies.append(p)

    return {
        "total": total,
        "maturity_counts": maturity_counts,
        "validation_total": validation_total,
        "avg_validation": round(validation_total / total, 1) if total > 0 else 0,
        "upgrades": upgrades,
        "anomalies": anomalies,
    }


def print_report(patterns: list[dict], stats: dict):
    """打印人类可读的扫描报告。"""
    print_header("模式成熟度偏差扫描报告", width=70)

    # 概览统计
    print(f"\n  总模式数:        {stats['total']}")
    print(f"  累计验证次数:    {stats['validation_total']} 次")
    print(f"  平均验证次数:    {stats['avg_validation']} 次/模式")
    print(f"\n  成熟度分布:")
    for level in ("L1", "L2", "L3", "L4"):
        count = stats["maturity_counts"].get(level, 0)
        pct = round(count / stats["total"] * 100, 1) if stats["total"] > 0 else 0
        bar = "█" * max(1, int(pct / 5))
        print(f"    {level}: {count:>2} 个 ({pct:>5.1f}%) {bar}")

    # 应升级的模式
    if stats["upgrades"]:
        print(f"\n  ⚠ 应升级的模式（validation_count ≥ 2 但 maturity = L1）: {len(stats['upgrades'])} 个")
        print(f"  {'─' * 60}")
        for p in stats["upgrades"]:
            domain = "架构" if "architecture" in p["file"] else ("代码" if "code" in p["file"] else "方法论")
            print(f"    [{domain}] {p['id']}")
            print(f"           文件: {p['file']}")
            print(f"           当前: {p['maturity']}  |  验证次数: {p['validation_count']}  |  应升级至: L2")
            print()
    else:
        print(f"\n  ✓ 无需升级的模式")

    # 异常模式
    if stats["anomalies"]:
        print(f"\n  ✗ 异常模式（validation_count = 1 但 maturity ≥ L2）: {len(stats['anomalies'])} 个")
        print(f"  {'─' * 60}")
        for p in stats["anomalies"]:
            print(f"    {p['id']}: {p['file']}")
            print(f"         maturity={p['maturity']}, validation_count={p['validation_count']}")
            print()

    # 逐条详细列表（可选）
    print(f"\n  {'─' * 70}")
    print(f"  {'ID':<40} {'成熟度':>4} {'验证':>4} {'状态':>6}")
    print(f"  {'─' * 70}")
    for p in patterns:
        status = classify(p)
        status_icon = {"upgrade": "⚠ 升", "anomaly": "✗ 异", "ok": "✓"}[status]
        print(f"  {p['id']:<40} {p['maturity']:>4} {p['validation_count']:>4} {status_icon:>6}")

    print()

    # 最终摘要
    warn_count = len(stats["upgrades"])
    error_count = len(stats["anomalies"])
    pass_count = stats["total"] - warn_count - error_count

    print_summary(pass_count, warn_count, error_count, width=70)


def print_json_output(patterns: list[dict], stats: dict):
    """以 JSON 格式输出结果。"""
    output = {
        "stats": {
            "total": stats["total"],
            "validation_total": stats["validation_total"],
            "avg_validation": stats["avg_validation"],
            "maturity_counts": stats["maturity_counts"],
        },
        "upgrades": [
            {
                "id": p["id"],
                "file": p["file"],
                "current_maturity": p["maturity"],
                "validation_count": p["validation_count"],
                "suggested_maturity": "L2",
            }
            for p in stats["upgrades"]
        ],
        "anomalies": [
            {
                "id": p["id"],
                "file": p["file"],
                "maturity": p["maturity"],
                "validation_count": p["validation_count"],
            }
            for p in stats["anomalies"]
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def print_all_summary(patterns: list[dict], stats: dict):
    """打印所有模式的状态一览（--all 模式）。"""
    print_header("全量模式成熟度一览", width=80)

    # 按类别分组
    by_category = {
        "methodology": [],
        "architecture": [],
        "code": [],
        "other": [],
    }
    for p in patterns:
        if "architecture" in p["file"]:
            by_category["architecture"].append(p)
        elif "code" in p["file"]:
            by_category["code"].append(p)
        elif "methodology" in p["file"]:
            by_category["methodology"].append(p)
        else:
            by_category["other"].append(p)

    category_labels = {
        "methodology": "方法论模式",
        "architecture": "架构模式",
        "code": "代码模式",
        "other": "其他",
    }

    for cat, cat_patterns in by_category.items():
        if not cat_patterns:
            continue
        print(f"\n  {category_labels[cat]} ({len(cat_patterns)} 个)")
        print(f"  {'─' * 75}")
        print(f"  {'ID':<40} {'成熟度':>4} {'验证':>4} {'复用':>4} {'状态':>6}")
        print(f"  {'─' * 75}")
        for p in cat_patterns:
            status = classify(p)
            status_icon = {"upgrade": "⚠ 升", "anomaly": "✗ 异", "ok": "✓"}[status]
            print(f"  {p['id']:<40} {p['maturity']:>4} {p['validation_count']:>4} {p['reuse_count']:>4} {status_icon:>6}")
        print()

    # 最终统计
    print(f"\n  {'─' * 75}")
    print(f"  总计: {stats['total']} 个模式  |  L1: {stats['maturity_counts'].get('L1', 0)}  |  L2: {stats['maturity_counts'].get('L2', 0)}  |  L3: {stats['maturity_counts'].get('L3', 0)}  |  L4: {stats['maturity_counts'].get('L4', 0)}")
    print(f"  应升级: {len(stats['upgrades'])} 个  |  异常: {len(stats['anomalies'])} 个  |  平均验证次数: {stats['avg_validation']}")

    warn_count = len(stats["upgrades"])
    error_count = len(stats["anomalies"])
    pass_count = stats["total"] - warn_count - error_count
    print()
    print_summary(pass_count, warn_count, error_count, width=75)


def main():
    parser = argparse.ArgumentParser(
        description="模式成熟度偏差扫描：检查 validation_count 与 maturity 是否一致"
    )
    add_common_args(parser)
    parser.add_argument(
        "--all", "-a", action="store_true",
        help="输出所有模式的状态一览（按类别分组）",
    )
    args = parser.parse_args()

    root_dir = resolve_project_root(__file__)
    patterns_dir = root_dir / PATTERNS_DIR

    if not patterns_dir.exists():
        print_error(f"模式目录不存在: {patterns_dir}")
        sys.exit(1)

    patterns = scan_patterns(patterns_dir)
    stats = build_stats(patterns)

    if args.json:
        print_json_output(patterns, stats)
    elif args.all:
        print_all_summary(patterns, stats)
    else:
        print_report(patterns, stats)


if __name__ == "__main__":
    main()
