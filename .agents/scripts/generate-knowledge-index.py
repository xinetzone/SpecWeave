#!/usr/bin/env python3
"""知识库多维索引生成工具。

扫描 docs/knowledge/ 目录下的所有 Markdown 文件，提取 frontmatter 元数据，
生成支持按知识类型（knowledge_type）、验证状态（validation_status）、
安全级别（security_level）等多维标签检索的索引。

用法：
  python generate-knowledge-index.py                      # 生成索引并输出到 stdout
  python generate-knowledge-index.py --output index.json  # 输出到 JSON 文件
  python generate-knowledge-index.py --stats              # 仅输出分类统计
  python generate-knowledge-index.py --type factual       # 仅输出指定类型条目
  python generate-knowledge-index.py --status verified    # 仅输出指定验证状态条目
  python generate-knowledge-index.py --level internal     # 仅输出指定安全级别条目
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.frontmatter import parse_frontmatter_unified
from lib.knowledge_classification import (
    multi_filter,
    compute_classification_stats,
    VALID_KNOWLEDGE_TYPES,
    VALID_VALIDATION_STATUSES,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE = PROJECT_ROOT / "docs" / "knowledge"


def scan_knowledge_entries(
    base_dir: Path | None = None,
) -> list[dict[str, str | list[str]]]:
    """递归扫描知识库目录，提取所有 Markdown 文件的 frontmatter 元数据。

    Args:
        base_dir: 知识库根目录，默认为 docs/knowledge/。

    Returns:
        知识条目元数据列表，每个条目包含文件路径和 frontmatter 字段。
    """
    if base_dir is None:
        base_dir = KNOWLEDGE_BASE

    entries = []
    for md_file in base_dir.rglob("*.md"):
        if md_file.name == "README.md":
            continue
        if "templates" in md_file.parts:
            continue

        metadata = parse_frontmatter_unified(md_file)
        if metadata is None:
            metadata = {}

        rel_path = md_file.relative_to(PROJECT_ROOT)
        entry = {
            "file": rel_path.as_posix(),
            "title": metadata.get("title", md_file.stem),
            "category": metadata.get("category", ""),
            "tags": metadata.get("tags", []),
            "knowledge_type": metadata.get("knowledge_type", "factual"),
            "validation_status": metadata.get("validation_status", "draft"),
            "security_level": metadata.get("security_level", "public"),
            "reuse_count": metadata.get("reuse_count", "0"),
            "date": metadata.get("date", ""),
            "status": metadata.get("status", ""),
        }
        entries.append(entry)

    return entries


def generate_index_json(
    entries: list[dict[str, str | list[str]]],
) -> dict:
    """生成结构化索引。

    Args:
        entries: 知识条目列表。

    Returns:
        包含条目列表和统计信息的字典。
    """
    return {
        "total": len(entries),
        "stats": compute_classification_stats(entries),
        "entries": entries,
    }


def generate_markdown_index(
    entries: list[dict[str, str | list[str]]],
) -> str:
    """生成 Markdown 格式的索引表。

    Args:
        entries: 知识条目列表。

    Returns:
        Markdown 格式的索引字符串。
    """
    stats = compute_classification_stats(entries)
    lines = [
        f"# 知识库索引",
        f"",
        f"总条目数：**{len(entries)}**",
        f"",
        f"## 分类统计",
        f"",
        f"### 按知识类型",
        f"",
    ]

    for kt, count in stats["by_type"].items():
        type_info = VALID_KNOWLEDGE_TYPES if isinstance(VALID_KNOWLEDGE_TYPES, frozenset) else {}
        lines.append(f"- {kt}: {count}")

    lines.extend(["", "### 按验证状态", ""])
    for vs, count in stats["by_validation"].items():
        lines.append(f"- {vs}: {count}")

    lines.extend(["", "### 按安全级别", ""])
    for sl, count in stats["by_security"].items():
        lines.append(f"- {sl}: {count}")

    lines.extend(["", "## 条目列表", ""])

    for entry in sorted(entries, key=lambda e: str(e.get("title", ""))):
        file_path = entry["file"]
        title = entry.get("title", "")
        kt = entry.get("knowledge_type", "")
        vs = entry.get("validation_status", "")
        lines.append(f"- [{title}]({file_path}) `{kt}` `{vs}`")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="知识库多维索引生成工具"
    )
    parser.add_argument(
        "--output", "-o",
        help="输出 JSON 文件路径",
    )
    parser.add_argument(
        "--stats", action="store_true",
        help="仅输出分类统计",
    )
    parser.add_argument(
        "--type", dest="knowledge_type",
        choices=sorted(VALID_KNOWLEDGE_TYPES),
        help="按知识类型筛选",
    )
    parser.add_argument(
        "--status", dest="validation_status",
        choices=sorted(VALID_VALIDATION_STATUSES),
        help="按验证状态筛选",
    )
    parser.add_argument(
        "--level", dest="security_level",
        choices=["public", "internal", "confidential"],
        help="按安全级别筛选",
    )
    parser.add_argument(
        "--markdown", action="store_true",
        help="输出 Markdown 格式索引",
    )

    args = parser.parse_args()

    entries = scan_knowledge_entries()

    if args.knowledge_type or args.validation_status or args.security_level:
        entries = multi_filter(
            entries,
            knowledge_type=args.knowledge_type,
            validation_status=args.validation_status,
            security_level=args.security_level,
        )

    if args.stats:
        stats = compute_classification_stats(entries)
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return

    if args.markdown:
        output = generate_markdown_index(entries)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            print(f"Markdown 索引已写入 {args.output}")
        else:
            print(output)
        return

    index = generate_index_json(entries)
    if args.output:
        Path(args.output).write_text(
            json.dumps(index, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"JSON 索引已写入 {args.output}")
    else:
        print(json.dumps(index, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()