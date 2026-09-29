"""文件仓库：JSON 表存储 + 原子写 + 跨平台单实例锁。

设计要点：
- 每张表一个 JSON 文件，写入使用 ``pid + random`` 临时名 + ``os.replace``
  原子替换（避免并发互踩与崩溃后半写残留）；
- 单实例锁复用仓库既有范式（Windows ``msvcrt`` / POSIX ``fcntl`` 非阻塞），
  进程被强杀时由操作系统自动释放；
- 运行期数据目录存放密文与摘要，**禁止入库**（见 ``.gitignore``）。
"""

import json
import os
import secrets
import sys
import tempfile
import time
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from ..errors import ByokError, ErrorCode
from ..logging_utils import get_logger

logger = get_logger("storage")

#: 单实例锁的默认等待上限（秒）与重试间隔（秒）：非阻塞加锁 + 有限等待，绝不死等
DEFAULT_LOCK_TIMEOUT = 5.0
LOCK_RETRY_INTERVAL = 0.05


class StorageError(ByokError):
    def __init__(self, message: str) -> None:
        super().__init__(ErrorCode.INTERNAL_ERROR, message)


def atomic_write_text(path: Path, text: str) -> None:
    """原子写文本：``.<name>.<pid>.<rand>.tmp`` → ``os.replace``。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_name = f".{path.name}.{os.getpid()}.{secrets.token_hex(6)}.tmp"
    tmp_path = path.parent / tmp_name
    try:
        with tmp_path.open("w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():  # pragma: no cover - 异常清理路径
            tmp_path.unlink(missing_ok=True)


class Table[T: BaseModel]:
    """一张 JSON 表。"""

    def __init__(self, directory: Path, name: str, factory: Callable[[dict[str, Any]], T]) -> None:
        self.path = directory / f"{name}.json"
        self.factory = factory
        self._rows: list[T] | None = None

    def _load(self) -> list[T]:
        if self._rows is not None:
            return self._rows
        rows: list[T] = []
        if self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise StorageError(f"表 {self.path.name} 解析失败：{exc}") from exc
            for item in raw:
                rows.append(self.factory(item))
        self._rows = rows
        return rows

    def _flush(self) -> None:
        rows = self._load()
        payload = [row.model_dump(mode="json") for row in rows]
        atomic_write_text(self.path, json.dumps(payload, ensure_ascii=False, indent=2))

    def all(self) -> list[T]:
        return list(self._load())

    def find(self, predicate: Callable[[T], bool]) -> T | None:
        for row in self._load():
            if predicate(row):
                return row
        return None

    def where(self, predicate: Callable[[T], bool]) -> list[T]:
        return [row for row in self._load() if predicate(row)]

    def add(self, row: T) -> T:
        rows = self._load()
        rows.append(row)
        self._flush()
        return row

    def replace(self, predicate: Callable[[T], bool], row: T) -> T:
        rows = self._load()
        for index, existing in enumerate(rows):
            if predicate(existing):
                rows[index] = row
                self._flush()
                return row
        raise StorageError("待替换的记录不存在")

    def upsert(self, predicate: Callable[[T], bool], row: T) -> T:
        rows = self._load()
        for index, existing in enumerate(rows):
            if predicate(existing):
                rows[index] = row
                self._flush()
                return row
        rows.append(row)
        self._flush()
        return row

    def remove(self, predicate: Callable[[T], bool]) -> int:
        rows = self._load()
        kept = [row for row in rows if not predicate(row)]
        removed = len(rows) - len(kept)
        if removed:
            self._rows = kept
            self._flush()
        return removed

    def clear(self) -> None:
        self._rows = []
        self._flush()

    def extend(self, rows: Iterable[T]) -> None:
        target = self._load()
        target.extend(rows)
        self._flush()


class Repository:
    """聚合所有表的文件仓库。"""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._tables: dict[str, Table[Any]] = {}

    def table[T: BaseModel](
        self, name: str, factory: Callable[[dict[str, Any]], T]
    ) -> Table[T]:
        if name not in self._tables:
            self._tables[name] = Table(self.data_dir, name, factory)
        return self._tables[name]  # type: ignore[return-value]

    def raw_text(self) -> str:
        """把所有表拼成一段文本，供「落盘不含明文」的审计测试使用。"""
        parts: list[str] = []
        for path in sorted(self.data_dir.glob("*.json")):
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
        return "\n".join(parts)


class SingleInstanceLock:
    """跨平台非阻塞单实例锁；进程被强杀时由 OS 自动释放。"""

    def __init__(self, path: Path, *, timeout: float = DEFAULT_LOCK_TIMEOUT) -> None:
        self.path = Path(path)
        #: 获取锁的**上限等待时间**（秒）。非阻塞加锁 + 有限重试，绝不无限等待。
        self.timeout = timeout
        self._fh: Any = None

    # ------------------------------------------------------------ 加锁
    def acquire(self, *, timeout: float | None = None) -> None:
        """获取锁；``timeout``（默认 5s）内未拿到即抛 :class:`StorageError`。"""
        limit = self.timeout if timeout is None else timeout
        deadline = time.monotonic() + limit
        while True:
            if self._try_acquire_once():
                return
            if time.monotonic() >= deadline:
                raise StorageError(
                    f"已有实例在运行（{limit:g}s 内未获得锁 {self.path}）"
                )
            time.sleep(LOCK_RETRY_INTERVAL)

    def _try_acquire_once(self) -> bool:
        """尝试加锁一次：成功返回 True，已被占用返回 False（不抛异常）。"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            import msvcrt

            fh = open(self.path, "a+")  # noqa: SIM115 - 生命周期由 release 管理
            # 先写 PID 并把文件指针归零，再在**偏移 0** 处加锁；
            # release 也在偏移 0 处解锁，两个区域必须一致，否则 Windows 会报
            # PermissionError（解锁未加锁的区域）。
            fh.seek(0)
            fh.truncate()
            fh.write(str(os.getpid()))
            fh.flush()
            fh.seek(0)
            try:
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                fh.close()
                return False
            self._fh = fh
            return True
        import fcntl

        fh = open(self.path, "a+")  # noqa: SIM115
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            fh.close()
            return False
        fh.seek(0)
        fh.truncate()
        fh.write(str(os.getpid()))
        fh.flush()
        self._fh = fh
        return True

    def release(self) -> None:
        if self._fh is None:
            return
        try:
            if sys.platform == "win32":
                import msvcrt

                self._fh.seek(0)
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
        finally:
            self._fh.close()
            self._fh = None

    def __enter__(self) -> SingleInstanceLock:
        self.acquire(timeout=self.timeout)
        return self

    def __exit__(self, *_exc: object) -> None:
        self.release()


def temp_lock_path(data_dir: Path) -> Path:
    """在给定目录内生成一个临时锁路径（测试用）。"""
    return Path(data_dir) / f".instance-{secrets.token_hex(4)}.lock"


def ensure_clean_dir(path: Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="byok-", dir=path))
