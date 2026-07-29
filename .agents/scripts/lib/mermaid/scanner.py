"""Mermaid 文件扫描器。"""


# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

from pathlib import Path
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
        for md in self.root_dir.rglob("*.md"):
            if self._should_include(md):
                files.append(md)
        return files

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

