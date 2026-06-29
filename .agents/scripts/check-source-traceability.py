#!/usr/bin/env python3
"""扫描 Markdown 文件的 frontmatter，提取 source 溯源字段，建立"源文件→派生产物"反向索引。

支持 TOML（+++ ... +++）和 YAML（--- ... ---）两种 frontmatter 格式。

支持两种模式：
  1. 审计模式（默认）：列出所有 source 字段及其对应派生产物
  2. 影响分析模式（--affected <文件>）：给定变更的源文件，输出受影响的派生产物清单
"""

import argparse
import sys
import json
from pathlib import Path

from lib.frontmatter import extract_frontmatter_field_from_file
from lib.project import resolve_project_root
from lib.cli import add_common_args
from lib.markdown import find_markdown_files


def extract_source_field(file_path: Path) -> str | None:
    """从 Markdown 文件的 frontmatter 中提取 source 字段值（自动识别 TOML/YAML 格式）。

    返回 source 字段值（如 "README.md#自我迭代机制"），无 frontmatter 或无 source 字段时返回 None。
    """
    return extract_frontmatter_field_from_file(file_path, "source")


def parse_source_reference(source_value: str) -> tuple[str, str]:
    """解析 source 字段值，分离文件路径与章节锚点。

    输入: "README.md#自我迭代机制"
    返回: ("README.md", "自我迭代机制")
    输入: "docs/spec.md"
    返回: ("docs/spec.md", "")
    """
    if "#" in source_value:
        file_part, _, anchor = source_value.partition("#")
        return (file_part, anchor)
    return (source_value, "")


def build_source_index(root_dir: Path) -> dict[str, list[dict]]:
    """构建反向索引：源文件 → 派生产物列表。

    返回字典: {
        "README.md": [
            {"artifact": ".agents/modules/self-iteration.md", "anchor": "自我迭代机制", "source": "README.md#自我迭代机制"},
            ...
        ],
        ...
    }
    """
    md_files = find_markdown_files(root_dir)
    index: dict[str, list[dict]] = {}

    for md_file in md_files:
        source_value = extract_source_field(md_file)
        if not source_value:
            continue

        file_part, anchor = parse_source_reference(source_value)
        try:
            rel_artifact = md_file.relative_to(root_dir).as_posix()
        except ValueError:
            rel_artifact = str(md_file)

        entry = {
            "artifact": rel_artifact,
            "anchor": anchor,
            "source": source_value,
        }
        index.setdefault(file_part, []).append(entry)

    return index


def normalize_source_file(source_file: str, root_dir: Path) -> str:
    """将用户输入的源文件路径归一化为相对项目根的 POSIX 路径。

    支持绝对路径与相对路径输入。
    """
    p = Path(source_file)
    if p.is_absolute():
        try:
            return p.relative_to(root_dir).as_posix()
        except ValueError:
            return p.as_posix()
    return p.as_posix()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="扫描 source 溯源字段，建立源文件→派生产物反向索引，支持影响分析。"
    )
    add_common_args(parser)
    parser.add_argument(
        "--affected",
        type=str,
        default=None,
        help="影响分析模式：指定变更的源文件，输出受影响的派生产物清单",
    )
    args = parser.parse_args()

    root = args.path or resolve_project_root(__file__)
    if not root.exists():
        print(f"错误: 路径不存在: {root}", file=sys.stderr)
        return 1

    index = build_source_index(root)

    # 影响分析模式
    if args.affected:
        normalized = normalize_source_file(args.affected, root)
        affected = index.get(normalized, [])

        if args.json:
            print(json.dumps({
                "source_file": normalized,
                "affected_count": len(affected),
                "affected_artifacts": affected,
            }, ensure_ascii=False, indent=2))
        else:
            print("=" * 60)
            print("源变更影响分析")
            print("=" * 60)
            print(f"\n变更源文件: {normalized}")
            print(f"受影响派生产物: {len(affected)} 个")
            if affected:
                print()
                for entry in affected:
                    anchor_str = f"#{entry['anchor']}" if entry["anchor"] else ""
                    print(f"  - {entry['artifact']}  (来源: {entry['source']})")
                print(f"\n建议: 检查以上 {len(affected)} 个产物的内容是否需要与源头同步更新。")
            else:
                print("\n无受影响产物（该源文件未被任何派生产物引用）。")
            print("\n" + "=" * 60)
        return 0

    # 审计模式（默认）
    total_artifacts = sum(len(v) for v in index.values())

    if args.json:
        print(json.dumps({
            "summary": {
                "source_files": len(index),
                "derived_artifacts": total_artifacts,
            },
            "index": index,
        }, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("source 溯源字段审计")
        print("=" * 60)
        print(f"\n扫描目录: {root}")
        print(f"源文件数: {len(index)}")
        print(f"派生产物数: {total_artifacts}")
        print()

        if not index:
            print("未发现含 source 字段的派生产物。")
            print("提示: 在派生产物的 frontmatter 中添加 source 字段以启用溯源。")
            print("      TOML 格式（+++）: source = \"README.md#章节名\"")
            print("      YAML 格式（---）: source: \"README.md#章节名\"")
        else:
            print("-" * 60)
            for source_file in sorted(index.keys()):
                entries = index[source_file]
                print(f"\n源文件: {source_file}  ({len(entries)} 个派生产物)")
                for entry in entries:
                    print(f"  - {entry['artifact']}  (来源: {entry['source']})")

        print("\n" + "=" * 60)
        print("提示: 使用 --affected <源文件> 查询源变更的受影响产物")
        print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
