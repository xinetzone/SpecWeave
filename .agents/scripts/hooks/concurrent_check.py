#!/usr/bin/env python3
"""
并发模块安全检查钩子：六维检查法
在 git commit 前自动扫描暂存的 Python 文件中的并发安全隐患。

集成方式：
  由 pre_commit.py 主钩子在敏感信息检测通过后调用。

环境变量控制：
  CONCURRENT_CHECK_SKIP=1        完全跳过并发安全检查
  CONCURRENT_CHECK_WARN_ONLY=1   检测到错误只警告不阻断（紧急修复用）
  SKIP=concurrent-safety-check   同上（兼容 pre-commit 框架习惯）
  CONCURRENT_CHECK_DIM=TIMEOUT   仅检查指定维度
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


DIMENSION_NAMES = {
    "TIMEOUT": "超时",
    "IDEMPOTENT": "幂等",
    "BOUNDARY": "边界",
    "DEFENSIVE": "防御",
    "CONFIG": "配置",
    "I18N": "国际化",
}


def _env_truthy(name: str) -> bool:
    val = os.environ.get(name, "").strip().lower()
    return val in ("1", "true", "yes", "on")


def _skip_requested() -> tuple[bool, str]:
    if _env_truthy("CONCURRENT_CHECK_SKIP"):
        return True, "CONCURRENT_CHECK_SKIP=1"
    skip_env = os.environ.get("SKIP", "").strip().lower()
    if "concurrent-safety" in skip_env or "concurrent_check" in skip_env:
        return True, f"SKIP={os.environ.get('SKIP', '')}"
    return False, ""


def _warn_only() -> bool:
    if _env_truthy("CONCURRENT_CHECK_WARN_ONLY"):
        return True
    skip_env = os.environ.get("SKIP", "").strip().lower()
    return "concurrent-safety-warn" in skip_env


def _dimension_filter() -> str | None:
    dim = os.environ.get("CONCURRENT_CHECK_DIM", "").strip().upper()
    if dim in DIMENSION_NAMES:
        return dim
    return None


def run_concurrent_check(project_root: Path, staged_files: list[Path]) -> int:
    """运行并发安全检查，返回 0=通过，1=阻断。"""
    skip, skip_reason = _skip_requested()
    warn_only_mode = _warn_only()
    dim_filter = _dimension_filter()

    print("=" * 60)
    print("⚡ 并发模块安全检查 (Pre-commit Hook) - 六维检查法")
    if warn_only_mode:
        print("   [警告模式] 检测到错误仅警告，不阻断提交")
    if dim_filter:
        print(f"   [维度过滤] 仅检查 {dim_filter}（{DIMENSION_NAMES.get(dim_filter, '')}）")
    print("=" * 60)

    if skip:
        print(f"\n⚠️  检测到 {skip_reason}，已跳过并发安全检查。")
        print("   请确保提交的并发代码无死锁/活锁风险！")
        print()
        return 0

    scripts_dir = project_root / ".agents" / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    py_files = [
        f for f in staged_files
        if f.suffix == ".py" and (project_root / f).exists()
    ]

    if not py_files:
        print("\n✅ 暂存区无 Python 文件，跳过并发安全检查。")
        print()
        return 0

    print(f"\n📋 待检查 Python 文件: {len(py_files)} 个")
    for f in py_files[:5]:
        print(f"   - {f}")
    if len(py_files) > 5:
        print(f"   ... 及其他 {len(py_files) - 5} 个文件")

    try:
        from lib.check_concurrent_safety import scan_python_file
    except ImportError as e:
        print(f"\n⚠️  无法加载并发安全检查模块: {e}")
        print("   尝试使用 CLI 脚本扫描...")
        check_script = scripts_dir / "check-concurrent-safety.py"
        if not check_script.exists():
            print("❌ 无法找到并发安全检查脚本，请确认 .agents/scripts/ 完整")
            return 1
        cmd = [sys.executable, str(check_script)]
        if dim_filter:
            cmd += ["-d", dim_filter]
        if warn_only_mode:
            pass
        result = 0
        for f in py_files:
            r = __import__("subprocess").run(
                cmd + ["-f", str(project_root / f)],
                cwd=str(scripts_dir),
            )
            if r.returncode != 0:
                result = r.returncode if not warn_only_mode else 0
        return result

    errors: list[tuple[Path, object]] = []
    warnings: list[tuple[Path, object]] = []
    infos: list[tuple[Path, object]] = []

    print("\n🔍 正在扫描暂存 Python 文件的并发安全问题...")
    for rel_path in py_files:
        abs_path = project_root / rel_path
        try:
            report = scan_python_file(abs_path, project_root)
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue

        for issue in report.issues:
            if dim_filter and issue.dimension != dim_filter and issue.code != "CC-PARSE":
                continue
            if issue.severity == "error":
                errors.append((rel_path, issue))
            elif issue.severity == "warn":
                warnings.append((rel_path, issue))
            else:
                infos.append((rel_path, issue))

    print()

    if infos and os.environ.get("CONCURRENT_CHECK_VERBOSE"):
        print(f"ℹ️  信息项: {len(infos)}")
        for rel_path, issue in infos[:5]:
            print(f"   {rel_path}:L{issue.line} [{issue.dimension_name}] {issue.message}")
        print()

    if warnings:
        print(f"⚠️  检测到 {len(warnings)} 项警告（不阻断提交）:")
        print("-" * 60)
        current_file = None
        for rel_path, issue in warnings:
            if str(rel_path) != current_file:
                print(f"\n  📄 {rel_path}:")
                current_file = str(rel_path)
            print(f"     L{issue.line} ⚠ [{issue.dimension_name}] {issue.message}")
        print()

    if errors:
        if warn_only_mode:
            print(f"⚠️  检测到 {len(errors)} 项并发安全错误（警告模式，不阻断）:")
        else:
            print(f"❌ 检测到 {len(errors)} 项并发安全错误，提交已阻断！")
        print("-" * 60)
        current_file = None
        for rel_path, issue in errors:
            if str(rel_path) != current_file:
                print(f"\n  📄 {rel_path}:")
                current_file = str(rel_path)
            icon = "⚠" if warn_only_mode else "✗"
            print(f"     L{issue.line} {icon} [{issue.dimension_name}] {issue.message}")

        if warn_only_mode:
            print("\n" + "=" * 60)
            print("⚠️  当前为警告模式，提交将继续。请务必处理上述错误！")
            print("=" * 60)
            return 0

        print("\n" + "=" * 60)
        print("💡 修复方法:")
        print("  1. 根据上述提示修复并发安全问题")
        print("  2. 运行完整扫描: python .agents/scripts/check-concurrent-safety.py")
        print(f"  3. 查看问题文件: 对应行已标注维度标签（TIMEOUT/IDEMPOTENT/BOUNDARY/DEFENSIVE/CONFIG/I18N）")
        print("")
        print("🔓 临时跳过方式（仅限紧急情况）:")
        print("  4. 仅跳过并发检查: CONCURRENT_CHECK_SKIP=1 git commit")
        print("  5. 只警告不阻断: CONCURRENT_CHECK_WARN_ONLY=1 git commit")
        print("  6. 跳过所有钩子: git commit --no-verify  (最不推荐！)")
        print("=" * 60)
        return 1

    if warnings:
        print("✅ 未检测到并发安全错误。建议处理上述警告后再提交。")
        print("   可运行: python .agents/scripts/check-concurrent-safety.py -v 查看详情")
        print()
        return 0

    print("✅ 未检测到并发安全问题，可以提交。")
    print()
    return 0
