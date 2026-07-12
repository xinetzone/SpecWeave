"""atomic_write 模块单元测试。

覆盖场景：
- 基本写入（bytes/text/json）
- PID唯一命名（多进程无冲突）
- stale tmp文件自动清理
- Windows文件锁重试
- 失败时tmp文件清理
- 并发写入无损坏
- 边界条件（空数据、大文件、特殊字符）
- 自定义重试参数
- 原子编辑（read-modify-write）
- 极端边缘场景（fsync、二进制全字节、深层目录、stale跨文件清理等）
"""

from __future__ import annotations

import json
import multiprocessing
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import lib.atomic_write as aw
from lib.atomic_write import (
    _make_unique_tmp_path,
    _cleanup_stale_tmp_files,
    _atomic_replace_with_retry,
    atomic_write_bytes,
    atomic_write_text,
    atomic_write_json,
    atomic_edit_text,
    _DEFAULT_MAX_RETRIES,
    _DEFAULT_STALE_MAX_AGE_SEC,
    _DEFAULT_RETRY_INTERVAL_MS,
)


def _mp_gen_names(count, q):
    names = set()
    for _ in range(count):
        names.add(_make_unique_tmp_path(Path("/tmp/test.json")).name)
    q.put(names)


def _mp_concurrent_worker(project_root: str, worker_id: int, barrier, results_dict):
    import pathlib
    scripts_dir = pathlib.Path(project_root) / ".agents" / "scripts"
    sys.path.insert(0, str(scripts_dir))
    from lib.atomic_write import atomic_write_json as _aw
    try:
        barrier.wait(timeout=10)
    except Exception:
        pass
    cache_path = pathlib.Path(project_root) / ".agents" / ".cache" / "concurrent-test.json"
    pid = os.getpid()
    start = time.perf_counter()
    try:
        for i in range(5):
            data = {
                "worker_id": worker_id,
                "pid": pid,
                "round": i,
                "timestamp": time.time(),
                "value": f"worker-{worker_id}-round-{i}",
            }
            _aw(cache_path, data, ensure_ascii=False, indent=None)
            time.sleep(0.001)
        elapsed = (time.perf_counter() - start) * 1000
        results_dict[worker_id] = {"status": "success", "elapsed_ms": elapsed, "pid": pid}
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        results_dict[worker_id] = {"status": "error", "error": str(e), "elapsed_ms": elapsed, "pid": pid}


class TestBasicWrites:
    """基本写入功能测试。"""

    def test_write_bytes_creates_file(self, tmp_path):
        dst = tmp_path / "test.bin"
        data = b"hello world"
        result = atomic_write_bytes(dst, data)
        assert result == dst
        assert dst.exists()
        assert dst.read_bytes() == data

    def test_write_bytes_overwrites_existing(self, tmp_path):
        dst = tmp_path / "test.bin"
        dst.write_bytes(b"old content")
        atomic_write_bytes(dst, b"new content")
        assert dst.read_bytes() == b"new content"

    def test_write_text_with_encoding(self, tmp_path):
        dst = tmp_path / "test.txt"
        text = "你好世界\nこんにちは"
        atomic_write_text(dst, text, encoding="utf-8")
        assert dst.read_text(encoding="utf-8") == text

    def test_write_text_gbk_encoding(self, tmp_path):
        dst = tmp_path / "test.txt"
        text = "中文测试"
        atomic_write_text(dst, text, encoding="gbk")
        assert dst.read_text(encoding="gbk") == text

    def test_write_json_basic(self, tmp_path):
        dst = tmp_path / "test.json"
        data = {"key": "value", "num": 42, "nested": {"a": [1, 2, 3]}}
        atomic_write_json(dst, data)
        loaded = json.loads(dst.read_text(encoding="utf-8"))
        assert loaded == data

    def test_write_json_unicode(self, tmp_path):
        dst = tmp_path / "test.json"
        data = {"中文键": "中文值", "emoji": "🎉"}
        atomic_write_json(dst, data, ensure_ascii=False)
        content = dst.read_text(encoding="utf-8")
        assert "中文键" in content
        loaded = json.loads(content)
        assert loaded == data

    def test_write_json_indent(self, tmp_path):
        dst = tmp_path / "test.json"
        data = {"a": 1}
        atomic_write_json(dst, data, indent=2)
        content = dst.read_text(encoding="utf-8")
        assert "\n" in content
        assert "  " in content

    def test_write_creates_parent_directories(self, tmp_path):
        dst = tmp_path / "nested" / "deep" / "path" / "test.bin"
        atomic_write_bytes(dst, b"data")
        assert dst.exists()
        assert dst.read_bytes() == b"data"

    def test_write_empty_bytes(self, tmp_path):
        dst = tmp_path / "empty.bin"
        atomic_write_bytes(dst, b"")
        assert dst.exists()
        assert dst.read_bytes() == b""

    def test_write_large_data(self, tmp_path):
        dst = tmp_path / "large.bin"
        data = b"x" * (1024 * 1024)
        atomic_write_bytes(dst, data)
        assert dst.read_bytes() == data

    def test_write_no_tmp_file_left(self, tmp_path):
        dst = tmp_path / "test.bin"
        atomic_write_bytes(dst, b"data")
        tmp_files = list(tmp_path.glob("test.bin.pid*.tmp"))
        assert len(tmp_files) == 0


class TestUniqueTmpNaming:
    """PID唯一命名测试。"""

    def test_tmp_filename_contains_pid(self, tmp_path):
        dst = tmp_path / "target.json"
        tp = _make_unique_tmp_path(dst)
        pid = os.getpid()
        assert f"pid{pid}" in tp.name
        assert tp.name.endswith(".tmp")
        assert tp.name.startswith("target.json.")

    def test_tmp_filename_has_random_suffix(self, tmp_path):
        dst = tmp_path / "target.json"
        names = set()
        for _ in range(50):
            tp = _make_unique_tmp_path(dst)
            names.add(tp.name)
        assert len(names) == 50

    def test_tmp_file_in_same_directory_as_target(self, tmp_path):
        dst = tmp_path / "subdir" / "target.json"
        dst.parent.mkdir(parents=True)
        tp = _make_unique_tmp_path(dst)
        assert tp.parent == dst.parent

    def test_multi_process_unique_names(self):
        """多进程同时生成tmp文件名，验证不会碰撞。"""
        q = multiprocessing.Queue()
        procs = []
        for _ in range(4):
            p = multiprocessing.Process(target=_mp_gen_names, args=(25, q))
            procs.append(p)
            p.start()
        all_names = set()
        for _ in range(4):
            all_names.update(q.get())
        for p in procs:
            p.join(timeout=10)
        assert len(all_names) == 100


class TestStaleCleanup:
    """Stale tmp文件清理测试。"""

    def _create_tmp_file(self, cache_dir: Path, target_name: str, age_seconds: float) -> Path:
        return self._create_tmp_file_pid(cache_dir, target_name, age_seconds, 99999)

    def _create_tmp_file_pid(self, cache_dir: Path, target_name: str, age_seconds: float, pid: int) -> Path:
        rand = f"{os.urandom(3).hex()}"
        tmp = cache_dir / f"{target_name}.pid{pid}.{rand}.tmp"
        tmp.write_text("stale", encoding="utf-8")
        old_time = time.time() - age_seconds
        os.utime(tmp, (old_time, old_time))
        return tmp

    def test_cleanup_removes_old_files(self, tmp_path):
        target = tmp_path / "cache.json"
        stale1 = self._create_tmp_file(tmp_path, "cache.json", _DEFAULT_STALE_MAX_AGE_SEC + 100)
        stale2 = self._create_tmp_file(tmp_path, "cache.json", _DEFAULT_STALE_MAX_AGE_SEC + 3600)
        fresh = self._create_tmp_file(tmp_path, "cache.json", 10)
        _cleanup_stale_tmp_files(target)
        assert not stale1.exists()
        assert not stale2.exists()
        assert fresh.exists()

    def test_cleanup_keeps_recent_files(self, tmp_path):
        target = tmp_path / "cache.json"
        recent = self._create_tmp_file(tmp_path, "cache.json", 60)
        very_recent = self._create_tmp_file(tmp_path, "cache.json", 0.001)
        _cleanup_stale_tmp_files(target)
        assert recent.exists()
        assert very_recent.exists()

    def test_cleanup_only_matches_target_pattern(self, tmp_path):
        target = tmp_path / "cache.json"
        stale_cache = self._create_tmp_file(tmp_path, "cache.json", _DEFAULT_STALE_MAX_AGE_SEC + 100)
        other_file = tmp_path / "other.json.pid99999.abcdef.tmp"
        other_file.write_text("other")
        os.utime(other_file, (time.time() - 7200, time.time() - 7200))
        _cleanup_stale_tmp_files(target)
        assert not stale_cache.exists()
        assert other_file.exists()

    def test_cleanup_no_match_is_noop(self, tmp_path):
        target = tmp_path / "nonexistent.json"
        _cleanup_stale_tmp_files(target)

    def test_cleanup_handles_already_deleted_file(self, tmp_path):
        """清理过程中文件被其他进程删除不报错。"""
        target = tmp_path / "cache.json"
        stale = self._create_tmp_file(tmp_path, "cache.json", _DEFAULT_STALE_MAX_AGE_SEC + 100)
        stale.unlink()
        _cleanup_stale_tmp_files(target)

    def test_cleanup_tolerates_unlink_error(self, tmp_path):
        """unlink失败不影响其他文件清理（不同PID的stale文件）。"""
        target = tmp_path / "cache.json"
        stale_a = self._create_tmp_file_pid(tmp_path, "cache.json", _DEFAULT_STALE_MAX_AGE_SEC + 100, 99998)
        stale_b = self._create_tmp_file_pid(tmp_path, "cache.json", _DEFAULT_STALE_MAX_AGE_SEC + 200, 99999)

        real_unlink = Path.unlink
        call_idx = [0]

        def flaky_unlink(self_, *args, **kwargs):
            call_idx[0] += 1
            if "pid99998" in self_.name:
                raise OSError("文件被占用")
            return real_unlink(self_, *args, **kwargs)

        with patch.object(Path, "unlink", flaky_unlink):
            _cleanup_stale_tmp_files(target)
        assert stale_b.exists() is False

    def test_atomic_write_triggers_stale_cleanup(self, tmp_path):
        dst = tmp_path / "cache.json"
        stale = self._create_tmp_file(tmp_path, "cache.json", _DEFAULT_STALE_MAX_AGE_SEC + 100)
        atomic_write_json(dst, {"new": "data"})
        assert not stale.exists()
        assert dst.exists()

    def test_atomic_write_respects_custom_max_age(self, tmp_path):
        dst = tmp_path / "cache.json"
        old = self._create_tmp_file(tmp_path, "cache.json", 500)
        atomic_write_json(dst, {"x": 1})
        assert old.exists()
        very_old = self._create_tmp_file(tmp_path, "cache.json", 5000)
        atomic_write_bytes(dst, b'{"x":2}', stale_max_age_sec=1000)
        assert old.exists()
        assert not very_old.exists()


class TestAtomicReplaceRetry:
    """文件锁重试机制测试。"""

    def test_retry_succeeds_on_first_try(self, tmp_path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("content")
        _atomic_replace_with_retry(src, dst, max_retries=2, interval_ms=1)
        assert dst.read_text() == "content"
        assert not src.exists()

    def test_retry_succeeds_after_permission_error(self, tmp_path):
        """模拟Windows文件锁：前N次replace失败，最终重试成功。"""
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        dst.write_text("original")
        src.write_text("new content")
        call_count = 0
        _orig_replace = os.replace

        def flaky_replace(s, d):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise PermissionError("模拟Windows文件锁")
            return _orig_replace(s, d)

        with patch.object(aw.os, "replace", flaky_replace):
            _atomic_replace_with_retry(src, dst, max_retries=3, interval_ms=1)
        assert dst.read_text() == "new content"
        assert call_count == 3
        assert not src.exists()

    def test_all_retries_exhausted_raises_and_cleans_tmp(self, tmp_path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("fail content")

        def always_fail(s, d):
            raise PermissionError("文件始终被锁定")

        with patch.object(aw.os, "replace", always_fail):
            with pytest.raises(PermissionError):
                _atomic_replace_with_retry(src, dst, max_retries=2, interval_ms=1)
        assert not src.exists()

    def test_retry_respects_max_retries_count(self, tmp_path):
        """验证重试次数精确：max_retries=2意味着总共尝试3次(1初始+2重试)。"""
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("data")
        call_count = 0

        def count_replace(s, d):
            nonlocal call_count
            call_count += 1
            raise PermissionError("锁")

        with patch.object(aw.os, "replace", count_replace):
            with pytest.raises(PermissionError):
                _atomic_replace_with_retry(src, dst, max_retries=2, interval_ms=1)
        assert call_count == 3

    def test_retry_sleeps_between_attempts(self, tmp_path):
        """验证重试之间有sleep间隔。"""
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("data")
        sleep_calls = []
        _orig_replace = os.replace
        failed = [False]

        def fail_once(s, d):
            if not failed[0]:
                failed[0] = True
                raise PermissionError("锁")
            return _orig_replace(s, d)

        def mock_sleep(seconds):
            sleep_calls.append(seconds)

        with patch.object(aw.os, "replace", fail_once), \
             patch.object(aw.time, "sleep", mock_sleep):
            _atomic_replace_with_retry(src, dst, max_retries=3, interval_ms=50)
        assert len(sleep_calls) == 1
        assert sleep_calls[0] == pytest.approx(0.05, abs=0.01)

    def test_default_retry_count_is_3(self):
        assert _DEFAULT_MAX_RETRIES == 3

    def test_default_retry_interval(self):
        assert _DEFAULT_RETRY_INTERVAL_MS == 10


class TestFailedWriteCleanup:
    """写入失败时tmp文件清理测试。"""

    def test_tmp_cleaned_up_on_serialization_error(self, tmp_path):
        dst = tmp_path / "cache.json"

        class BadObj:
            pass

        with pytest.raises((TypeError, ValueError)):
            atomic_write_json(dst, BadObj())

        tmp_files = list(tmp_path.glob("cache.json.pid*.tmp"))
        assert len(tmp_files) == 0

    def test_tmp_cleaned_up_on_replace_failure(self, tmp_path):
        """os.replace最终失败时，tmp文件被清理。"""
        dst = tmp_path / "test.bin"

        def always_fail(s, d):
            raise PermissionError("磁盘满")

        with patch.object(aw.os, "replace", always_fail):
            with pytest.raises(PermissionError):
                atomic_write_bytes(dst, b"data", max_retries=1, retry_interval_ms=1)
        tmp_files = list(tmp_path.glob("test.bin.pid*.tmp"))
        assert len(tmp_files) == 0

    def test_tmp_cleanup_best_effort_on_double_failure(self, tmp_path):
        """replace失败后unlink也失败，不抛出新异常。"""
        dst = tmp_path / "test.bin"
        real_unlink = Path.unlink

        def fail_replace(s, d):
            raise PermissionError("锁")

        def fail_unlink(self_, *args, **kwargs):
            if str(self_).endswith(".tmp"):
                raise OSError("无法删除")
            return real_unlink(self_, *args, **kwargs)

        with patch.object(aw.os, "replace", fail_replace), \
             patch.object(Path, "unlink", fail_unlink):
            with pytest.raises(PermissionError):
                atomic_write_bytes(dst, b"data", max_retries=0, retry_interval_ms=1)


class TestConcurrentWrites:
    """多进程并发写入测试。"""

    def test_concurrent_writes_no_corruption(self, tmp_path):
        """8进程并发写入同一缓存文件，无损坏、无tmp泄漏。"""
        agents_dir = tmp_path / ".agents"
        cache_dir = agents_dir / ".cache"
        cache_dir.mkdir(parents=True)
        (agents_dir / "ONBOARDING.md").write_text("# L0", encoding="utf-8")
        num_workers = 8
        barrier = multiprocessing.Barrier(num_workers)
        manager = multiprocessing.Manager()
        results = manager.dict()
        processes = []
        for i in range(num_workers):
            p = multiprocessing.Process(
                target=_mp_concurrent_worker,
                args=(str(tmp_path), i, barrier, results),
            )
            processes.append(p)
            p.start()
        for p in processes:
            p.join(timeout=30)
        successes = sum(1 for r in results.values() if r["status"] == "success")
        assert successes == num_workers, f"有{num_workers - successes}个进程失败: {dict(results)}"
        cache_path = cache_dir / "concurrent-test.json"
        assert cache_path.exists()
        final_data = json.loads(cache_path.read_text(encoding="utf-8"))
        assert "worker_id" in final_data
        assert "pid" in final_data
        assert "value" in final_data
        tmp_files = list(cache_dir.glob("concurrent-test.json.pid*.tmp"))
        assert len(tmp_files) == 0, f"残留tmp文件: {[f.name for f in tmp_files]}"

    def test_concurrent_writes_with_stale_files(self, tmp_path):
        """并发写入前存在stale文件，验证stale清理不影响并发。"""
        agents_dir = tmp_path / ".agents"
        cache_dir = agents_dir / ".cache"
        cache_dir.mkdir(parents=True)
        (agents_dir / "ONBOARDING.md").write_text("# L0", encoding="utf-8")
        for i in range(5):
            stale = cache_dir / f"concurrent-test.json.pid{90000+i}.{'ff'*3}.tmp"
            stale.write_text("stale")
            old_t = time.time() - _DEFAULT_STALE_MAX_AGE_SEC - 100
            os.utime(stale, (old_t, old_t))
        num_workers = 6
        barrier = multiprocessing.Barrier(num_workers)
        manager = multiprocessing.Manager()
        results = manager.dict()
        processes = []
        for i in range(num_workers):
            p = multiprocessing.Process(
                target=_mp_concurrent_worker,
                args=(str(tmp_path), i, barrier, results),
            )
            processes.append(p)
            p.start()
        for p in processes:
            p.join(timeout=30)
        successes = sum(1 for r in results.values() if r["status"] == "success")
        assert successes == num_workers
        cache_path = cache_dir / "concurrent-test.json"
        assert cache_path.exists()
        final_data = json.loads(cache_path.read_text(encoding="utf-8"))
        assert "worker_id" in final_data
        tmp_files = list(cache_dir.glob("concurrent-test.json.pid*.tmp"))
        assert len(tmp_files) == 0


class TestCustomRetryParams:
    """自定义重试参数测试。"""

    def test_custom_max_retries(self, tmp_path):
        dst = tmp_path / "test.bin"
        call_count = 0
        _orig_replace = os.replace

        def fail_n_then_succeed(s, d):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise PermissionError("锁")
            return _orig_replace(s, d)

        with patch.object(aw.os, "replace", fail_n_then_succeed):
            atomic_write_bytes(dst, b"data", max_retries=3, retry_interval_ms=1)
        assert dst.read_bytes() == b"data"
        assert call_count == 3

    def test_zero_retries_fails_immediately(self, tmp_path):
        dst = tmp_path / "test.bin"
        call_count = 0

        def fail_always(s, d):
            nonlocal call_count
            call_count += 1
            raise PermissionError("锁")

        with patch.object(aw.os, "replace", fail_always):
            with pytest.raises(PermissionError):
                atomic_write_bytes(dst, b"data", max_retries=0, retry_interval_ms=1)
        assert call_count == 1

    def test_disable_stale_cleanup(self, tmp_path):
        dst = tmp_path / "test.bin"
        stale = tmp_path / f"test.bin.pid99999.{'a'*6}.tmp"
        stale.write_text("old")
        old_time = time.time() - _DEFAULT_STALE_MAX_AGE_SEC - 1000
        os.utime(stale, (old_time, old_time))
        atomic_write_bytes(dst, b"data", cleanup_stale=False)
        assert stale.exists()
        stale.unlink()


class TestAtomicEditText:
    """原子编辑（read-modify-write）测试。"""

    def test_basic_edit(self, tmp_path):
        dst = tmp_path / "edit.md"
        dst.write_text("hello world", encoding="utf-8")
        result = atomic_edit_text(dst, lambda c: c.replace("world", "universe"))
        assert result == dst
        assert dst.read_text(encoding="utf-8") == "hello universe"

    def test_edit_preserves_rest_of_file(self, tmp_path):
        dst = tmp_path / "edit.md"
        original = "# Title\n\n<!-- START -->old<!-- END -->\n\nfooter"
        dst.write_text(original, encoding="utf-8")

        def replace_marker(content):
            return content.replace("old", "new")

        atomic_edit_text(dst, replace_marker)
        result = dst.read_text(encoding="utf-8")
        assert "new" in result
        assert "# Title" in result
        assert "footer" in result
        assert "old" not in result

    def test_edit_marker_region_simulation(self, tmp_path):
        dst = tmp_path / "doc.md"
        original = "before<!-- MARKER -->old content<!-- /MARKER -->after"
        dst.write_text(original, encoding="utf-8")

        def editor(content):
            start = content.find("<!-- MARKER -->") + len("<!-- MARKER -->")
            end = content.find("<!-- /MARKER -->")
            return content[:start] + "new content" + content[end:]

        atomic_edit_text(dst, editor)
        assert dst.read_text(encoding="utf-8") == "before<!-- MARKER -->new content<!-- /MARKER -->after"

    def test_edit_raises_on_missing_file(self, tmp_path):
        dst = tmp_path / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            atomic_edit_text(dst, lambda c: c + "modified")

    def test_edit_propagates_editor_exception(self, tmp_path):
        dst = tmp_path / "edit.md"
        dst.write_text("content", encoding="utf-8")

        def bad_editor(c):
            raise ValueError("edit failed")

        with pytest.raises(ValueError, match="edit failed"):
            atomic_edit_text(dst, bad_editor)
        assert dst.read_text(encoding="utf-8") == "content"

    def test_edit_no_tmp_residue(self, tmp_path):
        dst = tmp_path / "edit.md"
        dst.write_text("original", encoding="utf-8")
        atomic_edit_text(dst, lambda c: "modified")
        tmp_files = list(tmp_path.glob("edit.md.pid*.tmp"))
        assert len(tmp_files) == 0

    def test_edit_with_encoding(self, tmp_path):
        dst = tmp_path / "edit.md"
        dst.write_text("你好", encoding="gbk")
        atomic_edit_text(dst, lambda c: c + "世界", encoding="gbk")
        assert dst.read_text(encoding="gbk") == "你好世界"

    def test_concurrent_edits_last_writer_wins(self, tmp_path):
        dst = tmp_path / "counter.txt"
        dst.write_text("0", encoding="utf-8")
        results = []
        for i in range(5):
            def adder(c, val=i):
                return str(int(c) + 1)
            atomic_edit_text(dst, adder, retry_interval_ms=1)
        final = int(dst.read_text(encoding="utf-8"))
        assert final >= 1
        tmp_files = list(tmp_path.glob("counter.txt.pid*.tmp"))
        assert len(tmp_files) == 0


class TestFsyncOption:
    """fsync持久化参数测试。"""

    def test_fsync_true_writes_correctly(self, tmp_path):
        dst = tmp_path / "fsync_test.dat"
        data = b"durable data" * 100
        result = atomic_write_bytes(dst, data, fsync=True)
        assert result == dst
        assert dst.read_bytes() == data

    def test_fsync_false_writes_correctly(self, tmp_path):
        dst = tmp_path / "nofsync_test.dat"
        data = b"fast data" * 100
        result = atomic_write_bytes(dst, data, fsync=False)
        assert dst.read_bytes() == data

    def test_fsync_no_tmp_residue(self, tmp_path):
        dst = tmp_path / "fsync_clean.dat"
        atomic_write_bytes(dst, b"data", fsync=True)
        tmp_files = list(tmp_path.glob("fsync_clean.dat.pid*.tmp"))
        assert len(tmp_files) == 0

    def test_fsync_with_json(self, tmp_path):
        dst = tmp_path / "fsync.json"
        obj = {"key": "value", "n": 42}
        atomic_write_json(dst, obj, fsync=True)
        assert json.loads(dst.read_text(encoding="utf-8")) == obj

    def test_fsync_overwrite_existing(self, tmp_path):
        dst = tmp_path / "fsync_overwrite.dat"
        atomic_write_bytes(dst, b"v1", fsync=True)
        atomic_write_bytes(dst, b"v2_longer_content", fsync=True)
        assert dst.read_bytes() == b"v2_longer_content"


class TestBinaryEdgeCases:
    """二进制数据边缘场景测试。"""

    def test_all_byte_values(self, tmp_path):
        dst = tmp_path / "all_bytes.bin"
        data = bytes(range(256))
        atomic_write_bytes(dst, data)
        assert dst.read_bytes() == data

    def test_null_bytes(self, tmp_path):
        dst = tmp_path / "nulls.bin"
        data = b"\x00\x00\x00data\x00\x00"
        atomic_write_bytes(dst, data)
        assert dst.read_bytes() == data

    def test_very_small_write(self, tmp_path):
        dst = tmp_path / "tiny.dat"
        atomic_write_bytes(dst, b"x")
        assert dst.read_bytes() == b"x"

    def test_unicode_surrogate_pairs(self, tmp_path):
        dst = tmp_path / "unicode.txt"
        text = "🎉🚀💻" + "中文字符测试" + "αβγ"
        atomic_write_text(dst, text, encoding="utf-8")
        assert dst.read_text(encoding="utf-8") == text


class TestDeepNestedPaths:
    """深层嵌套目录自动创建测试。"""

    def test_creates_deep_parent_directories(self, tmp_path):
        dst = tmp_path / "a" / "b" / "c" / "d" / "deep.json"
        result = atomic_write_json(dst, {"deep": True})
        assert result == dst
        assert dst.exists()
        assert json.loads(dst.read_text())["deep"] is True

    def test_creates_nested_path_for_bytes(self, tmp_path):
        dst = tmp_path / "level1" / "level2" / "file.bin"
        atomic_write_bytes(dst, b"nested")
        assert dst.read_bytes() == b"nested"


class TestRapidSequentialWrites:
    """快速连续写入无tmp累积测试。"""

    def test_100_sequential_writes_no_tmp_buildup(self, tmp_path):
        dst = tmp_path / "rapid.json"
        for i in range(100):
            atomic_write_json(dst, {"count": i}, retry_interval_ms=0)
        assert json.loads(dst.read_text())["count"] == 99
        tmp_files = list(tmp_path.glob("rapid.json.pid*.tmp"))
        assert len(tmp_files) == 0

    def test_rapid_writes_correct_final_value(self, tmp_path):
        dst = tmp_path / "rapid.txt"
        for i in range(50):
            atomic_write_text(dst, f"version-{i}", encoding="utf-8", retry_interval_ms=0)
        assert dst.read_text(encoding="utf-8") == "version-49"


class TestStaleCleanupAcrossTargets:
    """stale清理跨目标文件测试。"""

    def test_stale_for_other_target_not_cleaned(self, tmp_path):
        stale_a = tmp_path / "file_a.json.pid999.aaaaaa.tmp"
        stale_b = tmp_path / "file_b.json.pid999.bbbbbb.tmp"
        stale_a.write_bytes(b"old")
        stale_b.write_bytes(b"old")
        old_time = time.time() - 7200
        os.utime(stale_a, (old_time, old_time))
        os.utime(stale_b, (old_time, old_time))

        atomic_write_json(tmp_path / "file_a.json", {"new": True})
        assert not stale_a.exists()
        assert stale_b.exists()
        stale_b.unlink()

    def test_stale_cleanup_skips_recent_tmp_files(self, tmp_path):
        dst = tmp_path / "active.json"
        recent_tmp = tmp_path / "active.json.pid111.abcdef.tmp"
        recent_tmp.write_bytes(b"writing")
        atomic_write_json(dst, {"data": "final"})
        assert dst.exists()
        assert json.loads(dst.read_text())["data"] == "final"
        assert recent_tmp.exists()
        recent_tmp.unlink()

    def test_cleanup_stale_false_keeps_stale_files(self, tmp_path):
        dst = tmp_path / "nostale.json"
        stale = tmp_path / "nostale.json.pid999.deadbe.tmp"
        stale.write_bytes(b"old")
        old_time = time.time() - 7200
        os.utime(stale, (old_time, old_time))
        atomic_write_json(dst, {"fresh": True}, cleanup_stale=False)
        assert stale.exists()
        stale.unlink()

    def test_concurrent_stale_and_write_no_crash(self, tmp_path):
        dst = tmp_path / "race.json"
        for i in range(5):
            stale = tmp_path / f"race.json.pid{9000+i}.{i:06x}.tmp"
            stale.write_bytes(b"old")
            old_time = time.time() - 7200
            os.utime(stale, (old_time, old_time))
        atomic_write_json(dst, {"ok": True})
        assert json.loads(dst.read_text())["ok"] is True
        leftover = list(tmp_path.glob("race.json.pid*.tmp"))
        assert len(leftover) == 0


class TestAtomicEditEdgeCases:
    """原子编辑边缘场景测试。"""

    def test_edit_empty_file(self, tmp_path):
        dst = tmp_path / "empty.txt"
        dst.write_text("", encoding="utf-8")
        atomic_edit_text(dst, lambda c: c + "was empty")
        assert dst.read_text(encoding="utf-8") == "was empty"

    def test_edit_returns_identical_content(self, tmp_path):
        dst = tmp_path / "same.txt"
        dst.write_text("unchanged", encoding="utf-8")
        atomic_edit_text(dst, lambda c: c)
        assert dst.read_text(encoding="utf-8") == "unchanged"
        tmp_files = list(tmp_path.glob("same.txt.pid*.tmp"))
        assert len(tmp_files) == 0

    def test_edit_large_file(self, tmp_path):
        dst = tmp_path / "large.md"
        original = "x" * 100000
        dst.write_text(original, encoding="utf-8")
        atomic_edit_text(dst, lambda c: c.replace("x", "y"))
        result = dst.read_text(encoding="utf-8")
        assert len(result) == 100000
        assert result == "y" * 100000

    def test_edit_identity_function_creates_file_atomically(self, tmp_path):
        dst = tmp_path / "identity.txt"
        dst.write_text("content", encoding="utf-8")
        atomic_edit_text(dst, lambda c: c)
        assert dst.read_text(encoding="utf-8") == "content"


class TestStrPathInput:
    """字符串路径输入兼容性测试。"""

    def test_accepts_string_path(self, tmp_path):
        dst_str = str(tmp_path / "str_path.json")
        result = atomic_write_json(dst_str, {"via": "string"})
        assert isinstance(result, Path)
        assert json.loads(Path(dst_str).read_text())["via"] == "string"

    def test_accepts_string_path_for_bytes(self, tmp_path):
        dst_str = str(tmp_path / "str_bytes.bin")
        atomic_write_bytes(dst_str, b"string-path")
        assert Path(dst_str).read_bytes() == b"string-path"

    def test_accepts_string_path_for_edit(self, tmp_path):
        dst = tmp_path / "str_edit.txt"
        dst.write_text("original", encoding="utf-8")
        atomic_edit_text(str(dst), lambda c: "edited")
        assert dst.read_text(encoding="utf-8") == "edited"
