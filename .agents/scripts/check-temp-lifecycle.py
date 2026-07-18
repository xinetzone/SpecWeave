#!/usr/bin/env python3
""".temp/ 临时文件生命周期治理脚本。

按用途分类检测 .temp/ 下内容的保留期，支持只读检查与交互式清理。

用途分类与保留期:
    backup/       3 天   迁移/重构前备份快照
    experiments/  14 天  实验性脚本（PoC、调试工具、一次性脚本）
    exports/      14 天  临时数据导出（报告草稿、中间数据集）
    screenshots/  14 天  调试截图、临时图片产物
    未分类根级    7 天   无用途前缀的根级内容（文件或目录）

命名合规规则:
    - 路径必须以用途分类前缀开头（backup/、experiments/、exports/、screenshots/）
    - 名称必须包含创建日期（YYYYMMDD，8 位连续数字）或关联 task-id
    - 合规示例：.temp/backup/docs-migration-20260715/、.temp/experiments/task-abc123/
    - 不合规示例：.temp/record.md（无用途前缀、无日期与 task-id）、.temp/backup/old/（无日期与 task-id）

基准日期确定:
    - 优先从名称中解析 YYYYMMDD 日期（正则 \\d{8}，首个可解析为日期者）
    - 若名称无日期但含 task-id（如 task-abc123），视为合规命名，基准日期回退取 mtime
    - 若名称无日期也无 task-id，回退取文件系统修改时间（mtime）
    - 输出中标注每项的基准日期来源（"名称解析"、"task-id" 或 "文件 mtime"）

用法:
    python check-temp-lifecycle.py                  # 只读检查（默认）
    python check-temp-lifecycle.py --clean         # 交互式清理过期项
    python check-temp-lifecycle.py --clean --yes   # 跳过确认（自动化场景）
    python check-temp-lifecycle.py --json          # JSON 输出供 CI 集成
    python check-temp-lifecycle.py --path /path/to/project  # 指定项目根目录

退出码:
    0 = .temp/ 不存在或为空，或全部合规且未过期（清理模式：无残留问题）
    1 = 存在命名不合规项，或存在过期项（只读模式）

来源规范:
    .trae/specs/standards-tools/config-file-placement-governance/spec.md
    （Requirement: .temp 临时文件生命周期治理，共 6 个 Scenario）
"""

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

# 把 .agents/scripts/ 加入 sys.path 以便导入 lib/ 共享库
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import (  # noqa: E402
    print_error,
    print_header,
    print_pass,
    print_summary,
    print_warn,
    setup_safe_output,
)
from lib.project import resolve_project_root  # noqa: E402

# ============================================================================
# 用途分类与保留期配置
# ============================================================================
# 用途前缀 → 保留天数
PURPOSE_RETENTION = {
    "backup": 3,        # 迁移/重构前备份快照
    "experiments": 14,  # 实验性脚本（PoC、调试工具、一次性脚本）
    "exports": 14,      # 临时数据导出（报告草稿、中间数据集）
    "screenshots": 14,  # 调试截图、临时图片产物
}
# 未分类根级内容（无用途前缀的文件或目录）保留天数
ROOT_LEVEL_RETENTION = 7
# YYYYMMDD 日期匹配模式（8 位连续数字）
DATE_PATTERN = re.compile(r"\d{8}")
# task-id 匹配模式（如 task-abc123、task-config-file-placement）
# 项目内常用 task-id 格式，作为日期之外的合规命名标识
TASK_ID_PATTERN = re.compile(r"task-[a-zA-Z0-9][a-zA-Z0-9-]*", re.IGNORECASE)


# ============================================================================
# 数据模型
# ============================================================================
@dataclass
class TempItem:
    """单个 .temp/ 项的检查结果。

    每项对应 .temp/ 下的一个文件或目录：
    - 用途前缀目录的直接子项（如 .temp/backup/<item>）归入对应用途
    - 根级条目（.temp/<item>，未匹配任何用途前缀）归为 unclassified
    """

    path: Path
    name: str
    purpose: str  # backup/experiments/exports/screenshots/unclassified
    is_root_level: bool
    has_prefix: bool
    has_date: bool
    base_date: date
    date_source: str  # "名称解析"、"task-id" 或 "文件 mtime"
    age_days: int
    retention_days: int
    expired: bool
    non_compliant_reasons: list[str] = field(default_factory=list)

    @property
    def compliant(self) -> bool:
        """命名是否合规（同时具备用途前缀与日期/task-id）。"""
        return not self.non_compliant_reasons

    def to_dict(self) -> dict:
        """转换为 JSON 可序列化字典。"""
        return {
            "path": str(self.path),
            "name": self.name,
            "purpose": self.purpose,
            "is_root_level": self.is_root_level,
            "has_prefix": self.has_prefix,
            "has_date": self.has_date,
            "base_date": self.base_date.isoformat(),
            "date_source": self.date_source,
            "age_days": self.age_days,
            "retention_days": self.retention_days,
            "expired": self.expired,
            "non_compliant_reasons": self.non_compliant_reasons,
        }


# ============================================================================
# 辅助函数
# ============================================================================
def parse_date_from_name(name: str) -> date | None:
    """从名称中解析 YYYYMMDD 格式日期。

    匹配 8 位连续数字并尝试解析为日期，返回首个可解析者。
    若无匹配或全部无法解析为有效日期则返回 None。
    """
    for match in DATE_PATTERN.finditer(name):
        try:
            return datetime.strptime(match.group(), "%Y%m%d").date()
        except ValueError:
            continue
    return None


def get_path_size(path: Path) -> int:
    """计算文件或目录的总字节数。"""
    if path.is_file():
        try:
            return path.stat().st_size
        except OSError:
            return 0
    total = 0
    try:
        for entry in path.rglob("*"):
            if entry.is_file():
                try:
                    total += entry.stat().st_size
                except OSError:
                    pass
    except OSError:
        pass
    return total


def format_size(bytes_count: int) -> str:
    """字节数转人类可读 MB 字符串。"""
    return f"{bytes_count / (1024 * 1024):.2f} MB"


def group_by_purpose(items: list[TempItem]) -> dict[str, list[TempItem]]:
    """按用途分组，返回有序字典（按用途名排序）。"""
    groups: dict[str, list[TempItem]] = {}
    for it in items:
        groups.setdefault(it.purpose, []).append(it)
    return dict(sorted(groups.items()))


def classify_item(path: Path, purpose: str | None, today: date) -> TempItem:
    """对单个 .temp/ 项进行分类、合规性检查、保留期计算。

    Args:
        path: 项的完整路径
        purpose: 用途分类（backup/experiments/exports/screenshots）或 None（根级未分类）
        today: 今日日期，用于计算存活天数
    """
    name = path.name
    is_root_level = purpose is None

    # 基准日期：优先从名称解析 YYYYMMDD，无日期时检查 task-id，最后回退到文件 mtime
    parsed_date = parse_date_from_name(name)
    if parsed_date is not None:
        date_source = "名称解析"
        has_date = True
    else:
        # 名称无日期时回退取 mtime 作为基准日期
        try:
            parsed_date = datetime.fromtimestamp(path.stat().st_mtime).date()
        except OSError:
            parsed_date = today
        # 检查 task-id：命中则视为合规命名（has_date=True），基准日期仍取 mtime
        # 因为 task-id 不含日期信息，无法解析基准日期
        if TASK_ID_PATTERN.search(name):
            date_source = "task-id"
            has_date = True
        else:
            date_source = "文件 mtime"
            has_date = False

    # 用途与保留期
    if purpose is None:
        purpose_name = "unclassified"
        retention = ROOT_LEVEL_RETENTION
        has_prefix = False
    else:
        purpose_name = purpose
        retention = PURPOSE_RETENTION[purpose]
        has_prefix = True

    # 合规性校验
    reasons: list[str] = []
    if not has_prefix:
        reasons.append("缺少用途前缀")
    if not has_date:
        reasons.append("缺少日期与 task-id")

    # 存活天数与过期判定
    age_days = max(0, (today - parsed_date).days)
    expired = age_days > retention

    return TempItem(
        path=path,
        name=name,
        purpose=purpose_name,
        is_root_level=is_root_level,
        has_prefix=has_prefix,
        has_date=has_date,
        base_date=parsed_date,
        date_source=date_source,
        age_days=age_days,
        retention_days=retention,
        expired=expired,
        non_compliant_reasons=reasons,
    )


def scan_temp_items(temp_dir: Path, today: date) -> list[TempItem]:
    """扫描 .temp/ 下所有项。

    扫描规则:
        - .temp/backup/、.temp/experiments/ 等用途前缀目录的直接子项归入对应用途
        - 其他根级条目（文件或目录）归为 unclassified
        - 用途前缀目录自身不作为检查项（仅其子项参与检查）
    """
    items: list[TempItem] = []
    for entry in sorted(temp_dir.iterdir()):
        if entry.name in PURPOSE_RETENTION and entry.is_dir():
            # 用途前缀目录：扫描其直接子项
            for child in sorted(entry.iterdir()):
                items.append(classify_item(child, entry.name, today))
        else:
            # 根级未分类项（文件或目录）
            items.append(classify_item(entry, None, today))
    return items


def delete_item(path: Path) -> int:
    """删除文件或目录，返回释放字节数。失败时打印错误并返回 0。"""
    size = get_path_size(path)
    try:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        return size
    except OSError as e:
        print_error(f"删除失败 {path}: {e}")
        return 0


# ============================================================================
# 输出渲染
# ============================================================================
def output_json(items: list[TempItem], temp_dir: Path, exit_code: int) -> int:
    """JSON 输出供 CI 集成。"""
    non_compliant = [it for it in items if not it.compliant]
    expired = [it for it in items if it.expired]
    payload = {
        "temp_dir": str(temp_dir),
        "total_items": len(items),
        "non_compliant": [it.to_dict() for it in non_compliant],
        "expired": [it.to_dict() for it in expired],
        "summary": {
            "non_compliant_count": len(non_compliant),
            "expired_count": len(expired),
        },
        "exit_code": exit_code,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


def report_empty(json_mode: bool, temp_dir: Path) -> int:
    """报告 .temp/ 为空或不存在，退出码 0。"""
    if json_mode:
        payload = {
            "temp_dir": str(temp_dir),
            "exists": temp_dir.exists(),
            "total_items": 0,
            "non_compliant": [],
            "expired": [],
            "summary": {"non_compliant_count": 0, "expired_count": 0},
            "exit_code": 0,
            "message": "无临时内容需检查",
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_header(".temp/ 临时文件生命周期检查")
        print_pass(f"{temp_dir} 不存在或为空 - 无临时内容需检查")
    return 0


def perform_clean(
    items_to_clean: list[TempItem],
    auto_yes: bool,
    project_root: Path,
) -> tuple[int, int]:
    """执行清理。返回 (删除项数, 释放字节数)。"""
    print_header("过期项清理")
    by_purpose = group_by_purpose(items_to_clean)
    for purpose, group in by_purpose.items():
        print(f"  [{purpose} 类] {len(group)} 项:")
        for it in group:
            rel = it.path.relative_to(project_root)
            print(f"    - {rel} ({format_size(get_path_size(it.path))})")
    print()

    if not auto_yes:
        try:
            answer = input("确认删除以上过期项？(y/N) ").strip().lower()
        except EOFError:
            answer = ""
        if answer != "y":
            print_warn("已取消清理")
            return 0, 0

    deleted_count = 0
    deleted_bytes = 0
    for it in items_to_clean:
        size = delete_item(it.path)
        if size > 0 or not it.path.exists():
            deleted_count += 1
            deleted_bytes += size
            print_pass(f"已删除: {it.path.relative_to(project_root)}")
    return deleted_count, deleted_bytes


# ============================================================================
# 主入口
# ============================================================================
def main() -> int:
    setup_safe_output()
    parser = argparse.ArgumentParser(
        description=".temp/ 临时文件生命周期治理脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="交互式清理过期内容（仅清理合规且过期的项，不合规项需人工处理）",
    )
    parser.add_argument(
        "--yes", action="store_true",
        help="跳过清理确认（自动化场景，需配合 --clean 使用，谨慎操作）",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="以 JSON 格式输出结果（供 CI 集成）",
    )
    parser.add_argument(
        "--path", type=Path, default=None,
        help="指定项目根目录路径（默认自动检测）",
    )
    args = parser.parse_args()

    # 确定项目根目录与 .temp/ 路径
    if args.path is not None:
        project_root = args.path.resolve()
    else:
        project_root = resolve_project_root(__file__)
    temp_dir = project_root / ".temp"

    today = date.today()

    # 边界场景：.temp/ 不存在或为空
    if (not temp_dir.exists()) or (not temp_dir.is_dir()) or (not any(temp_dir.iterdir())):
        return report_empty(args.json, temp_dir)

    # 扫描所有项
    items = scan_temp_items(temp_dir, today)

    # 分类：不合规项 / 过期且合规项
    non_compliant = [it for it in items if not it.compliant]
    expired_compliant = [it for it in items if it.compliant and it.expired]

    # JSON 模式：直接输出
    if args.json:
        exit_code = 1 if (non_compliant or expired_compliant) else 0
        return output_json(items, temp_dir, exit_code)

    # 文本输出：报告头
    print_header(".temp/ 临时文件生命周期检查")
    print(f"  扫描目录: {temp_dir}")
    print(f"  今日日期: {today.isoformat()}")
    print(f"  总项数:   {len(items)}")
    print()

    # 命名不合规项
    if non_compliant:
        print_warn(f"命名不合规项 {len(non_compliant)} 个：")
        for it in non_compliant:
            rel = it.path.relative_to(project_root)
            reason_str = "、".join(it.non_compliant_reasons)
            print_error(f"{rel}  -  {reason_str}  ({it.date_source})")
        print()
        print_warn("建议重命名为合规格式（含用途前缀与 YYYYMMDD 日期或 task-id），脚本不自动重命名。")
        print()

    # 过期项（按用途分组）
    if expired_compliant:
        print_warn(f"过期项 {len(expired_compliant)} 个（按用途分组）：")
        by_purpose = group_by_purpose(expired_compliant)
        for purpose, group in by_purpose.items():
            print_warn(f"  [{purpose} 类] 过期 {len(group)} 项:")
            for it in group:
                rel = it.path.relative_to(project_root)
                print(f"    - {rel}")
                print(f"      创建日期: {it.base_date.isoformat()} ({it.date_source})")
                print(f"      保留期: {it.retention_days} 天 | 已存活: {it.age_days} 天")
        print()
        if not args.clean:
            print_warn("建议执行清理: python .agents/scripts/check-temp-lifecycle.py --clean")
            print()

    # 全部合规且未过期
    if not non_compliant and not expired_compliant:
        print_pass("所有 .temp/ 内容均合规且未过期")

    # 合规未过期项汇总说明（不逐项列出，仅在汇总中体现）
    compliant_pending_count = sum(
        1 for it in items if it.compliant and not it.expired
    )
    if non_compliant or expired_compliant:
        print(f"  合规未过期项 {compliant_pending_count} 项（未逐项列出）")
        print()

    # 清理模式
    cleaned_count = 0
    cleaned_bytes = 0
    if args.clean:
        if not expired_compliant:
            print_pass("无过期合规项需要清理")
        else:
            cleaned_count, cleaned_bytes = perform_clean(
                expired_compliant, args.yes, project_root
            )
            print()
            print_header("清理摘要")
            print(f"  删除项数: {cleaned_count}")
            print(f"  释放空间: {format_size(cleaned_bytes)}")
            remaining = len(items) - cleaned_count
            print(f"  剩余项数: {remaining}")

    # 检查摘要
    pass_count = sum(1 for it in items if it.compliant and not it.expired)
    warn_count = sum(1 for it in items if it.compliant and it.expired)
    error_count = sum(1 for it in items if not it.compliant)
    print_summary(pass_count=pass_count, warn_count=warn_count, error_count=error_count)

    # 退出码判定
    if args.clean:
        # 清理模式：仍有命名不合规项或未删除的过期项则退出码 1
        remaining_expired = len(expired_compliant) - cleaned_count
        if non_compliant or remaining_expired > 0:
            return 1
        return 0
    # 只读模式：命名不合规或存在过期项均退出码 1
    return 1 if (non_compliant or expired_compliant) else 0


if __name__ == "__main__":
    sys.exit(main())
