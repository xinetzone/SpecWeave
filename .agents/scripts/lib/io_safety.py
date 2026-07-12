"""文件I/O安全工具集——分阶段计时日志、锁冲突重试策略。

提供三个可复用组件：
1. staged_timer: 分阶段计时上下文管理器，生成符合规范的DEBUG/WARNING日志
2. retry_on_lock: Windows文件锁冲突重试装饰器/函数
3. write_file_with_retry: 带重试的原子写入便捷封装（委托到atomic_write.py）

原子写入函数（atomic_write_bytes/text/json/edit_text）在 lib.atomic_write 中定义，
本模块不做重复导出，使用时从 lib.atomic_write 直接导入。

典型用法::

    from lib.atomic_write import atomic_write_bytes
    from lib.io_safety import staged_timer, retry_on_lock

    # 分阶段计时写缓存
    with staged_timer(_log, "磁盘缓存保存完成", path="cache.json") as t:
        with t.stage("build"):
            entries = build_entries()
        with t.stage("serialize"):
            data = json.dumps(entries).encode("utf-8")
        with t.stage("atomic-write"):
            atomic_write_bytes(path, data)
    # DEBUG: 磁盘缓存保存完成 | build=0.15ms | serialize=0.08ms | atomic-write=0.32ms | 总耗时=0.62ms | path=cache.json

    # 重试装饰器
    @retry_on_lock(max_retries=3, interval_ms=10)
    def save_file(path, data):
        os.replace(tmp, path)
"""

from __future__ import annotations

import functools
import logging
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, Optional, Union

from lib.atomic_write import atomic_write_bytes as _atomic_write_bytes


class _StageTimer:
    """分阶段计时器，配合staged_timer()使用。"""

    def __init__(self, logger: logging.Logger, operation: str, **fields: Any):
        self._log = logger
        self._operation = operation
        self._fields = fields
        self._t0 = time.perf_counter()
        self._stages: list[tuple[str, float]] = []
        self._t_stage_start: float = 0.0

    @contextmanager
    def stage(self, name: str) -> Iterator[None]:
        self._t_stage_start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = (time.perf_counter() - self._t_stage_start) * 1000
            self._stages.append((name, elapsed))

    def _format(self, error: Optional[BaseException] = None) -> str:
        parts = [self._operation]
        for name, ms in self._stages:
            parts.append(f"{name}={ms:.2f}ms")
        total = (time.perf_counter() - self._t0) * 1000
        parts.append(f"总耗时={total:.2f}ms")
        for k, v in self._fields.items():
            parts.append(f"{k}={v}")
        if error is not None:
            parts.append(f"error={error}")
        return " | ".join(parts)

    def _finish(self, error: Optional[BaseException] = None) -> None:
        msg = self._format(error)
        if error is not None:
            self._log.warning(msg)
        else:
            self._log.debug(msg)


@contextmanager
def staged_timer(
    logger: Union[logging.Logger, str],
    operation: str,
    **fields: Any,
) -> Iterator[_StageTimer]:
    """分阶段计时上下文管理器。

    进入时记录开始时间，退出时输出格式统一的日志：
    成功 -> DEBUG: "<operation> | <stage1>=X.XXms | <stage2>=X.XXms | 总耗时=X.XXms | k=v ..."
    失败 -> WARNING: "<operation> | ... | 总耗时=X.XXms | k=v ... | error=<err>"

    Args:
        logger: Logger实例或logger名称。
        operation: 操作描述（如"磁盘缓存保存完成"）。
        **fields: 额外键值对（如path=xxx, entries=42）。

    Yields:
        _StageTimer对象，通过.stage("name")上下文管理器记录各子阶段。
    """
    if isinstance(logger, str):
        logger = logging.getLogger(logger)
    timer = _StageTimer(logger, operation, **fields)
    try:
        yield timer
    except BaseException as e:
        timer._finish(error=e)
        raise
    else:
        timer._finish()


def retry_on_lock(
    func: Optional[Callable] = None,
    *,
    max_retries: int = 3,
    interval_ms: int = 10,
    cleanup: Optional[Callable[[], None]] = None,
    log: Union[logging.Logger, str, None] = None,
) -> Any:
    """Windows文件锁冲突重试装饰器/函数包装器。

    可作为装饰器使用::

        @retry_on_lock(max_retries=3, interval_ms=10)
        def replace_file(src, dst):
            os.replace(src, dst)

    也可直接包装可调用对象::

        retry_on_lock(os.replace, max_retries=3)(src, dst)

    重试策略：
    - 捕获OSError（PermissionError是其子类），覆盖Windows AV/索引器锁冲突
    - 固定间隔退避（非指数退避，锁通常在<10ms释放）
    - 重试耗尽时调用cleanup回调（如清理临时文件），然后抛出最后异常
    - 每次重试记录DEBUG日志

    Args:
        func: 被装饰的函数（装饰器模式时自动传入）。
        max_retries: 最大重试次数，默认3次（共4次机会）。
        interval_ms: 重试间隔毫秒数，默认10ms。
        cleanup: 重试耗尽后的清理回调（无参数），如清理临时文件。
        log: Logger实例或名称，默认使用"io_safety" logger。

    Returns:
        装饰后的函数或装饰器本身。
    """
    def decorator(fn: Callable) -> Callable:
        _logger = logging.getLogger(log if isinstance(log, str) else (log.name if log else "io_safety"))

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error: Optional[BaseException] = None
            for attempt in range(max_retries + 1):
                try:
                    return fn(*args, **kwargs)
                except OSError as e:
                    last_error = e
                    if attempt < max_retries:
                        _logger.debug(
                            "retry | attempt=%d/%d | error=%s | interval=%dms | func=%s",
                            attempt + 1, max_retries, e, interval_ms, fn.__name__,
                        )
                        time.sleep(interval_ms / 1000.0)
                    else:
                        if cleanup is not None:
                            try:
                                cleanup()
                            except OSError:
                                pass
                        raise
            assert last_error is not None
            raise last_error

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def write_file_with_retry(
    dst: Union[str, Path],
    data: bytes,
    *,
    max_retries: int = 3,
    interval_ms: int = 10,
    stale_max_age_sec: float = 3600,
    fsync: bool = False,
) -> Path:
    """便捷封装：带重试的原子写入文件（语义化别名，委托到atomic_write_bytes）。

    Args:
        dst: 目标文件路径。
        data: 字节数据。
        max_retries: os.replace重试次数，默认3。
        interval_ms: 重试间隔毫秒数，默认10。
        stale_max_age_sec: stale tmp文件最大存活秒数，默认3600（1小时）。
        fsync: 是否强制刷盘（关键数据设True，~1-5ms额外开销）。

    Returns:
        目标文件路径。
    """
    return _atomic_write_bytes(
        dst, data,
        max_retries=max_retries,
        retry_interval_ms=interval_ms,
        stale_max_age_sec=stale_max_age_sec,
        fsync=fsync,
    )
