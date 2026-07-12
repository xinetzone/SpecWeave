"""spec_loader.py 单元测试。

覆盖 L1 分层加载与磁盘缓存核心场景：
- L0/L1a 始终加载
- execution 阶段默认不加载 L1b
- execution 阶段使用 include_l1b=True 强制加载 L1b
- planning 阶段默认加载 L1b
- ensure_l1b() 延迟加载触发
- 磁盘缓存持久化（跨实例命中）
- 缓存 mtime 失效机制
- 内存缓存命中
- 任务类型匹配与路由
- 层加载 L0/L1a/L1b/L1
- 缺失文件处理
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.spec_loader import (
    SpecLoader,
    LoadResult,
    TASK_ROUTING,
    CACHE_DIRNAME,
    CACHE_FILENAME,
    CACHE_VERSION,
)
from lib.atomic_write import _atomic_replace_with_retry


def _make_project(tmp_path: Path, files: dict[str, str]) -> Path:
    agents = tmp_path / ".agents"
    agents.mkdir(parents=True, exist_ok=True)

    default_files = {
        "ONBOARDING.md": "# L0 Entry\nQuick start guide.",
        "global-core-rules.md": "# Global Core Rules\nAll agents must follow.",
        "capability-boundaries.md": "# Capability Boundaries\nWhat agents can/cannot do.",
        "capability-registry.md": "# Capability Registry\nIndex of all capabilities.",
        "context-routing.md": "# Context Routing\nRoute by task type.",
        "skills/README.md": "# Skills\nSkill documentation index.",
    }
    default_files.update(files)

    for rel_path, content in default_files.items():
        if "/" in rel_path:
            parent = agents / rel_path.rsplit("/", 1)[0]
            parent.mkdir(parents=True, exist_ok=True)
        (agents / rel_path).write_text(content, encoding="utf-8")

    return tmp_path


class TestL0L1aAlwaysLoaded:
    """L0 和 L1a 在任何阶段都应始终加载。"""

    def test_execution_loads_l0_and_l1a(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("some task", stage="execution")
            layers = {s.layer for s in result.loaded_specs}
            assert "L0" in layers
            assert "L1a" in layers
            assert result.layer_summary["L0"] == 1
            assert result.layer_summary["L1a"] == 2

    def test_planning_loads_l0_and_l1a(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("some task", stage="planning")
            assert result.layer_summary["L0"] == 1
            assert result.layer_summary["L1a"] == 2

    def test_startup_loads_l0_and_l1a(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("some task", stage="startup")
            assert result.layer_summary["L0"] == 1
            assert result.layer_summary["L1a"] == 2


class TestL1bDeferredInExecution:
    """execution 阶段默认不加载 L1b（P0 拆分优化核心）。"""

    def test_execution_default_no_l1b(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("代码审查", stage="execution")
            assert result.layer_summary["L1b"] == 0, "execution阶段不应加载L1b"
            loaded_paths = {s.path for s in result.loaded_specs}
            for l1b_file in SpecLoader.L1B_INDEX_SPECS:
                assert l1b_file not in loaded_paths, f"L1b文件 {l1b_file} 不应在execution阶段加载"

    def test_execution_forced_include_l1b(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task(
                "代码审查", stage="execution", include_l1b=True
            )
            assert result.layer_summary["L1b"] == 3, "include_l1b=True时应加载全部3个L1b文件"
            loaded_paths = {s.path for s in result.loaded_specs}
            for l1b_file in SpecLoader.L1B_INDEX_SPECS:
                assert l1b_file in loaded_paths, f"强制加载时 {l1b_file} 应被加载"

    def test_execution_include_l1b_false_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task(
                "代码审查", stage="planning", include_l1b=False
            )
            assert result.layer_summary["L1b"] == 0, "include_l1b=False应覆盖planning阶段默认行为"

    def test_verification_stage_no_l1b(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("代码审查", stage="verification")
            assert result.layer_summary["L1b"] == 0, "verification阶段不应加载L1b"


class TestL1bLoadedInPlanning:
    """planning 阶段默认加载 L1b。"""

    def test_planning_default_loads_l1b(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("代码审查", stage="planning")
            assert result.layer_summary["L1b"] == 3, "planning阶段应加载全部3个L1b文件"
            loaded_paths = {s.path for s in result.loaded_specs}
            for l1b_file in SpecLoader.L1B_INDEX_SPECS:
                assert l1b_file in loaded_paths, f"planning阶段 {l1b_file} 应被加载"

    def test_startup_default_loads_l1b(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("代码审查", stage="startup")
            assert result.layer_summary["L1b"] == 3, "startup阶段应加载L1b"


class TestEnsureL1b:
    """ensure_l1b() 延迟加载方法。"""

    def test_ensure_l1b_after_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result_exec = loader.load_for_task("代码审查", stage="execution")
            assert result_exec.layer_summary["L1b"] == 0

            result_l1b = loader.ensure_l1b()
            assert result_l1b.layer_summary["L1b"] == 3
            for l1b_file in SpecLoader.L1B_INDEX_SPECS:
                assert l1b_file in loader.get_loaded_paths()

    def test_ensure_l1b_already_loaded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            loader.load_for_task("代码审查", stage="planning")
            result = loader.ensure_l1b()
            assert len(result.loaded_specs) == 0
            assert len(result.already_loaded) == 3


class TestLayerLoading:
    """按层加载方法测试。"""

    def test_load_layer_l0(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_layer("L0")
            assert result.layer_summary["L0"] == 1
            assert result.layer_summary["L1a"] == 0
            assert result.layer_summary["L1b"] == 0

    def test_load_layer_l1a(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_layer("L1a")
            assert result.layer_summary["L1a"] == 2
            assert result.layer_summary["L1b"] == 0

    def test_load_layer_l1b(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_layer("L1b")
            assert result.layer_summary["L1b"] == 3
            assert result.layer_summary["L1a"] == 0

    def test_load_layer_l1_includes_all(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_layer("L1")
            assert result.layer_summary["L1a"] == 2
            assert result.layer_summary["L1b"] == 3


class TestTaskRouting:
    """任务类型关键词匹配与L2路由。"""

    def test_match_code_review(self):
        root = resolve_real_root()
        loader = SpecLoader(root, use_disk_cache=False)
        matched = loader.match_task_type("代码审查一下这个PR")
        assert "code_review" in matched

    def test_match_commit(self):
        root = resolve_real_root()
        loader = SpecLoader(root, use_disk_cache=False)
        matched = loader.match_task_type("帮我提交代码")
        assert "commit" in matched

    def test_match_multiple_types(self):
        root = resolve_real_root()
        loader = SpecLoader(root, use_disk_cache=False)
        matched = loader.match_task_type("复盘并生成mermaid流程图")
        assert "retrospective" in matched
        assert "mermaid" in matched

    def test_no_match_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            matched = loader.match_task_type("asdf qwerty zxcvbn")
            assert matched == []

    def test_l2_specs_loaded_for_matched_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {
                "workflows/code-review.md": "# Code Review\nReview workflow.",
                "roles/reviewer.md": "# Reviewer\nReviewer role.",
            })
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("代码审查", stage="execution")
            assert result.layer_summary["L2"] == 2
            assert result.total_chars > 0


class TestDiskCache:
    """磁盘缓存核心机制测试。"""

    def test_disk_cache_persists_across_instances(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader1 = SpecLoader(root, use_disk_cache=True)
            loader1.load_for_task("代码审查", stage="execution")
            loader1.save_cache()

            cache_path = root / ".agents" / CACHE_DIRNAME / CACHE_FILENAME
            assert cache_path.exists()

            loader2 = SpecLoader(root, use_disk_cache=True)
            result = loader2.load_for_task("代码审查", stage="execution")
            stats = loader2.get_cache_stats()
            assert stats["disk_cache_hits"] >= 3, f"温启动应命中磁盘缓存，实际命中={stats['disk_cache_hits']}"

    def test_disk_cache_mtime_invalidation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            target_file = root / ".agents" / "ONBOARDING.md"
            original_content = target_file.read_text(encoding="utf-8")

            loader1 = SpecLoader(root, use_disk_cache=True)
            loader1.load_for_task("代码审查", stage="execution")
            loader1.save_cache()

            time.sleep(0.05)
            target_file.write_text(original_content + "\n\n<!-- modified -->", encoding="utf-8")

            loader2 = SpecLoader(root, use_disk_cache=True)
            result = loader2.load_for_task("代码审查", stage="execution")
            onboarding_specs = [s for s in result.loaded_specs if s.path == "ONBOARDING.md"]
            assert len(onboarding_specs) == 1
            assert "modified" in onboarding_specs[0].content, "mtime变化后应读取新内容"

    def test_cache_version_mismatch_rebuilds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            cache_dir = root / ".agents" / CACHE_DIRNAME
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_path = cache_dir / CACHE_FILENAME
            cache_path.write_text(json.dumps({
                "version": 999,
                "entries": {"fake": {"path": "fake.md", "content": "stale", "mtime": 0}}
            }), encoding="utf-8")

            loader = SpecLoader(root, use_disk_cache=True)
            assert len(loader._disk_cache) == 0, "版本不匹配应丢弃所有缓存条目"

    def test_memory_cache_hit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            r1 = loader.load_for_task("代码审查", stage="execution")
            r2 = loader.load_for_task("代码审查", stage="execution")
            assert len(r2.loaded_specs) == 0
            assert len(r2.already_loaded) >= 3

    def test_invalidate_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=True)
            loader.load_for_task("代码审查", stage="execution")
            loader.save_cache()
            cache_path = root / ".agents" / CACHE_DIRNAME / CACHE_FILENAME
            assert cache_path.exists()

            loader.invalidate_cache()
            assert not cache_path.exists()
            assert len(loader._loaded) == 0
            assert len(loader._disk_cache) == 0


class TestAtomicReplaceRetry:
    """原子写入重试机制测试。"""

    def test_normal_replace_succeeds_first_try(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            src = d / "data.tmp"
            dst = d / "data.json"
            src.write_text('{"ok": true}', encoding="utf-8")
            _atomic_replace_with_retry(src, dst)
            assert dst.exists()
            assert not src.exists()
            data = json.loads(dst.read_text(encoding="utf-8"))
            assert data["ok"] is True

    def test_overwrite_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            src = d / "new.tmp"
            dst = d / "target.json"
            dst.write_text("old content", encoding="utf-8")
            src.write_text("new content", encoding="utf-8")
            _atomic_replace_with_retry(src, dst)
            assert dst.read_text(encoding="utf-8") == "new content"
            assert not src.exists()

    def test_retry_on_permission_error_succeeds_eventually(self):
        import unittest.mock as mock
        call_count = [0]
        real_replace = os.replace

        def flaky_replace(s, d):
            call_count[0] += 1
            if call_count[0] <= 2:
                raise PermissionError("[WinError 5] Access is denied")
            return real_replace(str(s), str(d))

        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            src = d / "data.tmp"
            dst = d / "data.json"
            src.write_text("flaky", encoding="utf-8")
            with mock.patch("lib.spec_loader.os.replace", side_effect=flaky_replace):
                _atomic_replace_with_retry(src, dst, max_retries=3, interval_ms=1)
            assert dst.read_text(encoding="utf-8") == "flaky"
            assert call_count[0] == 3

    def test_all_retries_exhausted_raises_and_cleans_tmp(self):
        import unittest.mock as mock
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            src = d / "data.tmp"
            dst = d / "data.json"
            src.write_text("fail", encoding="utf-8")
            with mock.patch("lib.spec_loader.os.replace",
                            side_effect=PermissionError("[WinError 5] Access denied")):
                with pytest.raises(PermissionError):
                    _atomic_replace_with_retry(src, dst, max_retries=2, interval_ms=1)
            assert not src.exists(), "所有重试失败后应清理临时文件"

    def test_non_permission_oserror_propagates(self):
        import unittest.mock as mock
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            src = d / "data.tmp"
            dst = d / "/nonexistent/dir/data.json"
            src.write_text("x", encoding="utf-8")
            with pytest.raises(OSError):
                _atomic_replace_with_retry(src, dst, max_retries=2, interval_ms=1)

    def test_save_cache_with_concurrent_write_no_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=True)
            loader.load_for_task("代码审查", stage="execution")
            loader.save_cache()
            cache_path = root / ".agents" / CACHE_DIRNAME / CACHE_FILENAME
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            assert data["version"] == CACHE_VERSION
            assert len(data["entries"]) >= 3
            for key, entry in data["entries"].items():
                assert "path" in entry
                assert "content" in entry
                assert "mtime" in entry

    def test_atomic_write_produces_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            for _ in range(5):
                loader = SpecLoader(root, use_disk_cache=True)
                loader.load_for_task("代码审查", stage="execution")
                loader.save_cache()
                cache_path = root / ".agents" / CACHE_DIRNAME / CACHE_FILENAME
                raw = cache_path.read_text(encoding="utf-8")
                data = json.loads(raw)
                assert "entries" in data
                assert isinstance(data["entries"], dict)

    def test_tmp_filename_contains_pid_and_unique_suffix(self):
        import unittest.mock as mock
        import random
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            cache_dir = root / ".agents" / CACHE_DIRNAME
            loader = SpecLoader(root, use_disk_cache=True)
            loader.load_for_task("代码审查", stage="execution")
            with mock.patch("os.getpid", return_value=12345):
                with mock.patch("random.randint", return_value=0xABCDEF):
                    loader.save_cache()
            tmp_files = list(cache_dir.glob("*.tmp*"))
            assert len(tmp_files) == 0, f"保存成功后不应残留tmp文件，但发现: {tmp_files}"
            cache_path = cache_dir / CACHE_FILENAME
            assert cache_path.exists()

    def test_concurrent_save_no_tmp_collision(self):
        import unittest.mock as mock
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            cache_dir = root / ".agents" / CACHE_DIRNAME
            loader1 = SpecLoader(root, use_disk_cache=True)
            loader1.load_for_task("代码审查", stage="execution")
            loader2 = SpecLoader(root, use_disk_cache=True)
            loader2.load_for_task("原子提交", stage="execution")
            with mock.patch("os.getpid", return_value=100):
                with mock.patch("random.randint", return_value=0x111111):
                    loader1.save_cache()
            assert not list(cache_dir.glob("*.tmp*")), "loader1保存后无tmp残留"
            with mock.patch("os.getpid", return_value=200):
                with mock.patch("random.randint", return_value=0x222222):
                    loader2.save_cache()
            tmp_files = list(cache_dir.glob("*.tmp*"))
            assert len(tmp_files) == 0, f"两次保存后无tmp残留，但发现: {tmp_files}"
            data = json.loads((cache_dir / CACHE_FILENAME).read_text(encoding="utf-8"))
            assert len(data["entries"]) >= 3

    def test_failed_save_only_cleans_own_tmp(self):
        import unittest.mock as mock
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            cache_dir = root / ".agents" / CACHE_DIRNAME
            stale_tmp = cache_dir / f"{CACHE_FILENAME}.pid999.abcdef.tmp"
            cache_dir.mkdir(parents=True, exist_ok=True)
            stale_tmp.write_text('{"stale": true}', encoding="utf-8")
            loader = SpecLoader(root, use_disk_cache=True)
            loader.load_for_task("代码审查", stage="execution")
            with mock.patch("os.getpid", return_value=12345):
                with mock.patch("random.randint", return_value=0xFEDCBA):
                    real_replace = os.replace
                    call_count = [0]
                    def flaky_replace(s, d):
                        call_count[0] += 1
                        if call_count[0] <= 3:
                            raise PermissionError("[WinError 5] Access denied")
                        return real_replace(str(s), str(d))
                    with mock.patch("lib.spec_loader.os.replace", side_effect=flaky_replace):
                        loader.save_cache()
            assert stale_tmp.exists(), "失败后不应清理其他进程的stale tmp"
            assert not list(cache_dir.glob(f"{CACHE_FILENAME}.pid12345.*.tmp")), "自己的tmp应被清理"
            stale_tmp.unlink()

    def test_stale_tmp_cleanup_on_save(self):
        import unittest.mock as mock
        import time as _time
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            cache_dir = root / ".agents" / CACHE_DIRNAME
            cache_dir.mkdir(parents=True, exist_ok=True)
            old_tmp = cache_dir / f"{CACHE_FILENAME}.pid1.old001.tmp"
            old_tmp.write_text('old', encoding="utf-8")
            old_time = _time.time() - 3600
            os.utime(old_tmp, (old_time, old_time))
            fresh_tmp = cache_dir / f"{CACHE_FILENAME}.pid2.fresh002.tmp"
            fresh_tmp.write_text('fresh', encoding="utf-8")
            loader = SpecLoader(root, use_disk_cache=True)
            loader.load_for_task("代码审查", stage="execution")
            with mock.patch("os.getpid", return_value=3):
                with mock.patch("random.randint", return_value=0x333333):
                    loader.save_cache()
            assert not old_tmp.exists(), "超过1小时的stale tmp应被清理"
            assert fresh_tmp.exists(), "近期tmp（<1小时）不应被误清理"
            fresh_tmp.unlink()


class TestMissingFiles:
    """缺失文件处理。"""

    def test_missing_l0_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            (root / ".agents" / "ONBOARDING.md").unlink()
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_layer("L0")
            assert "ONBOARDING.md" in result.missing_specs

    def test_missing_l2_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_specific(["nonexistent/file.md"], layer="L2")
            assert "nonexistent/file.md" in result.missing_specs


class TestResultSummary:
    """LoadResult.summary() 输出测试。"""

    def test_summary_format(self):
        result = LoadResult()
        text = result.summary()
        assert "规范加载结果" in text
        assert "L0" in text
        assert "L1a" in text
        assert "L1b" in text
        assert "L2" in text

    def test_summary_with_missing(self):
        result = LoadResult()
        result.missing_specs.append("missing.md")
        text = result.summary()
        assert "未找到" in text
        assert "missing.md" in text

    def test_spec_count_and_l1_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("代码审查", stage="planning")
            assert result.spec_count == result.layer_summary["L0"] + result.layer_summary["L1a"] + \
                   result.layer_summary["L1b"] + result.layer_summary["L2"]
            assert result.l1_count == result.layer_summary["L1a"] + result.layer_summary["L1b"]


class TestCacheStats:
    """缓存统计信息。"""

    def test_initial_stats_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            stats = loader.get_cache_stats()
            assert stats["memory_loaded"] == 0
            assert stats["disk_entries"] == 0
            assert stats["disk_cache_hits"] == 0
            assert stats["disk_cache_misses"] == 0

    def test_hit_rate_after_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            loader.load_for_task("代码审查", stage="execution")
            stats = loader.get_cache_stats()
            assert stats["disk_cache_misses"] > 0
            assert stats["hit_rate"] == 0.0


class TestL1bEdgeCases:
    """L1b 延迟加载边缘场景覆盖。"""

    def test_execution_then_planning_loads_l1b_without_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {
                "workflows/code-review.md": "# CR",
                "roles/reviewer.md": "# Reviewer",
            })
            loader = SpecLoader(root, use_disk_cache=False)
            r_exec = loader.load_for_task("代码审查", stage="execution")
            assert r_exec.layer_summary["L1b"] == 0
            paths_after_exec = loader.get_loaded_paths()
            for l1b_f in SpecLoader.L1B_INDEX_SPECS:
                assert l1b_f not in paths_after_exec

            r_plan = loader.load_for_task("代码审查", stage="planning")
            assert r_plan.layer_summary["L1b"] == 3
            l0_l1a_duplicates = sum(
                1 for s in r_plan.loaded_specs if s.layer in ("L0", "L1a")
            )
            assert l0_l1a_duplicates == 0, "第二次调用不应重复加载L0/L1a"

            all_paths = loader.get_loaded_paths()
            for l1b_f in SpecLoader.L1B_INDEX_SPECS:
                assert l1b_f in all_paths

    def test_l1b_content_correctness(self):
        unique_content = "UNIQUE_L1B_MARKER_xyz123"
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {
                "capability-registry.md": f"# Registry\n{unique_content}",
            })
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("代码审查", stage="planning")
            reg_specs = [s for s in result.loaded_specs if s.path == "capability-registry.md"]
            assert len(reg_specs) == 1
            assert unique_content in reg_specs[0].content

    def test_l1b_layer_marker_correct(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_layer("L1b")
            for spec in result.loaded_specs:
                assert spec.layer == "L1b", f"{spec.path} 应标记为L1b层"

    def test_l1a_l1b_no_overlap(self):
        l1a_set = set(SpecLoader.L1A_CORE_SPECS)
        l1b_set = set(SpecLoader.L1B_INDEX_SPECS)
        assert l1a_set & l1b_set == set(), "L1a和L1b不应有重叠文件"
        assert set(SpecLoader.L1_SPECS) == l1a_set | l1b_set, "L1_SPECS应等于L1a+L1b"

    def test_cross_instance_l1b_cold_load_after_execution_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader1 = SpecLoader(root, use_disk_cache=True)
            r1 = loader1.load_for_task("代码审查", stage="execution")
            assert r1.layer_summary["L1b"] == 0
            loader1.save_cache()

            loader2 = SpecLoader(root, use_disk_cache=True)
            r2 = loader2.load_for_task("代码审查", stage="planning")
            assert r2.layer_summary["L1b"] == 3, "实例2在planning阶段应能加载L1b（即使实例1未缓存）"
            paths2 = loader2.get_loaded_paths()
            for l1b_f in SpecLoader.L1B_INDEX_SPECS:
                assert l1b_f in paths2

    def test_format_prompt_excludes_l1b_in_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            r_exec = loader.load_for_task("代码审查", stage="execution")
            out_exec = loader.format_for_prompt(r_exec, include_content=False)
            assert "L1b" in out_exec
            for l1b_f in SpecLoader.L1B_INDEX_SPECS:
                assert l1b_f not in out_exec, f"execution输出不应包含L1b文件 {l1b_f}"

            r_plan = loader.load_for_task("代码审查", stage="planning")
            out_plan = loader.format_for_prompt(r_plan, include_content=False)
            for l1b_f in SpecLoader.L1B_INDEX_SPECS:
                assert l1b_f in out_plan, f"planning输出应包含L1b文件 {l1b_f}"

    def test_get_loaded_paths_after_ensure_l1b(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            loader.load_for_task("代码审查", stage="execution")
            assert not any(p in loader.get_loaded_paths() for p in SpecLoader.L1B_INDEX_SPECS)

            loader.ensure_l1b()
            loaded = loader.get_loaded_paths()
            for l1b_f in SpecLoader.L1B_INDEX_SPECS:
                assert l1b_f in loaded

    def test_loadedfrom_indicates_disk_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader1 = SpecLoader(root, use_disk_cache=True)
            loader1.load_for_task("代码审查", stage="execution")
            loader1.save_cache()

            loader2 = SpecLoader(root, use_disk_cache=True)
            r2 = loader2.load_for_task("代码审查", stage="execution")
            for spec in r2.loaded_specs:
                assert "disk-cache" in spec.loaded_from, f"温启动加载 {spec.path} 应标记disk-cache来源"

    def test_unknown_stage_defaults_to_l1a_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("代码审查", stage="unknown_stage")
            assert result.layer_summary["L1b"] == 0, "未知阶段应默认不加载L1b（fallback到execution行为）"

    def test_load_specific_l1b_marks_layer_correctly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_specific(SpecLoader.L1B_INDEX_SPECS, layer="L1b")
            assert result.layer_summary["L1b"] == 3
            for spec in result.loaded_specs:
                assert spec.layer == "L1b"


class TestLightweightMode:
    """P1 优化 3.3：轻量模式（L2 懒加载）测试。"""

    def test_lightweight_loads_only_l0_l1a(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {
                "workflows/code-review.md": "# CR\nReview workflow.",
                "roles/reviewer.md": "# Reviewer\nReviewer role.",
            })
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task_lightweight("代码审查")
            assert result.lightweight is True
            assert result.layer_summary["L0"] == 1
            assert result.layer_summary["L1a"] == 2
            assert result.layer_summary["L1b"] == 0
            assert result.layer_summary["L2"] == 0
            assert len(result.pending_l2) > 0, "轻量模式应返回L2待加载清单"

    def test_lightweight_pending_l2_contains_expected_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {
                "workflows/code-review.md": "# CR",
                "roles/reviewer.md": "# Reviewer",
            })
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task_lightweight("代码审查")
            assert "workflows/code-review.md" in result.pending_l2
            assert "roles/reviewer.md" in result.pending_l2

    def test_lightweight_does_not_read_l2_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {
                "workflows/code-review.md": "# CR content",
                "roles/reviewer.md": "# Reviewer content",
            })
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task_lightweight("代码审查")
            loaded_paths = {s.path for s in result.loaded_specs}
            assert "workflows/code-review.md" not in loaded_paths
            assert "roles/reviewer.md" not in loaded_paths

    def test_load_spec_content_reads_single_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            unique = "LOAD_SPEC_CONTENT_MARKER_abc999"
            root = _make_project(Path(tmp), {
                "workflows/code-review.md": f"# CR\n{unique}",
                "roles/reviewer.md": "# Reviewer",
            })
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task_lightweight("代码审查")
            assert result.layer_summary["L2"] == 0
            spec = loader.load_spec_content("workflows/code-review.md")
            assert spec is not None
            assert unique in spec.content
            assert spec.layer == "L2"
            assert "workflows/code-review.md" in loader.get_loaded_paths()

    def test_load_spec_content_returns_cached(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {
                "workflows/code-review.md": "# CR",
                "roles/reviewer.md": "# Reviewer",
            })
            loader = SpecLoader(root, use_disk_cache=False)
            s1 = loader.load_spec_content("workflows/code-review.md")
            s2 = loader.load_spec_content("workflows/code-review.md")
            assert s1 is s2, "重复调用应返回内存缓存中同一对象"

    def test_lightweight_then_full_load_no_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {
                "workflows/code-review.md": "# CR",
                "roles/reviewer.md": "# Reviewer",
            })
            loader = SpecLoader(root, use_disk_cache=False)
            r_light = loader.load_for_task_lightweight("代码审查")
            assert r_light.layer_summary["L2"] == 0
            r_full = loader.load_for_task("代码审查")
            l2_new = [s for s in r_full.loaded_specs if s.layer == "L2"]
            assert len(l2_new) == 2

    def test_lightweight_summary_contains_pending_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {
                "workflows/code-review.md": "# CR",
                "roles/reviewer.md": "# Reviewer",
            })
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task_lightweight("代码审查")
            text = result.summary()
            assert "轻量模式" in text
            assert "待加载L2清单" in text

    def test_format_prompt_lightweight_shows_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {
                "workflows/code-review.md": "# CR",
                "roles/reviewer.md": "# Reviewer",
            })
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task_lightweight("代码审查")
            out = loader.format_for_prompt(result, include_content=False)
            assert "lightweight" in out
            assert "待加载清单" in out
            assert "workflows/code-review.md" in out


class TestPrimaryTypeAndPriority:
    """P1 优化 3.5：多类型匹配权重排序与角色文件截断测试。"""

    def test_match_returns_primary_type_first(self):
        root = resolve_real_root()
        loader = SpecLoader(root, use_disk_cache=False)
        matched = loader.match_task_type("代码审查")
        assert matched[0] == "code_review", "精确关键词在句首应为最高权重主类型"

    def test_match_keyword_at_start_has_highest_weight(self):
        root = resolve_real_root()
        loader = SpecLoader(root, use_disk_cache=False)
        matched = loader.match_task_type("提交代码并做代码审查")
        assert matched[0] == "commit", "句首关键词'提交'应为主类型"
        assert "code_review" in matched

    def test_auxiliary_types_skip_role_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {
                "workflows/code-review.md": "# CR workflow",
                "roles/reviewer.md": "# Reviewer role",
                "workflows/testing.md": "# Testing workflow",
                "roles/tester.md": "# Tester role",
            })
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("代码审查和测试")
            loaded_paths = {s.path for s in result.loaded_specs}
            assert "workflows/code-review.md" in loaded_paths
            assert "roles/reviewer.md" in loaded_paths, "主类型的roles应加载"
            assert "workflows/testing.md" in loaded_paths, "辅助类型的workflow应加载"
            assert "roles/tester.md" not in loaded_paths, "辅助类型的roles应跳过，避免角色冲突"

    def test_primary_only_loads_single_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {
                "workflows/code-review.md": "# CR",
                "roles/reviewer.md": "# Reviewer",
                "workflows/testing.md": "# Testing",
                "roles/tester.md": "# Tester",
            })
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("代码审查和测试", primary_only=True)
            assert result.primary_type == "code_review"
            loaded_paths = {s.path for s in result.loaded_specs}
            assert "workflows/code-review.md" in loaded_paths
            assert "roles/reviewer.md" in loaded_paths
            assert "workflows/testing.md" not in loaded_paths, "primary_only时辅助类型完全跳过"
            assert "roles/tester.md" not in loaded_paths

    def test_result_primary_type_field_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {
                "workflows/code-review.md": "# CR",
                "roles/reviewer.md": "# Reviewer",
            })
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("代码审查")
            assert result.primary_type == "code_review"
            assert "code_review" in result.matched_types

    def test_no_match_primary_type_is_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("asdf qwerty")
            assert result.primary_type is None
            assert result.matched_types == []
            assert result.pending_l2 == []

    def test_summary_shows_primary_and_aux_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {
                "workflows/code-review.md": "# CR",
                "roles/reviewer.md": "# Reviewer",
                "workflows/testing.md": "# Testing",
                "roles/tester.md": "# Tester",
            })
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("代码审查和测试")
            text = result.summary()
            assert "主任务类型" in text
            assert "code_review" in text

    def test_exact_match_gets_bonus_weight(self):
        root = resolve_real_root()
        loader = SpecLoader(root, use_disk_cache=False)
        matched = loader.match_task_type("代码审查")
        assert matched[0] == "code_review"
        assert len(matched) == 1, "精确匹配不应混入其他类型"


class TestLoadSpecContentEdgeCases:
    """load_spec_content 边缘场景测试。"""

    def test_load_nonexistent_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            spec = loader.load_spec_content("nonexistent/file.md")
            assert spec is None

    def test_is_role_spec_helper(self):
        assert SpecLoader._is_role_spec(None, "roles/reviewer.md") is True
        assert SpecLoader._is_role_spec(None, "workflows/testing.md") is False
        assert SpecLoader._is_role_spec(None, "commands/mermaid.md") is False
        assert SpecLoader._is_role_spec(None, "skills/mermaid-cmd/SKILL.md") is False


class TestBatchRead:
    """3.4 批量文件读取优化测试（P2）。

    验证 _read_specs_batch 批量读取与逐文件读取行为一致，
    且 load_layer 对 L0/L1a 使用批量路径后结果正确。
    """

    def test_batch_read_l0_same_as_sequential(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            l0_paths = list(loader.L0_SPECS)
            loaded, already, missing = loader._read_specs_batch(
                l0_paths, "L0", "test:batch"
            )
            assert len(loaded) == 1, "L0应加载1个文件"
            assert len(already) == 0
            assert len(missing) == 0
            spec = loaded[0]
            assert spec.path in l0_paths
            assert spec.layer == "L0"
            assert len(spec.content) > 0
            assert spec.char_count == len(spec.content)

    def test_batch_read_l1a_same_content_as_sequential(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader_seq = SpecLoader(root, use_disk_cache=False)
            loader_batch = SpecLoader(root, use_disk_cache=False)
            l1a_paths = list(loader_batch.L1A_CORE_SPECS)
            loaded, already, missing = loader_batch._read_specs_batch(
                l1a_paths, "L1a", "test:batch"
            )
            assert len(loaded) == 2
            assert len(missing) == 0
            batch_contents = {s.path: s.content for s in loaded}
            for p in l1a_paths:
                seq_spec = loader_seq._read_spec(p, "L1a", "test:seq")
                assert seq_spec is not None
                assert batch_contents[p] == seq_spec.content, \
                    f"文件 {p} 批量读取内容应与逐文件读取一致"

    def test_batch_read_with_partial_memory_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            l1a_paths = list(loader.L1A_CORE_SPECS)
            first_spec = loader._read_spec(l1a_paths[0], "L1a", "test:preload")
            assert first_spec is not None
            loaded, already, missing = loader._read_specs_batch(
                l1a_paths, "L1a", "test:batch"
            )
            assert l1a_paths[0] in already, "已在内存缓存的文件应出现在already列表"
            assert len(loaded) == 1, "未缓存的文件应加载"
            assert loaded[0].path == l1a_paths[1]
            assert len(missing) == 0

    def test_batch_read_all_cached_returns_empty_loaded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            l0_paths = list(loader.L0_SPECS)
            loader._read_spec(l0_paths[0], "L0", "test:preload")
            loaded, already, missing = loader._read_specs_batch(
                l0_paths, "L0", "test:batch"
            )
            assert len(loaded) == 0
            assert l0_paths[0] in already
            assert len(missing) == 0

    def test_batch_read_missing_files_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            mixed_paths = ["ONBOARDING.md", "nonexistent/file.md"]
            loaded, already, missing = loader._read_specs_batch(
                mixed_paths, "L0", "test:batch"
            )
            assert len(loaded) == 1
            assert len(missing) == 1
            assert "nonexistent/file.md" in missing

    def test_load_layer_l0_l1a_uses_batch_and_produces_correct_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("random task")
            l0_count = result.layer_summary["L0"]
            l1a_count = result.layer_summary["L1a"]
            assert l0_count == 1, "L0应加载1个文件"
            assert l1a_count == 2, "L1a应加载2个文件"
            loaded_paths = {s.path for s in result.loaded_specs}
            assert "ONBOARDING.md" in loaded_paths
            assert "global-core-rules.md" in loaded_paths
            assert "capability-boundaries.md" in loaded_paths
            assert result.total_chars > 0

    def test_load_layer_l1b_still_works_after_batch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_project(Path(tmp), {})
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("random task", stage="planning")
            assert result.layer_summary["L1b"] == 3, "planning阶段L1b应加载3个文件"
            loaded_paths = {s.path for s in result.loaded_specs}
            assert "capability-registry.md" in loaded_paths
            assert "context-routing.md" in loaded_paths
            assert "skills/README.md" in loaded_paths


class TestLogFormattingAudit:
    """3.8 日志延迟格式化审计测试（P2）。

    扫描所有 .agents/scripts/*.py 文件，确认无 f-string 日志调用。
    """

    def test_no_fstring_in_log_calls(self):
        import re
        import pathlib
        pattern = re.compile(r'_log\.(debug|info|warning|error)\(\s*f["\']')
        errors = []
        scripts_root = SCRIPTS_DIR
        for py_file in scripts_root.rglob("*.py"):
            try:
                lines = py_file.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            for i, line in enumerate(lines, 1):
                if pattern.search(line):
                    errors.append(f"{py_file.name}:{i}: {line.strip()}")
        assert not errors, (
            "以下日志调用使用了f-string（应使用%s延迟格式化）:\n" +
            "\n".join(f"  {e}" for e in errors)
        )


class TestMaxCharsFileAtomicity:
    """2.9 max_chars 文件级原子性测试。

    验证：
    1. max_chars按文件粒度检查，要么整个加载要么跳过，不截断文件内容
    2. 达到80%预算时输出WARNING预警
    3. L2文件按优先级排序加载（commands > skills > workflows > roles > rules）
    """

    def test_max_chars_does_not_truncate_file_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            custom_specs = {
                "commands/large-cmd.md": "# Large Command\n" + ("x" * 2000),
                "skills/large-skill.md": "# Large Skill\n" + ("y" * 2000),
                "rules/some-rule.md": "# Rule\n" + ("z" * 1000),
            }
            root = _make_project(Path(tmp), {})
            l1a_dir = root / ".agents"
            for rel_path, content in custom_specs.items():
                fpath = l1a_dir / rel_path
                fpath.parent.mkdir(parents=True, exist_ok=True)
                fpath.write_text(content, encoding="utf-8")

            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("代码审查", stage="execution", max_chars=4500)
            for spec in result.loaded_specs:
                if spec.layer == "L2":
                    assert spec.char_count == len(spec.content), (
                        f"L2文件{spec.path}被截断: char_count={spec.char_count} vs "
                        f"actual={len(spec.content)}"
                    )

    def test_max_chars_atomicity_skips_low_priority_files(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            custom_specs = {
                "commands/cmd.md": "# CMD\n" + ("c" * 500),
                "skills/sk.md": "# SK\n" + ("s" * 500),
                "rules/big-rule.md": "# Big Rule\n" + ("r" * 5000),
            }
            root = _make_project(Path(tmp), {})
            l1a_dir = root / ".agents"
            for rel_path, content in custom_specs.items():
                fpath = l1a_dir / rel_path
                fpath.parent.mkdir(parents=True, exist_ok=True)
                fpath.write_text(content, encoding="utf-8")

            test_routing = {
                "test_task": {
                    "keywords": ["代码审查"],
                    "l2_specs": [
                        "rules/big-rule.md",
                        "skills/sk.md",
                        "commands/cmd.md",
                    ],
                    "description": "test",
                }
            }
            loader = SpecLoader(root, use_disk_cache=False)
            with patch.dict("lib.spec_loader.TASK_ROUTING", test_routing, clear=True):
                result = loader.load_for_task("代码审查", stage="execution", max_chars=2000)
            loaded_l2 = [s.path for s in result.loaded_specs if s.layer == "L2"]
            assert "commands/cmd.md" in loaded_l2, "高优先级commands应优先加载"
            assert "skills/sk.md" in loaded_l2, "高优先级skills应优先加载"
            assert "rules/big-rule.md" not in loaded_l2, (
                "低优先级且超大的rules文件应被跳过"
            )

    def test_max_chars_80_percent_warning(self):
        import logging
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            custom_specs = {
                "commands/a.md": "# A\n" + ("a" * 2500),
                "commands/b.md": "# B\n" + ("b" * 1000),
            }
            root = _make_project(Path(tmp), {})
            l1a_dir = root / ".agents"
            for rel_path, content in custom_specs.items():
                fpath = l1a_dir / rel_path
                fpath.parent.mkdir(parents=True, exist_ok=True)
                fpath.write_text(content, encoding="utf-8")

            test_routing = {
                "test_task": {
                    "keywords": ["代码审查"],
                    "l2_specs": ["commands/a.md", "commands/b.md"],
                    "description": "test",
                }
            }
            loader = SpecLoader(root, use_disk_cache=False)
            import io
            log_capture = io.StringIO()
            handler = logging.StreamHandler(log_capture)
            handler.setLevel(logging.WARNING)
            handler.setFormatter(logging.Formatter("%(message)s"))
            logging.getLogger("spec_loader").addHandler(handler)
            try:
                with patch.dict("lib.spec_loader.TASK_ROUTING", test_routing, clear=True):
                    loader.load_for_task("代码审查", stage="execution", max_chars=4000)
                log_output = log_capture.getvalue()
                assert "80%" in log_output or "预算" in log_output or "上限" in log_output, (
                    f"应输出80%预算预警日志，实际日志:\n{log_output}"
                )
            finally:
                logging.getLogger("spec_loader").removeHandler(handler)

    def test_l2_priority_ordering(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            custom_specs = {
                "commands/cmd.md": "# CMD\n" + ("c" * 200),
                "skills/sk.md": "# SK\n" + ("s" * 200),
                "workflows/wf.md": "# WF\n" + ("w" * 200),
                "roles/rl.md": "# RL\n" + ("r" * 200),
                "rules/ru.md": "# RU\n" + ("u" * 200),
            }
            root = _make_project(Path(tmp), {})
            l1a_dir = root / ".agents"
            for rel_path, content in custom_specs.items():
                fpath = l1a_dir / rel_path
                fpath.parent.mkdir(parents=True, exist_ok=True)
                fpath.write_text(content, encoding="utf-8")

            test_routing = {
                "test_task": {
                    "keywords": ["代码审查"],
                    "l2_specs": [
                        "rules/ru.md",
                        "roles/rl.md",
                        "workflows/wf.md",
                        "skills/sk.md",
                        "commands/cmd.md",
                    ],
                    "description": "test",
                }
            }
            loader = SpecLoader(root, use_disk_cache=False)
            with patch.dict("lib.spec_loader.TASK_ROUTING", test_routing, clear=True):
                result = loader.load_for_task("代码审查", stage="execution")
            l2_paths = [s.path for s in result.loaded_specs if s.layer == "L2"]
            priority_order = ["commands/", "skills/", "workflows/", "roles/", "rules/"]
            last_idx = -1
            for p in l2_paths:
                for pi, prefix in enumerate(priority_order):
                    if p.startswith(prefix):
                        assert pi >= last_idx, (
                            f"L2优先级排序错误: {p}(优先级{pi})出现在"
                            f"优先级{last_idx}的文件之后。实际顺序: {l2_paths}"
                        )
                        last_idx = pi
                        break


class TestNoMatchFallback:
    """2.4 无匹配任务兜底策略测试。

    验证无匹配时加载通用规则集(rules/ai-coding-guidelines.md)而非纯L0+L1a。
    """

    def test_no_match_loads_general_guidelines(self):
        with tempfile.TemporaryDirectory() as tmp:
            custom_l2 = {
                "rules/ai-coding-guidelines.md": "# AI Coding Guidelines\n通用编码规范内容"
            }
            root = _make_project(Path(tmp), custom_l2)
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("xyz随机无关任务12345", stage="execution")
            assert result.primary_type is None
            loaded_paths = {s.path for s in result.loaded_specs}
            assert "rules/ai-coding-guidelines.md" in loaded_paths, (
                "无匹配时应自动加载通用编码规范作为兜底"
            )

    def test_no_match_l2_contains_at_least_guidelines(self):
        with tempfile.TemporaryDirectory() as tmp:
            custom_l2 = {
                "rules/ai-coding-guidelines.md": "# AI Coding Guidelines\n通用规范"
            }
            root = _make_project(Path(tmp), custom_l2)
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("完全不匹配的任务abcxyz", stage="execution")
            l2_files = [s for s in result.loaded_specs if s.layer == "L2"]
            guideline_files = [s for s in l2_files if "ai-coding" in s.path]
            assert len(guideline_files) >= 1, "无匹配时至少应加载ai-coding-guidelines.md"

    def test_matched_task_does_not_load_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            custom_l2 = {
                "workflows/code-review.md": "# Code Review Workflow\n",
                "roles/reviewer.md": "# Reviewer Role\n",
            }
            root = _make_project(Path(tmp), custom_l2)
            loader = SpecLoader(root, use_disk_cache=False)
            result = loader.load_for_task("代码审查", stage="execution")
            assert result.primary_type is not None, "代码审查应匹配到code_review类型"
            loaded_paths = {s.path for s in result.loaded_specs}
            has_reviewer = any("reviewer" in p for p in loaded_paths)
            assert has_reviewer, "匹配到code_review时应加载reviewer.md"


class TestRoutingCoverage:
    """2.2 路由覆盖完整性测试。

    验证commands/*.md中的每个命令集在TASK_ROUTING中都有对应条目。
    验证已有路由中的文件路径都实际存在。
    """

    def test_all_commands_have_routing(self):
        from lib.spec_loader import TASK_ROUTING
        root = resolve_real_root()
        commands_dir = root / ".agents" / "commands"
        if not commands_dir.exists():
            pytest.skip("commands目录不存在")
        all_routed = set()
        for config in TASK_ROUTING.values():
            for spec in config["l2_specs"]:
                if spec.startswith("commands/"):
                    all_routed.add(spec)
        command_files = set()
        for cmd_file in commands_dir.glob("*.md"):
            if cmd_file.name == "README.md":
                continue
            rel = f"commands/{cmd_file.name}"
            command_files.add(rel)
        unrouted = command_files - all_routed
        assert not unrouted, (
            f"以下commands文件未在TASK_ROUTING中注册路由: {unrouted}"
        )

    def test_routed_files_exist_in_real_project(self):
        from lib.spec_loader import TASK_ROUTING
        root = resolve_real_root()
        missing = []
        for config in TASK_ROUTING.values():
            for spec in config["l2_specs"]:
                full = root / ".agents" / spec
                if not full.exists():
                    missing.append(spec)
        assert not missing, f"TASK_ROUTING中引用了不存在的文件: {missing}"

    def test_first_principles_has_routing(self):
        from lib.spec_loader import TASK_ROUTING
        has_first_principles = any(
            "first-principles" in str(spec)
            for config in TASK_ROUTING.values()
            for spec in config.get("l2_specs", [])
        )
        assert has_first_principles, (
            "commands/first-principles.md 缺少TASK_ROUTING路由条目"
        )


def resolve_real_root() -> Path:
    return SCRIPTS_DIR.parent.parent
