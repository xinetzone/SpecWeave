#!/usr/bin/env python3
"""
Git hooks 安装脚本（传统方式：复制到 .git/hooks/）

推荐团队分发方式：使用 python .githooks/setup-hooks.py 配置 core.hooksPath
钩子随代码更新自动生效，无需重复安装。

用法:
    python .agents/scripts/hooks/install-hooks.py          # 安装所有钩子到 .git/hooks/
    python .agents/scripts/hooks/install-hooks.py --force  # 覆盖已存在的钩子
    python .agents/scripts/hooks/install-hooks.py --uninstall  # 卸载钩子
"""
from __future__ import annotations

import argparse
import shutil
import stat
import sys
from pathlib import Path


HOOKS_TO_INSTALL = ["pre-commit"]


def find_project_root() -> Path:
    script_dir = Path(__file__).resolve().parent
    agents_dir = script_dir.parent.parent
    return agents_dir.parent


def install_hook(
    project_root: Path, hook_name: str, templates_dir: Path, force: bool = False
) -> bool:
    py_source = templates_dir / "pre_commit.py"
    sh_source = templates_dir / hook_name
    target = project_root / ".git" / "hooks" / hook_name

    if not py_source.exists():
        print(f"  ⚠️  钩子核心脚本 pre_commit.py 不存在，跳过")
        return False

    if target.exists() and not force:
        print(f"  ⏭️  {hook_name} 已存在，跳过（使用 --force 覆盖）")
        return False

    if target.exists() and force:
        backup = target.with_suffix(".bak")
        shutil.copy2(target, backup)
        print(f"  📦 已备份原有钩子到 {backup.name}")

    if sys.platform == "win32":
        cmd_target = project_root / ".git" / "hooks" / f"{hook_name}.cmd"
        cmd_content = f'@echo off\r\npython "%~dp0..\\..\\.agents\\scripts\\hooks\\pre_commit.py"\r\nif %errorlevel% neq 0 exit /b %errorlevel%\r\n'
        cmd_target.write_text(cmd_content, encoding="utf-8")
        print(f"  ✅ {hook_name}.cmd 已安装 (Windows CMD)")

        if sh_source.exists():
            shutil.copy2(sh_source, target)
        else:
            shutil.copy2(py_source, target)
            with open(target, encoding="utf-8") as f:
                content = f.read()
            if not content.startswith("#!"):
                content = "#!/usr/bin/env python3\n" + content
                target.write_text(content, encoding="utf-8")
        try:
            target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except OSError:
            pass
    else:
        if sh_source.exists():
            shutil.copy2(sh_source, target)
        else:
            shutil.copy2(py_source, target)
        target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print(f"  ✅ {hook_name} 已安装")
    return True


def uninstall_hook(project_root: Path, hook_name: str) -> bool:
    removed = False
    for suffix in ["", ".cmd"]:
        target = project_root / ".git" / "hooks" / f"{hook_name}{suffix}"
        if target.exists():
            target.unlink()
            print(f"  🗑️  {target.name} 已卸载")
            removed = True
        else:
            print(f"  ⏭️  {target.name} 未安装")
    return removed


def main():
    parser = argparse.ArgumentParser(description="安装 Git 钩子")
    parser.add_argument("--force", "-f", action="store_true", help="覆盖已存在的钩子")
    parser.add_argument("--uninstall", "-u", action="store_true", help="卸载钩子")
    args = parser.parse_args()

    project_root = find_project_root()
    templates_dir = Path(__file__).resolve().parent
    git_hooks_dir = project_root / ".git" / "hooks"

    if not git_hooks_dir.exists():
        print(f"❌ .git/hooks 目录不存在: {git_hooks_dir}")
        print("   请先在项目根目录执行 git init")
        return 1

    print("=" * 50)
    if args.uninstall:
        print("🗑️  卸载 Git 钩子")
    else:
        print("🔧 安装 Git 钩子")
    print(f"   项目根目录: {project_root}")
    print(f"   Git hooks 目录: {git_hooks_dir}")
    if sys.platform == "win32":
        print(f"   平台: Windows (额外安装 .cmd 包装器)")
    print("=" * 50)
    print()

    installed = 0
    for hook_name in HOOKS_TO_INSTALL:
        if args.uninstall:
            if uninstall_hook(project_root, hook_name):
                installed += 1
        else:
            if install_hook(project_root, hook_name, templates_dir, args.force):
                installed += 1

    print()
    if args.uninstall:
        print(f"✅ 已卸载 {installed} 个钩子")
    else:
        print(f"✅ 成功安装 {installed}/{len(HOOKS_TO_INSTALL)} 个钩子")
        if installed > 0:
            print()
            print("💡 提示:")
            print("   - 现在 git commit 时会自动执行两项检查：")
            print("     ① 敏感信息检测（密码/密钥/Token）— 高风险阻断提交")
            print("     ② 并发模块安全八维检查（超时/幂等/边界/防御/配置/国际化/死锁/泄漏）— 错误阻断提交")
            print("   - 中风险/警告级信息仅警告，不阻断提交")
            print("   - 使用 git commit --no-verify 可临时跳过所有钩子（不推荐）")
            print("   - 单独跳过敏感信息: SENSITIVE_CHECK_SKIP=1 git commit")
            print("   - 单独跳过并发检查: CONCURRENT_CHECK_SKIP=1 git commit")
            print("   - 自动修复敏感信息: python .agents/scripts/check-sensitive-info.py --fix")
            print("   - 运行并发检查: python .agents/scripts/check-concurrent-safety.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
