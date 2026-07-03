"""模式成熟度工具 - README统计表解析与更新。"""

import re
from collections import OrderedDict
from pathlib import Path

from .constants import README_INDEX_TABLE_RE, README_STATS_TABLE_RE
from .scanner import grep_maturity_per_directory


def parse_readme_stats_table(readme_path):
    """从 patterns/README.md 统计表中解析报告数据。

    兼容两种表格格式：
    1. 原始格式（| **dir/** | **N** | **L1** | **L2** | **L3** | **L4** |）
    2. 简单格式（| dir/ | N | L1 | L2 | L3 | L4 |）

    Args:
        readme_path: README.md 的 Path 对象。

    Returns:
        {"dir/": {"L1": N, "L2": N, "L3": N, "L4": N, "_total": N}, ...}
    """
    content = readme_path.read_text(encoding='utf-8')
    dir_stats = {}

    for match in README_STATS_TABLE_RE.finditer(content):
        dir_name = match.group(1).strip().rstrip('/')
        if '合计' in dir_name:
            continue
        total = int(match.group(2))
        l1 = int(match.group(3))
        l2 = int(match.group(4))
        l3 = int(match.group(5))
        l4 = int(match.group(6))

        dir_stats[dir_name] = {
            'L1': l1,
            'L2': l2,
            'L3': l3,
            'L4': l4,
            '_total': total,
        }

    return dir_stats


def parse_readme_index_table(readme_path):
    """从 patterns/README.md 的索引表中提取目录统计（用于 check-index 子命令）。

    表格格式：| 目录 | 模式数 | L1 | L2 | L3 | L4 |

    Args:
        readme_path: README.md 的 Path 对象。

    Returns:
        OrderedDict，key 为目录名（如 "methodology-patterns/"），
        value 为 {"patterns": N, "L1": N, "L2": N, "L3": N, "L4": N}
    """
    content = readme_path.read_text(encoding='utf-8')
    stats = OrderedDict()
    in_table = False

    for line in content.splitlines():
        if line.startswith('| 目录 |'):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith('|---'):
            continue
        m = README_INDEX_TABLE_RE.match(line)
        if m:
            name = m.group(1).strip()
            try:
                stats[name] = {
                    'patterns': int(m.group(2)),
                    'L1': int(m.group(3)),
                    'L2': int(m.group(4)),
                    'L3': int(m.group(5)),
                    'L4': int(m.group(6)),
                }
            except (ValueError, IndexError):
                continue
        else:
            if '**' in line:
                in_table = False

    return stats


def check_stats_consistency(patterns_root, readme_path):
    """比较 grep 统计与 README 统计表的差异。

    Args:
        patterns_root: patterns/ 目录 Path。
        readme_path: README.md Path。

    Returns:
        [{"directory": str, "field": str, "grep": int, "readme": int, "diff": int}, ...]
    """
    grep_stats = grep_maturity_per_directory(patterns_root)
    readme_stats = parse_readme_stats_table(readme_path)
    discrepancies = []

    for dir_name in grep_stats:
        grep_data = grep_stats[dir_name]
        readme_data = readme_stats.get(
            dir_name,
            {'L1': 0, 'L2': 0, 'L3': 0, 'L4': 0, '_total': 0},
        )

        for field in ['L1', 'L2', 'L3', 'L4']:
            g = grep_data.get(field, 0)
            r = readme_data.get(field, 0)
            if g != r:
                discrepancies.append({
                    'directory': dir_name,
                    'field': field,
                    'grep': g,
                    'readme': r,
                    'diff': g - r,
                })

        g_total = grep_data.get('_total', 0)
        r_total = readme_data.get('_total', 0)
        if g_total != r_total:
            discrepancies.append({
                'directory': dir_name,
                'field': '总计',
                'grep': g_total,
                'readme': r_total,
                'diff': g_total - r_total,
            })

    return discrepancies


def update_readme_index_table(readme_path, declared_stats, actual_counts):
    """更新 patterns/README.md 中的索引统计表数值。

    仅替换数字，不改变表格结构。返回更新后的内容。

    Args:
        readme_path: README.md Path。
        declared_stats: parse_readme_index_table 返回的声明统计（保留 L1-L4 值）。
        actual_counts: {"dir/": actual_count, ...} 实际文件数。

    Returns:
        更新后的文件内容字符串。
    """
    content = readme_path.read_text(encoding='utf-8')
    lines = content.splitlines()
    new_lines = []

    total_patterns = 0
    total_l1 = 0
    total_l2 = 0
    total_l3 = 0
    total_l4 = 0

    in_table = False
    for line in lines:
        if line.startswith('| 目录 |'):
            in_table = True
            new_lines.append(line)
            continue

        if not in_table:
            new_lines.append(line)
            continue

        if line.startswith('|---'):
            new_lines.append(line)
            continue

        m = re.match(
            r"^\|\s*(\S+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|",
            line,
        )
        if m:
            name = m.group(1).strip()
            if name in actual_counts:
                count = actual_counts[name]
                l1 = declared_stats.get(name, {}).get('L1', int(m.group(3)))
                l2 = declared_stats.get(name, {}).get('L2', int(m.group(4)))
                l3 = declared_stats.get(name, {}).get('L3', int(m.group(5)))
                l4 = declared_stats.get(name, {}).get('L4', int(m.group(6)))
                new_lines.append(f"| {name} | {count} | {l1} | {l2} | {l3} | {l4} |")
                total_patterns += count
                total_l1 += l1
                total_l2 += l2
                total_l3 += l3
                total_l4 += l4
            else:
                new_lines.append(line)
            continue

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

    return '\n'.join(new_lines) + '\n'
