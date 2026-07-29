"""格式化输出模块——将匹配结果格式化为字符串或字典"""

from .constants import WORKFLOWS, ANTI_PATTERN_WARNINGS
from .models import MatchResult
from .scenarios import get_all_scenarios


def format_match_result(result: MatchResult, index: int = 0) -> str:
    lines = []
    prefix = f"[Top{index+1}] " if index > 0 else ""
    lines.append(f"{prefix}🎯 场景：{result.scenario}")
    lines.append(f"   置信度：{'█' * (result.confidence // 10)}{'░' * (10 - result.confidence // 10)} {result.confidence}%")

    if result.concepts:
        chain = " → ".join(result.concepts)
        lines.append(f"   概念组合：{chain}")
    else:
        lines.append(f"   概念组合：（无）")

    if result.workflow:
        wf = WORKFLOWS[result.workflow]
        lines.append(f"   参考流程：{result.workflow} {wf['name']} [{wf['chain']}]")

    if result.notes:
        lines.append(f"   💡 提示：{result.notes}")

    if result.quality_gates:
        lines.append(f"   🚧 质量门：")
        for g in result.quality_gates:
            lines.append(f"      • {g}")

    if result.anti_patterns:
        for ap_id in result.anti_patterns:
            warnings = ANTI_PATTERN_WARNINGS.get(ap_id, [f"⚠️ {ap_id}反模式预警"])
            for w in warnings:
                lines.append(f"   {w}")

    return "\n" + "\n".join(lines)


def format_scenario_list() -> str:
    scenarios = get_all_scenarios()
    lines = []
    lines.append("支持的场景列表：")
    lines.append("-" * 70)
    for keyword, wf, chain in scenarios:
        wf_display = wf if wf is not None else "无"
        lines.append(f"  {keyword:<30} → {chain:<15} ({wf_display})")
    lines.append("-" * 70)
    lines.append(f"共 {len(scenarios)} 种典型场景")
    return "\n".join(lines)


def format_match_result_dict(result: MatchResult) -> dict:
    return {
        "scenario": result.scenario,
        "confidence": result.confidence,
        "concepts": result.concepts,
        "workflow": result.workflow,
        "notes": result.notes,
        "quality_gates": result.quality_gates,
        "anti_patterns": result.anti_patterns,
    }
