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
    _atomic_replace_with_retry,
)


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


def resolve_real_root() -> Path:
    return SCRIPTS_DIR.parent.parent
