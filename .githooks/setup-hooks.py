#!/usr/bin/env python3
"""
SpecWeave 团队 Git Hooks 一键配置脚本

用法:
    python .githooks/setup-hooks.py              # 配置当前仓库使用 .githooks 目录
    python .githooks/setup-hooks.py --global     # 配置全局 Git 模板目录（所有新仓库自动启用）
    python .githooks/setup-hooks.py --status     # 查看当前 hooks 配置状态
    python .githooks/setup-hooks.py --uninstall  # 卸载（恢复默认 .git/hooks）

工作原理:
    设置 git config core.hooksPath .githooks 后，Git 会从仓库内 .githooks/ 目录加载钩子。
    该目录被 Git 跟踪，团队成员 pull 代码后自动获得最新钩子，无需重复安装。
"""
from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path


def run_git(*args: str, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=check,
    )


def get_project_root() -> Path:
    result = run_git("rev-parse", "--show-toplevel")
    if result.returncode == 0:
        return Path(result.stdout.strip())
    return Path(__file__).resolve().parent.parent


def check_git_version() -> tuple[int, int] | None:
    result = run_git("--version")
    if result.returncode != 0:
        return None
    parts = result.stdout.strip().split()
    for part in parts:
        if "." in part:
            try:
                major, minor = part.split(".")[:2]
                return (int(major), int(minor))
            except (ValueError, IndexError):
                continue
    return None


def setup_repo_hooks(project_root: Path, force: bool = False) -> bool:
    githooks_dir = project_root / ".githooks"
    if not githooks_dir.exists():
        print(f"❌ .githooks 目录不存在: {githooks_dir}")
        return False

    result = run_git("config", "core.hooksPath")
    current = result.stdout.strip() if result.returncode == 0 else ""

    if current == ".githooks":
        print("✅ 当前仓库已配置使用 .githooks 目录")
        return True

    if current and not force:
        print(f"⚠️  当前 core.hooksPath = {current}")
        print("   使用 --force 覆盖")
        return False

    run_git("config", "core.hooksPath", ".githooks")
    print("✅ 已配置当前仓库使用 .githooks 目录")
    print(f"   git config core.hooksPath .githooks")

    pre_commit = githooks_dir / "pre-commit"
    if pre_commit.exists():
        try:
            pre_commit.chmod(
                pre_commit.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            )
        except OSError:
            pass
        print("✅ pre-commit 钩子已就绪")

    print()
    print("💡 现在 git commit 时将自动从 .githooks/ 加载钩子")
    print("   钩子更新随代码一起 pull，无需重复安装")
    return True


def setup_global_template(project_root: Path, force: bool = False) -> bool:
    home = Path.home()
    template_dir = home / ".git-templates" / "hooks"
    template_dir.mkdir(parents=True, exist_ok=True)

    githooks_dir = project_root / ".githooks"
    scripts_hooks_dir = project_root / ".agents" / "scripts" / "hooks"

    installed = 0
    for hook_name in ["pre-commit"]:
        src = githooks_dir / hook_name
        if not src.exists():
            src = scripts_hooks_dir / hook_name
        if not src.exists():
            print(f"  ⚠️  未找到 {hook_name} 钩子模板")
            continue

        dst = template_dir / hook_name
        if dst.exists() and not force:
            print(f"  ⏭️  全局模板 {hook_name} 已存在（使用 --force 覆盖）")
            continue
        if dst.exists() and force:
            backup = dst.with_suffix(".bak")
            shutil.copy2(dst, backup)

        shutil.copy2(src, dst)
        try:
            dst.chmod(dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except OSError:
            pass
        print(f"  ✅ 全局模板 {hook_name} 已安装")
        installed += 1

    result = subprocess.run(
        ["git", "config", "--global", "init.templateDir"],
        capture_output=True, text=True,
    )
    current_template = result.stdout.strip() if result.returncode == 0 else ""
    expected = str(home / ".git-templates").replace("\\", "/")

    if current_template != str(home / ".git-templates"):
        run_git("config", "--global", "init.templateDir", str(home / ".git-templates"))
        print(f"✅ 已配置全局模板目录: {home / '.git-templates'}")
    else:
        print("✅ 全局模板目录已配置")

    print()
    print(f"💡 之后 git clone/git init 的新仓库将自动获得钩子")
    print(f"   已有仓库需执行: python .githooks/setup-hooks.py")
    return installed > 0


def show_status(project_root: Path) -> None:
    print("=" * 50)
    print("📊 Git Hooks 配置状态")
    print("=" * 50)
    print()

    result = run_git("config", "core.hooksPath")
    repo_hooks = result.stdout.strip() if result.returncode == 0 else ""
    print(f"  当前仓库 hooksPath: {repo_hooks or '(默认 .git/hooks)'}")

    githooks_dir = project_root / ".githooks"
    if githooks_dir.exists():
        hooks = [f.name for f in githooks_dir.iterdir() if f.is_file() and not f.name.startswith(".") and f.name != "setup-hooks.py"]
        print(f"  .githooks/ 目录钩子: {', '.join(hooks) if hooks else '(无)'}")
    else:
        print("  .githooks/ 目录: 不存在")

    result = subprocess.run(
        ["git", "config", "--global", "init.templateDir"],
        capture_output=True, text=True,
    )
    global_template = result.stdout.strip() if result.returncode == 0 else ""
    print(f"  全局模板目录: {global_template or '(未配置)'}")

    result = run_git("--version")
    if result.returncode == 0:
        print(f"  Git 版本: {result.stdout.strip()}")
        version = check_git_version()
        if version and version < (2, 9):
            print("  ⚠️  Git 版本 < 2.9，core.hooksPath 可能不可用，建议升级")

    print()
    if repo_hooks == ".githooks":
        print("✅ 仓库级钩子已正确配置")
    else:
        print("💡 运行 python .githooks/setup-hooks.py 配置仓库钩子")


def uninstall_repo(project_root: Path) -> bool:
    result = run_git("config", "--unset", "core.hooksPath")
    if result.returncode == 0:
        print("✅ 已恢复使用默认 .git/hooks 目录")
        return True
    else:
        print("ℹ️  当前未配置自定义 hooksPath，无需卸载")
        return False


def main():
    parser = argparse.ArgumentParser(description="SpecWeave Git Hooks 配置工具")
    parser.add_argument("--global", dest="global_mode", action="store_true",
                        help="配置全局 Git 模板目录（所有新仓库自动启用）")
    parser.add_argument("--status", action="store_true", help="查看当前配置状态")
    parser.add_argument("--uninstall", action="store_true", help="卸载仓库级钩子配置")
    parser.add_argument("--force", "-f", action="store_true", help="覆盖已有配置")
    args = parser.parse_args()

    project_root = get_project_root()
    git_version = check_git_version()

    if args.status:
        show_status(project_root)
        return 0

    print("=" * 50)
    print("🔧 SpecWeave Git Hooks 配置")
    print(f"   项目根目录: {project_root}")
    if git_version:
        print(f"   Git 版本: {git_version[0]}.{git_version[1]}")
    print("=" * 50)
    print()

    if git_version and git_version < (2, 9):
        print("❌ Git 版本过低，core.hooksPath 需要 Git >= 2.9")
        print("   请升级 Git 后重试，或使用 install-hooks.py 安装到 .git/hooks/")
        return 1

    if args.uninstall:
        return 0 if uninstall_repo(project_root) else 1

    if args.global_mode:
        return 0 if setup_global_template(project_root, args.force) else 1

    return 0 if setup_repo_hooks(project_root, args.force) else 0


if __name__ == "__main__":
    sys.exit(main())
