#!/usr/bin/env python3
"""原子化操作收尾脚本：自动完成断链修复、导航更新、看板刷新等后处理工作。

在文档/代码原子化拆分、文件移动、目录重构等操作完成后运行，一键执行：
  1. 自动检测并修复断链（相对路径层级校正、绝对路径转换等）
  2. 更新文档导航表
  3. 更新 Spec 执行进度看板
  4. 输出验证摘要

用法：
  python finalize-atomization.py                        # 完整后处理（实际执行修复）
  python finalize-atomization.py --dry-run              # 预览模式，不修改文件
  python finalize-atomization.py --no-links             # 跳过链接修复
  python finalize-atomization.py --no-nav               # 跳过导航表更新
  python finalize-atomization.py --no-dashboard         # 跳过看板更新
  python finalize-atomization.py --scope <path>         # 只检查指定目录/文件范围内的链接
  python finalize-atomization.py --scope staged         # 只检查git暂存区变更的文件
  python finalize-atomization.py --scope HEAD~1         # 只检查最近一次提交变更的文件
  python finalize-atomization.py --scope <commit-ish>   # 只检查指定提交/分支范围变更的文件
"""

import argparse
import subprocess
import sys
from pathlib import Path

from lib.project import resolve_project_root
from lib.cli import print_header, print_pass, print_warn, print_error
from lib.link_fixer import fix_broken_links, print_fix_report
from constants import EXCLUDED_DIRS


def get_git_changed_files(project_root: Path, revision: str = "staged") -> list[Path]:
    """通过git获取变更的文件列表。

    Args:
        project_root: 项目根目录。
        revision: "staged"表示暂存区，commit-ish表示指定提交范围（如HEAD~1, HEAD~3..HEAD）。

    Returns:
        变更文件的绝对路径列表（仅包含存在的.md文件）。
    """
    if revision == "staged":
        cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"]
    else:
        cmd = ["git", "diff", "--name-only", "--diff-filter=ACMR", revision]

    try:
        result = subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode != 0:
            print_warn(f"  git命令失败: {result.stderr.strip()}")
            return []

        files = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            file_path = (project_root / line).resolve()
            if file_path.exists() and file_path.suffix == ".md":
                files.append(file_path)
        return files
    except FileNotFoundError:
        print_warn("  git不可用，无法获取变更文件列表")
        return []
    except Exception as e:
        print_warn(f"  获取git变更文件失败: {e}")
        return []


def resolve_scope(scope_str: str, project_root: Path) -> tuple[Path | list[Path], str]:
    """解析--scope参数，返回扫描目标和描述信息。

    Args:
        scope_str: --scope参数值。
        project_root: 项目根目录。

    Returns:
        (target, description) 元组：
        - target为Path时表示目录/文件；为list[Path]时表示多个文件。
        - description为人类可读的范围描述。
    """
    if scope_str in ("staged", "--staged", "--cached"):
        files = get_git_changed_files(project_root, "staged")
        if not files:
            print_warn("  暂存区没有.md文件变更")
        return files, f"git暂存区（{len(files)}个.md文件）"

    scope_path = Path(scope_str)
    if not scope_path.is_absolute():
        scope_path = (project_root / scope_path).resolve()

    if scope_path.exists():
        if scope_path.is_dir():
            return scope_path, f"目录 {scope_path.relative_to(project_root)}"
        else:
            return [scope_path], f"文件 {scope_path.relative_to(project_root)}"

    try:
        files = get_git_changed_files(project_root, scope_str)
        if files:
            return files, f"git范围 {scope_str}（{len(files)}个.md文件）"
    except Exception:
        pass

    print_warn(f"  无法解析scope: {scope_str}，将使用整个项目根目录")
    return project_root, f"整个项目（默认，无法解析scope={scope_str}）"


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
        import traceback
        traceback.print_exc()
        return None


def run_link_fix(target: Path | list[Path], project_root: Path, dry_run: bool) -> int:
    """步骤1：自动修复断链。支持目录/文件/文件列表三种target类型。"""
    if isinstance(target, list):
        all_fixes = []
        for f in target:
            fixes = fix_broken_links(
                f,
                project_root=project_root,
                exclude_dirs=EXCLUDED_DIRS,
                dry_run=dry_run,
                verbose=False,
            )
            all_fixes.extend(fixes)

        if not all_fixes:
            print_pass("范围内所有链接均有效，无需修复")
            return 0

        broken_count = sum(1 for f in all_fixes if f.fix_type == "unresolved")
        fixed_count = len(all_fixes) - broken_count
        print_fix_report(all_fixes)

        if dry_run:
            print(f"\n  预览完成: 可修复 {fixed_count} 处，{broken_count} 处无法自动修复")
        else:
            print(f"\n  修复完成: 已修复 {fixed_count} 处，{broken_count} 处需人工处理")
        return 0 if broken_count == 0 else 1

    fixes = fix_broken_links(
        target,
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
        help="指定扫描修复的目标目录或文件（默认整个项目根目录）"
    )
    parser.add_argument(
        "--scope", "-s",
        type=str,
        default=None,
        help="限定检查范围：目录路径、'staged'（git暂存区）、或commit-ish（如HEAD~1、HEAD~3..HEAD）"
    )
    args = parser.parse_args()

    project_root = resolve_project_root(__file__)

    if args.scope:
        target, scope_desc = resolve_scope(args.scope, project_root)
    elif args.target:
        target = args.target.resolve()
        if target.is_dir():
            scope_desc = f"目录 {target.relative_to(project_root)}"
        else:
            scope_desc = f"文件 {target.relative_to(project_root)}"
    else:
        target = project_root
        scope_desc = "整个项目根目录"

    print_header("原子化操作收尾工具")
    print(f"  项目根: {project_root}")
    print(f"  检查范围: {scope_desc}")
    mode = "预览模式（dry-run）" if args.dry_run else "实际执行"
    print(f"  模式: {mode}")

    if args.scope and not args.no_nav and not args.no_dashboard:
        print_warn("  提示: --scope仅限制链接检查范围，导航表和看板更新仍为全项目")

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

    if not args.no_links:
        code = run_step("自动检测并修复断链", run_link_fix, target, project_root, args.dry_run)
        if code is not None and code != 0:
            exit_code = code

    if not args.no_nav:
        code = run_step("更新文档导航表", run_generate_nav, project_root, args.dry_run)
        if code is not None and code != 0:
            exit_code = code

    if not args.no_dashboard:
        code = run_step("更新 Spec 执行进度看板", run_generate_dashboard, project_root, args.dry_run)
        if code is not None and code != 0:
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
