#!/usr/bin/env python3
"""自动生成 README.md 和 docs/README.md 的文档导航表。

扫描 docs/ 目录下的 .md 文件，提取标题和描述，自动更新导航表。
支持通过 HTML 注释标记（<!-- NAV_TABLE_START --> / <!-- NAV_TABLE_END -->）
定位需要更新的表格区域。
"""

import re
import sys
from pathlib import Path

# 需要扫描的文档目录（相对于项目根目录）
SCAN_DIRS = [
    ("docs/", "docs/"),       # (目录, 链接前缀)
]
# 额外的根目录文件
ROOT_FILES = ["CONTRIBUTING.md"]

# 需要更新的目标文件及其配置
TARGETS = {
    "README.md": {
        "marker_start": "<!-- NAV_TABLE_START -->",
        "marker_end": "<!-- NAV_TABLE_END -->",
        "link_prefix": "docs/",       # 从根目录链接到 docs/
        "root_files_prefix": "",       # 根目录文件不加前缀
    },
    "docs/README.md": {
        "marker_start": "<!-- NAV_TABLE_START -->",
        "marker_end": "<!-- NAV_TABLE_END -->",
        "link_prefix": "",             # docs/ 内部文件直接链接
        "root_files_prefix": "../",    # 根目录文件需要 ../ 前缀
    },
}

# 手动指定的文件描述（优先级高于自动提取）
MANUAL_DESCRIPTIONS = {
    "project-overview.md": "项目定位、设计理念、核心特性",
    "project-structure.md": "完整目录树与职责说明",
    "tech-stack.md": "技术选型、环境依赖",
    "agent-roles.md": "5 个核心角色定义与绑定关系",
    "collaboration.md": "4 项协作协议、3 个标准工作流",
    "development-standards.md": "代码风格、提交规范、测试要求、文档边界",
    "verification-automation.md": "临时依赖治理、验证脚本",
    "knowledge-base.md": "技术知识库、复盘文档体系",
    "related-links.md": "外部标准、工具文档、项目仓库",
    "CONTRIBUTING.md": "贡献流程、分支命名、PR 规范",
}

# 标题提取：匹配第一个一级标题
TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
# 描述提取：匹配标题后第一个非空段落（排除引用块和元数据行）
DESC_RE = re.compile(r"^#\s+.+\n\n(?:>.*\n)*\n?([^\n#>`\-\|].+)", re.MULTILINE)


def extract_title(file_path: Path) -> str:
    """从 Markdown 文件中提取第一个一级标题。"""
    content = file_path.read_text(encoding="utf-8")
    m = TITLE_RE.search(content)
    if m:
        return m.group(1).strip()
    return file_path.stem


def extract_description(file_path: Path) -> str:
    """从 Markdown 文件中提取描述文本。"""
    name = file_path.name
    if name in MANUAL_DESCRIPTIONS:
        return MANUAL_DESCRIPTIONS[name]

    content = file_path.read_text(encoding="utf-8")
    m = DESC_RE.search(content)
    if m:
        desc = m.group(1).strip()
        # 取第一句，限制长度
        desc = re.split(r"[。\.]\s", desc)[0]
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


def update_file(file_path: Path, marker_start: str, marker_end: str, table: str) -> bool:
    """更新文件中的导航表区域。"""
    content = file_path.read_text(encoding="utf-8")

    start_idx = content.find(marker_start)
    end_idx = content.find(marker_end)

    if start_idx == -1 or end_idx == -1:
        print(f"  警告: {file_path} 中未找到标记 {marker_start} / {marker_end}，跳过")
        return False

    # 替换标记之间的内容
    new_content = (
        content[: start_idx + len(marker_start)]
        + "\n\n"
        + table
        + "\n\n"
        + content[end_idx:]
    )
    file_path.write_text(new_content, encoding="utf-8")
    return True


def main() -> int:
    root = Path(__file__).parent.parent.parent
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
        if update_file(target_path, config["marker_start"], config["marker_end"], table):
            print(f"  已更新: {target_file}")
            updated += 1

    if updated == 0:
        print("  未更新任何文件", file=sys.stderr)
        return 1

    print(f"\n完成: 已更新 {updated} 个文件")
    return 0


if __name__ == "__main__":
    sys.exit(main())