#!/usr/bin/env python3
"""四维留余框架交互式检查工具。

通过交互式问卷评估当前决策/项目在天地人时四维上的冗余度，
检测伪留余/单维留余/静态留余三种反模式，输出结构化风险报告。

用法:
    python .agents/scripts/check-margin.py              # 交互式问卷
    python .agents/scripts/check-margin.py --json       # JSON格式输出
    python .agents/scripts/check-margin.py --non-interactive --scores "90,80,70,60"  # 非交互式评分
"""


import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import json
import sys
from dataclasses import dataclass, field

from lib.cli import (
    add_common_args,
    print_error,
    print_header,
    print_pass,
    print_summary,
    print_warn,
    setup_safe_output,
)


# ── 问卷题目定义 ──────────────────────────────────────────

@dataclass
class Question:
    """单道评估题目。"""
    id: str
    dimension: str  # tian/di/ren/shi/anti
    text: str
    options: list[tuple[str, int]]  # (选项文本, 分数0-20)


QUESTIONS: list[Question] = [
    # ── 天维·能力冗余（造化）──
    Question("t1", "tian", "你当前投入的关键资源（服务器/产能/精力/算力）用到了总容量的百分之多少？", [
        ("95%以上，几乎打满了", 0),
        ("85%-95%，接近极限", 5),
        ("70%-85%，较高但有余量", 12),
        ("50%-70%，安全区间", 18),
        ("50%以下，非常充裕", 20),
    ]),
    Question("t2", "tian", "你的系统/方案是否设计了熔断、限流、降级、紧急停止等保护机制？", [
        ("完全没有，出问题只能手动处理", 0),
        ("有部分机制但从未测试过", 5),
        ("有基本保护机制，偶尔测试", 12),
        ("完善的保护机制，定期演练", 18),
        ("多层防护+自动故障转移，经过实战检验", 20),
    ]),
    Question("t3", "tian", "你是否保留了至少一个技术/能力备选方案（如多供应商、多技术路线）？", [
        ("完全依赖单一方案，没有备选", 0),
        ("想过但没准备", 5),
        ("有粗略的备选方案但未验证", 12),
        ("有经过验证的备选方案", 18),
        ("多个备选方案随时可切换", 20),
    ]),
    Question("t4", "tian", '你是否及时清除了已知的"死代码"/废弃功能/过期配置？', [
        ("大量废弃内容堆积，不敢删", 0),
        ("知道有但没清理", 5),
        ("定期清理大部分", 12),
        ("及时清理，保持精简", 18),
        ("严格的废弃代码零容忍政策", 20),
    ]),
    Question("t5", "tian", "如果关键组件/核心能力突然失效，你的系统/方案多久能恢复？", [
        ("无法恢复，直接崩溃", 0),
        ("需要几天以上修复", 5),
        ("几小时内能恢复", 12),
        ("分钟级自动恢复", 18),
        ("秒级无感切换", 20),
    ]),
    # ── 地维·合规冗余（朝廷）──
    Question("d1", "di", "你距离政策/法律/监管/制度红线有多远？", [
        ("正在利用灰色地带/打擦边球", 0),
        ("紧贴红线，稍微越界就违规", 5),
        ("有一定缓冲空间", 12),
        ("保持明显安全距离", 18),
        ("远超合规要求，主动加严", 20),
    ]),
    Question("d2", "di", "你是否定期做合规自查/安全审计/风险评估？", [
        ("从未做过", 0),
        ("出问题才查", 5),
        ("偶尔自查，不系统", 12),
        ("定期自查有记录", 18),
        ("系统化持续合规监控", 20),
    ]),
    Question("d3", "di", "面对规则漏洞/监管灰色地带，你的态度是？", [
        ("主动利用漏洞获取最大利益", 0),
        ("别人钻我也钻", 5),
        ("不主动钻但也不刻意避开", 12),
        ("主动避开灰色地带", 18),
        ("即使有漏洞也坚持合规底线", 20),
    ]),
    Question("d4", "di", "如果政策/规则/上级要求突然变化，你有多少缓冲时间来调整？", [
        ("没有缓冲，立即违规", 0),
        ("几天内必须调整", 5),
        ("有几周缓冲期", 12),
        ("有几个月缓冲", 18),
        ("设计本身不受政策变化影响", 20),
    ]),
    # ── 人维·关系冗余（百姓）──
    Question("r1", "ren", "你给合作伙伴/供应商/客户/员工留了合理的利益空间吗？", [
        ("尽可能压缩对方利润/收益", 0),
        ("对方刚好不亏", 5),
        ("有一定利润空间", 12),
        ("让对方有利可图愿意长期合作", 18),
        ("主动让利，建立共赢生态", 20),
    ]),
    Question("r2", "ren", "你是否在某个关键关系上过度依赖单一对象（如一个客户/一个供应商/一个领导）？", [
        ("超过80%依赖单一对象", 0),
        ("60%-80%依赖", 5),
        ("40%-60%依赖", 12),
        ("20%-40%依赖", 18),
        ("没有任何单一点超过20%", 20),
    ]),
    Question("r3", "ren", "面对竞争对手或与你有冲突的人，你的态度是？", [
        ("赶尽杀绝，不留活路", 0),
        ("能打压就打压", 5),
        ("公平竞争，不刻意针对", 12),
        ("留一线，日后好相见", 18),
        ("帮助对手/敌人成长", 20),
    ]),
    Question("r4", "ren", '你在顺境/有能力时是否帮助过他人、建立了"信任储蓄"？', [
        ("从不帮人，独来独往", 0),
        ("只帮对自己有用的人", 5),
        ("偶尔帮人", 12),
        ("经常主动帮助他人", 18),
        ("持续投入建立互惠网络", 20),
    ]),
    Question("r5", "ren", "如果主要合作伙伴/客户/关键人突然离开或翻脸，你有替代方案吗？", [
        ("完全没有，直接崩盘", 0),
        ("损失巨大但能勉强维持", 5),
        ("有替代但需较长过渡期", 12),
        ("有多个备选，过渡平滑", 18),
        ("关系网络足够深，可快速替换", 20),
    ]),
    # ── 时维·选项冗余（子孙）──
    Question("s1", "shi", "你的现金/核心资源储备，在没有任何收入的情况下能支撑多久？", [
        ("不到1个月", 0),
        ("1-3个月", 5),
        ("3-6个月", 12),
        ("6-18个月", 18),
        ("18个月以上", 20),
    ]),
    Question("s2", "shi", "如果当前方向完全失败，你有Plan B或转型路径吗？", [
        ("没有任何退路", 0),
        ("想过但没具体方案", 5),
        ("有模糊的方向", 12),
        ("有具体可行的Plan B", 18),
        ("多条可行的备选路径随时可启动", 20),
    ]),
    Question("s3", "shi", "你是否在持续学习/积累可迁移的核心能力（而非绑定于单一工具/平台/职位）？", [
        ("完全绑定当前工具/平台，没有可迁移能力", 0),
        ("很少学习新东西", 5),
        ("偶尔学习但不系统", 12),
        ("持续学习有明确计划", 18),
        ("学习体系化，能力高度可迁移", 20),
    ]),
    Question("s4", "shi", "你是否因为过去的投入（沉没成本）而无法转向新方向？", [
        ("完全被沉没成本绑架，明知错了也停不下来", 0),
        ("很难转向，投入太大舍不得", 5),
        ("可以转向但心疼", 12),
        ("做决策时不考虑沉没成本", 18),
        ("定期检视沉没成本，果断止损", 20),
    ]),
    Question("s5", "shi", "你现在的决策是否透支了未来的选择权（如健康/信誉/人脉/时间）？", [
        ("严重透支，未来选择越来越少", 0),
        ("有透支但还没到临界点", 5),
        ("基本平衡", 12),
        ("在为未来积累更多选择", 18),
        ("每一个决策都在增加未来的选项", 20),
    ]),
    # ── 反模式检测 ──
    Question("a1", "anti", '你让利/留余/做"好事"的时候，内心是否期待将来获得回报？', [
        ("是的，我明确期望加倍回报", 0),
        ("大多时期望有回报", 5),
        ("有时候会期望", 12),
        ("很少期望回报", 18),
        ("完全不期望回报，做了就忘了", 20),
    ]),
    Question("a2", "anti", "你是否只在某一两个维度留余（比如只对人好），但在其他维度All in？", [
        ("是的，其他维度基本不留", 0),
        ("大部分维度不留", 5),
        ("有一半维度有留余", 12),
        ("大部分维度都有留余", 18),
        ("四维全部有系统的留余设计", 20),
    ]),
    Question("a3", "anti", "你的留余策略/风险控制手段，多久没有根据环境变化调整了？", [
        ("从未调整过，一直一样", 0),
        ("一年以上没调整", 5),
        ("半年到一年", 12),
        ("每季度审视调整", 18),
        ("持续动态调整，实时响应环境", 20),
    ]),
]

DIMENSIONS = {
    "tian": {"name": "天维·能力冗余（造化）", "icon": "☰", "questions": 5},
    "di": {"name": "地维·合规冗余（朝廷）", "icon": "☷", "questions": 4},
    "ren": {"name": "人维·关系冗余（百姓）", "icon": "☵", "questions": 5},
    "shi": {"name": "时维·选项冗余（子孙）", "icon": "☲", "questions": 5},
    "anti": {"name": "反模式检测", "icon": "⚠", "questions": 3},
}

DIMENSION_WEIGHTS = {"tian": 0.25, "di": 0.25, "ren": 0.25, "shi": 0.25}


# ── 评分引擎 ──────────────────────────────────────────────

@dataclass
class DimensionResult:
    """单个维度的评估结果。"""
    key: str
    name: str
    score: float  # 0-100
    max_score: float
    level: str  # danger/warning/moderate/good/excellent
    warnings: list[str] = field(default_factory=list)


@dataclass
class CheckResult:
    """完整评估结果。"""
    dimensions: dict[str, DimensionResult]
    total_score: float
    total_level: str
    anti_patterns: list[str]
    advice: list[str]
    adversity_passed: bool


def _score_to_level(score: float) -> str:
    if score < 30:
        return "danger"
    if score < 50:
        return "warning"
    if score < 70:
        return "moderate"
    if score < 90:
        return "good"
    return "excellent"


def _level_cn(level: str) -> str:
    return {
        "danger": "危险🔴",
        "warning": "警告🟠",
        "moderate": "一般🟡",
        "good": "健康🟢",
        "excellent": "优秀🔵",
    }.get(level, "未知")


def evaluate(answers: dict[str, int]) -> CheckResult:
    """根据答案计算评估结果。"""
    dimensions = {}
    anti_patterns = []
    advice = []

    for dim_key, dim_info in DIMENSIONS.items():
        dim_questions = [q for q in QUESTIONS if q.dimension == dim_key]
        if not dim_questions:
            continue
        total = sum(answers.get(q.id, 0) for q in dim_questions)
        max_total = len(dim_questions) * 20
        score = round(total / max_total * 100, 1)
        level = _score_to_level(score)
        warnings = []

        # 维度特定的警告生成
        if dim_key == "tian" and score < 50:
            warnings.append("天维（能力冗余）偏低：系统缺乏容错能力，一旦关键组件失效可能直接崩溃。建议立即建立熔断/降级机制并保留容量余量。")
        elif dim_key == "di" and score < 50:
            warnings.append("地维（合规冗余）偏低：存在合规风险，一次政策变化或监管检查可能造成致命打击。建议立即进行合规自查并扩大安全距离。")
        elif dim_key == "ren" and score < 50:
            warnings.append("人维（关系冗余）偏低：关系网络脆弱，关键人变动可能导致业务中断。建议分散依赖、建立信任储蓄、对伙伴留足利益空间。")
        elif dim_key == "shi" and score < 50:
            warnings.append("时维（选项冗余）偏低：缺乏退路和储备，一旦方向错误或环境变化无力回天。建议立即建立现金/能力储备并准备Plan B。")

        # 中等分数也给建议
        if 50 <= score < 70 and dim_key in DIMENSION_WEIGHTS:
            warnings.append(f"{dim_info['name']}处于中等水平，仍有提升空间。可参考四维留余框架的5条行动原则优化。")

        dimensions[dim_key] = DimensionResult(
            key=dim_key,
            name=dim_info["name"],
            score=score,
            max_score=100,
            level=level,
            warnings=warnings,
        )

    # 反模式检测
    if answers.get("a1", 20) <= 5:
        anti_patterns.append("🔴 伪留余风险：你让利/留余时期待明确回报。这不是真正的留余而是伪装的投资——一旦预期落空可能反转，比不留余更损伤信任。")
    elif answers.get("a1", 20) <= 12:
        anti_patterns.append('🟡 伪留余倾向：你有时会期待留余产生回报。注意：留余是"消费型保险"而非投资，它的价值是"确保你还在牌桌上"。')
    if answers.get("a2", 20) <= 5:
        anti_patterns.append("🔴 单维留余风险：你只在少数维度留余，其他维度All in。记住四维缺一不可——某一维崩溃时其他维冗余无法替代。")
    elif answers.get("a2", 20) <= 12:
        anti_patterns.append("🟡 单维留余倾向：检查是否存在被忽视的维度。合规出问题时客户关系再好也没用。")
    if answers.get("a3", 20) <= 5:
        anti_patterns.append("🔴 静态留余风险：你的风险策略长期未调整。不确定环境中静态策略必然失效——和平时期的冗余标准在危机时等于裸奔。")
    elif answers.get("a3", 20) <= 12:
        anti_patterns.append("🟡 静态留余倾向：建议每季度审视冗余策略，根据环境不确定性动态调整留余比例。")

    # 综合建议
    core_dims = {k: v for k, v in dimensions.items() if k in DIMENSION_WEIGHTS}
    min_dim = min(core_dims.values(), key=lambda d: d.score)
    if min_dim.score < 50:
        advice.append(f"🚨 最薄弱维度是「{min_dim.name}」（{min_dim.score}分），这是你当前最大的风险敞口。四维中短板决定生死——优先补齐最弱的一维。")

    total_weighted = sum(
        dimensions[k].score * w for k, w in DIMENSION_WEIGHTS.items() if k in dimensions
    )
    total_score = round(total_weighted, 1)
    total_level = _score_to_level(total_score)

    # 逆境测试
    adversity_passed = all(dimensions[k].score >= 30 for k in DIMENSION_WEIGHTS if k in dimensions)
    if not adversity_passed:
        advice.append("⚠️ 逆境测试未通过：存在低于30分的维度，在黑天鹅事件中可能无法存续。建议立即将所有维度提升至30分以上（基本生存线）。")

    if total_score < 30:
        advice.append("💀 总体评估危险：你正在进行高风险All in操作，如果失败可能彻底出局。强烈建议立即建立四维冗余。")
    elif total_score < 50:
        advice.append("⚠️ 总体偏低：你有一定的风险意识但不够系统，一次意外就可能造成重大损失。建议按四维框架系统建立冗余。")
    elif total_score < 70:
        advice.append("👍 总体一般：你有基本的留余意识，但需要更系统化。建议用本工具定期（每月）自检，逐步提升。")
    elif total_score < 90:
        advice.append("🎉 总体健康：你的四维留余做得不错！继续保持，并考虑将留余原则制度化/工具化。")
    else:
        advice.append("🏆 总体优秀：你是留余大师！考虑将你的经验沉淀为模式，帮助更多人。")

    return CheckResult(
        dimensions=dimensions,
        total_score=total_score,
        total_level=total_level,
        anti_patterns=anti_patterns,
        advice=advice,
        adversity_passed=adversity_passed,
    )


# ── 交互式问卷 ────────────────────────────────────────────

def run_interactive() -> dict[str, int]:
    """运行交互式问卷，返回答案字典。"""
    answers = {}

    print_header("四维留余框架 · 决策冗余度评估", width=60)
    print()
    print("本工具将通过 22 道问题评估你当前决策/项目在天地人时四维的冗余度，")
    print("检测三种典型反模式（伪留余/单维留余/静态留余），并给出改进建议。")
    print()
    print("请根据你的真实情况选择最符合的选项（输入数字1-5）。")
    print("-" * 60)
    print()

    for idx, q in enumerate(QUESTIONS, 1):
        dim_name = DIMENSIONS[q.dimension]["name"]
        print(f"[{idx}/{len(QUESTIONS)}] [{dim_name}]")
        print(f"  {q.text}")
        print()
        for opt_idx, (opt_text, _) in enumerate(q.options, 1):
            print(f"    {opt_idx}. {opt_text}")
        print()

        while True:
            try:
                raw = input("  你的选择 [1-5]: ").strip()
                choice = int(raw)
                if 1 <= choice <= 5:
                    answers[q.id] = q.options[choice - 1][1]
                    break
                else:
                    print("  请输入1-5之间的数字")
            except (ValueError, EOFError):
                if not raw:
                    print("  请输入选项数字")
                else:
                    answers[q.id] = q.options[2][1]  # 默认选中间
                    print(f"  (默认选择: 3)")
                    break
        print()

    return answers


def print_report(result: CheckResult) -> None:
    """打印评估报告。"""
    print()
    print_header("评估报告", width=60)
    print()

    # 各维度得分
    print("【四维得分】")
    print()
    for dim_key in ["tian", "di", "ren", "shi"]:
        dim = result.dimensions[dim_key]
        level_cn = _level_cn(dim.level)
        bar_len = 30
        filled = int(dim.score / 100 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"  {DIMENSIONS[dim_key]['icon']} {dim.name}")
        print(f"    [{bar}] {dim.score}/100 {level_cn}")
        for w in dim.warnings:
            print_warn(w)
        print()

    # 反模式
    if result.anti_patterns:
        print("【反模式预警】")
        print()
        for ap in result.anti_patterns:
            if ap.startswith("🔴"):
                print_error(ap[2:].strip())
            else:
                print_warn(ap[2:].strip())
        print()
    else:
        print_pass("未检测到反模式，留余认知健康！")
        print()

    # 综合评分
    print("【综合评估】")
    print()
    total_bar_len = 40
    filled = int(result.total_score / 100 * total_bar_len)
    bar = "█" * filled + "░" * (total_bar_len - filled)
    level_cn = _level_cn(result.total_level)
    print(f"  总分: [{bar}] {result.total_score}/100 {level_cn}")
    print()

    # 逆境测试
    if result.adversity_passed:
        print_pass("逆境测试通过：所有维度均高于生存线（30分）")
    else:
        print_error("逆境测试未通过：存在致命薄弱维度，黑天鹅事件可能导致出局")
    print()

    # 建议
    if result.advice:
        print("【改进建议】")
        print()
        for a in result.advice:
            if a.startswith("🚨") or a.startswith("💀"):
                print_error(a)
            elif a.startswith("⚠️"):
                print_warn(a)
            else:
                print_pass(a)
        print()

    # 核心忠告
    print("-" * 60)
    print("💡 留余的终极价值不是让你赢最多，而是让你活得最久。")
    print("   在无限游戏中，不下牌桌比赢下某一手牌重要一万倍。")
    print("-" * 60)
    print()

    pass_count = sum(1 for d in result.dimensions.values() if d.level in ("good", "excellent"))
    warn_count = sum(1 for d in result.dimensions.values() if d.level in ("moderate", "warning"))
    error_count = sum(1 for d in result.dimensions.values() if d.level == "danger")
    error_count += sum(1 for ap in result.anti_patterns if ap.startswith("🔴"))
    warn_count += sum(1 for ap in result.anti_patterns if ap.startswith("🟡"))

    print_summary(pass_count, warn_count, error_count)


def result_to_json(result: CheckResult, answers: dict[str, int]) -> dict:
    """将结果转换为JSON可序列化字典。"""
    return {
        "total_score": result.total_score,
        "total_level": result.total_level,
        "total_level_cn": _level_cn(result.total_level),
        "adversity_passed": result.adversity_passed,
        "dimensions": {
            k: {
                "name": v.name,
                "score": v.score,
                "level": v.level,
                "level_cn": _level_cn(v.level),
                "warnings": v.warnings,
            }
            for k, v in result.dimensions.items()
        },
        "anti_patterns": result.anti_patterns,
        "advice": result.advice,
        "answers": answers,
    }


# ── 主入口 ────────────────────────────────────────────────

def main() -> None:
    setup_safe_output()

    parser = argparse.ArgumentParser(
        description="四维留余框架决策冗余度评估工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python .agents/scripts/check-margin.py                  # 交互式问卷
  python .agents/scripts/check-margin.py --json           # JSON输出
  python .agents/scripts/check-margin.py --non-interactive --scores "90,80,70,60"  # 快速评分（天,地,人,时）
        """,
    )
    add_common_args(parser)
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        default=False,
        help="非交互模式，需配合--scores使用",
    )
    parser.add_argument(
        "--scores",
        type=str,
        default=None,
        help="非交互模式下的四维评分（天,地,人,时），如 90,80,70,60",
    )

    args = parser.parse_args()

    if args.non_interactive and args.scores:
        # 非交互式评分模式
        try:
            scores = [int(s.strip()) for s in args.scores.split(",")]
            if len(scores) != 4:
                print_error("--scores 需要4个数字（天,地,人,时），范围0-100")
                sys.exit(1)
            answers = {}
            dim_question_ids = {
                "tian": ["t1", "t2", "t3", "t4", "t5"],
                "di": ["d1", "d2", "d3", "d4"],
                "ren": ["r1", "r2", "r3", "r4", "r5"],
                "shi": ["s1", "s2", "s3", "s4", "s5"],
            }
            # 将维度总分平均分配到各题
            dim_score_map = {"tian": scores[0], "di": scores[1], "ren": scores[2], "shi": scores[3]}
            for dim_key, dim_score in dim_score_map.items():
                qids = dim_question_ids[dim_key]
                per_q = dim_score / 100 * 20  # 每题平均分数
                for qid in qids:
                    answers[qid] = round(per_q)
            # 反模式默认中等
            for q in QUESTIONS:
                if q.dimension == "anti":
                    answers[q.id] = 12
        except ValueError:
            print_error("--scores 格式错误，应为逗号分隔的数字")
            sys.exit(1)
    else:
        # 交互式问卷
        answers = run_interactive()

    result = evaluate(answers)

    if args.json:
        print(json.dumps(result_to_json(result, answers), ensure_ascii=False, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
