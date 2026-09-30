"""行程 JSON 文件存储：CRUD、原子写、滚动备份、路径守卫。

布局：``<data_dir>/trips/<id>.json`` + ``<data_dir>/backups/<id>-<时间戳>.json``。
所有写入路径必须位于数据目录之内（越界抛受控异常）。
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from .errors import StorageError, ValidationError
from .models import Trip, new_id

_BACKUP_TS = "%Y%m%d-%H%M%S-%f"


class TripStore:
    """行程文件存储（单用户、无并发，配合单实例锁使用）。"""

    def __init__(self, data_dir: Path, backup_keep: int = 5) -> None:
        self._dir = data_dir.resolve()
        self._trips_dir = self._dir / "trips"
        self._backups_dir = self._dir / "backups"
        self._backup_keep = max(1, backup_keep)
        self.load_errors: list[str] = []

    @property
    def data_dir(self) -> Path:
        return self._dir

    # ------------------------------------------------------------------ 路径守卫
    def _trip_path(self, trip_id: str) -> Path:
        if not trip_id or not isinstance(trip_id, str):
            raise StorageError("行程 id 不能为空")
        from .models import ID_PATTERN

        if not ID_PATTERN.match(trip_id):
            raise StorageError(f"行程 id 不合法：{trip_id!r}")
        path = (self._trips_dir / f"{trip_id}.json").resolve()
        if not path.is_relative_to(self._trips_dir):
            raise StorageError("写入路径越界（数据必须落在数据目录内）")
        return path

    # ------------------------------------------------------------------ 读取
    def list_trips(self) -> list[Trip]:
        """列出全部行程；损坏文件跳过并记录到 ``load_errors``（不阻塞列表页）。"""
        self.load_errors = []
        trips: list[Trip] = []
        if not self._trips_dir.is_dir():
            return trips
        for path in sorted(self._trips_dir.glob("*.json")):
            try:
                trips.append(self._load_path(path))
            except (StorageError, ValidationError) as exc:
                self.load_errors.append(f"{path.name}：{exc}")
        trips.sort(key=lambda t: (t.status == "archived", t.start_date or "9999", t.name))
        return trips

    def load(self, trip_id: str) -> Trip:
        path = self._trip_path(trip_id)
        if not path.is_file():
            raise StorageError(f"行程不存在：{trip_id}")
        return self._load_path(path)

    def _load_path(self, path: Path) -> Trip:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"读取失败：{path.name}（{exc.strerror}）") from exc
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise StorageError(f"JSON 解析失败（第 {exc.lineno} 行第 {exc.colno} 列附近）") from None
        return Trip.from_dict(data, path=f"行程文件 {path.name}")

    def count(self) -> int:
        return len(self.list_trips())

    def exists(self, trip_id: str) -> bool:
        """判断行程 id 是否已存在（id 格式非法视为不存在）。"""
        try:
            return self._trip_path(trip_id).is_file()
        except StorageError:
            return False

    # ------------------------------------------------------------------ 写入
    def save(self, trip: Trip) -> Trip:
        """校验并原子落盘；覆盖已有文件前先备份。"""
        # 白盒再校验（含日期范围与 day_index 边界，AC-2 的拦截点）
        checked = Trip.from_dict(trip.to_dict(), path=f"行程 {trip.id}")
        checked.updated_at = trip.updated_at or checked.updated_at
        path = self._trip_path(checked.id)
        if path.exists():
            self._backup(path)
        tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
        try:
            tmp.write_text(
                json.dumps(checked.to_dict(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            os.replace(tmp, path)
        except OSError as exc:
            tmp.unlink(missing_ok=True)
            raise StorageError(f"写入失败：{path.name}（{exc.strerror}）") from exc
        return checked

    def delete(self, trip_id: str) -> None:
        path = self._trip_path(trip_id)
        if not path.is_file():
            raise StorageError(f"行程不存在：{trip_id}")
        try:
            path.unlink()
        except OSError as exc:
            raise StorageError(f"删除失败：{path.name}（{exc.strerror}）") from exc

    def duplicate(self, trip_id: str) -> Trip:
        """复制行程：新 id、完成态重置、状态回「规划中」。"""
        source = self.load(trip_id)
        data = source.to_dict()
        data["id"] = new_id("t")
        data["name"] = f"{source.name}（副本）"
        data["status"] = "planning"
        data["created_at"] = ""
        data["updated_at"] = ""
        for item in data["items"]:
            item["id"] = new_id("i")
            item["done"] = False
        for pack in data["packing"]:
            pack["id"] = new_id("p")
            pack["packed"] = False
        copy = Trip.from_dict(data)
        return self.save(copy)

    # ------------------------------------------------------------------ 备份
    def _backup(self, path: Path) -> None:
        self._backups_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime(_BACKUP_TS)
        target = self._backups_dir / f"{path.stem}-{stamp}.json"
        try:
            shutil.copy2(path, target)
        except OSError:
            return  # 备份失败不阻塞主写入
        self._prune_backups(path.stem)

    def _prune_backups(self, trip_id: str) -> None:
        backups = sorted(self._backups_dir.glob(f"{trip_id}-*.json"))
        for stale in backups[: max(0, len(backups) - self._backup_keep)]:
            stale.unlink(missing_ok=True)
