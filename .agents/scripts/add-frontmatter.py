#!/usr/bin/env python3
"""为 docs/knowledge/ 下缺少 frontmatter 的文件批量添加 YAML frontmatter。

扫描 docs/knowledge/ 目录下所有 .md 文件，识别缺少 frontmatter 的文件，
根据目录结构自动推断 category，生成标准 YAML frontmatter，交互式确认后批量添加。

用法示例:
  python .agents/scripts/add-frontmatter.py              # 扫描并交互确认
  python .agents/scripts/add-frontmatter.py --dry-run    # 预览但不修改
  python .agents/scripts/add-frontmatter.py --force      # 直接添加，跳过确认
  python .agents/scripts/add-frontmatter.py --category learning  # 指定类别
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from lib.frontmatter import parse_frontmatter_unified
from lib.markdown import extract_title

# 目录到 category 的映射
CATEGORY_MAP = {
    "learning": "learning",
    "operations": "operations",
    "troubleshooting": "troubleshooting",
    "decisions": "decisions",
    "best-practices": "best-practices",
    "platform": "platform",
    "scripts": "scripts",
}


def infer_category(file_path: Path, knowledge_root: Path) -> str:
    """根据文件所在目录推断 category。

    Args:
        file_path: 文件路径
        knowledge_root: docs/knowledge/ 目录路径

    Returns:
        category 字符串；根级 README.md 返回 "index"，无法推断时返回 "uncategorized"
    """
    try:
        rel_path = file_path.relative_to(knowledge_root)
    except ValueError:
        return "uncategorized"

    if len(rel_path.parts) == 1 and rel_path.name == "README.md":
        return "index"

    first_dir = rel_path.parts[0] if len(rel_path.parts) > 1 else ""
    return CATEGORY_MAP.get(first_dir, "uncategorized")


def has_frontmatter(file_path: Path) -> bool:
    """检查文件是否已有 frontmatter。

    Args:
        file_path: 文件路径

    Returns:
        True 表示已有 frontmatter，False 表示缺少
    """
    return parse_frontmatter_unified(file_path) is not None


def generate_frontmatter(file_path: Path, knowledge_root: Path, category: str = None) -> str:
    """生成标准 YAML frontmatter。

    Args:
        file_path: 文件路径
        knowledge_root: docs/knowledge/ 目录路径
        category: 指定的 category（可选）

    Returns:
        YAML frontmatter 字符串（包含 --- 标记）
    """
    inferred_category = category or infer_category(file_path, knowledge_root)
    title = extract_title(file_path) or file_path.stem.replace("-", " ").title()
    today = datetime.now().strftime("%Y-%m-%d")

    frontmatter = f"""---
title: "{title}"
category: "{inferred_category}"
tags: []
date: "{today}"
status: "draft"
author: ""
summary: ""
---
"""
    return frontmatter


def scan_missing_frontmatter(knowledge_root: Path) -> list[Path]:
    """扫描缺少 frontmatter 的文件。

    Args:
        knowledge_root: docs/knowledge/ 目录路径

    Returns:
        缺少 frontmatter 的文件路径列表
    """
    missing = []
    for md_file in knowledge_root.rglob("*.md"):
        if not has_frontmatter(md_file):
            missing.append(md_file)
    return missing


def add_frontmatter(file_path: Path, knowledge_root: Path, category: str = None) -> None:
    """为单个文件添加 frontmatter。

    Args:
        file_path: 文件路径
        knowledge_root: docs/knowledge/ 目录路径
        category: 指定的 category（可选）
    """
    content = file_path.read_text(encoding="utf-8")
    frontmatter = generate_frontmatter(file_path, knowledge_root, category)
    new_content = frontmatter + "\n" + content
    file_path.write_text(new_content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="为 docs/knowledge/ 下缺少 frontmatter 的文件批量添加 YAML frontmatter"
    )
    parser.add_argument("--dry-run", action="store_true", help="预览但不修改文件")
    parser.add_argument("--force", action="store_true", help="直接添加，跳过确认")
    parser.add_argument("--category", type=str, default=None, help="指定 category")
    parser.add_argument("--path", type=str, default=None, help="指定扫描路径（默认 docs/knowledge/）")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    knowledge_root = Path(args.path) if args.path else project_root / ".agents" / "docs" / "knowledge"

    if not knowledge_root.exists():
        print(f"错误：目录不存在: {knowledge_root}", file=sys.stderr)
        return 1

    missing_files = scan_missing_frontmatter(knowledge_root)

    if not missing_files:
        print("所有文件都已有 frontmatter")
        return 0

    print(f"发现 {len(missing_files)} 个缺少 frontmatter 的文件：")
    print("-" * 60)

    for i, file_path in enumerate(missing_files, 1):
        rel_path = file_path.relative_to(project_root)
        category = args.category or infer_category(file_path, knowledge_root)
        title = extract_title(file_path) or file_path.stem.replace("-", " ").title()
        frontmatter = generate_frontmatter(file_path, knowledge_root, args.category)
        print(f"\n{i}. {rel_path}")
        print(f"   category: {category}")
        print(f"   title: {title}")
        if args.dry_run:
            print("   frontmatter:")
            print(f"   {frontmatter.strip()}")

    if args.dry_run:
        print("\n--dry-run 模式：未修改任何文件")
        return 0

    if not args.force:
        print("\n" + "-" * 60)
        confirm = input("是否为以上文件添加 frontmatter？(y/N): ").strip().lower()
        if confirm != "y":
            print("操作已取消")
            return 0

    print("\n正在添加 frontmatter...")
    for i, file_path in enumerate(missing_files, 1):
        rel_path = file_path.relative_to(project_root)
        try:
            add_frontmatter(file_path, knowledge_root, args.category)
            print(f"✓ {rel_path}")
        except Exception as e:
            print(f"✗ {rel_path}: {e}", file=sys.stderr)

    print(f"\n完成！共为 {len(missing_files)} 个文件添加了 frontmatter")
    return 0


if __name__ == "__main__":
    sys.exit(main())