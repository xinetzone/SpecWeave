"""本地安全：CSRF 双提交令牌 + Origin/Referer 本地白名单 + 单实例文件锁。"""

import os
import secrets
from pathlib import Path
from urllib.parse import urlparse

from ..errors import WorkspaceError

CSRF_COOKIE = "zhihu_checkin_csrf"
CSRF_FIELD = "_csrf"
LOCAL_HOSTS = {"127.0.0.1", "localhost", "[::1]", "::1"}
UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def issue_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def is_local_origin(value: str) -> bool:
    parsed = urlparse(value)
    host = parsed.hostname or ""
    return host in {"127.0.0.1", "localhost", "::1"}


def verify_post(request, cookie_token: str | None) -> tuple[bool, str]:
    """供中间件调用：返回（是否放行, 拒绝原因）。"""
    origin = request.headers.get("origin")
    if origin:
        if not is_local_origin(origin):
            return False, f"非本地 Origin 已拒绝：{origin}"
    referer = request.headers.get("referer")
    if not origin and referer:
        if not is_local_origin(referer):
            return False, f"非本地 Referer 已拒绝：{referer}"
    if not cookie_token:
        return False, "缺少 CSRF Cookie"
    return True, ""


class SingleInstanceLock:
    """对 local/.serve.lock 加字节区间锁；进程退出时由 OS 自动释放。"""

    LOCK_BYTES = 1

    def __init__(self, lock_path: Path) -> None:
        self.path = lock_path
        self._fh = None

    def acquire_nonblocking(self) -> None:
        """非阻塞加锁；锁被占用时立即抛 WorkspaceError（单实例 fail-fast，不等待）。"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fh = open(self.path, "a+b")  # noqa: SIM115 - 生命周期随进程，由 release/OS 管理
        try:
            if os.name == "nt":
                import msvcrt

                # msvcrt 区间锁作用于实际字节；空文件需先落一个字节
                fh.seek(0, os.SEEK_END)
                if fh.tell() < self.LOCK_BYTES:
                    fh.write(b"0")
                    fh.flush()
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, self.LOCK_BYTES)
            else:
                import fcntl

                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            fh.close()
            raise WorkspaceError(
                f"检测到另一个 zhihu-checkin 工作台正在使用该工作区（锁：{self.path}）。"
                "请关闭原窗口后再启动，避免并发写坏 tracker.md。"
            ) from exc
        self._fh = fh

    def release(self) -> None:
        if self._fh is None:
            return
        try:
            if os.name == "nt":
                import msvcrt

                self._fh.seek(0)
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, self.LOCK_BYTES)
            else:
                import fcntl

                fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
        finally:
            self._fh.close()
            self._fh = None
