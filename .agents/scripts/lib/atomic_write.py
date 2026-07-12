"""跨平台原子文件写入工具。

提供Windows兼容的原子文件写入能力：
- 唯一临时文件名（PID+随机后缀），消除多进程竞态
- Windows文件锁自动重试（PermissionError/os.replace冲突）
- stale临时文件自动清理
- JSON/text/binary三种便捷写入接口

典型用法::

    from lib.atomic_write import atomic_write_text, atomic_write_json

    atomic_write_json(path, data, retry_on_win_lock=True)
    atomic_write_text(path, text, encoding="utf-8")

线程/进程安全：每个进程使用独立临时文件，os.replace原子提交，
写前不持有目标文件锁，并发写入时后写入者的内容生效（last-writer-wins），
不会产生文件损坏或死锁。
"""

from __future__ import annotations

import logging
import os
import random
import time
from pathlib import Path
from typing import Any, Optional, Union

_log = logging.getLogger("atomic_write")

_DEFAULT_MAX_RETRIES = 3
_DEFAULT_RETRY_INTERVAL_MS = 10
_DEFAULT_STALE_MAX_AGE_SEC = 3600


def _make_unique_tmp_path(dst: Path) -> Path:
    pid = os.getpid()
    rand_suffix = f"{random.randint(0, 0xFFFFFF):06x}"
    return dst.parent / f"{dst.name}.pid{pid}.{rand_suffix}.tmp"


def _cleanup_stale_tmp_files(dst: Path, max_age_sec: float = _DEFAULT_STALE_MAX_AGE_SEC):
    pattern = f"{dst.name}.pid*.tmp"
    now = time.time()
    scanned = 0
    cleaned = 0
    errors = 0
    _t_start = time.perf_counter()
    for tmp_file in dst.parent.glob(pattern):
        scanned += 1
        try:
            stat = tmp_file.stat()
            age = now - stat.st_mtime
            if age > max_age_sec:
                tmp_file.unlink()
                cleaned += 1
                _log.debug("清理stale tmp | age=%.0fs | size=%dB | path=%s",
                           age, stat.st_size, tmp_file.name)
        except OSError as e:
            errors += 1
            _log.debug("清理tmp失败 | path=%s | error=%s", tmp_file.name, e)
    if scanned > 0:
        _t_ms = (time.perf_counter() - _t_start) * 1000
        _log.debug("stale清理完成 | scanned=%d | cleaned=%d | errors=%d | 耗时=%.3fms",
                   scanned, cleaned, errors, _t_ms)


def _atomic_replace_with_retry(src: Path, dst: Path,
                                max_retries: int = _DEFAULT_MAX_RETRIES,
                                interval_ms: int = _DEFAULT_RETRY_INTERVAL_MS):
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            os.replace(src, dst)
            return
        except OSError as e:
            last_error = e
            if attempt < max_retries:
                _log.debug("atomic_replace重试 | attempt=%d/%d | error=%s | interval=%dms | src=%s",
                           attempt + 1, max_retries, e, interval_ms, src.name)
                time.sleep(interval_ms / 1000.0)
            else:
                try:
                    src.unlink(missing_ok=True)
                except OSError:
                    pass
    raise last_error


def atomic_write_bytes(dst: Union[str, Path], data: bytes,
                       max_retries: int = _DEFAULT_MAX_RETRIES,
                       retry_interval_ms: int = _DEFAULT_RETRY_INTERVAL_MS,
                       stale_max_age_sec: float = _DEFAULT_STALE_MAX_AGE_SEC,
                       cleanup_stale: bool = True,
                       ) -> Path:
    """原子写入字节数据到文件。

    流程：确保父目录存在 → 清理stale tmp → 写入唯一tmp文件 → os.replace原子提交。
    Windows上os.replace遇到PermissionError（AV/索引器短暂锁）时自动重试。

    Args:
        dst: 目标文件路径
        data: 要写入的字节数据
        max_retries: os.replace失败最大重试次数（不含首次尝试）
        retry_interval_ms: 重试间隔毫秒
        stale_max_age_sec: stale tmp文件最大存活时间（秒）
        cleanup_stale: 是否在写入前清理stale tmp文件

    Returns:
        目标文件路径

    Raises:
        OSError: 所有重试均失败时抛出
    """
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if cleanup_stale:
        _cleanup_stale_tmp_files(dst, stale_max_age_sec)
    tmp_path = _make_unique_tmp_path(dst)
    try:
        with open(tmp_path, "wb") as f:
            f.write(data)
        _atomic_replace_with_retry(tmp_path, dst, max_retries, retry_interval_ms)
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    return dst


def atomic_write_text(dst: Union[str, Path], text: str, encoding: str = "utf-8",
                      max_retries: int = _DEFAULT_MAX_RETRIES,
                      retry_interval_ms: int = _DEFAULT_RETRY_INTERVAL_MS,
                      **kwargs) -> Path:
    """原子写入文本数据到文件。"""
    return atomic_write_bytes(dst, text.encode(encoding),
                              max_retries=max_retries,
                              retry_interval_ms=retry_interval_ms,
                              **kwargs)


def atomic_write_json(dst: Union[str, Path], obj: Any,
                      encoding: str = "utf-8",
                      ensure_ascii: bool = False,
                      indent: Optional[int] = 2,
                      max_retries: int = _DEFAULT_MAX_RETRIES,
                      retry_interval_ms: int = _DEFAULT_RETRY_INTERVAL_MS,
                      **kwargs) -> Path:
    """原子写入JSON数据到文件。"""
    import json
    data = json.dumps(obj, ensure_ascii=ensure_ascii, indent=indent).encode(encoding)
    return atomic_write_bytes(dst, data,
                              max_retries=max_retries,
                              retry_interval_ms=retry_interval_ms,
                              **kwargs)
