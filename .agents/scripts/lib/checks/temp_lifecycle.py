""".temp/ 临时文件生命周期检查模块（CI 分级策略）。

封装对 `check-temp-lifecycle.py` 的只读调用，供 ci-check、repo-check、pre_commit
等编排入口复用。

两层策略说明：
    1. 底层脚本策略（用途保留期）：backup=3天、experiments/exports/screenshots=14天、
       未分类根级=7天。命名不合规或超保留期时脚本退出码 1。
    2. CI/pre-commit 策略（统一年龄阈值，与用途分类无关）：
       - 年龄 > 14 天 → CI 警告（不阻塞）
       - 年龄 > 30 天 → CI 错误（阻塞流水线 / 阻塞提交）
    pre-commit 仅采用 30 天阻塞阈值（与 CI 错误阈值一致），14 天不阻塞提交。

接口约定：
    - ``run(project_root, args) -> int``：遵循 lib/checks/ 通用约定，
      调用底层脚本只读模式，打印报告并返回退出码。
    - ``run_check(project_root=None) -> CheckResult``：返回结构化结果，
      warnings 含 14-30 天项，errors 含 >30 天项。
    - ``run_ci_check(project_root=None) -> int``：CI 质量门禁入口，
      >30 天返回 1（阻塞），14-30 天或全部合规返回 0（警告但不阻塞）。
    - ``run_precommit_check(project_root=None) -> int``：pre-commit 入口，
      >30 天返回 1（阻塞提交），其余返回 0。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from lib.checks.base import CheckResult
from lib.cli import print_error, print_header, print_pass, print_summary, print_warn
from lib.project import resolve_project_root

# 底层校验脚本（位于 .agents/scripts/ 根目录）
_CHECK_SCRIPT_NAME = "check-temp-lifecycle.py"

# CI 统一年龄阈值（与用途分类无关）
CI_WARN_AGE_DAYS = 14   # 超过 14 天 → CI 警告（不阻塞）
CI_ERROR_AGE_DAYS = 30  # 超过 30 天 → CI 错误（阻塞）


def _scripts_dir(project_root: Path) -> Path:
    """返回 .agents/scripts/ 目录路径。"""
    return project_root / ".agents" / "scripts"


def _invoke_script(project_root: Path) -> tuple[int, dict | None]:
    """以只读 --json 模式调用底层 check-temp-lifecycle.py。

    返回 (exit_code, parsed_json)。若脚本执行失败或 JSON 解析失败，
    parsed_json 为 None。
    """
    script = _scripts_dir(project_root) / _CHECK_SCRIPT_NAME
    if not script.exists():
        print_error(f"底层校验脚本不存在: {script}")
        return 1, None

    try:
        result = subprocess.run(
            [sys.executable, str(script), "--json"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        print_error(f"调用底层脚本失败: {exc}")
        return 1, None

    stdout = result.stdout or ""
    parsed: dict | None = None
    if stdout.strip():
        try:
            parsed = json.loads(stdout)
        except json.JSONDecodeError:
            parsed = None
    return result.returncode, parsed


def _collect_items_with_age(payload: dict) -> list[dict]:
    """从 JSON 载荷中收集所有带 age_days 的项（去重）。

    底层脚本的 JSON 仅输出 non_compliant 与 expired 两个子集，但：
      - 任何年龄 >14 天的合规项必然超用途保留期（最大 14 天）→ 出现在 expired
      - 任何不合规项 → 出现在 non_compliant
    因此两者的并集（按 path 去重）覆盖所有可能触及 CI 14/30 阈值的项。
    """
    seen: dict[str, dict] = {}
    for key in ("non_compliant", "expired"):
        for item in payload.get(key, []) or []:
            path = item.get("path")
            if path and path not in seen:
                seen[path] = item
    return list(seen.values())


def _classify_by_ci_age(items: list[dict]) -> tuple[list[dict], list[dict]]:
    """按 CI 年龄阈值分类：返回 (warn_items, error_items)。

    - error_items: age_days > 30
    - warn_items: 14 < age_days <= 30
    """
    warn_items: list[dict] = []
    error_items: list[dict] = []
    for item in items:
        age = item.get("age_days", 0)
        try:
            age_int = int(age)
        except (TypeError, ValueError):
            continue
        if age_int > CI_ERROR_AGE_DAYS:
            error_items.append(item)
        elif age_int > CI_WARN_AGE_DAYS:
            warn_items.append(item)
    return warn_items, error_items


def _format_item(item: dict, project_root: Path) -> str:
    """格式化单项为可读字符串。"""
    path = item.get("path", "<未知路径>")
    try:
        rel = str(Path(path).relative_to(project_root))
    except ValueError:
        rel = path
    age = item.get("age_days", "?")
    purpose = item.get("purpose", "?")
    base_date = item.get("base_date", "?")
    date_source = item.get("date_source", "?")
    reasons = item.get("non_compliant_reasons") or []
    suffix = f"（不合规: {'、'.join(reasons)}）" if reasons else ""
    return f"{rel} | 用途={purpose} | 年龄={age}天 | 基准={base_date}({date_source}){suffix}"


def run_check(project_root: Path | str | None = None) -> CheckResult:
    """执行只读检查并返回结构化 CheckResult（按 CI 年龄阈值分级）。

    Args:
        project_root: 项目根目录。为 None 时自动定位。

    Returns:
        CheckResult：name="temp_lifecycle"，warnings 含 14-30 天项，
        errors 含 >30 天项，passed=True 表示无 >30 天项。
    """
    root = Path(project_root).resolve() if project_root else resolve_project_root(__file__)
    exit_code, payload = _invoke_script(root)

    result = CheckResult(name="temp_lifecycle")

    if payload is None:
        result.passed = False
        result.errors.append("底层脚本未返回有效 JSON 结果，无法判定 .temp 生命周期状态")
        return result

    # 空目录场景：底层脚本返回 message 字段且 total_items=0
    total = payload.get("total_items", 0)
    if total == 0 or payload.get("message"):
        result.passed = True
        return result

    items = _collect_items_with_age(payload)
    warn_items, error_items = _classify_by_ci_age(items)

    for it in warn_items:
        result.warnings.append(_format_item(it, root))
    for it in error_items:
        result.errors.append(_format_item(it, root))

    # passed 仅由 >30 天错误项决定（14-30 天警告不阻断）
    result.passed = len(error_items) == 0
    return result


def run(project_root: Path, args: argparse.Namespace) -> int:
    """lib/checks/ 通用接口：调用底层脚本只读模式并打印报告。

    返回底层脚本退出码（基于用途保留期策略：命名不合规或超保留期均返回 1）。
    供 repo-check.py 等编排器调用。
    """
    print_header(".temp/ 生命周期检查 (lib/checks/temp_lifecycle)")
    exit_code, payload = _invoke_script(project_root)

    if payload is None:
        print_error("底层脚本未返回有效 JSON 结果")
        print_summary(pass_count=0, warn_count=0, error_count=1)
        return 1

    total = payload.get("total_items", 0)
    if total == 0 or payload.get("message"):
        print_pass(payload.get("message", ".temp/ 无临时内容需检查"))
        print_summary(pass_count=1, warn_count=0, error_count=0)
        return 0

    non_compliant = payload.get("non_compliant", []) or []
    expired = payload.get("expired", []) or []
    items = _collect_items_with_age(payload)
    warn_items, error_items = _classify_by_ci_age(items)

    if non_compliant:
        print_warn(f"命名不合规项 {len(non_compliant)} 个（建议重命名含用途前缀+YYYYMMDD）:")
        for it in non_compliant:
            print(f"  - {_format_item(it, project_root)}")

    if warn_items:
        print_warn(f"CI 警告：年龄超 {CI_WARN_AGE_DAYS} 天的项 {len(warn_items)} 个（不阻塞）:")
        for it in warn_items:
            print(f"  - {_format_item(it, project_root)}")

    if error_items:
        print_error(f"CI 错误：年龄超 {CI_ERROR_AGE_DAYS} 天的项 {len(error_items)} 个（阻塞）:")
        for it in error_items:
            print(f"  - {_format_item(it, project_root)}")

    if not non_compliant and not warn_items and not error_items:
        print_pass("所有 .temp/ 内容均在 CI 阈值内（无 >14 天项）")

    print_summary(
        pass_count=1 if not error_items else 0,
        warn_count=len(warn_items),
        error_count=len(error_items),
    )
    return exit_code


def run_ci_check(project_root: Path | str | None = None) -> int:
    """CI 质量门禁入口：>30 天阻塞，14-30 天警告不阻塞。

    Returns:
        0 = 通过或仅警告；1 = 存在 >30 天项（阻塞流水线）。
    """
    root = Path(project_root).resolve() if project_root else resolve_project_root(__file__)
    result = run_check(root)

    if result.passed and not result.warnings:
        print(f"[temp_lifecycle] PASS: .temp/ 无超 {CI_WARN_AGE_DAYS} 天内容")
        return 0

    if result.warnings:
        print(f"[temp_lifecycle] WARN: 检测到 {result.warning_count} 项超 {CI_WARN_AGE_DAYS} 天"
              f"（未达 {CI_ERROR_AGE_DAYS} 天，不阻塞流水线）:")
        for w in result.warnings:
            print(f"  - {w}")

    if not result.passed:
        print(f"[temp_lifecycle] ERROR: 检测到 {result.error_count} 项超 {CI_ERROR_AGE_DAYS} 天，"
              f"阻塞流水线")
        for e in result.errors:
            print(f"  - {e}")
        print("[temp_lifecycle] 清理指引: python .agents/scripts/check-temp-lifecycle.py --clean")
        return 1

    return 0


def run_precommit_check(project_root: Path | str | None = None) -> int:
    """pre-commit 入口：仅 >30 天项阻塞提交（与 CI 错误阈值一致）。

    14-30 天项在 pre-commit 中仅打印提示，不阻塞提交（保持提交流畅）。

    Returns:
        0 = 通过或仅提示；1 = 存在 >30 天项（阻塞提交）。
    """
    root = Path(project_root).resolve() if project_root else resolve_project_root(__file__)
    result = run_check(root)

    if result.passed and not result.warnings:
        return 0

    if result.warnings:
        print(f"[temp_lifecycle] 提示: {result.warning_count} 项超 {CI_WARN_AGE_DAYS} 天"
              f"（未达 {CI_ERROR_AGE_DAYS} 天，不阻塞提交）")

    if not result.passed:
        print(f"[temp_lifecycle] ERROR: 检测到 {result.error_count} 项超 {CI_ERROR_AGE_DAYS} 天，"
              f"阻塞提交")
        for e in result.errors:
            print(f"  - {e}")
        print("[temp_lifecycle] 清理指引: python .agents/scripts/check-temp-lifecycle.py --clean")
        return 1

    return 0


__all__ = [
    "run",
    "run_check",
    "run_ci_check",
    "run_precommit_check",
    "CI_WARN_AGE_DAYS",
    "CI_ERROR_AGE_DAYS",
]
