#!/usr/bin/env python3
"""原子化后内容一致性检查：检测源文件中是否残留已提取至模式文件的深度分析内容。

检查项：
  1. Mermaid 流程图 — 模式文件与源文件是否同时包含相同的 mermaid 图
  2. 对比/维度表格 — 模式文件与源文件是否同时包含结构相同的表格
  3. 代码示例 — 模式文件与源文件是否同时包含相同的代码块
  4. "一句话总结" — 模式文件与源文件是否同时包含引用块形式的一句话总结
  5. 成熟度统计验证 — grep 所有模式文件的 maturity 字段，与 README 统计表对比（--verify-stats）

输出：疑似重复内容清单，包括位置和重复类型。

用法：
  python check-atomization-duplication.py <源文件路径> [模式文件路径 ...]
  python check-atomization-duplication.py execution-s1-s3.md package-structure-leverage.md
  python check-atomization-duplication.py --batch execution-s1-s3.md  # 从溯源链接自动解析模式文件
  python check-atomization-duplication.py --verify-stats .           # 成熟度统计一致性验证
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

from lib.project import resolve_project_root
from lib.cli import print_pass, print_warn, print_header
from lib.frontmatter import parse_toml_frontmatter, extract_frontmatter_field

# 匹配溯源链接
ATOMIZED_LINK_RE = re.compile(
    r"已原子化至.*?\[([^\]]+\.md)\]\(([^)]+)\)", re.MULTILINE
)
EXISTING_COVERAGE_RE = re.compile(
    r"已有模式覆盖.*?\[([^\]]+\.md)\]\(([^)]+)\)", re.MULTILINE
)

# 提取内容块的正则
MERMAID_BLOCK_RE = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)
CODE_BLOCK_RE = re.compile(r"```(?:python|bash|toml|yaml)?\n(.*?)```", re.DOTALL)
TABLE_RE = re.compile(r"^\|.+\|$", re.MULTILINE)
QUOTE_BLOCK_RE = re.compile(r"^> \*\*(.+?)\*\*", re.MULTILINE)


README_STATS_TABLE_RE = re.compile(
    r"^\|\s*\**([\w/-]+?)\**\s*\|\s*\**(\d+)\**\s*\|\s*\**(\d+)\**\s*\|\s*\**(\d+)\**\s*\|\s*\**(\d+)\**\s*\|\s*\**(\d+)\**\s*\|",
    re.MULTILINE,
)


def find_referenced_patterns(source_path: Path) -> list[Path]:
    """从源文件的溯源链接中解析引用的模式文件路径。"""
    content = source_path.read_text(encoding="utf-8")
    patterns = []

    for match in ATOMIZED_LINK_RE.finditer(content):
        ref_path = match.group(2)
        patterns.append(ref_path)

    for match in EXISTING_COVERAGE_RE.finditer(content):
        ref_path = match.group(2)
        patterns.append(ref_path)

    return patterns


def extract_signatures(content: str) -> dict:
    """提取文件内容的各类结构签名。"""
    return {
        "mermaid_count": len(MERMAID_BLOCK_RE.findall(content)),
        "code_blocks": [b.strip()[:80] for b in CODE_BLOCK_RE.findall(content)],
        "table_lines": len(TABLE_RE.findall(content)),
        "quote_summaries": [m.group(1)[:60] for m in QUOTE_BLOCK_RE.finditer(content)],
    }


def check_duplication(
    source: Path, pattern_refs: list[str], root_dir: Path
) -> list[dict]:
    """
    逐项检查源文件与模式文件之间的内容重复。

    返回: [{"type": "...", "source_line": N, "pattern": "..."}, ...]
    """
    source_content = source.read_text(encoding="utf-8")
    source_sig = extract_signatures(source_content)
    findings = []

    for ref in pattern_refs:
        # 解析相对路径
        pattern_path = root_dir / ref
        if not pattern_path.exists():
            # 路径可能是从报告目录的相对路径
            alt_path = source.parent / ref
            if alt_path.exists():
                pattern_path = alt_path.resolve()
            else:
                print_warn(f"  模式文件不存在: {ref}")
                continue

        pattern_content = pattern_path.read_text(encoding="utf-8")
        pattern_sig = extract_signatures(pattern_content)

        # 检查 1：Mermaid 图重复
        if source_sig["mermaid_count"] > 0 and pattern_sig["mermaid_count"] > 0:
            source_mermaids = set(MERMAID_BLOCK_RE.findall(source_content))
            pattern_mermaids = set(MERMAID_BLOCK_RE.findall(pattern_content))
            overlap = source_mermaids & pattern_mermaids
            if overlap:
                for m in overlap:
                    # 找到源文件中的行号
                    first_line = m.strip().split("\n")[0][:60]
                    findings.append({
                        "type": "Mermaid 图重复",
                        "detail": first_line,
                        "source": str(source.relative_to(root_dir)),
                        "pattern": str(pattern_path.relative_to(root_dir)),
                    })

        # 检查 2：代码块重复（取前 80 字符比较）
        if source_sig["code_blocks"] and pattern_sig["code_blocks"]:
            overlap = set(source_sig["code_blocks"]) & set(pattern_sig["code_blocks"])
            if overlap:
                for code in overlap:
                    findings.append({
                        "type": "代码块重复",
                        "detail": code[:60],
                        "source": str(source.relative_to(root_dir)),
                        "pattern": str(pattern_path.relative_to(root_dir)),
                    })

        # 检查 3：表格密集度异常
        if source_sig["table_lines"] > 15 and pattern_sig["table_lines"] > 15:
            findings.append({
                "type": "表格密集度异常（可能重复）",
                "detail": f"源文件 {source_sig['table_lines']} 行表格 vs 模式 {pattern_sig['table_lines']} 行表格",
                "source": str(source.relative_to(root_dir)),
                "pattern": str(pattern_path.relative_to(root_dir)),
            })

        # 检查 4：一句话总结重复
        if source_sig["quote_summaries"] and pattern_sig["quote_summaries"]:
            overlap = set(source_sig["quote_summaries"]) & set(pattern_sig["quote_summaries"])
            if overlap:
                for q in overlap:
                    findings.append({
                        "type": "一句话总结重复",
                        "detail": q,
                        "source": str(source.relative_to(root_dir)),
                        "pattern": str(pattern_path.relative_to(root_dir)),
                    })

    return findings


def grep_maturity_per_directory(patterns_root: Path) -> dict[str, dict[str, int]]:
    """遍历模式目录，从各文件 frontmatter 中 grep maturity 字段并按目录汇总。

    返回: {
        "architecture-patterns": {"L1": 1, "L2": 5, "L3": 0, "L4": 0},
        "code-patterns": {"L1": 1, "L2": 5, "L3": 0, "L4": 0},
        "methodology-patterns": {"L1": 17, "L2": 16, "L3": 1, "L4": 0},
    }
    """
    dir_maturity: dict[str, dict[str, int]] = {}
    pattern_dirs = ["architecture-patterns", "code-patterns", "methodology-patterns"]

    for dir_name in pattern_dirs:
        dir_path = patterns_root / dir_name
        if not dir_path.is_dir():
            continue

        counts: dict[str, int] = {f"L{i}": 0 for i in range(1, 5)}
        pattern_count = 0

        for md_file in sorted(dir_path.glob("*.md")):
            if md_file.name == "README.md":
                continue
            fm = parse_toml_frontmatter(md_file)
            if not fm:
                continue
            level = extract_frontmatter_field(fm, "maturity")
            if level in counts:
                counts[level] += 1
                pattern_count += 1

        counts["_total"] = pattern_count
        dir_maturity[dir_name] = counts

    return dir_maturity


def parse_readme_stats(readme_path: Path) -> dict[str, dict[str, int]]:
    """从 patterns/README.md 统计表中解析报告的各类数据。

    返回格式与 grep_maturity_per_directory() 一致。
    """
    content = readme_path.read_text(encoding="utf-8")
    dir_stats: dict[str, dict[str, int]] = {}

    for match in README_STATS_TABLE_RE.finditer(content):
        dir_name = match.group(1).strip().rstrip("/")
        # 跳过合计行
        if "合计" in dir_name:
            continue
        total = int(match.group(2))
        l1 = int(match.group(3))
        l2 = int(match.group(4))
        l3 = int(match.group(5))
        l4 = int(match.group(6))

        dir_stats[dir_name] = {
            "L1": l1,
            "L2": l2,
            "L3": l3,
            "L4": l4,
            "_total": total,
        }

    return dir_stats


def check_stats_consistency(patterns_root: Path, readme_path: Path) -> list[dict]:
    """比较 grep 统计与 README 统计表的差异。

    返回: [{"directory": "...", "field": "L1", "grep": 17, "readme": 15}, ...]
    """
    grep_stats = grep_maturity_per_directory(patterns_root)
    readme_stats = parse_readme_stats(readme_path)
    discrepancies = []

    for dir_name in grep_stats:
        grep_data = grep_stats[dir_name]
        readme_data = readme_stats.get(
            dir_name,
            {"L1": 0, "L2": 0, "L3": 0, "L4": 0, "_total": 0},
        )

        for field in ["L1", "L2", "L3", "L4"]:
            g = grep_data.get(field, 0)
            r = readme_data.get(field, 0)
            if g != r:
                discrepancies.append({
                    "directory": dir_name,
                    "field": field,
                    "grep": g,
                    "readme": r,
                    "diff": g - r,
                })

        # 检查总模式数
        g_total = grep_data.get("_total", 0)
        r_total = readme_data.get("_total", 0)
        if g_total != r_total:
            discrepancies.append({
                "directory": dir_name,
                "field": "总计",
                "grep": g_total,
                "readme": r_total,
                "diff": g_total - r_total,
            })

    return discrepancies


def main():
    parser = argparse.ArgumentParser(description="原子化后内容一致性检查")
    parser.add_argument("source", help="源文件路径")
    parser.add_argument(
        "patterns",
        nargs="*",
        help="模式文件路径（可选，不提供则从溯源链接自动解析）",
    )
    parser.add_argument(
        "--batch",
        "-b",
        action="store_true",
        help="批量模式：从源文件的溯源链接自动解析模式文件",
    )
    parser.add_argument(
        "--verify-stats",
        "-s",
        action="store_true",
        help="成熟度统计验证：grep 所有模式文件的 maturity 字段，与 README 统计表对比",
    )
    args = parser.parse_args()

    root_dir = resolve_project_root(__file__)
    source_path = Path(args.source)

    if not source_path.is_absolute():
        source_path = Path.cwd() / source_path
    source_path = source_path.resolve()

    # --verify-stats 模式：grep 全量 maturity vs README 统计表
    if args.verify_stats:
        patterns_root = root_dir / "docs" / "retrospective" / "patterns"
        readme_path = patterns_root / "README.md"

        if not readme_path.exists():
            print_warn(f"README 不存在: {readme_path}")
            sys.exit(1)

        print_header("成熟度统计一致性验证")
        discrepancies = check_stats_consistency(patterns_root, readme_path)

        if not discrepancies:
            print_pass("通过 — grep 成熟度分布与 README 统计表完全一致")
            # 打印当前分布供核查
            grep_stats = grep_maturity_per_directory(patterns_root)
            total_all = {"L1": 0, "L2": 0, "L3": 0, "L4": 0, "_total": 0}
            for dir_name, data in grep_stats.items():
                if dir_name == "合计":
                    continue
                print(f"  {dir_name}: L1={data['L1']} L2={data['L2']} L3={data['L3']} L4={data['L4']} (共 {data['_total']} 模式)")
                for k in total_all:
                    total_all[k] += data.get(k, 0)
            print(f"  合计: L1={total_all['L1']} L2={total_all['L2']} L3={total_all['L3']} L4={total_all['L4']} (共 {total_all['_total']} 模式)")
            return

        print_warn(f"发现 {len(discrepancies)} 处统计偏差:")
        for i, d in enumerate(discrepancies, 1):
            direction = "+" if d["diff"] > 0 else ""
            print(f"  [{i}] {d['directory']} {d['field']}: grep={d['grep']} README={d['readme']} (偏差 {direction}{d['diff']})")

        print(f"\n  建议：更新 patterns/README.md 统计表，或将 grep 结果同步到报告。")
        return

    if not source_path.exists():
        print_warn(f"源文件不存在: {source_path}")
        sys.exit(1)

    # 获取模式文件列表
    if args.patterns:
        pattern_refs = args.patterns
    else:
        pattern_refs = find_referenced_patterns(source_path)

    if not pattern_refs:
        if args.batch:
            print_pass("未找到溯源链接，无需检查")
            return
        print_warn("未提供模式文件，也未在源文件中找到溯源链接")
        sys.exit(1)

    print_header(f"原子化后内容一致性检查: {source_path.relative_to(root_dir)}")
    print(f"  引用模式: {', '.join(pattern_refs)}")

    findings = check_duplication(source_path, pattern_refs, root_dir)

    if not findings:
        print_pass("通过 — 未发现源文件与模式文件之间的内容重复")
        return

    print_warn(f"发现 {len(findings)} 处疑似重复内容:")
    for i, f in enumerate(findings, 1):
        print(f"  [{i}] {f['type']}: {f['detail'][:60]}")
        print(f"      源文件: {f['source']}")
        print(f"      模式文件: {f['pattern']}")

    print(f"\n  建议：将源文件中对应的深度分析内容降级为概要 + 引用链接。")


if __name__ == "__main__":
    main()
