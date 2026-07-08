"""check-concurrent-safety.py 单元测试 - 八维检查法验证。"""

import sys
import tempfile
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.check_concurrent_safety import scan_python_file


def _write_py(content: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8")
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


def _scan(code: str) -> list:
    f = _write_py(code)
    try:
        report = scan_python_file(f, f.parent)
        return report.issues
    finally:
        f.unlink()


def _codes(issues) -> set[str]:
    return {i.code for i in issues}


def _dims(issues) -> set[str]:
    return {i.dimension for i in issues}


# ============================================================
# 维度1: TIMEOUT 超时检查
# ============================================================

class TestTimeoutDimension:
    def test_lock_acquire_no_timeout_detected(self):
        code = """
import threading

class TaskManager:
    def __init__(self):
        self._lock = threading.Lock()

    def process(self):
        self._lock.acquire()
        try:
            pass
        finally:
            self._lock.release()
"""
        issues = _scan(code)
        codes = _codes(issues)
        assert "CC-TIMEOUT" in codes
        assert any("timeout" in i.message for i in issues)

    def test_lock_acquire_with_timeout_ok(self):
        code = """
import threading

class TaskManager:
    def __init__(self):
        self._lock = threading.Lock()

    def process(self):
        acquired = self._lock.acquire(timeout=5.0)
        if acquired:
            try:
                pass
            finally:
                self._lock.release()
"""
        issues = _scan(code)
        timeout_issues = [i for i in issues if i.code == "CC-TIMEOUT"]
        assert len(timeout_issues) == 0

    def test_lock_acquire_blocking_false_ok(self):
        code = """
import threading

class TaskManager:
    def __init__(self):
        self._lock = threading.Lock()

    def try_process(self):
        if self._lock.acquire(blocking=False):
            try:
                pass
            finally:
                self._lock.release()
"""
        issues = _scan(code)
        timeout_issues = [i for i in issues if i.code == "CC-TIMEOUT"]
        assert len(timeout_issues) == 0

    def test_event_wait_no_timeout_detected(self):
        code = """
import threading

class Worker:
    def __init__(self):
        self._event = threading.Event()

    def run(self):
        self._event.wait()
"""
        issues = _scan(code)
        codes = _codes(issues)
        assert "CC-TIMEOUT" in codes

    def test_event_wait_with_timeout_ok(self):
        code = """
import threading

class Worker:
    def __init__(self):
        self._event = threading.Event()

    def run(self):
        self._event.wait(timeout=10)
"""
        issues = _scan(code)
        timeout_issues = [i for i in issues if i.code == "CC-TIMEOUT" and "wait" in i.message]
        assert len(timeout_issues) == 0

    def test_while_true_no_exit_detected(self):
        code = """
class TaskScheduler:
    def run_loop(self):
        while True:
            self.process_one()
"""
        issues = _scan(code)
        dims = _dims(issues)
        assert "TIMEOUT" in dims
        assert any("while True" in i.message for i in issues)

    def test_while_true_with_break_ok(self):
        code = """
class TaskScheduler:
    def run_loop(self):
        while True:
            item = self.queue.get()
            if item is None:
                break
            self.process(item)
"""
        issues = _scan(code)
        infinite_loop_issues = [i for i in issues if "while True" in i.message]
        assert len(infinite_loop_issues) == 0

    def test_str_join_not_flagged(self):
        code = """
class Resolver:
    def combine(self, items):
        return ", ".join(items)
"""
        issues = _scan(code)
        join_issues = [i for i in issues if i.code == "CC-TIMEOUT" and "join" in i.message]
        assert len(join_issues) == 0

    def test_thread_join_no_timeout_detected(self):
        code = """
import threading

class Pool:
    def shutdown(self):
        t = threading.Thread(target=self.worker)
        t.start()
        t.join()
"""
        issues = _scan(code)
        assert any("join()" in i.message and "timeout" in i.message for i in issues)

    def test_asyncio_wait_for_missing_timeout(self):
        code = """
import asyncio

async def run_task():
    await asyncio.wait_for(self.do_work())
"""
        issues = _scan(code)
        assert any("wait_for" in i.message for i in issues)

    def test_lock_name_variations_detected(self):
        code = """
import threading

class Manager:
    def __init__(self):
        self.rwlock = threading.Lock()
        self.mutex = threading.Lock()
        self._sem = threading.Semaphore(1)

    def op(self):
        self.rwlock.acquire()
        self.mutex.acquire()
"""
        issues = _scan(code)
        lock_issues = [i for i in issues if i.code == "CC-TIMEOUT" and "锁操作" in i.message]
        assert len(lock_issues) >= 2


# ============================================================
# 维度2: IDEMPOTENT 幂等检查
# ============================================================

class TestIdempotentDimension:
    def test_append_without_guard_detected(self):
        code = """
class ConflictResolver:
    def __init__(self):
        self.rejected_by = []

    def reject(self, agent_id):
        self.rejected_by.append(agent_id)
"""
        issues = _scan(code)
        dims = _dims(issues)
        assert "IDEMPOTENT" in dims
        assert any("去重" in i.message for i in issues)

    def test_append_with_not_in_guard_ok(self):
        code = """
class ConflictResolver:
    def __init__(self):
        self.rejected_by = []

    def reject(self, agent_id):
        if agent_id not in self.rejected_by:
            self.rejected_by.append(agent_id)
"""
        issues = _scan(code)
        idem_issues = [i for i in issues if i.dimension == "IDEMPOTENT"]
        assert len(idem_issues) == 0

    def test_set_add_not_flagged(self):
        code = """
class ConflictResolver:
    def __init__(self):
        self.seen = set()

    def process(self, aid):
        self.seen.add(aid)
"""
        issues = _scan(code)
        idem_issues = [i for i in issues if i.dimension == "IDEMPOTENT"]
        assert len(idem_issues) == 0


# ============================================================
# 维度3: BOUNDARY 边界检查
# ============================================================

class TestBoundaryDimension:
    def test_list_in_in_loop_detected(self):
        code = """
class TaskScheduler:
    def __init__(self):
        self.pending_list = []

    def dispatch(self):
        for item in self.work_items:
            if item in self.pending_list:
                continue
            self.assign(item)
"""
        issues = _scan(code)
        dims = _dims(issues)
        assert "BOUNDARY" in dims
        assert any("O(n)" in i.message for i in issues)

    def test_set_in_lookup_ok(self):
        code = """
class TaskScheduler:
    def __init__(self):
        self._pending_set = set()

    def dispatch(self):
        for item in self.work_items:
            if item in self._pending_set:
                continue
            self.assign(item)
"""
        issues = _scan(code)
        boundary_issues = [i for i in issues if i.dimension == "BOUNDARY" and "线性查找" in i.message]
        assert len(boundary_issues) == 0


# ============================================================
# 维度4: DEFENSIVE 防御性编程
# ============================================================

class TestDefensiveDimension:
    def test_mutable_default_list_detected(self):
        code = """
class Resolver:
    def process(self, items=[]):
        for item in items:
            pass
"""
        issues = _scan(code)
        dims = _dims(issues)
        assert "DEFENSIVE" in dims
        assert any("可变默认参数" in i.message for i in issues)

    def test_mutable_default_dict_detected(self):
        code = """
class Resolver:
    def process(self, config={}):
        pass
"""
        issues = _scan(code)
        assert any("可变默认参数" in i.message and "dict" in i.message for i in issues)

    def test_none_default_ok(self):
        code = """
class Resolver:
    def process(self, items=None):
        if items is None:
            items = []
        for item in items:
            pass
"""
        issues = _scan(code)
        mutable_default_issues = [i for i in issues if "可变默认参数" in i.message]
        assert len(mutable_default_issues) == 0

    def test_return_internal_list_detected(self):
        code = """
class ConflictResolver:
    def __init__(self):
        self._agents_list = []

    def get_agents(self):
        return self._agents_list
"""
        issues = _scan(code)
        assert any("直接返回self" in i.message and "copy" in i.message for i in issues)

    def test_return_copy_ok(self):
        code = """
class ConflictResolver:
    def __init__(self):
        self._agents_list = []

    def get_agents(self):
        return list(self._agents_list)
"""
        issues = _scan(code)
        return_internal = [i for i in issues if "直接返回self" in i.message]
        assert len(return_internal) == 0

    def test_assign_mutable_param_without_copy_detected(self):
        code = """
class Resolver:
    def __init__(self, agents: list):
        self.agents_list = agents
"""
        issues = _scan(code)
        assert any("直接引用外部可变对象" in i.message for i in issues)

    def test_assign_mutable_param_with_copy_ok(self):
        code = """
class Resolver:
    def __init__(self, agents: list):
        self.agents_list = list(agents)
"""
        issues = _scan(code)
        assign_issues = [i for i in issues if "直接引用外部可变对象" in i.message]
        assert len(assign_issues) == 0


# ============================================================
# 维度5: CONFIG 可配置性检查
# ============================================================

class TestConfigDimension:
    def test_hardcoded_sleep_in_resolver_detected(self):
        code = """
class TaskResolver:
    def retry(self):
        import time
        time.sleep(5)
"""
        issues = _scan(code)
        dims = _dims(issues)
        assert "CONFIG" in dims
        assert any("硬编码" in i.message for i in issues)

    def test_constant_timeout_ok(self):
        code = """
LOCK_TIMEOUT = 5.0

class TaskResolver:
    def acquire(self, lock):
        lock.acquire(timeout=LOCK_TIMEOUT)
"""
        issues = _scan(code)
        config_issues = [i for i in issues if i.dimension == "CONFIG"]
        assert len(config_issues) == 0


# ============================================================
# 维度6: I18N 国际化检查
# ============================================================

class TestI18NDimension:
    def test_chinese_comparison_detected(self):
        code = """
class Resolver:
    def get_status(self, status_text):
        if status_text == "已完成":
            return "done"
        elif status_text.startswith("处理中"):
            return "processing"
"""
        issues = _scan(code)
        dims = _dims(issues)
        assert "I18N" in dims
        assert any("中文" in i.message for i in issues)

    def test_chinese_in_logging_ok(self):
        code = """
import logging

class Resolver:
    def process(self):
        self.logger.info("开始处理任务")
        logging.warning("检测到冲突")
"""
        issues = _scan(code)
        i18n_issues = [i for i in issues if i.dimension == "I18N"]
        assert len(i18n_issues) == 0

    def test_enum_constant_ok(self):
        code = """
class Status:
    DONE = "DONE"
    PROCESSING = "PROCESSING"

class Resolver:
    def get_status(self, status):
        if status == Status.DONE:
            return True
"""
        issues = _scan(code)
        i18n_issues = [i for i in issues if i.dimension == "I18N"]
        assert len(i18n_issues) == 0


# ============================================================
# 集成测试：已修复代码应得满分
# ============================================================

class TestCleanCodePasses:
    def test_fixed_conflict_resolver_passes(self):
        code = """
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

class ConflictType(Enum):
    RESPONSIBILITY = "responsibility"
    TECHNICAL = "technical"
    RESOURCE = "resource"

class ResolutionStatus(Enum):
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    REJECTED = "rejected"

@dataclass
class ConflictReport:
    task_id: str
    conflict_type: ConflictType
    reporter_id: str
    opponent_id: str
    reason: str
    proposal_a: str = ""
    proposal_b: str = ""

@dataclass
class ArbitrationResult:
    status: ResolutionStatus
    winner: Optional[str] = None
    reason: str = ""
    ttl: float = 0.0

class ConflictResolver:
    LOCK_TIMEOUT = 5.0
    MAX_RETRY = 3

    def __init__(self, agents: dict, spec_rules: dict,
                 module_ownership_map: Optional[dict] = None):
        self.agents = dict(agents)
        self.spec_rules = dict(spec_rules)
        self.module_ownership_map = dict(module_ownership_map or {})
        self._lock = threading.Lock()
        self._cache: dict[str, Any] = {}
        self._from_str_cache: dict[str, ConflictType] = {}
        self.rejected_by: set[str] = set()

    def resolve(self, report: ConflictReport) -> ArbitrationResult:
        acquired = self._lock.acquire(timeout=self.LOCK_TIMEOUT)
        if not acquired:
            return ArbitrationResult(status=ResolutionStatus.ESCALATED,
                                     reason="锁获取超时")
        try:
            if report.conflict_type == ConflictType.RESPONSIBILITY:
                return self._resolve_responsibility(report)
            elif report.conflict_type == ConflictType.TECHNICAL:
                return self._resolve_technical(report)
            elif report.conflict_type == ConflictType.RESOURCE:
                return self._resolve_resource(report)
            return ArbitrationResult(status=ResolutionStatus.ESCALATED,
                                     reason="未知冲突类型")
        finally:
            self._lock.release()

    def _resolve_responsibility(self, report):
        owner = self.module_ownership_map.get(report.task_id)
        if owner and owner == report.reporter_id:
            return ArbitrationResult(status=ResolutionStatus.RESOLVED,
                                     winner=report.reporter_id,
                                     reason="模块所有者判定")
        return ArbitrationResult(status=ResolutionStatus.ESCALATED,
                                 reason="需架构师仲裁")

    def _resolve_technical(self, report):
        return ArbitrationResult(status=ResolutionStatus.ESCALATED,
                                 reason="技术分歧需架构师决策")

    def _resolve_resource(self, report):
        return ArbitrationResult(status=ResolutionStatus.ESCALATED,
                                 reason="资源竞争需上级协调")

    def get_cache_snapshot(self) -> dict:
        return dict(self._cache)
"""
        issues = _scan(code)
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0, f"干净代码不应有错误: {[i.message for i in errors]}"

    def test_test_functions_skipped(self):
        code = """
def test_resolver():
    items = []
    items.append(1)
    items.append(2)
    while True:
        pass
"""
        issues = _scan(code)
        assert len(issues) == 0


# ============================================================
# CLI 功能测试
# ============================================================

class TestCLI:
    def test_help_runs(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "check-concurrent-safety.py"), "--help"],
            capture_output=True, text=True, cwd=str(SCRIPTS_DIR),
        )
        assert result.returncode == 0
        assert "八维检查法" in result.stdout

    def test_json_output(self):
        code = """
import threading
class M:
    def __init__(self):
        self.lock = threading.Lock()
    def p(self):
        self.lock.acquire()
"""
        f = _write_py(code)
        try:
            import subprocess, json
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "check-concurrent-safety.py"),
                 "-f", str(f), "--json"],
                capture_output=True, text=True, cwd=str(SCRIPTS_DIR),
            )
            data = json.loads(result.stdout)
            assert "files" in data
            assert len(data["files"]) == 1
            issues = data["files"][0]["issues"]
            assert any(i["code"] == "CC-TIMEOUT" for i in issues)
        finally:
            f.unlink()

    def test_dimension_filter(self):
        code = """
import threading
class M:
    def __init__(self):
        self.lock = threading.Lock()
    def p(self, items=[]):
        self.lock.acquire()
"""
        f = _write_py(code)
        try:
            import subprocess, json
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "check-concurrent-safety.py"),
                 "-f", str(f), "-d", "TIMEOUT", "--json"],
                capture_output=True, text=True, cwd=str(SCRIPTS_DIR),
            )
            data = json.loads(result.stdout)
            issues = data["files"][0]["issues"]
            for i in issues:
                assert i["dimension"] in ("TIMEOUT", "PARSE"), \
                    f"维度过滤应只返回TIMEOUT，收到 {i['dimension']}"
        finally:
            f.unlink()


# ============================================================
# 维度7: I18N 增强 - in操作符/字典key中文检测
# ============================================================

class TestI18NEnhanced:
    def test_chinese_in_dict_get_detected(self):
        code = """
class StatusChecker:
    def __init__(self):
        self.state_map = {}

    def is_processing(self):
        return self.state_map.get("处理中") is not None
"""
        issues = _scan(code)
        i18n_issues = [i for i in issues if i.dimension == "I18N"]
        assert len(i18n_issues) >= 1, f"应检测到字典get中文字面量, got {[i.message for i in issues]}"

    def test_chinese_subscript_key_detected(self):
        code = """
class Router:
    def __init__(self):
        self.routes = {}

    def dispatch(self, action):
        return self.routes["删除"]
"""
        issues = _scan(code)
        i18n_issues = [i for i in issues if i.dimension == "I18N"]
        assert len(i18n_issues) >= 1, f"应检测到字典索引中文字面量"

    def test_chinese_in_logging_ok(self):
        code = """
import logging
logger = logging.getLogger(__name__)

class M:
    def p(self):
        logger.info("处理完成")
        print("错误信息")
"""
        issues = _scan(code)
        i18n_issues = [i for i in issues if i.dimension == "I18N"]
        assert len(i18n_issues) == 0, f"日志中中文不应报错: {[i.message for i in i18n_issues]}"

    def test_chinese_enum_constant_ok(self):
        code = """
from enum import Enum

class Status(Enum):
    DONE = "已完成"
    PENDING = "待处理"

class M:
    def check(self, s):
        if s == Status.DONE:
            return True
        return False
"""
        issues = _scan(code)
        i18n_issues = [i for i in issues if i.dimension == "I18N"]
        assert len(i18n_issues) == 0, f"枚举常量中文值不应报错"

    def test_chinese_comparison_still_detected(self):
        code = """
class M:
    def check(self, s):
        if s == "处理中":
            return True
        return False
"""
        issues = _scan(code)
        i18n_issues = [i for i in issues if i.dimension == "I18N"]
        assert len(i18n_issues) >= 1, f"直接中文比较仍应被检测"


# ============================================================
# 维度8: DEADLOCK 死锁顺序检查
# ============================================================

class TestDeadlockDimension:
    def test_inconsistent_lock_order_detected(self):
        code = """
import threading

class TransferService:
    def __init__(self):
        self.lock_a = threading.Lock()
        self.lock_b = threading.Lock()

    def transfer_a_to_b(self):
        self.lock_a.acquire(timeout=5)
        try:
            self.lock_b.acquire(timeout=5)
            try:
                pass
            finally:
                self.lock_b.release()
        finally:
            self.lock_a.release()

    def transfer_b_to_a(self):
        self.lock_b.acquire(timeout=5)
        try:
            self.lock_a.acquire(timeout=5)
            try:
                pass
            finally:
                self.lock_a.release()
        finally:
            self.lock_b.release()
"""
        issues = _scan(code)
        deadlock_issues = [i for i in issues if i.dimension == "DEADLOCK"]
        assert len(deadlock_issues) >= 1, f"应检测到锁顺序不一致死锁风险, got {[i.dimension for i in issues]}"

    def test_consistent_lock_order_ok(self):
        code = """
import threading

class SafeService:
    def __init__(self):
        self.lock_a = threading.Lock()
        self.lock_b = threading.Lock()

    def op1(self):
        self.lock_a.acquire(timeout=5)
        try:
            self.lock_b.acquire(timeout=5)
            try:
                pass
            finally:
                self.lock_b.release()
        finally:
            self.lock_a.release()

    def op2(self):
        self.lock_a.acquire(timeout=5)
        try:
            self.lock_b.acquire(timeout=5)
            try:
                pass
            finally:
                self.lock_b.release()
        finally:
            self.lock_a.release()
"""
        issues = _scan(code)
        deadlock_issues = [i for i in issues if i.dimension == "DEADLOCK"]
        assert len(deadlock_issues) == 0, f"一致的锁顺序不应报错: {[i.message for i in deadlock_issues]}"

    def test_with_statement_lock_order_detected(self):
        code = """
import threading

class M:
    def __init__(self):
        self.lock_a = threading.Lock()
        self.lock_b = threading.Lock()

    def op1(self):
        with self.lock_a:
            with self.lock_b:
                pass

    def op2(self):
        with self.lock_b:
            with self.lock_a:
                pass
"""
        issues = _scan(code)
        deadlock_issues = [i for i in issues if i.dimension == "DEADLOCK"]
        assert len(deadlock_issues) >= 1, f"with语句中锁顺序不一致应被检测"


# ============================================================
# 维度8扩展: LEAK 线程池/资源泄漏检查
# ============================================================

class TestLeakDimension:
    def test_threadpool_no_shutdown_detected(self):
        code = """
from concurrent.futures import ThreadPoolExecutor

class M:
    def process(self, tasks):
        pool = ThreadPoolExecutor(max_workers=4)
        futures = [pool.submit(t) for t in tasks]
        results = [f.result() for f in futures]
        return results
"""
        issues = _scan(code)
        leak_issues = [i for i in issues if i.dimension == "LEAK"]
        assert len(leak_issues) >= 1, f"应检测到线程池未shutdown, got {[i.dimension for i in issues]}"

    def test_threadpool_with_context_manager_ok(self):
        code = """
from concurrent.futures import ThreadPoolExecutor

class M:
    def process(self, tasks):
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(t) for t in tasks]
            results = [f.result() for f in futures]
            return results
"""
        issues = _scan(code)
        leak_issues = [i for i in issues if i.dimension == "LEAK"]
        assert len(leak_issues) == 0, f"with语句管理线程池不应报错: {[i.message for i in leak_issues]}"

    def test_threadpool_with_shutdown_ok(self):
        code = """
from concurrent.futures import ThreadPoolExecutor

class M:
    def process(self, tasks):
        pool = ThreadPoolExecutor(max_workers=4)
        try:
            futures = [pool.submit(t) for t in tasks]
            return [f.result() for f in futures]
        finally:
            pool.shutdown(wait=True)
"""
        issues = _scan(code)
        leak_issues = [i for i in issues if i.dimension == "LEAK"]
        assert len(leak_issues) == 0, f"显式shutdown的线程池不应报错: {[i.message for i in leak_issues]}"


# ============================================================
# 回归测试：原有六维检查仍正常工作
# ============================================================

class TestRegression:
    def test_all_eight_dimensions_in_constants(self):
        from lib.check_concurrent_safety.constants import DIMENSIONS
        expected = {"TIMEOUT", "IDEMPOTENT", "BOUNDARY", "DEFENSIVE",
                    "CONFIG", "I18N", "DEADLOCK", "LEAK"}
        assert set(DIMENSIONS.keys()) == expected

    def test_original_timeout_still_works(self):
        code = """
import threading
class M:
    def __init__(self):
        self.lock = threading.Lock()
    def p(self):
        self.lock.acquire()
"""
        issues = _scan(code)
        assert "CC-TIMEOUT" in _codes(issues)

    def test_original_idempotent_still_works(self):
        code = """
class Resolver:
    def __init__(self):
        self.pending_list = []
    def add(self, item):
        self.pending_list.append(item)
"""
        issues = _scan(code)
        assert "CC-IDEMPOTENT" in _codes(issues)

    def test_original_defensive_still_works(self):
        code = """
class M:
    def p(self, items=[]):
        pass
"""
        issues = _scan(code)
        assert "CC-DEFENSIVE" in _codes(issues)
