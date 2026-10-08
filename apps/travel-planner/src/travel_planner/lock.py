"""单实例文件锁：内核级排他锁，进程退出自动释放（无陈旧锁问题）。

同一数据目录同时只允许一个 travel-planner 实例持有锁（serve 命令使用）。
"""

import os
import sys
from pathlib import Path

from .errors import LockError

LOCK_FILENAME = "travel-planner.lock"


class InstanceLock:
    """数据目录级单实例锁。

    Windows 使用 ``msvcrt.locking``，POSIX 使用 ``fcntl.flock``；
    两者均为内核级锁：持有进程退出（含崩溃）后自动释放。
    """

    def __init__(self, data_dir: Path) -> None:
        self._path = data_dir / LOCK_FILENAME
        self._fd: int | None = None

    @property
    def held(self) -> bool:
        return self._fd is not None

    def acquire_nowait(self) -> None:
        """非阻塞获取锁（LK_NBLCK / LOCK_NB）：锁被持有时立即抛出中文 LockError。"""
        if self._fd is not None:
            return
        fd = os.open(self._path, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            os.lseek(fd, 0, os.SEEK_SET)
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(fd)
            raise LockError(
                "已有 travel-planner 实例正在运行（同一数据目录），请先关闭旧实例后再启动"
            ) from exc
        try:
            os.truncate(fd, 0)
            os.write(fd, str(os.getpid()).encode("ascii", "ignore"))
        except OSError:
            pass  # 锁文件内容仅作诊断参考，写失败不影响锁语义
        self._fd = fd

    def release(self) -> None:
        """释放锁（幂等）。"""
        fd = self._fd
        if fd is None:
            return
        self._fd = None
        try:
            os.lseek(fd, 0, os.SEEK_SET)
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)
