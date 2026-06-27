#!/usr/bin/env python3
"""原子化操作收尾脚本：自动完成断链修复、导航更新、看板刷新等后处理工作。

在文档/代码原子化拆分、文件移动、目录重构等操作完成后运行，一键执行：
  1. 自动检测并修复断链（相对路径层级校正、绝对路径转换等）
  2. 更新文档导航表
  3. 更新 Spec 执行进度看板
  4. 输出验证摘要

用法：
  python finalize-atomization.py              # 完整后处理（实际执行修复）
  python finalize-atomization.py --dry-run    # 预览模式，不修改文件
  python finalize-atomization.py --no-links   # 跳过链接修复
  python finalize-atomization.py --no-nav     # 跳过导航表更新
  python finalize-atomization.py --no-dashboard  # 跳过看板更新
"""

import argparse
import subprocess
import sys
from pathlib import Path

from lib.project import resolve_project_root
from lib.cli import print_header, print_pass, print_warn, print_error
from lib.link_fixer import fix_broken_links, print_fix_report
from constants import EXCLUDED_DIRS


def run_step(description: str, func, *args, **kwargs):
    """运行单个步骤并捕获结果。"""
    print(f"\n{'─' * 60}")
    print(f"  ▶ {description}")
    print(f"{'─' * 60}")
    try:
        result = func(*args, **kwargs)
        return result
    except Exception as e:
        print_error(f"  ✗ 步骤失败: {e}")
        return None


def run_link_fix(project_root: Path, dry_run: bool) -> int:
    """步骤1：自动修复断链。"""
    fixes = fix_broken_links(
        project_root,
        project_root=project_root,
        exclude_dirs=EXCLUDED_DIRS,
        dry_run=dry_run,
        verbose=True,
    )

    if not fixes:
        print_pass("所有链接均有效，无需修复")
        return 0

    broken_count = sum(1 for f in fixes if f.fix_type == "unresolved")
    fixed_count = len(fixes) - broken_count

    if dry_run:
        print(f"\n  预览完成: 可修复 {fixed_count} 处，{broken_count} 处无法自动修复")
    else:
        print(f"\n  修复完成: 已修复 {fixed_count} 处，{broken_count} 处需人工处理")

    return 0 if broken_count == 0 else 1


def run_generate_nav(project_root: Path, dry_run: bool) -> int:
    """步骤2：更新导航表（通过子进程调用 docgen.py nav）。"""
    script_path = project_root / ".agents" / "scripts" / "docgen.py"
    if not script_path.exists():
        print_warn(f"  脚本不存在: {script_path}")
        return 1

    cmd = [sys.executable, str(script_path), "nav"]
    if dry_run:
        print("  [dry-run] 将运行: python .agents/scripts/docgen.py nav")
        return 0

    result = subprocess.run(cmd, cwd=str(project_root), capture_output=True, text=True, encoding="utf-8")
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        if result.stderr:
            print_error(result.stderr)
        return result.returncode

    print_pass("导航表已更新")
    return 0


def run_generate_dashboard(project_root: Path, dry_run: bool) -> int:
    """步骤3：更新 Spec 执行进度看板（通过子进程调用 docgen.py dashboard）。"""
    script_path = project_root / ".agents" / "scripts" / "docgen.py"
    if not script_path.exists():
        print_warn(f"  脚本不存在: {script_path}")
        return 1

    cmd = [sys.executable, str(script_path), "dashboard"]
    if dry_run:
        print("  [dry-run] 将运行: python .agents/scripts/docgen.py dashboard")
        return 0

    result = subprocess.run(cmd, cwd=str(project_root), capture_output=True, text=True, encoding="utf-8")
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        if result.stderr:
            print_error(result.stderr)
        return result.returncode

    print_pass("Spec 看板已更新")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="原子化操作收尾脚本：自动修复链接、更新导航与看板"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="预览模式，仅显示将要执行的操作，不修改文件"
    )
    parser.add_argument("--no-links", action="store_true", help="跳过链接修复步骤")
    parser.add_argument("--no-nav", action="store_true", help="跳过导航表更新")
    parser.add_argument("--no-dashboard", action="store_true", help="跳过看板更新")
    parser.add_argument(
        "--target", "-t",
        type=Path,
        default=None,
        help="指定扫描修复的目标目录（默认整个项目根目录）"
    )
    args = parser.parse_args()

    project_root = resolve_project_root(__file__)
    target = args.target.resolve() if args.target else project_root

    print_header("原子化操作收尾工具")
    print(f"  项目根: {project_root}")
    print(f"  目标目录: {target}")
    mode = "预览模式（dry-run）" if args.dry_run else "实际执行"
    print(f"  模式: {mode}")

    skipped = []
    if args.no_links:
        skipped.append("链接修复")
    if args.no_nav:
        skipped.append("导航表更新")
    if args.no_dashboard:
        skipped.append("看板更新")
    if skipped:
        print(f"  跳过: {', '.join(skipped)}")

    exit_code = 0

    # 步骤 1：链接修复
    if not args.no_links:
        code = run_step("自动检测并修复断链", run_link_fix, target if args.target else project_root, args.dry_run)
        if code != 0:
            exit_code = code

    # 步骤 2：导航表更新
    if not args.no_nav:
        code = run_step("更新文档导航表", run_generate_nav, project_root, args.dry_run)
        if code != 0:
            exit_code = code

    # 步骤 3：Spec 看板更新
    if not args.no_dashboard:
        code = run_step("更新 Spec 执行进度看板", run_generate_dashboard, project_root, args.dry_run)
        if code != 0:
            exit_code = code

    print(f"\n{'=' * 60}")
    if exit_code == 0:
        print_pass("✓ 原子化收尾完成")
    else:
        print_warn(f"⚠ 部分步骤有警告（exit code: {exit_code}），请检查上面的输出")
    print(f"{'=' * 60}")

    if not args.dry_run and exit_code == 0:
        print("\n提示：如需进一步验证，可运行:")
        print("  python .agents/scripts/check-links.py           # 完整链接检查")
        print("  python .agents/scripts/ci-check.ps1             # 全量 CI 检查")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
