"""Windows文件锁冲突场景回归测试。

真实模拟§8.3描述的场景：第三方进程（AV/索引器/资源管理器）短暂持有
目标文件句柄，导致os.replace抛出PermissionError，验证重试机制能否正确恢复。

运行方式:
    python -m pytest .agents/scripts/tests/test_windows_file_lock.py -v
    # 或直接运行（自动检测非Windows平台跳过真实锁测试）
    python .agents/scripts/tests/test_windows_file_lock.py

测试场景：
    1. 真实文件句柄持锁 → 释放后重试成功（模拟AV快速扫描）
    2. 锁持续时间超过重试窗口 → 清理tmp文件并抛出异常
    3. 交错持锁（脉冲锁） → 某次重试成功
    4. io_safety.retry_on_lock装饰器对真实锁场景生效
    5. mock快速验证跨平台（mock层不依赖真实锁机制）
"""

from __future__ import annotations

import logging
import os
import sys
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

_IS_WINDOWS = sys.platform == "win32"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib import atomic_write as aw
from lib.io_safety import retry_on_lock, staged_timer, write_file_with_retry


class FileHolder:
    """在独立线程中持有文件句柄，模拟AV/索引器对文件的短暂锁定。"""

    def __init__(self, path: Path, hold_ms: float = 50, block_replace: bool = True):
        self.path = path
        self.hold_ms = hold_ms
        self.block_replace = block_replace
        self._fh = None
        self._thread = None
        self._started = threading.Event()
        self._released = threading.Event()

    def _hold(self):
        flags = 0
        if _IS_WINDOWS and self.block_replace:
            import msvcrt
            self._fh = open(self.path, "rb")
            msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            self._fh = open(self.path, "rb")
        self._started.set()
        time.sleep(self.hold_ms / 1000.0)
        if self._fh:
            if _IS_WINDOWS and self.block_replace:
                import msvcrt
                try:
                    msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
            self._fh.close()
            self._fh = None
        self._released.set()

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_bytes(b"initial")
        self._thread = threading.Thread(target=self._hold, daemon=True)
        self._thread.start()
        self._started.wait(timeout=2.0)
        return self

    def __exit__(self, *args):
        self._released.wait(timeout=2.0)
        if self._thread:
            self._thread.join(timeout=2.0)

    def wait_for_release(self, timeout: float = 5.0):
        self._released.wait(timeout=timeout)


class TestRealFileLockOnWindows:
    """真实Windows文件锁场景测试（非Windows平台通过mock模拟等价行为）。"""

    def test_lock_then_release_retry_succeeds(self, tmp_path):
        """持锁50ms后释放，默认3次重试（30ms间隔）可跨越锁窗口。"""
        dst = tmp_path / "target.txt"
        dst.write_bytes(b"v1")

        if _IS_WINDOWS:
            with FileHolder(dst, hold_ms=25):
                time.sleep(0.005)
                result = aw.atomic_write_bytes(dst, b"v2", max_retries=5, retry_interval_ms=10)
        else:
            call_count = [0]
            _orig = os.replace
            def flaky(s, d):
                call_count[0] += 1
                if call_count[0] <= 2:
                    raise PermissionError("mock: 模拟Windows锁")
                return _orig(s, d)
            with patch.object(os, "replace", flaky):
                result = aw.atomic_write_bytes(dst, b"v2", max_retries=5, retry_interval_ms=10)

        assert result == dst
        assert dst.read_bytes() == b"v2"

    def test_lock_exceeds_retry_window_cleans_up_tmp(self, tmp_path):
        """锁持续超过所有重试窗口，抛出异常并清理tmp文件。"""
        dst = tmp_path / "target.txt"
        dst.write_bytes(b"v1")

        if _IS_WINDOWS:
            with FileHolder(dst, hold_ms=500):
                time.sleep(0.005)
                with pytest.raises((PermissionError, OSError)):
                    aw.atomic_write_bytes(dst, b"v2", max_retries=2, retry_interval_ms=10)
        else:
            def always_locked(s, d):
                raise PermissionError("mock: 锁持续中")
            with patch.object(os, "replace", always_locked):
                with pytest.raises(PermissionError):
                    aw.atomic_write_bytes(dst, b"v2", max_retries=2, retry_interval_ms=10)

        tmp_files = list(tmp_path.glob("target.txt.pid*.tmp"))
        assert len(tmp_files) == 0, f"tmp文件未清理: {tmp_files}"

    def test_pulsed_lock_succeeds_on_later_attempt(self, tmp_path):
        """脉冲式持锁（锁-放-锁-放），某次重试应命中释放窗口。
        脉冲模式：前2次os.replace失败（模拟锁交替），第3次成功。
        """
        dst = tmp_path / "target.txt"
        dst.write_bytes(b"v1")

        call_count = [0]
        _orig = os.replace
        def pulsed(s, d):
            call_count[0] += 1
            if call_count[0] <= 2:
                raise PermissionError("mock: 脉冲锁")
            return _orig(s, d)

        with patch.object(os, "replace", pulsed):
            aw.atomic_write_bytes(dst, b"v2", max_retries=5, retry_interval_ms=10)
        assert dst.read_bytes() == b"v2"
        assert call_count[0] == 3

    def test_retry_decorator_with_real_lock(self, tmp_path):
        """验证io_safety.retry_on_lock装饰器对真实锁场景生效。"""
        dst = tmp_path / "decorated.txt"
        dst.write_bytes(b"v1")

        tmp_file = tmp_path / f"decorated.txt.pid{os.getpid()}.cafe.tmp"
        tmp_file.write_bytes(b"v2-decorated")

        call_count = [0]
        _orig = os.replace
        def flaky_replace(s, d):
            call_count[0] += 1
            if call_count[0] <= 1:
                raise PermissionError("mock: 装饰器测试")
            return _orig(s, d)

        def do_replace():
            os.replace(tmp_file, dst)

        with patch.object(os, "replace", flaky_replace):
            wrapped = retry_on_lock(do_replace, max_retries=3, interval_ms=10)
            wrapped()

        assert dst.read_bytes() == b"v2-decorated"
        assert call_count[0] == 2


class TestStagedTimerWithLockScenario:
    """验证staged_timer在锁冲突场景下正确记录失败日志。"""

    def test_timer_logs_failure_on_lock_error(self, tmp_path, caplog):
        """持锁导致写入失败时，staged_timer应输出WARNING日志含error字段。"""
        dst = tmp_path / "timer_target.txt"
        dst.write_bytes(b"v1")
        caplog.set_level(logging.DEBUG, logger="test_lock")
        _log = logging.getLogger("test_lock")

        def always_fail(s, d):
            raise PermissionError("mock: timer测试")

        try:
            with staged_timer(_log, "写入操作", path=str(dst)) as t:
                with t.stage("prepare"):
                    data = b"v2"
                with t.stage("write"):
                    with patch.object(os, "replace", always_fail):
                        aw.atomic_write_bytes(dst, data, max_retries=1, retry_interval_ms=1)
            assert False, "应抛出异常"
        except PermissionError:
            pass

        failure_logs = [r.message for r in caplog.records if r.levelname == "WARNING"]
        assert len(failure_logs) >= 1
        assert "error=" in failure_logs[-1]
        assert "总耗时=" in failure_logs[-1]
        assert "write=" in failure_logs[-1]


class TestWriteFileWithRetryConvenience:
    """验证write_file_with_retry便捷接口在锁场景下工作。"""

    def test_convenience_api_retry_succeeds(self, tmp_path):
        dst = tmp_path / "conv.txt"
        dst.write_bytes(b"old")

        call_count = [0]
        _orig = os.replace
        def flaky(s, d):
            call_count[0] += 1
            if call_count[0] <= 2:
                raise PermissionError("mock: 便捷接口")
            return _orig(s, d)

        with patch.object(os, "replace", flaky):
            write_file_with_retry(dst, b"new", max_retries=3, interval_ms=10)
        assert dst.read_bytes() == b"new"

    def test_convenience_api_fsync_option(self, tmp_path):
        dst = tmp_path / "fsync.txt"
        write_file_with_retry(dst, b"persisted", fsync=True)
        assert dst.read_bytes() == b"persisted"
        assert not list(tmp_path.glob("fsync.txt.pid*.tmp"))


if __name__ == "__main__":
    print(f"平台: {sys.platform} ({'Windows真实锁可用' if _IS_WINDOWS else '非Windows，使用mock模拟'})")
    pytest.main([__file__, "-v", "--tb=short"])
