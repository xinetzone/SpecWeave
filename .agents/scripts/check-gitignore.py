#!/usr/bin/env python3
"""验证 .gitignore 规则是否覆盖所有临时依赖路径，并检查 git status 输出。"""

import subprocess
import sys
from pathlib import Path

from constants import REQUIRED_RULES, TEMP_PATHS


def check_gitignore_rules(gitignore_path: Path) -> list[str]:
    """检查 .gitignore 是否包含所有必需规则。"""
    if not gitignore_path.exists():
        return [f"错误: .gitignore 文件不存在于 {gitignore_path}"]

    content = gitignore_path.read_text(encoding="utf-8")
    missing = []
    for rule in REQUIRED_RULES:
        if rule not in content:
            missing.append(rule)
    return missing


def check_git_status() -> list[str]:
    """检查 git status 输出是否包含临时依赖路径。"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )
        if result.returncode != 0:
            return [f"错误: git status 执行失败: {result.stderr}"]

        violations = []
        for line in result.stdout.splitlines():
            for temp_path in TEMP_PATHS:
                if temp_path in line:
                    violations.append(line.strip())
                    break
        return violations
    except FileNotFoundError:
        return ["错误: git 命令未找到，请确保 git 已安装并添加到 PATH"]


def main() -> int:
    project_root = Path(__file__).parent.parent.parent
    gitignore_path = project_root / ".gitignore"

    print("=" * 60)
    print("Git 忽略规则验证")
    print("=" * 60)

    # 检查 .gitignore 规则
    print("\n1. 检查 .gitignore 规则覆盖...")
    missing_rules = check_gitignore_rules(gitignore_path)
    if missing_rules:
        print(f"   失败: 缺少以下规则: {', '.join(missing_rules)}")
        return 1
    print(f"   通过: 所有 {len(REQUIRED_RULES)} 条必需规则均已覆盖")

    # 检查 git status 输出
    print("\n2. 检查 git status 输出...")
    violations = check_git_status()
    if violations:
        print("   失败: git status 输出中包含临时依赖路径:")
        for v in violations:
            print(f"     - {v}")
        return 1
    print("   通过: git status 输出中不包含临时依赖路径")

    print("\n" + "=" * 60)
    print("验证通过: 所有临时依赖路径已被 .gitignore 覆盖")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
