"""vendor 检查 Git 操作模块。

Git 命令执行封装、子模块路径加载、子模块判断等基础功能。
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess | None:
    """执行 git 命令，返回 CompletedProcess 或 None（git 不可用时）。"""
    try:
        return subprocess.run(
            ["git"] + args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None


def _load_submodule_paths(project_root: Path) -> set[str]:
    """从 .gitmodules 加载所有子模块路径。"""
    gm = project_root / ".gitmodules"
    if not gm.exists():
        return set()
    paths = set()
    for line in gm.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("path ="):
            paths.add(s.split("=", 1)[1].strip())
    return paths


def _is_submodule(lib_dir: Path, project_root: Path, submodule_paths: set[str]) -> bool:
    """判断目录是否为 git 子模块。"""
    rel_str = str(lib_dir.relative_to(project_root)).replace("\\", "/")
    if rel_str in submodule_paths:
        return True
    git_marker = lib_dir / ".git"
    return git_marker.exists() and git_marker.is_file()
