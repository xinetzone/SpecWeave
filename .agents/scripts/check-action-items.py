#!/usr/bin/env python3
"""扫描复盘报告中的行动计划表格，提取状态为"待规划"的条目，输出待办清单。"""

import sys
from pathlib import Path

from lib.project import resolve_project_root


# 默认扫描目录
DEFAULT_REPORTS_DIR = resolve_project_root(__file__) / "docs" / "retrospective" / "reports"

# 行动计划表格表头匹配模式（以这些列开头的表格即为行动计划表格）
HEADER_PATTERN = "| 优先级 | 改进项 | 具体措施 |"


def parse_args() -> Path:
    """解析命令行参数，返回报告目录路径。"""
    if len(sys.argv) > 1:
        dir_path = Path(sys.argv[1])
        if not dir_path.is_dir():
            print(f"错误: 指定路径不是有效目录: {dir_path}", file=sys.stderr)
            sys.exit(2)
        return dir_path
    return DEFAULT_REPORTS_DIR


def is_separator_line(line: str) -> bool:
    """判断是否为 Markdown 表格的分隔行（如 |---|---|）。"""
    stripped = line.strip()
    return stripped.startswith("|") and "---" in stripped


def parse_table_row(line: str) -> list[str]:
    """将表格行按 | 分割为列，去除首尾空白与首尾空元素。"""
    parts = line.strip().split("|")
    # 去除首尾可能因前后 | 产生的空字符串
    if parts and parts[0] == "":
        parts = parts[1:]
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return [p.strip() for p in parts]


def extract_status_index(header_columns: list[str]) -> int | None:
    """从表头列中定位"状态"列的索引，返回索引（从 0 开始）。"""
    for i, col in enumerate(header_columns):
        if "状态" in col:
            return i
    return None


def scan_file(file_path: Path) -> list[dict]:
    """扫描单个 Markdown 文件，返回所有待规划行动项的列表。

    每项为一个字典，包含 priority、item、status 字段。
    """
    results = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return results

    lines = content.splitlines()
    in_table = False
    status_index = None

    for line in lines:
        stripped = line.strip()

        # 检测表头：包含 | 优先级 | 改进项 | 具体措施 |
        if HEADER_PATTERN in stripped:
            header_columns = parse_table_row(stripped)
            status_index = extract_status_index(header_columns)
            in_table = True
            continue

        if not in_table:
            continue

        # 跳过表头后的分隔行
        if is_separator_line(stripped):
            continue

        # 空行或非表格行 → 表格结束
        if not stripped.startswith("|"):
            in_table = False
            status_index = None
            continue

        # 解析数据行
        columns = parse_table_row(stripped)
        if status_index is None or status_index >= len(columns):
            continue

        raw_status = columns[status_index]
        priority = columns[0] if len(columns) > 0 else ""
        item = columns[1] if len(columns) > 1 else ""

        # 模糊匹配：去除空白后检查是否包含"待规划"
        if "待规划" in raw_status:
            results.append({
                "priority": priority,
                "item": item,
                "status": raw_status,
            })

    return results


def main() -> int:
    reports_dir = parse_args()

    if not reports_dir.is_dir():
        print(f"错误: 报告目录不存在: {reports_dir}", file=sys.stderr)
        return 2

    md_files = sorted(reports_dir.glob("*.md"))
    if not md_files:
        print(f"提示: 目录 {reports_dir} 中未找到 .md 文件")
        return 0

    total_files = 0
    total_pending = 0
    priority_counts = {"高": 0, "中": 0, "低": 0}
    output_lines = []

    for md_file in md_files:
        items = scan_file(md_file)
        if not items:
            continue

        total_files += 1
        total_pending += len(items)
        output_lines.append(f"文件: {md_file.name}")

        for entry in items:
            p = entry["priority"]
            item = entry["item"]
            output_lines.append(f"  [{p}] {item} → 待规划")
            if p in priority_counts:
                priority_counts[p] += 1

    # 输出结果
    if output_lines:
        print("\n".join(output_lines))
        print()

    # 统计汇总
    print(
        f"统计: 共扫描 {len(md_files)} 篇报告, "
        f"发现 {total_pending} 个待规划行动项 "
        f"(高:{priority_counts['高']} 中:{priority_counts['中']} 低:{priority_counts['低']})"
    )

    return 1 if total_pending > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
