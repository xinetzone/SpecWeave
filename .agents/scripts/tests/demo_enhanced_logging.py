"""演示增强后的详细日志输出效果。"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.testing import generate_malformed_agents
from lib.collaboration.conflict_resolution import (
    ConflictResolver, ConflictReport, ConflictType, ResolutionStatus
)


def collect_logs():
    """创建一个收集日志的resolver。"""
    logs = []

    def log_collector(msg):
        logs.append(msg)
        print(f"  📝 {msg}")

    resolver = ConflictResolver(logger=log_collector)
    return resolver, logs


def demo_logging():
    print("=" * 80)
    print("📋 增强日志演示：畸形数据处理流程完整日志追踪")
    print("=" * 80)

    # 场景1：负负载被过滤
    print("\n🔍 场景1: 负负载agent被过滤（negative_load）")
    print("-" * 60)
    resolver, _ = collect_logs()
    agents = {
        "bad_agent": {"id": "bad_agent", "role": "developer", "priority": 2, "load": -50, "capabilities": ["coding"]},
        "good_agent": {"id": "good_agent", "role": "developer", "priority": 2, "load": 50, "capabilities": ["coding"]},
        "high_load_agent": {"id": "high_load_agent", "role": "developer", "priority": 2, "load": 90, "capabilities": ["coding"]},
    }
    report = ConflictReport(
        reporter_id="bad_agent", opponent_id="high_load_agent",
        conflict_type=ConflictType.RESPONSIBILITY,
        description="负负载过滤日志测试",
        task_id="LOG-TEST-001", required_capability="coding",
    )
    result = resolver.resolve(report, agents=agents)
    print(f"  ✅ 最终结果: status={result.status.value}, winner={result.winner}")

    # 场景2：混合无效负载（缺失+超范围+负值）
    print("\n🔍 场景2: 混合异常负载（缺失+超100+负值+正常值）")
    print("-" * 60)
    resolver, _ = collect_logs()
    agents = {
        "neg": {"id": "neg", "role": "developer", "priority": 2, "load": -5, "capabilities": ["coding"]},
        "over": {"id": "over", "role": "developer", "priority": 2, "load": 150, "capabilities": ["coding"]},
        "miss": {"id": "miss", "role": "developer", "priority": 2, "capabilities": ["coding"]},
        "valid_low": {"id": "valid_low", "role": "developer", "priority": 2, "load": 20, "capabilities": ["coding"]},
        "valid_mid": {"id": "valid_mid", "role": "developer", "priority": 2, "load": 60, "capabilities": ["coding"]},
    }
    report = ConflictReport(
        reporter_id="neg", opponent_id="valid_mid",
        conflict_type=ConflictType.RESPONSIBILITY,
        description="混合异常负载日志测试",
        task_id="LOG-TEST-002", required_capability="coding",
    )
    result = resolver.resolve(report, agents=agents)
    print(f"  ✅ 最终结果: status={result.status.value}, winner={result.winner}")

    # 场景3：全异常负载升级
    print("\n🔍 场景3: 所有候选负载异常，触发升级")
    print("-" * 60)
    resolver, _ = collect_logs()
    agents = {
        "bad1": {"id": "bad1", "role": "developer", "priority": 2, "load": -10, "capabilities": ["coding"]},
        "bad2": {"id": "bad2", "role": "developer", "priority": 2, "load": 200, "capabilities": ["coding"]},
        "bad3": {"id": "bad3", "role": "developer", "priority": 2, "capabilities": ["coding"]},
    }
    report = ConflictReport(
        reporter_id="bad1", opponent_id="bad2",
        conflict_type=ConflictType.RESPONSIBILITY,
        description="全异常负载升级日志测试",
        task_id="LOG-TEST-003", required_capability="coding",
    )
    result = resolver.resolve(report, agents=agents)
    print(f"  ✅ 最终结果: status={result.status.value}, winner={result.winner}, needs_human={result.needs_human}")

    # 场景4：平局负载均衡
    print("\n🔍 场景4: 多agent平局（相同最低负载）")
    print("-" * 60)
    resolver, _ = collect_logs()
    agents = {
        "a1": {"id": "a1", "role": "developer", "priority": 2, "load": 30, "capabilities": ["coding"]},
        "a2": {"id": "a2", "role": "developer", "priority": 2, "load": 30, "capabilities": ["coding"]},
        "a3": {"id": "a3", "role": "developer", "priority": 2, "load": 70, "capabilities": ["coding"]},
    }
    report = ConflictReport(
        reporter_id="a3", opponent_id="a1",
        conflict_type=ConflictType.RESPONSIBILITY,
        description="平局负载均衡日志测试",
        task_id="LOG-TEST-004", required_capability="coding",
    )
    result = resolver.resolve(report, agents=agents)
    print(f"  ✅ 最终结果: status={result.status.value}, winner={result.winner}")

    # 场景5：唯一匹配候选
    print("\n🔍 场景5: 唯一具备所需能力的agent")
    print("-" * 60)
    resolver, _ = collect_logs()
    agents = {
        "dev": {"id": "dev", "role": "developer", "priority": 2, "load": 80, "capabilities": ["coding"]},
        "arch": {"id": "arch", "role": "architect", "priority": 1, "load": 20, "capabilities": ["architecture"]},
        "reviewer": {"id": "reviewer", "role": "reviewer", "priority": 3, "load": 10, "capabilities": ["review"]},
    }
    report = ConflictReport(
        reporter_id="arch", opponent_id="reviewer",
        conflict_type=ConflictType.RESPONSIBILITY,
        description="唯一匹配日志测试",
        task_id="LOG-TEST-005", required_capability="coding",
    )
    result = resolver.resolve(report, agents=agents)
    print(f"  ✅ 最终结果: status={result.status.value}, winner={result.winner}")

    print("\n" + "=" * 80)
    print("📊 日志增强总结：每个决策分支都有详细日志可追踪")
    print("=" * 80)


if __name__ == "__main__":
    demo_logging()
