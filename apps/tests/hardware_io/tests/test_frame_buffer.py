"""frame_buffer 线程安全缓存单元测试."""

import threading
import time

import pytest

from hardware_io.frame_buffer import FrameBuffer


class TestFrameBuffer:
    """FrameBuffer 基本功能测试."""

    def test_initial_state(self):
        buf = FrameBuffer()
        val, ts = buf.get()
        assert val is None
        assert ts == 0.0
        assert not buf.is_fresh
        assert buf.age_ms == -1.0
        assert buf.frame_count == 0

    def test_set_and_get(self):
        buf = FrameBuffer()
        buf.set("hello")
        val, ts = buf.get()
        assert val == "hello"
        assert ts > 0
        assert buf.is_fresh
        assert buf.frame_count == 1

    def test_overwrite(self):
        buf = FrameBuffer()
        buf.set("first")
        buf.set("second")
        val, _ = buf.get()
        assert val == "second"
        assert buf.frame_count == 2

    def test_age_ms(self):
        buf = FrameBuffer()
        buf.set("data")
        time.sleep(0.05)
        age = buf.age_ms
        assert age >= 40  # 至少 40ms

    def test_clear(self):
        buf = FrameBuffer()
        buf.set("data")
        buf.clear()
        val, ts = buf.get()
        assert val is None
        assert ts == 0.0
        assert not buf.is_fresh

    def test_explicit_timestamp(self):
        buf = FrameBuffer()
        buf.set("data", timestamp=1000.0)
        _, ts = buf.get()
        assert ts == 1000.0

    def test_set_copy_with_numpy_like(self):
        """测试 set_copy 对有 copy() 方法的对象."""

        class FakeFrame:
            def __init__(self):
                self.value = 42
                self.copied = False

            def copy(self):
                new = FakeFrame()
                new.value = self.value
                new.copied = True
                return new

        buf = FrameBuffer()
        original = FakeFrame()
        buf.set_copy(original)
        val, _ = buf.get()
        assert val.copied is True
        assert val is not original

    def test_get_copy(self):
        buf = FrameBuffer()
        buf.set([1, 2, 3])
        val, _ = buf.get_copy()
        # list 有 copy 方法
        assert val == [1, 2, 3]
        # 修改副本不影响缓存
        val.append(4)
        cached, _ = buf.get()
        assert cached == [1, 2, 3]


class TestFrameBufferThreadSafety:
    """FrameBuffer 多线程测试."""

    def test_concurrent_set_get(self):
        """多线程写入不崩溃，计数正确."""
        buf = FrameBuffer()
        n_threads = 4
        n_per_thread = 100

        def writer(thread_id):
            for i in range(n_per_thread):
                buf.set((thread_id, i))

        threads = [threading.Thread(target=writer, args=(t,)) for t in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert buf.frame_count == n_threads * n_per_thread
        val, _ = buf.get()
        assert val is not None

    def test_consumer_sees_latest(self):
        """消费者能持续读到值，且生产者结束后最终值为 49."""
        buf = FrameBuffer()
        stop = threading.Event()
        seen = []

        def producer():
            for i in range(50):
                buf.set(i)
                time.sleep(0.001)

        def consumer():
            while not stop.is_set():
                val, _ = buf.get()
                if val is not None:
                    seen.append(val)
                time.sleep(0.001)
            # 停止信号后再读一次，确保拿到最终值
            val, _ = buf.get()
            if val is not None:
                seen.append(val)

        t1 = threading.Thread(target=producer)
        t2 = threading.Thread(target=consumer)
        t1.start()
        t2.start()
        t1.join()
        stop.set()
        t2.join()

        assert len(seen) > 0
        assert 49 in seen
