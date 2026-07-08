#!/usr/bin/env python3
"""
Pre-commit 钩子入口：敏感信息检测 + 并发模块安全八维检查
在 git commit 前自动扫描暂存文件中的高风险问题并阻断提交。

检查链路：
  1. 敏感信息检测（密码/密钥/Token 等）
  2. 并发模块安全八维检查（超时/幂等/边界/防御/配置/国际化/死锁/泄漏）

使用方式：
  1. 通过 install-hooks.py 自动安装（推荐）
  2. 手动复制本文件到 .git/hooks/pre-commit 并添加执行权限

环境变量控制：
  敏感信息检测：
    SENSITIVE_CHECK_SKIP=1     完全跳过敏感信息检查
    SENSITIVE_CHECK_WARN_ONLY=1  检测高风险但只警告不阻断（紧急修复用）
    SKIP=sensitive-info-check  同上（兼容 pre-commit 框架习惯）
  并发安全检查：
    CONCURRENT_CHECK_SKIP=1       完全跳过并发安全检查
    CONCURRENT_CHECK_WARN_ONLY=1  检测到错误只警告不阻断
    SKIP=concurrent-safety-check  同上
    CONCURRENT_CHECK_DIM=TIMEOUT  仅检查指定维度

Git 原生方式：
  git commit --no-verify     跳过所有钩子（不推荐，会跳过其他检查）
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _env_truthy(name: str) -> bool:
    val = os.environ.get(name, "").strip().lower()
    return val in ("1", "true", "yes", "on")


def _skip_requested() -> tuple[bool, str]:
    if _env_truthy("SENSITIVE_CHECK_SKIP"):
        return True, "SENSITIVE_CHECK_SKIP=1"
    skip_env = os.environ.get("SKIP", "").strip().lower()
    if "sensitive-info" in skip_env or "sensitive_check" in skip_env:
        return True, f"SKIP={os.environ.get('SKIP', '')}"
    return False, ""


def _warn_only() -> bool:
    if _env_truthy("SENSITIVE_CHECK_WARN_ONLY"):
        return True
    skip_env = os.environ.get("SKIP", "").strip().lower()
    return "sensitive-info-warn" in skip_env


def find_project_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return Path(__file__).resolve().parent.parent.parent
    return Path(result.stdout.strip())


def get_staged_files() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return []
    files = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if line:
            files.append(Path(line))
    return files


def _run_sensitive_check(project_root: Path, scripts_dir: Path, staged_files: list[Path]) -> int:
    skip, skip_reason = _skip_requested()
    warn_only_mode = _warn_only()

    if skip:
        print("=" * 60)
        print("🔒 敏感信息检测 (Pre-commit Hook)")
        print("=" * 60)
        print(f"\n⚠️  检测到 {skip_reason}，已跳过敏感信息检查。")
        print("   请确保本次提交不包含真实敏感信息！")
        print()
        return 0

    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    print("=" * 60)
    print("🔒 敏感信息检测 (Pre-commit Hook)")
    if warn_only_mode:
        print("   [警告模式] 检测到高风险仅警告，不阻断提交")
    print("=" * 60)

    if not staged_files:
        return 0

    print(f"\n📋 待提交文件: {len(staged_files)} 个")
    for f in staged_files[:5]:
        print(f"   - {f}")
    if len(staged_files) > 5:
        print(f"   ... 及其他 {len(staged_files) - 5} 个文件")

    try:
        from lib.checks.sensitive_info import (
            scan_file, SEVERITY_HIGH, SEVERITY_MEDIUM,
            SUPPORTED_EXTENSIONS, FILE_EXCLUDE_PATTERNS,
        )
    except ImportError:
        print("\n⚠️  无法加载检测模块，回退到 CLI 扫描...")
        check_script = scripts_dir / "check-sensitive-info.py"
        if check_script.exists():
            if warn_only_mode:
                result = subprocess.run(
                    [sys.executable, str(check_script)],
                    cwd=str(scripts_dir),
                )
                return 0
            else:
                result = subprocess.run(
                    [sys.executable, str(check_script), "--only-severity", "high"],
                    cwd=str(scripts_dir),
                )
                return result.returncode
        print("❌ 无法找到敏感信息检测脚本，请确认 .agents/scripts/ 完整")
        return 1

    high_findings: list[tuple[Path, object]] = []
    medium_findings: list[tuple[Path, object]] = []

    print("\n🔍 正在扫描暂存文件中的敏感信息...")
    for rel_path in staged_files:
        abs_path = project_root / rel_path
        if not abs_path.exists():
            continue
        if abs_path.name in FILE_EXCLUDE_PATTERNS:
            continue
        if abs_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        try:
            findings = scan_file(abs_path)
            for finding in findings:
                if finding.severity == SEVERITY_HIGH:
                    high_findings.append((rel_path, finding))
                elif finding.severity == SEVERITY_MEDIUM:
                    medium_findings.append((rel_path, finding))
        except (OSError, UnicodeDecodeError):
            continue

    print()

    if medium_findings:
        print(f"⚠️  检测到 {len(medium_findings)} 项中风险敏感信息（警告，不阻断提交）:")
        print("-" * 60)
        current_file = None
        for rel_path, f in medium_findings:
            if str(rel_path) != current_file:
                print(f"\n  📄 {rel_path}:")
                current_file = str(rel_path)
            match_preview = f.match[:60] + ("..." if len(f.match) > 60 else "")
            print(f"     L{f.line} ⚠ {f.rule_name}: {match_preview}")
        print()

    if high_findings:
        if warn_only_mode:
            print(f"⚠️  检测到 {len(high_findings)} 项高风险敏感信息（警告模式，不阻断）:")
        else:
            print(f"❌ 检测到 {len(high_findings)} 项高风险敏感信息，提交已阻断！")
        print("-" * 60)
        current_file = None
        for rel_path, f in high_findings:
            if str(rel_path) != current_file:
                print(f"\n  📄 {rel_path}:")
                current_file = str(rel_path)
            match_preview = f.match[:60] + ("..." if len(f.match) > 60 else "")
            fixable = "[可自动修复]" if f.fixable else "[需人工处理]"
            icon = "⚠" if warn_only_mode else "✗"
            print(f"     L{f.line} {icon} {f.rule_name} {fixable}")
            print(f"       匹配: {match_preview}")
            print(f"       建议: {f.suggestion}")

        if warn_only_mode:
            print("\n" + "=" * 60)
            print("⚠️  当前为警告模式，提交将继续。请务必处理上述高风险项！")
            print("=" * 60)
            return 0

        print("\n" + "=" * 60)
        print("💡 修复方法:")
        print("  1. 自动修复: python .agents/scripts/check-sensitive-info.py --fix")
        print("  2. 手动修复: 按上述建议替换敏感信息")
        print("  3. 示例数据: 在代码行尾添加 # nosec 标记（仅限示例/测试数据）")
        print("")
        print("🔓 临时跳过方式（仅限紧急情况）:")
        print("  4. 仅跳过敏感信息检查: SENSITIVE_CHECK_SKIP=1 git commit")
        print("  5. 只警告不阻断: SENSITIVE_CHECK_WARN_ONLY=1 git commit")
        print("  6. 跳过所有钩子: git commit --no-verify  (最不推荐！)")
        print("=" * 60)
        return 1

    if medium_findings:
        print("✅ 未检测到高风险敏感信息。建议处理上述中风险项后再提交。")
        print("   可运行: python .agents/scripts/check-sensitive-info.py --fix 自动修复")
        print()
        return 0

    print("✅ 未检测到敏感信息。")
    print()
    return 0


def main() -> int:
    project_root = find_project_root()
    scripts_dir = project_root / ".agents" / "scripts"

    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    staged_files = get_staged_files()

    if not staged_files:
        return 0

    result = _run_sensitive_check(project_root, scripts_dir, staged_files)
    if result != 0:
        return result

    try:
        from hooks.concurrent_check import run_concurrent_check
        return run_concurrent_check(project_root, staged_files)
    except ImportError as e:
        print("⚠️  并发安全检查模块未加载，跳过:", e)
        return 0


if __name__ == "__main__":
    sys.exit(main())
