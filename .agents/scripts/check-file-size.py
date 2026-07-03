#!/usr/bin/env python3
"""源代码文件大小门禁检查工具。

基于 module-size-bug-correlation 模式的三级警戒线，检查Python源代码文件大小，
防止"上帝文件"反模式——超过1200行的文件Bug密度是<500行文件的3-6倍。

用法:
    python check-file-size.py                     # 检查 .agents/scripts/ 下的Python文件
    python check-file-size.py --path <path>       # 检查指定目录
    python check-file-size.py --warn 800 --error 1200  # 自定义阈值
    python check-file-size.py --warn-only         # CI模式：只告警不阻断（渐进式门禁）
    python check-file-size.py --demo              # 演示模式

阈值分级（参考 module-size-bug-correlation 模式）:
    - < 500行: 绿色安全区，正常
    - 500-800行: 黄色预警区，规划拆分
    - 800-1200行: 橙色高风险区，WARN，下次重构优先拆分
    - > 1200行: 红色警报区，ERROR，"上帝文件"反模式，停止新增代码优先拆分

渐进式门禁策略:
    - 初始CI集成使用 --warn-only，只告警不阻断，给团队缓冲期
    - 新增代码不允许超过ERROR阈值（对新文件严格）
    - 历史遗留大文件加入ALLOWLIST，标记为"待拆分"，跟踪进度
    - 拆分完成后从ALLOWLIST移除，最终升级为严格ERROR阻断模式

相关模式:
    docs/retrospective/patterns/methodology-patterns/governance-strategy/module-size-bug-correlation.md
"""

import argparse
import sys
from pathlib import Path
from dataclasses import dataclass, field

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, setup_safe_output

ALLOWLIST = {
    'scripts\\lib\\checks\\mermaid.py': '历史遗留：Mermaid语法检查逻辑复杂，待后续重构拆分',
}


@dataclass
class FileSizeInfo:
    filepath: Path
    line_count: int
    level: str
    suggestion: str
    is_allowlisted: bool = False
    allowlist_reason: str = ''


def count_lines(filepath: Path) -> int:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except (UnicodeDecodeError, PermissionError, OSError):
        return 0


def classify_file(line_count: int, warn_threshold: int, error_threshold: int) -> tuple[str, str]:
    if line_count > error_threshold:
        return (
            'ERROR',
            f'🔴 红色警报区（"上帝文件"反模式），停止在此文件新增代码，优先拆分！'
        )
    elif line_count > warn_threshold:
        return (
            'WARN',
            f'🟠 橙色高风险区，立即制定拆分计划，新增功能优先放到新文件'
        )
    elif line_count > 500:
        return (
            'INFO',
            f'🟡 黄色预警区，规划拆分方案，下次重构时优先处理'
        )
    else:
        return (
            'PASS',
            f'🟢 绿色安全区'
        )


def should_exclude(filepath: Path) -> bool:
    exclude_patterns = [
        '__pycache__',
        '.git',
        'node_modules',
        '.venv',
        'venv',
        'dist',
        'build',
        '.tox',
        '.mypy_cache',
        '.pytest_cache',
    ]
    path_str = str(filepath)
    return any(pattern in path_str for pattern in exclude_patterns)


def is_allowlisted(rel_path: Path) -> tuple[bool, str]:
    rel_str = str(rel_path).replace('/', '\\')
    if rel_str in ALLOWLIST:
        return True, ALLOWLIST[rel_str]
    for pattern, reason in ALLOWLIST.items():
        if rel_str.endswith(pattern.replace('scripts\\', '')):
            return True, reason
    return False, ''


def scan_directory(
    root_path: Path,
    extensions: list[str],
    warn_threshold: int,
    error_threshold: int,
) -> list[FileSizeInfo]:
    results = []
    base_path = root_path.parent if root_path.name == 'scripts' else root_path
    for ext in extensions:
        for filepath in root_path.rglob(f'*{ext}'):
            if should_exclude(filepath):
                continue
            if not filepath.is_file():
                continue
            line_count = count_lines(filepath)
            if line_count == 0:
                continue
            level, suggestion = classify_file(line_count, warn_threshold, error_threshold)
            rel_path = filepath.relative_to(base_path)
            allowed, reason = is_allowlisted(rel_path)
            results.append(FileSizeInfo(
                filepath=rel_path,
                line_count=line_count,
                level=level if not allowed else 'WARN',
                suggestion=suggestion,
                is_allowlisted=allowed,
                allowlist_reason=reason,
            ))
    results.sort(key=lambda x: (x.is_allowlisted, x.line_count), reverse=True)
    return results


def main():
    setup_safe_output()
    parser = argparse.ArgumentParser(description='源代码文件大小门禁检查工具')
    parser.add_argument('--path', type=str, default=None, help='要检查的目录路径（默认.agents/scripts/）')
    parser.add_argument('--ext', type=str, nargs='+', default=['.py'], help='要检查的文件扩展名（默认.py）')
    parser.add_argument('--warn', type=int, default=800, help='WARN阈值行数（默认800）')
    parser.add_argument('--error', type=int, default=1200, help='ERROR阈值行数（默认1200）')
    parser.add_argument('--warn-only', action='store_true', help='CI渐进模式：只告警不阻断退出')
    parser.add_argument('--demo', action='store_true', help='演示模式')
    args = parser.parse_args()

    if args.demo:
        print_header("文件大小门禁检查 [DEMO MODE]")
        print()
        demo_files = [
            (Path("big_parser.py"), 1465, "ERROR", "🔴 红色警报区（\"上帝文件\"反模式）", True, "P0待拆分"),
            (Path("versioning.py"), 872, "WARN", "🟠 橙色高风险区", False, ""),
            (Path("generator.py"), 607, "INFO", "🟡 黄色预警区", False, ""),
            (Path("utils.py"), 246, "PASS", "🟢 绿色安全区", False, ""),
            (Path("models.py"), 110, "PASS", "🟢 绿色安全区", False, ""),
        ]
        for filepath, lines, level, suggestion, allowed, reason in demo_files:
            prefix = "  [ALLOWLIST] " if allowed else "  "
            if level == 'ERROR':
                print_error(f"{prefix}{filepath}: {lines}行 - {suggestion}")
                if allowed:
                    print_warn(f"     └─ 例外原因: {reason}")
            elif level in ('WARN', 'INFO'):
                print_warn(f"{prefix}{filepath}: {lines}行 - {suggestion}")
            else:
                print_pass(f"{prefix}{filepath}: {lines}行 - {suggestion}")
        print()
        print_summary(pass_count=2, warn_count=3, error_count=0)
        print_warn("\n  建议：按照 module-size-bug-correlation 模式拆分大文件，按单一职责原则：")
        print_warn("    - Parser类: tokenizer / section-builder / directive-parser")
        print_warn("    - Service类: 按业务域拆分")
        return 0

    if args.path:
        root_path = Path(args.path).resolve()
    else:
        root_path = SCRIPTS_DIR

    mode_str = " (WARN-ONLY渐进模式)" if args.warn_only else ""
    print_header(f"文件大小门禁检查{mode_str}: {root_path}")
    print(f"  阈值: WARN={args.warn}行, ERROR={args.error}行")
    print(f"  模式: module-size-bug-correlation (三级警戒线)")
    if ALLOWLIST:
        print(f"  例外列表: {len(ALLOWLIST)}个历史遗留大文件（标记待拆分，不阻断）")
    print()

    if not root_path.exists():
        print_error(f"目录不存在: {root_path}")
        return 1

    results = scan_directory(root_path, args.ext, args.warn, args.error)

    if not results:
        print_warn("未找到需要检查的文件")
        return 0

    pass_count = 0
    warn_count = 0
    error_count = 0

    for info in results:
        prefix = "[ALLOWLIST] " if info.is_allowlisted else ""
        if info.level == 'ERROR':
            print_error(f"  {prefix}{info.filepath}: {info.line_count}行 - {info.suggestion}")
            if info.is_allowlisted:
                print_warn(f"     └─ 例外原因: {info.allowlist_reason}")
                warn_count += 1
            else:
                error_count += 1
        elif info.level in ('WARN', 'INFO'):
            print_warn(f"  {prefix}{info.filepath}: {info.line_count}行 - {info.suggestion}")
            if info.is_allowlisted:
                print_warn(f"     └─ 例外原因: {info.allowlist_reason}")
            warn_count += 1
        else:
            pass_count += 1

    print()
    print(f"  文件统计: 总计{len(results)}个文件 | 🟢{pass_count}安全 | 🟡/🟠{warn_count}预警")
    if error_count > 0:
        print(f"                | 🔴{error_count}超限（新增代码禁止超过ERROR阈值）")
    if len(ALLOWLIST) > 0:
        print(f"                | 📋{len(ALLOWLIST)}个历史遗留在例外列表（待拆分）")
    print_summary(pass_count=pass_count, warn_count=warn_count, error_count=error_count if not args.warn_only else 0)

    if error_count > 0 and not args.warn_only:
        print()
        print_error("  🔴 发现新增超限文件！超过1200行的新文件禁止提交。")
        print_warn("  红色警报文件拆分建议（按单一职责原则）：")
        print_warn("    1. Parser类大文件 → tokenizer / section-builder / directive-parser")
        print_warn("    2. 大Service类 → 按业务域/功能职责拆分")
        print_warn("    3. 大工具类 → 按输入/处理/输出阶段拆分")
        print_warn("    4. 参考: module-size-bug-correlation.md")
        return 1

    if error_count > 0 and args.warn_only:
        print()
        print_warn("  ⚠️  WARN-ONLY模式：存在超限文件但不阻断CI（渐进式门禁缓冲期）")
        print_warn("     历史遗留大文件请按P0改进计划逐步拆分")
        print_warn("     新增代码请勿超过ERROR阈值，后续将升级为严格阻断模式")

    if warn_count > 0:
        print()
        print_warn("  🟡/🟠 存在预警文件，建议在下次重构时优先拆分")
        print_warn("    新增功能时优先放到新文件，避免继续往大文件里加代码")

    if error_count == 0 and warn_count == 0:
        print_pass("  所有文件大小均在安全区")

    return 0


if __name__ == '__main__':
    sys.exit(main())
