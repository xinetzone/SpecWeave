"""Git 忽略规则检查（来自 check-gitignore.py）。"""

import subprocess
import sys
from pathlib import Path

from constants import REQUIRED_RULES, TEMP_PATHS
from lib.cli import print_header


def _check_rules(gitignore_path: Path) -> list[str]:
    if not gitignore_path.exists():
        return [f"错误: .gitignore 文件不存在于 {gitignore_path}"]
    content = gitignore_path.read_text(encoding="utf-8")
    return [rule for rule in REQUIRED_RULES if rule not in content]


def _is_actually_ignored(project_root: Path, file_path: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "check-ignore", "-q", file_path],
            capture_output=True, text=True, cwd=str(project_root),
        )
        return result.returncode == 0
    except FileNotFoundError:
        return True


def _check_git_status(project_root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=str(project_root),
        )
        if result.returncode != 0:
            return [f"错误: git status 执行失败: {result.stderr}"]
        violations = []
        for line in result.stdout.splitlines():
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ")[-1].strip()
            for temp_path in TEMP_PATHS:
                if temp_path in line:
                    if not _is_actually_ignored(project_root, path):
                        break
                    violations.append(line.strip())
                    break
        return violations
    except FileNotFoundError:
        return ["错误: git 命令未找到，请确保 git 已安装并添加到 PATH"]


def run(project_root: Path, args) -> int:
    gitignore_path = project_root / ".gitignore"
    print_header("Git 忽略规则验证")

    print("\n1. 检查 .gitignore 规则覆盖...")
    missing = _check_rules(gitignore_path)
    if missing:
        print(f"   失败: 缺少以下规则: {', '.join(missing)}")
        return 1
    print(f"   通过: 所有 {len(REQUIRED_RULES)} 条必需规则均已覆盖")

    print("\n2. 检查 git status 输出...")
    violations = _check_git_status(project_root)
    if violations:
        print("   失败: git status 输出中包含临时依赖路径:")
        for v in violations:
            print(f"     - {v}")
        return 1
    print("   通过: git status 输出中不包含临时依赖路径")

    print()
    print_header("验证通过: 所有临时依赖路径已被 .gitignore 覆盖")
    return 0
