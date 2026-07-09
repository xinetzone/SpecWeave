"""演示5种负载异常类型的完整诊断日志输出。"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.collaboration.conflict_resolution import (
    ConflictResolver, ConflictReport, ConflictType, ResolutionStatus
)


def demo(name, agents, reporter, opponent, task_id, desc, cap="coding"):
    print(f"\n{'='*70}")
    print(f"场景: {name}")
    print(f"{'='*70}")
    logs = []

    def log_fn(msg):
        logs.append(msg)
        print(f"  | {msg}")

    resolver = ConflictResolver(logger=log_fn)
    report = ConflictReport(
        reporter_id=reporter, opponent_id=opponent,
        conflict_type=ConflictType.RESPONSIBILITY,
        description=desc, task_id=task_id, required_capability=cap,
    )
    result = resolver.resolve(report, agents=agents)
    print(f"  => 结果: status={result.status.value}, winner={result.winner}, needs_human={result.needs_human}")
    return result


if __name__ == "__main__":
    # 场景1: 5种异常 + 1个正常 → 过滤后正常分配
    demo(
        name="5种异常类型 + 1个正常agent → 过滤后正常分配",
        agents={
            "miss_load":   {"role": "developer", "priority": 2, "capabilities": ["coding"]},
            "str_load":    {"role": "developer", "priority": 2, "load": "high", "capabilities": ["coding"]},
            "bool_load":   {"role": "developer", "priority": 2, "load": True, "capabilities": ["coding"]},
            "neg_load":    {"role": "developer", "priority": 2, "load": -50, "capabilities": ["coding"]},
            "over_load":   {"role": "developer", "priority": 2, "load": 150, "capabilities": ["coding"]},
            "valid_agent": {"role": "developer", "priority": 2, "load": 20, "capabilities": ["coding"]},
        },
        reporter="neg_load", opponent="over_load",
        task_id="DIAG-5TYPES", desc="5种负载异常诊断验证",
    )

    # 场景2: 5种异常 无正常 → 全异常升级
    demo(
        name="5种异常类型 无正常agent → 全异常升级人工处理",
        agents={
            "miss_load": {"role": "developer", "priority": 2, "capabilities": ["coding"]},
            "str_load":  {"role": "developer", "priority": 2, "load": "low", "capabilities": ["coding"]},
            "bool_load": {"role": "developer", "priority": 2, "load": False, "capabilities": ["coding"]},
            "neg_load":  {"role": "developer", "priority": 2, "load": -10, "capabilities": ["coding"]},
            "over_load": {"role": "developer", "priority": 2, "load": 200, "capabilities": ["coding"]},
        },
        reporter="miss_load", opponent="over_load",
        task_id="DIAG-5ESCALATE", desc="全异常负载升级诊断",
    )

    print(f"\n{'='*70}")
    print("诊断日志中包含的5种异常类型验证：")
    print(f"{'='*70}")
    print("  1. 缺失(None)        ← miss_load 无load字段")
    print("  2. 类型异常(str=...) ← str_load load为字符串")
    print("  3. 类型异常(bool=..) ← bool_load load为布尔值")
    print("  4. 负值(...)         ← neg_load load为负数")
    print("  5. 超范围(...>100)   ← over_load load超过100")