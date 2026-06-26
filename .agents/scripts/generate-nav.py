#!/usr/bin/env python3
"""自动生成 README.md 和 docs/README.md 的文档导航表。

扫描 docs/ 目录下的 .md 文件，提取标题和描述，自动更新导航表。
支持通过 HTML 注释标记（<!-- NAV_TABLE_START --> / <!-- NAV_TABLE_END -->）
定位需要更新的表格区域。
"""

import sys
from pathlib import Path

from constants import SCAN_DIRS, ROOT_FILES, TARGETS, MANUAL_DESCRIPTIONS
from lib.markdown import (
    extract_description as _extract_description,
    extract_title as _extract_title,
    update_marker_region,
)
from lib.project import resolve_project_root


def extract_title(file_path: Path) -> str:
    """从 Markdown 文件中提取第一个一级标题。"""
    title = _extract_title(file_path)
    return title if title else file_path.stem


def extract_description(file_path: Path) -> str:
    """从 Markdown 文件中提取描述文本。"""
    name = file_path.name
    if name in MANUAL_DESCRIPTIONS:
        return MANUAL_DESCRIPTIONS[name]

    desc = _extract_description(file_path)
    if desc:
        if len(desc) > 60:
            desc = desc[:57] + "..."
        return desc
    return extract_title(file_path)


def scan_docs(root: Path) -> list[tuple[str, str, str, bool]]:
    """扫描文档目录，返回 [(显示名称, 文件名, 描述, 是否根目录文件), ...] 列表。"""
    entries = []

    # 扫描 docs/ 目录下的 .md 文件
    for scan_dir, link_prefix in SCAN_DIRS:
        scan_path = root / scan_dir
        if scan_path.exists():
            for md_file in sorted(scan_path.glob("*.md")):
                if md_file.name == "README.md":
                    continue
                title = extract_title(md_file)
                desc = extract_description(md_file)
                entries.append((title, md_file.name, desc, False))

    # 添加根目录文件
    for rf in ROOT_FILES:
        rf_path = root / rf
        if rf_path.exists():
            title = extract_title(rf_path)
            desc = extract_description(rf_path)
            entries.append((title, rf, desc, True))

    return entries


def generate_table(entries: list[tuple[str, str, str, bool]], link_prefix: str, root_files_prefix: str) -> str:
    """生成 Markdown 导航表，根据目标文件位置使用不同的链接前缀。"""
    lines = ["| 文档 | 说明 |", "|------|------|"]
    for title, filename, desc, is_root_file in entries:
        if is_root_file:
            link = f"{root_files_prefix}{filename}"
        else:
            link = f"{link_prefix}{filename}"
        lines.append(f"| [{title}]({link}) | {desc} |")
    return "\n".join(lines)


def main() -> int:
    root = resolve_project_root(__file__)
    if not root.exists():
        print(f"错误: 项目根目录不存在: {root}", file=sys.stderr)
        return 1

    print("扫描文档目录...")
    entries = scan_docs(root)
    print(f"  找到 {len(entries)} 个文档")

    # 更新目标文件（每个目标使用不同的链接前缀）
    print("\n更新目标文件...")
    updated = 0
    for target_file, config in TARGETS.items():
        target_path = root / target_file
        if not target_path.exists():
            print(f"  跳过: {target_file} 不存在")
            continue

        table = generate_table(entries, config["link_prefix"], config["root_files_prefix"])
        try:
            update_marker_region(target_path, config["marker_start"], config["marker_end"], table)
            print(f"  已更新: {target_file}")
            updated += 1
        except ValueError:
            print(f"  警告: {target_path} 中未找到标记 {config['marker_start']} / {config['marker_end']}，跳过")

    if updated == 0:
        print("  未更新任何文件", file=sys.stderr)
        return 1

    print(f"\n完成: 已更新 {updated} 个文件")
    return 0


if __name__ == "__main__":
    sys.exit(main())