"""执行工作台定位与 local/ 目录布局（唯一的数据根）。"""

import os
from dataclasses import dataclass
from pathlib import Path

from ..errors import WorkspaceError

TRACKER_NAME = "tracker.md"
LOCAL_DIR = "local"


@dataclass(frozen=True)
class Workspace:
    """已校验的执行工作台布局。所有运行时产物只允许落在 ``local/`` 之内。"""

    root: Path

    @property
    def tracker(self) -> Path:
        return self.root / TRACKER_NAME

    @property
    def local(self) -> Path:
        return self.root / LOCAL_DIR

    @property
    def entries_dir(self) -> Path:
        return self.local / "entries"

    @property
    def posts_dir(self) -> Path:
        return self.local / "posts"

    @property
    def screenshots_dir(self) -> Path:
        return self.local / "screenshots"

    @property
    def backups_dir(self) -> Path:
        return self.local / "backups"

    @property
    def records_dir(self) -> Path:
        return self.local / "records"

    @property
    def gate_exports_dir(self) -> Path:
        return self.local / "gate-exports"

    def ensure_dirs(self) -> None:
        """幂等创建 local 数据子目录。"""
        for d in (
            self.local,
            self.entries_dir,
            self.posts_dir,
            self.screenshots_dir,
            self.backups_dir,
            self.records_dir,
            self.gate_exports_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)

    def ensure_within_local(self, path: Path) -> Path:
        """断言给定路径位于 local/ 之内，返回 resolve 后的路径。"""
        resolved = path.resolve()
        local_root = self.local.resolve()
        if local_root not in resolved.parents and resolved != local_root:
            raise WorkspaceError(f"写入路径越出 local/ 数据区：{path}")
        return resolved

    def is_local_ignored(self) -> bool:
        """检查工作区 .gitignore 是否忽略 local 内容（仅告警用途）。"""
        gitignore = self.root / ".gitignore"
        if not gitignore.is_file():
            return False
        rules = {
            line.strip()
            for line in gitignore.read_text(encoding="utf-8").splitlines()
        }
        return "local/*" in rules or "local/" in rules


def _is_root_or_direct_child(path: Path) -> bool:
    """是否为文件系统根（如 ``D:\\``）或根的直接子级（如 ``D:\\.temp``）。"""
    root = Path(path.anchor)
    return path == root or path.parent == root


def open_workspace(raw_path: str | os.PathLike[str], *, create_local: bool = True) -> Workspace:
    """校验并打开执行工作台。

    守卫顺序：存在性 → 根级越界 → tracker.md → local 准备。
    """
    path = Path(raw_path).expanduser()
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise WorkspaceError(
            f"工作区路径不存在：{path}。请用 --workspace 指定知乎变现执行工作台目录"
            f"（应包含 tracker.md 与 local/）。"
        ) from exc

    if not resolved.is_dir():
        raise WorkspaceError(f"工作区路径不是目录：{resolved}")

    if _is_root_or_direct_child(resolved):
        raise WorkspaceError(
            f"工作区路径落在文件系统根或其直接子级（{resolved}），已按越界守卫拒绝。"
            "请将 workspace 指向 projects/monetize/zhihu-monetization 或其副本。"
        )

    ws = Workspace(resolved)
    if not ws.tracker.is_file():
        raise WorkspaceError(
            f"目录中找不到 {TRACKER_NAME}：{resolved}。"
            "该目录不是知乎变现执行工作台，请检查 --workspace / ZHIHU_CHECKIN_WORKSPACE。"
        )

    if create_local:
        ws.ensure_dirs()
    elif not ws.local.is_dir():
        raise WorkspaceError(
            f"工作区缺少 {LOCAL_DIR}/ 目录（且未允许自动创建）：{resolved}"
        )
    return ws
