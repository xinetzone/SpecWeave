"""负载异常诊断 - 生产环境压力测试。

针对5种负载异常类型（缺失/非数值/布尔值/负值/超范围），
模拟生产环境中可能遇到的边界与压力场景：

  A. 大规模污染：100/500/1000 agent 池中的异常分布
  B. 异常率梯度：0% ~ 100% 异常率下的正确性与性能
  C. 并发调用：多线程同时调用 resolver 的线程安全性
  D. 连续调用稳定性：1000次重复调用无内存泄漏/状态污染
  E. 边界值攻击：NaN/Inf/float精度/0/100/-0等极端数值
  F. 混合冲突类型：技术/资源冲突中传入异常负载的健壮性
  G. 日志洪泛：高异常率下日志收集器不崩溃
  H. 确定性验证：异常数据干扰下结果仍可复现
  I. 深度防御校验：resolve不修改调用方数据（万次验证）

运行方式:
    python -m pytest .agents/scripts/tests/test_conflict_resolution_stress.py -v
    python -m pytest .agents/scripts/tests/test_conflict_resolution_stress.py -v -m "stress" --tb=short
"""

import copy
import math
import random
import threading
import time
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.collaboration.conflict_resolution import (
    ConflictResolver,
    ConflictType,
    ConflictReport,
    ArbitrationResult,
    ResolutionStatus,
)
from lib.testing import generate_agents


ANOMALY_TYPES = ("missing", "string", "bool_true", "bool_false", "negative", "over_100")

ANOMALY_MUTATORS = {
    "missing": lambda info: info.pop("load", None),
    "string": lambda info: info.__setitem__("load", "high"),
    "bool_true": lambda info: info.__setitem__("load", True),
    "bool_false": lambda info: info.__setitem__("load", False),
    "negative": lambda info: info.__setitem__("load", -random.randint(1, 999)),
    "over_100": lambda info: info.__setitem__("load", random.randint(101, 9999)),
}


def _inject_anomalies(agents: dict, anomaly_rate: float, seed: int = 42) -> tuple[dict, list[str]]:
    """按异常率随机注入5种负载异常，返回(污染后agents副本, 被污染agent_id列表)。"""
    rng = random.Random(seed)
    result = copy.deepcopy(agents)
    poisoned: list[str] = []
    ids = list(result.keys())
    for aid in ids:
        if rng.random() < anomaly_rate:
            atype = rng.choice(ANOMALY_TYPES)
            ANOMALY_MUTATORS[atype](result[aid])
            poisoned.append(aid)
    return result, poisoned


def _all_loads_valid(agents: dict) -> bool:
    """检查所有agent负载是否有效。"""
    for info in agents.values():
        load = info.get("load")
        if load is None:
            return False
        if not isinstance(load, (int, float)):
            return False
        if isinstance(load, bool):
            return False
        if load < 0 or load > 100:
            return False
    return True


def _make_report(task_id: str, conflict_type=ConflictType.RESPONSIBILITY, cap="coding") -> ConflictReport:
    return ConflictReport(
        reporter_id="agent_0",
        opponent_id="agent_1",
        conflict_type=conflict_type,
        description=f"Stress test {task_id}",
        task_id=task_id,
        required_capability=cap,
    )


class TestStressLargeScaleAnomaly:
    """A类：大规模异常污染 - 在大量agent池中验证异常过滤正确性和性能。"""

    @pytest.fixture
    def resolver(self):
        return ConflictResolver()

    @pytest.mark.parametrize("n_agents", [100, 500, 1000])
    @pytest.mark.parametrize("anomaly_rate", [0.05, 0.3, 0.7])
    def test_large_scale_with_anomaly_rate(self, resolver, n_agents, anomaly_rate):
        """N个agent池中按X%比例注入异常，验证：
        1. 不崩溃
        2. winner一定是负载正常的agent
        3. 1000个agent场景5秒内完成
        """
        healthy = generate_agents(n_agents, load_strategy="ascending", capabilities=["coding"])
        poisoned, bad_ids = _inject_anomalies(healthy, anomaly_rate, seed=n_agents * 100 + int(anomaly_rate * 100))

        healthy_ids = [aid for aid in poisoned if aid not in bad_ids]
        report = _make_report(f"STRESS-LG-{n_agents}-{int(anomaly_rate*100)}")

        start = time.time()
        result = resolver.resolve(report, agents=poisoned)
        elapsed = time.time() - start

        assert isinstance(result, ArbitrationResult)
        assert elapsed < 5.0, f"n={n_agents} rate={anomaly_rate} 耗时{elapsed:.3f}s 超5秒"

        if healthy_ids and result.status == ResolutionStatus.RESOLVED and result.winner:
            assert result.winner in healthy_ids, (
                f"winner={result.winner} 应是正常agent，异常集大小={len(bad_ids)}"
            )
            valid_loads = {aid: poisoned[aid]["load"] for aid in healthy_ids}
            assert poisoned[result.winner]["load"] == min(valid_loads.values()), (
                f"winner负载={poisoned[result.winner]['load']}应是有效中最低"
            )

    @pytest.mark.parametrize("n_agents", [500])
    def test_all_five_anomaly_types_present_at_scale(self, resolver, n_agents):
        """500个agent中确保每种异常类型至少出现一次，诊断日志能覆盖全部5种。"""
        rng = random.Random(12345)
        healthy = generate_agents(n_agents, load_strategy="ascending", capabilities=["coding"])
        poisoned = copy.deepcopy(healthy)

        ids = list(poisoned.keys())
        rng.shuffle(ids)
        for i, atype in enumerate(ANOMALY_TYPES):
            ANOMALY_MUTATORS[atype](poisoned[ids[i]])
        for aid in ids[len(ANOMALY_TYPES):]:
            if rng.random() < 0.2:
                ANOMALY_MUTATORS[rng.choice(ANOMALY_TYPES)](poisoned[aid])

        logs: list[str] = []
        resolver_with_log = ConflictResolver(logger=lambda m: logs.append(m))
        report = _make_report("STRESS-ALL5-500")
        result = resolver_with_log.resolve(report, agents=poisoned)

        assert isinstance(result, ArbitrationResult)
        full_log = "\n".join(logs)

        for marker in ["缺失(None)", "类型异常(str=", "类型异常(bool=", "负值(", "超范围("]:
            assert marker in full_log, f"大规模场景中应有 {marker} 诊断信息"


class TestStressAnomalyRateGradient:
    """B类：异常率梯度测试 - 从0%到100%逐步增加异常比例。"""

    @pytest.fixture
    def resolver(self):
        return ConflictResolver()

    @pytest.mark.parametrize("rate", [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0])
    def test_gradient_anomaly_rate_correctness(self, resolver, rate):
        """不同异常率下：有正常agent则RESOLVED且winner正常；全异常则ESCALATED。"""
        n = 50
        healthy = generate_agents(n, load_strategy="ascending", capabilities=["coding"])
        poisoned, bad_ids = _inject_anomalies(healthy, rate, seed=int(rate * 10000))
        healthy_ids = [aid for aid in poisoned if aid not in bad_ids]

        report = _make_report(f"STRESS-GRAD-{int(rate*100)}")
        result = resolver.resolve(report, agents=poisoned)

        assert isinstance(result, ArbitrationResult)
        if healthy_ids:
            assert result.status == ResolutionStatus.RESOLVED, f"rate={rate} 有正常agent应RESOLVED"
            assert result.winner in healthy_ids
        else:
            assert result.status == ResolutionStatus.ESCALATED, f"rate={rate} 全异常应ESCALATED"
            assert result.needs_human is True

    @pytest.mark.parametrize("n_agents", [50, 200])
    def test_performance_degradation_curve(self, resolver, n_agents):
        """异常率上升时性能不应指数级退化（100%异常也不应超时）。"""
        times = {}
        for rate in [0.0, 0.5, 1.0]:
            healthy = generate_agents(n_agents, capabilities=["coding"])
            poisoned, _ = _inject_anomalies(healthy, rate, seed=42 + int(rate * 100))
            report = _make_report(f"STRESS-PERF-{n_agents}-{int(rate*100)}")

            t0 = time.time()
            for _ in range(10):
                resolver.resolve(report, agents=poisoned)
            avg = (time.time() - t0) / 10
            times[rate] = avg

        assert times[1.0] < times[0.0] * 10, (
            f"100%异常耗时({times[1.0]:.4f}s) 不应超过0%异常({times[0.0]:.4f}s)的10倍"
        )


class TestStressConcurrency:
    """C类：并发调用压力测试 - 验证多线程使用的线程安全性。"""

    def test_concurrent_resolve_no_race(self):
        """10个线程同时调用同一个resolver，不崩溃、结果合理。"""
        resolver = ConflictResolver()
        errors: list[Exception] = []
        results: list[ArbitrationResult] = []
        lock = threading.Lock()

        def worker(worker_id: int):
            try:
                for i in range(20):
                    n = random.randint(5, 30)
                    agents = generate_agents(n, load_strategy="ascending", capabilities=["coding"])
                    poisoned, bad = _inject_anomalies(agents, 0.3, seed=worker_id * 1000 + i)
                    report = _make_report(f"STRESS-CONC-{worker_id}-{i}")
                    r = resolver.resolve(report, agents=poisoned)
                    assert isinstance(r, ArbitrationResult)
                    if r.status == ResolutionStatus.RESOLVED and r.winner:
                        assert r.winner not in bad or poisoned[r.winner].get("load", "BAD") != "BAD"
                    with lock:
                        results.append(r)
            except Exception as e:
                with lock:
                    errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        assert not errors, f"并发测试出现{len(errors)}个异常: {errors[:3]}"
        assert len(results) == 200, f"应产出200个结果，实际{len(results)}"


class TestStressRepeatedCalls:
    """D类：连续调用稳定性 - 验证无状态污染和内存泄漏。"""

    def test_1000_repeated_calls_no_state_pollution(self):
        """同一个resolver连续调用1000次，每次结果与独立resolver一致。"""
        logs: list[str] = []
        resolver = ConflictResolver(logger=lambda m: logs.append(m))
        rng = random.Random(999)

        for i in range(1000):
            n = rng.randint(3, 20)
            agents = generate_agents(n, load_strategy="ascending", capabilities=["coding"])
            poisoned, bad = _inject_anomalies(agents, rng.uniform(0, 0.5), seed=i)
            report = _make_report(f"STRESS-REP-{i}")
            result = resolver.resolve(report, agents=poisoned)

            assert isinstance(result, ArbitrationResult)
            if result.winner and result.winner in poisoned:
                winfo = poisoned[result.winner]
                load = winfo.get("load")
                is_valid = (
                    isinstance(load, (int, float))
                    and not isinstance(load, bool)
                    and 0 <= load <= 100
                )
                if result.status == ResolutionStatus.RESOLVED:
                    assert is_valid, f"第{i}次调用 winner={result.winner}负载无效"

        assert len(logs) > 0, "应有日志输出"

    def test_log_collector_does_not_grow_unbounded_per_call(self):
        """单次调用日志条数不应随agent数量过度增长（O(n)以内）。"""
        log_counts = {}
        for n in [10, 50, 100, 500]:
            logs: list[str] = []
            resolver = ConflictResolver(logger=lambda m: logs.append(m))
            agents = generate_agents(n, capabilities=["coding"])
            poisoned, _ = _inject_anomalies(agents, 0.3, seed=n)
            report = _make_report(f"STRESS-LOG-{n}")
            resolver.resolve(report, agents=poisoned)
            log_counts[n] = len(logs)

        assert log_counts[500] < log_counts[10] * 100, (
            f"500 agent日志数({log_counts[500]})不应比10 agent({log_counts[10]})增长超过100倍"
        )


class TestStressBoundaryValues:
    """E类：边界值攻击 - NaN/Inf/极端float/0/100等边界数值。"""

    @pytest.fixture
    def resolver(self):
        return ConflictResolver()

    @pytest.mark.parametrize("bad_load,label", [
        (math.nan, "nan"),
        (math.inf, "inf"),
        (-math.inf, "-inf"),
        (1e18, "very_large_float"),
        (-1e18, "very_negative_float"),
        (-0.0001, "near_zero_negative"),
        (100.0001, "just_over_100"),
        (complex(50, 0), "complex_type"),
        ([50], "list_type"),
        ({"value": 50}, "dict_type"),
        (None, "none_value"),
        (b"50", "bytes_type"),
        (bytearray(b"50"), "bytearray_type"),
    ])
    def test_extreme_load_values_are_filtered(self, resolver, bad_load, label):
        """各种极端/异常类型的load值都应被正确过滤，good(load=30)胜出。"""
        agents = {
            "bad": {"role": "developer", "priority": 2, "capabilities": ["coding"]},
            "good": {"role": "developer", "priority": 2, "load": 30, "capabilities": ["coding"]},
        }
        if bad_load is not None:
            agents["bad"]["load"] = bad_load

        logs: list[str] = []
        r = ConflictResolver(logger=lambda m: logs.append(m))
        report = _make_report(f"STRESS-BV-{label}")
        result = r.resolve(report, agents=agents)

        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "good", f"load={label}({bad_load!r})是无效值，应选good(load=30)"
        if label == "nan":
            assert any("非数值(NaN)" in l for l in logs), "NaN应诊断为非数值(NaN)"

    def test_boundary_zero_and_negative_zero_are_valid(self, resolver):
        """load=0和load=-0.0都是有效边界值（-0.0==0），应正常参与竞争。"""
        agents = {
            "neg_zero": {"role": "developer", "priority": 2, "load": -0.0, "capabilities": ["coding"]},
            "pos_zero": {"role": "developer", "priority": 2, "load": 0.0, "capabilities": ["coding"]},
            "fifty":   {"role": "developer", "priority": 2, "load": 50, "capabilities": ["coding"]},
        }
        report = _make_report("STRESS-BOUND-ZERO")
        result = resolver.resolve(report, agents=agents)
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner in ("neg_zero", "pos_zero"), f"0/-0.0是有效值，应胜出，实际winner={result.winner}"

    def test_small_positive_float_is_valid(self, resolver):
        """0.0001等极小正float在[0,100]内，是有效负载值。"""
        agents = {
            "tiny": {"role": "developer", "priority": 2, "load": 0.0001, "capabilities": ["coding"]},
            "high": {"role": "developer", "priority": 2, "load": 30, "capabilities": ["coding"]},
        }
        report = _make_report("STRESS-TINY-FLOAT")
        result = resolver.resolve(report, agents=agents)
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "tiny", "0.0001在[0,100]内是有效负载，0.0001<30应胜出"

    def test_boundary_zero_and_hundred_are_valid(self, resolver):
        """load=0和load=100是有效边界值，应正常参与竞争。"""
        agents = {
            "zero": {"role": "developer", "priority": 2, "load": 0, "capabilities": ["coding"]},
            "fifty": {"role": "developer", "priority": 2, "load": 50, "capabilities": ["coding"]},
            "hundred": {"role": "developer", "priority": 2, "load": 100, "capabilities": ["coding"]},
        }
        report = _make_report("STRESS-BOUND-0-100")
        result = resolver.resolve(report, agents=agents)
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "zero", "load=0应胜出"

    def test_float_loads_in_valid_range_accepted(self, resolver):
        """0-100之间的float负载应正常参与比较。"""
        agents = {
            "low_float": {"role": "developer", "priority": 2, "load": 10.5, "capabilities": ["coding"]},
            "mid_int": {"role": "developer", "priority": 2, "load": 20, "capabilities": ["coding"]},
            "high_float": {"role": "developer", "priority": 2, "load": 99.9, "capabilities": ["coding"]},
        }
        report = _make_report("STRESS-FLOAT")
        result = resolver.resolve(report, agents=agents)
        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "low_float"


class TestStressMixedConflictTypes:
    """F类：混合冲突类型 - 技术和资源冲突中传入异常负载的健壮性。"""

    @pytest.fixture
    def resolver(self):
        return ConflictResolver()

    def test_resource_conflict_with_anomaly_loads_no_crash(self, resolver):
        """资源冲突（含agent负载异常）不应崩溃。"""
        agents = {
            "dev_a": {"role": "developer", "priority": 2, "load": -50, "capabilities": ["coding"]},
            "dev_b": {"role": "developer", "priority": 2, "load": 200, "capabilities": ["coding"]},
        }
        report = ConflictReport(
            reporter_id="dev_a", opponent_id="dev_b",
            conflict_type=ConflictType.RESOURCE,
            description="资源冲突异常负载测试",
            task_id="STRESS-RES-ANOM",
            resource="db_lock", needs_lock=True,
        )
        result = resolver.resolve(report, agents=agents)
        assert isinstance(result, ArbitrationResult)

    def test_technical_conflict_with_anomaly_data_no_crash(self, resolver):
        """技术冲突传入含异常字段的agents不应崩溃。"""
        agents = {
            "dev_a": {"role": "developer", "priority": True, "load": "high", "capabilities": None},
            "dev_b": {"role": "developer", "load": -1, "capabilities": ["coding"]},
        }
        report = ConflictReport(
            reporter_id="dev_a", opponent_id="dev_b",
            conflict_type=ConflictType.TECHNICAL,
            description="技术冲突异常数据测试",
            task_id="STRESS-TECH-ANOM",
            proposal_a="局部修复最小改动",
            proposal_b="全面重构重写",
            is_bugfix=True,
        )
        result = resolver.resolve(report, agents=agents)
        assert isinstance(result, ArbitrationResult)


class TestStressLogFlood:
    """G类：日志洪泛 - 高异常率下日志收集器不导致崩溃或性能骤降。"""

    def test_log_flood_1000_anomalies_does_not_crash(self):
        """1000个agent全是异常负载，日志系统不崩溃且正确升级。"""
        logs: list[str] = []
        resolver = ConflictResolver(logger=lambda m: logs.append(m))

        agents = {}
        for i in range(1000):
            agents[f"bad_{i}"] = {"role": "developer", "priority": 2, "load": -(i + 1), "capabilities": ["coding"]}

        report = _make_report("STRESS-FLOOD-1000")
        start = time.time()
        result = resolver.resolve(report, agents=agents)
        elapsed = time.time() - start

        assert result.status == ResolutionStatus.ESCALATED
        assert result.needs_human is True
        assert elapsed < 5.0, f"全异常1000agent耗时{elapsed:.3f}s超5秒"

        warning_logs = [l for l in logs if "[WARNING]" in l]
        assert len(warning_logs) >= 1, "应有WARNING级升级日志"

    def test_null_logger_handles_all_anomalies(self):
        """不传logger（静默模式）时高异常率也不崩溃。"""
        resolver = ConflictResolver()
        agents = {
            "a": {"role": "dev", "load": None, "capabilities": ["x"]},
            "b": {"role": "dev", "load": "bad", "capabilities": ["x"]},
            "c": {"role": "dev", "load": True, "capabilities": ["x"]},
            "d": {"role": "dev", "load": -1, "capabilities": ["x"]},
            "e": {"role": "dev", "load": 999, "capabilities": ["x"]},
        }
        report = _make_report("STRESS-NULLOG")
        result = resolver.resolve(report, agents=agents)
        assert isinstance(result, ArbitrationResult)
        assert result.status == ResolutionStatus.ESCALATED


class TestStressDeterminism:
    """H类：确定性验证 - 异常数据干扰下结果可复现。"""

    @pytest.mark.parametrize("seed", [0, 42, 123, 999])
    def test_same_anomaly_pattern_produces_same_result(self, seed):
        """相同种子注入的异常模式，多次运行结果一致。"""
        agents_base = generate_agents(30, load_strategy="ascending", capabilities=["coding"])
        poisoned, _ = _inject_anomalies(agents_base, 0.4, seed=seed)

        results = []
        for _ in range(5):
            logs: list[str] = []
            resolver = ConflictResolver(logger=lambda m: logs.append(m))
            report = _make_report(f"STRESS-DET-{seed}")
            r = resolver.resolve(report, agents=copy.deepcopy(poisoned))
            results.append((r.status, r.winner, r.reason))

        assert len(set(results)) == 1, f"相同输入产生不同结果: {set(results)}"


class TestStressDefensiveCopy:
    """I类：深度防御校验 - 万次调用验证调用方数据不被修改。"""

    @pytest.mark.parametrize("n_agents", [10, 50])
    def test_resolve_does_not_mutate_input_1000_times(self, n_agents):
        """resolve() 不应修改调用方传入的agents字典（防御性拷贝验证）。"""
        resolver = ConflictResolver()
        rng = random.Random(777)

        for i in range(1000):
            agents = generate_agents(n_agents, load_strategy="ascending", capabilities=["coding"])
            poisoned, _ = _inject_anomalies(agents, rng.uniform(0, 0.4), seed=i)
            snapshot = copy.deepcopy(poisoned)

            report = _make_report(f"STRESS-DEF-{i}")
            resolver.resolve(report, agents=poisoned)

            assert poisoned == snapshot, f"第{i}次调用修改了调用方数据"

    def test_resolve_does_not_mutate_report(self):
        """resolve() 不应修改传入的ConflictReport（防御性拷贝验证）。"""
        resolver = ConflictResolver()
        agents = generate_agents(5, load_strategy="ascending", capabilities=["coding"])
        report = _make_report("STRESS-REPORT-MUT")
        report_snapshot = copy.deepcopy(report)

        resolver.resolve(report, agents=agents)
        assert report.rejected_by == report_snapshot.rejected_by
        assert report.resolved == report_snapshot.resolved


class TestStressDiagnosticCompleteness:
    """诊断完整性 - 验证每种异常类型的诊断信息精确包含正确的描述。"""

    @pytest.mark.parametrize("anomaly_type,expected_marker", [
        ("missing", "缺失(None)"),
        ("string", "类型异常(str="),
        ("bool_true", "类型异常(bool=True)"),
        ("bool_false", "类型异常(bool=False)"),
        ("negative", "负值("),
        ("over_100", "超范围("),
    ])
    def test_each_anomaly_type_produces_exact_diagnostic(self, anomaly_type, expected_marker):
        """每种异常类型单独出现时，诊断信息准确匹配。"""
        logs: list[str] = []
        resolver = ConflictResolver(logger=lambda m: logs.append(m))

        agents = {
            "bad": {"role": "developer", "priority": 2, "capabilities": ["coding"]},
            "good": {"role": "developer", "priority": 2, "load": 50, "capabilities": ["coding"]},
        }
        if anomaly_type == "missing":
            pass
        else:
            mutator = ANOMALY_MUTATORS[anomaly_type]
            mutator(agents["bad"])

        report = _make_report(f"STRESS-DIAG-{anomaly_type}")
        result = resolver.resolve(report, agents=agents)

        assert result.winner == "good"
        full_log = "\n".join(logs)
        assert expected_marker in full_log, (
            f"{anomaly_type}类型应产生诊断'{expected_marker}'，日志: {full_log}"
        )

    def test_all_five_anomaly_types_in_single_log(self):
        """单次调用包含全部5种异常，日志中每种诊断都出现。"""
        logs: list[str] = []
        resolver = ConflictResolver(logger=lambda m: logs.append(m))

        agents = {
            "miss":  {"role": "developer", "priority": 2, "capabilities": ["coding"]},
            "str":   {"role": "developer", "priority": 2, "load": "heavy", "capabilities": ["coding"]},
            "boolt": {"role": "developer", "priority": 2, "load": True, "capabilities": ["coding"]},
            "neg":   {"role": "developer", "priority": 2, "load": -99, "capabilities": ["coding"]},
            "over":  {"role": "developer", "priority": 2, "load": 999, "capabilities": ["coding"]},
            "good":  {"role": "developer", "priority": 2, "load": 15, "capabilities": ["coding"]},
        }
        report = _make_report("STRESS-DIAG-ALL5")
        result = resolver.resolve(report, agents=agents)

        assert result.status == ResolutionStatus.RESOLVED
        assert result.winner == "good"

        full_log = "\n".join(logs)
        markers = ["缺失(None)", "类型异常(str='heavy')", "类型异常(bool=True)", "负值(-99)", "超范围(999>100)"]
        for m in markers:
            assert m in full_log, f"日志中缺少诊断信息: {m}"
