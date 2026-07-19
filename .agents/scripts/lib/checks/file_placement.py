"""关键配置文件放置校验检查模块。

封装对 `check-file-placement.py` 的调用，供 ci-check、repo-check、pre_commit
等编排入口复用。检测分为两类：

1. 受管关键文件（MANAGED_FILES）：标准位置为 `.agents/scripts/`，若出现在
   项目根目录则判定为错误放置。
2. Glob 模式匹配（GLOB_PATTERNS）：根目录下不应出现的临时目录/文件模式，
   标准位置为 `.temp/`，如 `.tmp-ci-logs*`。

接口约定：
    - ``run(project_root, args) -> int``：遵循 lib/checks/ 通用约定，
      打印人类可读报告并返回退出码（0=通过，1=存在错误放置）。
    - ``run_check(project_root=None) -> CheckResult``：返回结构化结果，
      供 CI 集成与程序化调用使用。
    - ``run_ci_check(project_root=None) -> int``：CI 质量门禁入口，
      错误放置时报错误并返回 1（阻塞流水线），全部正确返回 0。

底层脚本退出码与 CI 策略一致（0=全部正确，1=存在错误放置），故 CI 直接以
退出码作为通过/失败判定。
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
_CHECK_SCRIPT_NAME = "check-file-placement.py"

# CI 策略：错误放置即阻塞（无警告分级）
CI_BLOCK_ON_MISPLACED = True


def _scripts_dir(project_root: Path) -> Path:
    """返回 .agents/scripts/ 目录路径。"""
    return project_root / ".agents" / "scripts"


def _invoke_script(project_root: Path) -> tuple[int, dict | None]:
    """以 --json 模式调用底层 check-file-placement.py。

    返回 (exit_code, parsed_json)。若脚本执行失败或 JSON 解析失败，
    parsed_json 为 None，exit_code 反映真实退出状态。
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


def run_check(project_root: Path | str | None = None) -> CheckResult:
    """执行放置校验并返回结构化 CheckResult。

    Args:
        project_root: 项目根目录。为 None 时自动定位（基于 AGENTS.md 标记）。

    Returns:
        CheckResult：name="file_placement"，errors 含每个错误放置项的描述，
        passed=True 表示全部正确。
    """
    root = Path(project_root).resolve() if project_root else resolve_project_root(__file__)
    exit_code, payload = _invoke_script(root)

    result = CheckResult(name="file_placement")
    if payload is None:
        result.passed = False
        result.errors.append("底层脚本未返回有效 JSON 结果，无法判定放置状态")
        return result

    summary = payload.get("summary", {}) or {}
    details = payload.get("details", []) or []
    misplaced = [d for d in details if d.get("status") == "misplaced"]

    if exit_code == 0 and not misplaced:
        result.passed = True
        return result

    result.passed = False
    for item in misplaced:
        filename = item.get("filename", "<未知文件>")
        current = item.get("current_path", "")
        standard = item.get("standard_path", "")
        fix_cmd = item.get("fix_command", "")
        msg = f"{filename} 被错误放置到根目录（当前: {current}；应位于: {standard}）"
        if fix_cmd:
            msg += f" | 修复: {fix_cmd}"
        result.errors.append(msg)
    return result


def run(project_root: Path, args: argparse.Namespace) -> int:
    """lib/checks/ 通用接口：打印人类可读报告并返回退出码。

    供 repo-check.py 等编排器调用。args 参数保留以兼容通用接口约定，
    本模块不读取额外参数。
    """
    print_header("关键配置文件放置校验 (lib/checks/file_placement)")
    result = run_check(project_root)

    if result.passed:
        print_pass("所有受管文件与临时目录均在正确位置")
        print_summary(pass_count=1, warn_count=0, error_count=0)
        return 0

    for err in result.errors:
        print_error(err)
    print()
    print_warn("修复指引（在项目根目录执行）:")
    for err in result.errors:
        if "| 修复: " in err:
            fix_cmd = err.split("| 修复: ", 1)[1]
            print(f"  {fix_cmd}")
    print_summary(pass_count=0, warn_count=0, error_count=result.error_count)
    return 1


def run_ci_check(project_root: Path | str | None = None) -> int:
    """CI 质量门禁入口：错误放置时阻塞流水线。

    CI 策略：错误放置 → ERROR（阻塞，退出码 1）；全部正确 → PASS（退出码 0）。

    Returns:
        0 = 通过；1 = 存在错误放置（阻塞流水线）。
    """
    root = Path(project_root).resolve() if project_root else resolve_project_root(__file__)
    result = run_check(root)

    if result.passed:
        print(f"[file_placement] PASS: 所有受管文件与临时目录放置正确")
        return 0

    print(f"[file_placement] ERROR: 检测到 {result.error_count} 项错误放置，阻塞流水线")
    for err in result.errors:
        print(f"  - {err}")
    print("[file_placement] 修复指引（在项目根目录执行）:")
    for err in result.errors:
        if "| 修复: " in err:
            fix_cmd = err.split("| 修复: ", 1)[1]
            print(f"  {fix_cmd}")
    return 1


__all__ = ["run", "run_check", "run_ci_check", "CI_BLOCK_ON_MISPLACED"]
