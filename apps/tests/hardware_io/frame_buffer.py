"""线程安全的"最新值"缓存.

适用于实时数据流（视频帧、传感器读数等）的生产者-消费者场景：
生产者持续更新最新值，消费者按需读取。与队列不同，本缓存**只保留最新值**，
当消费者处理速度跟不上时自动丢弃旧值——对实时预览而言，延迟比丢帧更不可接受。

示例::

    import threading, time

    buf = FrameBuffer()

    def producer():
        while True:
            frame = capture_frame()
            buf.set(frame)

    def consumer():
        while True:
            frame, ts = buf.get()
            if frame is not None:
                process(frame)

    threading.Thread(target=producer, daemon=True).start()
    consumer()
"""

from __future__ import annotations

import threading
import time
from typing import Generic, Optional, Tuple, TypeVar

T = TypeVar("T")


class FrameBuffer(Generic[T]):
    """线程安全的最新值缓存.

    泛型参数 ``T`` 为缓存值的类型（如 numpy.ndarray、dict、bytes 等）。
    ``set()`` 存储值的副本引用，调用方如需避免外部修改可传入 ``copy=True``。
    """

    __slots__ = ("_lock", "_value", "_timestamp", "_frame_count")

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._value: Optional[T] = None
        self._timestamp: float = 0.0
        self._frame_count: int = 0

    def set(self, value: T, timestamp: Optional[float] = None) -> None:
        """更新缓存值.

        Args:
            value: 要缓存的值。对于 numpy 数组等可变对象，建议传入副本
                （或使用 ``copy=True`` 的 :meth:`set_copy`）。
            timestamp: 可选的时间戳（``time.time()`` 格式）。为 ``None``
                时自动使用当前时间。
        """
        ts = timestamp if timestamp is not None else time.time()
        with self._lock:
            self._value = value
            self._timestamp = ts
            self._frame_count += 1

    def set_copy(self, value: T, timestamp: Optional[float] = None) -> None:
        """更新缓存值并存储副本（如果值支持 copy() 方法）.

        对于 numpy.ndarray，调用 ``.copy()``；对于其他类型，直接存储引用。
        """
        copied = value.copy() if hasattr(value, "copy") else value
        self.set(copied, timestamp)

    def get(self) -> Tuple[Optional[T], float]:
        """获取最新值及其时间戳.

        Returns:
            ``(value, timestamp)`` 元组。若从未 set 过，value 为 ``None``，
            timestamp 为 ``0.0``。返回值的引用不保证是副本——若调用方需要
            长期持有，应自行复制。
        """
        with self._lock:
            return self._value, self._timestamp

    def get_copy(self) -> Tuple[Optional[T], float]:
        """获取最新值的副本及其时间戳.

        如果值支持 ``copy()`` 方法则返回副本，否则返回引用。
        """
        with self._lock:
            if self._value is not None and hasattr(self._value, "copy"):
                return self._value.copy(), self._timestamp
            return self._value, self._timestamp

    @property
    def age_ms(self) -> float:
        """最新值的年龄（毫秒）。无值时返回 -1."""
        with self._lock:
            if self._timestamp <= 0:
                return -1.0
            return (time.time() - self._timestamp) * 1000.0

    @property
    def is_fresh(self) -> bool:
        """是否已有值缓存."""
        with self._lock:
            return self._value is not None

    @property
    def frame_count(self) -> int:
        """累计 set 次数（可用于帧率统计）."""
        with self._lock:
            return self._frame_count

    def clear(self) -> None:
        """清空缓存."""
        with self._lock:
            self._value = None
            self._timestamp = 0.0
