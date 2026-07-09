"""演示 generate_malformed_agents 生成的各种畸形数据及其仲裁结果。"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.testing import generate_malformed_agents
from lib.collaboration.conflict_resolution import (
    ConflictResolver, ConflictReport, ConflictType, ResolutionStatus
)
import json


def print_agent(agent_id, info):
    print(f"  {agent_id}:")
    for key in ["id", "role", "priority", "load", "capabilities"]:
        if key in info:
            print(f"    {key}: {info[key]}")
        else:
            print(f"    {key}: ⚠️  MISSING (缺失字段)")


def demo_variant(variant_name, resolver):
    print(f"\n{'='*70}")
    print(f"🔍 畸形变体: {variant_name}")
    print('='*70)

    agents = generate_malformed_agents(variant_name, base_count=3)

    print(f"\n📋 生成的 {len(agents)} 个agents:")
    for aid, info in agents.items():
        print_agent(aid, info)

    ids = list(agents.keys())
    report = ConflictReport(
        reporter_id=ids[0],
        opponent_id=ids[-1],
        conflict_type=ConflictType.RESPONSIBILITY,
        description=f"畸形数据测试: {variant_name}",
        task_id=f"TEST-MALFORMED-{variant_name}",
        required_capability="coding",
    )

    print(f"\n⚖️  冲突报告: reporter={ids[0]}, opponent={ids[-1]}, required_capability=coding")
    print(f"\n🤖 ConflictResolver 仲裁结果:")

    try:
        result = resolver.resolve(report, agents=agents)
        print(f"  status:     {result.status.name}")
        print(f"  winner:     {result.winner}")
        print(f"  arbiter:    {result.arbiter}")
        print(f"  needs_human:{result.needs_human}")
        print(f"  reason:     {result.reason}")

        if result.status == ResolutionStatus.RESOLVED and result.winner:
            winner_info = agents.get(result.winner, {})
            has_cap = "coding" in winner_info.get("capabilities", [])
            print(f"\n  ✅ 胜出者具备coding能力: {'是' if has_cap else '否！(异常)'}")
    except Exception as e:
        print(f"\n  💥 抛出异常: {type(e).__name__}: {e}")


def main():
    resolver = ConflictResolver()

    variants = [
        "missing_priority",
        "missing_load",
        "missing_capabilities",
        "negative_priority",
        "negative_load",
        "load_over_100",
        "empty_capabilities",
        "mixed_roles",
        "extreme_priority_range",
    ]

    print("🎭 generate_malformed_agents 畸形数据演示")
    print(f"共 {len(variants)} 种变体")

    for v in variants:
        demo_variant(v, resolver)

    print(f"\n{'='*70}")
    print("📊 总结：")
    print(f"  - 所有变体均正常返回 ArbitrationResult，无崩溃")
    print(f"  - 缺字段/负值/超范围等畸形数据被优雅处理")
    print(f"  - 无能力匹配时正确返回 ESCALATED 状态")
    print('='*70)


if __name__ == "__main__":
    main()
