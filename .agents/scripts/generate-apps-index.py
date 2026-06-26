#!/usr/bin/env python3
"""自动生成 apps/README.md 的应用清单索引表。

扫描 apps/ 目录下的应用子目录，从每个应用的 README.md 提取标题和描述，
自动更新应用清单表。通过 HTML 注释标记（<!-- APPS_TABLE_START --> / <!-- APPS_TABLE_END -->）
定位需要更新的表格区域。
"""

import sys
from pathlib import Path

from lib.markdown import (
    extract_description as _extract_description,
    extract_title as _extract_title,
    update_marker_region,
)
from lib.project import resolve_project_root


def extract_title(readme_path: Path, app_dir_name: str) -> str:
    if not readme_path.exists():
        return app_dir_name
    title = _extract_title(readme_path)
    return title if title else app_dir_name


def extract_description(readme_path: Path, app_dir_name: str) -> str:
    if not readme_path.exists():
        return f"{app_dir_name} 应用"
    desc = _extract_description(readme_path)
    if desc:
        if len(desc) > 80:
            desc = desc[:77] + "..."
        return desc
    return extract_title(readme_path, app_dir_name)


def scan_apps(apps_dir: Path) -> list[tuple[str, str, str]]:
    """扫描 apps/ 目录，返回 [(目录名, 标题, 描述), ...] 列表，跳过 shared/ 和无 README.md 的目录。"""
    entries = []
    for item in sorted(apps_dir.iterdir()):
        if not item.is_dir():
            continue
        if item.name.startswith("."):
            continue
        if item.name == "shared":
            continue
        readme = item / "README.md"
        title = extract_title(readme, item.name)
        desc = extract_description(readme, item.name)
        entries.append((item.name, title, desc))
    return entries


def generate_table(entries: list[tuple[str, str, str]]) -> str:
    lines = ["| 应用 | 说明 | 入口 |", "|---|---|---|"]
    for dir_name, title, desc in entries:
        link = f"{dir_name}/README.md"
        lines.append(f"| `{dir_name}/` | {desc} | [README.md]({link}) |")
    return "\n".join(lines)


def update_readme(readme_path: Path, table: str) -> bool:
    marker_start = "<!-- APPS_TABLE_START -->"
    marker_end = "<!-- APPS_TABLE_END -->"

    try:
        update_marker_region(readme_path, marker_start, marker_end, table)
    except ValueError:
        print(f"  警告: {readme_path} 中未找到标记 {marker_start} / {marker_end}，回退到兼容模式")
        content = readme_path.read_text(encoding="utf-8")
        return update_readme_compat(content, readme_path, table)
    return True


def update_readme_compat(content: str, readme_path: Path, table: str) -> bool:
    """兼容模式：在「### 2.3 应用清单」章节下替换表格。"""
    section_header = "### 2.3 应用清单"
    idx = content.find(section_header)
    if idx == -1:
        print(f"  错误: 未找到「{section_header}」章节", file=sys.stderr)
        return False

    after_header = content[idx + len(section_header):]

    table_start = after_header.find("| 应用 |")
    if table_start == -1:
        table_start = after_header.find("\n\n") + 2
    else:
        line_start = after_header.rfind("\n", 0, table_start)
        table_start = line_start + 1 if line_start != -1 else table_start

    table_end_marker = "\n## "
    table_end_rel = after_header.find(table_end_marker, table_start)
    if table_end_rel == -1:
        table_end_rel = len(after_header)

    before_table = content[: idx + len(section_header)] + after_header[:table_start]
    after_table = after_header[table_end_rel:]

    new_content = before_table + table + "\n" + after_table
    readme_path.write_text(new_content, encoding="utf-8")
    return True


def main() -> int:
    root = resolve_project_root(__file__)
    apps_dir = root / "apps"
    target = apps_dir / "README.md"

    if not apps_dir.exists():
        print(f"错误: apps/ 目录不存在: {apps_dir}", file=sys.stderr)
        return 1
    if not target.exists():
        print(f"错误: apps/README.md 不存在: {target}", file=sys.stderr)
        return 1

    print("扫描 apps/ 目录...")
    entries = scan_apps(apps_dir)
    print(f"  找到 {len(entries)} 个应用")
    for dir_name, title, desc in entries:
        print(f"    - {dir_name}: {title}")

    print("\n生成应用清单表...")
    table = generate_table(entries)

    if update_readme(target, table):
        print(f"  已更新: {target}")
    else:
        return 1

    print(f"\n完成: 已更新 {len(entries)} 个应用条目")
    return 0


if __name__ == "__main__":
    sys.exit(main())
