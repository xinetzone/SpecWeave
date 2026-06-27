#!/usr/bin/env python3
"""原子化后内容一致性检查：检测源文件中是否残留已提取至模式文件的深度分析内容。

检查项：
  1. Mermaid 流程图 — 模式文件与源文件是否同时包含相同的 mermaid 图
  2. 对比/维度表格 — 模式文件与源文件是否同时包含结构相同的表格
  3. 代码示例 — 模式文件与源文件是否同时包含相同的代码块
  4. "一句话总结" — 模式文件与源文件是否同时包含引用块形式的一句话总结

注：成熟度统计验证功能已迁移至 pattern-maturity.py verify 子命令。

输出：疑似重复内容清单，包括位置和重复类型。

用法：
  python check-atomization-duplication.py <源文件路径> [模式文件路径 ...]
  python check-atomization-duplication.py execution-s1-s3.md package-structure-leverage.md
  python check-atomization-duplication.py --batch execution-s1-s3.md  # 从溯源链接自动解析模式文件
"""

import argparse
import re
import sys
from pathlib import Path

from lib.project import resolve_project_root
from lib.cli import print_pass, print_warn, print_header

ATOMIZED_LINK_RE = re.compile(
    r"已原子化至.*?\[([^\]]+\.md)\]\(([^)]+)\)", re.MULTILINE
)
EXISTING_COVERAGE_RE = re.compile(
    r"已有模式覆盖.*?\[([^\]]+\.md)\]\(([^)]+)\)", re.MULTILINE
)

MERMAID_BLOCK_RE = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)
CODE_BLOCK_RE = re.compile(r"```(?:python|bash|toml|yaml)?\n(.*?)```", re.DOTALL)
TABLE_RE = re.compile(r"^\|.+\|$", re.MULTILINE)
QUOTE_BLOCK_RE = re.compile(r"^> \*\*(.+?)\*\*", re.MULTILINE)


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
        pattern_path = root_dir / ref
        if not pattern_path.exists():
            alt_path = source.parent / ref
            if alt_path.exists():
                pattern_path = alt_path.resolve()
            else:
                print_warn(f"  模式文件不存在: {ref}")
                continue

        pattern_content = pattern_path.read_text(encoding="utf-8")
        pattern_sig = extract_signatures(pattern_content)

        if source_sig["mermaid_count"] > 0 and pattern_sig["mermaid_count"] > 0:
            source_mermaids = set(MERMAID_BLOCK_RE.findall(source_content))
            pattern_mermaids = set(MERMAID_BLOCK_RE.findall(pattern_content))
            overlap = source_mermaids & pattern_mermaids
            if overlap:
                for m in overlap:
                    first_line = m.strip().split("\n")[0][:60]
                    findings.append({
                        "type": "Mermaid 图重复",
                        "detail": first_line,
                        "source": str(source.relative_to(root_dir)),
                        "pattern": str(pattern_path.relative_to(root_dir)),
                    })

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

        if source_sig["table_lines"] > 15 and pattern_sig["table_lines"] > 15:
            findings.append({
                "type": "表格密集度异常（可能重复）",
                "detail": f"源文件 {source_sig['table_lines']} 行表格 vs 模式 {pattern_sig['table_lines']} 行表格",
                "source": str(source.relative_to(root_dir)),
                "pattern": str(pattern_path.relative_to(root_dir)),
            })

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
    args = parser.parse_args()

    root_dir = resolve_project_root(__file__)
    source_path = Path(args.source)

    if not source_path.is_absolute():
        source_path = Path.cwd() / source_path
    source_path = source_path.resolve()

    if not source_path.exists():
        print_warn(f"源文件不存在: {source_path}")
        sys.exit(1)

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
