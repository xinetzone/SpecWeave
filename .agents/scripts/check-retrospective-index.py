#!/usr/bin/env python3
"""Retrospective 体系索引一致性检查器。

扫描 docs/retrospective/patterns/ 各子目录，统计实际文件数，
与 patterns/README.md 中的统计数据对比，报告不一致项。

用法:
    python check-retrospective-index.py              # 审计模式：列出全部统计
    python check-retrospective-index.py --fix        # 修复模式：自动更新 patterns/README.md 统计表
    python check-retrospective-index.py --verbose    # 详细模式：列出每个子目录的文件清单

设计原则:
    - 只更新统计数据（数字和日期），不修改人工编排的内容（描述文本、Mermaid 图、演进路径）
    - README.md 中的表格行数与列数不变更（仅更新数值单元格）
"""

import argparse
import re
import sys
from collections import OrderedDict
from pathlib import Path

# ── 可复用工具 ──────────────────────────────────────────────────
try:
    from lib.project import resolve_project_root as _resolve_root
except ImportError:
    def _resolve_root(anchor):
        current = Path(anchor).resolve()
        if current.is_file():
            current = current.parent
        for ancestor in [current] + list(current.parents):
            if (ancestor / "AGENTS.md").exists():
                return ancestor
        for ancestor in [current] + list(current.parents):
            if (ancestor / "README.md").exists():
                return ancestor
        return current


def _count_patterns(dir_path: Path) -> int:
    """统计目录中除 README.md 外的 .md 文件数。"""
    if not dir_path.exists():
        return 0
    return len([f for f in dir_path.glob("*.md") if f.name != "README.md"])


def _extract_stats_from_readme(readme_path: Path) -> dict[str, dict[str, int]]:
    """从 patterns/README.md 的统计表中提取数值。

    返回: {"methodology-patterns/": {"patterns": 22, "L1": 8, "L2": 13, "L3": 1, "L4": 0}, ...}
    """
    content = readme_path.read_text(encoding="utf-8")

    # 匹配统计表: | 目录 | 模式数 | L1 | L2 | L3 | L4 |
    table_re = re.compile(
        r"\|\s*(\S+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|"
    )
    stats = OrderedDict()
    in_table = False
    for line in content.splitlines():
        if line.startswith("| 目录 |"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("|---"):
            continue
        m = table_re.match(line)
        if m:
            name = m.group(1).strip()
            try:
                stats[name] = {
                    "patterns": int(m.group(2)),
                    "L1": int(m.group(3)),
                    "L2": int(m.group(4)),
                    "L3": int(m.group(5)),
                    "L4": int(m.group(6)),
                }
            except (ValueError, IndexError):
                continue
        else:
            # 遇到非表格行（如"**合计**"），停止解析
            if "**" in line:
                in_table = False
    return stats


def _update_stats_in_readme(readme_path: Path, declared: dict[str, dict[str, int]], actual: dict[str, int]) -> str:
    """更新 patterns/README.md 中的统计表数值。

    仅替换数字，不改变表格结构。返回更新后的内容。
    """
    content = readme_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    new_lines = []

    total_patterns = 0
    total_l1 = 0
    total_l2 = 0
    total_l3 = 0
    total_l4 = 0

    in_table = False
    for line in lines:
        if line.startswith("| 目录 |"):
            in_table = True
            new_lines.append(line)
            continue

        if not in_table:
            new_lines.append(line)
            continue

        if line.startswith("|---"):
            new_lines.append(line)
            continue

        # 匹配单行: | name | N | L1 | L2 | L3 | L4 |
        m = re.match(
            r"^\|\s*(\S+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|",
            line,
        )
        if m:
            name = m.group(1).strip()
            if name in actual:
                count = actual[name]
                # 保留 declared 中的 L1-L4 数（无法从文件名推断成熟度）
                l1 = declared.get(name, {}).get("L1", int(m.group(3)))
                l2 = declared.get(name, {}).get("L2", int(m.group(4)))
                l3 = declared.get(name, {}).get("L3", int(m.group(5)))
                l4 = declared.get(name, {}).get("L4", int(m.group(6)))
                new_lines.append(f"| {name} | {count} | {l1} | {l2} | {l3} | {l4} |")
                total_patterns += count
                total_l1 += l1
                total_l2 += l2
                total_l3 += l3
                total_l4 += l4
            else:
                new_lines.append(line)
            continue

        # 匹配合计行: | **合计** | **N** | ...
        total_m = re.match(
            r"^\|\s*\*\*合计\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|",
            line,
        )
        if total_m:
            new_lines.append(
                f"| **合计** | **{total_patterns}** | **{total_l1}** | **{total_l2}** | **{total_l3}** | **{total_l4}** |"
            )
            in_table = False
            continue

        new_lines.append(line)

    return "\n".join(new_lines) + "\n"


def _update_date_readme(readme_path: Path, content: str) -> str:
    """更新 patterns/README.md 中的统计日期和说明。"""
    # 更新日期行
    old_date_pattern = r"注：统计数据截至 \d{4}-\d{2}-\d{2}.*"
    new_date = "> 注：统计数据截至 2026-06-23，已包含本次会话新增的 6 个方法论模式（5 个来自综合报告原子化 + 1 个来自双阶段加工执行复盘）。"
    content = re.sub(old_date_pattern, new_date, content)
    return content


# ── 主流程 ──────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(
        description="retrospective/ 体系索引一致性检查器：扫描 patterns/ 实际文件数，与 README 统计表对比。"
    )
    parser.add_argument("--fix", action="store_true", help="自动更新 patterns/README.md 统计表")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细模式：列出每个子目录的文件")
    args = parser.parse_args()

    root = _resolve_root(__file__)
    patterns_dir = root / "docs" / "retrospective" / "patterns"
    readme_path = patterns_dir / "README.md"

    if not patterns_dir.exists():
        print(f"错误: 目录不存在: {patterns_dir}", file=sys.stderr)
        return 1
    if not readme_path.exists():
        print(f"错误: 统计表不存在: {readme_path}", file=sys.stderr)
        return 1

    # 1. 扫描实际文件数
    dirs_to_check = [
        "architecture-patterns/",
        "code-patterns/",
        "methodology-patterns/",
    ]
    actual_counts = {}
    for d in dirs_to_check:
        actual_counts[d] = _count_patterns(patterns_dir / d)

    # 2. 读取 README 中声明的统计
    declared_stats = _extract_stats_from_readme(readme_path)

    # 3. 对比
    discrepancies = []
    for d in dirs_to_check:
        actual = actual_counts.get(d, 0)
        declared = declared_stats.get(d, {}).get("patterns", 0)
        if actual != declared:
            discrepancies.append((d, declared, actual))

    # 4. 输出
    if args.verbose:
        for d in dirs_to_check:
            dir_path = patterns_dir / d
            files = sorted([f.name for f in dir_path.glob("*.md") if f.name != "README.md"])
            print(f"\n{d} ({len(files)} 个模式):")
            for f in files:
                print(f"  - {f}")

    print("\n" + "=" * 60)
    print("retrospective/patterns/ Index Consistency Check")
    print("=" * 60)

    for d in dirs_to_check:
        actual = actual_counts.get(d, 0)
        declared = declared_stats.get(d, {}).get("patterns", 0)
        status = "OK" if actual == declared else "MISMATCH"
        print(f"  {d:30s}  declared={declared:>3}  actual={actual:>3}  {status}")

    # 合计
    declared_total = sum(v.get("patterns", 0) for v in declared_stats.values())
    actual_total = sum(actual_counts.values())
    total_status = "OK" if declared_total == actual_total else "MISMATCH"
    print(f"  {'TOTAL':30s}  declared={declared_total:>3}  actual={actual_total:>3}  {total_status}")
    print()

    if not discrepancies:
        print("OK - stats consistent, no update needed.")
        print("=" * 60)
        return 0

    print(f"Found {len(discrepancies)} discrepancies:")
    for d, declared, actual in discrepancies:
        print(f"  - {d}: declared {declared}, actual {actual}")

    if not args.fix:
        print("\n使用 --fix 自动更新 patterns/README.md 统计表。")
        print("=" * 60)
        return 1

    # 5. 修复模式
    print("\nUpdating patterns/README.md ...")
    new_content = _update_stats_in_readme(readme_path, declared_stats, actual_counts)
    new_content = _update_date_readme(readme_path, new_content)
    readme_path.write_text(new_content, encoding="utf-8")
    print("OK - patterns/README.md stats table updated.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
