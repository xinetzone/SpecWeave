"""Mermaid 文件扫描器。"""


# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

import os
from pathlib import Path
import subprocess
from typing import Set, List

try:
    from constants import EXCLUDED_DIRS
    from lib.project import is_non_worktree_path
except ImportError:
    EXCLUDED_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv'}

    def is_non_worktree_path(path: Path, root: Path) -> bool:
        return False


class FileScanner:
    def __init__(self, root_dir: Path, exclude_dirs: Set[str]):
        self.root_dir = root_dir
        self.exclude_dirs = exclude_dirs

    def scan(self) -> List[Path]:
        files = []
        for current, directories, filenames in os.walk(self.root_dir):
            current_dir = Path(current)
            directories[:] = sorted(
                name
                for name in directories
                if self._should_descend(current_dir / name)
            )
            for filename in sorted(filenames):
                md = current_dir / filename
                if md.match("*.md") and self._should_include(md):
                    files.append(md)
        ignored_paths = self._git_ignored_paths(files)
        return [
            path for path in files
            if path.relative_to(self.root_dir).as_posix() not in ignored_paths
        ]

    def _git_ignored_paths(self, files: List[Path]) -> Set[str]:
        if not files:
            return set()
        paths = [
            path.relative_to(self.root_dir).as_posix()
            for path in files
        ]
        try:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(self.root_dir),
                    "check-ignore",
                    "-z",
                    "--stdin",
                ],
                input="\0".join(paths) + "\0",
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
        except OSError:
            return set()
        if result.returncode not in (0, 1):
            return set()
        return {path for path in result.stdout.split("\0") if path}

    def _should_descend(self, path: Path) -> bool:
        if path.name in EXCLUDED_DIRS or is_non_worktree_path(path, self.root_dir):
            return False
        try:
            relative_path = path.relative_to(self.root_dir).as_posix()
        except ValueError:
            relative_path = str(path)
        return not any(
            relative_path.startswith(exclude.replace("\\", "/"))
            for exclude in self.exclude_dirs
        )

    def _should_include(self, path: Path) -> bool:
        parts = set(path.parts)
        if EXCLUDED_DIRS & parts:
            return False
        if is_non_worktree_path(path, self.root_dir):
            return False
        try:
            rel = path.relative_to(self.root_dir).as_posix()
        except ValueError:
            rel = str(path)
        if any(rel.startswith(excl.replace("\\", "/")) for excl in self.exclude_dirs):
            return False
        return True
